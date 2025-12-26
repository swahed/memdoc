#!/usr/bin/env python3
"""
Load Sample Memoir Data

Copies the sample memoir data from tests/fixtures/sample_memoir/
to the configured data directory (or ./data if no config exists).

Usage:
    python scripts/load_sample_data.py [--force]

    --force: Overwrite existing data (WARNING: will delete current memoir data!)
"""

import sys
import shutil
import argparse
from pathlib import Path

# Add parent directory to path so we can import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import get_data_dir, load_config


def load_sample_data(force=False):
    """
    Load sample memoir data to the configured data directory.

    Args:
        force: If True, will overwrite existing data
    """
    # Get paths
    repo_root = Path(__file__).parent.parent
    sample_data = repo_root / "tests" / "fixtures" / "sample_memoir"

    if not sample_data.exists():
        print(f"❌ Error: Sample data not found at {sample_data}")
        print("   Make sure you're running from the repo root.")
        return False

    # Get configured data directory
    try:
        data_dir = get_data_dir()
    except Exception:
        # No config exists, use default
        data_dir = repo_root / "data"
        print(f"ℹ️  No config found, using default: {data_dir}")

    print(f"📁 Source: {sample_data}")
    print(f"📁 Target: {data_dir}")

    # Check if data directory exists and has content
    if data_dir.exists():
        memoir_file = data_dir / "memoir.json"
        if memoir_file.exists() and not force:
            print(f"\n⚠️  WARNING: Data directory already exists with memoir data!")
            print(f"   Target: {data_dir}")
            print(f"\n   Use --force to overwrite existing data.")
            print(f"   This will DELETE your current memoir data!")
            return False

        if force:
            print(f"\n⚠️  --force flag set: Deleting existing data at {data_dir}")
            try:
                # Create backup before deleting
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = data_dir.parent / f"{data_dir.name}.backup.{timestamp}"

                print(f"📦 Creating backup at: {backup_dir}")
                shutil.copytree(data_dir, backup_dir)

                # Remove old data
                shutil.rmtree(data_dir)
            except Exception as e:
                print(f"❌ Error creating backup: {e}")
                return False

    # Copy sample data
    print(f"\n📋 Copying sample memoir data...")
    try:
        shutil.copytree(sample_data, data_dir)

        # Count what was copied
        chapters_dir = data_dir / "chapters"
        images_dir = data_dir / "images"

        chapter_count = len([f for f in chapters_dir.glob("*.md") if f.is_file()])
        image_count = len([f for f in images_dir.glob("*") if f.is_file()])

        print(f"✅ Sample data loaded successfully!")
        print(f"\n📊 Data loaded:")
        print(f"   - {chapter_count} chapters")
        print(f"   - {image_count} images")
        print(f"   - memoir.json")
        print(f"\n🚀 You can now run: python app.py --browser")

        return True

    except Exception as e:
        print(f"❌ Error copying data: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Load sample memoir data for development',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/load_sample_data.py           # Load to configured directory
  python scripts/load_sample_data.py --force   # Overwrite existing data

Sample data includes:
  - A memoir about becoming a plant parent (5 chapters)
  - Sample images
  - Cover page configuration
        """
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing data (creates backup first)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Load Sample Memoir Data")
    print("=" * 60)
    print()

    success = load_sample_data(force=args.force)

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
