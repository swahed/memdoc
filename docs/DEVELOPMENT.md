# MemDoc Development Guide

## Project Context

**MemDoc** is a personal memoir writing application for 1-2 users (primarily mom). This is NOT a commercial product.

- **Users**: Mom (retired computer specialist) + developer (her child)
- **Privacy**: Critical — memoir content is personal, no data leaves the machine
- **Simplicity**: More important than features or scalability
- **Aesthetic**: iA Writer inspired — clean, distraction-free, typography-focused

### Key Principles

- **Simplicity over features**: Resist feature creep, YAGNI
- **Readability over cleverness**: Code should be understandable by someone learning Python
- **Working over perfect**: Ship functional features, iterate later
- **Privacy-first**: No external API calls with memoir content, no telemetry

### What NOT to Do

- Don't add features not in ROADMAP.md without asking
- Don't use heavy frameworks (no React/Vue/Angular, no Django/FastAPI)
- Don't optimize prematurely or design for hypothetical scaling
- Don't send personal data to external APIs
- Don't make it complex — mom should be able to understand the code

---

## Development Environment

### Prerequisites
- Python 3.10+
- Git
- Chrome or Edge (for desktop mode)

### Setup

```bash
git clone https://github.com/swahed/memdoc.git
cd memdoc
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Running

```bash
# Browser mode (development)
python app.py --browser --debug

# Desktop mode (production-like, Chrome app mode)
python app.py
```

### Deployment (for mom)

Download `MemDoc-Setup.exe` from GitHub Releases. See `INSTALLATION.md`.

---

## Code Style

### Python
- PEP 8 compliant, clear naming, docstrings, type hints
- One concern per file (`image_handler.py`, not `utils.py`)

### JavaScript
- ES6+ syntax, vanilla JS (no frameworks)
- Comments explain "why", not "what"

### CSS
- Typography-first, minimal chrome, high contrast, generous whitespace

---

## Git Workflow

- **main**: Always working, deployable
- **feature branches**: For experimental or risky changes

### Release Process
1. Bump `VERSION` in `core/version.py`
2. Commit, tag (`git tag v1.X.X`), push with tags
3. CI builds `MemDoc-Setup.exe` and creates GitHub Release

---

## Testing

**165 unit tests passing**, 1 pre-existing failure, 8 E2E tests (skipped in CI).

```bash
# Run all tests
py -m pytest tests/ -q --ignore=tests/test_updater.py -k "not test_get_prompts"

# Run with coverage
py -m pytest --cov=core --cov-report=html tests/

# Run specific module
py -m pytest tests/test_data_migrator.py -v
```

### What to test
- `core/markdown_handler.py`: Chapter CRUD, metadata parsing
- `core/image_handler.py`: Image validation and processing
- `core/data_migrator.py`: Migration, integrity verification
- `tests/test_api.py`: API endpoint tests
- `tests/e2e/`: Playwright browser tests (need running server)

---

## Adding New Features

1. Check ROADMAP.md — is it planned?
2. Backend first (core module in `core/`)
3. Add API endpoint in `app.py`
4. Frontend (JS in `static/js/`, HTML in `templates/`)
5. Write tests
6. Test manually, then commit

---

## Debugging

```bash
# Python: run with debug mode (auto-reload, detailed errors)
python app.py --browser --debug

# Frontend: F12 → Console and Network tabs
```

### Common Issues
- **Port conflict**: Another app on port 5000
- **Stale templates**: Flask caches in non-debug mode — restart or use `--debug`
- **PyInstaller paths**: `sys.executable` = the .exe, not Python — use `get_resource_path()`

---

## Key Documents

- `ROADMAP.md` — Feature phases, current status, known issues
- `ARCHITECTURE.md` — Technical design, data model, API endpoints
- `BUILD_PROCESS.md` — PyInstaller + Inno Setup build pipeline
- `INSTALLATION.md` — End-user installation guide
- `AI_FEATURES_BACKLOG.md` — AI feature designs for future phases
