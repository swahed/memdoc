"""
MemDoc - Memoir Documentation Tool
Main application entry point
"""

import sys
import json
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
from core.markdown_handler import MemoirHandler
from core.image_handler import save_uploaded_image, check_image_resolution
from core.pdf_generator import generate_chapter_preview_html, generate_chapter_pdf
from core.config_manager import (
    load_config, save_config, validate_data_path,
    get_data_dir, get_directory_size, count_files,
    is_first_run, get_default_data_dir
)
from core.data_migrator import migrate_data_directory
from core.version import get_window_title, IS_TEST_BUILD, TEST_BUILD_BRANCH, VERSION


# ===== PyInstaller Path Handling =====
def get_resource_path(relative_path):
    """
    Get absolute path to resource - works for dev and PyInstaller bundled mode.

    When PyInstaller creates the .exe, it unpacks files into sys._MEIPASS.
    This function finds the correct base path for resource files.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # Running in normal Python environment
        base_path = Path(__file__).parent

    return base_path / relative_path


# Configure Flask with proper paths for PyInstaller bundle
app = Flask(
    __name__,
    template_folder=str(get_resource_path('templates')),
    static_folder=str(get_resource_path('static'))
)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Initialize memoir handler (will be set in initialize_memoir_handler)
memoir_handler = None


@app.route('/')
def index():
    """Render the main editor interface."""
    # Check if running from PyInstaller bundle
    is_bundled = getattr(sys, 'frozen', False)

    return render_template(
        'index.html',
        is_test_build=IS_TEST_BUILD,
        test_build_branch=TEST_BUILD_BRANCH,
        version=VERSION,
        is_bundled=is_bundled
    )


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


@app.route('/api/memoir/export/pdf', methods=['GET'])
def export_memoir_pdf():
    """Generate and download PDF of the entire memoir."""
    import tempfile
    import os

    temp_pdf = None
    try:
        # Generate PDF in temp file
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf.close()

        from core.pdf_generator import generate_memoir_pdf
        generate_memoir_pdf(memoir_handler, Path(temp_pdf.name))

        # Get memoir title for filename
        metadata = memoir_handler.load_memoir_metadata()
        title = metadata.get('cover', {}).get('title', 'memoir')
        # Sanitize filename
        safe_title = ''.join(c if c.isalnum() or c in ('-', '_') else '-' for c in title.lower())
        safe_title = safe_title[:30]  # Limit length

        # Send file
        return send_file(
            temp_pdf.name,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{safe_title}.pdf'
        )
    except RuntimeError as e:
        # PDF dependencies not available - return helpful error message
        if temp_pdf and os.path.exists(temp_pdf.name):
            os.unlink(temp_pdf.name)
        return jsonify({'status': 'error', 'message': str(e), 'type': 'dependency_error'}), 500
    except Exception as e:
        if temp_pdf and os.path.exists(temp_pdf.name):
            os.unlink(temp_pdf.name)
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


# ===== Status & Recovery Endpoints =====

@app.route('/api/status/recovery', methods=['GET'])
def check_recovery():
    """Check if memoir.json was recovered from a corrupt file."""
    try:
        backup_path = memoir_handler.recovered_from_corrupt
        if backup_path:
            # Clear the flag so it only shows once
            memoir_handler.recovered_from_corrupt = None
            return jsonify({
                'status': 'success',
                'recovered': True,
                'backupPath': backup_path
            })
        return jsonify({'status': 'success', 'recovered': False})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===== First-Run Onboarding Endpoints =====

@app.route('/api/config/is-first-run', methods=['GET'])
def check_first_run():
    """Check if this is the first run (no memoir data yet)."""
    try:
        return jsonify({
            'status': 'success',
            'firstRun': is_first_run(),
            'defaultDataDir': str(get_default_data_dir())
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/config/initial-setup', methods=['POST'])
def initial_setup():
    """Set up memoir for the first time with user-provided values."""
    global memoir_handler

    try:
        data = request.json
        title = data.get('title', '').strip() or 'My Memoir'
        subtitle = data.get('subtitle', '').strip()
        data_directory = data.get('dataDirectory', '').strip()

        # Update config with data directory if provided
        if data_directory:
            config = load_config()
            config['data_directory'] = data_directory
            save_config(config)

        # Reinitialize memoir handler with (possibly new) data directory
        memoir_handler = initialize_memoir_handler()

        # Create memoir.json with user's values
        memoir_data = {
            "title": title,
            "author": "",
            "cover": {
                "title": title,
                "subtitle": subtitle,
                "author": ""
            },
            "chapters": []
        }
        memoir_handler.save_memoir_metadata(memoir_data)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===== Settings & Configuration Endpoints =====

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current application settings including data directory."""
    try:
        config = load_config()
        data_dir = get_data_dir()

        # Get size and file count of current data directory
        total_size = get_directory_size(data_dir)
        file_count = count_files(data_dir)

        return jsonify({
            'status': 'success',
            'data': {
                'data_directory': str(data_dir),
                'data_size_mb': total_size / (1024 * 1024),
                'file_count': file_count,
                'config_file': str(Path.home() / ".memdoc" / "config.json"),
                'preferences': config.get('preferences', {})
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/settings/validate-path', methods=['POST'])
def validate_path():
    """Validate a potential data directory path."""
    try:
        data = request.json
        path_str = data.get('path')

        if not path_str:
            return jsonify({'status': 'error', 'message': 'No path provided'}), 400

        path = Path(path_str).resolve()
        is_valid, message = validate_data_path(path)

        return jsonify({
            'status': 'success',
            'data': {
                'is_valid': is_valid,
                'message': message,
                'resolved_path': str(path)
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/settings/migrate-data', methods=['POST'])
def migrate_data():
    """Migrate memoir data to a new directory."""
    try:
        data = request.json
        new_path_str = data.get('new_path')
        keep_backup = data.get('keep_backup', True)

        if not new_path_str:
            return jsonify({'status': 'error', 'message': 'No path provided'}), 400

        new_path = Path(new_path_str).resolve()
        old_path = get_data_dir()

        # Validate new path
        is_valid, message = validate_data_path(new_path)
        if not is_valid:
            return jsonify({'status': 'error', 'message': message}), 400

        # Perform migration
        success, stats = migrate_data_directory(
            old_path,
            new_path,
            keep_backup=keep_backup
        )

        if success:
            # Update config
            config = load_config()
            config['data_directory'] = str(new_path)

            from datetime import datetime
            config['last_migration'] = {
                'timestamp': datetime.now().isoformat(),
                'from': str(old_path),
                'to': str(new_path),
                'backup_kept': keep_backup
            }
            save_config(config)

            # Reinitialize memoir_handler with new path
            global memoir_handler
            memoir_handler = MemoirHandler(data_dir=str(new_path))

            return jsonify({
                'status': 'success',
                'data': {
                    'files_copied': stats['files_copied'],
                    'bytes_copied': stats['bytes_copied'],
                    'backup_location': stats.get('backup_location')
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Migration failed',
                'details': stats.get('error')
            }), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/settings/preferences', methods=['PUT'])
def update_preferences():
    """Update user preferences (non-critical settings)."""
    try:
        preferences = request.json
        config = load_config()
        config['preferences'] = {**config.get('preferences', {}), **preferences}
        save_config(config)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/settings/browse-folder', methods=['POST'])
def browse_folder():
    """Open native folder picker dialog and return selected path."""
    try:
        import subprocess

        # Get initial directory from request (optional)
        data = request.json or {}
        initial_dir = data.get('initial_dir') or str(Path.home())

        if getattr(sys, 'frozen', False):
            # Bundled mode: use PowerShell folder browser (sys.executable is MemDoc.exe)
            ps_script = (
                "Add-Type -AssemblyName System.Windows.Forms; "
                "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
                f"$f.SelectedPath = '{initial_dir}'; "
                "$f.Description = 'Wähle Speicherort für Memoir-Daten'; "
                "if ($f.ShowDialog() -eq 'OK') { $f.SelectedPath }"
            )
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=300
            )
        else:
            # Dev mode: use Python tkinter folder picker script
            script_path = get_resource_path('scripts/folder_picker.py')
            cmd = [sys.executable, str(script_path)]
            if initial_dir:
                cmd.append(initial_dir)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

        # Get selected path from stdout
        selected_folder = result.stdout.strip()

        if selected_folder:
            # Convert to Path and resolve to absolute
            folder_path = Path(selected_folder).resolve()
            return jsonify({
                'status': 'success',
                'path': str(folder_path)
            })
        else:
            # User cancelled
            return jsonify({
                'status': 'cancelled'
            })

    except subprocess.TimeoutExpired:
        return jsonify({'status': 'error', 'message': 'Folder picker timed out'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===== Update Mechanism Endpoints =====

# Global state for tracking download progress
download_state = {
    'in_progress': False,
    'downloaded_bytes': 0,
    'total_bytes': 0,
    'downloaded_file': None,
    'error': None
}


@app.route('/api/version', methods=['GET'])
def get_version():
    """Get current version information."""
    return jsonify({
        'status': 'success',
        'data': {
            'version': VERSION,
            'is_test_build': IS_TEST_BUILD,
            'test_build_branch': TEST_BUILD_BRANCH if IS_TEST_BUILD else None
        }
    })


@app.route('/api/updates/check', methods=['GET'])
def check_updates():
    """Check for available updates from GitHub Releases."""
    try:
        from core.updater import check_for_updates
        update_info = check_for_updates()

        return jsonify({
            'status': 'success',
            'data': update_info
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/updates/download', methods=['POST'])
def start_download_update():
    """Start downloading an update in the background."""
    global download_state

    try:
        # Check if already downloading
        if download_state['in_progress']:
            return jsonify({
                'status': 'error',
                'message': 'Download already in progress'
            }), 400

        # Get download URL from request
        data = request.json
        download_url = data.get('download_url')

        if not download_url:
            return jsonify({
                'status': 'error',
                'message': 'No download URL provided'
            }), 400

        # Reset download state
        download_state = {
            'in_progress': True,
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'downloaded_file': None,
            'error': None
        }

        # Progress callback
        def progress_callback(downloaded, total):
            download_state['downloaded_bytes'] = downloaded
            download_state['total_bytes'] = total

        # Start download in background thread
        import threading
        from core.updater import download_update

        def download_thread():
            success, file_path, error = download_update(download_url, progress_callback)
            download_state['in_progress'] = False
            if success:
                download_state['downloaded_file'] = str(file_path)
            else:
                download_state['error'] = error

        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()

        return jsonify({
            'status': 'success',
            'message': 'Download started'
        })

    except Exception as e:
        download_state['in_progress'] = False
        download_state['error'] = str(e)
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/updates/download/status', methods=['GET'])
def get_download_status():
    """Get the current download progress."""
    global download_state

    return jsonify({
        'status': 'success',
        'data': {
            'in_progress': download_state['in_progress'],
            'downloaded_bytes': download_state['downloaded_bytes'],
            'total_bytes': download_state['total_bytes'],
            'progress_percent': (
                int((download_state['downloaded_bytes'] / download_state['total_bytes']) * 100)
                if download_state['total_bytes'] > 0 else 0
            ),
            'completed': not download_state['in_progress'] and download_state['downloaded_file'] is not None,
            'error': download_state['error']
        }
    })


@app.route('/api/updates/install', methods=['POST'])
def install_update():
    """Install the downloaded update (requires restart)."""
    global download_state

    try:
        # Check if we have a downloaded file
        if not download_state['downloaded_file']:
            return jsonify({
                'status': 'error',
                'message': 'No update has been downloaded'
            }), 400

        downloaded_file = Path(download_state['downloaded_file'])

        if not downloaded_file.exists():
            return jsonify({
                'status': 'error',
                'message': 'Downloaded file not found'
            }), 400

        # Backup current version
        from core.updater import backup_current_version, apply_update

        success, error = backup_current_version()
        if not success:
            return jsonify({
                'status': 'error',
                'message': f'Backup failed: {error}'
            }), 500

        # Apply update - launches Inno Setup installer which handles
        # closing this app, replacing files, and restarting
        success, error = apply_update(downloaded_file)
        if not success:
            return jsonify({
                'status': 'error',
                'message': f'Update installation failed: {error}'
            }), 500

        # Installer will handle closing this app via /CLOSEAPPLICATIONS
        return jsonify({
            'status': 'success',
            'message': 'Installer launched, app will restart...'
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/updates/backups', methods=['GET'])
def list_backups():
    """List all available backup versions."""
    try:
        from core.updater import list_available_backups
        backups = list_available_backups()

        return jsonify({
            'status': 'success',
            'data': backups
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/updates/rollback', methods=['POST'])
def rollback_update():
    """Rollback to a previous version."""
    try:
        data = request.json
        backup_version = data.get('version')

        if not backup_version:
            return jsonify({
                'status': 'error',
                'message': 'No version specified'
            }), 400

        from core.updater import rollback_to_version

        success, error = rollback_to_version(backup_version)
        if not success:
            return jsonify({
                'status': 'error',
                'message': f'Rollback failed: {error}'
            }), 500

        # Rollback uses same update mechanism, so app will restart
        return jsonify({
            'status': 'success',
            'message': f'Rolling back to v{backup_version}, app will restart...'
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ===== Application Initialization =====

def initialize_memoir_handler():
    """Initialize memoir handler with configured data directory and validation."""
    data_dir = get_data_dir()
    is_valid, error_msg = validate_data_path(data_dir, check_not_current=False)

    if not is_valid:
        print(f"\n{'='*60}")
        print("ERROR: Cannot access memoir data directory")
        print(f"Path: {data_dir}")
        print(f"Reason: {error_msg}")
        print("\nPossible solutions:")
        print("1. Ensure OneDrive is running and synced")
        print("2. Check folder permissions")
        print(f"3. Edit config: {Path.home() / '.memdoc' / 'config.json'}")
        print(f"{'='*60}\n")
        sys.exit(1)

    return MemoirHandler(data_dir=str(data_dir))


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use (another instance running)."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True


def main():
    """Main entry point."""
    global memoir_handler

    port = 5000

    # Check if another instance is already running
    if is_port_in_use(port):
        print("MemDoc is already running. Opening in browser...")
        import webbrowser
        webbrowser.open(f'http://localhost:{port}')
        sys.exit(0)

    # Initialize memoir handler with validation
    memoir_handler = initialize_memoir_handler()

    # Check for command-line arguments
    browser_mode = '--browser' in sys.argv
    debug_mode = '--debug' in sys.argv

    if browser_mode:
        # Run as Flask web server
        print("\n" + "="*50)
        print("MemDoc - Memoir Documentation Tool")
        print("="*50)
        print(f"\nData directory: {memoir_handler.data_dir}")
        print("\nRunning in BROWSER mode")
        print("Open your browser to: http://localhost:5000")
        print("\nPress Ctrl+C to stop the server\n")
        app.run(host='localhost', port=5000, debug=debug_mode)
    else:
        # Desktop mode - Flask + Chrome app mode
        print("\n" + "="*50)
        print(f"{get_window_title()}")
        print("="*50)
        print(f"\nData directory: {memoir_handler.data_dir}")
        if IS_TEST_BUILD:
            print(f"\n⚠️  TEST BUILD - Branch: {TEST_BUILD_BRANCH}")
            print("Using sample data from: %APPDATA%/MemDoc-Test/data/")
        print("\nStarting desktop application...")
        print("="*50 + "\n")

        # Start Flask in a background thread
        import threading
        import subprocess
        import time

        server_thread = threading.Thread(
            target=lambda: app.run(host='localhost', port=5000, debug=False, use_reloader=False),
            daemon=True
        )
        server_thread.start()

        # Give Flask a moment to start
        time.sleep(2)

        # Find Chrome or Edge executable (Edge is installed by default on Windows)
        browser_paths = [
            # Chrome
            (r"C:\Program Files\Google\Chrome\Application\chrome.exe", "Chrome"),
            (r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", "Chrome"),
            (os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"), "Chrome"),
            # Edge (installed by default on Windows 10+)
            (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "Edge"),
            (os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"), "Edge"),
        ]

        browser_exe = None
        browser_name = None
        for path, name in browser_paths:
            if os.path.exists(path):
                browser_exe = path
                browser_name = name
                break

        browser_process = None
        if not browser_exe:
            print("Chrome/Edge not found. Opening in default browser...")
            import webbrowser
            webbrowser.open('http://localhost:5000')
        else:
            # Open browser in app mode (looks like a desktop app)
            print(f"Opening {browser_name} in app mode...")
            browser_process = subprocess.Popen([
                browser_exe,
                '--app=http://localhost:5000',
                f'--window-size=1200,800',
                '--window-position=100,100'
            ])

        print("\nMemDoc is running!")
        print("Close the browser window to exit.\n")

        # Keep the server running until browser closes
        try:
            if browser_process:
                # Wait a moment then check if browser process is still alive.
                # Chrome may exit immediately if an existing instance takes over
                # the --app window (process delegates and exits).
                launch_time = time.time()
                min_runtime = 5  # seconds

                while browser_process.poll() is None:
                    time.sleep(1)

                elapsed = time.time() - launch_time
                if elapsed < min_runtime:
                    # Browser process exited too fast - Chrome likely delegated
                    # to an existing instance. Fall back to keeping server alive.
                    print("Browser delegated to existing instance. Server stays running.")
                    print("Press Ctrl+C to stop.\n")
                    while True:
                        time.sleep(1)
                else:
                    print("\nBrowser closed. Shutting down...")
            else:
                # Fallback: no browser process to monitor
                while True:
                    time.sleep(1)
        except (SystemExit, KeyboardInterrupt):
            print("\nShutting down...")
        except Exception as e:
            print(f"\nError: {e}")

        sys.exit(0)


if __name__ == '__main__':
    main()
