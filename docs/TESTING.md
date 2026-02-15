# Testing Guide for MemDoc

## Current Test Status

**165 unit tests passing**, 1 pre-existing failure (`config_manager` default dir name), 8 E2E tests (skipped in CI).

```bash
# Run all tests
py -m pytest tests/ -q --ignore=tests/test_updater.py -k "not test_get_prompts"
```

---

## Testing Infrastructure Setup

### 1. Install Testing Dependencies

```bash
# Add to requirements.txt
pip install pytest pytest-cov pytest-playwright

# Install Playwright browsers
playwright install
```

### 2. Create Test Directory Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── fixtures/                # Test data files
│   └── memoir.json
├── test_markdown_handler.py # Unit tests for markdown operations
├── test_timeline.py         # Unit tests for timeline generation
├── test_api.py              # API endpoint tests
└── e2e/                     # End-to-end tests
    ├── __init__.py
    ├── test_chapter_workflow.py
    └── test_writing_workflow.py
```

---

## Unit Tests to Implement

### Priority 1: Core Backend Tests

#### `tests/test_markdown_handler.py`

Test all chapter operations:

```python
import pytest
import json
from pathlib import Path
from core.markdown_handler import MemoirHandler

@pytest.fixture
def handler(tmp_path):
    """Create a temporary MemoirHandler for testing."""
    return MemoirHandler(data_dir=str(tmp_path))

def test_create_chapter(handler):
    """Test creating a new chapter."""
    chapter_id = handler.create_chapter("Chapter One", "A Beginning")
    assert chapter_id == "ch001"

    chapter = handler.load_chapter(chapter_id)
    assert chapter['frontmatter']['title'] == "Chapter One"
    assert chapter['frontmatter']['subtitle'] == "A Beginning"

def test_load_chapter(handler):
    """Test loading an existing chapter."""
    handler.create_chapter("Test Chapter", "Subtitle")
    chapter = handler.load_chapter("ch001")

    assert chapter is not None
    assert 'frontmatter' in chapter
    assert 'content' in chapter

def test_save_chapter(handler):
    """Test saving chapter content."""
    chapter_id = handler.create_chapter("Test", "")

    new_content = "This is my memoir content."
    frontmatter = {'title': 'Updated Title', 'subtitle': ''}

    handler.save_chapter(chapter_id, frontmatter, new_content)

    loaded = handler.load_chapter(chapter_id)
    assert loaded['frontmatter']['title'] == 'Updated Title'
    assert loaded['content'] == new_content

def test_delete_chapter(handler):
    """Test deleting a chapter."""
    chapter_id = handler.create_chapter("To Delete", "")
    handler.delete_chapter(chapter_id)

    chapter = handler.load_chapter(chapter_id)
    assert chapter is None

def test_reorder_chapters(handler):
    """Test reordering chapters."""
    ch1 = handler.create_chapter("Chapter 1", "")
    ch2 = handler.create_chapter("Chapter 2", "")
    ch3 = handler.create_chapter("Chapter 3", "")

    # Move chapter 3 up
    handler.reorder_chapters(ch3, 'up')

    chapters = handler.list_chapters()
    assert chapters[1]['id'] == ch3
    assert chapters[2]['id'] == ch2

def test_update_chapter_metadata(handler):
    """Test updating chapter title and subtitle."""
    chapter_id = handler.create_chapter("Original", "Old subtitle")
    handler.update_chapter_metadata(chapter_id, "Updated", "New subtitle")

    chapter = handler.load_chapter(chapter_id)
    assert chapter['frontmatter']['title'] == "Updated"
    assert chapter['frontmatter']['subtitle'] == "New subtitle"

def test_list_chapters(handler):
    """Test listing all chapters."""
    handler.create_chapter("Chapter 1", "First")
    handler.create_chapter("Chapter 2", "Second")

    chapters = handler.list_chapters()
    assert len(chapters) == 2
    assert chapters[0]['title'] == "Chapter 1"
    assert chapters[1]['title'] == "Chapter 2"
```

#### `tests/test_api.py`

Test API endpoints:

```python
import pytest
import json
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_chapters(client):
    """Test GET /api/chapters endpoint."""
    response = client.get('/api/chapters')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'data' in data

def test_create_chapter(client):
    """Test POST /api/chapters endpoint."""
    response = client.post('/api/chapters',
        json={'title': 'New Chapter', 'subtitle': 'Subtitle'},
        content_type='application/json')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'id' in data['data']

def test_get_chapter(client):
    """Test GET /api/chapters/<id> endpoint."""
    # First create a chapter
    create_response = client.post('/api/chapters',
        json={'title': 'Test', 'subtitle': ''},
        content_type='application/json')
    chapter_id = json.loads(create_response.data)['data']['id']

    # Then retrieve it
    response = client.get(f'/api/chapters/{chapter_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['frontmatter']['title'] == 'Test'

def test_update_chapter(client):
    """Test PUT /api/chapters/<id> endpoint."""
    # Create chapter
    create_response = client.post('/api/chapters',
        json={'title': 'Original', 'subtitle': ''},
        content_type='application/json')
    chapter_id = json.loads(create_response.data)['data']['id']

    # Update chapter
    response = client.put(f'/api/chapters/{chapter_id}',
        json={'frontmatter': {'title': 'Updated'}, 'content': 'New content'},
        content_type='application/json')

    assert response.status_code == 200

def test_delete_chapter(client):
    """Test DELETE /api/chapters/<id> endpoint."""
    # Create chapter
    create_response = client.post('/api/chapters',
        json={'title': 'To Delete', 'subtitle': ''},
        content_type='application/json')
    chapter_id = json.loads(create_response.data)['data']['id']

    # Delete it
    response = client.delete(f'/api/chapters/{chapter_id}')
    assert response.status_code == 200

    # Verify it's gone
    get_response = client.get(f'/api/chapters/{chapter_id}')
    assert get_response.status_code == 404
```

---

## End-to-End Tests to Implement

### Priority 1: Core User Workflows

#### `tests/e2e/test_chapter_workflow.py`

```python
import pytest
from playwright.sync_api import Page, expect

def test_create_chapter(page: Page):
    """Test creating a new chapter through the UI."""
    page.goto("http://localhost:5000")

    # Click new chapter button
    page.click("#btnNewChapter")

    # Fill in title (using browser prompt)
    page.on("dialog", lambda dialog: dialog.accept("My First Chapter"))

    # Verify chapter appears in sidebar
    expect(page.locator(".chapter-item-title")).to_contain_text("My First Chapter")

def test_edit_chapter_content(page: Page):
    """Test editing chapter content with auto-save."""
    page.goto("http://localhost:5000")

    # Create a chapter
    page.click("#btnNewChapter")
    page.on("dialog", lambda dialog: dialog.accept("Test Chapter"))

    # Type content
    page.fill(".markdown-editor", "This is my memoir story.")

    # Wait for auto-save (2 second debounce + processing)
    page.wait_for_timeout(3000)

    # Refresh page
    page.reload()

    # Verify content persisted
    expect(page.locator(".markdown-editor")).to_have_value("This is my memoir story.")

def test_reorder_chapters(page: Page):
    """Test reordering chapters."""
    page.goto("http://localhost:5000")

    # Create three chapters
    for i in range(1, 4):
        page.click("#btnNewChapter")
        page.on("dialog", lambda dialog: dialog.accept(f"Chapter {i}"))
        page.wait_for_timeout(500)

    # Move chapter 3 up
    chapter_items = page.locator(".chapter-item")
    chapter_items.nth(2).hover()
    chapter_items.nth(2).locator(".btn-move-chapter[data-direction='up']").click()

    # Verify order changed
    titles = page.locator(".chapter-item-title").all_text_contents()
    assert titles[1] == "Chapter 3"
    assert titles[2] == "Chapter 2"

def test_delete_chapter(page: Page):
    """Test deleting a chapter."""
    page.goto("http://localhost:5000")

    # Create a chapter
    page.click("#btnNewChapter")
    page.on("dialog", lambda dialog: dialog.accept("To Delete"))

    # Delete it
    page.locator(".chapter-item").hover()

    # Confirm deletion
    page.on("dialog", lambda dialog: dialog.accept())
    page.click(".btn-delete-chapter")

    # Verify it's gone
    expect(page.locator(".chapter-item")).to_have_count(0)

def test_writing_prompts(page: Page):
    """Test inserting writing prompts."""
    page.goto("http://localhost:5000")

    # Create a chapter
    page.click("#btnNewChapter")
    page.on("dialog", lambda dialog: dialog.accept("Test Chapter"))

    # Open prompts sidebar
    page.click("#btnTogglePrompts")

    # Click a prompt
    page.click(".prompt-question:first-child")

    # Verify prompt was inserted
    content = page.locator(".markdown-editor").input_value()
    assert "**" in content  # Prompt should be bolded
```

---

## Running Tests

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=core --cov=app --cov-report=html

# Run only unit tests
pytest tests/ -k "not e2e"

# Run only E2E tests
pytest tests/e2e/

# Run tests in parallel (faster)
pytest -n auto
```

### Run Specific Test

```bash
# Run single test file
pytest tests/test_markdown_handler.py

# Run single test function
pytest tests/test_markdown_handler.py::test_create_chapter

# Run tests matching pattern
pytest -k "chapter"
```

---

## Test Coverage Goals

Aim for these coverage targets:

- **Backend core modules**: 80%+ coverage
  - `core/markdown_handler.py`: Critical - aim for 95%+
  - `core/timeline.py`: 80%+
  - `core/search.py`: 80%+
  - `core/image_handler.py`: 80%+

- **API endpoints**: 70%+ coverage
  - All happy paths tested
  - Error cases tested

- **Frontend E2E**: Cover all critical user journeys
  - Chapter CRUD operations
  - Auto-save functionality
  - Writing prompts
  - (Future) PDF export

---

## CI/CD Integration (Future)

When ready, add GitHub Actions workflow:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-playwright
          playwright install
      - name: Run tests
        run: pytest --cov=core --cov=app
```

---

## Notes for When Resuming Development

1. **Start with unit tests** - Easier to write, faster to run
2. **Add E2E tests for critical flows** - Chapter workflow is most important
3. **Run tests before committing** - Add to pre-commit hook
4. **Maintain tests as features evolve** - Update tests when changing behavior
5. **Use tests to catch regressions** - Any bug found should get a test

**Testing is especially important because:**
- Mom will rely on this tool - data loss would be catastrophic
- The markdown file format is critical - corruption could lose memoir content
- Auto-save is complex - timing bugs could cause data loss
- The app will evolve - tests prevent breaking existing features

---

## Quick Reference

```bash
# Run all tests (excluding updater and prompts)
py -m pytest tests/ -q --ignore=tests/test_updater.py -k "not test_get_prompts"

# Run with coverage
py -m pytest --cov=core --cov-report=html tests/

# Run specific module tests
py -m pytest tests/test_data_migrator.py -v
```
