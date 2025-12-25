"""
Unit tests for Flask API endpoints.

Tests all REST API endpoints for memoir and chapter operations.
"""

import pytest
import json


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
