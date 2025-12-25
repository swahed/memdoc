# MemDoc - Memoir Documentation Tool

A simple, elegant application for writing and formatting personal memoirs, designed for 1-2 users with a focus on simplicity and beautiful output.

## Purpose

MemDoc helps you write your life story with:
- **Clean writing interface** inspired by iA Writer ✅
- **Chapter organization** with dedicated title and subtitle fields ✅
- **Auto-save** that saves your work as you type ✅
- **Writing prompts** to inspire your memoir writing ✅
- **Automatic formatting** for professional-looking output (planned)
- **Timeline generation** from events mentioned throughout your memoir (planned)
- **Image support** with automatic print-quality checking (planned)
- **PDF export** with cover, table of contents, and page numbers (planned)

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url> memdoc
cd memdoc

# Install core dependencies
python -m pip install Flask==3.0.0 PyYAML==6.0.1 markdown2==2.4.12
```

**Note:** Image processing (Pillow) and PDF generation (WeasyPrint) dependencies will be added in later phases. For now, the core memoir writing functionality works perfectly without them.

### Running the Application

**Browser mode (during development):**
```bash
python app.py --browser
```

**Desktop mode:**
```bash
python app.py
```

### Updating

```bash
git pull origin main
pip install -r requirements.txt
```

## Current Features

**✅ Available Now:**
1. **Create chapters**: Click "+ New Chapter" to add a new chapter to your memoir
2. **Write freely**: Clean, distraction-free editor with auto-save (saves 2 seconds after you stop typing)
3. **Markdown formatting**: Toolbar with bold, italic, and heading buttons (Ctrl+B, Ctrl+I shortcuts)
4. **Remove formatting**: Strip markdown formatting from selected text with one click
5. **Organize**: Navigate between chapters using the sidebar, reorder with up/down arrows
6. **Safe delete**: Deleted chapters are preserved in `data/chapters/deleted/` folder for recovery
7. **Get inspired**: Click the prompts button (bottom-right) for 40+ memoir writing prompts
8. **Track progress**: Word count displayed in the status bar and per-chapter in sidebar

**🚧 Coming Soon:**
- Event tagging and timeline generation
- Image uploads with resolution checking
- PDF export with professional formatting
- Desktop application mode

## File Storage

Your memoir is saved as markdown files in the `data/` folder. Keep this folder synced with OneDrive (or any cloud storage) for automatic backup.

### Deleted Chapters

When you delete a chapter, it's not permanently removed. Instead, it's moved to `data/chapters/deleted/` with a timestamp added to the filename. This means:
- You can always recover deleted chapters if needed
- No memoir content is ever truly lost
- Files are organized and don't clutter the main chapters folder

## Support

This is a personal project maintained for family use. If you encounter issues, check the documentation in the `docs/` folder or review the code - it's designed to be simple and readable.

## Philosophy

**Keep it simple.** This tool does one thing well: helps you write and format your memoirs beautifully. No feature bloat, no complexity, just focused writing.
