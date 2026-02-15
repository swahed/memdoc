# Known Issues

## Open Issues

### PowerShell console visible during folder pick

**Status:** Parked (cosmetic, all fixes break the dialog)
**Severity:** Low

**Symptom:** Clicking "Durchsuchen" in settings opens a visible PowerShell window that closes when the folder dialog is dismissed.

**Attempted fixes (all failed):**
- `CREATE_NO_WINDOW`: dialog never appears (no window station)
- `STARTUPINFO SW_HIDE`: dialog hidden behind windows, spawns stuck processes
- `-WindowStyle Hidden`: console minimizes but dialog doesn't appear
- Win32 `GetConsoleWindow+ShowWindow`: spawns 2 processes, unreliable

**Decision:** Accept visible console. Only working approach is plain `subprocess.run()`.

**Files:** `app.py` — folder picker route

---

### Uninstaller leaves `~/.memdoc` folder

**Status:** Parked (safer to leave it)
**Severity:** Low

**Symptom:** After uninstalling, `~/.memdoc/config.json` remains on disk.

**Decision:** Leave it. Deleting could risk removing user's memoir data if the data dir is inside `~/.memdoc`. User can manually delete `~/.memdoc` and their data folder.

---

## Resolved Issues

### Fixed in v1.4.0

- **Multi-window support:** Second instance now opens in Chrome/Edge app mode instead of default browser. Cross-window sync via BroadcastChannel API.
- **Migration failures:** Empty directories (`chapters/`, `images/`) now copied correctly. No dangerous `shutil.rmtree()` cleanup on failure.
- **Settings UI bugs:** `addEventListener` stacking caused duplicate folder picker dialogs — switched to `onclick`. Migration options hidden after reopening settings — fixed by resetting display. Empty green validation box — fixed by clearing className.
- **Subfolder prompt removed:** Migration now sets path directly (consistent with onboarding).
- **Backup option removed:** Migration simply copies files, old folder stays as-is.

### Fixed in v1.3.6: Single-instance check

**Root cause:** `is_port_in_use()` socket bind check was unreliable — socket released immediately after check, race condition.

**Fix:** Replaced with Windows named mutex (`CreateMutexW`). Required `ctypes.WinDLL('kernel32', use_last_error=True)` instead of `ctypes.windll.kernel32` for `ctypes.get_last_error()` to work.

### Fixed in v1.3.6: Installer can't kill running MemDoc during upgrade

**Fix:** Added `[Code]` section to `installer.iss` with `CurStepChanged(ssInstall)` running `taskkill /IM MemDoc.exe /F`.

### Fixed in v1.3.4: Preview rendering broken (v1.3.2 regression)

**Root cause:** Regex `(\*{1,2})(\S(?:.*?\S)?)\s+(\1)` caused catastrophic backtracking.

**Fix:** Replaced with simpler `re.sub(r'\s+(\*{1,2})(?=\s|$|[.,;:!?\)])', r'\1', ...)`. Added 7 unit tests.

### Fixed in v1.3.2: Bold/italic toolbar wraps trailing whitespace

**Root cause:** Double-clicking a word selects the trailing space. Toolbar wrapped the space inside markers.

**Fix:** `editor.js` `wrapSelection()` trims whitespace from selection and places it outside markers.

### Fixed in v1.3.1: Multiple UX issues

- Folder picker opened new app instance (PyInstaller `sys.executable` issue — now uses PowerShell)
- "Titelseite gespeichert" alert removed
- New chapter skips title/subtitle prompts, focuses title input
- Print button added to preview modal
- Corrupt `memoir.json` recovery shows user feedback banner
- All English strings localized to German
- Markdown help link added to toolbar

### Fixed in v1.3.0: First-run onboarding, corrupt memoir.json, uninstaller

- First-run onboarding wizard (title, subtitle, data directory)
- Corrupt/empty `memoir.json` gracefully recovered with backup
- Uninstaller kills MemDoc.exe before uninstall

### Fixed in v1.2.2: Default data directory resolved to Program Files

**Fix:** Changed default to `~/Documents/MemDoc` via `get_default_data_dir()`.

### Fixed in v1.2.1: Browser close kills Flask server

**Fix:** Browser-close detection with Chrome delegation fallback.
