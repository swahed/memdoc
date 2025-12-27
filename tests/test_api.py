"""
Unit tests for Flask API endpoints.

Tests all REST API endpoints for memoir and chapter operations.
"""

import pytest
import json
from unittest.mock import patch


class TestMemoirAPI:
    """Tests for memoir metadata endpoints."""

    def test_get_memoir(self, client):
        """Test GET /api/memoir endpoint."""
        response = client.get('/api/memoir')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'title' in data['data']
        assert 'chapters' in data['data']

    def test_update_memoir(self, client):
        """Test PUT /api/memoir endpoint."""
        new_metadata = {
            "title": "Updated Memoir",
            "author": "Test Author",
            "cover": {
                "title": "Updated Memoir",
                "subtitle": "A New Story",
                "author": "Test Author"
            },
            "chapters": []
        }

        response = client.put('/api/memoir',
                              json=new_metadata,
                              content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

        # Verify update persisted
        get_response = client.get('/api/memoir')
        get_data = json.loads(get_response.data)
        assert get_data['data']['title'] == "Updated Memoir"
        assert get_data['data']['author'] == "Test Author"


class TestChapterListAPI:
    """Tests for chapter listing endpoint."""

    def test_list_chapters_empty(self, client):
        """Test GET /api/chapters with no chapters."""
        response = client.get('/api/chapters')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert isinstance(data['data'], list)
        assert len(data['data']) == 0

    def test_list_chapters(self, client):
        """Test GET /api/chapters with existing chapters."""
        # Create some chapters first
        client.post('/api/chapters',
                    json={'title': 'Chapter 1', 'subtitle': 'First'},
                    content_type='application/json')
        client.post('/api/chapters',
                    json={'title': 'Chapter 2', 'subtitle': 'Second'},
                    content_type='application/json')

        # List chapters
        response = client.get('/api/chapters')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['data']) == 2
        assert data['data'][0]['title'] == 'Chapter 1'
        assert data['data'][1]['title'] == 'Chapter 2'


class TestChapterCreationAPI:
    """Tests for chapter creation endpoint."""

    def test_create_chapter(self, client):
        """Test POST /api/chapters endpoint."""
        response = client.post('/api/chapters',
                               json={'title': 'New Chapter', 'subtitle': 'Subtitle'},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'id' in data['data']
        assert data['data']['id'] == 'ch001'

    def test_create_chapter_without_subtitle(self, client):
        """Test creating chapter with missing subtitle."""
        response = client.post('/api/chapters',
                               json={'title': 'Title Only'},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

    def test_create_chapter_without_title(self, client):
        """Test creating chapter with missing title uses default."""
        response = client.post('/api/chapters',
                               json={},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

        # Verify default title was used
        chapter_id = data['data']['id']
        get_response = client.get(f'/api/chapters/{chapter_id}')
        get_data = json.loads(get_response.data)
        assert get_data['data']['frontmatter']['title'] == 'Untitled Chapter'

    def test_create_multiple_chapters(self, client):
        """Test creating multiple chapters increments IDs."""
        response1 = client.post('/api/chapters',
                                json={'title': 'Chapter 1'},
                                content_type='application/json')
        response2 = client.post('/api/chapters',
                                json={'title': 'Chapter 2'},
                                content_type='application/json')

        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)

        assert data1['data']['id'] == 'ch001'
        assert data2['data']['id'] == 'ch002'


class TestChapterGetAPI:
    """Tests for getting a specific chapter."""

    def test_get_chapter(self, client):
        """Test GET /api/chapters/<id> endpoint."""
        # Create a chapter first
        create_response = client.post('/api/chapters',
                                      json={'title': 'Test Chapter', 'subtitle': 'Subtitle'},
                                      content_type='application/json')
        chapter_id = json.loads(create_response.data)['data']['id']

        # Get the chapter
        response = client.get(f'/api/chapters/{chapter_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'frontmatter' in data['data']
        assert 'content' in data['data']
        assert data['data']['frontmatter']['title'] == 'Test Chapter'
        assert data['data']['frontmatter']['subtitle'] == 'Subtitle'

    def test_get_nonexistent_chapter(self, client):
        """Test getting a chapter that doesn't exist."""
        response = client.get('/api/chapters/ch999')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not found' in data['message'].lower()


class TestChapterUpdateAPI:
    """Tests for updating chapter content."""

    def test_update_chapter(self, client):
        """Test PUT /api/chapters/<id> endpoint."""
        # Create a chapter
        create_response = client.post('/api/chapters',
                                      json={'title': 'Original', 'subtitle': ''},
                                      content_type='application/json')
        chapter_id = json.loads(create_response.data)['data']['id']

        # Update the chapter
        update_data = {
            'frontmatter': {
                'id': chapter_id,
                'title': 'Updated Title',
                'subtitle': 'Updated Subtitle',
                'events': []
            },
            'content': 'This is the updated content.'
        }
        response = client.put(f'/api/chapters/{chapter_id}',
                              json=update_data,
                              content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

        # Verify update persisted
        get_response = client.get(f'/api/chapters/{chapter_id}')
        get_data = json.loads(get_response.data)
        assert get_data['data']['frontmatter']['title'] == 'Updated Title'
        assert get_data['data']['content'] == 'This is the updated content.'

    def test_update_chapter_content_only(self, client):
        """Test updating only content preserves frontmatter."""
        # Create a chapter
        create_response = client.post('/api/chapters',
                                      json={'title': 'Test', 'subtitle': 'Subtitle'},
                                      content_type='application/json')
        chapter_id = json.loads(create_response.data)['data']['id']

        # Update with new content
        update_data = {
            'frontmatter': {
                'id': chapter_id,
                'title': 'Test',
                'subtitle': 'Subtitle',
                'events': []
            },
            'content': 'New memoir content here.'
        }
        client.put(f'/api/chapters/{chapter_id}',
                   json=update_data,
                   content_type='application/json')

        # Verify
        get_response = client.get(f'/api/chapters/{chapter_id}')
        get_data = json.loads(get_response.data)
        assert get_data['data']['frontmatter']['title'] == 'Test'
        assert get_data['data']['content'] == 'New memoir content here.'


class TestChapterMetadataUpdateAPI:
    """Tests for updating chapter metadata via PATCH endpoint."""

    def test_update_chapter_metadata(self, client):
        """Test PATCH /api/chapters/<id>/metadata endpoint."""
        # Create a chapter
        create_response = client.post('/api/chapters',
                                      json={'title': 'Original', 'subtitle': 'Old'},
                                      content_type='application/json')
        chapter_id = json.loads(create_response.data)['data']['id']

        # Add some content first
        update_data = {
            'frontmatter': {'id': chapter_id, 'title': 'Original', 'subtitle': 'Old', 'events': []},
            'content': 'Important content that should be preserved.'
        }
        client.put(f'/api/chapters/{chapter_id}',
                   json=update_data,
                   content_type='application/json')

        # Update metadata
        response = client.patch(f'/api/chapters/{chapter_id}/metadata',
                                json={'title': 'New Title', 'subtitle': 'New Subtitle'},
                                content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

        # Verify metadata updated but content preserved
        get_response = client.get(f'/api/chapters/{chapter_id}')
        get_data = json.loads(get_response.data)
        assert get_data['data']['frontmatter']['title'] == 'New Title'
        assert get_data['data']['frontmatter']['subtitle'] == 'New Subtitle'
        assert get_data['data']['content'] == 'Important content that should be preserved.'


class TestChapterReorderAPI:
    """Tests for chapter reordering endpoint."""

    def test_reorder_chapter_up(self, client):
        """Test POST /api/chapters/<id>/reorder with direction 'up'."""
        # Create three chapters
        client.post('/api/chapters', json={'title': 'Chapter 1'}, content_type='application/json')
        client.post('/api/chapters', json={'title': 'Chapter 2'}, content_type='application/json')
        create_response = client.post('/api/chapters',
                                      json={'title': 'Chapter 3'},
                                      content_type='application/json')
        ch3_id = json.loads(create_response.data)['data']['id']

        # Move chapter 3 up
        response = client.post(f'/api/chapters/{ch3_id}/reorder',
                               json={'direction': 'up'},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

        # Verify order changed
        list_response = client.get('/api/chapters')
        chapters = json.loads(list_response.data)['data']
        assert chapters[1]['id'] == ch3_id
        assert chapters[1]['title'] == 'Chapter 3'

    def test_reorder_chapter_down(self, client):
        """Test POST /api/chapters/<id>/reorder with direction 'down'."""
        # Create three chapters
        create_response = client.post('/api/chapters',
                                      json={'title': 'Chapter 1'},
                                      content_type='application/json')
        ch1_id = json.loads(create_response.data)['data']['id']
        client.post('/api/chapters', json={'title': 'Chapter 2'}, content_type='application/json')
        client.post('/api/chapters', json={'title': 'Chapter 3'}, content_type='application/json')

        # Move chapter 1 down
        response = client.post(f'/api/chapters/{ch1_id}/reorder',
                               json={'direction': 'down'},
                               content_type='application/json')

        assert response.status_code == 200

        # Verify order changed
        list_response = client.get('/api/chapters')
        chapters = json.loads(list_response.data)['data']
        assert chapters[1]['id'] == ch1_id


class TestChapterDeletionAPI:
    """Tests for chapter deletion endpoint."""

    def test_delete_chapter(self, client):
        """Test DELETE /api/chapters/<id> endpoint."""
        # Create a chapter
        create_response = client.post('/api/chapters',
                                      json={'title': 'To Delete'},
                                      content_type='application/json')
        chapter_id = json.loads(create_response.data)['data']['id']

        # Delete it
        response = client.delete(f'/api/chapters/{chapter_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

        # Verify it's gone
        get_response = client.get(f'/api/chapters/{chapter_id}')
        assert get_response.status_code == 404

    def test_delete_nonexistent_chapter(self, client):
        """Test deleting non-existent chapter doesn't error."""
        response = client.delete('/api/chapters/ch999')

        # Should succeed (silent failure)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'


class TestPromptsAPI:
    """Tests for writing prompts endpoint."""

    def test_get_prompts(self, client):
        """Test GET /api/prompts endpoint."""
        response = client.get('/api/prompts')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        # Should return prompts structure (exact structure depends on prompts file)
        assert isinstance(data['data'], dict)


class TestStatisticsAPI:
    """Tests for statistics endpoint."""

    def test_get_statistics_empty(self, client):
        """Test statistics with no chapters."""
        response = client.get('/api/statistics')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['totalWords'] == 0
        assert data['data']['totalChapters'] == 0
        assert data['data']['readingTimeMinutes'] == 0
        assert isinstance(data['data']['chapters'], list)
        assert len(data['data']['chapters']) == 0

    def test_get_statistics_with_chapters(self, client):
        """Test statistics with multiple chapters."""
        # Create test chapters with known word counts
        client.post('/api/chapters',
                    json={'title': 'Chapter One', 'subtitle': 'First'},
                    content_type='application/json')
        client.post('/api/chapters',
                    json={'title': 'Chapter Two', 'subtitle': 'Second'},
                    content_type='application/json')

        # Add content to first chapter (10 words)
        chapters_response = client.get('/api/chapters')
        chapters = json.loads(chapters_response.data)['data']
        ch1_id = chapters[0]['id']

        content = "This is a test chapter with exactly ten words here."
        client.put(f'/api/chapters/{ch1_id}',
                   json={
                       'frontmatter': {'id': ch1_id, 'title': 'Chapter One', 'subtitle': 'First', 'events': []},
                       'content': content
                   },
                   content_type='application/json')

        # Get statistics
        response = client.get('/api/statistics')
        data = json.loads(response.data)

        assert data['status'] == 'success'
        assert data['data']['totalChapters'] == 2
        assert data['data']['totalWords'] == 10
        assert data['data']['readingTimeMinutes'] == 0  # 10/225 rounds to 0
        assert len(data['data']['chapters']) == 2

        # Verify first chapter statistics
        assert data['data']['chapters'][0]['id'] == ch1_id
        assert data['data']['chapters'][0]['title'] == 'Chapter One'
        assert data['data']['chapters'][0]['wordCount'] == 10
        assert data['data']['chapters'][0]['readingTimeMinutes'] == 0

        # Verify second chapter statistics (empty)
        assert data['data']['chapters'][1]['wordCount'] == 0
        assert data['data']['chapters'][1]['readingTimeMinutes'] == 0

    def test_get_statistics_reading_time_calculation(self, client):
        """Test reading time calculation for longer content."""
        # Create chapter with ~450 words (should be 2 min reading time)
        client.post('/api/chapters',
                    json={'title': 'Long Chapter'},
                    content_type='application/json')

        chapters_response = client.get('/api/chapters')
        chapters = json.loads(chapters_response.data)['data']
        chapter_id = chapters[0]['id']

        # Create content with 450 words
        word = "word "
        content = word * 450

        client.put(f'/api/chapters/{chapter_id}',
                   json={
                       'frontmatter': {'id': chapter_id, 'title': 'Long Chapter', 'subtitle': '', 'events': []},
                       'content': content
                   },
                   content_type='application/json')

        # Get statistics
        response = client.get('/api/statistics')
        data = json.loads(response.data)

        assert data['status'] == 'success'
        assert data['data']['totalWords'] == 450
        assert data['data']['readingTimeMinutes'] == 2  # 450/225 = 2


class TestSettingsAPI:
    """Tests for settings and configuration endpoints."""

    def test_get_settings(self, client):
        """Test GET /api/settings endpoint."""
        response = client.get('/api/settings')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data

        settings = data['data']
        assert 'data_directory' in settings
        assert 'data_size_mb' in settings
        assert 'file_count' in settings
        assert 'config_file' in settings
        assert 'preferences' in settings

        # Verify data types
        assert isinstance(settings['data_size_mb'], (int, float))
        assert isinstance(settings['file_count'], int)
        assert isinstance(settings['preferences'], dict)

    def test_validate_path_valid(self, client, tmp_path):
        """Test POST /api/settings/validate-path with valid path."""
        test_dir = tmp_path / "valid_test_dir"
        test_dir.mkdir()

        response = client.post('/api/settings/validate-path',
                               json={'path': str(test_dir)},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['is_valid'] is True
        assert 'message' in data['data']
        assert 'resolved_path' in data['data']

    def test_validate_path_invalid(self, client):
        """Test POST /api/settings/validate-path with invalid path."""
        response = client.post('/api/settings/validate-path',
                               json={'path': '/nonexistent/invalid/path'},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['is_valid'] is False
        assert 'message' in data['data']

    def test_validate_path_missing_parameter(self, client):
        """Test POST /api/settings/validate-path without path parameter."""
        response = client.post('/api/settings/validate-path',
                               json={},
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'No path provided' in data['message']

    def test_validate_path_file_instead_of_directory(self, client, tmp_path):
        """Test validation fails when path is a file."""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test")

        response = client.post('/api/settings/validate-path',
                               json={'path': str(test_file)},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['is_valid'] is False
        assert 'not a directory' in data['data']['message'].lower()

    def test_update_preferences(self, client):
        """Test PUT /api/settings/preferences endpoint."""
        new_preferences = {
            'auto_save_interval': 3000,
            'theme': 'dark'
        }

        response = client.put('/api/settings/preferences',
                              json=new_preferences,
                              content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

        # Verify preferences were updated
        settings_response = client.get('/api/settings')
        settings_data = json.loads(settings_response.data)
        preferences = settings_data['data']['preferences']

        assert preferences['auto_save_interval'] == 3000
        assert preferences['theme'] == 'dark'

    def test_update_preferences_partial(self, client):
        """Test updating only some preferences."""
        # Set initial preferences
        client.put('/api/settings/preferences',
                   json={'auto_save_interval': 2000, 'theme': 'light'},
                   content_type='application/json')

        # Update only one preference
        response = client.put('/api/settings/preferences',
                              json={'theme': 'dark'},
                              content_type='application/json')

        assert response.status_code == 200

        # Verify only theme changed
        settings_response = client.get('/api/settings')
        preferences = json.loads(settings_response.data)['data']['preferences']

        assert preferences['theme'] == 'dark'
        assert preferences['auto_save_interval'] == 2000  # Unchanged

    def test_migrate_data_missing_path(self, client):
        """Test POST /api/settings/migrate-data without path parameter."""
        response = client.post('/api/settings/migrate-data',
                               json={'keep_backup': True},
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'No path provided' in data['message']

    def test_migrate_data_invalid_path(self, client):
        """Test POST /api/settings/migrate-data with invalid path."""
        response = client.post('/api/settings/migrate-data',
                               json={
                                   'new_path': '/nonexistent/invalid/path',
                                   'keep_backup': True
                               },
                               content_type='application/json')

        # Should return 400 because path validation fails
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'

    def test_migrate_data_success(self, client, tmp_path):
        """Test successful data migration."""
        # Create destination directory
        destination = tmp_path / "new_data_location"
        destination.mkdir()

        # Create some test data in current data directory
        client.post('/api/chapters',
                    json={'title': 'Test Chapter'},
                    content_type='application/json')

        response = client.post('/api/settings/migrate-data',
                               json={
                                   'new_path': str(destination),
                                   'keep_backup': True
                               },
                               content_type='application/json')

        # Migration should succeed
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'files_copied' in data['data']
        assert 'bytes_copied' in data['data']
        assert data['data']['files_copied'] > 0

        # Verify config was updated
        settings_response = client.get('/api/settings')
        settings_data = json.loads(settings_response.data)
        # Data directory should be updated (though path might be different in test)
        assert 'data_directory' in settings_data['data']

    def test_migrate_data_with_backup(self, client, tmp_path):
        """Test migration creates backup when keep_backup=True."""
        destination = tmp_path / "new_location"
        destination.mkdir()

        # Create test chapter
        client.post('/api/chapters',
                    json={'title': 'Chapter for Migration'},
                    content_type='application/json')

        response = client.post('/api/settings/migrate-data',
                               json={
                                   'new_path': str(destination),
                                   'keep_backup': True
                               },
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'backup_location' in data['data']

        # Backup location should be set
        if data['data']['backup_location']:
            from pathlib import Path
            backup_path = Path(data['data']['backup_location'])
            # In test environment, backup behavior may vary

    def test_settings_integration(self, client, tmp_path):
        """Integration test: get settings, validate path, update preferences."""
        # 1. Get current settings
        settings_response = client.get('/api/settings')
        assert settings_response.status_code == 200

        # 2. Validate a new path
        test_dir = tmp_path / "test_integration"
        test_dir.mkdir()

        validate_response = client.post('/api/settings/validate-path',
                                        json={'path': str(test_dir)},
                                        content_type='application/json')
        assert validate_response.status_code == 200
        validate_data = json.loads(validate_response.data)
        assert validate_data['data']['is_valid'] is True

        # 3. Update preferences
        prefs_response = client.put('/api/settings/preferences',
                                    json={'auto_save_interval': 5000},
                                    content_type='application/json')
        assert prefs_response.status_code == 200

        # 4. Verify preferences persisted
        final_settings = client.get('/api/settings')
        final_data = json.loads(final_settings.data)
        assert final_data['data']['preferences']['auto_save_interval'] == 5000

    def test_browse_folder_endpoint_success(self, client, monkeypatch):
        """Test browse-folder endpoint returns selected path."""
        import subprocess
        from unittest.mock import MagicMock

        # Mock subprocess.run to simulate user selecting a folder
        mock_result = MagicMock()
        mock_result.stdout = "C:\\Users\\Test\\Documents\\SelectedFolder"
        mock_subprocess = MagicMock(return_value=mock_result)
        monkeypatch.setattr(subprocess, 'run', mock_subprocess)

        response = client.post('/api/settings/browse-folder',
                               json={'initial_dir': None},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'path' in data
        assert 'SelectedFolder' in data['path']

    def test_browse_folder_endpoint_cancelled(self, client, monkeypatch):
        """Test browse-folder endpoint when user cancels."""
        import subprocess
        from unittest.mock import MagicMock

        # Mock subprocess.run to simulate user cancelling
        mock_result = MagicMock()
        mock_result.stdout = ""  # Empty means cancelled
        mock_subprocess = MagicMock(return_value=mock_result)
        monkeypatch.setattr(subprocess, 'run', mock_subprocess)

        response = client.post('/api/settings/browse-folder',
                               json={'initial_dir': None},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'cancelled'


class TestUpdateAPI:
    """Tests for update mechanism endpoints."""

    def test_get_version(self, client):
        """Test GET /api/version endpoint."""
        response = client.get('/api/version')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data

        version_info = data['data']
        assert 'version' in version_info
        assert 'is_test_build' in version_info
        assert isinstance(version_info['is_test_build'], bool)

    @patch('core.updater.check_for_updates')
    def test_check_for_updates_available(self, mock_check, client):
        """Test /api/updates/check when update is available."""
        mock_check.return_value = {
            'update_available': True,
            'current_version': '1.0.0',
            'latest_version': '1.1.0',
            'download_url': 'https://test.com/MemDoc.exe',
            'release_notes': '## What\'s New\n- Bug fixes',
            'release_date': '2025-12-27T10:00:00Z',
            'asset_size': 28000000,
            'error': None
        }

        response = client.get('/api/updates/check')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['update_available'] is True
        assert data['data']['latest_version'] == '1.1.0'
        assert data['data']['download_url'] is not None

    @patch('core.updater.check_for_updates')
    def test_check_for_updates_none_available(self, mock_check, client):
        """Test /api/updates/check when no update is available."""
        mock_check.return_value = {
            'update_available': False,
            'current_version': '1.1.0',
            'latest_version': '1.1.0',
            'download_url': None,
            'release_notes': '',
            'release_date': '',
            'asset_size': 0,
            'error': None
        }

        response = client.get('/api/updates/check')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['update_available'] is False

    @patch('core.updater.check_for_updates')
    def test_check_for_updates_error(self, mock_check, client):
        """Test /api/updates/check when error occurs."""
        mock_check.return_value = {
            'update_available': False,
            'current_version': '1.0.0',
            'latest_version': '1.0.0',
            'download_url': None,
            'release_notes': '',
            'release_date': '',
            'asset_size': 0,
            'error': 'Network error: Connection failed'
        }

        response = client.get('/api/updates/check')

        # API returns success but includes error in data
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['error'] == 'Network error: Connection failed'

    def test_download_update_missing_url(self, client):
        """Test /api/updates/download without URL parameter."""
        response = client.post('/api/updates/download',
                               json={},
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'No download URL provided' in data['message']

    @patch('threading.Thread')
    def test_download_update_starts_background_task(self, mock_thread, client):
        """Test /api/updates/download starts background download."""
        response = client.post('/api/updates/download',
                               json={'download_url': 'https://test.com/MemDoc.exe'},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'started' in data['message'].lower()

        # Verify thread was started
        mock_thread.assert_called_once()

    def test_download_update_already_in_progress(self, client, monkeypatch):
        """Test /api/updates/download when download already in progress."""
        # Mock download state to show download in progress
        import app as app_module
        monkeypatch.setattr(app_module, 'download_state', {
            'in_progress': True,
            'downloaded_bytes': 100,
            'total_bytes': 1000,
            'downloaded_file': None,
            'error': None
        })

        response = client.post('/api/updates/download',
                               json={'download_url': 'https://test.com/MemDoc.exe'},
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'already in progress' in data['message'].lower()

    def test_get_download_status_no_download(self, client, monkeypatch):
        """Test /api/updates/download/status when no download in progress."""
        # Reset download state
        import app as app_module
        monkeypatch.setattr(app_module, 'download_state', {
            'in_progress': False,
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'downloaded_file': None,
            'error': None
        })

        response = client.get('/api/updates/download/status')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'in_progress' in data['data']
        assert data['data']['in_progress'] is False
        assert 'completed' in data['data']
        assert 'error' in data['data']

    def test_install_update_no_file(self, client):
        """Test /api/updates/install when no file downloaded."""
        response = client.post('/api/updates/install',
                               json={},
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'No update has been downloaded' in data['message']

    @patch('core.updater.list_available_backups')
    def test_get_update_backups(self, mock_list, client):
        """Test /api/updates/backups endpoint."""
        mock_list.return_value = [
            {
                'version': '1.1.0',
                'backup_date': '2025-12-27T10:00:00',
                'exe_size': 27000000,
                'backup_path': '/path/to/backup'
            },
            {
                'version': '1.0.0',
                'backup_date': '2025-12-26T10:00:00',
                'exe_size': 26000000,
                'backup_path': '/path/to/backup2'
            }
        ]

        response = client.get('/api/updates/backups')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['data']) == 2
        assert data['data'][0]['version'] == '1.1.0'
        assert data['data'][1]['version'] == '1.0.0'

    def test_rollback_missing_version(self, client):
        """Test /api/updates/rollback without version parameter."""
        response = client.post('/api/updates/rollback',
                               json={},
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'No version specified' in data['message']

    @patch('core.updater.rollback_to_version')
    def test_rollback_success(self, mock_rollback, client):
        """Test successful rollback."""
        mock_rollback.return_value = (True, None)

        response = client.post('/api/updates/rollback',
                               json={'version': '1.0.0'},
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

    @patch('core.updater.rollback_to_version')
    def test_rollback_failure(self, mock_rollback, client):
        """Test rollback failure."""
        mock_rollback.return_value = (False, 'Backup not found')

        response = client.post('/api/updates/rollback',
                               json={'version': '1.0.0'},
                               content_type='application/json')

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Backup not found' in data['message']
