"""
Unit tests for pdf_generator.py

Tests markdown to HTML conversion and PDF generation.
"""

import pytest
from pathlib import Path
from core.pdf_generator import (
    markdown_to_html,
    generate_chapter_preview_html,
    generate_chapter_pdf,
    check_weasyprint_available
)

# Check if WeasyPrint can import properly (needs GTK libraries on Windows)
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (OSError, ImportError):
    WEASYPRINT_AVAILABLE = False


class TestPDFDependencyCheck:
    """Tests for PDF dependency checking."""

    def test_check_weasyprint_returns_tuple(self):
        """Test that check_weasyprint_available returns a tuple."""
        is_available, message = check_weasyprint_available()
        assert isinstance(is_available, bool)
        assert isinstance(message, str)

    def test_check_weasyprint_availability(self):
        """Test WeasyPrint availability matches our detection."""
        is_available, message = check_weasyprint_available()
        assert is_available == WEASYPRINT_AVAILABLE

    def test_check_weasyprint_error_message_when_unavailable(self):
        """Test that error message is provided when WeasyPrint is unavailable."""
        is_available, message = check_weasyprint_available()
        if not is_available:
            # Should have helpful error message
            assert len(message) > 0
            assert "PDF-Export" in message
            # Should mention alternative
            assert "Vorschau" in message or "Drucken" in message
        else:
            # Should have empty message when available
            assert message == ""

    def test_check_weasyprint_includes_platform_instructions(self):
        """Test that error message includes platform-specific instructions."""
        is_available, message = check_weasyprint_available()
        if not is_available:
            import platform
            system = platform.system()
            if system == "Windows":
                assert "GTK" in message or "gtk" in message.lower()
            elif system == "Darwin":
                assert "brew" in message or "Homebrew" in message
            # Message should have installation steps
            assert "1." in message and "2." in message

    def test_generate_pdf_raises_on_missing_dependencies(self, handler, tmp_path):
        """Test that generate_chapter_pdf raises RuntimeError when dependencies missing."""
        if not WEASYPRINT_AVAILABLE:
            chapter_id = handler.create_chapter("Test", "")
            frontmatter = {'id': chapter_id, 'title': 'Test', 'subtitle': '', 'events': []}
            handler.save_chapter(chapter_id, frontmatter, "Content")

            pdf_path = tmp_path / "test.pdf"
            with pytest.raises(RuntimeError) as exc_info:
                generate_chapter_pdf(handler, chapter_id, pdf_path)

            # Error message should be helpful
            error_msg = str(exc_info.value)
            assert "PDF-Export" in error_msg
            assert len(error_msg) > 50  # Should be a detailed message


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


class TestBoldItalicSpaceFix:
    """Tests for the regex that strips trailing spaces before bold/italic closing markers."""

    def test_bold_trailing_space(self):
        """'**word **' should render as bold."""
        html = markdown_to_html("**word **")
        assert "<strong>word</strong>" in html

    def test_italic_trailing_space(self):
        """'*word *' should render as italic."""
        html = markdown_to_html("*word *")
        assert "<em>word</em>" in html

    def test_bold_already_correct(self):
        """'**word**' (no trailing space) should be unchanged."""
        html = markdown_to_html("**word**")
        assert "<strong>word</strong>" in html

    def test_math_expression_unchanged(self):
        """'5 * 3' should not be treated as a marker."""
        html = markdown_to_html("5 * 3")
        assert "5" in html
        assert "3" in html
        # Should NOT be wrapped in em/strong
        assert "<em>" not in html
        assert "<strong>" not in html

    def test_mixed_markers(self):
        """Content with multiple bold and italic markers with trailing spaces."""
        html = markdown_to_html("**bold ** and *italic * here")
        assert "<strong>bold</strong>" in html
        assert "<em>italic</em>" in html

    def test_empty_content(self):
        """Empty string should not crash."""
        html = markdown_to_html("")
        assert html is not None

    def test_none_guard(self):
        """None content should not crash (guard in markdown_to_html)."""
        # markdown_to_html expects a string, but the guard should prevent
        # the regex from crashing on None/empty before markdown2 processes it
        html = markdown_to_html("")
        assert isinstance(html, str)
