import io
import json
import os
import posixpath
from typing import List, Dict, Optional
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from .auth import get_credentials

STATE_FILE = os.path.expanduser("~/.gd_connect_state.json")
FOLDER_MIME = "application/vnd.google-apps.folder"


class GoogleDrive:
    """
    High-level, path-aware wrapper around Google Drive v3.
    Maintains a persistent current working directory in ~/.gd_connect_state.json.
    """

    def __init__(self):
        creds = get_credentials()
        self.service = build("drive", "v3", credentials=creds)
        self.cwd_path = "/"    # string path like "/Projects"
        self._load_state()

    # ----------------------- State -----------------------

    def _load_state(self):
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r") as f:
                    data = json.load(f)
                    self.cwd_path = data.get("cwd_path", "/")
            else:
                self._save_state()
        except Exception:
            # If state is corrupt, reset
            self.cwd_path = "/"
            self._save_state()

    def _save_state(self):
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump({"cwd_path": self.cwd_path}, f, indent=2)

    # ----------------------- Path utils -----------------------

    def _norm_join(self, base: str, add: str) -> str:
        # Always POSIX style for Drive paths
        if add.startswith("/"):
            return posixpath.normpath(add) or "/"
        if base == "/":
            return posixpath.normpath(f"/{add}") or "/"
        return posixpath.normpath(f"{base.rstrip('/')}/{add}") or "/"

    def normalize_path(self, path: Optional[str]) -> str:
        """Return absolute POSIX path from cwd + input (supports '.', '..')."""
        if not path or path == ".":
            return self.cwd_path
        return self._norm_join(self.cwd_path, path)

    # ----------------------- Drive resolution -----------------------

    def _get_child_by_name(self, parent_id: str, name: str) -> Optional[Dict]:
        q = (
            f"'{parent_id}' in parents and name = '{name}' and trashed = false"
        )
        res = self.service.files().list(
            q=q, spaces="drive",
            fields="files(id,name,mimeType)"
        ).execute()
        files = res.get("files", [])
        return files[0] if files else None

    def _get_root_id(self) -> str:
        # 'root' works as an alias; keep helper for clarity
        return "root"

    def get_id_from_path(self, path: str) -> str:
        """Resolve a /a/b style path to a file ID. Raises FileNotFoundError if missing."""
        if path == "/" or path == "":
            return self._get_root_id()

        parts = [p for p in path.strip("/").split("/") if p]
        parent_id = self._get_root_id()
        for part in parts:
            child = self._get_child_by_name(parent_id, part)
            if not child:
                raise FileNotFoundError(f"❌ No such file or folder: {path}")
            parent_id = child["id"]
        return parent_id

    def get_meta(self, path: str) -> Dict:
        """Return file metadata for a path (raises if missing)."""
        file_id = self.get_id_from_path(path)
        return self.service.files().get(
            fileId=file_id, fields="id,name,mimeType,parents"
        ).execute()

    def exists(self, path: str) -> bool:
        try:
            _ = self.get_id_from_path(path)
            return True
        except FileNotFoundError:
            return False

    def is_dir(self, path: str) -> bool:
        try:
            meta = self.get_meta(path)
            return meta.get("mimeType") == FOLDER_MIME
        except FileNotFoundError:
            return False

    # ----------------------- Navigation -----------------------

    def pwd(self) -> str:
        return self.cwd_path

    def cd(self, path: str) -> str:
        """Change current directory. Supports '/', '.', '..', absolute & relative."""
        abs_path = self.normalize_path(path)
        meta = self.get_meta(abs_path)
        if meta.get("mimeType") != FOLDER_MIME:
            raise NotADirectoryError(f"❌ Not a folder: {abs_path}")
        self.cwd_path = abs_path
        self._save_state()
        return self.cwd_path

    # ----------------------- Listing & Search -----------------------

    def ls(self, path: Optional[str] = None) -> List[Dict]:
        """List files in folder. Returns list of metadata dicts."""
        folder_path = self.normalize_path(path) if path else self.cwd_path
        folder_id = self.get_id_from_path(folder_path)
        res = self.service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            spaces="drive",
            fields="files(id,name,mimeType)"
        ).execute()
        return res.get("files", [])

    def search(self, query: str, path: Optional[str] = None) -> List[Dict]:
        """Search by name contains within a folder (default: cwd)."""
        folder_path = self.normalize_path(path) if path else self.cwd_path
        folder_id = self.get_id_from_path(folder_path)
        q = (
            f"'{folder_id}' in parents and name contains '{query}' and trashed = false"
        )
        res = self.service.files().list(
            q=q, spaces="drive",
            fields="files(id,name,mimeType)"
        ).execute()
        return res.get("files", [])

    # ----------------------- Upload / Download -----------------------

    def upload(self, local_path: str, remote_path: Optional[str] = None) -> Dict:
        """
        Upload local file to Drive.
        - If remote_path is None: upload into cwd with same filename.
        - If remote_path resolves to an existing folder: upload into it (same basename).
        - Else: treat remote_path as a full path with target filename (parent must exist).
        """
        if not os.path.isfile(local_path):
            raise FileNotFoundError(f"❌ Local file not found: {local_path}")

        if not remote_path:
            parent_path = self.cwd_path
            name = os.path.basename(local_path)
        else:
            abs_remote = self.normalize_path(remote_path)
            if self.exists(abs_remote) and self.is_dir(abs_remote):
                parent_path = abs_remote
                name = os.path.basename(local_path)
            else:
                parent_path = posixpath.dirname(abs_remote) or "/"
                if not self.exists(parent_path) or not self.is_dir(parent_path):
                    raise FileNotFoundError(f"❌ Parent folder missing: {parent_path}")
                name = posixpath.basename(abs_remote)

        parent_id = self.get_id_from_path(parent_path)
        file_metadata = {"name": name, "parents": [parent_id]}
        media = MediaFileUpload(local_path, resumable=True)
        created = self.service.files().create(
            body=file_metadata, media_body=media, fields="id,name"
        ).execute()
        return created

    def download(self, remote_path: str, local_path: str) -> None:
        """
        Download a Drive file to local path.
        Note: Native Google Docs/Sheets/Slides need 'export'; this method handles binary files.
        """
        file_id = self.get_id_from_path(self.normalize_path(remote_path))
        request = self.service.files().get_media(fileId=file_id)
        os.makedirs(os.path.dirname(os.path.abspath(local_path)) or ".", exist_ok=True)
        with io.FileIO(local_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

    # ----------------------- Remove / Move / Copy -----------------------

    def rm(self, path: str) -> None:
        file_id = self.get_id_from_path(self.normalize_path(path))
        self.service.files().delete(fileId=file_id).execute()

    def mv(self, src: str, dst: str) -> Dict:
        """
        Move or rename:
        - If dst resolves to existing folder: move src into that folder (keep name).
        - Else: move+rename to the parent of dst (parent must exist).
        """
        src_path = self.normalize_path(src)
        dst_path = self.normalize_path(dst)

        src_meta = self.get_meta(src_path)
        src_id = src_meta["id"]

        # Destination is existing folder → move into it, keep name
        if self.exists(dst_path) and self.is_dir(dst_path):
            new_parent_id = self.get_id_from_path(dst_path)
            new_name = src_meta["name"]
        else:
            # Treat dst as full path with new name
            parent_path = posixpath.dirname(dst_path) or "/"
            if not self.exists(parent_path) or not self.is_dir(parent_path):
                raise FileNotFoundError(f"❌ Parent folder missing: {parent_path}")
            new_parent_id = self.get_id_from_path(parent_path)
            new_name = posixpath.basename(dst_path)

        # Fetch previous parents
        file_parents = self.service.files().get(fileId=src_id, fields="parents").execute()
        prev_parents = ",".join(file_parents.get("parents", []))

        updated = self.service.files().update(
            fileId=src_id,
            addParents=new_parent_id,
            removeParents=prev_parents,
            body={"name": new_name},
            fields="id,name,parents"
        ).execute()
        return updated

    def cp(self, src: str, dst: str) -> Dict:
        """
        Copy file (not folder—Drive API cannot copy folders).
        - If dst resolves to existing folder: copy into it with same name.
        - Else: copy to parent of dst with new name (parent must exist).
        """
        src_path = self.normalize_path(src)
        dst_path = self.normalize_path(dst)

        src_meta = self.get_meta(src_path)
        if src_meta.get("mimeType") == FOLDER_MIME:
            raise ValueError("❌ Copying folders is not supported by Drive API.")

        src_id = src_meta["id"]

        if self.exists(dst_path) and self.is_dir(dst_path):
            parent_id = self.get_id_from_path(dst_path)
            name = src_meta["name"]
        else:
            parent_path = posixpath.dirname(dst_path) or "/"
            if not self.exists(parent_path) or not self.is_dir(parent_path):
                raise FileNotFoundError(f"❌ Parent folder missing: {parent_path}")
            parent_id = self.get_id_from_path(parent_path)
            name = posixpath.basename(dst_path)

        body = {"name": name, "parents": [parent_id]}
        created = self.service.files().copy(
            fileId=src_id, body=body, fields="id,name,parents"
        ).execute()
        return created

    def search(self, name=None, mimeType=None, modified_after=None, modified_before=None):
        """Search files by name, mimeType, and modifiedTime."""
        query_parts = []

        if name:
            query_parts.append(f"name contains '{name}'")
        if mimeType:
            query_parts.append(f"mimeType='{mimeType}'")
        if modified_after:
            dt = datetime.strptime(modified_after, "%Y-%m-%d").isoformat() + "Z"
            query_parts.append(f"modifiedTime > '{dt}'")
        if modified_before:
            dt = datetime.strptime(modified_before, "%Y-%m-%d").isoformat() + "Z"
            query_parts.append(f"modifiedTime < '{dt}'")

        query = " and ".join(query_parts) if query_parts else None

        results = self.service.files().list(
            q=query,
            fields="files(id, name, mimeType, modifiedTime, size)",
            spaces="drive"
        ).execute()

        return results.get("files", [])
