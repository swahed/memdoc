# Known Issues

## First Launch: "Fehler beim Laden der Kapitel: Failed to fetch"

**Status:** Open
**Since:** v1.2.0
**Severity:** Low (cosmetic - app works after dismissing)

**Symptom:** On first launch after fresh install, an error alert appears: "Fehler beim Laden der Kapitel: Failed to fetch"

**Likely cause:** The browser window opens before the Flask server is fully ready to accept connections. The frontend makes API calls immediately on load, but the server isn't listening yet.

**Possible fixes to investigate:**
- Increase the delay before opening the browser (currently 2 seconds in `app.py`)
- Add a health-check endpoint and have the frontend retry on failure
- Add a retry mechanism to `API.getChapters()` in `app.js`

## First Launch: No onboarding / empty state is confusing

**Status:** Open
**Since:** v1.2.0 (likely earlier, just not noticed)
**Severity:** Medium (UX - confusing for non-technical users)

**Symptom:** When opening the app for the first time with no chapters, the editor area shows disabled/greyed-out UI elements. There's no guidance on what to do next. The user doesn't know whether to create a chapter, select a folder, or what the first step is.

**Expected behavior:** A clean empty state with a friendly welcome message and clear instructions, e.g.:
- "Willkommen bei MemDoc! Erstelle dein erstes Kapitel mit dem + Button."
- Or a guided first-run wizard: pick data folder → create first chapter
- The editor area should be blank (not disabled-looking) until a chapter is selected

**Notes:**
- The startup workflow itself may need clarification (folder selection vs. chapter creation order)
- This is especially important for non-technical users (mom) who won't intuit the next step

## Settings dialog: "Fehler beim Laden der Einstellungen: Failed to fetch" + stuck on "Lädt..."

**Status:** Open
**Since:** v1.2.0 (likely related to first-launch fetch issue)
**Severity:** Medium (settings dialog is non-functional on first launch)

**Symptom:** Clicking the gear icon shows two error alerts "Fehler beim Laden der Einstellungen: Failed to fetch". After dismissing, the settings dialog opens but "Aktuelle Version" and "Aktueller Speicherort" both show "Lädt..." and never populate.

**Screenshot:** Desktop/2.png

**Likely cause:** Same root cause as the chapter fetch issue - Flask server not ready when frontend makes API calls. The settings modal calls `/api/settings` and `/api/version` which both fail.

**Possible fixes:**
- Same retry/health-check approach as the chapter loading fix
- Settings modal could retry loading when opened if initial load failed

## Uninstaller leaves MemDoc.exe behind

**Status:** Open
**Since:** v1.2.0
**Severity:** Low (cosmetic - app is removed from "Apps" list, but exe stays on disk)

**Symptom:** After uninstalling via Windows Settings or the uninstaller, the `C:\Program Files\MemDoc\` folder remains with `MemDoc.exe` still in it. The uninstaller itself and other files are removed. The app no longer appears in Windows "Apps & features".

**Likely cause:** The exe was still running (or locked by a process) when the uninstaller tried to delete it. Inno Setup's `CloseApplications=yes` may not be working reliably, or the app wasn't fully shut down before the uninstaller tried to remove it.

**Possible fixes to investigate:**
- Ensure the `AppMutex` in `installer.iss` matches a real mutex created by the app
- Add `[UninstallRun]` section to kill the process before uninstall
- Add `CloseApplicationsFilter` with the correct exe name
- Test whether the issue is timing-related (uninstaller not waiting long enough)

## Creating a chapter fails: "Fehler beim Erstellen des Kapitels: Failed to fetch"

**Status:** Open
**Since:** v1.2.0
**Severity:** High (core functionality broken on first launch)

**Symptom:** After entering title and subtitle for a new chapter, error alert appears: "Fehler beim Erstellen des Kapitels: Failed to fetch"

**Likely cause:** Same Flask server connectivity issue. All API calls are failing, not just reads. This suggests the server may not be starting at all when launched from Program Files, or the port is blocked, or a different root cause than just timing.

**Note:** This pattern of ALL fetches failing suggests it may not be a timing issue but something more fundamental - possibly the Flask server failing to start from the installed location (missing bundled files, wrong working directory, etc.). Need to check the console/logs.
