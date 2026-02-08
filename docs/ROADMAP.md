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

## Phase 2: Localization & Polish ✅ COMPLETE
**Goal: Make the app ready for mom to use with German UI and professional features**

### Features
- [x] German localization
  - Translate all UI elements (buttons, labels, messages)
  - Translate writing prompts (8 categories, 40 prompts)
  - i18n module with centralized translations
- [x] Cover page generation
  - UI to enter cover details (title, author, subtitle)
  - Optional cover image upload
  - Live preview of cover page
  - Smart color picker with automatic color extraction from images
  - Background color customization
- [x] Full memoir preview
  - Preview entire memoir (cover + all chapters)
  - PDF export for full memoir
  - Print-optimized layout with page breaks
- [x] UI improvements
  - Optimized chapter navigation sidebar
  - Text truncation with tooltips for long titles
  - 2x2 button grid layout for maximum title space
  - Always-visible action buttons (subtle opacity)
  - Efficient space utilization

**Deliverable:** Fully German interface with professional cover page and polished UI. ✅

**Status:** COMPLETE - Ready for mom to use

---

## Phase 3: Deployment & Data Management ✅ COMPLETE
**Goal: Safe distribution and updates for mom**

### Features
- [x] Configurable data storage location
  - Settings UI to choose data folder
  - OneDrive backup instructions
  - Data migration tool with backup option
  - Default: ~/Documents/MemDoc (user-writable)
- [x] Update mechanism
  - Check for updates from GitHub releases
  - In-app update banner and modal
  - Automatic data backup before update
  - Download progress with install & restart
- [x] Release process
  - GitHub Actions CI/CD: tag → PyInstaller → Inno Setup → GitHub Release
  - Semantic versioning
  - German release notes
- [x] Desktop experience
  - PyInstaller single-exe build
  - Inno Setup installer (German UI, shortcuts, Program Files)
  - Chrome app mode with process cleanup on close (v1.2.1)

**Deliverable:** Mom can safely install, update, and backup her work. ✅

**Status:** COMPLETE

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
- [x] ~~Process cleanup on window close~~ ✅ Fixed in v1.2.1 (Chrome delegation detection)
- [ ] AI-assisted writing features (LLM-based)
  - App provides rich context from user's writing — high potential
  - Writing suggestions removed from UI in v1.3.0 (shelved until proper MVP is designed)
  - Needs careful scoping: what prompts, what model, privacy, opt-in
  - **Note:** Do NOT just add generic prompts — design a thoughtful writing assistant
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
- Phase 2 → Localization + Cover ✅ (complete)
- Phase 3 → Deployment ✅ (complete)
- Phase 4 → Enhanced writing (independent)
- Phase 5 → Images ✅ (complete)
- Phase 6 → Timeline (needs event tagging from Phase 4)
- Phase 7 → PDF export (partially complete - full memoir done, TOC deferred)
- Phase 8 → Desktop wrapper (mostly done via Chrome app mode)

## Current Status

**Completed Phases:**
- ✅ Phase 1: MVP - Core writing experience with tests
- ✅ Phase 2: Localization & Polish - German UI, cover page, full memoir preview
- ✅ Phase 3: Deployment - Installer, updates, data management, CI/CD
- ✅ Phase 5: Images & Media with quality checks

**Immediate TODOs (v1.3.x):**
1. First-run onboarding wizard (title, subtitle, data dir, settings hint)
2. Handle corrupt/empty memoir.json gracefully
3. Fix uninstaller leaving MemDoc.exe behind

**Future Work:**
- Phase 4: Enhanced writing tools (WYSIWYG, search, event tagging)
- Phase 6: Timeline generation
- LLM-based writing assistant (needs MVP design)

**Testing Status:**
- ✅ 76 unit tests passing, 10 E2E tests (skipped in CI)
- 62% overall coverage, 96% on critical modules
- All features tested individually before commit
