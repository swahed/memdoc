"""
MemDoc - Memoir Documentation Tool
Main application entry point
"""

import sys
import json
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
from core.markdown_handler import MemoirHandler
from core.image_handler import save_uploaded_image, check_image_resolution
from core.pdf_generator import generate_chapter_preview_html, generate_chapter_pdf

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Initialize memoir handler
memoir_handler = MemoirHandler(data_dir="data")


@app.route('/')
def index():
    """Render the main editor interface."""
    return render_template('index.html')


@app.route('/api/memoir', methods=['GET'])
def get_memoir():
    """Get memoir metadata."""
    try:
        metadata = memoir_handler.load_memoir_metadata()
        return jsonify({'status': 'success', 'data': metadata})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/memoir', methods=['PUT'])
def update_memoir():
    """Update memoir metadata."""
    try:
        data = request.json
        memoir_handler.save_memoir_metadata(data)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/chapters', methods=['GET'])
def list_chapters():
    """Get list of all chapters."""
    try:
        chapters = memoir_handler.list_chapters()
        return jsonify({'status': 'success', 'data': chapters})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/chapters/<chapter_id>', methods=['GET'])
def get_chapter(chapter_id):
    """Get a specific chapter."""
    try:
        chapter = memoir_handler.load_chapter(chapter_id)
        if chapter is None:
            return jsonify({'status': 'error', 'message': 'Chapter not found'}), 404
        return jsonify({'status': 'success', 'data': chapter})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/chapters', methods=['POST'])
def create_chapter():
    """Create a new chapter."""
    try:
        data = request.json
        title = data.get('title', 'Untitled Chapter')
        subtitle = data.get('subtitle', '')

        chapter_id = memoir_handler.create_chapter(title, subtitle)
        return jsonify({'status': 'success', 'data': {'id': chapter_id}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/chapters/<chapter_id>', methods=['PUT'])
def update_chapter(chapter_id):
    """Update a chapter."""
    try:
        data = request.json
        frontmatter = data.get('frontmatter', {})
        content = data.get('content', '')

        memoir_handler.save_chapter(chapter_id, frontmatter, content)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/chapters/<chapter_id>/metadata', methods=['PATCH'])
def update_chapter_metadata(chapter_id):
    """Update chapter metadata (title, subtitle)."""
    try:
        data = request.json
        title = data.get('title', 'Untitled Chapter')
        subtitle = data.get('subtitle', '')

        memoir_handler.update_chapter_metadata(chapter_id, title, subtitle)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/chapters/<chapter_id>/reorder', methods=['POST'])
def reorder_chapter(chapter_id):
    """Reorder a chapter (move up or down)."""
    try:
        data = request.json
        direction = data.get('direction', 'up')  # 'up' or 'down'

        memoir_handler.reorder_chapters(chapter_id, direction)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/chapters/<chapter_id>', methods=['DELETE'])
def delete_chapter(chapter_id):
    """Delete a chapter."""
    try:
        memoir_handler.delete_chapter(chapter_id)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    """Get writing prompts (German)."""
    try:
        prompts_file = Path('prompts/writing_prompts_de.json')
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        return jsonify({'status': 'success', 'data': prompts})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get word count statistics across all chapters."""
    try:
        chapters = memoir_handler.list_chapters()
        total_words = 0
        chapter_stats = []

        for chapter_info in chapters:
            chapter = memoir_handler.load_chapter(chapter_info['id'])
            if chapter:
                content = chapter['content']
                word_count = len(content.split()) if content.strip() else 0
                total_words += word_count

                chapter_stats.append({
                    'id': chapter_info['id'],
                    'title': chapter['frontmatter'].get('title', 'Untitled'),
                    'subtitle': chapter['frontmatter'].get('subtitle', ''),
                    'wordCount': word_count,
                    'readingTimeMinutes': round(word_count / 225)  # 225 avg words/min
                })

        return jsonify({
            'status': 'success',
            'data': {
                'totalWords': total_words,
                'totalChapters': len(chapters),
                'readingTimeMinutes': round(total_words / 225),
                'chapters': chapter_stats
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/images/upload', methods=['POST'])
def upload_image():
    """Upload an image file."""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400

        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'status': 'error',
                'message': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }), 400

        # Read file data
        file_data = file.read()

        # Save image
        images_dir = memoir_handler.images_dir
        saved_path, info = save_uploaded_image(file_data, file.filename, images_dir)

        # Check resolution for warnings
        is_suitable, resolution_msg = check_image_resolution(saved_path)

        # Compile response with all info and warnings
        response = {
            'status': 'success',
            'data': {
                'filename': info['saved_filename'],
                'path': f'../images/{info["saved_filename"]}',
                'original_filename': info['original_filename'],
                'dimensions': info.get('new_dimensions', info['original_dimensions']),
                'size_mb': info['final_size_mb'],
                'optimized': info['optimized'],
                'warnings': info['warnings'].copy()
            }
        }

        # Add resolution warning
        if not is_suitable:
            response['data']['warnings'].insert(0, resolution_msg)
        else:
            response['data']['resolution_ok'] = True

        return jsonify(response)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/images/<filename>', methods=['GET'])
def get_image(filename):
    """Serve an image file."""
    try:
        images_dir = memoir_handler.images_dir
        return send_from_directory(images_dir, filename)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404


@app.route('/api/images/<filename>', methods=['DELETE'])
def delete_image(filename):
    """Delete an image file."""
    try:
        images_dir = memoir_handler.images_dir
        image_path = images_dir / filename

        if not image_path.exists():
            return jsonify({'status': 'error', 'message': 'Image not found'}), 404

        # Delete the file
        image_path.unlink()

        return jsonify({'status': 'success', 'message': 'Image deleted'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/chapters/<chapter_id>/preview', methods=['GET'])
def preview_chapter(chapter_id):
    """Generate HTML preview of a chapter."""
    try:
        html = generate_chapter_preview_html(memoir_handler, chapter_id)
        return html, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/memoir/preview', methods=['GET'])
def preview_memoir():
    """Generate HTML preview of the entire memoir (cover + all chapters)."""
    try:
        from core.pdf_generator import generate_memoir_preview_html
        html = generate_memoir_preview_html(memoir_handler)
        return html, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/pdf/check', methods=['GET'])
def check_pdf_availability():
    """Check if PDF export is available (WeasyPrint dependencies installed)."""
    try:
        from core.pdf_generator import check_weasyprint_available
        is_available, error_message = check_weasyprint_available()
        return jsonify({
            'status': 'success',
            'available': is_available,
            'message': error_message if not is_available else ''
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'available': False,
            'message': f'Error checking PDF availability: {str(e)}'
        }), 500


@app.route('/api/chapters/<chapter_id>/export/pdf', methods=['GET'])
def export_chapter_pdf(chapter_id):
    """Generate and download PDF of a chapter."""
    import tempfile
    import os

    temp_pdf = None
    try:
        # Generate PDF in temp file
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf.close()

        generate_chapter_pdf(memoir_handler, chapter_id, Path(temp_pdf.name))

        # Get chapter title for filename
        chapter = memoir_handler.load_chapter(chapter_id)
        title = chapter['frontmatter'].get('title', 'chapter') if chapter else 'chapter'
        # Sanitize filename
        safe_title = ''.join(c if c.isalnum() or c in ('-', '_') else '-' for c in title.lower())
        safe_title = safe_title[:30]  # Limit length

        # Send file
        return send_file(
            temp_pdf.name,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{chapter_id}-{safe_title}.pdf'
        )
    except ValueError as e:
        if temp_pdf and os.path.exists(temp_pdf.name):
            os.unlink(temp_pdf.name)
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except RuntimeError as e:
        # PDF dependencies not available - return helpful error message
        if temp_pdf and os.path.exists(temp_pdf.name):
            os.unlink(temp_pdf.name)
        return jsonify({'status': 'error', 'message': str(e), 'type': 'dependency_error'}), 500
    except Exception as e:
        if temp_pdf and os.path.exists(temp_pdf.name):
            os.unlink(temp_pdf.name)
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)


def main():
    """Main entry point."""
    # Check for command-line arguments
    browser_mode = '--browser' in sys.argv
    debug_mode = '--debug' in sys.argv

    if browser_mode:
        # Run as Flask web server
        print("\n" + "="*50)
        print("MemDoc - Memoir Documentation Tool")
        print("="*50)
        print("\nRunning in BROWSER mode")
        print("Open your browser to: http://localhost:5000")
        print("\nPress Ctrl+C to stop the server\n")
        app.run(host='localhost', port=5000, debug=debug_mode)
    else:
        # TODO: Run with Eel for desktop mode
        print("\n" + "="*50)
        print("MemDoc - Memoir Documentation Tool")
        print("="*50)
        print("\nDesktop mode not yet implemented.")
        print("Please run with --browser flag for now:")
        print("  python app.py --browser")
        print("="*50 + "\n")


if __name__ == '__main__':
    main()
