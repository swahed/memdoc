"""
Tests for folder picker subprocess script.
"""
import subprocess
import sys
from pathlib import Path
import pytest


def test_folder_picker_script_exists():
    """Test that folder picker script exists."""
    script_path = Path(__file__).parent.parent / 'scripts' / 'folder_picker.py'
    assert script_path.exists()
    assert script_path.is_file()


def test_folder_picker_script_syntax():
    """Test that folder picker script has valid Python syntax."""
    script_path = Path(__file__).parent.parent / 'scripts' / 'folder_picker.py'

    # Run script with --help to check if it's valid Python
    # Note: The script doesn't have --help, but we can at least import it
    result = subprocess.run(
        [sys.executable, '-m', 'py_compile', str(script_path)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Script has syntax errors: {result.stderr}"


def test_folder_picker_with_no_args():
    """Test folder picker runs without arguments (uses home dir)."""
    script_path = Path(__file__).parent.parent / 'scripts' / 'folder_picker.py'

    # We can't actually test the interactive dialog in CI,
    # but we can verify the script accepts no args without crashing on import
    # This is a smoke test
    result = subprocess.run(
        [sys.executable, '-c', f'import sys; sys.path.insert(0, "{script_path.parent.parent}"); from scripts.folder_picker import pick_folder'],
        capture_output=True,
        text=True,
        timeout=5
    )
    # Should not have import errors
    assert 'ImportError' not in result.stderr
    assert 'ModuleNotFoundError' not in result.stderr


def test_folder_picker_with_valid_initial_dir():
    """Test folder picker accepts valid initial directory argument."""
    script_path = Path(__file__).parent.parent / 'scripts' / 'folder_picker.py'
    home_dir = str(Path.home())

    # We can't test the actual dialog, but we can verify the script
    # accepts the argument without syntax errors
    # Note: This will hang waiting for user input, so we don't actually run it
    # Instead, we just verify the pick_folder function exists and is callable
    import sys
    sys.path.insert(0, str(script_path.parent.parent))
    from scripts.folder_picker import pick_folder

    assert callable(pick_folder)


def test_folder_picker_module_structure():
    """Test that folder picker has required structure."""
    script_path = Path(__file__).parent.parent / 'scripts' / 'folder_picker.py'

    # Read the script and verify it has required components
    content = script_path.read_text(encoding='utf-8')

    assert 'import tkinter' in content
    assert 'from tkinter import filedialog' in content
    assert 'def pick_folder' in content
    assert 'askdirectory' in content
    assert "if __name__ == '__main__':" in content
