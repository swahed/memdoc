"""
Unit tests for pdf_generator.py

Tests markdown to HTML conversion and PDF generation.
"""

import pytest
from pathlib import Path
from core.pdf_generator import markdown_to_html, generate_chapter_preview_html, generate_chapter_pdf

# Check if WeasyPrint can import properly (needs GTK libraries on Windows)
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (OSError, ImportError):
    WEASYPRINT_AVAILABLE = False


class TestMarkdownToHTML:
    """Tests for markdown to HTML conversion."""

    def test_basic_markdown_conversion(self):
        """Test basic markdown to HTML conversion."""
        markdown = "# Heading\n\nThis is **bold** and *italic* text."
        html = markdown_to_html(markdown, "Test Chapter")

        assert "<h1>Test Chapter</h1>" in html
        assert "<strong>bold</strong>" in html or "<b>bold</b>" in html
        assert "<em>italic</em>" in html or "<i>italic</i>" in html

    def test_markdown_with_title(self):
        """Test HTML generation includes chapter title."""
        markdown = "Content here"
        html = markdown_to_html(markdown, "My Chapter Title")

        assert "<h1>My Chapter Title</h1>" in html
        assert "Content here" in html

    def test_markdown_without_title(self):
        """Test HTML generation without chapter title."""
        markdown = "Content here"
        html = markdown_to_html(markdown)

        assert "<h1>" not in html
        assert "Content here" in html

    def test_markdown_with_images(self):
        """Test markdown with image tags."""
        markdown = "![Photo](../images/test.jpg)\n{: .img-center .img-medium}"
        html = markdown_to_html(markdown)

        assert "<img" in html
        assert "test.jpg" in html

    def test_html_contains_print_styles(self):
        """Test that generated HTML includes print-optimized styles."""
        html = markdown_to_html("Test content")

        assert "@page" in html
        assert "font-family" in html
        assert "line-height" in html
        assert ".img-center" in html
        assert ".img-medium" in html


class TestChapterPreview:
    """Tests for chapter preview generation."""

    def test_generate_preview_html(self, handler):
        """Test generating preview HTML for a chapter."""
        chapter_id = handler.create_chapter("Test Chapter", "Subtitle")

        # Add content
        frontmatter = {'id': chapter_id, 'title': 'Test Chapter', 'subtitle': 'Subtitle', 'events': []}
        content = "This is test content with **bold** text."
        handler.save_chapter(chapter_id, frontmatter, content)

        # Generate preview
        html = generate_chapter_preview_html(handler, chapter_id)

        assert "<h1>Test Chapter: Subtitle</h1>" in html
        assert "test content" in html
        assert "<strong>bold</strong>" in html or "<b>bold</b>" in html

    def test_generate_preview_nonexistent_chapter(self, handler):
        """Test preview generation for non-existent chapter raises error."""
        with pytest.raises(ValueError, match="not found"):
            generate_chapter_preview_html(handler, "ch999")


class TestChapterPDF:
    """Tests for PDF generation."""

    @pytest.mark.skipif(not WEASYPRINT_AVAILABLE, reason="WeasyPrint requires GTK libraries (not installed)")
    def test_generate_pdf(self, handler, tmp_path):
        """Test generating PDF for a chapter."""
        chapter_id = handler.create_chapter("PDF Test", "")

        # Add content
        frontmatter = {'id': chapter_id, 'title': 'PDF Test', 'subtitle': '', 'events': []}
        content = "This is PDF test content.\n\n**Bold text** and *italic text*."
        handler.save_chapter(chapter_id, frontmatter, content)

        # Generate PDF
        pdf_path = tmp_path / "test.pdf"
        result = generate_chapter_pdf(handler, chapter_id, pdf_path)

        assert result is True
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0  # PDF has content

    @pytest.mark.skipif(not WEASYPRINT_AVAILABLE, reason="WeasyPrint requires GTK libraries (not installed)")
    def test_generate_pdf_nonexistent_chapter(self, handler, tmp_path):
        """Test PDF generation for non-existent chapter raises error."""
        pdf_path = tmp_path / "test.pdf"

        with pytest.raises(ValueError, match="not found"):
            generate_chapter_pdf(handler, "ch999", pdf_path)
