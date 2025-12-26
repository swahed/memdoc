# Session Notes: Phase 3 - Configurable Data Storage with Folder Picker

**Date**: 2025-12-26
**Phase**: 3.1 - Data Storage Configuration
**Status**: ✅ Completed

## Overview

Implemented user-friendly folder selection with native OS folder picker and automatic subfolder creation for memoir data storage configuration.

## Features Implemented

### 1. Native Folder Picker (Subprocess Approach)

**Problem**: tkinter cannot run from Flask request threads
**Solution**: Separate subprocess script for folder picker dialog

**Files Created**:
- `scripts/folder_picker.py` - Standalone tkinter folder picker script
- `tests/test_folder_picker.py` - Unit tests for picker script

**Implementation**:
- Backend endpoint: `POST /api/settings/browse-folder`
- Uses `subprocess.run()` to launch picker in separate process
- Returns selected path or cancelled status
- Timeout: 5 minutes

### 2. Subfolder Creation UX

**User Flow**:
1. Click "Durchsuchen" → Select parent folder (e.g., OneDrive/Documents)
2. Dialog appears → Enter subfolder name (default: "MemDoc")
3. Live preview shows full path
4. Auto-fills path input field

**Files Modified**:
- `templates/index.html` - Added subfolder prompt modal
- `static/js/app.js` - Added subfolder prompt logic (3 new methods)
- `static/css/style.css` - Modal styling

**Methods Added**:
- `showSubfolderPrompt()` - Shows dialog with live path preview
- `confirmSubfolder()` - Combines parent + subfolder paths
- `closeSubfolderPrompt()` - Closes dialog

### 3. Simplified Migration UX

**Before**: Browse → Validate → Migrate (3 clicks)
**After**: Browse → Migrate (2 clicks - auto-validates)

**Changes**:
- Removed "Prüfen" (Validate) button
- "Daten verschieben" button always visible (disabled initially)
- Auto-validation on migrate button click
- Clear tooltips for button states

### 4. Enhanced Path Validation

**New Parameter**: `validate_data_path(path, check_not_current=True)`

**Validation Rules**:

**When selecting new location** (`check_not_current=True`):
- ❌ Reject if same as current data directory
- ❌ Reject if directory exists and not empty
- ✓ Allow if directory exists but empty
- ✓ Allow new directories (auto-created)

**When validating at startup** (`check_not_current=False`):
- ✓ Allow current data directory with files
- Only check: is directory, is writable

**Files Modified**:
- `core/config_manager.py` - Added `check_not_current` parameter
- `app.py` - Use `check_not_current=False` at startup

## Testing

### New Tests Created

**1. Folder Picker Tests** (`tests/test_folder_picker.py`):
- Script exists and has valid syntax
- Module structure verification
- Import/callable checks
- **5 tests** - All passed

**2. Validation Parameter Tests** (`tests/test_config_manager.py`):
- Reject current directory when `check_not_current=True`
- Allow current directory when `check_not_current=False`
- Reject non-empty when `check_not_current=True`
- Allow non-empty when `check_not_current=False`
- Allow empty existing directory
- **5 tests** - All passed

**3. Browse Folder API Tests** (`tests/test_api.py`):
- Success case (mocked subprocess)
- Cancelled case (mocked subprocess)
- **2 tests** - All passed

**Total Test Count**: 154 tests (143 passed, 11 skipped)

## Technical Details

### Subprocess Implementation

```python
# app.py browse_folder endpoint
script_path = Path(__file__).parent / 'scripts' / 'folder_picker.py'
cmd = [sys.executable, str(script_path)]
if initial_dir:
    cmd.append(initial_dir)

result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
selected_folder = result.stdout.strip()
```

### Validation Logic

```python
def validate_data_path(path: Path, check_not_current: bool = True):
    if path.exists():
        if check_not_current:
            # Check if current directory
            if path == get_data_dir():
                return False, "Already current directory"
            # Check if not empty
            if list(path.iterdir()):
                return False, f"Contains {len(contents)} items"
        # Check writable
        return True, "Valid and writable"
```

## Files Changed

**Created** (6 files):
- `scripts/folder_picker.py`
- `tests/test_folder_picker.py`
- `docs/SESSION_NOTES_PHASE3_FOLDER_PICKER.md`

**Modified** (7 files):
- `app.py` - Browse endpoint + validation parameter
- `core/config_manager.py` - Enhanced validation
- `templates/index.html` - Subfolder modal + removed Prüfen button
- `static/js/app.js` - Subfolder logic + simplified UX
- `static/js/api.js` - browseFolder method
- `static/css/style.css` - Modal styling
- `tests/test_config_manager.py` - 5 new tests
- `tests/test_api.py` - 2 new tests

## Key Improvements

1. **User-Friendly**: Native OS folder picker (familiar UX)
2. **Guided Creation**: Subfolder prompt prevents manual folder creation
3. **Safety**: Prevents accidental data loss (empty folder checks)
4. **Simplified**: One less click (auto-validation)
5. **Robust**: Subprocess approach solves threading issues
6. **Well-Tested**: 12 new tests with mocking

## Known Limitations

- Folder picker timeout: 5 minutes (configurable)
- Cannot create nested subfolders in UI (only one level)
- Requires tkinter (included in Python standard library)

## Next Steps

- Phase 3.2: Release versioning
- Phase 3.3: Update mechanism
- Consider: Multi-level folder creation in picker

## Commit Message

```
feat: Add native folder picker with subfolder creation UX

- Implement subprocess-based folder picker to avoid threading issues
- Add subfolder creation dialog with live path preview
- Simplify migration UX (remove separate validation button)
- Enhance path validation with check_not_current parameter
- Prevent accidental data loss (reject non-empty folders)
- Add 12 new tests (folder picker, validation, API)

Files: +3 created, 7 modified
Tests: 154 total (143 passed, 11 skipped)
```
