"""
Configuration Management Module

Manages application configuration stored in ~/.memdoc/config.json
Handles data directory path configuration and validation.
"""

import json
import os
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime


def get_config_path() -> Path:
    """
    Get the path to the application config file.

    Returns:
        Path to ~/.memdoc/config.json
    """
    return Path.home() / ".memdoc" / "config.json"


def get_default_config() -> Dict:
    """
    Get default configuration.

    Returns:
        Dictionary with default configuration values
    """
    return {
        "version": "1.0",
        "data_directory": str(Path("data").resolve()),
        "created_at": datetime.now().isoformat(),
        "last_migration": None,
        "preferences": {
            "auto_save_interval": 2000,
            "theme": "light"
        }
    }


def load_config() -> Dict:
    """
    Load configuration from ~/.memdoc/config.json.
    Creates default config if file doesn't exist.

    Returns:
        Dictionary containing configuration
    """
    config_path = get_config_path()

    if not config_path.exists():
        # First run - check if ./data exists with content
        data_dir = Path("data").resolve()
        memoir_file = data_dir / "memoir.json"

        # Create default config
        config = get_default_config()

        # If data directory exists with memoir.json, use it
        if memoir_file.exists():
            config["data_directory"] = str(data_dir)

        # Save config for future use
        save_config(config)
        return config

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Ensure all required fields exist (for backward compatibility)
        default_config = get_default_config()
        for key in default_config:
            if key not in config:
                config[key] = default_config[key]

        # Ensure preferences exist
        if "preferences" not in config:
            config["preferences"] = default_config["preferences"]

        return config
    except Exception as e:
        print(f"Warning: Error loading config from {config_path}: {e}")
        print("Using default configuration.")
        return get_default_config()


def save_config(config: Dict) -> None:
    """
    Save configuration to ~/.memdoc/config.json.

    Args:
        config: Dictionary containing configuration
    """
    config_path = get_config_path()

    # Ensure config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise IOError(f"Failed to save config to {config_path}: {e}")


def validate_data_path(path: Path, check_not_current: bool = True) -> Tuple[bool, str]:
    """
    Validate that a data directory path is suitable.

    Args:
        path: Path to validate
        check_not_current: If True, reject if path is current data directory (default True)

    Returns:
        Tuple of (is_valid, message)
        - is_valid: True if path is valid and usable
        - message: Descriptive message about the validation result
    """
    # Resolve to absolute path
    try:
        path = path.resolve()
    except Exception as e:
        return False, f"Invalid path: {e}"

    # Check if path exists
    if path.exists():
        # If exists, must be a directory
        if not path.is_dir():
            return False, "Path exists but is not a directory"

        # Check if it's the current data directory (only when selecting new location)
        if check_not_current:
            try:
                current_data_dir = get_data_dir()
                if path.resolve() == current_data_dir.resolve():
                    return False, "This is already your current data directory"
            except Exception:
                pass  # If we can't get current dir, continue

            # Check if directory is not empty (only when selecting new location)
            try:
                contents = list(path.iterdir())
                if contents:
                    # Directory has files - warn user
                    return False, f"Directory already exists and contains {len(contents)} items. Please choose an empty folder or use a different name."
            except Exception:
                pass

        # Check if writable
        test_file = path / ".memdoc_write_test"
        try:
            test_file.touch()
            test_file.unlink()
            return True, "Path is valid and writable"
        except PermissionError:
            return False, "Directory exists but is not writable (permission denied)"
        except Exception as e:
            return False, f"Cannot write to directory: {e}"
    else:
        # Path doesn't exist - check if parent exists and is writable
        parent = path.parent

        if not parent.exists():
            return False, f"Parent directory does not exist: {parent}"

        if not parent.is_dir():
            return False, f"Parent path is not a directory: {parent}"

        # Check if we can create directory in parent
        try:
            path.mkdir(parents=True, exist_ok=True)
            # Test write
            test_file = path / ".memdoc_write_test"
            test_file.touch()
            test_file.unlink()
            return True, "Path is valid and writable (directory created)"
        except PermissionError:
            return False, f"Cannot create directory (permission denied): {path}"
        except Exception as e:
            return False, f"Cannot create directory: {e}"


def get_data_dir() -> Path:
    """
    Get the configured data directory path.

    Returns:
        Path to the data directory
    """
    config = load_config()
    data_dir_str = config.get("data_directory", "data")
    return Path(data_dir_str).resolve()


def get_directory_size(path: Path) -> int:
    """
    Calculate total size of a directory in bytes.

    Args:
        path: Directory path

    Returns:
        Total size in bytes
    """
    total_size = 0

    if not path.exists() or not path.is_dir():
        return 0

    try:
        for item in path.rglob('*'):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                except (OSError, PermissionError):
                    # Skip files we can't access
                    pass
    except Exception:
        # Return what we have so far
        pass

    return total_size


def count_files(path: Path) -> int:
    """
    Count number of files in a directory (recursively).

    Args:
        path: Directory path

    Returns:
        Number of files
    """
    if not path.exists() or not path.is_dir():
        return 0

    try:
        return sum(1 for item in path.rglob('*') if item.is_file())
    except Exception:
        return 0
