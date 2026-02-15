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
            instructions = """Für den PDF-Export werden GTK-Bibliotheken benötigt, die nicht installiert sind.

So aktivierst du den PDF-Export unter Windows:
1. Lade GTK3 Runtime herunter: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Führe das Installationsprogramm aus
3. Starte MemDoc neu

Alternativ: Nutze die Vorschau-Funktion und klicke dort auf „Drucken", um als PDF zu speichern."""
        elif system == "Darwin":  # macOS
            instructions = """Für den PDF-Export werden Systembibliotheken benötigt, die nicht installiert sind.

So aktivierst du den PDF-Export unter macOS:
1. Installiere Homebrew falls nötig: https://brew.sh
2. Führe aus: brew install pango
3. Starte MemDoc neu

Alternativ: Nutze die Vorschau-Funktion und klicke dort auf „Drucken", um als PDF zu speichern."""
        else:  # Linux
            instructions = """Für den PDF-Export werden Systembibliotheken benötigt, die möglicherweise nicht installiert sind.

So aktivierst du den PDF-Export unter Linux:
1. Installiere die benötigten Pakete:
   - Ubuntu/Debian: sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0
   - Fedora: sudo dnf install pango
2. Starte MemDoc neu

Alternativ: Nutze die Vorschau-Funktion und klicke dort auf „Drucken", um als PDF zu speichern."""

        return False, instructions
    except Exception as e:
        return False, f"PDF-Export nicht verfügbar: {str(e)}"


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
    import re

    # Fix lenient bold/italic: strip spaces before closing markers
    # e.g. "**word **" → "**word**", "*word *" → "*word*"
    if markdown_content:
        markdown_content = re.sub(r'\s+(\*{1,2})(?=\s|$|[.,;:!?\)])', r'\1', markdown_content)

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
    <title>{chapter_title if chapter_title else 'Kapitel'}</title>
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
            clear: both;
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

    title = chapter['frontmatter'].get('title', 'Ohne Titel')
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


def generate_memoir_pdf(memoir_handler, output_path: Path) -> bool:
    """
    Generate PDF for the entire memoir (cover + all chapters).

    Args:
        memoir_handler: MemoirHandler instance
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
    html_content = generate_memoir_preview_html(memoir_handler)

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


def generate_memoir_preview_html(memoir_handler) -> str:
    """
    Generate HTML preview for the entire memoir (cover + all chapters).

    Args:
        memoir_handler: MemoirHandler instance

    Returns:
        HTML string for browser preview of complete memoir
    """
    import markdown2

    # Load memoir metadata
    metadata = memoir_handler.load_memoir_metadata()
    cover = metadata.get('cover', {})

    # Get all chapters in order
    chapters = memoir_handler.list_chapters()

    # Build cover page HTML
    cover_html = ""
    if cover:
        cover_title = cover.get('title', '')
        cover_subtitle = cover.get('subtitle', '')
        cover_author = cover.get('author', '')
        cover_image = cover.get('image', '')
        cover_bg_color = cover.get('backgroundColor', '#f5f5f5')

        # Fix image path for display
        cover_image_url = ''
        if cover_image:
            filename = cover_image.split('/')[-1]
            cover_image_url = f'/api/images/{filename}'

        cover_html = f"""
        <div class="cover-page" style="background-color: {cover_bg_color}; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; page-break-after: always; text-align: center; padding: 2rem;">
            {f'<img src="{cover_image_url}" alt="Cover" style="max-width: 400px; max-height: 400px; margin-bottom: 2rem; border-radius: 8px;" />' if cover_image_url else ''}
            <h1 style="font-size: 3em; margin-bottom: 0.5rem; color: #1a1a1a;">{cover_title or ''}</h1>
            {f'<h2 style="font-size: 1.8em; margin-bottom: 2rem; color: #555; font-weight: 400;">{cover_subtitle}</h2>' if cover_subtitle else ''}
            {f'<p style="font-size: 1.3em; color: #333; margin-top: 3rem;">{cover_author}</p>' if cover_author else ''}
        </div>
        """

    # Build chapters HTML
    import re
    chapters_html = ""
    for idx, chapter_info in enumerate(chapters):
        chapter = memoir_handler.load_chapter(chapter_info['id'])
        if chapter:
            title = chapter['frontmatter'].get('title', 'Ohne Titel')
            subtitle = chapter['frontmatter'].get('subtitle', '')
            content = chapter['content']

            # Fix lenient bold/italic: strip spaces before closing markers
            if content:
                content = re.sub(r'\s+(\*{1,2})(?=\s|$|[.,;:!?\)])', r'\1', content)

            # Convert markdown to HTML
            html_content = markdown2.markdown(
                content,
                extras=[
                    'fenced-code-blocks',
                    'tables',
                    'break-on-newline',
                    'cuddled-lists',
                    'footnotes'
                ]
            )

            # Fix image paths
            html_content = html_content.replace('src="../images/', 'src="/api/images/')

            # Process kramdown-style class attributes
            pattern = r'(<img[^>]*>)(<br\s*/?>)?\s*\{:\s*([^}]+)\}\s*(<br\s*/?>)?'
            def add_classes_to_img(match):
                img_tag = match.group(1)
                classes = match.group(3).strip()
                class_names = ' '.join([c.strip('.') for c in classes.split()])
                if 'class=' in img_tag:
                    img_tag = img_tag.replace('class="', f'class="{class_names} ')
                else:
                    if img_tag.endswith('/>'):
                        img_tag = img_tag[:-2] + f' class="{class_names}" />'
                    elif img_tag.endswith('>'):
                        img_tag = img_tag[:-1] + f' class="{class_names}">'
                return img_tag

            html_content = re.sub(pattern, add_classes_to_img, html_content)

            # Add chapter HTML (with page break before each chapter except first)
            page_break = 'page-break-before: always;' if idx > 0 else ''
            chapters_html += f"""
            <div class="chapter" style="{page_break}">
                <h1 style="font-size: 2.2em; margin-top: 0; border-bottom: 2px solid #333; padding-bottom: 0.3em;">{title}</h1>
                {f'<h2 style="font-size: 1.4em; color: #555; margin-top: -0.5em; margin-bottom: 1.5em; font-weight: 400;">{subtitle}</h2>' if subtitle else ''}
                {html_content}
            </div>
            """

    # Generate complete HTML document
    html_doc = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <title>{cover.get('title', 'Meine Memoiren')}</title>
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
            clear: both;
        }}

        h1 {{
            font-size: 2.2em;
            margin-top: 0;
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

        /* Image captions */
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

        /* Links */
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
    {cover_html}
    {chapters_html}
</body>
</html>"""

    return html_doc
