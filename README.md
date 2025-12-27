# MemDoc - Memoir Documentation Tool

A simple, elegant desktop application for writing and organizing personal memoirs. Designed for non-technical users with a focus on simplicity and beautiful output.

## Features

### ✅ Available Now
- **Clean writing interface** - Distraction-free editor inspired by iA Writer
- **Chapter organization** - Dedicated title and subtitle fields
- **Auto-save** - Your work is saved as you type
- **German UI** - Fully localized for German-speaking users
- **Writing prompts** - 40+ prompts across 8 categories to inspire your writing
- **Cover page** - Beautiful cover with image and color customization
- **Image support** - Upload and embed photos with quality checking
- **PDF export** - Export individual chapters or entire memoir
- **Desktop app** - Runs as native-looking Windows application
- **Auto-update** - Built-in update mechanism (in development)
- **OneDrive integration** - Automatic cloud backup support

### 🚧 Planned
- Timeline generation from events
- Advanced formatting options
- Multi-language support (English, others)

## Quick Start

### For End Users

**Download the latest release:**
1. Visit [Releases](https://github.com/swahed/memdoc/releases/latest)
2. Download `MemDoc.exe`
3. Run the file (Windows may show a security warning - click "More info" → "Run anyway")
4. Choose a folder for your memoir (OneDrive recommended for automatic backup)

**Full documentation:** [docs/INSTALLATION.md](docs/INSTALLATION.md)

### For Developers

**Clone and run:**
```bash
git clone https://github.com/swahed/memdoc.git
cd memdoc
pip install -r requirements.txt
python app.py --browser
```

Open browser to: http://localhost:5000

**Build standalone .exe:**
```bash
pip install pyinstaller
python build.py
```

Output: `dist/MemDoc.exe`

## Documentation

### User Documentation
- **[Installation Guide](docs/INSTALLATION.md)** - Download, install, and setup
- **[Update Process](docs/UPDATE_PROCESS.md)** - How updates work

### Developer Documentation
- **[Build Process](docs/BUILD_PROCESS.md)** - Build .exe locally or via GitHub Actions
- **[Development Roadmap](docs/ROADMAP.md)** - Project phases and progress
- **[Cleanup Notes](docs/CLEANUP_NOTES.md)** - Maintenance and cleanup tasks
- **[Update Debug Notes](docs/UPDATE_MECHANISM_DEBUG_NOTES.md)** - Known issues with updates

## Tech Stack

- **Backend:** Python 3.10, Flask
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **Desktop:** Chrome/Edge in app mode (no Electron)
- **Storage:** Markdown files, YAML metadata
- **Build:** PyInstaller for standalone .exe
- **CI/CD:** GitHub Actions

## Project Structure

```
memdoc/
├── app.py                  # Flask application entry point
├── build.py               # PyInstaller build script
├── core/                  # Core Python modules
│   ├── markdown_handler.py
│   ├── pdf_generator.py
│   ├── updater.py        # Update mechanism
│   └── version.py        # Version info
├── static/               # CSS, JavaScript
├── templates/            # HTML templates
├── prompts/              # Writing prompts (German)
├── data-sample/          # Sample memoir data
├── tests/                # Unit and E2E tests
├── docs/                 # Documentation
└── .github/              # GitHub Actions workflows
```

## Development

### Running Tests
```bash
pytest                    # Run all tests
pytest --cov             # With coverage
pytest -v                # Verbose
```

### Creating a Release
```bash
# 1. Update version
edit core/version.py

# 2. Update changelog
edit CHANGELOG.md

# 3. Commit and tag
git commit -m "Bump version to 1.2.0"
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main v1.2.0
```

GitHub Actions automatically builds and publishes the release.

## Contributing

This is a personal project, but suggestions and bug reports are welcome via [Issues](https://github.com/swahed/memdoc/issues).

## License

[Choose your license - currently not specified]

## Credits

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [PyInstaller](https://pyinstaller.org/) - Standalone executable builder
- [WeasyPrint](https://weasyprint.org/) - PDF generation
- [Pillow](https://python-pillow.org/) - Image processing

Inspired by [iA Writer](https://ia.net/writer) for the clean writing interface.

## Support

- **Documentation:** See [docs/](docs/) folder
- **Issues:** [GitHub Issues](https://github.com/swahed/memdoc/issues)
- **Releases:** [GitHub Releases](https://github.com/swahed/memdoc/releases)
