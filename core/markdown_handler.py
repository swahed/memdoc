"""
Markdown Handler Module

Manages memoir.json and individual chapter markdown files.
Handles YAML frontmatter parsing and chapter operations.
"""

import os
import json
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MemoirHandler:
    """Handles memoir metadata and chapter file operations."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the memoir handler.

        Args:
            data_dir: Path to the data directory containing memoir files
        """
        self.data_dir = Path(data_dir)
        self.memoir_file = self.data_dir / "memoir.json"
        self.chapters_dir = self.data_dir / "chapters"
        self.deleted_dir = self.data_dir / "chapters" / "deleted"
        self.images_dir = self.data_dir / "images"

        # Ensure directories exist
        self.chapters_dir.mkdir(parents=True, exist_ok=True)
        self.deleted_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def load_memoir_metadata(self) -> Dict:
        """
        Load memoir metadata from memoir.json.

        Returns:
            Dictionary containing memoir metadata and chapter list
        """
        default_memoir = {
            "title": "My Memoir",
            "author": "",
            "cover": {
                "title": "My Memoir",
                "subtitle": "A Life Story",
                "author": ""
            },
            "chapters": []
        }

        if not self.memoir_file.exists():
            self.save_memoir_metadata(default_memoir)
            return default_memoir

        try:
            with open(self.memoir_file, 'r', encoding='utf-8') as f:
                raw = f.read()

            if not raw.strip():
                raise ValueError("memoir.json is empty")

            return json.loads(raw)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("Corrupt memoir.json detected (%s), backing up and creating default", e)
            backup_path = self.memoir_file.with_suffix('.json.corrupt')
            try:
                self.memoir_file.rename(backup_path)
            except OSError:
                pass
            self.save_memoir_metadata(default_memoir)
            return default_memoir

    def save_memoir_metadata(self, metadata: Dict) -> None:
        """
        Save memoir metadata to memoir.json.

        Args:
            metadata: Dictionary containing memoir metadata
        """
        with open(self.memoir_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def load_chapter(self, chapter_id: str) -> Optional[Dict]:
        """
        Load a specific chapter by ID.

        Args:
            chapter_id: The chapter ID (e.g., 'ch001')

        Returns:
            Dictionary with 'frontmatter' and 'content' keys, or None if not found
        """
        memoir = self.load_memoir_metadata()
        chapter_info = next((ch for ch in memoir['chapters'] if ch['id'] == chapter_id), None)

        if not chapter_info:
            return None

        chapter_file = self.chapters_dir / chapter_info['file']
        if not chapter_file.exists():
            return None

        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse frontmatter and content
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            markdown_content = parts[2].strip()
        else:
            frontmatter = {}
            markdown_content = content

        return {
            'frontmatter': frontmatter,
            'content': markdown_content
        }

    def save_chapter(self, chapter_id: str, frontmatter: Dict, content: str) -> None:
        """
        Save a chapter to file.

        Args:
            chapter_id: The chapter ID
            frontmatter: Dictionary of chapter metadata
            content: Markdown content
        """
        memoir = self.load_memoir_metadata()
        chapter_info = next((ch for ch in memoir['chapters'] if ch['id'] == chapter_id), None)

        if not chapter_info:
            raise ValueError(f"Chapter {chapter_id} not found in memoir metadata")

        chapter_file = self.chapters_dir / chapter_info['file']

        # Build the file content with frontmatter
        frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        file_content = f"---\n{frontmatter_yaml}---\n\n{content}"

        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(file_content)

    def create_chapter(self, title: str, subtitle: str = "") -> str:
        """
        Create a new chapter.

        Args:
            title: Chapter title
            subtitle: Chapter subtitle (optional)

        Returns:
            The new chapter ID
        """
        memoir = self.load_memoir_metadata()

        # Generate new chapter ID (find max existing number + 1)
        existing_ids = [ch['id'] for ch in memoir['chapters']]
        if existing_ids:
            # Extract numbers from existing IDs and find the maximum
            existing_nums = [int(ch_id[2:]) for ch_id in existing_ids if ch_id.startswith('ch')]
            chapter_num = max(existing_nums) + 1 if existing_nums else 1
        else:
            chapter_num = 1
        chapter_id = f"ch{chapter_num:03d}"

        # Generate filename from title
        slug = title.lower().replace(' ', '-')[:30]  # Limit slug length
        filename = f"{chapter_id}-{slug}.md"

        # Add to memoir metadata
        memoir['chapters'].append({
            'id': chapter_id,
            'file': filename,
            'order': chapter_num
        })
        self.save_memoir_metadata(memoir)

        # Create chapter file
        frontmatter = {
            'id': chapter_id,
            'title': title,
            'subtitle': subtitle,
            'events': []
        }
        # Start with empty content - title and subtitle are in dedicated fields
        content = ""

        self.save_chapter(chapter_id, frontmatter, content)

        return chapter_id

    def update_chapter_metadata(self, chapter_id: str, title: str, subtitle: str = "") -> None:
        """
        Update chapter title and subtitle.

        Args:
            chapter_id: The chapter ID to update
            title: New chapter title
            subtitle: New chapter subtitle
        """
        chapter = self.load_chapter(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        # Update frontmatter
        frontmatter = chapter['frontmatter']
        frontmatter['title'] = title
        frontmatter['subtitle'] = subtitle

        # Save updated chapter
        self.save_chapter(chapter_id, frontmatter, chapter['content'])

    def delete_chapter(self, chapter_id: str) -> None:
        """
        Delete a chapter by moving it to the deleted folder.

        The chapter file is moved to data/chapters/deleted/ instead of being
        permanently deleted, allowing recovery if needed.

        Args:
            chapter_id: The chapter ID to delete
        """
        memoir = self.load_memoir_metadata()
        chapter_info = next((ch for ch in memoir['chapters'] if ch['id'] == chapter_id), None)

        if not chapter_info:
            return

        # Move file to deleted folder instead of deleting
        chapter_file = self.chapters_dir / chapter_info['file']
        if chapter_file.exists():
            import shutil
            import datetime

            # Add timestamp to filename to avoid conflicts
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            original_name = chapter_file.stem  # filename without extension
            deleted_filename = f"{original_name}_deleted_{timestamp}.md"
            deleted_path = self.deleted_dir / deleted_filename

            shutil.move(str(chapter_file), str(deleted_path))

        # Remove from metadata
        memoir['chapters'] = [ch for ch in memoir['chapters'] if ch['id'] != chapter_id]
        self.save_memoir_metadata(memoir)

    def reorder_chapters(self, chapter_id: str, direction: str) -> None:
        """
        Move a chapter up or down in the order.

        Args:
            chapter_id: The chapter ID to move
            direction: 'up' or 'down'
        """
        memoir = self.load_memoir_metadata()
        chapters = memoir['chapters']

        # Find current index
        current_index = next((i for i, ch in enumerate(chapters) if ch['id'] == chapter_id), None)
        if current_index is None:
            return

        # Calculate new index
        if direction == 'up' and current_index > 0:
            new_index = current_index - 1
        elif direction == 'down' and current_index < len(chapters) - 1:
            new_index = current_index + 1
        else:
            return  # Can't move further

        # Swap chapters
        chapters[current_index], chapters[new_index] = chapters[new_index], chapters[current_index]

        # Update order numbers
        for i, chapter in enumerate(chapters):
            chapter['order'] = i + 1

        # Save updated metadata
        self.save_memoir_metadata(memoir)

    def list_chapters(self) -> List[Dict]:
        """
        Get list of all chapters with their metadata.

        Returns:
            List of chapter dictionaries with title, subtitle, and word count
        """
        memoir = self.load_memoir_metadata()
        chapters_with_titles = []

        for chapter_info in memoir['chapters']:
            # Load each chapter to get title, subtitle, and word count
            chapter_data = self.load_chapter(chapter_info['id'])
            if chapter_data:
                content = chapter_data['content']
                word_count = len(content.split()) if content.strip() else 0

                chapters_with_titles.append({
                    **chapter_info,
                    'title': chapter_data['frontmatter'].get('title', ''),
                    'subtitle': chapter_data['frontmatter'].get('subtitle', ''),
                    'wordCount': word_count
                })
            else:
                # If chapter file doesn't exist, use defaults
                chapters_with_titles.append({
                    **chapter_info,
                    'title': 'Untitled',
                    'subtitle': '',
                    'wordCount': 0
                })

        return chapters_with_titles
