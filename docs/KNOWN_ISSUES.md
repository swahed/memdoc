# Known Issues

## Open Issues

### Preview rendering broken (v1.3.2 regression)

**Status:** Open — introduced in v1.3.2
**Severity:** High (core feature broken)

**Symptom:** Kapitel-Vorschau shows an error. The regex added in v1.3.2 to fix lenient bold/italic (`**word **` → `**word**`) in `pdf_generator.py` likely causes a Python exception.

**Root cause:** The regex `(\*{1,2})(\S(?:.*?\S)?)\s+(\1)` in `markdown_to_html()` and `generate_memoir_preview_html()` may be failing on certain content patterns.

**Fix:** Debug the regex or replace with simpler pre-processing. Test with the "Foosen" chapter content:
```
this is a text. I might **make ** this bold or even *underline *it though i *don't *know how to do that in markdown-
```

**Files:** `core/pdf_generator.py` (lines ~121 and ~525)

---

### Single-instance check not working

**Status:** Open — implemented in v1.3.1, not working in installed build
**Severity:** Medium

**Symptom:** Launching MemDoc.exe when already running opens a browser tab to the existing instance (good) but does NOT prevent the second server from starting (bad). Two servers may end up competing on the same port.

**Root cause:** The `is_port_in_use()` socket check in `app.py` may not work correctly in the installed build (timing, firewall, or binding behavior difference).

**Fix:** Investigate alternative approaches:
- File-based lock (`~/.memdoc/memdoc.lock`)
- Windows named mutex (`win32event.CreateMutex`)
- Check if the socket test works at all in the PyInstaller bundle

**Files:** `app.py` — `is_port_in_use()` and `main()`

---

### Folder picker shows visible PowerShell window

**Status:** Open (low priority)
**Severity:** Low (cosmetic annoyance)

**Symptom:** Clicking "Durchsuchen" in settings or onboarding opens a visible (empty) PowerShell window that closes when the folder dialog is dismissed.

**Fix:** Try adding `-WindowStyle Hidden` to the PowerShell command. If that doesn't work, use `subprocess.STARTUPINFO` with `STARTF_USESHOWWINDOW` to hide the console window.

**Files:** `app.py` — folder picker route

---

### Uninstaller leaves ~/.memdoc folder

**Status:** Parked (needs discussion)
**Severity:** Low

**Symptom:** After uninstalling, `~/.memdoc/config.json` remains on disk. The uninstaller only removes `C:\Program Files\MemDoc\`.

**Question:** Should the uninstaller delete user config and data? Risky — could delete the user's memoir data if the data dir is inside `~/.memdoc`. Probably better to leave it and document that the user can manually delete `~/.memdoc` and their data folder.

---

## Resolved Issues

### Fixed in v1.3.2: Bold/italic toolbar wraps trailing whitespace

**Root cause:** Double-clicking a word in the editor selects the trailing space. Bold/italic toolbar buttons wrapped the entire selection including the space, producing `**word **` which doesn't render in markdown.

**Fix:** `editor.js` `wrapSelection()` now trims whitespace from the selection and places it outside the markers: `**word** `.

### Fixed in v1.3.1: Multiple UX issues

- Folder picker opened new app instance (PyInstaller `sys.executable` issue — now uses PowerShell)
- "Titelseite gespeichert" alert removed
- New chapter skips title/subtitle prompts, focuses title input
- Print button added to preview modal
- Corrupt memoir.json recovery shows user feedback banner
- All English strings localized to German
- Markdown help link added to toolbar

### Fixed in v1.3.0: First-run onboarding, corrupt memoir.json, uninstaller

- First-run onboarding wizard (title, subtitle, data directory)
- Corrupt/empty memoir.json gracefully recovered with backup
- Uninstaller `[UninstallRun]` kills MemDoc.exe before uninstall

### Fixed in v1.2.2: Default data directory resolved to Program Files

**Root cause:** `Path("data").resolve()` resolved relative to CWD. When launched from `C:\Program Files\MemDoc\`, data dir became unwritable.

**Fix:** Changed default to `~/Documents/MemDoc` via `get_default_data_dir()`.

### Fixed in v1.2.1: Browser close kills Flask server

**Root cause:** Chrome delegation detection killed the wrong process.

**Fix:** Browser-close detection with Chrome delegation fallback.
