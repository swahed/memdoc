"""
Unit tests for image_handler.py

Tests image upload, validation, and markdown generation.
"""

import pytest
from pathlib import Path
from core.image_handler import save_uploaded_image, check_image_resolution, generate_image_markdown
from PIL import Image
import io


class TestImageResolutionCheck:
    """Tests for image resolution checking."""

    def test_check_high_resolution_image(self, tmp_path):
        """Test resolution check with high DPI image."""
        # Create a test image with high DPI
        img = Image.new('RGB', (3000, 2000), color='red')
        img_path = tmp_path / "high_res.jpg"
        img.save(img_path, dpi=(300, 300))

        is_suitable, message = check_image_resolution(img_path)

        assert is_suitable is True
        assert "suitable" in message.lower()

    def test_check_low_resolution_image(self, tmp_path):
        """Test resolution check with low DPI image."""
        # Create a test image with low resolution
        img = Image.new('RGB', (800, 600), color='blue')
        img_path = tmp_path / "low_res.jpg"
        img.save(img_path)

        is_suitable, message = check_image_resolution(img_path)

        assert is_suitable is False
        assert "low" in message.lower()

    def test_check_nonexistent_image(self, tmp_path):
        """Test resolution check with non-existent file."""
        img_path = tmp_path / "nonexistent.jpg"

        is_suitable, message = check_image_resolution(img_path)

        assert is_suitable is False
        assert "error" in message.lower()


class TestImageUpload:
    """Tests for image upload and saving."""

    def test_save_uploaded_image(self, tmp_path):
        """Test saving an uploaded image."""
        # Create a test image in memory
        img = Image.new('RGB', (1920, 1080), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_data = img_bytes.getvalue()

        # Save image
        images_dir = tmp_path / "images"
        saved_path, info = save_uploaded_image(img_data, "test_photo.jpg", images_dir)

        # Verify file was saved
        assert saved_path.exists()
        assert saved_path.name == "test_photo.jpg"
        assert info['saved_filename'] == "test_photo.jpg"
        assert info['original_filename'] == "test_photo.jpg"
        assert 'original_dimensions' in info
        assert info['optimized'] is False

    def test_save_duplicate_filename(self, tmp_path):
        """Test saving image with duplicate filename adds timestamp."""
        img = Image.new('RGB', (800, 600), color='yellow')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_data = img_bytes.getvalue()

        images_dir = tmp_path / "images"

        # Save first image
        saved_path1, info1 = save_uploaded_image(img_data, "photo.jpg", images_dir)

        # Save second image with same filename
        saved_path2, info2 = save_uploaded_image(img_data, "photo.jpg", images_dir)

        # Verify both files exist with different names
        assert saved_path1.exists()
        assert saved_path2.exists()
        assert saved_path1 != saved_path2
        assert info2['saved_filename'] != "photo.jpg"
        assert "photo_" in info2['saved_filename']

    def test_save_large_image_gets_optimized(self, tmp_path):
        """Test that large images are automatically resized."""
        # Create a very large image
        img = Image.new('RGB', (6000, 4000), color='purple')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_data = img_bytes.getvalue()

        images_dir = tmp_path / "images"
        saved_path, info = save_uploaded_image(img_data, "large.jpg", images_dir, optimize=True)

        # Verify image was optimized
        assert saved_path.exists()
        assert info['optimized'] is True
        assert 'new_dimensions' in info
        assert len(info['warnings']) > 0

        # Verify image was actually resized
        saved_img = Image.open(saved_path)
        assert max(saved_img.size) <= 4000

    def test_save_image_sanitizes_filename(self, tmp_path):
        """Test that unsafe filenames are sanitized."""
        img = Image.new('RGB', (800, 600), color='cyan')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_data = img_bytes.getvalue()

        images_dir = tmp_path / "images"
        saved_path, info = save_uploaded_image(
            img_data,
            "my photo!@#$%^&*().jpg",
            images_dir
        )

        # Verify filename was sanitized
        assert saved_path.exists()
        assert '!' not in saved_path.name
        assert '@' not in saved_path.name
        assert '_' in saved_path.name  # Special chars replaced with underscore

    def test_save_png_image(self, tmp_path):
        """Test saving PNG format image."""
        img = Image.new('RGBA', (1000, 800), color=(255, 0, 0, 128))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_data = img_bytes.getvalue()

        images_dir = tmp_path / "images"
        saved_path, info = save_uploaded_image(img_data, "test.png", images_dir)

        assert saved_path.exists()
        assert saved_path.suffix == '.png'

    def test_save_invalid_image_raises_error(self, tmp_path):
        """Test that invalid image data raises an error."""
        invalid_data = b"This is not an image"
        images_dir = tmp_path / "images"

        with pytest.raises(ValueError, match="Failed to save image"):
            save_uploaded_image(invalid_data, "invalid.jpg", images_dir)


class TestImageMarkdownGeneration:
    """Tests for generating image markdown."""

    def test_generate_basic_markdown(self):
        """Test generating basic image markdown."""
        markdown = generate_image_markdown("../images/photo.jpg", "My Photo", "center", "medium")

        assert "![My Photo](../images/photo.jpg)" in markdown
        assert "{: .img-center .img-medium}" in markdown

    def test_generate_markdown_without_caption(self):
        """Test generating markdown without caption."""
        markdown = generate_image_markdown("../images/test.png", "", "left", "small")

        assert "![](../images/test.png)" in markdown
        assert "{: .img-left .img-small}" in markdown

    def test_generate_markdown_all_positions(self):
        """Test all position options."""
        positions = ["left", "center", "right", "full"]

        for pos in positions:
            markdown = generate_image_markdown("../images/img.jpg", "Test", pos, "medium")
            assert f".img-{pos}" in markdown

    def test_generate_markdown_all_sizes(self):
        """Test all size options."""
        sizes = ["small", "medium", "large", "full"]

        for size in sizes:
            markdown = generate_image_markdown("../images/img.jpg", "Test", "center", size)
            assert f".img-{size}" in markdown
