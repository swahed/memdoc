"""
MemDoc - Memoir Documentation Tool
Main application entry point
"""

import sys
import json
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from core.markdown_handler import MemoirHandler

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
    """Get writing prompts."""
    try:
        prompts_file = Path('prompts/writing_prompts.json')
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
