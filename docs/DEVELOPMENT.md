# MemDoc Development Guidelines

## Project Context

This is a **personal family project** for 1-2 users (primarily for mom to write her memoirs). The user is a retired computer specialist who may contribute code herself.

**Key principles:**
- **Simplicity over features**: Resist feature creep
- **Readability over cleverness**: Code should be easy to understand
- **Working over perfect**: Ship functional features, iterate later
- **Privacy-first**: No data leaves the local machine

---

## Development Environment Setup

### Prerequisites
- Python 3.10 or higher
- Git
- A code editor (VS Code recommended for Python)
- OneDrive (for automatic file backup)

### Initial Setup

```bash
# Clone the repository
git clone <repository-url> memdoc
cd memdoc

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running in Development Mode

```bash
# Browser mode (easier for development)
python app.py --browser

# Desktop mode (production-like)
python app.py
```

The app will open at `http://localhost:5000` in browser mode.

---

## Code Style & Conventions

### Python Code Style
- **PEP 8 compliant**: Use standard Python style
- **Clear naming**: Prefer `calculate_timeline()` over `calc_tl()`
- **Docstrings**: Add docstrings to all functions
- **Type hints**: Use type hints for function parameters and returns

Example:
```python
def extract_events(content: str) -> list[dict]:
    """
    Extract event data from markdown frontmatter.

    Args:
        content: Markdown file content with YAML frontmatter

    Returns:
        List of event dictionaries with 'date' and 'title' keys
    """
    # Implementation here
    pass
```

### JavaScript Code Style
- **ES6+ syntax**: Use modern JavaScript
- **Clear naming**: Same as Python
- **Comments**: Explain "why", not "what"
- **No frameworks**: Keep it vanilla JS for simplicity

Example:
```javascript
/**
 * Auto-save content after user stops typing
 * Debounced to avoid excessive saves
 */
function autoSave() {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
        saveContent();
    }, 2000);
}
```

### File Organization
- **One concern per file**: Keep modules focused
- **Clear file names**: `image_handler.py`, not `utils.py`
- **Group related code**: Keep API routes together, core logic separate

---

## Git Workflow

### Branching Strategy
Since this is a personal project with 1-2 contributors:
- **main**: Always working, deployable code
- **feature branches**: Optional, for experimental features

### Commit Messages
Keep commits clear and descriptive:

```bash
# Good commit messages
git commit -m "Add event tagging to chapter frontmatter"
git commit -m "Fix image resolution warning threshold"
git commit -m "Implement full-text search across chapters"

# Avoid vague messages
git commit -m "Fix bug"
git commit -m "Update stuff"
git commit -m "WIP"
```

### Updating (for mom)
```bash
# Pull latest changes
git pull origin main

# If there are local changes, stash first
git stash
git pull origin main
git stash pop

# Update dependencies
pip install -r requirements.txt
```

---

## Adding New Features

### Feature Development Checklist

1. **Document first**: Update ROADMAP.md with the feature plan
2. **Design data model**: How will data be stored?
3. **Backend first**: Implement core logic in Python
4. **Add API endpoint**: Create Flask route
5. **Frontend**: Build UI and connect to API
6. **Test manually**: Verify feature works end-to-end
7. **Update docs**: Add to README if user-facing

### Example: Adding a New Feature

Let's say we want to add "word count per chapter":

1. **Update ROADMAP.md**: Add to Phase 2 features
2. **Backend** (`core/word_count.py`):
   ```python
   def count_words(chapter_text: str) -> int:
       """Count words in a chapter."""
       return len(chapter_text.split())
   ```
3. **API** (`app.py`):
   ```python
   @app.route('/api/chapters/<chapter_id>/wordcount')
   def get_word_count(chapter_id):
       content = get_chapter_content(chapter_id)
       count = count_words(content)
       return jsonify({'count': count})
   ```
4. **Frontend** (`static/js/app.js`):
   ```javascript
   async function displayWordCount(chapterId) {
       const response = await fetch(`/api/chapters/${chapterId}/wordcount`);
       const data = await response.json();
       document.getElementById('word-count').textContent = data.count;
   }
   ```
5. **UI** (`templates/index.html`): Add display element
6. **Test**: Verify it works
7. **Commit**: `git commit -m "Add word count per chapter"`

---

## Testing Strategy

### Manual Testing
Since this is a small personal project, manual testing is sufficient:

1. **Smoke test**: Can you start the app?
2. **Feature test**: Does the feature work as expected?
3. **Edge cases**: What happens with empty input? Very long text?
4. **Cross-browser** (optional): Test in Chrome, Firefox, Safari

### Testing Checklist (before committing)
- [ ] App starts without errors
- [ ] New feature works as expected
- [ ] Existing features still work
- [ ] No console errors in browser
- [ ] Files save correctly
- [ ] PDF export still works (if applicable)

### Future: Automated Tests
If the project grows, consider adding:
- **pytest**: For Python backend tests
- **Simple JS tests**: For critical frontend logic

---

## Common Development Tasks

### Adding a New API Endpoint

```python
@app.route('/api/your-endpoint', methods=['GET', 'POST'])
def your_endpoint():
    """Brief description of what this endpoint does."""
    try:
        # Your logic here
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

### Adding a New Writing Prompt

Edit `prompts/writing_prompts.json`:
```json
{
    "prompts": [
        {
            "category": "Childhood",
            "question": "What is your earliest memory?"
        },
        {
            "category": "Relationships",
            "question": "Describe meeting someone important in your life."
        }
    ]
}
```

### Adding a New CSS Style

Follow iA Writer aesthetic:
- **Typography-first**: Focus on readable fonts
- **Minimal chrome**: Reduce UI clutter
- **High contrast**: Easy to read
- **Generous whitespace**: Let content breathe

```css
/* Add to static/css/style.css */
.chapter-title {
    font-family: 'Georgia', serif;
    font-size: 2em;
    font-weight: normal;
    margin: 2em 0 1em 0;
    color: #1a1a1a;
}
```

---

## Debugging Tips

### Python Backend Issues

```bash
# Run with debug mode
python app.py --debug

# Check Flask logs in terminal
# Errors will show detailed stack traces
```

### Frontend Issues

- **Open browser console**: F12 in most browsers
- **Check Network tab**: See API requests/responses
- **Console.log liberally**: Debug JavaScript

```javascript
console.log('Chapter data:', chapterData);
```

### File Save Issues

- **Check permissions**: Can Python write to `data/` folder?
- **Check OneDrive sync**: Is the folder syncing properly?
- **Check disk space**: Enough room for images?

---

## Performance Best Practices

### Backend
- **Lazy loading**: Don't load all chapters if user is editing one
- **Caching**: Cache parsed markdown if content hasn't changed
- **Async operations**: Use background tasks for PDF generation

### Frontend
- **Debounce auto-save**: Don't save on every keystroke (wait 2-3s)
- **Throttle search**: Don't search on every character typed
- **Lazy load images**: Don't load all images at once in preview

---

## Working with Claude Code

When asking Claude Code for help on this project:

### Provide Context
```
"I'm working on MemDoc, a memoir writing tool.
See AI_CONTEXT.md for project details.
I need help with [specific task]."
```

### Be Specific
```
"Add a feature to export chapter summaries to the timeline page.
Each timeline entry should show the first 100 words of the chapter."
```

### Reference Existing Patterns
```
"Following the pattern in image_handler.py,
add a video_handler.py module for video uploads."
```

### Ask for Simple Solutions
```
"Keep it simple - we only have 1-2 users.
No need for advanced optimization or scaling."
```

---

## Deployment Notes

### For Mom's Computer

1. **Install Python**: Download from python.org
2. **Clone repo**: Use GitHub Desktop or command line
3. **Setup OneDrive sync**: Point `data/` folder to OneDrive
4. **Create desktop shortcut**:
   ```bash
   # Windows: Create .bat file
   @echo off
   cd C:\path\to\memdoc
   python app.py
   ```
5. **First run**: Run setup to create data directory structure

### Desktop App Packaging (Future)

When using Eel for desktop mode:
```bash
# Package with PyInstaller
pip install pyinstaller
pyinstaller --onefile --windowed app.py
```

---

## Troubleshooting

### Common Issues

**App won't start**
- Check Python version: `python --version` (should be 3.10+)
- Reinstall dependencies: `pip install -r requirements.txt`
- Check for port conflicts: Another app using port 5000?

**Images not appearing**
- Check file paths in markdown
- Verify images are in `data/images/`
- Check file permissions

**PDF export fails**
- Check WeasyPrint installation
- Verify all images exist
- Check for invalid HTML in content

**Can't save files**
- Check folder permissions
- Verify `data/` folder exists
- Check disk space

---

## Code Review Checklist

Before considering a feature "done":

- [ ] Code is readable and well-commented
- [ ] Follows existing code style
- [ ] No hardcoded paths or values (use config)
- [ ] Error handling for common failures
- [ ] Tested manually with real content
- [ ] No console errors
- [ ] Doesn't break existing features
- [ ] Documentation updated if needed

---

## Contact & Support

This is a family project maintained by [your name]. For issues or questions:
- Check the documentation first
- Read the code - it's designed to be simple
- Ask Claude Code for help (see AI_CONTEXT.md)
- If all else fails, ask the maintainer

Remember: **The goal is to help mom write her memoirs, not to build the perfect software.** Ship working features, keep it simple, iterate based on real usage.
