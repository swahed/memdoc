# AI Assistant Context for MemDoc

**Purpose of this document:** Provide essential context to AI assistants (like Claude Code) working on this project in future sessions.

---

## Project Overview

**MemDoc** is a personal memoir writing application built for a specific user (mom) to document her life story. This is NOT a commercial product or multi-user SaaS application.

### Key Facts
- **Users**: 1-2 people (primarily mom)
- **Scale**: Single memoir, personal use
- **Context**: Family project, mom is a retired computer specialist
- **Privacy**: Critical - memoir content is personal and private
- **Simplicity**: More important than features or scalability

---

## Design Philosophy

### Core Principles

1. **Simplicity Over Everything**
   - Avoid over-engineering
   - No frameworks unless absolutely necessary
   - Keep dependencies minimal
   - Code should be readable by someone learning Python

2. **Privacy First**
   - No external API calls with personal content
   - No telemetry or analytics
   - All data stays local (OneDrive-synced for backup)
   - Fixed writing prompts, no AI API (for now)

3. **User-Centric**
   - Built for one specific user (mom)
   - Features based on her actual needs, not hypothetical use cases
   - UX inspired by iA Writer (clean, distraction-free)
   - Easy enough for non-technical users, but mom can code if needed

4. **Git as Distribution**
   - Git clone for installation
   - Git pull for updates
   - No complex deployment or packaging (initially)
   - Mom might contribute code herself

---

## Important Constraints

### What NOT to Do

**Don't add features proactively**
- Only implement what's explicitly requested or clearly necessary
- Resist the urge to add "nice-to-have" features
- Check ROADMAP.md for planned features before adding anything

**Don't optimize prematurely**
- No caching unless there's a proven performance problem
- No complex architecture for hypothetical scaling
- Simple solutions are preferred

**Don't use heavy frameworks**
- No React, Vue, Angular
- No Django, FastAPI (Flask is sufficient)
- No complex CSS frameworks (vanilla CSS is fine)

**Don't compromise privacy**
- No external API calls with memoir content
- No cloud services beyond OneDrive sync (user-controlled)
- No telemetry or usage tracking

**Don't make it complex**
- Mom should be able to understand the code
- Future maintainer might be a family member learning to code
- Clarity > cleverness

---

## Technical Context

### Why These Choices?

**Python**: User has .NET/JS experience but wanted to learn Python. Keep it beginner-friendly.

**Flask + Eel**: Lightweight, allows browser development then desktop deployment without Electron's overhead.

**Markdown storage**: Human-readable, git-friendly, not locked into proprietary format. Mom can edit files directly if needed.

**No database**: Overkill for 1-2 users. Files are simpler, more transparent, easier to backup.

**Fixed prompts (no AI API)**: Privacy concern - don't send personal memoir content to external APIs. Can add AI features later if requested.

**iA Writer aesthetic**: Clean, typography-focused, distraction-free writing environment. Mom likes this style.

---

## User Context

### About the User (Mom)
- Retired computer specialist - technically capable
- Writing her life story - content is personal and meaningful
- May contribute code herself - keep it readable
- Values simplicity and elegance over feature richness
- Uses Windows laptop, OneDrive for backup

### About the Developer (User's child)
- Experience: .NET and JavaScript, learning Python
- Will maintain and extend the project
- May ask AI assistants for help (that's you!)
- Prefers simple, maintainable solutions

---

## Common AI Assistant Tasks

### When Helping with This Project

**Always:**
- Read the relevant docs first (ROADMAP.md, ARCHITECTURE.md, DEVELOPMENT.md)
- Keep solutions simple and readable
- Consider privacy implications
- Follow existing code patterns
- Explain your approach (educational value for Python learner)

**Never:**
- Add features not in ROADMAP.md without asking
- Use complex libraries when simple code works
- Make API calls that send personal data externally
- Sacrifice readability for minor performance gains
- Assume multi-user or scaling requirements

### Typical Requests You'll Get

1. **"Add feature X"**
   - Check if it's in ROADMAP.md
   - Ask for clarification if ambiguous
   - Propose simple implementation
   - Code it following existing patterns

2. **"Fix bug in Y"**
   - Understand the bug first
   - Fix it simply
   - Don't refactor unrelated code "while you're at it"

3. **"How does Z work?"**
   - Explain clearly - user is learning Python
   - Reference specific files and line numbers
   - Educational tone is appreciated

4. **"Improve the UI"**
   - Keep iA Writer aesthetic in mind
   - Minimal, clean, typography-focused
   - Don't add unnecessary UI chrome

---

## Code Patterns to Follow

### Python

```python
# Good: Clear, simple, documented
def extract_events_from_chapter(chapter_content: str) -> list[dict]:
    """
    Extract event data from chapter frontmatter.

    Args:
        chapter_content: Markdown with YAML frontmatter

    Returns:
        List of events with 'date' and 'title' keys
    """
    # Parse YAML frontmatter
    events = parse_frontmatter(chapter_content).get('events', [])
    return events

# Avoid: Clever but unclear
def ext_ev(c): return yaml.safe_load(c.split('---')[1]).get('events', [])
```

### JavaScript

```javascript
// Good: Clear intent, modern syntax
async function saveChapter(chapterId, content) {
    try {
        const response = await fetch(`/api/chapters/${chapterId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({content})
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to save chapter:', error);
        showError('Could not save chapter. Please try again.');
    }
}

// Avoid: Unclear error handling, no user feedback
function save(id,c){fetch(`/api/chapters/${id}`,{method:'POST',body:JSON.stringify({c})}).then(r=>r.json())}
```

---

## Project State Awareness

### How to Check Project Status

1. **Read ROADMAP.md**: See what phase we're in, what's next
2. **Check git log**: See recent changes
3. **Look at file structure**: What exists vs. what's planned
4. **Read existing code**: Understand patterns before adding more

### Typical Development State

**Early stage (Phase 1-2):**
- Basic features being built
- Focus on core writing experience
- Many features from ROADMAP.md not yet implemented

**Later stage (Phase 3-5):**
- Core features done
- Adding polish and export capabilities
- Focus on UX refinement

**Maintenance:**
- All features complete
- Bug fixes and small improvements
- User-requested enhancements

---

## Privacy Considerations

### Critical Privacy Rules

1. **No external API calls with content**
   - Don't send memoir text to AI APIs
   - Don't use external services for processing
   - Fixed prompts only (stored locally)

2. **Local-first architecture**
   - All data in `data/` folder
   - OneDrive sync is user-controlled
   - No cloud services without explicit user setup

3. **Transparent data handling**
   - User can see all their data as files
   - No hidden databases or caches
   - Clear where everything is stored

### When to Ask About Privacy

If a feature would:
- Send data to external API
- Store data in a new location
- Add telemetry or logging
- Access files outside `data/` folder

**Stop and ask the user first.**

---

## Debugging Context

### Common Issues

**File paths:**
- Windows uses backslashes: `C:\Users\Shadow\code\memdoc`
- Use `os.path.join()` or `pathlib.Path` for cross-platform paths
- `data/` folder might be on OneDrive with sync delays

**OneDrive sync:**
- Files might show as "syncing" placeholder
- Need to handle file access gracefully
- Don't assume instant write/read

**Port conflicts:**
- Port 5000 (Flask default) might be in use
- Make port configurable

---

## Success Metrics

### How to Know You're Helping Well

**Good signs:**
- User can understand your code
- Feature works on first try (or second)
- Code fits naturally with existing patterns
- No new dependencies added unnecessarily
- Mom can use the feature easily

**Warning signs:**
- User asks "why did you do it this way?"
- Code is much more complex than existing code
- New dependencies for simple tasks
- Over-abstracted or over-architected solutions

---

## Future Direction

### Possible Evolution

1. **AI Writing Assistant** (if requested)
   - Use API with explicit user consent
   - Privacy-preserving prompts
   - Optional, disabled by default

2. **Multiple Memoirs** (if requested)
   - Project selection at startup
   - Separate data folders
   - Still local-first

3. **Family Collaboration** (maybe)
   - Comments or suggestions from family
   - Still privacy-focused
   - Git-based workflow

4. **Publishing Features** (maybe)
   - Professional printing service export
   - EPUB for e-readers
   - Website generation for family

**Key point:** Don't build these until requested. YAGNI principle.

---

## Questions to Ask

### When Unclear About a Request

**Feature requests:**
- "Should this be added to ROADMAP.md first?"
- "How should this fit with existing features?"
- "Any privacy concerns with this approach?"

**Implementation choices:**
- "Simple solution X vs. robust solution Y - which fits the project better?"
- "Should this be configurable or fixed?"
- "Where should this code live in the existing structure?"

**UX decisions:**
- "Should this be visible by default or hidden in settings?"
- "How should we handle errors - show message or fail silently?"
- "Does this match the iA Writer minimal aesthetic?"

---

## Remember

You're helping build a **meaningful personal project** - a tool for someone to document their life story for their family. This is about:

- **Helping mom** preserve her memories
- **Teaching Python** to the developer
- **Creating something useful** that will be used for years
- **Keeping it simple** so it can be maintained long-term

Not about:
- Impressive architecture
- Cutting-edge technology
- Scalability to thousands of users
- Showcasing technical skills

**Simple, functional, and maintainable beats clever and complex every time.**

---

## Quick Reference

**Key documents:**
- `README.md` - User-facing documentation (root)
- `docs/ROADMAP.md` - Feature backlog and phases
- `docs/ARCHITECTURE.md` - Technical design
- `docs/DEVELOPMENT.md` - Development guidelines
- `docs/AI_CONTEXT.md` - This file

**Key principles:**
- Simple > Complex
- Privacy > Features
- Working > Perfect
- Readable > Clever

**Key question before any change:**
*"Does this help mom write her memoirs better?"*

If yes → do it simply.
If no → don't do it.
