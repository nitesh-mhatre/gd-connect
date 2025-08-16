import argparse
import os
import sys
from gd_connect.auth import get_credentials
from gd_connect.drive import GoogleDrive
from gd_connect.utils import resolve_path, path_exists


def main():
    parser = argparse.ArgumentParser(
        description="Google Drive CLI (path-based, OS-like)"
    )
    subparsers = parser.add_subparsers(dest="command")

    # List directory
    ls_parser = subparsers.add_parser("ls", help="List files in a folder")
    ls_parser.add_argument("path", help="Remote path (e.g., /Projects)", nargs="?", default="/")
    ls_parser.add_argument("--limit", type=int, default=20, help="Limit number of results")

    # Upload
    upload_parser = subparsers.add_parser("upload", help="Upload a local file to Drive")
    upload_parser.add_argument("local_file", help="Local file to upload")
    upload_parser.add_argument("dest_path", help="Destination path on Drive (/Projects/file.txt)")

    # Download
    download_parser = subparsers.add_parser("download", help="Download a file from Drive")
    download_parser.add_argument("src_path", help="Remote file path on Drive (/Projects/file.txt)")
    download_parser.add_argument("dest_folder", help="Local destination folder")

    # Mkdir
    mkdir_parser = subparsers.add_parser("mkdir", help="Create a folder in Drive")
    mkdir_parser.add_argument("path", help="Remote folder path (/Projects/NewFolder)")

    # Remove
    rm_parser = subparsers.add_parser("rm", help="Remove a file or folder from Drive")
    rm_parser.add_argument("path", help="Remote path (/Projects/file.txt)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    creds = get_credentials()
    drive = GoogleDrive(creds)

    if args.command == "ls":
        folder_id = resolve_path(drive, args.path)
        files = drive.list_files(folder_id, args.limit)
        for f in files:
            print(f"{f['name']:<30} {f['mimeType']}  ({f['id']})")

    elif args.command == "upload":
        parent_path, file_name = os.path.split(args.dest_path)
        folder_id = resolve_path(drive, parent_path, create_missing=True)
        file_id = drive.upload_file(args.local_file, folder_id, name=file_name)
        print(f"✅ Uploaded {args.local_file} → {args.dest_path} (id: {file_id})")

    elif args.command == "download":
        file_id = resolve_path(drive, args.src_path)
        local_file = os.path.join(args.dest_folder, os.path.basename(args.src_path))
        drive.download_file(file_id, local_file)
        print(f"✅ Downloaded {args.src_path} → {local_file}")

    elif args.command == "mkdir":
        folder_id = resolve_path(drive, args.path, create_missing=True)
        print(f"✅ Created folder {args.path} (id: {folder_id})")

    elif args.command == "rm":
        file_id = resolve_path(drive, args.path)
        drive.delete_file(file_id)
        print(f"🗑️ Removed {args.path}")

    else:
        print("❌ Unknown command")


if __name__ == "__main__":
    main()
