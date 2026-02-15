# TODO — Next Session

**Date written:** 2026-02-15
**Current version:** v1.4.0
**Context:** All core bugs fixed. App is ready for handover to mom.

---

## Parked Issues

### PowerShell console visible during folder pick (cosmetic)

Clicking "Durchsuchen" opens a visible PowerShell window alongside the folder dialog. All hiding approaches were tried and break the dialog:

- `CREATE_NO_WINDOW`: dialog never appears (no window station)
- `STARTUPINFO SW_HIDE`: dialog hidden behind windows, spawns stuck processes
- `-WindowStyle Hidden`: console minimizes but dialog doesn't appear
- Win32 `GetConsoleWindow+ShowWindow`: spawns 2 processes, unreliable

**Decision:** Accept visible console. User rarely changes folders.

### Uninstaller leaves `~/.memdoc` folder

After uninstalling, `~/.memdoc/config.json` remains. Safer to leave it than risk deleting user data.

---

## Future Work (not needed for handover)

- **Phase 4:** WYSIWYG editor, full-text search, event tagging
- **Phase 6:** Timeline generation (needs event tagging)
- **Phase 7:** Full PDF export with table of contents
- **AI features:** See `AI_FEATURES_BACKLOG.md`

---

## Test Command

```bash
py -m pytest tests/ -q --ignore=tests/test_updater.py -k "not test_get_prompts"
```

165 passing, 1 pre-existing failure (`config_manager` default dir name).
