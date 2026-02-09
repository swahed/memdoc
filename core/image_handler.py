"""
Image Handler Module

Manages image uploads, resolution checking, and positioning.
"""

from pathlib import Path
from typing import Tuple, Optional
from PIL import Image


def check_image_resolution(image_path: Path, min_dpi: int = 300) -> Tuple[bool, str]:
    """
    Check if image resolution is suitable for printing.

    Args:
        image_path: Path to image file
        min_dpi: Minimum DPI for print quality (default 300)

    Returns:
        Tuple of (is_suitable, message)
    """
    try:
        with Image.open(image_path) as img:
            # Get image size in pixels
            width, height = img.size

            # Check if image has DPI info
            dpi = img.info.get('dpi')
            if dpi:
                dpi_x, dpi_y = dpi
                avg_dpi = (dpi_x + dpi_y) / 2

                if avg_dpi < min_dpi:
                    return False, f"\u26a0\ufe0f Bild-DPI ({avg_dpi:.0f}) liegt unter den empfohlenen {min_dpi} DPI für Druckqualität"
            else:
                # Estimate DPI based on size (assume 8x10 inch print)
                estimated_dpi = min(width / 8, height / 10)
                if estimated_dpi < min_dpi:
                    return False, f"\u26a0\ufe0f Bildauflösung ({width}x{height}px) ist möglicherweise zu niedrig für gute Druckqualität"

            return True, "Bildauflösung ist geeignet für den Druck"

    except Exception as e:
        return False, f"Fehler beim Prüfen des Bildes: {str(e)}"


def save_uploaded_image(file_data: bytes, filename: str, images_dir: Path,
                       optimize: bool = True, max_size: int = 4000) -> Tuple[Path, dict]:
    """
    Save an uploaded image to the images directory.

    Args:
        file_data: Binary file data
        filename: Desired filename
        images_dir: Path to images directory
        optimize: Whether to optimize/resize large images (default True)
        max_size: Maximum dimension in pixels (default 4000)

    Returns:
        Tuple of (Path to saved image, dict with info including warnings)
    """
    import re
    import io
    from datetime import datetime

    # Ensure images directory exists
    images_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename: remove special chars, keep only alphanumeric, dash, underscore, dot
    safe_filename = re.sub(r'[^\w\-.]', '_', filename)
    safe_filename = safe_filename.lower()

    # Check if file already exists, add timestamp if needed
    final_path = images_dir / safe_filename
    if final_path.exists():
        stem = final_path.stem
        suffix = final_path.suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{stem}_{timestamp}{suffix}"
        final_path = images_dir / safe_filename

    info = {
        'original_filename': filename,
        'saved_filename': safe_filename,
        'warnings': [],
        'optimized': False,
        'original_size_mb': len(file_data) / (1024 * 1024)
    }

    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(file_data))
        width, height = img.size

        info['original_dimensions'] = f"{width}x{height}"

        # Check if optimization is needed
        needs_resize = optimize and (width > max_size or height > max_size)

        if needs_resize:
            # Calculate new dimensions maintaining aspect ratio
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            info['optimized'] = True
            info['new_dimensions'] = f"{new_width}x{new_height}"
            info['warnings'].append(f'Bild wurde von {width}x{height} auf {new_width}x{new_height} Pixel verkleinert')

        # Save image
        save_kwargs = {}
        if img.format == 'JPEG' or final_path.suffix.lower() in ['.jpg', '.jpeg']:
            save_kwargs['quality'] = 90
            save_kwargs['optimize'] = True
        elif img.format == 'PNG' or final_path.suffix.lower() == '.png':
            save_kwargs['optimize'] = True

        img.save(final_path, **save_kwargs)

        # Get final file size
        info['final_size_mb'] = final_path.stat().st_size / (1024 * 1024)

        # Add file size warning if too large
        if info['final_size_mb'] > 10:
            info['warnings'].append(f'Große Dateigröße ({info["final_size_mb"]:.1f} MB)')

        return final_path, info

    except Exception as e:
        raise ValueError(f"Fehler beim Speichern des Bildes: {str(e)}")


def generate_image_markdown(image_path: str, caption: str = "", position: str = "center",
                           size: str = "medium") -> str:
    """
    Generate markdown for an image with positioning.

    Args:
        image_path: Relative path to image
        caption: Image caption
        position: Position (left, center, right, full)
        size: Size (small, medium, large)

    Returns:
        Markdown string with image and attributes
    """
    md = f"![{caption}]({image_path})\n"
    md += f"{{: .img-{position} .img-{size}}}\n"
    return md
