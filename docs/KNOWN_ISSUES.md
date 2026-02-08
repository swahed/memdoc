# Known Issues

## First Launch: No onboarding / empty state is confusing

**Status:** Open
**Since:** v1.2.0 (likely earlier, just not noticed)
**Severity:** Medium (UX - confusing for non-technical users)

**Symptom:** When opening the app for the first time with no chapters, the editor area shows disabled/greyed-out UI elements. There's no guidance on what to do next.

**Planned fix:** First-run onboarding wizard that asks for memoir title, subtitle, data directory, and tells the user where to find settings later.

## Uninstaller leaves MemDoc.exe behind

**Status:** Open
**Since:** v1.2.0
**Severity:** Low (cosmetic - app is removed from "Apps" list, but exe stays on disk)

**Symptom:** After uninstalling, `C:\Program Files\MemDoc\` folder remains with `MemDoc.exe` still in it.

**Likely cause:** The exe was still running (or locked by a process) when the uninstaller tried to delete it.

**Possible fixes to investigate:**
- Ensure the `AppMutex` in `installer.iss` matches a real mutex created by the app
- Add `[UninstallRun]` section to kill the process before uninstall
- Add `CloseApplicationsFilter` with the correct exe name

## Corrupt/empty memoir.json causes crash

**Status:** Open
**Since:** v1.2.0
**Severity:** Low (edge case from failed operations)

**Symptom:** An empty `memoir.json` file from a failed operation causes a JSON parse error that prevents the app from starting.

**Fix:** Add graceful handling — detect empty/corrupt file, create valid default, continue.

---

## Resolved Issues

### Fixed in v1.2.2: All API calls fail on first launch from installed exe

**Root cause:** Default data directory used `Path("data").resolve()` which resolved relative to CWD. When launched from `C:\Program Files\MemDoc\`, this became `C:\Program Files\MemDoc\data` — not writable by standard users. The Flask server exited immediately with a permission error.

**Fix:** Changed default data directory to `~/Documents/MemDoc` via `get_default_data_dir()` in `config_manager.py`.

**Issues this resolved:**
- "Fehler beim Laden der Kapitel: Failed to fetch"
- "Fehler beim Erstellen des Kapitels: Failed to fetch"
- "Fehler beim Laden der Einstellungen: Failed to fetch"
- Settings dialog stuck on "Lädt..."
