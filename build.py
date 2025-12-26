"""
PyInstaller Build Script for MemDoc

Builds either production or test executables based on the current branch.
- Production builds: MemDoc.exe (from main or version tags)
- Test builds: MemDoc-TEST.exe (from any other branch)

Test builds are isolated with separate data directories and clear warnings.
"""

import os
import sys
from pathlib import Path
import PyInstaller.__main__


def detect_build_type():
    """
    Detect whether this is a production or test build.

    Returns:
        tuple: (is_test_build, branch_name, exe_name)
    """
    # Try to get branch from GitHub Actions environment
    branch = os.getenv('GITHUB_REF_NAME', '')

    # If not in GitHub Actions, try git command
    if not branch:
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
        except Exception:
            branch = 'main'  # Default fallback

    # Determine if this is a test build
    # Production: main, master, or version tags (v1.0.0)
    is_production = (
        branch in ['main', 'master'] or
        branch.startswith('v') and branch[1:2].isdigit()
    )

    is_test_build = not is_production
    exe_name = 'MemDoc-TEST' if is_test_build else 'MemDoc'

    return is_test_build, branch, exe_name


def get_hidden_imports():
    """
    Get list of hidden imports for PyInstaller.

    Returns:
        list: Hidden import module names
    """
    return [
        'jinja2',  # Flask dependency
        'markupsafe',  # Jinja2 dependency
        'PIL',  # Pillow
        'PIL.Image',
        'yaml',  # PyYAML
        'weasyprint',  # PDF generation
    ]


def build_executable():
    """
    Build the MemDoc executable with PyInstaller.
    """
    # Detect build type
    is_test, branch, exe_name = detect_build_type()

    print("=" * 60)
    print("MemDoc Build Configuration")
    print("=" * 60)
    print(f"Build Type: {'TEST' if is_test else 'PRODUCTION'}")
    print(f"Branch: {branch}")
    print(f"Executable: {exe_name}.exe")
    print("=" * 60)

    # Set environment variables for the build
    # These will be baked into the executable
    if is_test:
        os.environ['MEMDOC_TEST_BUILD'] = 'true'
        os.environ['MEMDOC_BRANCH'] = branch
    else:
        os.environ['MEMDOC_TEST_BUILD'] = 'false'
        os.environ['MEMDOC_BRANCH'] = 'main'

    # Base directory
    base_dir = Path(__file__).parent

    # Build PyInstaller arguments
    args = [
        'app.py',  # Main script
        '--onefile',  # Single executable
        '--windowed',  # No console window
        f'--name={exe_name}',  # Output name
        f'--distpath={base_dir / "dist"}',  # Output directory
        f'--workpath={base_dir / "build"}',  # Build directory
        f'--specpath={base_dir}',  # Spec file location

        # Add data files
        f'--add-data={base_dir / "templates"};templates',
        f'--add-data={base_dir / "static"};static',
        f'--add-data={base_dir / "prompts"};prompts',
        f'--add-data={base_dir / "data-sample"};data-sample',  # Sample memoir data

        # Icon (if exists)
        # f'--icon={base_dir / "static/images/icon.ico"}',  # Uncomment when icon exists

        # Clean build
        '--clean',

        # Hidden imports
        *[f'--hidden-import={mod}' for mod in get_hidden_imports()],

        # Additional options
        '--noupx',  # Don't use UPX compression (can cause issues)
    ]

    # Run PyInstaller
    print("\nStarting PyInstaller build...")
    print(f"Command: PyInstaller {' '.join(args)}")
    print()

    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 60)
        print(f"Build successful: dist/{exe_name}.exe")
        print("=" * 60)

        # Print build info
        exe_path = base_dir / 'dist' / f'{exe_name}.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Size: {size_mb:.1f} MB")

            if is_test:
                print()
                print("WARNING: TEST BUILD - This executable will:")
                print(f"   - Show '[TEST BUILD - Branch: {branch}]' in window title (RED)")
                print("   - Use %APPDATA%/MemDoc-Test/ for data (isolated)")
                print("   - Pre-load sample memoir data on first launch")
                print("   - Cannot access production memoir data")

    except Exception as e:
        print(f"\nBuild failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    build_executable()
