# Update Mechanism - Debug Notes

## Current Status: NOT WORKING ❌

**Last tested:** 2025-12-26
**Tested versions:** v1.1.8 → v1.1.9

## What Works ✅
1. Repository made public - GitHub API accessible
2. Update detection works (checks GitHub releases API)
3. Update banner displays correctly
4. Download progress works and completes
5. Update modal UI works correctly
6. Dev mode detection works (bundled vs. non-bundled)

## What Doesn't Work ❌
1. **Installation hangs** - Progress bar reaches 100%, shows "Starte Anwendung neu..." but nothing happens
2. **App doesn't update** - After closing and reopening, still shows old version
3. **App doesn't restart automatically** - User must manually close and reopen

## Technical Details

### Update Flow (as designed)
1. User clicks "Installieren & Neustarten"
2. Frontend calls `/api/updates/install`
3. Backend:
   - Backs up current version (`backup_current_version()`)
   - Creates batch script (`apply_update()`)
   - Launches batch script in background
   - Schedules app exit after 1 second (`os._exit(0)`)
   - Returns success response
4. Batch script (update.bat):
   ```batch
   timeout /t 2 /nobreak >nul
   move /y "new.exe" "current.exe"
   start "" "current.exe"
   del "%~f0"
   ```

### Suspected Issues

#### Issue 1: App Not Exiting Properly
**Theory:** `os._exit(0)` might not kill all processes, especially Chrome/Edge browser
- Flask runs in background thread
- Chrome/Edge opened via subprocess.Popen
- Chrome process might prevent .exe from being unlocked

**Possible fixes to try:**
- Explicitly kill Chrome process before exit
- Use `psutil` to terminate all child processes
- Use Windows taskkill before exit

#### Issue 2: Batch Script Timing
**Theory:** 2-second timeout not enough, or batch script fails silently
- .exe might still be locked when batch script tries to move it
- Error handling in batch script might not be visible

**Possible fixes to try:**
- Increase timeout to 5 seconds
- Add logging to batch script (write to temp file)
- Use PowerShell script instead (better error handling)

#### Issue 3: Working Directory Issues
**Theory:** Batch script runs from wrong directory
- Current .exe might be in Downloads folder
- Paths in batch script might be wrong

**Possible fixes to try:**
- Use absolute paths everywhere
- Change working directory in script
- Verify paths before executing move command

#### Issue 4: Permissions
**Theory:** Windows User Access Control (UAC) blocks file replacement
- .exe replacement might require admin rights
- Silent failure if UAC prompt denied

**Possible fixes to try:**
- Request admin elevation for update process
- Move .exe to non-protected location before updating
- Use Windows Installer (.msi) instead

## Code Locations

### Backend (Python)
- `core/updater.py` - Update logic
  - `check_for_updates()` - GitHub API check
  - `download_update()` - Download with progress
  - `apply_update()` - Create and launch batch script
  - `backup_current_version()` - Backup before update
- `app.py` - API endpoints
  - `/api/updates/check` - Check for updates
  - `/api/updates/download` - Start download
  - `/api/updates/install` - Install update (Lines 741-798)

### Frontend (JavaScript)
- `static/js/app.js` - Update UI logic
  - `checkForUpdatesOnStartup()` - Auto-check
  - `manualCheckForUpdates()` - Manual check
  - `startDownload()` - Download with progress
  - `installUpdate()` - Install and restart

## Next Steps for Debugging

1. **Add logging to batch script:**
   ```batch
   @echo off
   echo Starting update > "%TEMP%\memdoc_update.log"
   timeout /t 2 /nobreak >nul
   echo Attempting file move >> "%TEMP%\memdoc_update.log"
   move /y "new.exe" "current.exe" >> "%TEMP%\memdoc_update.log" 2>&1
   echo Move result: %ERRORLEVEL% >> "%TEMP%\memdoc_update.log"
   ```

2. **Test batch script manually:**
   - Find update.bat in `%APPDATA%\MemDoc\backups\`
   - Run it manually to see errors
   - Check if .exe gets replaced

3. **Check process tree:**
   - Use Task Manager to see all MemDoc processes
   - Check if Chrome/Edge processes remain
   - See if .exe is actually locked

4. **Try alternative approach:**
   - Use Python updater library (e.g., `pyupdater`)
   - Use Windows Installer (.msi) for updates
   - Use self-extracting archive approach

## Alternative Solutions

### Option 1: Manual Update
- Download new .exe
- Close app
- Replace .exe manually
- Simpler, always works, but not user-friendly

### Option 2: Separate Updater Executable
- Small updater.exe that:
  1. Downloads new version
  2. Closes main app
  3. Replaces .exe
  4. Starts new version
- More complex but more reliable

### Option 3: Use Existing Tools
- **PyUpdater** - Self-updating library
- **Squirrel.Windows** - Update framework
- **Advanced Installer** - Professional installer with updates

## Test Plan (for future fixes)

1. Build two versions (e.g., v1.2.0 and v1.2.1)
2. Run v1.2.0
3. Trigger update to v1.2.1
4. Verify:
   - [ ] Download completes
   - [ ] App exits within 2 seconds
   - [ ] .exe is replaced (check file modification time)
   - [ ] App restarts automatically
   - [ ] New version shows in UI
   - [ ] All functionality works

## References

- PyInstaller docs: https://pyinstaller.org/
- Windows batch script guide: https://ss64.com/nt/
- Auto-update patterns: https://github.com/topics/auto-update
