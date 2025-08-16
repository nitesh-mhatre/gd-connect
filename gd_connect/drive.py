# gd_connect/drive.py
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from tqdm import tqdm

class GoogleDrive:
    def __init__(self, creds):
        from googleapiclient.discovery import build
        self.service = build("drive", "v3", credentials=creds)

    def list_files(self, folder_id="root", limit=20):
        """List files inside a folder (default root)."""
        query = f"'{folder_id}' in parents and trashed=false"
        results = (
            self.service.files()
            .list(q=query, pageSize=limit, fields="files(id, name, mimeType)")
            .execute()
        )
        return results.get("files", [])

    def upload_file(self, local_file, folder_id="root", name=None):
        from googleapiclient.http import MediaFileUpload
        file_metadata = {"name": name or os.path.basename(local_file), "parents": [folder_id]}
        media = MediaFileUpload(local_file, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        return file.get("id")

    def download_file(self, file_id, local_path):
        from googleapiclient.http import MediaIoBaseDownload
        import io
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(local_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return local_path

    def delete_file(self, file_id):
        self.service.files().delete(fileId=file_id).execute()
