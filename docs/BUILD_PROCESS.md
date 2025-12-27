# MemDoc Build Process

## Overview

MemDoc uses PyInstaller to create a standalone Windows executable. The build process is automated via GitHub Actions and can also be run locally.

## Build Types

### Production Build
- Executable name: `MemDoc.exe`
- Triggers: Tags matching `v*.*.*` (e.g., `v1.1.0`)
- Data directory: `%APPDATA%\MemDoc\`
- No test warnings or sample data

### Test Build
- Executable name: `MemDoc-TEST.exe`
- Triggers: Any branch except main/master or version tags
- Data directory: `%APPDATA%\MemDoc-Test\`
- Shows red warning banner
- Pre-loads sample memoir data

## Local Build

### Prerequisites
```bash
python 3.10+
pip install -r requirements.txt
pip install pyinstaller
```

### Build Command
```bash
python build.py
```

The script automatically detects build type based on git branch:
- `main`, `master`, or `vX.Y.Z` tags → Production build
- Any other branch → Test build

### Build Output
```
dist/
  MemDoc.exe          # Production (27+ MB)
  or
  MemDoc-TEST.exe     # Test build
build/                # Temporary build files (can be deleted)
MemDoc.spec           # PyInstaller spec file (generated)
```

## GitHub Actions Build

### Trigger
Push a version tag:
```bash
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

### Workflow Location
`.github/workflows/release.yml`

### Build Steps
1. Checkout code
2. Set up Python 3.10
3. Install dependencies from `requirements.txt`
4. Install PyInstaller
5. Run `build.py`
6. Extract version from tag
7. Create GitHub Release
8. Upload `MemDoc.exe` as release asset

### Build Environment
- Runner: `windows-latest`
- Python: 3.10
- Build time: ~2-3 minutes

## Build Configuration

### PyInstaller Options (`build.py`)

```python
args = [
    'app.py',                    # Entry point
    '--onefile',                 # Single .exe file
    '--windowed',                # No console window
    '--name=MemDoc',            # Output name
    '--clean',                   # Clean build
    '--noupx',                   # No UPX compression

    # Data files to include
    '--add-data=templates;templates',
    '--add-data=static;static',
    '--add-data=prompts;prompts',
    '--add-data=data-sample;data-sample',

    # Hidden imports (modules not auto-detected)
    '--hidden-import=jinja2',
    '--hidden-import=markupsafe',
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--hidden-import=yaml',
    '--hidden-import=weasyprint',
]
```

### Environment Variables Set During Build

Production build:
```python
os.environ['MEMDOC_TEST_BUILD'] = 'false'
os.environ['MEMDOC_BRANCH'] = 'main'
```

Test build:
```python
os.environ['MEMDOC_TEST_BUILD'] = 'true'
os.environ['MEMDOC_BRANCH'] = '<branch-name>'
```

These are baked into the .exe and read by `core/version.py`.

## Resource Path Handling

The app uses `get_resource_path()` to locate bundled files:

```python
def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # Running in normal Python environment
        base_path = Path(__file__).parent

    return base_path / relative_path
```

Usage:
```python
templates_path = get_resource_path('templates')
prompts_file = get_resource_path('prompts/writing_prompts_de.json')
```

## Versioning

### Version Location
`core/version.py`:
```python
VERSION = "1.1.0"
RELEASE_DATE = "2025-12-26"
GITHUB_REPO = "swahed/memdoc"
```

### Semantic Versioning
- **Major (X.0.0)**: Breaking changes, major new features
- **Minor (1.X.0)**: New features, backward-compatible
- **Patch (1.1.X)**: Bug fixes, small improvements

### Version Bumping Process
1. Update `VERSION` in `core/version.py`
2. Update `CHANGELOG.md` with changes
3. Commit changes
4. Create and push tag:
   ```bash
   git tag -a v1.2.0 -m "Release v1.2.0"
   git push origin v1.2.0
   ```

## Troubleshooting

### Build Fails Locally

**Error: Module not found**
```bash
pip install -r requirements.txt
pip install pyinstaller
```

**Error: Emoji encoding issues**
- Ensure console supports UTF-8
- Or use plain text in build output (already fixed)

### Build Fails in GitHub Actions

**Check Actions logs:**
https://github.com/swahed/memdoc/actions

**Common issues:**
- Missing dependency in `requirements.txt`
- PyInstaller can't find hidden imports
- Template/static files not included

**Fix:**
Add to `get_hidden_imports()` in `build.py` or update `--add-data` arguments.

### .exe Doesn't Run

**Missing DLL errors:**
- Install Visual C++ Redistributable
- Or add DLL to build via `--add-binary`

**Templates not found:**
- Check `get_resource_path()` implementation
- Verify `--add-data` includes all needed files

**.exe Too Large:**
- Current size: ~27 MB (acceptable)
- Includes Flask, WeasyPrint, Pillow, and dependencies
- To reduce: remove optional dependencies (PDF, images)

## Testing Builds

### Test Production Build Locally
```bash
# 1. Checkout main branch
git checkout main

# 2. Build
python build.py

# 3. Test .exe
dist/MemDoc.exe
```

### Test Build from Specific Version
```bash
# 1. Checkout tag
git checkout v1.1.0

# 2. Build
python build.py

# 3. Test
dist/MemDoc.exe
```

## CI/CD Pipeline

```
Code Push
    ↓
Git Tag (v1.2.0)
    ↓
GitHub Actions Trigger
    ↓
Windows Runner
    ↓
Install Python & Dependencies
    ↓
Run build.py
    ↓
Create GitHub Release
    ↓
Upload MemDoc.exe
    ↓
Users Download
```

## Build Artifacts

### Included in .exe
- Python runtime
- All Python dependencies
- Templates (HTML, CSS, JS)
- Static files
- Writing prompts
- Sample memoir data (for test builds)

### NOT Included
- User memoir data (stored in %APPDATA%)
- Configuration files
- Previous version backups
- Download cache

## Security Considerations

### Code Signing
**Current:** Not signed (Windows SmartScreen warning)

**Future:** Consider code signing certificate
- Removes SmartScreen warnings
- Increases user trust
- Costs ~$200-500/year

### Dependencies
All dependencies from PyPI, verified by pip.

### Update Mechanism
- Downloads only from GitHub Releases (HTTPS)
- Verifies downloaded .exe integrity
- Backs up before update
- Rollback available

## References

- PyInstaller documentation: https://pyinstaller.org/
- GitHub Actions for Python: https://docs.github.com/actions/automating-builds-and-tests/building-and-testing-python
- Semantic Versioning: https://semver.org/
