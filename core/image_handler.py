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
                    return False, f"Image DPI ({avg_dpi:.0f}) is below recommended {min_dpi} for printing"
            else:
                # Estimate DPI based on size (assume 8x10 inch print)
                estimated_dpi = min(width / 8, height / 10)
                if estimated_dpi < min_dpi:
                    return False, f"Image resolution ({width}x{height}px) may be too low for quality printing"

            return True, "Image resolution is suitable for printing"

    except Exception as e:
        return False, f"Error checking image: {str(e)}"


def save_uploaded_image(file_data: bytes, filename: str, images_dir: Path) -> Path:
    """
    Save an uploaded image to the images directory.

    Args:
        file_data: Binary file data
        filename: Desired filename
        images_dir: Path to images directory

    Returns:
        Path to saved image
    """
    # TODO: Implement image saving with optional optimization
    pass


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
