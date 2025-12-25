"""
PDF Generator Module

Converts memoir to print-quality PDF with cover, TOC, and page numbers.
"""

from pathlib import Path
from typing import Dict, List, Tuple


def check_weasyprint_available() -> Tuple[bool, str]:
    """
    Check if WeasyPrint is available and can generate PDFs.

    Returns:
        Tuple of (is_available, error_message)
        If available, error_message will be empty string.
        If not available, error_message contains user-friendly instructions.
    """
    try:
        from weasyprint import HTML, CSS
        # Try a simple operation to ensure dependencies are working
        test_html = HTML(string='<html><body>Test</body></html>')
        return True, ""
    except (ImportError, OSError) as e:
        error_msg = str(e)

        # Provide platform-specific installation instructions
        import platform
        system = platform.system()

        if system == "Windows":
            instructions = """PDF export requires GTK libraries which are not installed.

To enable PDF export on Windows:
1. Download GTK3 Runtime: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Run the installer and follow the setup wizard
3. Restart the MemDoc application

Alternative: Use the Preview button to view your chapter in the browser, then use your browser's Print to PDF feature (Ctrl+P)."""
        elif system == "Darwin":  # macOS
            instructions = """PDF export requires system libraries which are not installed.

To enable PDF export on macOS:
1. Install Homebrew if you haven't already: https://brew.sh
2. Run: brew install pango
3. Restart the MemDoc application

Alternative: Use the Preview button to view your chapter in the browser, then use your browser's Print to PDF feature (⌘+P)."""
        else:  # Linux
            instructions = """PDF export requires system libraries which may not be installed.

To enable PDF export on Linux:
1. Install required packages:
   - Ubuntu/Debian: sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0
   - Fedora: sudo dnf install pango
2. Restart the MemDoc application

Alternative: Use the Preview button to view your chapter in the browser, then use your browser's Print to PDF feature."""

        return False, instructions
    except Exception as e:
        return False, f"PDF export is unavailable: {str(e)}"


def generate_pdf(memoir_metadata: Dict, chapters: List[Dict], output_path: Path) -> None:
    """
    Generate a PDF from the memoir.

    Args:
        memoir_metadata: Memoir metadata from memoir.json
        chapters: List of chapter data (frontmatter + content)
        output_path: Path where PDF should be saved
    """
    # TODO: Implement PDF generation with WeasyPrint
    pass


def generate_cover_html(memoir_metadata: Dict) -> str:
    """
    Generate HTML for the cover page.

    Args:
        memoir_metadata: Memoir metadata

    Returns:
        HTML string for cover page
    """
    # TODO: Implement cover page generation
    return ""


def generate_toc_html(chapters: List[Dict]) -> str:
    """
    Generate HTML for table of contents.

    Args:
        chapters: List of chapter data

    Returns:
        HTML string for TOC
    """
    # TODO: Implement TOC generation
    return ""


def markdown_to_html(markdown_content: str, chapter_title: str = "") -> str:
    """
    Convert markdown content to styled HTML for preview/PDF.

    Args:
        markdown_content: Markdown string
        chapter_title: Optional chapter title for H1

    Returns:
        Complete HTML document with styling
    """
    import markdown2

    # Convert markdown to HTML with extras
    html_content = markdown2.markdown(
        markdown_content,
        extras=[
            'fenced-code-blocks',
            'tables',
            'break-on-newline',
            'cuddled-lists',
            'footnotes'
        ]
    )

    # Fix image paths for web preview (convert ../images/ to /api/images/)
    html_content = html_content.replace('src="../images/', 'src="/api/images/')

    # Process kramdown-style class attributes {: .class1 .class2}
    # Pattern: <img...><br />\n{: .class1 .class2}<br />
    import re

    # Find and apply classes to images
    pattern = r'(<img[^>]*>)(<br\s*/?>)?\s*\{:\s*([^}]+)\}\s*(<br\s*/?>)?'
    def add_classes_to_img(match):
        img_tag = match.group(1)
        classes = match.group(3).strip()
        # Extract class names (remove dots)
        class_names = ' '.join([c.strip('.') for c in classes.split()])
        # Add class attribute to img tag
        if 'class=' in img_tag:
            # Append to existing classes
            img_tag = img_tag.replace('class="', f'class="{class_names} ')
        else:
            # Add new class attribute before closing / or >
            if img_tag.endswith('/>'):
                img_tag = img_tag[:-2] + f' class="{class_names}" />'
            elif img_tag.endswith('>'):
                img_tag = img_tag[:-1] + f' class="{class_names}">'
        return img_tag

    html_content = re.sub(pattern, add_classes_to_img, html_content)

    # Generate complete HTML document with print-optimized CSS
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{chapter_title if chapter_title else 'Chapter'}</title>
    <style>
        /* Print-optimized typography */
        @page {{
            size: A4;
            margin: 2.5cm 2cm;
        }}

        body {{
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 12pt;
            line-height: 1.8;
            color: #1a1a1a;
            max-width: 650px;
            margin: 0 auto;
            padding: 2rem;
        }}

        /* Headings */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-weight: 600;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            page-break-after: avoid;
        }}

        h1 {{
            font-size: 2.2em;
            margin-top: 0;
            border-bottom: 2px solid #333;
            padding-bottom: 0.3em;
        }}

        h2 {{
            font-size: 1.6em;
        }}

        h3 {{
            font-size: 1.3em;
        }}

        /* Paragraphs */
        p {{
            margin: 0 0 1em 0;
            text-align: justify;
            orphans: 3;
            widows: 3;
        }}

        /* Images */
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5em auto;
            page-break-inside: avoid;
        }}

        .img-left {{
            float: left;
            margin: 0.5em 1.5em 1em 0;
            max-width: 45%;
        }}

        .img-right {{
            float: right;
            margin: 0.5em 0 1em 1.5em;
            max-width: 45%;
        }}

        .img-center {{
            display: block;
            margin: 1.5em auto;
        }}

        .img-full {{
            display: block;
            margin: 1.5em 0;
            max-width: 100%;
        }}

        .img-small {{
            max-width: 300px;
        }}

        .img-medium {{
            max-width: 500px;
        }}

        .img-large {{
            max-width: 700px;
        }}

        /* Image captions (italic text after images) */
        img + p em, img + p i {{
            display: block;
            text-align: center;
            font-size: 0.9em;
            color: #666;
            margin-top: -0.5em;
            margin-bottom: 1.5em;
        }}

        /* Lists */
        ul, ol {{
            margin: 0 0 1em 0;
            padding-left: 2em;
        }}

        li {{
            margin-bottom: 0.3em;
        }}

        /* Blockquotes */
        blockquote {{
            margin: 1.5em 2em;
            padding: 0.5em 1em;
            border-left: 4px solid #ccc;
            font-style: italic;
            color: #555;
        }}

        /* Code */
        code {{
            font-family: 'Courier New', monospace;
            background: #f5f5f5;
            padding: 0.1em 0.3em;
            border-radius: 3px;
            font-size: 0.9em;
        }}

        pre {{
            background: #f5f5f5;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
            page-break-inside: avoid;
        }}

        pre code {{
            background: none;
            padding: 0;
        }}

        /* Tables */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            page-break-inside: avoid;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 0.5em;
            text-align: left;
        }}

        th {{
            background: #f5f5f5;
            font-weight: 600;
        }}

        /* Links - show URL in print */
        a {{
            color: #0066cc;
            text-decoration: none;
        }}

        @media print {{
            a[href]:after {{
                content: " (" attr(href) ")";
                font-size: 0.8em;
                color: #666;
            }}
        }}

        /* Horizontal rules */
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 2em 0;
        }}

        /* Strong and emphasis */
        strong, b {{
            font-weight: 700;
        }}

        em, i {{
            font-style: italic;
        }}
    </style>
</head>
<body>
    {'<h1>' + chapter_title + '</h1>' if chapter_title else ''}
    {html_content}
</body>
</html>"""

    return html_doc


def generate_chapter_preview_html(memoir_handler, chapter_id: str) -> str:
    """
    Generate HTML preview for a single chapter.

    Args:
        memoir_handler: MemoirHandler instance
        chapter_id: Chapter ID to preview

    Returns:
        HTML string for browser preview
    """
    chapter = memoir_handler.load_chapter(chapter_id)
    if not chapter:
        raise ValueError(f"Chapter {chapter_id} not found")

    title = chapter['frontmatter'].get('title', 'Untitled')
    subtitle = chapter['frontmatter'].get('subtitle', '')
    content = chapter['content']

    # Add subtitle to title if present
    full_title = f"{title}: {subtitle}" if subtitle else title

    return markdown_to_html(content, full_title)


def generate_chapter_pdf(memoir_handler, chapter_id: str, output_path: Path) -> bool:
    """
    Generate PDF for a single chapter.

    Args:
        memoir_handler: MemoirHandler instance
        chapter_id: Chapter ID to export
        output_path: Path where PDF should be saved

    Returns:
        True if successful, raises exception otherwise
    """
    # Check if WeasyPrint is available
    is_available, error_message = check_weasyprint_available()
    if not is_available:
        raise RuntimeError(error_message)

    from weasyprint import HTML, CSS

    # Generate HTML content
    html_content = generate_chapter_preview_html(memoir_handler, chapter_id)

    # Convert to PDF with WeasyPrint
    HTML(string=html_content, base_url=str(memoir_handler.data_dir)).write_pdf(
        output_path,
        stylesheets=[CSS(string='''
            @page {
                size: A4;
                margin: 2.5cm 2cm;
            }
        ''')]
    )

    return True
