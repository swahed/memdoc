# MemDoc Architecture

## Overview

MemDoc is a single-user memoir writing application with a web-based UI and Python backend. It can run in a browser during development and as a desktop app in production.

## Technology Stack

### Backend
- **Python 3.10+**: Main programming language
- **Flask**: Lightweight web framework for API endpoints
- **Pillow**: Image processing and resolution checking
- **PyYAML**: YAML frontmatter parsing
- **PyInstaller**: Bundled as single .exe for distribution

### Frontend
- **Vanilla JavaScript**: No frameworks - keep it simple
- **HTML5/CSS3**: Semantic markup, modern CSS
- **Markdown-it** or similar: Client-side markdown preview (optional)

### Storage
- **Markdown files**: Content stored as `.md` files
- **YAML frontmatter**: Metadata (chapters, events) in file headers
- **Local filesystem**: Files saved to OneDrive-synced folder
- **JSON**: Configuration and prompts

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│              Browser / Desktop Window            │
│  ┌───────────────────────────────────────────┐  │
│  │          HTML/CSS/JS Frontend             │  │
│  │  - Editor interface (iA Writer style)     │  │
│  │  - Chapter navigation                     │  │
│  │  - Writing prompts sidebar                │  │
│  │  - Image upload UI                        │  │
│  └─────────────────┬─────────────────────────┘  │
│                    │ Fetch API                      │
│  ┌─────────────────▼─────────────────────────┐  │
│  │          Flask Backend (Python)           │  │
│  │  ┌────────────────────────────────────┐  │  │
│  │  │     API Routes                     │  │  │
│  │  │  /api/chapters                     │  │  │
│  │  │  /api/save                         │  │  │
│  │  │  /api/images                       │  │  │
│  │  │  /api/search                       │  │  │
│  │  │  /api/export/pdf                   │  │  │
│  │  └────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────┐  │  │
│  │  │     Core Modules                   │  │  │
│  │  │  - markdown_handler.py             │  │  │
│  │  │  - timeline.py                     │  │  │
│  │  │  - pdf_generator.py                │  │  │
│  │  │  - image_handler.py                │  │  │
│  │  │  - search.py                       │  │  │
│  │  └────────────────────────────────────┘  │  │
│  └─────────────────┬─────────────────────────┘  │
└────────────────────┼─────────────────────────────┘
                     │
         ┌───────────▼──────────┐
         │   Filesystem (OneDrive-synced)   │
         │   data/                          │
         │     memoir.json         # Metadata & chapter order │
         │     chapters/                    │
         │       ch001-early-years.md       │
         │       ch002-college-days.md      │
         │     images/                      │
         │       photo1.jpg                 │
         │       photo2.jpg                 │
         └──────────────────────────────────┘
```

## Directory Structure

```
memdoc/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # User-facing documentation
├── .claude                     # Claude Code context (auto-loaded)
├── .gitignore                  # Git ignore rules
│
├── docs/                       # Documentation
│   ├── ROADMAP.md              # Feature backlog
│   ├── ARCHITECTURE.md         # This file - technical design
│   ├── DEVELOPMENT.md          # Development guidelines
│   └── AI_CONTEXT.md           # Context for AI assistants (detailed)
│
├── core/                       # Python backend modules
│   ├── __init__.py
│   ├── markdown_handler.py     # Parse/save markdown + YAML frontmatter
│   ├── pdf_generator.py        # HTML preview and markdown conversion
│   ├── image_handler.py        # Image upload, resolution check, positioning
│   ├── config_manager.py       # User config at ~/.memdoc/config.json
│   ├── data_migrator.py        # Safe data directory migration
│   ├── updater.py              # GitHub release update checker
│   └── version.py              # VERSION constant, build type detection
│
├── static/                     # Frontend static files
│   ├── css/
│   │   ├── style.css          # Main stylesheet (iA Writer inspired)
│   │   └── print.css          # Print-specific styles for PDF
│   ├── js/
│   │   ├── app.js             # Main application logic
│   │   ├── editor.js          # Editor functionality
│   │   └── api.js             # API communication
│   └── images/
│       └── icon.png           # Application icon
│
├── templates/                  # HTML templates
│   ├── index.html             # Main editor interface
│   ├── preview.html           # Preview template
│   └── pdf_template.html      # PDF export template
│
├── prompts/
│   └── writing_prompts_de.json  # German writing prompts
│
├── build.py                   # PyInstaller build script
├── installer.iss              # Inno Setup installer script
│
└── ~/Documents/MemDoc/        # User data (configurable location)
    ├── memoir.json            # Memoir metadata & chapter order
    ├── chapters/              # Individual chapter files
    │   ├── ch001-early-years.md
    │   └── ...
    ├── images/                # Uploaded images
    └── deleted/               # Archived deleted chapters
```

## Data Model

### File Structure Overview

The memoir is stored as **one file per chapter** for better performance, organization, and version control:

- **memoir.json**: Memoir-level metadata and chapter ordering
- **chapters/**: Individual chapter markdown files
- **images/**: Uploaded images shared across chapters

### memoir.json Format

Contains memoir-level metadata and defines chapter order:

```json
{
    "title": "My Life Story",
    "author": "Author Name",
    "cover": {
        "title": "My Life Story",
        "subtitle": "A Memoir",
        "author": "Author Name",
        "image": "images/cover.jpg"
    },
    "chapters": [
        {
            "id": "ch001",
            "file": "ch001-early-years.md",
            "order": 1
        },
        {
            "id": "ch002",
            "file": "ch002-college-days.md",
            "order": 2
        },
        {
            "id": "ch003",
            "file": "ch003-meeting-dad.md",
            "order": 3
        }
    ],
    "created": "2024-01-15T10:30:00Z",
    "modified": "2024-03-20T15:45:00Z"
}
```

### Individual Chapter File Format

Each chapter is a separate markdown file with YAML frontmatter:

**File: chapters/ch001-early-years.md**
```markdown
---
id: ch001
title: "Early Years"
subtitle: "Growing up in the 1950s"
events:
  - date: "1952-03-15"
    title: "Born in Chicago"
  - date: "1957-09-01"
    title: "Started elementary school"
created: "2024-01-15T10:30:00Z"
modified: "2024-02-10T14:20:00Z"
wordCount: 1250
---

# Early Years
## Growing up in the 1950s

I was born on a cold March day in Chicago...

![Family photo](../images/family1952.jpg)
{: .img-center .img-medium}

The winters were harsh, but our home was filled with warmth...
```

**File: chapters/ch002-college-days.md**
```markdown
---
id: ch002
title: "College Days"
subtitle: "Finding my path"
events:
  - date: "1970-09-01"
    title: "Enrolled at State University"
  - date: "1972-06-15"
    title: "Graduated with honors"
created: "2024-01-20T11:00:00Z"
modified: "2024-03-15T09:30:00Z"
wordCount: 2100
---

# College Days
## Finding my path

University life opened new doors...
```

### Event Data Structure

Events are stored in each chapter's YAML frontmatter:
```yaml
events:
  - date: "YYYY-MM-DD"      # ISO format for easy sorting
    title: "Event name"      # Short description
```

The timeline is generated by:
1. Reading all chapter files
2. Extracting events from each chapter's frontmatter
3. Sorting all events chronologically
4. Generating timeline HTML with links back to chapters

### Image Metadata

Images can have positioning attributes:
```markdown
![Caption](images/photo.jpg)
{: .img-left .img-small}

<!-- Position classes: .img-left, .img-center, .img-right, .img-full -->
<!-- Size classes: .img-small, .img-medium, .img-large -->
```

## Key Design Decisions

### 1. Why Markdown?
- **Human-readable**: Mom can edit files directly if needed
- **Git-friendly**: Text-based, good diffs, version control
- **Portable**: Not locked into proprietary format
- **Simple**: Easy to parse and generate
- **Extensible**: YAML frontmatter for metadata

### 2. Why Flask + Chrome App Mode (not Electron)?
- **Keep it Python**: Single language for backend
- **Lighter**: Chrome app mode gives native-like feel without Electron overhead
- **Development workflow**: Run in browser during dev, Chrome app mode in production
- **Simple deployment**: No Node.js required

### 4. Why Local Storage (vs Database)?
- **Simplicity**: No database setup
- **Portability**: Files can be moved, backed up easily
- **OneDrive integration**: Automatic cloud sync
- **Transparency**: Users can see their data
- **Git-friendly**: Version control for free

### 6. Why One File Per Chapter (vs Single File)?
- **Performance**: Load only the chapter being edited
- **Git-friendly**: Clean diffs, changes to one chapter don't affect others
- **Organization**: Easy to reorder, rename, or archive chapters
- **Scalability**: Memoir can grow to hundreds of pages without performance issues
- **User experience**: Clearer chapter navigation and management

### 5. Why Fixed Prompts (vs AI API)?
- **Privacy**: No personal memoir content sent to external APIs
- **Reliability**: No API costs or rate limits
- **Offline**: Works without internet
- **Future-proof**: AI features planned for later (see `AI_FEATURES_BACKLOG.md`)

## Component Responsibilities

### markdown_handler.py
- Load and parse memoir.json (chapter order and metadata)
- Read individual chapter markdown files
- Extract YAML frontmatter from chapters
- Update chapter content and metadata
- Save changes back to appropriate chapter files
- Create new chapter files with proper naming (ch###-slug.md)
- Validate file structure and frontmatter
- Handle chapter reordering in memoir.json

### pdf_generator.py
- Convert markdown to HTML for preview
- Generate chapter preview HTML
- Generate full memoir preview HTML (cover + all chapters)
- Apply print-optimized CSS styles

### image_handler.py
- Process uploaded images
- Check resolution (warn if <300 DPI for print)
- Resize/optimize if needed
- Generate image references for markdown (relative paths)
- Manage image storage in data/images/
- Track image usage across chapters

### config_manager.py
- Load/save user config from `~/.memdoc/config.json`
- First-run detection
- Data directory management

### data_migrator.py
- Safe data migration between directories
- Integrity verification (file count + checksum sampling)
- Progress tracking via callback

### updater.py
- Check GitHub releases for updates
- Download installer with progress tracking
- Backup current version before update
- Apply update (launch Inno Setup in silent mode)
- Rollback to previous version

### version.py
- VERSION constant and RELEASE_DATE
- Build type detection (dev vs production)

## API Endpoints

### Content Management
- `GET /api/memoir` - Get memoir metadata (from memoir.json)
- `PUT /api/memoir` - Update memoir metadata
- `GET /api/chapters` - List all chapters (from memoir.json)
- `GET /api/chapters/<id>` - Get specific chapter content
- `POST /api/chapters` - Create new chapter file
- `PUT /api/chapters/<id>` - Update chapter content and metadata
- `DELETE /api/chapters/<id>` - Delete chapter file
- `POST /api/chapters/reorder` - Reorder chapters in memoir.json

### Images
- `POST /api/images/upload` - Upload image
- `GET /api/images/<filename>` - Retrieve image

### Settings & Config
- `GET /api/settings` - Get app settings
- `PUT /api/settings/preferences` - Update preferences
- `POST /api/settings/validate-path` - Validate data directory path
- `POST /api/settings/migrate-data` - Migrate data to new directory
- `POST /api/settings/browse-folder` - Open native folder picker
- `GET /api/config/is-first-run` - Check if first run
- `POST /api/config/initial-setup` - Complete initial setup

### Updates
- `GET /api/version` - Current version info
- `GET /api/updates/check` - Check for updates
- `POST /api/updates/download` - Start download
- `GET /api/updates/download/status` - Download progress
- `POST /api/updates/install` - Install and restart
- `GET /api/updates/backups` - List backups
- `POST /api/updates/rollback` - Rollback to version

### Statistics & Preview
- `GET /api/statistics` - Word count stats

## Security Considerations

Since this is a local, single-user application:
- **No authentication**: Runs locally, assumes trusted user
- **No CORS**: Local-only access
- **File access**: Limited to `data/` directory only
- **Image uploads**: Validate file types (jpg, png, gif only)
- **Path traversal**: Sanitize all file paths

## Performance Considerations

- **Chapter loading**: Load only the active chapter being edited (not entire memoir)
- **Lazy loading**: Load chapter list from memoir.json first, fetch content on-demand
- **Auto-save**: Debounce saves (2-3 seconds after typing stops), save only modified chapter
- **Search**: Index all chapters on startup, incremental updates when chapters change
- **Image preview**: Generate thumbnails for large images
- **PDF generation**: Background process, show progress indicator, stream chapters
- **Chapter caching**: Cache recently accessed chapters in memory
- **File watching**: Monitor chapters/ directory for external changes (OneDrive sync)

## Extensibility Points

Future features can hook into:
1. **Export formats**: Add new exporters (EPUB, DOCX)
2. **Themes**: CSS-based theming system
3. **Prompts**: Add AI-powered prompts via API
4. **Collaboration**: Add multi-user support
5. **Plugins**: Simple plugin system for custom features
