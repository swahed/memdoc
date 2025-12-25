"""
Unit tests for markdown_handler.py

Tests all chapter operations including create, read, update, delete, and reorder.
"""

import pytest
import json
from pathlib import Path
from core.markdown_handler import MemoirHandler


class TestMemoirHandler:
    """Tests for MemoirHandler class."""

    def test_init_creates_directories(self, temp_data_dir):
        """Test that handler initialization creates necessary directories."""
        handler = MemoirHandler(data_dir=str(temp_data_dir))

        assert handler.chapters_dir.exists()
        assert handler.images_dir.exists()
        assert handler.chapters_dir.is_dir()
        assert handler.images_dir.is_dir()

    def test_load_memoir_metadata_creates_default(self, handler):
        """Test loading memoir metadata creates default if not exists."""
        metadata = handler.load_memoir_metadata()

        assert metadata is not None
        assert 'title' in metadata
        assert 'author' in metadata
        assert 'cover' in metadata
        assert 'chapters' in metadata
        assert metadata['title'] == "My Memoir"
        assert isinstance(metadata['chapters'], list)

    def test_save_memoir_metadata(self, handler, sample_memoir_metadata):
        """Test saving memoir metadata to file."""
        handler.save_memoir_metadata(sample_memoir_metadata)

        # Verify file exists
        assert handler.memoir_file.exists()

        # Verify content
        with open(handler.memoir_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        assert saved_data['title'] == sample_memoir_metadata['title']
        assert saved_data['author'] == sample_memoir_metadata['author']


class TestChapterCreation:
    """Tests for chapter creation."""

    def test_create_chapter(self, handler):
        """Test creating a new chapter."""
        chapter_id = handler.create_chapter("Test Chapter", "Test Subtitle")

        assert chapter_id == "ch001"

        # Verify chapter exists in metadata
        metadata = handler.load_memoir_metadata()
        assert len(metadata['chapters']) == 1
        assert metadata['chapters'][0]['id'] == "ch001"

        # Verify chapter file exists
        chapter = handler.load_chapter(chapter_id)
        assert chapter is not None
        assert chapter['frontmatter']['title'] == "Test Chapter"
        assert chapter['frontmatter']['subtitle'] == "Test Subtitle"

    def test_create_multiple_chapters(self, handler):
        """Test creating multiple chapters increments IDs."""
        ch1 = handler.create_chapter("Chapter 1", "")
        ch2 = handler.create_chapter("Chapter 2", "")
        ch3 = handler.create_chapter("Chapter 3", "")

        assert ch1 == "ch001"
        assert ch2 == "ch002"
        assert ch3 == "ch003"

        metadata = handler.load_memoir_metadata()
        assert len(metadata['chapters']) == 3

    def test_create_chapter_with_empty_subtitle(self, handler):
        """Test creating chapter with empty subtitle."""
        chapter_id = handler.create_chapter("Title Only", "")

        chapter = handler.load_chapter(chapter_id)
        assert chapter['frontmatter']['subtitle'] == ""

    def test_create_chapter_generates_filename(self, handler):
        """Test that chapter creation generates proper filename."""
        chapter_id = handler.create_chapter("My First Chapter", "Subtitle")

        metadata = handler.load_memoir_metadata()
        chapter_info = metadata['chapters'][0]

        assert chapter_info['file'].startswith("ch001-")
        assert "my-first-chapter" in chapter_info['file']
        assert chapter_info['file'].endswith(".md")


class TestChapterLoading:
    """Tests for chapter loading."""

    def test_load_chapter(self, handler):
        """Test loading an existing chapter."""
        chapter_id = handler.create_chapter("Test Chapter", "Subtitle")

        chapter = handler.load_chapter(chapter_id)

        assert chapter is not None
        assert 'frontmatter' in chapter
        assert 'content' in chapter
        assert chapter['frontmatter']['title'] == "Test Chapter"
        assert chapter['frontmatter']['subtitle'] == "Subtitle"

    def test_load_nonexistent_chapter(self, handler):
        """Test loading a chapter that doesn't exist."""
        chapter = handler.load_chapter("ch999")

        assert chapter is None

    def test_load_chapter_with_content(self, handler):
        """Test loading chapter with markdown content."""
        chapter_id = handler.create_chapter("Test", "")

        # Add content
        frontmatter = {'id': chapter_id, 'title': 'Test', 'subtitle': '', 'events': []}
        content = "This is my memoir content.\n\nIt has multiple paragraphs."
        handler.save_chapter(chapter_id, frontmatter, content)

        # Load and verify
        loaded = handler.load_chapter(chapter_id)
        assert loaded['content'] == content


class TestChapterSaving:
    """Tests for chapter saving."""

    def test_save_chapter(self, handler):
        """Test saving chapter content."""
        chapter_id = handler.create_chapter("Original Title", "")

        frontmatter = {
            'id': chapter_id,
            'title': 'Updated Title',
            'subtitle': 'New Subtitle',
            'events': []
        }
        content = "Updated content here."

        handler.save_chapter(chapter_id, frontmatter, content)

        # Verify changes saved
        loaded = handler.load_chapter(chapter_id)
        assert loaded['frontmatter']['title'] == 'Updated Title'
        assert loaded['frontmatter']['subtitle'] == 'New Subtitle'
        assert loaded['content'] == content

    def test_save_nonexistent_chapter_raises_error(self, handler):
        """Test saving non-existent chapter raises ValueError."""
        frontmatter = {'title': 'Test'}
        content = "Content"

        with pytest.raises(ValueError, match="Chapter ch999 not found"):
            handler.save_chapter("ch999", frontmatter, content)

    def test_save_chapter_preserves_frontmatter(self, handler):
        """Test that saving preserves frontmatter structure."""
        chapter_id = handler.create_chapter("Test", "")

        frontmatter = {
            'id': chapter_id,
            'title': 'Test',
            'subtitle': '',
            'events': [
                {'date': '2020-01-01', 'title': 'Important Event'}
            ]
        }
        handler.save_chapter(chapter_id, frontmatter, "Content")

        loaded = handler.load_chapter(chapter_id)
        assert 'events' in loaded['frontmatter']
        assert len(loaded['frontmatter']['events']) == 1
        assert loaded['frontmatter']['events'][0]['title'] == 'Important Event'


class TestChapterMetadataUpdate:
    """Tests for updating chapter metadata."""

    def test_update_chapter_metadata(self, handler):
        """Test updating chapter title and subtitle."""
        chapter_id = handler.create_chapter("Original", "Old subtitle")

        handler.update_chapter_metadata(chapter_id, "Updated Title", "New subtitle")

        chapter = handler.load_chapter(chapter_id)
        assert chapter['frontmatter']['title'] == "Updated Title"
        assert chapter['frontmatter']['subtitle'] == "New subtitle"

    def test_update_metadata_preserves_content(self, handler):
        """Test that updating metadata doesn't affect content."""
        chapter_id = handler.create_chapter("Original", "")

        # Add content
        frontmatter = {'id': chapter_id, 'title': 'Original', 'subtitle': '', 'events': []}
        content = "Important memoir content that should not change."
        handler.save_chapter(chapter_id, frontmatter, content)

        # Update metadata
        handler.update_chapter_metadata(chapter_id, "New Title", "New Subtitle")

        # Verify content preserved
        loaded = handler.load_chapter(chapter_id)
        assert loaded['content'] == content

    def test_update_nonexistent_chapter_raises_error(self, handler):
        """Test updating non-existent chapter raises ValueError."""
        with pytest.raises(ValueError, match="Chapter ch999 not found"):
            handler.update_chapter_metadata("ch999", "Title", "Subtitle")


class TestChapterDeletion:
    """Tests for chapter deletion."""

    def test_delete_chapter(self, handler):
        """Test deleting a chapter."""
        chapter_id = handler.create_chapter("To Delete", "")

        handler.delete_chapter(chapter_id)

        # Verify chapter removed from metadata
        metadata = handler.load_memoir_metadata()
        assert len(metadata['chapters']) == 0

        # Verify chapter file deleted
        chapter = handler.load_chapter(chapter_id)
        assert chapter is None

    def test_delete_nonexistent_chapter_silent(self, handler):
        """Test deleting non-existent chapter doesn't raise error."""
        # Should not raise an error
        handler.delete_chapter("ch999")

    def test_delete_chapter_moves_to_deleted_folder(self, handler):
        """Test that deletion moves file to deleted folder instead of removing it."""
        chapter_id = handler.create_chapter("Test", "")

        # Get file path before deletion
        metadata = handler.load_memoir_metadata()
        chapter_info = next(ch for ch in metadata['chapters'] if ch['id'] == chapter_id)
        chapter_file = handler.chapters_dir / chapter_info['file']

        assert chapter_file.exists()

        handler.delete_chapter(chapter_id)

        # Original file should be gone
        assert not chapter_file.exists()

        # File should be in deleted folder with timestamp
        deleted_files = list(handler.deleted_dir.glob(f"{chapter_file.stem}_deleted_*.md"))
        assert len(deleted_files) == 1
        assert deleted_files[0].exists()


class TestChapterReordering:
    """Tests for chapter reordering."""

    def test_reorder_chapter_up(self, populated_handler):
        """Test moving a chapter up in the order."""
        # Get initial order
        chapters = populated_handler.list_chapters()
        ch3_id = chapters[2]['id']

        # Move chapter 3 up
        populated_handler.reorder_chapters(ch3_id, 'up')

        # Verify new order
        new_chapters = populated_handler.list_chapters()
        assert new_chapters[1]['id'] == ch3_id
        assert new_chapters[2]['id'] == chapters[1]['id']

    def test_reorder_chapter_down(self, populated_handler):
        """Test moving a chapter down in the order."""
        chapters = populated_handler.list_chapters()
        ch1_id = chapters[0]['id']

        # Move chapter 1 down
        populated_handler.reorder_chapters(ch1_id, 'down')

        # Verify new order
        new_chapters = populated_handler.list_chapters()
        assert new_chapters[0]['id'] == chapters[1]['id']
        assert new_chapters[1]['id'] == ch1_id

    def test_reorder_first_chapter_up_no_change(self, populated_handler):
        """Test that moving first chapter up doesn't change order."""
        chapters = populated_handler.list_chapters()
        first_id = chapters[0]['id']

        populated_handler.reorder_chapters(first_id, 'up')

        # Order should be unchanged
        new_chapters = populated_handler.list_chapters()
        assert new_chapters[0]['id'] == first_id

    def test_reorder_last_chapter_down_no_change(self, populated_handler):
        """Test that moving last chapter down doesn't change order."""
        chapters = populated_handler.list_chapters()
        last_id = chapters[-1]['id']

        populated_handler.reorder_chapters(last_id, 'down')

        # Order should be unchanged
        new_chapters = populated_handler.list_chapters()
        assert new_chapters[-1]['id'] == last_id

    def test_reorder_updates_order_numbers(self, populated_handler):
        """Test that reordering updates order numbers correctly."""
        chapters = populated_handler.list_chapters()
        ch3_id = chapters[2]['id']

        populated_handler.reorder_chapters(ch3_id, 'up')

        metadata = populated_handler.load_memoir_metadata()
        for i, chapter in enumerate(metadata['chapters']):
            assert chapter['order'] == i + 1

    def test_reorder_nonexistent_chapter_silent(self, handler):
        """Test reordering non-existent chapter doesn't raise error."""
        # Should not raise an error
        handler.reorder_chapters("ch999", "up")


class TestListChapters:
    """Tests for listing chapters."""

    def test_list_chapters_empty(self, handler):
        """Test listing chapters when none exist."""
        chapters = handler.list_chapters()

        assert isinstance(chapters, list)
        assert len(chapters) == 0

    def test_list_chapters(self, populated_handler):
        """Test listing all chapters with metadata."""
        chapters = populated_handler.list_chapters()

        assert len(chapters) == 3
        assert all('id' in ch for ch in chapters)
        assert all('title' in ch for ch in chapters)
        assert all('subtitle' in ch for ch in chapters)
        assert all('file' in ch for ch in chapters)
        assert all('order' in ch for ch in chapters)

    def test_list_chapters_returns_titles(self, populated_handler):
        """Test that list_chapters includes actual titles from files."""
        chapters = populated_handler.list_chapters()

        assert chapters[0]['title'] == "Chapter One"
        assert chapters[1]['title'] == "Chapter Two"
        assert chapters[2]['title'] == "Chapter Three"

    def test_list_chapters_maintains_order(self, populated_handler):
        """Test that chapters are listed in correct order."""
        # Reorder chapters
        chapters = populated_handler.list_chapters()
        ch3_id = chapters[2]['id']
        populated_handler.reorder_chapters(ch3_id, 'up')

        # Get new list
        new_chapters = populated_handler.list_chapters()

        # Verify order
        assert new_chapters[1]['id'] == ch3_id
