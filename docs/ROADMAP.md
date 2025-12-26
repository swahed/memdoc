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

## Phase 2: Localization & Cover Page 🎯 CURRENT PRIORITY
**Goal: Make the app ready for mom to use with German UI and cover page**

### Features
- [ ] German localization
  - Translate all UI elements (buttons, labels, messages)
  - Translate writing prompts
  - German date/time formatting
- [ ] Cover page generation
  - UI to enter cover details (title, author, subtitle)
  - Optional cover image upload
  - Live preview of cover page
  - Display cover page when opening memoir

**Deliverable:** Fully German interface with professional cover page.

**Status:** In Progress - Highest priority for stable release

---

## Phase 3: Deployment & Data Management
**Goal: Safe distribution and updates for mom**

### Features
- [ ] Configurable data storage location
  - Let user choose data folder outside repo
  - OneDrive backup instructions
  - Data migration tool
- [ ] Update mechanism
  - Check for updates from GitHub releases
  - In-app update button
  - Automatic data backup before update
  - Safety mechanisms to prevent data loss
- [ ] Release process
  - GitHub releases for stable versions
  - Version numbering
  - Release notes in German

**Deliverable:** Mom can safely install, update, and backup her work.

**Status:** Next priority after Phase 2

---

## Phase 4: Enhanced Writing & Organization
**Goal: Add tools that make writing easier**

### Features
- [ ] Visual feedback for markdown formatting (WYSIWYG editor)
  - Show bold/italic text rendered while editing
  - Visual indicators for images
  - Syntax highlighting for markdown
  - Options: EasyMDE (split-pane), Tiptap (inline), or custom lightweight solution
- [ ] Event tagging system (inline event markers with dates)
- [ ] Full-text search across all chapters
- [ ] Chapter navigation/outline view
- [ ] Enhanced word count statistics

**Deliverable:** More productive writing experience with helpful tools.

**Estimated complexity:** Moderate - Several independent features

---

## Phase 5: Images & Media ✅ COMPLETE
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

## Phase 6: Timeline Generation
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

## Phase 7: Export & Publishing (DEFERRED)
**Goal: Professional-quality output**

### Chapter-Level Export (✅ Complete)
- [x] HTML preview in browser
- [x] PDF export with print-quality settings
- [x] Print-optimized styling (page breaks, margins, typography)
- [x] Professional fonts (Georgia serif, Helvetica headings)
- [x] Image support in export (all positions and sizes)

### Full Memoir Export (Deferred)
- [ ] Automatic table of contents
- [ ] Page numbering across chapters
- [ ] Export entire memoir as one PDF (with cover page)
- [ ] Professional PDF generation via WeasyPrint

**Deliverable:** Chapter preview works. ✅

**Status:** Browser print functionality sufficient for now. Full PDF export deferred to later phase.

**Note:** Users can print individual chapters using browser's print-to-PDF feature.

---

## Phase 8: Desktop Experience
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
- [ ] AI-assisted writing features
  - Smart writing prompts based on context
  - Grammar and style suggestions
  - Story arc analysis
  - **Note:** Needs more conceptual work, privacy considerations
  - Must be opt-in with clear data handling
- [ ] Multiple memoir projects support
- [ ] Export to EPUB format
- [ ] Advanced image editing (crop, rotate)
- [ ] Spell check integration
- [ ] Version history/snapshots
- [ ] Custom themes/typography options
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

- Phase 1 → Required for all others ✅
- Phase 2 → Localization + Cover (current priority) 🎯
- Phase 3 → Deployment (needs Phase 2 complete)
- Phase 4 → Enhanced writing (independent)
- Phase 5 → Images ✅ (complete)
- Phase 6 → Timeline (needs event tagging from Phase 4)
- Phase 7 → PDF export (deferred)
- Phase 8 → Desktop wrapper (can be done anytime)

## Current Status

**Active Phase:** Phase 2 - Localization & Cover Page 🎯

**Completed Phases:**
- ✅ Phase 1: MVP - Core writing experience with tests
- ✅ Phase 5: Images & Media with quality checks

**Current Work:**
1. German UI translation (all elements + prompts)
2. Cover page generation with preview
3. Individual commits for each feature

**Next Up:**
- Phase 3: Deployment mechanism and data management
- Phase 4: Enhanced writing tools (WYSIWYG, search, etc.)

**Testing Status:**
- ✅ 50 unit tests, 62% overall coverage, 96% on critical modules
- Testing strategy: Test and commit each feature individually
