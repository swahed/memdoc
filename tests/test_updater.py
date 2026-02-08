"""
Unit tests for the update mechanism.

Tests update checking, downloading, backup/restore, and rollback functionality.
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Mock sys.frozen before importing updater
sys.frozen = True
sys.executable = str(Path.cwd() / "MemDoc.exe")

from core import updater
from core.version import VERSION


@pytest.fixture
def mock_github_release():
    """Mock GitHub API release response."""
    return {
        'tag_name': 'v1.2.0',
        'body': '## What\'s New\n- New feature\n- Bug fix',
        'published_at': '2025-12-27T10:00:00Z',
        'assets': [
            {
                'name': 'MemDoc-Setup.exe',
                'browser_download_url': 'https://github.com/test/memdoc/releases/download/v1.2.0/MemDoc-Setup.exe',
                'size': 28000000
            }
        ]
    }


@pytest.fixture
def temp_backup_dir(tmp_path, monkeypatch):
    """Create temporary backup directory."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    # Patch get_backup_dir to use temp directory
    monkeypatch.setattr('core.updater.get_backup_dir', lambda: backup_dir)

    return backup_dir


class TestUpdateChecking:
    """Tests for checking updates from GitHub."""

    @patch('core.updater.requests.get')
    @patch('core.updater.IS_TEST_BUILD', False)
    def test_check_for_updates_newer_version_available(self, mock_get, mock_github_release):
        """Test update check when newer version is available."""
        # Mock successful GitHub API response
        mock_response = Mock()
        mock_response.json.return_value = mock_github_release
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = updater.check_for_updates()

        assert result['update_available'] is True
        assert result['current_version'] == VERSION
        assert result['latest_version'] == '1.2.0'
        assert result['download_url'] is not None
        assert result['asset_size'] == 28000000
        assert result['error'] is None

    @patch('core.updater.requests.get')
    @patch('core.updater.IS_TEST_BUILD', False)
    def test_check_for_updates_no_newer_version(self, mock_get):
        """Test update check when current version is latest."""
        # Mock response with same version
        mock_response = Mock()
        mock_response.json.return_value = {
            'tag_name': f'v{VERSION}',
            'body': 'Current version',
            'published_at': '2025-12-26T10:00:00Z',
            'assets': []
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = updater.check_for_updates()

        assert result['update_available'] is False
        assert result['latest_version'] == VERSION

    @patch('core.updater.IS_TEST_BUILD', True)
    def test_check_for_updates_test_build(self):
        """Test that test builds cannot check for updates."""
        result = updater.check_for_updates()

        assert result['update_available'] is False
        assert result['error'] == 'Updates not available for test builds'

    @patch('core.updater.get_current_exe_path')
    @patch('core.updater.IS_TEST_BUILD', False)
    def test_check_for_updates_not_exe(self, mock_exe_path):
        """Test that updates only work for .exe builds."""
        mock_exe_path.return_value = None

        result = updater.check_for_updates()

        assert result['update_available'] is False
        assert result['error'] == 'Updates only available for compiled .exe builds'

    @patch('core.updater.requests.get')
    @patch('core.updater.IS_TEST_BUILD', False)
    def test_check_for_updates_network_error(self, mock_get):
        """Test handling of network errors."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")

        result = updater.check_for_updates()

        assert result['update_available'] is False
        assert 'Network error' in result['error']

    @patch('core.updater.requests.get')
    @patch('core.updater.IS_TEST_BUILD', False)
    def test_check_for_updates_no_exe_asset(self, mock_get):
        """Test handling when release has no .exe file."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'tag_name': 'v1.2.0',
            'body': 'Release notes',
            'published_at': '2025-12-27T10:00:00Z',
            'assets': []  # No assets
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = updater.check_for_updates()

        assert result['update_available'] is False
        assert 'No installer found' in result['error']

    @patch('core.updater.requests.get')
    @patch('core.updater.IS_TEST_BUILD', False)
    def test_check_for_updates_filters_test_exe(self, mock_get):
        """Test that TEST.exe files are ignored."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'tag_name': 'v1.2.0',
            'body': 'Release notes',
            'published_at': '2025-12-27T10:00:00Z',
            'assets': [
                {
                    'name': 'MemDoc-TEST.exe',
                    'browser_download_url': 'https://test.com/test.exe',
                    'size': 1000
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = updater.check_for_updates()

        assert result['update_available'] is False
        assert 'No installer found' in result['error']

    @patch('core.updater.requests.get')
    @patch('core.updater.IS_TEST_BUILD', False)
    def test_check_for_updates_prefers_setup_exe(self, mock_get):
        """Test that MemDoc-Setup.exe is preferred over bare MemDoc.exe."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'tag_name': 'v1.2.0',
            'body': 'Release notes',
            'published_at': '2025-12-27T10:00:00Z',
            'assets': [
                {
                    'name': 'MemDoc.exe',
                    'browser_download_url': 'https://test.com/MemDoc.exe',
                    'size': 27000000
                },
                {
                    'name': 'MemDoc-Setup.exe',
                    'browser_download_url': 'https://test.com/MemDoc-Setup.exe',
                    'size': 30000000
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = updater.check_for_updates()

        assert result['update_available'] is True
        assert 'MemDoc-Setup.exe' in result['download_url']
        assert result['asset_size'] == 30000000

    @patch('core.updater.requests.get')
    @patch('core.updater.IS_TEST_BUILD', False)
    def test_check_for_updates_falls_back_to_bare_exe(self, mock_get):
        """Test fallback to MemDoc.exe when MemDoc-Setup.exe is not available."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'tag_name': 'v1.2.0',
            'body': 'Release notes',
            'published_at': '2025-12-27T10:00:00Z',
            'assets': [
                {
                    'name': 'MemDoc.exe',
                    'browser_download_url': 'https://test.com/MemDoc.exe',
                    'size': 27000000
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = updater.check_for_updates()

        assert result['update_available'] is True
        assert 'MemDoc.exe' in result['download_url']


class TestDownload:
    """Tests for downloading updates."""

    @patch('core.updater.requests.get')
    def test_download_update_success(self, mock_get, temp_backup_dir):
        """Test successful update download."""
        # Mock successful download
        mock_response = Mock()
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content = Mock(return_value=[b'x' * 512, b'y' * 512])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Track progress callback
        progress_calls = []
        def progress_callback(downloaded, total):
            progress_calls.append((downloaded, total))

        success, file_path, error = updater.download_update(
            'https://test.com/MemDoc.exe',
            progress_callback
        )

        assert success is True
        assert file_path is not None
        assert file_path.exists()
        assert file_path.suffix == '.exe'
        assert error is None

        # Verify progress was tracked
        assert len(progress_calls) > 0
        assert progress_calls[-1] == (1024, 1024)  # Final progress

    @patch('core.updater.requests.get')
    def test_download_update_network_error(self, mock_get, temp_backup_dir):
        """Test download failure due to network error."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Connection lost")

        success, file_path, error = updater.download_update('https://test.com/MemDoc.exe')

        assert success is False
        assert file_path is None
        assert 'Download failed' in error


class TestExeIntegrity:
    """Tests for .exe integrity verification."""

    def test_verify_exe_integrity_valid(self, tmp_path):
        """Test verification of valid .exe file."""
        exe_file = tmp_path / "test.exe"

        # Create file with PE header (MZ) and sufficient size
        with open(exe_file, 'wb') as f:
            f.write(b'MZ')  # DOS header
            f.write(b'\x00' * (2 * 1024 * 1024))  # 2 MB file

        assert updater.verify_exe_integrity(exe_file) is True

    def test_verify_exe_integrity_too_small(self, tmp_path):
        """Test rejection of file that's too small."""
        exe_file = tmp_path / "test.exe"

        with open(exe_file, 'wb') as f:
            f.write(b'MZ')
            f.write(b'\x00' * 100)  # Only 100 bytes

        assert updater.verify_exe_integrity(exe_file) is False

    def test_verify_exe_integrity_wrong_header(self, tmp_path):
        """Test rejection of file without PE header."""
        exe_file = tmp_path / "test.exe"

        with open(exe_file, 'wb') as f:
            f.write(b'XX')  # Wrong header
            f.write(b'\x00' * (2 * 1024 * 1024))

        assert updater.verify_exe_integrity(exe_file) is False

    def test_verify_exe_integrity_nonexistent(self, tmp_path):
        """Test handling of nonexistent file."""
        exe_file = tmp_path / "nonexistent.exe"

        assert updater.verify_exe_integrity(exe_file) is False


class TestBackupAndRestore:
    """Tests for backup and restore functionality."""

    @patch('core.updater.get_current_exe_path')
    def test_backup_current_version_success(self, mock_exe_path, temp_backup_dir, tmp_path):
        """Test successful backup of current version."""
        # Create fake current exe
        current_exe = tmp_path / "MemDoc.exe"
        with open(current_exe, 'wb') as f:
            f.write(b'MZ')
            f.write(b'\x00' * 1000)

        mock_exe_path.return_value = current_exe

        success, error = updater.backup_current_version()

        assert success is True
        assert error is None

        # Verify backup was created
        backup_version_dir = temp_backup_dir / f'v{VERSION}'
        assert backup_version_dir.exists()
        assert (backup_version_dir / 'MemDoc.exe').exists()
        assert (backup_version_dir / 'backup_info.json').exists()

        # Verify metadata
        with open(backup_version_dir / 'backup_info.json', 'r') as f:
            metadata = json.load(f)
        assert metadata['version'] == VERSION
        assert 'backup_date' in metadata
        assert metadata['exe_size'] > 0

    @patch('core.updater.get_current_exe_path')
    def test_backup_current_version_not_exe(self, mock_exe_path, temp_backup_dir):
        """Test backup fails when not running as .exe."""
        mock_exe_path.return_value = None

        success, error = updater.backup_current_version()

        assert success is False
        assert 'Not running as .exe' in error

    def test_list_available_backups(self, temp_backup_dir):
        """Test listing available backups."""
        import time

        # Create mock backups with staggered times
        for i, version in enumerate(['1.0.0', '1.1.0', '1.2.0']):
            version_dir = temp_backup_dir / f'v{version}'
            version_dir.mkdir()

            metadata = {
                'version': version,
                'backup_date': f'2025-12-{20+i:02d}T10:00:00',
                'exe_path': f'/path/to/v{version}/MemDoc.exe',
                'exe_size': 27000000
            }

            with open(version_dir / 'backup_info.json', 'w') as f:
                json.dump(metadata, f)

            # Sleep briefly to ensure modification times differ
            time.sleep(0.01)

        backups = updater.list_available_backups()

        assert len(backups) == 3
        # Should be sorted by backup_date newest first
        assert backups[0]['version'] == '1.2.0'
        assert backups[1]['version'] == '1.1.0'
        assert backups[2]['version'] == '1.0.0'

    def test_list_available_backups_empty(self, temp_backup_dir):
        """Test listing backups when none exist."""
        backups = updater.list_available_backups()

        assert backups == []

    def test_cleanup_old_backups(self, temp_backup_dir):
        """Test cleanup of old backups."""
        # Create 5 backup versions
        for i in range(5):
            version_dir = temp_backup_dir / f'v1.{i}.0'
            version_dir.mkdir()

            # Touch file to set modification time
            (version_dir / 'backup_info.json').touch()

        updater.cleanup_old_backups(keep_count=2)

        # Should only have 2 most recent backups left
        remaining = [d for d in temp_backup_dir.iterdir() if d.is_dir()]
        assert len(remaining) == 2


class TestApplyUpdate:
    """Tests for applying updates via Inno Setup installer."""

    @patch('core.updater.subprocess.Popen')
    def test_apply_update_launches_installer(self, mock_popen, tmp_path):
        """Test that update launches Inno Setup installer with correct flags."""
        # Create fake installer file
        installer = tmp_path / "MemDoc-Setup.exe"
        with open(installer, 'wb') as f:
            f.write(b'MZ')
            f.write(b'\x00' * (2 * 1024 * 1024))

        success, error = updater.apply_update(installer)

        assert success is True
        assert error is None

        # Verify Popen was called with correct Inno Setup flags
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert str(installer) == call_args[0]
        assert '/SILENT' in call_args
        assert '/SUPPRESSMSGBOXES' in call_args
        assert '/CLOSEAPPLICATIONS' in call_args
        assert '/RESTARTAPPLICATIONS' in call_args

    def test_apply_update_invalid_installer(self, tmp_path):
        """Test update fails for invalid installer file."""
        installer = tmp_path / "invalid.exe"

        # Create invalid file (wrong header)
        with open(installer, 'wb') as f:
            f.write(b'XX')  # Wrong header

        success, error = updater.apply_update(installer)

        assert success is False
        assert 'integrity check' in error

    def test_apply_update_nonexistent_file(self, tmp_path):
        """Test update fails for nonexistent file."""
        installer = tmp_path / "nonexistent.exe"

        success, error = updater.apply_update(installer)

        assert success is False
        assert 'integrity check' in error


class TestRollback:
    """Tests for rollback functionality."""

    @patch('core.updater.get_current_exe_path')
    @patch('core.updater.apply_update')
    def test_rollback_to_version_success(self, mock_apply, mock_exe_path, temp_backup_dir, tmp_path):
        """Test successful rollback to previous version."""
        # Create fake current exe
        current_exe = tmp_path / "MemDoc.exe"
        mock_exe_path.return_value = current_exe

        # Create backup
        backup_version = '1.0.0'
        version_dir = temp_backup_dir / f'v{backup_version}'
        version_dir.mkdir()

        backup_exe = version_dir / 'MemDoc.exe'
        with open(backup_exe, 'wb') as f:
            f.write(b'MZ')
            f.write(b'\x00' * 1000)

        # Mock successful apply_update
        mock_apply.return_value = (True, None)

        success, error = updater.rollback_to_version(backup_version)

        assert success is True
        assert error is None

        # Verify apply_update was called with backup exe
        mock_apply.assert_called_once()
        call_args = mock_apply.call_args[0]
        assert str(call_args[0]) == str(backup_exe)

    @patch('core.updater.get_current_exe_path')
    def test_rollback_to_nonexistent_version(self, mock_exe_path, temp_backup_dir, tmp_path):
        """Test rollback fails for nonexistent backup."""
        mock_exe_path.return_value = tmp_path / "MemDoc.exe"

        success, error = updater.rollback_to_version('9.9.9')

        assert success is False
        assert 'not found' in error


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_current_exe_path_frozen(self):
        """Test exe path detection when frozen."""
        # sys.frozen is mocked at top of file
        exe_path = updater.get_current_exe_path()

        assert exe_path is not None
        assert exe_path.suffix == '.exe'

    @patch('core.updater.IS_TEST_BUILD', False)
    def test_get_backup_dir_production(self):
        """Test backup dir for production build."""
        backup_dir = updater.get_backup_dir()

        assert 'MemDoc' in str(backup_dir)
        assert 'MemDoc-Test' not in str(backup_dir)
        assert backup_dir.name == 'backups'

    @patch('core.updater.IS_TEST_BUILD', True)
    def test_get_backup_dir_test_build(self):
        """Test backup dir for test build."""
        backup_dir = updater.get_backup_dir()

        assert 'MemDoc-Test' in str(backup_dir)
        assert backup_dir.name == 'backups'
