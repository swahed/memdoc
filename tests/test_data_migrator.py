"""
Tests for Data Migration Module
"""

import pytest
import json
from pathlib import Path
from core.data_migrator import (
    calculate_directory_size,
    calculate_file_checksum,
    verify_migration,
    migrate_data_directory,
    estimate_migration_time
)


@pytest.fixture
def populated_data_dir(tmp_path):
    """Create a populated data directory for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Create memoir.json
    memoir_data = {
        "title": "Test Memoir",
        "author": "Test Author",
        "chapters": [
            {"id": "ch001", "file": "ch001-test.md", "order": 1}
        ]
    }
    (data_dir / "memoir.json").write_text(json.dumps(memoir_data))

    # Create chapters directory with file
    chapters_dir = data_dir / "chapters"
    chapters_dir.mkdir()
    (chapters_dir / "ch001-test.md").write_text("# Test Chapter\n\nContent here")

    # Create images directory with files
    images_dir = data_dir / "images"
    images_dir.mkdir()
    (images_dir / "test1.jpg").write_bytes(b"fake_image_data_1" * 100)
    (images_dir / "test2.png").write_bytes(b"fake_image_data_2" * 100)

    return data_dir


def test_calculate_directory_size(tmp_path):
    """Test calculating directory size."""
    test_dir = tmp_path / "size_test"
    test_dir.mkdir()

    # Create files with known sizes
    (test_dir / "file1.txt").write_text("a" * 100)
    (test_dir / "file2.txt").write_text("b" * 200)

    # Create subdirectory with file
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("c" * 300)

    size = calculate_directory_size(test_dir)

    assert size == 600


def test_calculate_directory_size_empty(tmp_path):
    """Test directory size for empty directory."""
    test_dir = tmp_path / "empty"
    test_dir.mkdir()

    size = calculate_directory_size(test_dir)
    assert size == 0


def test_calculate_file_checksum(tmp_path):
    """Test calculating file checksum."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    checksum1 = calculate_file_checksum(test_file)
    checksum2 = calculate_file_checksum(test_file)

    # Same file should have same checksum
    assert checksum1 == checksum2
    assert len(checksum1) == 32  # MD5 hex digest length

    # Different content should have different checksum
    test_file.write_text("different content")
    checksum3 = calculate_file_checksum(test_file)
    assert checksum3 != checksum1


def test_verify_migration_success(populated_data_dir, tmp_path):
    """Test verification of successful migration."""
    destination = tmp_path / "destination"
    destination.mkdir()

    # Copy all files to destination
    import shutil
    for item in populated_data_dir.rglob('*'):
        if item.is_file():
            relative_path = item.relative_to(populated_data_dir)
            dest_file = destination / relative_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_file)

    is_valid, message = verify_migration(populated_data_dir, destination)

    assert is_valid is True
    assert "successfully" in message.lower()


def test_verify_migration_missing_memoir_json(populated_data_dir, tmp_path):
    """Test verification fails if memoir.json is missing."""
    destination = tmp_path / "destination"
    destination.mkdir()

    # Copy files but skip memoir.json
    import shutil
    for item in populated_data_dir.rglob('*'):
        if item.is_file() and item.name != "memoir.json":
            relative_path = item.relative_to(populated_data_dir)
            dest_file = destination / relative_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_file)

    is_valid, message = verify_migration(populated_data_dir, destination)

    assert is_valid is False
    assert "memoir.json" in message.lower()


def test_verify_migration_missing_chapters_dir(populated_data_dir, tmp_path):
    """Test verification fails if chapters/ directory is missing."""
    destination = tmp_path / "destination"
    destination.mkdir()

    # Copy only memoir.json and images
    import shutil
    memoir_file = populated_data_dir / "memoir.json"
    shutil.copy2(memoir_file, destination / "memoir.json")

    (destination / "images").mkdir()

    is_valid, message = verify_migration(populated_data_dir, destination)

    assert is_valid is False
    assert "chapters" in message.lower()


def test_verify_migration_file_count_mismatch(populated_data_dir, tmp_path):
    """Test verification fails if file counts don't match."""
    destination = tmp_path / "destination"
    destination.mkdir()

    # Copy all files except one image (skip one image file, not memoir.json)
    import shutil
    skipped = False
    for item in populated_data_dir.rglob('*'):
        if item.is_file():
            # Skip one of the image files
            if not skipped and item.parent.name == "images":
                skipped = True
                continue

            relative_path = item.relative_to(populated_data_dir)
            dest_file = destination / relative_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_file)

    is_valid, message = verify_migration(populated_data_dir, destination)

    assert is_valid is False
    assert "mismatch" in message.lower()


def test_migrate_empty_directory(tmp_path):
    """Test migrating empty data directory."""
    source = tmp_path / "source"
    source.mkdir()

    destination = tmp_path / "destination"

    success, stats = migrate_data_directory(source, destination)

    assert success is True
    assert stats['files_copied'] == 0
    assert stats['bytes_copied'] == 0
    assert destination.exists()


def test_migrate_with_files(populated_data_dir, tmp_path):
    """Test migrating directory with memoir data."""
    destination = tmp_path / "destination"

    success, stats = migrate_data_directory(
        populated_data_dir,
        destination,
        keep_backup=False
    )

    assert success is True
    assert stats['files_copied'] > 0
    assert stats['bytes_copied'] > 0
    assert destination.exists()
    assert (destination / "memoir.json").exists()
    assert (destination / "chapters").exists()
    assert (destination / "images").exists()


def test_migration_preserves_structure(populated_data_dir, tmp_path):
    """Test that directory structure is preserved."""
    destination = tmp_path / "destination"

    success, stats = migrate_data_directory(
        populated_data_dir,
        destination,
        keep_backup=False
    )

    assert success is True

    # Verify structure
    assert (destination / "memoir.json").is_file()
    assert (destination / "chapters").is_dir()
    assert (destination / "chapters" / "ch001-test.md").is_file()
    assert (destination / "images").is_dir()
    assert (destination / "images" / "test1.jpg").is_file()
    assert (destination / "images" / "test2.png").is_file()


def test_migration_with_backup(populated_data_dir, tmp_path):
    """Test that backup is created when keep_backup=True."""
    destination = tmp_path / "destination"

    success, stats = migrate_data_directory(
        populated_data_dir,
        destination,
        keep_backup=True
    )

    assert success is True
    assert stats['backup_location'] is not None

    # Verify backup exists
    backup_path = Path(stats['backup_location'])
    assert backup_path.exists()
    assert backup_path.is_dir()
    assert "backup" in backup_path.name.lower()

    # Original source should not exist (renamed to backup)
    assert not populated_data_dir.exists()


def test_migration_without_backup(populated_data_dir, tmp_path):
    """Test that source is removed when keep_backup=False."""
    destination = tmp_path / "destination"

    success, stats = migrate_data_directory(
        populated_data_dir,
        destination,
        keep_backup=False
    )

    assert success is True
    assert stats['backup_location'] is None

    # Source should not exist
    assert not populated_data_dir.exists()

    # Destination should exist with all files
    assert destination.exists()


def test_migration_integrity_verification(populated_data_dir, tmp_path):
    """Test that file contents match after migration."""
    destination = tmp_path / "destination"

    # Get checksums of source files before migration
    source_checksums = {}
    for item in populated_data_dir.rglob('*'):
        if item.is_file():
            relative_path = item.relative_to(populated_data_dir)
            source_checksums[str(relative_path)] = calculate_file_checksum(item)

    success, stats = migrate_data_directory(
        populated_data_dir,
        destination,
        keep_backup=True
    )

    assert success is True

    # Verify checksums match in destination
    for relative_path_str, source_checksum in source_checksums.items():
        dest_file = destination / relative_path_str
        assert dest_file.exists()
        dest_checksum = calculate_file_checksum(dest_file)
        assert dest_checksum == source_checksum


def test_migration_source_does_not_exist(tmp_path):
    """Test migration fails if source doesn't exist."""
    source = tmp_path / "nonexistent"
    destination = tmp_path / "destination"

    success, stats = migrate_data_directory(source, destination)

    assert success is False
    assert "does not exist" in stats['error'].lower()


def test_migration_source_is_file(tmp_path):
    """Test migration fails if source is a file."""
    source = tmp_path / "file.txt"
    source.write_text("test")
    destination = tmp_path / "destination"

    success, stats = migrate_data_directory(source, destination)

    assert success is False
    assert "not a directory" in stats['error'].lower()


def test_migration_destination_is_file(populated_data_dir, tmp_path):
    """Test migration fails if destination exists as a file."""
    destination = tmp_path / "file.txt"
    destination.write_text("test")

    success, stats = migrate_data_directory(populated_data_dir, destination)

    assert success is False
    assert "not a directory" in stats['error'].lower()


def test_migration_destination_not_empty(populated_data_dir, tmp_path):
    """Test migration fails if destination is not empty."""
    destination = tmp_path / "destination"
    destination.mkdir()
    (destination / "existing_file.txt").write_text("test")

    success, stats = migrate_data_directory(populated_data_dir, destination)

    assert success is False
    assert "not empty" in stats['error'].lower()


def test_migration_same_source_and_destination(populated_data_dir):
    """Test migration fails if source and destination are the same."""
    success, stats = migrate_data_directory(populated_data_dir, populated_data_dir)

    assert success is False
    assert "same" in stats['error'].lower()


def test_migration_progress_callback(populated_data_dir, tmp_path):
    """Test that progress callback is called during migration."""
    destination = tmp_path / "destination"

    progress_calls = []

    def progress_callback(bytes_copied, total_bytes):
        progress_calls.append((bytes_copied, total_bytes))

    success, stats = migrate_data_directory(
        populated_data_dir,
        destination,
        keep_backup=False,
        progress_callback=progress_callback
    )

    assert success is True
    assert len(progress_calls) > 0

    # Verify progress calls make sense
    for bytes_copied, total_bytes in progress_calls:
        assert bytes_copied <= total_bytes
        assert bytes_copied > 0


def test_estimate_migration_time(populated_data_dir, tmp_path):
    """Test migration time estimation."""
    destination = tmp_path / "destination"

    estimated_time = estimate_migration_time(populated_data_dir, destination)

    # Should return a positive number
    assert estimated_time > 0

    # Should be reasonable (not too large)
    assert estimated_time < 3600  # Less than 1 hour for small test data


def test_migration_preserves_timestamps(populated_data_dir, tmp_path):
    """Test that file modification times are preserved."""
    destination = tmp_path / "destination"

    # Get timestamps before migration
    source_file = populated_data_dir / "memoir.json"
    source_mtime = source_file.stat().st_mtime

    success, stats = migrate_data_directory(
        populated_data_dir,
        destination,
        keep_backup=True
    )

    assert success is True

    # Check timestamp was preserved
    dest_file = destination / "memoir.json"
    dest_mtime = dest_file.stat().st_mtime

    # Should be very close (within 1 second tolerance)
    assert abs(dest_mtime - source_mtime) < 1.0


def test_migration_creates_nested_directories(tmp_path):
    """Test migration creates nested directory structure."""
    source = tmp_path / "source"
    source.mkdir()

    # Create nested structure
    nested_dir = source / "level1" / "level2" / "level3"
    nested_dir.mkdir(parents=True)
    (nested_dir / "deep_file.txt").write_text("deep content")

    destination = tmp_path / "destination"

    success, stats = migrate_data_directory(
        source,
        destination,
        keep_backup=False
    )

    assert success is True
    assert (destination / "level1" / "level2" / "level3" / "deep_file.txt").exists()
