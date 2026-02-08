"""
Generate MemDoc application icon (.ico file).
Creates a simple book/pen motif at multiple sizes.
"""
from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path


def create_icon_image(size):
    """Create a single icon image at the given size."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scale factor
    s = size / 256

    # Background - rounded rectangle (warm cream/paper color)
    margin = int(16 * s)
    bg_color = (89, 130, 175, 255)  # Steel blue
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=int(32 * s),
        fill=bg_color
    )

    # Book shape - white pages
    book_left = int(48 * s)
    book_top = int(56 * s)
    book_right = int(208 * s)
    book_bottom = int(208 * s)
    page_color = (255, 255, 255, 240)

    # Left page
    draw.rounded_rectangle(
        [book_left, book_top, int(124 * s), book_bottom],
        radius=int(8 * s),
        fill=page_color
    )

    # Right page
    draw.rounded_rectangle(
        [int(132 * s), book_top, book_right, book_bottom],
        radius=int(8 * s),
        fill=page_color
    )

    # Book spine - center line
    spine_color = (60, 100, 140, 200)
    spine_x = int(128 * s)
    draw.line(
        [(spine_x, book_top + int(8 * s)), (spine_x, book_bottom - int(8 * s))],
        fill=spine_color,
        width=max(1, int(3 * s))
    )

    # Text lines on left page (simulating writing)
    line_color = (180, 180, 180, 200)
    line_width = max(1, int(2 * s))
    for i in range(5):
        y = int((85 + i * 22) * s)
        x1 = int(60 * s)
        x2 = int(115 * s) - (i % 2) * int(12 * s)
        if y < book_bottom - int(16 * s):
            draw.line([(x1, y), (x2, y)], fill=line_color, width=line_width)

    # Text lines on right page
    for i in range(5):
        y = int((85 + i * 22) * s)
        x1 = int(142 * s)
        x2 = int(198 * s) - (i % 2) * int(12 * s)
        if y < book_bottom - int(16 * s):
            draw.line([(x1, y), (x2, y)], fill=line_color, width=line_width)

    # Pen / quill - diagonal across bottom-right
    pen_color = (220, 180, 60, 255)  # Gold
    pen_tip = (int(190 * s), int(190 * s))
    pen_end = (int(230 * s), int(150 * s))

    # Pen body
    draw.line([pen_tip, pen_end], fill=pen_color, width=max(2, int(6 * s)))

    # Pen tip
    tip_color = (60, 60, 60, 255)
    draw.line(
        [pen_tip, (int(196 * s), int(184 * s))],
        fill=tip_color,
        width=max(1, int(4 * s))
    )

    return img


def main():
    # Ensure output directory exists
    output_dir = Path(__file__).parent.parent / 'static' / 'images'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate icon at multiple sizes
    sizes = [16, 32, 48, 256]
    images = []

    for size in sizes:
        img = create_icon_image(size)
        images.append(img)
        print(f"  Created {size}x{size} icon")

    # Save as .ico with all sizes
    ico_path = output_dir / 'memdoc.ico'
    images[0].save(
        str(ico_path),
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )

    print(f"\nIcon saved to: {ico_path}")


if __name__ == '__main__':
    main()
