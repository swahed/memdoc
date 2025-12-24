"""
Search Module

Provides full-text search across all chapters.
"""

from pathlib import Path
from typing import List, Dict


class ChapterSearch:
    """Simple full-text search for memoir chapters."""

    def __init__(self):
        """Initialize the search index."""
        self.index = {}

    def index_chapters(self, chapters: List[Dict]) -> None:
        """
        Index all chapters for search.

        Args:
            chapters: List of chapter dictionaries with 'id', 'title', and 'content'
        """
        self.index = {}
        for chapter in chapters:
            chapter_id = chapter.get('id', '')
            title = chapter.get('title', '')
            content = chapter.get('content', '')

            # Simple indexing: store full text
            self.index[chapter_id] = {
                'title': title,
                'content': content.lower(),
                'original_content': content
            }

    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for a query across all chapters.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search results with chapter info and context
        """
        query_lower = query.lower()
        results = []

        for chapter_id, data in self.index.items():
            if query_lower in data['content']:
                # Find context around the match
                content = data['original_content']
                index = content.lower().find(query_lower)

                # Extract context (50 chars before and after)
                start = max(0, index - 50)
                end = min(len(content), index + len(query) + 50)
                context = content[start:end]

                if start > 0:
                    context = "..." + context
                if end < len(content):
                    context = context + "..."

                results.append({
                    'chapter_id': chapter_id,
                    'title': data['title'],
                    'context': context,
                    'match_index': index
                })

        # Sort by relevance (for now, just by position in chapter)
        results.sort(key=lambda x: x['match_index'])

        return results[:max_results]
