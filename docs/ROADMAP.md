# MemDoc Development Roadmap

## Implementation Strategy

Build in phases, delivering working functionality at each stage. Each phase should be fully functional before moving to the next.

---

## Phase 1: MVP - Core Writing Experience ✅ COMPLETE
**Goal: Get mom writing as soon as possible**

### Must-Have Features
- [x] Project structure and dependencies
- [x] Basic text editor (markdown-based)
- [x] Chapter management (create, edit, delete, reorder chapters)
- [x] Subtitle support
- [x] Basic text formatting (bold, italic, headers) with toolbar
- [x] Auto-save to markdown files in `data/` folder
- [x] Simple browser-based UI (iA Writer aesthetic)
- [x] Writing prompts sidebar

### Bonus Features Added
- [x] Keyboard shortcuts (Ctrl+B, Ctrl+I)
- [x] Remove formatting button
- [x] Safe delete (chapters moved to deleted folder, not permanently removed)
- [x] Per-chapter word counts in sidebar
- [x] Comprehensive test coverage (50 tests, 62% overall, 96% on critical modules)

**Deliverable:** Mom can write and organize her memoir in chapters, with content automatically saved. ✅

**Status:** COMPLETE - All features implemented and tested

---

## Phase 2: Enhanced Writing & Organization
**Goal: Add tools that make writing easier**

### Features
- [ ] Visual feedback for markdown formatting (WYSIWYG editor)
  - Show bold/italic text rendered while editing
  - Visual indicators for images
  - Syntax highlighting for markdown
  - Options: EasyMDE (split-pane), Tiptap (inline), or custom lightweight solution
- [ ] Event tagging system (inline event markers with dates)
- [ ] Writing prompts improvements
  - Better categorization
  - Search/filter functionality
  - Random prompt suggestions
- [ ] Full-text search across all chapters
- [ ] Chapter navigation/outline view
- [ ] Enhanced word count statistics

**Deliverable:** More productive writing experience with helpful tools.

**Estimated complexity:** Moderate - Several independent features

---

## Phase 3: Images & Media ✅ COMPLETE
**Goal: Support visual storytelling**

### Features
- [x] Image upload (drag & drop)
- [x] Resolution checking with warnings for low-quality images
- [x] Automatic image positioning in document
- [x] Basic positioning options (left, center, right, full-width)
- [x] Image captions
- [x] Image storage in `data/images/`

**Bonus Features Added:**
- [x] Color-coded quality warnings (red/yellow/green)
- [x] Automatic image optimization (resize if too large)
- [x] Size control options (small, medium, large, full)
- [x] Smart filename sanitization with duplicate handling
- [x] Helpful tips panel with best practices
- [x] Direct drag-and-drop into editor

**Deliverable:** Full multimedia memoir support. ✅

**Status:** COMPLETE - All features implemented and tested (13 unit tests passing)

---

## Phase 4: Timeline Generation
**Goal: Automatic chronological overview**

### Features
- [ ] Extract events from chapter metadata
- [ ] Generate chronological timeline
- [ ] Timeline formatting for PDF export
- [ ] Timeline page placement (early in document)
- [ ] Date validation and sorting

**Deliverable:** Automatic timeline page showing life events in order.

**Estimated complexity:** Moderate - Data extraction and formatting

---

## Phase 5: Export & Publishing (PARTIALLY COMPLETE)
**Goal: Professional-quality output**

### Chapter-Level Export (✅ Complete)
- [x] HTML preview in browser
- [x] PDF export with print-quality settings
- [x] Print-optimized styling (page breaks, margins, typography)
- [x] Professional fonts (Georgia serif, Helvetica headings)
- [x] Image support in export (all positions and sizes)

### Full Memoir Export (Future)
- [ ] Cover page generation
- [ ] Automatic table of contents
- [ ] Page numbering across chapters
- [ ] Export entire memoir as one PDF

**Deliverable:** Chapter preview and export working. ✅

**Status:** Chapter-level preview/export complete. Full memoir export deferred.

**Note:** PDF export requires GTK libraries on Windows. Preview in browser works on all platforms.

---

## Phase 6: Desktop Experience
**Goal: Native application feel**

### Features
- [ ] Eel integration for desktop wrapper
- [ ] Window management (size, position persistence)
- [ ] Native file dialogs
- [ ] System tray integration (optional)
- [ ] Startup scripts for easy launching

**Deliverable:** Desktop application that feels native.

**Estimated complexity:** Simple - Wrapper around existing web app

---

## Future Enhancements
**Nice-to-have features for later consideration**

### Possible Features
- [ ] Multiple memoir projects support
- [ ] Export to EPUB format
- [ ] Advanced image editing (crop, rotate)
- [ ] Spell check integration
- [ ] Version history/snapshots
- [ ] Print directly from app
- [ ] Custom themes/typography options
- [ ] AI-assisted writing prompts (using API, privacy-aware)
- [ ] Collaboration features (comments, suggestions)
- [ ] Audio recording integration (oral history)

**Status:** Backlog - Only implement if requested

---

## Development Principles

1. **Ship working software early:** Phase 1 should be usable immediately
2. **One feature at a time:** Fully complete each feature before moving on
3. **Test with mom:** Get real user feedback between phases
4. **Keep it simple:** Resist feature creep
5. **Maintain code clarity:** Code should be readable by someone learning Python

## Dependencies Between Phases

- Phase 1 → Required for all others
- Phase 2 → Independent, can be built anytime after Phase 1
- Phase 3 → Independent, but needed before Phase 5 (PDF export)
- Phase 4 → Requires event tagging from Phase 2
- Phase 5 → Should be last major feature (depends on 1, 3, 4)
- Phase 6 → Can be done anytime, just wraps existing functionality

## Current Status

**Active Phase:** Phase 1 - MVP (Mostly Complete)
**Completed:**
- ✅ Project structure and dependencies
- ✅ Basic Flask/Eel app with iA Writer-inspired UI
- ✅ Chapter management (create, edit, delete, reorder)
- ✅ Auto-save to markdown files
- ✅ Writing prompts sidebar
- ✅ File persistence in OneDrive-synced folder

**Next Up When Resuming:**
- **PRIORITY**: Add unit tests and end-to-end tests before continuing development
- Complete remaining Phase 1 features (markdown formatting)
- Begin Phase 2 (event tagging, timeline, search)
