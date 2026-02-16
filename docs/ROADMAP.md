# MemDoc Development Roadmap

## Current Status (v1.4.0)

**Completed:** Phases 1, 2, 3, 5 — app is ready for daily use.

**Testing:** 165 unit tests passing, 1 pre-existing failure, 8 E2E tests (skipped in CI).

```bash
py -m pytest tests/ -q --ignore=tests/test_updater.py -k "not test_get_prompts"
```

**Known Issues:**
- PowerShell console visible during folder pick (cosmetic, parked — all hiding approaches break the dialog)
- Uninstaller leaves `~/.memdoc` folder (parked, safer than risking data deletion)

---

## Phase 1: MVP - Core Writing Experience ✅
- Chapter management (create, edit, delete, reorder)
- Markdown editor with toolbar (bold, italic, headers, keyboard shortcuts)
- Auto-save, writing prompts sidebar, per-chapter word counts
- Safe delete (chapters moved to deleted folder)

## Phase 2: Localization & Polish ✅
- German localization (UI + 40 writing prompts)
- Cover page with image upload, color picker, live preview
- Full memoir preview (cover + all chapters), print support

## Phase 3: Deployment & Data Management ✅
- Inno Setup installer, GitHub Actions CI/CD
- In-app update mechanism (check, download, silent install, rollback)
- Configurable data directory with migration and integrity verification
- Single-instance enforcement (Windows named mutex)
- Multi-window support (Chrome/Edge app mode, BroadcastChannel sync)
- Installer kills running MemDoc before upgrade

## Phase 5: Images & Media ✅
- Drag-and-drop upload with resolution checking and quality warnings
- Positioning (left, center, right, full) and size options
- Auto-optimization, captions, filename sanitization

---

## Future Phases

### Phase 4: Enhanced Writing & Organization
- [ ] WYSIWYG editor (show formatting while editing)
- [ ] Full-text search across all chapters
- [ ] Event tagging system (inline markers with dates)
- [ ] Chapter navigation/outline view

### Phase 6: Timeline Generation
- [ ] Extract events from chapter metadata
- [ ] Generate chronological timeline view
- Depends on event tagging from Phase 4

### Phase 7: Export & Publishing
Chapter-level preview and print already work. Remaining:
- [ ] Automatic table of contents
- [x] Page numbering in PDF export and print (no number on cover page)
- [ ] Full memoir PDF export

### AI Features
See `AI_FEATURES_BACKLOG.md` for detailed designs:
- Contextual writing prompts (cursor-level)
- Chapter review assistant (gaps, structure, flow)
- Full book review (balance, consistency)
- Interview mode, photo-triggered memories

### Other Ideas (backlog)
- Edit existing image settings: click image button when cursor is on image markdown to re-open dialog with pre-filled caption/position/size
- Full-page cover background in PDF/print export (xhtml2pdf limitation)
- Paged scrolling preview with page numbers and visible chapter breaks (requires JavaScript-based pagination)
- Multiple memoir projects
- EPUB export
- Spell check integration
- Version history/snapshots
- Custom themes

---

## Development Principles

1. **Ship working software early**
2. **One feature at a time** — fully complete before moving on
3. **Test with mom** — real user feedback between phases
4. **Keep it simple** — resist feature creep
5. **Maintain code clarity** — readable by someone learning Python
