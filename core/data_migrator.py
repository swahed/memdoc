"""
Data Migration Module

Handles safe data migration between directories with:
- Progress tracking
- Backup creation
- Integrity verification
- Rollback on failure
"""

import shutil
import hashlib
from pathlib import Path
from typing import Tuple, Dict, Callable, Optional
from datetime import datetime


def calculate_directory_size(path: Path) -> int:
    """
    Calculate total size of directory in bytes.

    Args:
        path: Directory path

    Returns:
        Total size in bytes
    """
    total_size = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                except (OSError, PermissionError):
                    pass
    except Exception:
        pass
    return total_size


def calculate_file_checksum(file_path: Path) -> str:
    """
    Calculate MD5 checksum of a file.

    Args:
        file_path: Path to file

    Returns:
        MD5 hex digest
    """
    md5 = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception:
        return ""


def verify_migration(source: Path, destination: Path) -> Tuple[bool, str]:
    """
    Verify migration completed successfully.

    Args:
        source: Source directory
        destination: Destination directory

    Returns:
        Tuple of (is_valid, message)
    """
    # Check that destination exists
    if not destination.exists():
        return False, "Destination directory does not exist"

    if not destination.is_dir():
        return False, "Destination exists but is not a directory"

    # Check critical files exist (only if they exist in source)
    source_memoir = source / "memoir.json"
    if source_memoir.exists():
        memoir_file = destination / "memoir.json"
        if not memoir_file.exists():
            return False, "memoir.json not found in destination"

        # Check critical directories exist
        chapters_dir = destination / "chapters"
        images_dir = destination / "images"

        if not chapters_dir.exists() or not chapters_dir.is_dir():
            return False, "chapters/ directory not found in destination"

        if not images_dir.exists() or not images_dir.is_dir():
            return False, "images/ directory not found in destination"

    # Count files in source and destination
    source_files = list(source.rglob('*'))
    source_file_count = sum(1 for f in source_files if f.is_file())

    dest_files = list(destination.rglob('*'))
    dest_file_count = sum(1 for f in dest_files if f.is_file())

    if source_file_count != dest_file_count:
        return False, f"File count mismatch: source has {source_file_count}, destination has {dest_file_count}"

    # Sample checksum verification (check 5 random files)
    import random
    sample_files = [f for f in source_files if f.is_file()]
    if sample_files:
        sample_size = min(5, len(sample_files))
        sample = random.sample(sample_files, sample_size)

        for source_file in sample:
            relative_path = source_file.relative_to(source)
            dest_file = destination / relative_path

            if not dest_file.exists():
                return False, f"File missing in destination: {relative_path}"

            source_checksum = calculate_file_checksum(source_file)
            dest_checksum = calculate_file_checksum(dest_file)

            if source_checksum != dest_checksum:
                return False, f"Checksum mismatch for {relative_path}"

    return True, "Migration verified successfully"


def migrate_data_directory(
    source: Path,
    destination: Path,
    keep_backup: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Tuple[bool, Dict]:
    """
    Migrate memoir data from source to destination directory.

    Process:
    1. Validate source and destination
    2. Calculate total size for progress tracking
    3. Create destination directories
    4. Copy all files with verification
    5. Verify integrity
    6. If keep_backup: rename source to source.backup.TIMESTAMP
    7. If not keep_backup: delete source (after confirmation)

    Args:
        source: Current data directory
        destination: New data directory
        keep_backup: Keep old data as backup
        progress_callback: Optional callback(bytes_copied, total_bytes)

    Returns:
        Tuple of (success, stats_dict)
        stats_dict contains:
            - files_copied: Number of files copied
            - bytes_copied: Total bytes copied
            - backup_location: Path to backup (if keep_backup=True)
            - error: Error message (if success=False)
    """
    stats = {
        'files_copied': 0,
        'bytes_copied': 0,
        'backup_location': None,
        'error': None
    }

    try:
        # Resolve paths to absolute
        source = source.resolve()
        destination = destination.resolve()

        # Validate source exists
        if not source.exists():
            stats['error'] = f"Source directory does not exist: {source}"
            return False, stats

        if not source.is_dir():
            stats['error'] = f"Source is not a directory: {source}"
            return False, stats

        # Check that source and destination are different
        if source == destination:
            stats['error'] = "Source and destination are the same"
            return False, stats

        # Validate destination doesn't exist or is empty
        if destination.exists():
            if not destination.is_dir():
                stats['error'] = f"Destination exists but is not a directory: {destination}"
                return False, stats

            # Check if destination is empty
            dest_items = list(destination.iterdir())
            if dest_items:
                stats['error'] = f"Destination directory is not empty: {destination}"
                return False, stats

        # Calculate total size for progress tracking
        total_bytes = calculate_directory_size(source)

        # Check disk space
        if destination.exists():
            dest_stat = shutil.disk_usage(destination)
        else:
            dest_stat = shutil.disk_usage(destination.parent)

        if dest_stat.free < total_bytes * 1.1:  # 10% buffer
            stats['error'] = f"Insufficient disk space. Need {total_bytes / (1024**3):.2f} GB, have {dest_stat.free / (1024**3):.2f} GB free"
            return False, stats

        # Create destination directory if it doesn't exist
        destination.mkdir(parents=True, exist_ok=True)

        # Copy all files
        bytes_copied = 0

        for source_item in source.rglob('*'):
            if source_item.is_file():
                # Calculate relative path
                relative_path = source_item.relative_to(source)
                dest_item = destination / relative_path

                # Create parent directory if needed
                dest_item.parent.mkdir(parents=True, exist_ok=True)

                # Copy file (preserves metadata)
                shutil.copy2(str(source_item), str(dest_item))

                # Update stats
                file_size = source_item.stat().st_size
                bytes_copied += file_size
                stats['files_copied'] += 1
                stats['bytes_copied'] = bytes_copied

                # Progress callback
                if progress_callback:
                    progress_callback(bytes_copied, total_bytes)

        # Verify migration
        is_valid, message = verify_migration(source, destination)
        if not is_valid:
            # Migration verification failed - clean up destination
            try:
                shutil.rmtree(destination)
            except Exception:
                pass

            stats['error'] = f"Migration verification failed: {message}"
            return False, stats

        # Migration successful - handle backup
        if keep_backup:
            # Rename source to backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source.name}.backup.{timestamp}"
            backup_path = source.parent / backup_name

            try:
                shutil.move(str(source), str(backup_path))
                stats['backup_location'] = str(backup_path)
            except Exception as e:
                # Backup failed but data was copied successfully
                stats['error'] = f"Warning: Could not create backup: {e}"
                # Don't return False - migration was successful
        else:
            # Remove source directory
            try:
                shutil.rmtree(source)
            except Exception as e:
                stats['error'] = f"Warning: Could not remove source directory: {e}"
                # Don't return False - migration was successful

        return True, stats

    except Exception as e:
        stats['error'] = f"Migration failed: {e}"
        return False, stats


def estimate_migration_time(source: Path, destination: Path) -> float:
    """
    Estimate migration time in seconds.

    Very rough estimate based on file size and typical disk speeds.

    Args:
        source: Source directory
        destination: Destination directory

    Returns:
        Estimated time in seconds
    """
    total_size = calculate_directory_size(source)

    # Assume different speeds based on whether it's same drive or different
    # This is a rough estimate - actual speed varies greatly
    try:
        # Check if on same drive (Windows: compare drive letters, Unix: compare mount points)
        source_drive = str(source.resolve().parts[0])
        dest_drive = str(destination.resolve().parts[0])

        if source_drive == dest_drive:
            # Same drive - faster (assume 100 MB/s)
            speed_mb_s = 100
        else:
            # Different drive - slower (assume 50 MB/s)
            speed_mb_s = 50

    except Exception:
        # Default to conservative estimate
        speed_mb_s = 50

    size_mb = total_size / (1024 * 1024)
    estimated_seconds = size_mb / speed_mb_s

    return max(1.0, estimated_seconds)  # Minimum 1 second
