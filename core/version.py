"""
Version information and build configuration for MemDoc.

This module provides version constants and detects whether this is a test build
or production build based on environment variables set during compilation.
"""

import os

# Version information
VERSION = "1.2.1"
RELEASE_DATE = "2026-02-08"
GITHUB_REPO = "swahed/memdoc"

# Build type detection
# These environment variables are set by build.py during PyInstaller compilation
IS_TEST_BUILD = os.getenv('MEMDOC_TEST_BUILD', 'false').lower() == 'true'
TEST_BUILD_BRANCH = os.getenv('MEMDOC_BRANCH', 'unknown')


def get_version_string() -> str:
    """
    Get formatted version string.

    Returns:
        Version string like "v1.0.0" for production or "v1.0.0-TEST" for test builds
    """
    if IS_TEST_BUILD:
        return f"v{VERSION}-TEST"
    return f"v{VERSION}"


def get_window_title() -> str:
    """
    Get window title for the application.

    Returns:
        Window title with test build warning if applicable
    """
    if IS_TEST_BUILD:
        return f'MemDoc [TEST BUILD - Branch: {TEST_BUILD_BRANCH}]'
    return f'MemDoc v{VERSION}'


def is_production_build() -> bool:
    """
    Check if this is a production build.

    Returns:
        True if production build, False if test build
    """
    return not IS_TEST_BUILD
