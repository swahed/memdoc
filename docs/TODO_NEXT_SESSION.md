# TODO — Next Session

**Current version:** v1.4.0
**Status:** All core features complete. App handed over to mom.

---

## Nothing blocking — pick from future work if needed

- **Phase 4:** WYSIWYG editor, full-text search, event tagging
- **Phase 6:** Timeline generation (needs event tagging)
- **Phase 7:** Full PDF export with table of contents
- **AI features:** See `AI_FEATURES_BACKLOG.md`
- **Known issues:** See `KNOWN_ISSUES.md` (cosmetic only)

## Test Command

```bash
py -m pytest tests/ -q --ignore=tests/test_updater.py -k "not test_get_prompts"
```

165 passing, 1 pre-existing failure (`config_manager` default dir name).
