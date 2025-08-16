# 📂 gd-connect

`gd-connect` is a Python package + CLI tool that makes it easy to **connect to Google Drive**,  
so you can **list, upload, download, and delete files** directly from Python or the terminal.

---

## ✨ Features
- 🔑 Simple Google OAuth2 authentication
- 📜 List files in your Drive
- ⬆️ Upload files with automatic MIME type detection
- ⬇️ Download files with progress bar
- ❌ Delete files
- 💻 CLI support (`gd-connect list`, `gd-connect upload`, etc.)

---

## 📦 Installation

### 1. Install from source (development mode)
```bash
git clone https://github.com/nitesh-mhatre/gd-connect.git
cd gd-connect
pip install -e .
```


======================================================
 How to Create Google Drive API credentials.json
======================================================

1. Create a Project in Google Cloud Console
-------------------------------------------
1. Go to https://console.cloud.google.com/
2. Log in with your Google account.
3. On the top bar, click the project dropdown → "New Project".
4. Enter a Project Name (e.g., "gd-connect") and click "Create".



2. Enable Google Drive API
--------------------------
1. Inside your new project, go to:
   Navigation Menu → APIs & Services → Library
2. Search for "Google Drive API".
3. Click "Enable".



3. Create OAuth Client ID
--------------------------
1. Go to:
   Navigation Menu → APIs & Services → Credentials
2. Click "Create Credentials" → "OAuth client ID".
3. If asked, configure the **OAuth consent screen** first (see step 4).
4. For Application type, choose: **Desktop App**.
5. Give it a name (e.g., "gd-connect").
6. Click "Create".
7. A popup will show your new OAuth Client. Click "Download JSON".
8. Save it as:credentials.jsonand place it inside your `gd_connect` project root folder: ~/gd_connect/credentials.json

so you don’t need to log in again next time.

======================================================
DONE ✅
You now have a valid credentials.json and can use gd-connect.
======================================================

## Setup Credentials

To use `gd-connect`, you must create a Google Cloud project, enable the Drive API, and download your `credentials.json`.

👉 Follow the detailed step-by-step guide here:  
[docs/credentials_setup.txt](docs/credentials_setup.txt)


# 🚀 Roadmap – gd-connect

## ✅ Implemented Features
- Authentication with Google OAuth2
- List files & folders (`ls`)
- Change directories (`cd`)
- Upload, download, delete files
- Create directories (`mkdir`)
- Check if file/folder exists
- Path-based navigation (basic)
- Persistent credentials storage (`token.json`)

---

## 🔮 Planned / Nice-to-have Features

### Path & Navigation
- Full path-style navigation (`ls`, `cd`, `pwd`)
- Relative/absolute path handling like a real filesystem

### Mounting
- Mount Google Drive as a FUSE filesystem (`~/gdrive`)
- Native Linux file commands (`ls`, `cp`, `mv`) on mounted drive

### File Operations
- File syncing (`sync` local ↔ drive)
- Batch upload/download
- Resumable uploads for large files

### Search & Info
- Search by name, type, or MIME (`gd-connect search "report"`)
- File metadata & info (size, owner, permissions, last modified)

### Sharing & Permissions
- Share files with users (`--with user@gmail.com --role reader`)
- Manage folder/file permissions

### Trash & Recovery
- Move files to trash
- Restore or permanently delete from trash

### Config & Profiles
- Multiple Google accounts / profiles
- Switch with `--profile`

### Advanced Features
- Interactive shell mode (`gd-connect shell`)
- Tab-completion support
- Logging & verbose/debug modes
- Cross-platform installer (`pipx`, Homebrew, etc.)




# 🚀 Roadmap – gd-connect

## ✅ Implemented Features
- Authentication with Google OAuth2
- List files & folders (`ls`)
- Change directories (`cd`)
- Upload, download, delete files
- Create directories (`mkdir`)
- Check if file/folder exists
- Path-based navigation (basic)
- Persistent credentials storage (`token.json`)

---

## 🔮 Planned / Nice-to-have Features

### Path & Navigation
- Full path-style navigation (`ls`, `cd`, `pwd`)
- Relative/absolute path handling like a real filesystem

### Mounting
- Mount Google Drive as a FUSE filesystem (`~/gdrive`)
- Native Linux file commands (`ls`, `cp`, `mv`) on mounted drive

### File Operations
- File syncing (`sync` local ↔ drive)
- Batch upload/download
- Resumable uploads for large files

### Search & Info
- Search by name, type, or MIME (`gd-connect search "report"`)
- File metadata & info (size, owner, permissions, last modified)

### Sharing & Permissions
- Share files with users (`--with user@gmail.com --role reader`)
- Manage folder/file permissions

### Trash & Recovery
- Move files to trash
- Restore or permanently delete from trash

### Config & Profiles
- Multiple Google accounts / profiles
- Switch with `--profile`

### Advanced Features
- Interactive shell mode (`gd-connect shell`)
- Tab-completion support
- Logging & verbose/debug modes
- Cross-platform installer (`pipx`, Homebrew, etc.)
