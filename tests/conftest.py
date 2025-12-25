"""
Shared pytest fixtures for MemDoc tests.
"""

import pytest
import json
import shutil
from pathlib import Path
from core.markdown_handler import MemoirHandler
from app import app as flask_app


@pytest.fixture
def temp_data_dir(tmp_path):
    """
    Create a temporary data directory for testing.

    Returns:
        Path: Temporary directory path
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "chapters").mkdir()
    (data_dir / "images").mkdir()
    return data_dir


@pytest.fixture
def handler(temp_data_dir):
    """
    Create a MemoirHandler instance with temporary data directory.

    Returns:
        MemoirHandler: Handler instance for testing
    """
    return MemoirHandler(data_dir=str(temp_data_dir))


@pytest.fixture
def sample_memoir_metadata():
    """
    Sample memoir metadata for testing.

    Returns:
        dict: Sample memoir metadata
    """
    return {
        "title": "Test Memoir",
        "author": "Test Author",
        "cover": {
            "title": "Test Memoir",
            "subtitle": "A Test Story",
            "author": "Test Author"
        },
        "chapters": []
    }


@pytest.fixture
def client(temp_data_dir, monkeypatch):
    """
    Create a Flask test client with temporary data directory.

    Returns:
        FlaskClient: Flask test client
    """
    # Configure app for testing
    flask_app.config['TESTING'] = True

    # Patch the memoir handler to use temp directory
    from app import memoir_handler as original_handler
    test_handler = MemoirHandler(data_dir=str(temp_data_dir))
    monkeypatch.setattr('app.memoir_handler', test_handler)

    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def populated_handler(handler):
    """
    Create a handler with sample chapters already created.

    Returns:
        MemoirHandler: Handler with sample data
    """
    handler.create_chapter("Chapter One", "First chapter")
    handler.create_chapter("Chapter Two", "Second chapter")
    handler.create_chapter("Chapter Three", "Third chapter")
    return handler
