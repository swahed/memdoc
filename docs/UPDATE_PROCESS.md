# MemDoc Update Process

## Overview

MemDoc uses **Inno Setup** to create a proper Windows installer (`MemDoc-Setup.exe`), distributed via **GitHub Releases**. Updates are downloaded within the app and installed by running the Inno Setup installer in silent mode.

## How Updates Work

### Automatic Update Check
- **When:** On app startup
- **Frequency:** Once per session
- **Behavior:** Silent check, shows banner if update available
- **Network:** Requires internet connection

### Manual Update Check
- **Where:** Settings > Software Updates
- **Action:** Click "Check for Updates Now"
- **Result:** Immediate check, shows status message

## Update Flow (User Perspective)

### Step 1: Update Available
```
App startup
    |
Auto-check GitHub Releases
    |
New version found
    |
Blue banner appears at top:
"Version X.Y.Z available - New features and improvements"
[Details] [x]
```

### Step 2: View Details
```
Click "Details"
    |
Update modal opens
    |
Shows:
- Current version: 1.1.0
- New version: 1.2.0
- Release date
- What's new (release notes)
- Download size
```

### Step 3: Download
```
Click "Download"
    |
Progress bar shows download
"Downloading... 45%"
"5.2 MB / 11.5 MB"
    |
Download completes
    |
"Install & Restart" button appears
```

### Step 4: Install
```
Click "Install & Restart"
    |
Confirmation dialog
    |
Click "OK"
    |
Inno Setup installer launches silently
    |
Brief progress bar (Inno Setup silent mode)
    |
App restarts automatically
    |
New version running!
```

## Technical Implementation

### Components

#### Frontend (JavaScript)
**File:** `static/js/app.js`

**Key Methods:**
- `checkForUpdatesOnStartup()` - Auto-check on load
- `manualCheckForUpdates()` - Manual check button
- `showUpdateBanner()` - Display update notification
- `startDownload()` - Download with progress tracking
- `installUpdate()` - Trigger installation

#### Backend (Python)
**File:** `core/updater.py`

**Key Functions:**
- `check_for_updates()` - Query GitHub API, looks for `MemDoc-Setup.exe` asset
- `download_update()` - Download with progress callback
- `backup_current_version()` - Backup before update
- `apply_update()` - Launch Inno Setup installer in silent mode
- `rollback_to_version()` - Restore previous version

#### API Endpoints
**File:** `app.py`

- `GET /api/version` - Current version info
- `GET /api/updates/check` - Check for updates
- `POST /api/updates/download` - Start background download
- `GET /api/updates/download/status` - Poll download progress
- `POST /api/updates/install` - Install and restart
- `GET /api/updates/backups` - List available backups
- `POST /api/updates/rollback` - Rollback to version

### Inno Setup Installer

**Script:** `installer.iss` (project root)

**Features:**
- German language UI
- Installs to `C:\Program Files\MemDoc`
- Desktop shortcut + Start Menu entry
- Proper uninstaller (visible in Windows Settings > Apps)
- `AppMutex` for detecting running instances
- `CloseApplications=yes` - gracefully closes running MemDoc during upgrade
- `RestartApplications=yes` - relaunches after upgrade

**Silent mode flags (used during updates):**
```
MemDoc-Setup.exe /SILENT /SUPPRESSMSGBOXES /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS
```

### Process Lifecycle

**Browser close = app exit:**
The app monitors the browser subprocess. When the user closes the browser window, the Python process exits cleanly (no more zombie processes).

## First-Time Installation

1. User downloads `MemDoc-Setup.exe` from GitHub Releases
2. Runs installer - German-language wizard
3. Installs to Program Files, creates shortcuts
4. MemDoc launches on finish
5. User picks OneDrive data folder

## Version Detection

### Dev Mode vs. Production
- **Dev mode:** Updates disabled (running from source)
- **Production:** Updates enabled (running from .exe)

### Test Builds
- Updates always disabled for test builds
- Prevents accidental upgrade of test version

## Safety Features

### Backup Before Update
**Location:** `%APPDATA%\MemDoc\backups\vX.Y.Z\`

**Contains:**
- Old MemDoc.exe
- backup_info.json (metadata)

### Integrity Verification
Downloaded installer is checked for valid PE header before execution.

### Rollback Support
1. Settings > Software Updates
2. Scroll to "Previous Versions"
3. Click "Restore" on desired version
4. Confirm
5. App restarts with old version

## Release Process

### For Developers

#### 1. Prepare Release
```bash
# Update version
Edit core/version.py: VERSION = "1.2.0"

# Update changelog
Edit CHANGELOG.md

# Commit
git add core/version.py CHANGELOG.md
git commit -m "Bump version to 1.2.0"
git push origin main
```

#### 2. Create Tag
```bash
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

#### 3. GitHub Actions Builds
- Workflow: `.github/workflows/release.yml`
- Trigger: Tag push
- Steps: PyInstaller build -> Inno Setup compile -> Upload `MemDoc-Setup.exe`

#### 4. Edit Release Notes
1. Go to GitHub Releases
2. Edit the auto-created release
3. Fill in German release notes

## What We're NOT Doing

- No code signing (SmartScreen warning stays)
- No auto-update without user action
- No delta updates (full installer each time, ~30MB)
- No custom update UI during install (Inno Setup progress bar is enough)

## References

- Inno Setup: https://jrsoftware.org/isinfo.php
- GitHub Releases API: https://docs.github.com/rest/releases
- PyInstaller docs: https://pyinstaller.org/
