# gd_connect/utils.py

import mimetypes
import os
import sys


def guess_mime_type(filename: str) -> str:
    """
    Guess the MIME type of a file based on its extension.
    Defaults to 'application/octet-stream' if unknown.

    Parameters:
        filename (str): Path or name of the file.

    Returns:
        str: MIME type string.
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


def ensure_file_exists(filepath: str):
    """
    Ensure that a file exists, otherwise exit gracefully.

    Parameters:
        filepath (str): Path to the file.

    Returns:
        None
    """
    if not os.path.exists(filepath):
        print(f"❌ Error: File '{filepath}' not found.")
        sys.exit(1)


def format_file_info(file: dict) -> str:
    """
    Format Google Drive file info for pretty printing.

    Parameters:
        file (dict): Dictionary containing 'id' and 'name'.

    Returns:
        str: Formatted string like "filename.txt (FILE_ID)".
    """
    return f"{file.get('name', 'Unnamed')} ({file.get('id', 'NoID')})"
    
def resolve_path(drive, path: str, create_missing=False):
    """
    Convert a UNIX-like path (/folder/subfolder/file.txt) into a Google Drive ID.
    If create_missing=True, will create folders if they don't exist.
    """
    if path in ["/", ""]:
        return "root"

    parts = [p for p in path.strip("/").split("/") if p]
    parent_id = "root"

    for i, part in enumerate(parts):
        query = f"'{parent_id}' in parents and name='{part}' and trashed=false"
        results = drive.service.files().list(q=query, fields="files(id, name, mimeType)").execute().get("files", [])

        if not results:
            if create_missing:
                file_metadata = {
                    "name": part,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [parent_id],
                }
                folder = drive.service.files().create(body=file_metadata, fields="id").execute()
                parent_id = folder.get("id")
            else:
                raise FileNotFoundError(f"Path '{path}' not found")
        else:
            parent_id = results[0]["id"]

    return parent_id


def path_exists(drive, path: str) -> bool:
    """Check if a given path exists in Drive"""
    try:
        resolve_path(drive, path)
        return True
    except FileNotFoundError:
        return False

