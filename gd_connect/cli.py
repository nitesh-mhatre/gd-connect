import argparse
import sys

from .drive import GoogleDrive, FOLDER_MIME


def print_list(items):
    for f in items:
        icon = "📁" if f.get("mimeType") == FOLDER_MIME else "📄"
        print(f"{icon} {f.get('name')}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="gd-connect",
        description="📂 Google Drive CLI — OS-like commands with persistent cwd",
        epilog="""Examples:
  gd-connect pwd
  gd-connect ls
  gd-connect ls /Projects
  gd-connect cd /Projects/Reports
  gd-connect upload ./local.txt
  gd-connect upload ./local.txt /Projects/NewName.txt
  gd-connect download /Projects/NewName.txt ./local_copy.txt
  gd-connect mv report.txt /Projects/Archive/
  gd-connect mv report.txt renamed.txt
  gd-connect cp report.txt /Projects/Backup/
  gd-connect rm /Projects/Old/file.txt
  gd-connect is-exist /Projects/Notes.txt
  gd-connect is-dir /Projects
  gd-connect search budget
Tips:
- Paths can be relative (note.txt) or absolute (/Team/note.txt).
- Use '..' and '.' just like a shell. 'cd /' goes to root.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", help="Commands")

    sub.add_parser("pwd", help="Print current directory")

    ls = sub.add_parser("ls", help="List files in a folder")
    ls.add_argument("path", nargs="?", help="Folder path (default: cwd)")

    cd = sub.add_parser("cd", help="Change current directory")
    cd.add_argument("path", help="Path to folder")

    up = sub.add_parser("upload", help="Upload local file to Drive")
    up.add_argument("local", help="Local file path")
    up.add_argument("remote", nargs="?", help="Remote path or folder (default: cwd)")

    down = sub.add_parser("download", help="Download Drive file to local path")
    down.add_argument("remote", help="Remote file path")
    down.add_argument("local", help="Local destination path")

    rm = sub.add_parser("rm", help="Remove a file or folder")
    rm.add_argument("path", help="Path to remove")

    mv = sub.add_parser("mv", help="Move/rename a file or folder")
    mv.add_argument("src", help="Source path")
    mv.add_argument("dst", help="Destination path or folder")

    cp = sub.add_parser("cp", help="Copy a file (folders not supported by Drive API)")
    cp.add_argument("src", help="Source file path")
    cp.add_argument("dst", help="Destination path or folder")

    ise = sub.add_parser("is-exist", help="Check if a path exists")
    ise.add_argument("path", help="Path to check")

    isd = sub.add_parser("is-dir", help="Check if a path is a folder")
    isd.add_argument("path", help="Path to check")

    sea = sub.add_parser("search", help="Search by name within a folder (default: cwd)")
    sea.add_argument("query", help="Name contains...")
    sea.add_argument("path", nargs="?", help="Folder to search in (default: cwd)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(0)

    d = GoogleDrive()

    try:
        if args.cmd == "pwd":
            print(f"📍 {d.pwd()}")

        elif args.cmd == "ls":
            items = d.ls(args.path)
            print_list(items)

        elif args.cmd == "cd":
            new_path = d.cd(args.path)
            print(f"📂 Changed directory to: {new_path}")

        elif args.cmd == "upload":
            created = d.upload(args.local, args.remote)
            print(f"⬆️  Uploaded: {created.get('name')} (id={created.get('id')})")

        elif args.cmd == "download":
            d.download(args.remote, args.local)
            print(f"⬇️  Downloaded: {args.remote} → {args.local}")

        elif args.cmd == "rm":
            d.rm(args.path)
            print(f"🗑️  Removed: {args.path}")

        elif args.cmd == "mv":
            updated = d.mv(args.src, args.dst)
            print(f"🔀 Moved/Renamed to: {updated.get('name')}")

        elif args.cmd == "cp":
            created = d.cp(args.src, args.dst)
            print(f"📄 Copied as: {created.get('name')} (id={created.get('id')})")

        elif args.cmd == "is-exist":
            print("✅ Exists" if d.exists(args.path) else "❌ Not found")

        elif args.cmd == "is-dir":
            print("📁 Folder" if d.is_dir(args.path) else "📄 File or missing")

        elif args.cmd == "search":
            items = d.search(args.query, args.path)
            if not items:
                print("🔍 No matches")
            else:
                print_list(items)

    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)
    except IsADirectoryError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except NotADirectoryError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except HttpError as e:
        print(f"❌ API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
