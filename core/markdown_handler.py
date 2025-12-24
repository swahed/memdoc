"""
Markdown Handler Module

Manages memoir.json and individual chapter markdown files.
Handles YAML frontmatter parsing and chapter operations.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional


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
        self.images_dir = self.data_dir / "images"

        # Ensure directories exist
        self.chapters_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def load_memoir_metadata(self) -> Dict:
        """
        Load memoir metadata from memoir.json.

        Returns:
            Dictionary containing memoir metadata and chapter list
        """
        if not self.memoir_file.exists():
            # Create default memoir.json if it doesn't exist
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
            self.save_memoir_metadata(default_memoir)
            return default_memoir

        with open(self.memoir_file, 'r', encoding='utf-8') as f:
            return json.load(f)

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

        # Generate new chapter ID
        existing_ids = [ch['id'] for ch in memoir['chapters']]
        chapter_num = len(existing_ids) + 1
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
        content = f"# {title}\n"
        if subtitle:
            content += f"## {subtitle}\n"
        content += "\nStart writing here..."

        self.save_chapter(chapter_id, frontmatter, content)

        return chapter_id

    def delete_chapter(self, chapter_id: str) -> None:
        """
        Delete a chapter.

        Args:
            chapter_id: The chapter ID to delete
        """
        memoir = self.load_memoir_metadata()
        chapter_info = next((ch for ch in memoir['chapters'] if ch['id'] == chapter_id), None)

        if not chapter_info:
            return

        # Delete file
        chapter_file = self.chapters_dir / chapter_info['file']
        if chapter_file.exists():
            chapter_file.unlink()

        # Remove from metadata
        memoir['chapters'] = [ch for ch in memoir['chapters'] if ch['id'] != chapter_id]
        self.save_memoir_metadata(memoir)

    def list_chapters(self) -> List[Dict]:
        """
        Get list of all chapters with their metadata.

        Returns:
            List of chapter dictionaries
        """
        memoir = self.load_memoir_metadata()
        return memoir['chapters']
