"""
Tests for Configuration Manager Module
"""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from core.config_manager import (
    get_config_path,
    get_default_config,
    load_config,
    save_config,
    validate_data_path,
    get_data_dir,
    get_directory_size,
    count_files
)


def test_get_config_path():
    """Test that config path points to user home directory."""
    config_path = get_config_path()
    assert config_path == Path.home() / ".memdoc" / "config.json"
    assert config_path.parts[-2:] == (".memdoc", "config.json")


def test_get_default_config():
    """Test that default config has all required fields."""
    config = get_default_config()

    assert "version" in config
    assert config["version"] == "1.0"
    assert "data_directory" in config
    assert "created_at" in config
    assert "last_migration" in config
    assert config["last_migration"] is None
    assert "preferences" in config
    assert "auto_save_interval" in config["preferences"]
    assert config["preferences"]["auto_save_interval"] == 2000


def test_save_and_load_config(tmp_path, monkeypatch):
    """Test saving and loading configuration."""
    # Mock config path to use tmp_path
    config_file = tmp_path / "config.json"
    monkeypatch.setattr("core.config_manager.get_config_path", lambda: config_file)

    # Create test config
    test_config = {
        "version": "1.0",
        "data_directory": str(tmp_path / "test_data"),
        "created_at": "2025-12-26T10:00:00",
        "last_migration": None,
        "preferences": {
            "auto_save_interval": 3000,
            "theme": "dark"
        }
    }

    # Save config
    save_config(test_config)

    # Verify file exists
    assert config_file.exists()

    # Load config
    loaded_config = load_config()

    # Verify loaded config matches saved config
    assert loaded_config["version"] == test_config["version"]
    assert loaded_config["data_directory"] == test_config["data_directory"]
    assert loaded_config["preferences"]["auto_save_interval"] == 3000
    assert loaded_config["preferences"]["theme"] == "dark"


def test_load_config_creates_default_if_missing(tmp_path, monkeypatch):
    """Test that load_config creates default config if file doesn't exist."""
    config_file = tmp_path / "config.json"
    monkeypatch.setattr("core.config_manager.get_config_path", lambda: config_file)

    # Ensure file doesn't exist
    assert not config_file.exists()

    # Load config (should create default)
    config = load_config()

    # Verify default config was created
    assert config_file.exists()
    assert "version" in config
    assert "data_directory" in config
    assert "preferences" in config


def test_load_config_with_existing_data_dir(tmp_path, monkeypatch):
    """Test that first-run config uses existing ./data if it has memoir.json."""
    config_file = tmp_path / "config.json"
    data_dir = tmp_path / "data"
    memoir_file = data_dir / "memoir.json"

    monkeypatch.setattr("core.config_manager.get_config_path", lambda: config_file)

    # Change to tmp_path as working directory
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Create data directory with memoir.json
        data_dir.mkdir()
        memoir_file.write_text('{"title": "Test"}')

        # Load config (first run)
        config = load_config()

        # Should use existing data directory
        assert Path(config["data_directory"]).name == "data"
    finally:
        os.chdir(original_cwd)


def test_validate_valid_writable_directory(tmp_path):
    """Test path validation with valid writable directory."""
    test_dir = tmp_path / "valid_dir"
    test_dir.mkdir()

    is_valid, message = validate_data_path(test_dir)

    assert is_valid is True
    assert "valid" in message.lower()
    assert "writable" in message.lower()


def test_validate_creates_directory_if_parent_exists(tmp_path):
    """Test that validation creates directory if parent exists."""
    test_dir = tmp_path / "new_dir"

    # Directory doesn't exist yet
    assert not test_dir.exists()

    is_valid, message = validate_data_path(test_dir)

    # Should be valid and directory should be created
    assert is_valid is True
    assert test_dir.exists()
    assert test_dir.is_dir()
    assert "created" in message.lower()


def test_validate_path_is_file_not_directory(tmp_path):
    """Test validation fails if path exists but is a file."""
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("test")

    is_valid, message = validate_data_path(test_file)

    assert is_valid is False
    assert "not a directory" in message.lower()


def test_validate_parent_does_not_exist():
    """Test validation fails if parent directory doesn't exist."""
    # Use a path with non-existent parent
    invalid_path = Path("/nonexistent/parent/child")

    is_valid, message = validate_data_path(invalid_path)

    assert is_valid is False
    assert "parent" in message.lower()


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Windows permissions work differently - read-only doesn't prevent writes"
)
def test_validate_readonly_directory(tmp_path):
    """Test validation fails if directory is read-only."""
    test_dir = tmp_path / "readonly_dir"
    test_dir.mkdir()

    # Make directory read-only
    import os
    import stat
    os.chmod(test_dir, stat.S_IRUSR | stat.S_IXUSR)

    try:
        is_valid, message = validate_data_path(test_dir)

        # Should fail validation
        assert is_valid is False
        assert "permission" in message.lower() or "write" in message.lower()
    finally:
        # Restore permissions for cleanup
        os.chmod(test_dir, stat.S_IRWXU)


def test_get_data_dir_returns_configured_path(tmp_path, monkeypatch):
    """Test that get_data_dir returns the configured directory."""
    config_file = tmp_path / "config.json"
    data_dir = tmp_path / "my_memoir_data"

    monkeypatch.setattr("core.config_manager.get_config_path", lambda: config_file)

    # Save config with custom data directory
    test_config = get_default_config()
    test_config["data_directory"] = str(data_dir)
    save_config(test_config)

    # Get data dir
    result = get_data_dir()

    # Should return configured path (resolved)
    assert result.resolve() == data_dir.resolve()


def test_get_data_dir_falls_back_to_default(tmp_path, monkeypatch):
    """Test that get_data_dir falls back to ./data if no config."""
    config_file = tmp_path / "nonexistent_config.json"
    monkeypatch.setattr("core.config_manager.get_config_path", lambda: config_file)

    # Change to tmp_path as working directory
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Get data dir (should create default config)
        result = get_data_dir()

        # Should resolve to ./data in current directory
        assert result.name == "data"
    finally:
        os.chdir(original_cwd)


def test_get_directory_size(tmp_path):
    """Test calculating directory size."""
    test_dir = tmp_path / "size_test"
    test_dir.mkdir()

    # Create files with known sizes
    (test_dir / "file1.txt").write_text("a" * 100)  # 100 bytes
    (test_dir / "file2.txt").write_text("b" * 200)  # 200 bytes

    # Create subdirectory with file
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("c" * 300)  # 300 bytes

    total_size = get_directory_size(test_dir)

    # Should be 600 bytes total
    assert total_size == 600


def test_get_directory_size_empty_directory(tmp_path):
    """Test directory size for empty directory."""
    test_dir = tmp_path / "empty_dir"
    test_dir.mkdir()

    size = get_directory_size(test_dir)
    assert size == 0


def test_get_directory_size_nonexistent_directory(tmp_path):
    """Test directory size for non-existent directory."""
    nonexistent = tmp_path / "does_not_exist"

    size = get_directory_size(nonexistent)
    assert size == 0


def test_count_files(tmp_path):
    """Test counting files in directory."""
    test_dir = tmp_path / "count_test"
    test_dir.mkdir()

    # Create files
    (test_dir / "file1.txt").write_text("test")
    (test_dir / "file2.md").write_text("test")

    # Create subdirectory with files
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("test")
    (subdir / "file4.json").write_text("test")

    count = count_files(test_dir)

    # Should count all files recursively (4 total)
    assert count == 4


def test_count_files_empty_directory(tmp_path):
    """Test file count for empty directory."""
    test_dir = tmp_path / "empty_dir"
    test_dir.mkdir()

    count = count_files(test_dir)
    assert count == 0


def test_count_files_nonexistent_directory(tmp_path):
    """Test file count for non-existent directory."""
    nonexistent = tmp_path / "does_not_exist"

    count = count_files(nonexistent)
    assert count == 0


def test_config_backward_compatibility(tmp_path, monkeypatch):
    """Test that old config files without new fields still work."""
    config_file = tmp_path / "config.json"
    monkeypatch.setattr("core.config_manager.get_config_path", lambda: config_file)

    # Create old-style config (missing some fields)
    old_config = {
        "data_directory": str(tmp_path / "data")
    }

    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(old_config, f)

    # Load config
    config = load_config()

    # Should have all fields (filled with defaults)
    assert "version" in config
    assert "data_directory" in config
    assert "preferences" in config
    assert config["data_directory"] == old_config["data_directory"]


def test_save_config_creates_directory(tmp_path, monkeypatch):
    """Test that save_config creates config directory if it doesn't exist."""
    config_dir = tmp_path / ".memdoc"
    config_file = config_dir / "config.json"

    monkeypatch.setattr("core.config_manager.get_config_path", lambda: config_file)

    # Directory doesn't exist yet
    assert not config_dir.exists()

    # Save config
    test_config = get_default_config()
    save_config(test_config)

    # Directory and file should be created
    assert config_dir.exists()
    assert config_file.exists()


def test_validate_path_with_spaces(tmp_path):
    """Test path validation with directory names containing spaces."""
    test_dir = tmp_path / "my memoir data"
    test_dir.mkdir()

    is_valid, message = validate_data_path(test_dir)

    assert is_valid is True
    assert test_dir.exists()


def test_validate_resolves_relative_paths(tmp_path):
    """Test that validation resolves relative paths to absolute."""
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        # Create directory
        test_dir = Path("relative_dir")
        test_dir.mkdir()

        # Validate relative path
        is_valid, message = validate_data_path(test_dir)

        assert is_valid is True
        # Path should exist as absolute
        assert test_dir.resolve().is_absolute()
    finally:
        os.chdir(original_cwd)


def test_validate_rejects_current_directory_when_check_not_current_true(tmp_path, monkeypatch):
    """Test that validation rejects current data directory when check_not_current=True."""
    test_dir = tmp_path / "current_data"
    test_dir.mkdir()

    # Mock get_data_dir to return test_dir
    monkeypatch.setattr('core.config_manager.get_data_dir', lambda: test_dir)

    # With check_not_current=True (default), should reject
    is_valid, message = validate_data_path(test_dir, check_not_current=True)

    assert is_valid is False
    assert "already your current data directory" in message.lower()


def test_validate_allows_current_directory_when_check_not_current_false(tmp_path, monkeypatch):
    """Test that validation allows current data directory when check_not_current=False."""
    test_dir = tmp_path / "current_data"
    test_dir.mkdir()

    # Mock get_data_dir to return test_dir
    monkeypatch.setattr('core.config_manager.get_data_dir', lambda: test_dir)

    # With check_not_current=False, should allow
    is_valid, message = validate_data_path(test_dir, check_not_current=False)

    assert is_valid is True
    assert "valid and writable" in message.lower()


def test_validate_rejects_non_empty_directory_when_check_not_current_true(tmp_path):
    """Test that validation rejects non-empty directory when check_not_current=True."""
    test_dir = tmp_path / "nonempty"
    test_dir.mkdir()

    # Create some files
    (test_dir / "file1.txt").write_text("content")
    (test_dir / "file2.txt").write_text("content")

    # With check_not_current=True (default), should reject non-empty dir
    is_valid, message = validate_data_path(test_dir, check_not_current=True)

    assert is_valid is False
    assert "already exists and contains" in message.lower()
    assert "2 items" in message.lower()


def test_validate_allows_non_empty_directory_when_check_not_current_false(tmp_path):
    """Test that validation allows non-empty directory when check_not_current=False."""
    test_dir = tmp_path / "nonempty"
    test_dir.mkdir()

    # Create some files
    (test_dir / "file1.txt").write_text("content")
    (test_dir / "file2.txt").write_text("content")

    # With check_not_current=False, should allow non-empty dir (for startup validation)
    is_valid, message = validate_data_path(test_dir, check_not_current=False)

    assert is_valid is True
    assert "valid and writable" in message.lower()


def test_validate_allows_empty_existing_directory_when_check_not_current_true(tmp_path):
    """Test that validation allows empty existing directory even when check_not_current=True."""
    test_dir = tmp_path / "empty_existing"
    test_dir.mkdir()

    # Empty directory should be allowed
    is_valid, message = validate_data_path(test_dir, check_not_current=True)

    assert is_valid is True
    assert "valid and writable" in message.lower()
