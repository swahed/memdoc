# MemDoc Installation & Setup Guide

## System Requirements

### Minimum Requirements
- **OS:** Windows 10 or Windows 11
- **RAM:** 2 GB
- **Disk Space:** 100 MB for app, plus space for memoir data
- **Browser:** Chrome or Microsoft Edge (for desktop mode)
- **Internet:** Required for updates and initial download

### Recommended
- **RAM:** 4 GB or more
- **Disk Space:** 1 GB+ for memoir data and images
- **Cloud Storage:** OneDrive for automatic backup

## Installation Methods

### Method 1: Download Release (Recommended)

1. **Download MemDoc-Setup.exe**
   - Visit: https://github.com/swahed/memdoc/releases/latest
   - Download `MemDoc-Setup.exe`

2. **Handle Windows SmartScreen Warning**
   - Windows may show: "Windows protected your PC"
   - Click "More info"
   - Click "Run anyway"
   - **Note:** Warning appears because .exe is not code-signed (costs $200-500/year)

3. **Run MemDoc-Setup.exe**
   - Double-click the downloaded file
   - Follow the German-language install wizard
   - Installs to `C:\Program Files\MemDoc`, creates desktop + Start Menu shortcuts

4. **Choose Data Location (First Run)**
   - App will prompt for memoir storage location
   - **Recommended:** Choose a OneDrive folder for automatic backup
   - Example: `C:\Users\YourName\OneDrive\MemDoc`
   - Click "Browse" to select folder
   - Default: `~/Documents/MemDoc`

5. **Start Writing**
   - App opens in Chrome/Edge (looks like a desktop app)
   - No URL bar visible
   - Create your first chapter!

### Method 2: Run from Source (Developers)

1. **Clone Repository**
   ```bash
   git clone https://github.com/swahed/memdoc.git
   cd memdoc
   ```

2. **Create Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run in Browser Mode**
   ```bash
   python app.py --browser
   ```
   Open browser to: http://localhost:5000

5. **Or Run in Desktop Mode** (requires Chrome/Edge)
   ```bash
   python app.py
   ```

## First-Time Setup

### Choosing Data Directory

**Good Locations:**
- ✅ OneDrive folder: `C:\Users\Name\OneDrive\MemDoc`
- ✅ Google Drive: `C:\Users\Name\Google Drive\MemDoc`
- ✅ Dropbox: `C:\Users\Name\Dropbox\MemDoc`
- ✅ External drive: `E:\Backups\MemDoc`

**Bad Locations:**
- ❌ Desktop (gets cluttered)
- ❌ Downloads folder (might get deleted)
- ❌ System folders (permissions issues)
- ❌ Network drive (slow, unreliable)

### Data Directory Structure

After setup, your data folder contains:
```
MemDoc/
├── data/
│   ├── memoir.yml          # Memoir metadata (title, author)
│   ├── chapters/
│   │   ├── chapter-1.md    # Chapter markdown files
│   │   ├── chapter-2.md
│   │   └── ...
│   ├── images/             # Uploaded images
│   └── deleted/            # Archived deleted chapters
└── .memdoc_data_marker     # Marker file (don't delete)
```

### Configuration File

User config stored at:
```
%APPDATA%\MemDoc\config.json
```

Example:
```json
{
  "data_directory": "C:\\Users\\Name\\OneDrive\\MemDoc",
  "preferences": {},
  "last_migration": {
    "timestamp": "2025-12-26T10:30:00",
    "from": "C:\\Users\\Name\\Desktop\\MemDoc",
    "to": "C:\\Users\\Name\\OneDrive\\MemDoc"
  }
}
```

## Desktop Mode vs. Browser Mode

### Desktop Mode (Default for .exe)
- **Runs:** Chrome or Edge in app mode
- **Look:** Native desktop app (no URL bar)
- **Launch:** Double-click `MemDoc.exe`
- **Best for:** End users

### Browser Mode (Dev/Testing)
- **Runs:** Flask server, any browser
- **Look:** Regular web page
- **Launch:** `python app.py --browser`
- **Best for:** Development, debugging

## OneDrive Integration

### Why OneDrive?
- ✅ Automatic cloud backup
- ✅ Access from multiple devices
- ✅ Version history (30 days)
- ✅ Included with Windows/Office 365

### Setup OneDrive Sync

1. **Ensure OneDrive is Running**
   - Check system tray for OneDrive icon
   - If not running: Start → OneDrive

2. **Select Folder in OneDrive**
   - Settings → Browse
   - Navigate to: `C:\Users\YourName\OneDrive\`
   - Create subfolder: `MemDoc`
   - Confirm

3. **Verify Sync**
   - Green checkmark on folder = synced
   - Blue arrows = syncing in progress
   - Red X = sync error (check OneDrive settings)

## Moving Data Location

If you need to change where your memoir is stored:

1. **Open Settings**
   - Click gear icon (top right)

2. **Data Storage Section**
   - Shows current location
   - Click "Browse" to choose new location

3. **Select New Folder**
   - Choose or create new folder
   - Must be empty or valid MemDoc folder

4. **Migrate**
   - Click "Daten verschieben"
   - Wait for completion (status shown)
   - Old folder stays as-is (you can delete it later)
   - **App restarts automatically**

5. **Verify**
   - Check new location has all chapters

## Uninstallation

### Remove Application
1. Windows Settings > Apps > MemDoc > Uninstall
   - Or: Run `C:\Program Files\MemDoc\unins000.exe`
   - Uninstaller kills running MemDoc processes automatically

### Remove Configuration (optional)
2. Delete folder: `%USERPROFILE%\.memdoc\`
   - Contains `config.json`

### Keep or Remove Data
3. **Keep your memoir:** Leave data folder alone
4. **Delete everything:** Delete your chosen data folder (default: `~/Documents/MemDoc`)
   - WARNING: This deletes all your writing!
   - Make sure you have backups first

## Troubleshooting

### Windows SmartScreen Warning

**Issue:** "Windows protected your PC" message

**Solution:**
- Click "More info"
- Click "Run anyway"
- This is expected for unsigned .exe files

**Why:** Code signing certificates cost $200-500/year

### App Won't Start

**Issue:** Double-click does nothing

**Solutions:**
1. Check Task Manager for running MemDoc processes
2. Kill any existing processes:
   ```
   taskkill /F /IM MemDoc.exe
   ```
3. Try again

### Chrome/Edge Not Found

**Issue:** "Chrome/Edge not found" error

**Solutions:**
1. Install Chrome: https://www.google.com/chrome/
2. Or install Edge (comes with Windows 10+)
3. App will auto-detect and use available browser

### Data Folder Not Found

**Issue:** App can't find memoir data

**Solutions:**
1. Check OneDrive is running and synced
2. Verify folder exists and has correct permissions
3. Settings → Change data location
4. Or: Edit config manually:
   ```
   %APPDATA%\MemDoc\config.json
   ```

### Permission Errors

**Issue:** Can't save chapters or create folders

**Solutions:**
1. Run as administrator (right-click .exe)
2. Choose different data folder (not in Program Files)
3. Check OneDrive sync status

### Slow Performance

**Possible Causes:**
- Large images (>5 MB each)
- Network drive or slow OneDrive sync
- Hundreds of chapters

**Solutions:**
- Optimize images before uploading
- Use local drive instead of network
- Archive old chapters

## Getting Help

### Documentation
- Build process: `docs/BUILD_PROCESS.md`
- Update mechanism: `docs/UPDATE_PROCESS.md`
- Development guide: `docs/ROADMAP.md`

### Support
- GitHub Issues: https://github.com/swahed/memdoc/issues
- Provide:
  - Windows version
  - MemDoc version (shown in status bar)
  - Error messages
  - Steps to reproduce

### Logs
- No automatic logging yet
- To add: Run with `--debug` flag (developers only)

## Next Steps

After installation:
1. ✅ Create your first chapter
2. ✅ Add a cover page (Settings)
3. ✅ Write your memoir!
4. ✅ Export to PDF when ready
5. ✅ Check for updates periodically (Settings)
