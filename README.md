# MemDoc - Memoir Documentation Tool

A simple, elegant application for writing and formatting personal memoirs, designed for 1-2 users with a focus on simplicity and beautiful output.

## Purpose

MemDoc helps you write your life story with:
- **Clean writing interface** inspired by iA Writer
- **Automatic formatting** for professional-looking output
- **Timeline generation** from events mentioned throughout your memoir
- **Image support** with automatic print-quality checking
- **PDF export** with cover, table of contents, and page numbers

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url> memdoc
cd memdoc

# Install dependencies
pip install -r requirements.txt
```

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

## Basic Usage

1. **Writing**: Use the main editor to write your memoir in chapters
2. **Chapters**: Add chapters and subtitles using the chapter management panel
3. **Events**: Tag important events with dates for automatic timeline generation
4. **Images**: Drag and drop images - the app will warn if resolution is too low for printing
5. **Preview**: Click "Preview" to see how your memoir will look
6. **Export**: Generate a print-ready PDF with automatic formatting

## File Storage

Your memoir is saved as markdown files in the `data/` folder. Keep this folder synced with OneDrive (or any cloud storage) for automatic backup.

## Support

This is a personal project maintained for family use. If you encounter issues, check the documentation in the `docs/` folder or review the code - it's designed to be simple and readable.

## Philosophy

**Keep it simple.** This tool does one thing well: helps you write and format your memoirs beautifully. No feature bloat, no complexity, just focused writing.
