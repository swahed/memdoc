"""
Update Mechanism for MemDoc

Handles checking for updates from GitHub Releases, downloading new versions,
installing updates, and rolling back to previous versions.

Update Flow:
1. Check GitHub Releases API for newer version
2. Download new .exe with progress tracking
3. Backup current version and data
4. Replace .exe (requires restart)
5. Rollback available if needed
"""

import os
import sys
import json
import hashlib
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Callable, Tuple
from datetime import datetime
import requests
from packaging import version

from core.version import VERSION, GITHUB_REPO, IS_TEST_BUILD


def get_backup_dir() -> Path:
    """
    Get the backup directory for storing previous versions.

    Returns:
        Path to backup directory
    """
    if IS_TEST_BUILD:
        # Test builds: %APPDATA%/MemDoc-Test/backups/
        appdata = os.getenv('APPDATA', str(Path.home()))
        backup_dir = Path(appdata) / 'MemDoc-Test' / 'backups'
    else:
        # Production: %APPDATA%/MemDoc/backups/
        appdata = os.getenv('APPDATA', str(Path.home()))
        backup_dir = Path(appdata) / 'MemDoc' / 'backups'

    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def get_current_exe_path() -> Optional[Path]:
    """
    Get the path to the current executable.

    Returns:
        Path to current .exe, or None if running from Python
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return Path(sys.executable)
    else:
        # Running as Python script - no updates available
        return None


def check_for_updates() -> Dict:
    """
    Check GitHub Releases API for newer version.

    Returns:
        Dictionary with update information:
        {
            'update_available': bool,
            'current_version': str,
            'latest_version': str,
            'download_url': str,
            'release_notes': str,
            'release_date': str,
            'asset_size': int,
            'error': str (if error occurred)
        }
    """
    result = {
        'update_available': False,
        'current_version': VERSION,
        'latest_version': VERSION,
        'download_url': None,
        'release_notes': '',
        'release_date': '',
        'asset_size': 0,
        'error': None
    }

    # Test builds don't get updates
    if IS_TEST_BUILD:
        result['error'] = 'Updates not available for test builds'
        return result

    # Only works for .exe builds
    if not get_current_exe_path():
        result['error'] = 'Updates only available for compiled .exe builds'
        return result

    try:
        # Fetch latest release from GitHub
        api_url = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        release_data = response.json()

        # Extract version from tag (e.g., "v1.1.0" -> "1.1.0")
        tag_name = release_data.get('tag_name', '')
        latest_version = tag_name.lstrip('v')

        result['latest_version'] = latest_version
        result['release_notes'] = release_data.get('body', 'No release notes available')
        result['release_date'] = release_data.get('published_at', '')

        # Check if newer version available
        try:
            if version.parse(latest_version) > version.parse(VERSION):
                result['update_available'] = True
            else:
                result['update_available'] = False
                return result
        except Exception as e:
            result['error'] = f'Version comparison failed: {e}'
            return result

        # Find .exe asset in release
        assets = release_data.get('assets', [])
        exe_asset = None

        for asset in assets:
            if asset['name'].endswith('.exe') and 'TEST' not in asset['name']:
                exe_asset = asset
                break

        if not exe_asset:
            result['error'] = 'No .exe file found in latest release'
            result['update_available'] = False
            return result

        result['download_url'] = exe_asset['browser_download_url']
        result['asset_size'] = exe_asset['size']

        return result

    except requests.exceptions.RequestException as e:
        result['error'] = f'Network error: {e}'
        return result
    except Exception as e:
        result['error'] = f'Unexpected error: {e}'
        return result


def download_update(
    download_url: str,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Tuple[bool, Optional[Path], Optional[str]]:
    """
    Download new version .exe with progress tracking.

    Args:
        download_url: URL to download .exe from
        progress_callback: Optional callback function(bytes_downloaded, total_bytes)

    Returns:
        Tuple of (success, downloaded_file_path, error_message)
    """
    try:
        # Download to temp location
        backup_dir = get_backup_dir()
        temp_file = backup_dir / f'MemDoc-download-{datetime.now().strftime("%Y%m%d-%H%M%S")}.exe'

        # Stream download with progress
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(temp_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    if progress_callback:
                        progress_callback(downloaded_size, total_size)

        return True, temp_file, None

    except requests.exceptions.RequestException as e:
        return False, None, f'Download failed: {e}'
    except Exception as e:
        return False, None, f'Unexpected error during download: {e}'


def verify_exe_integrity(exe_path: Path) -> bool:
    """
    Verify downloaded .exe is valid (basic check).

    Args:
        exe_path: Path to .exe file

    Returns:
        True if file appears valid
    """
    try:
        # Check file exists and is not empty
        if not exe_path.exists() or exe_path.stat().st_size < 1024 * 1024:  # At least 1 MB
            return False

        # Check PE header (Windows .exe signature)
        with open(exe_path, 'rb') as f:
            header = f.read(2)
            if header != b'MZ':  # DOS header signature
                return False

        return True

    except Exception:
        return False


def backup_current_version() -> Tuple[bool, Optional[str]]:
    """
    Backup current .exe and data directory.

    Returns:
        Tuple of (success, error_message)
    """
    try:
        current_exe = get_current_exe_path()
        if not current_exe:
            return False, 'Not running as .exe - cannot backup'

        backup_dir = get_backup_dir()
        version_backup_dir = backup_dir / f'v{VERSION}'
        version_backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup .exe
        backup_exe = version_backup_dir / current_exe.name
        shutil.copy2(current_exe, backup_exe)

        # Save backup metadata
        metadata = {
            'version': VERSION,
            'backup_date': datetime.now().isoformat(),
            'exe_path': str(current_exe),
            'exe_size': current_exe.stat().st_size
        }

        metadata_file = version_backup_dir / 'backup_info.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        # Clean up old backups (keep last 2 versions)
        cleanup_old_backups()

        return True, None

    except Exception as e:
        return False, f'Backup failed: {e}'


def cleanup_old_backups(keep_count: int = 2):
    """
    Remove old backup versions, keeping only the most recent ones.

    Args:
        keep_count: Number of recent backups to keep
    """
    try:
        backup_dir = get_backup_dir()

        # Get all version backup directories
        version_dirs = [d for d in backup_dir.iterdir() if d.is_dir() and d.name.startswith('v')]

        # Sort by modification time (newest first)
        version_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)

        # Remove old backups
        for old_dir in version_dirs[keep_count:]:
            shutil.rmtree(old_dir, ignore_errors=True)

    except Exception:
        pass  # Don't fail update if cleanup fails


def apply_update(new_exe_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Replace current .exe with new version.

    Windows locks running .exe files, so we use a batch script workaround:
    1. Create update.bat script
    2. Script waits for app to exit
    3. Script replaces .exe
    4. Script restarts app
    5. Script deletes itself

    Args:
        new_exe_path: Path to new .exe file

    Returns:
        Tuple of (success, error_message)
    """
    try:
        current_exe = get_current_exe_path()
        if not current_exe:
            return False, 'Not running as .exe - cannot update'

        # Verify new .exe is valid
        if not verify_exe_integrity(new_exe_path):
            return False, 'Downloaded .exe failed integrity check'

        # Create update batch script
        backup_dir = get_backup_dir()
        update_script = backup_dir / 'update.bat'

        # Batch script that:
        # 1. Waits 2 seconds for app to close
        # 2. Replaces old .exe with new one
        # 3. Starts new .exe
        # 4. Deletes itself
        script_content = f'''@echo off
timeout /t 2 /nobreak >nul
move /y "{new_exe_path}" "{current_exe}" >nul 2>&1
if errorlevel 1 (
    echo Update failed - could not replace executable
    pause
    exit /b 1
)
start "" "{current_exe}"
del "%~f0"
'''

        with open(update_script, 'w') as f:
            f.write(script_content)

        # Launch update script and exit
        subprocess.Popen(
            ['cmd', '/c', str(update_script)],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        return True, None

    except Exception as e:
        return False, f'Failed to apply update: {e}'


def list_available_backups() -> list:
    """
    List all available backup versions.

    Returns:
        List of backup info dictionaries, sorted by date (newest first)
    """
    backups = []

    try:
        backup_dir = get_backup_dir()

        for version_dir in backup_dir.iterdir():
            if not version_dir.is_dir() or not version_dir.name.startswith('v'):
                continue

            metadata_file = version_dir / 'backup_info.json'
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    metadata['backup_path'] = str(version_dir)
                    backups.append(metadata)
                except Exception:
                    continue

        # Sort by backup date (newest first)
        backups.sort(key=lambda b: b.get('backup_date', ''), reverse=True)

    except Exception:
        pass

    return backups


def rollback_to_version(backup_version: str) -> Tuple[bool, Optional[str]]:
    """
    Restore a previous version from backup.

    Args:
        backup_version: Version to restore (e.g., "1.0.0")

    Returns:
        Tuple of (success, error_message)
    """
    try:
        current_exe = get_current_exe_path()
        if not current_exe:
            return False, 'Not running as .exe - cannot rollback'

        backup_dir = get_backup_dir()
        version_backup_dir = backup_dir / f'v{backup_version}'

        if not version_backup_dir.exists():
            return False, f'Backup for version {backup_version} not found'

        backup_exe = version_backup_dir / current_exe.name
        if not backup_exe.exists():
            return False, f'Backup .exe not found for version {backup_version}'

        # Use same update mechanism to replace .exe
        return apply_update(backup_exe)

    except Exception as e:
        return False, f'Rollback failed: {e}'
