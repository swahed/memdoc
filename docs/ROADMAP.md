# MemDoc Development Roadmap

## Implementation Strategy

Build in phases, delivering working functionality at each stage. Each phase should be fully functional before moving to the next.

---

## Phase 1: MVP - Core Writing Experience
**Goal: Get mom writing as soon as possible**

### Must-Have Features
- [x] Project structure and dependencies
- [ ] Basic text editor (markdown-based)
- [ ] Chapter management (add, edit, delete chapters)
- [ ] Subtitle support
- [ ] Basic text formatting (bold, italic, headers)
- [ ] Auto-save to markdown files in `data/` folder
- [ ] Simple browser-based UI (iA Writer aesthetic)

**Deliverable:** Mom can write and organize her memoir in chapters, with content automatically saved.

**Estimated complexity:** Simple - Core functionality, minimal features

---

## Phase 2: Enhanced Writing & Organization
**Goal: Add tools that make writing easier**

### Features
- [ ] Event tagging system (inline event markers with dates)
- [ ] Writing prompts sidebar (fixed prompts, no AI API)
- [ ] Full-text search across all chapters
- [ ] Chapter navigation/outline view
- [ ] Word count statistics

**Deliverable:** More productive writing experience with helpful tools.

**Estimated complexity:** Moderate - Several independent features

---

## Phase 3: Images & Media
**Goal: Support visual storytelling**

### Features
- [ ] Image upload (drag & drop)
- [ ] Resolution checking with warnings for low-quality images
- [ ] Automatic image positioning in document
- [ ] Basic positioning options (left, center, right, full-width)
- [ ] Image captions
- [ ] Image storage in `data/images/`

**Deliverable:** Full multimedia memoir support.

**Estimated complexity:** Moderate - File handling, image processing

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

## Phase 5: Export & Publishing
**Goal: Professional-quality output**

### Features
- [ ] HTML preview in browser
- [ ] Cover page generation
- [ ] Automatic table of contents
- [ ] Page numbering
- [ ] PDF export with print-quality settings
- [ ] Print-optimized styling (page breaks, margins, typography)

**Deliverable:** Print-ready PDF memoir.

**Estimated complexity:** Complex - PDF generation, print styling

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

**Active Phase:** Phase 1 - MVP
**Next Up:** Core writing experience
