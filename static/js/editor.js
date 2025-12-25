/**
 * Editor Module
 * Handles editor functionality and auto-save
 */

class Editor {
    constructor() {
        this.currentChapterId = null;
        this.currentFrontmatter = null;
        this.saveTimeout = null;
        this.saveDelay = 2000; // 2 seconds
        this.onSaveCallback = null; // Callback to execute after successful save

        // Get DOM elements
        this.titleInput = document.getElementById('chapterTitle');
        this.subtitleInput = document.getElementById('chapterSubtitle');
        this.editor = document.getElementById('editor');
        this.saveStatus = document.getElementById('saveStatus');
        this.wordCount = document.getElementById('wordCount');

        // Get formatting toolbar buttons
        this.btnBold = document.getElementById('btnBold');
        this.btnItalic = document.getElementById('btnItalic');
        this.btnH1 = document.getElementById('btnH1');
        this.btnH2 = document.getElementById('btnH2');
        this.btnH3 = document.getElementById('btnH3');

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Auto-save on input
        this.titleInput.addEventListener('input', () => this.handleInput());
        this.subtitleInput.addEventListener('input', () => this.handleInput());
        this.editor.addEventListener('input', () => {
            this.handleInput();
            this.updateWordCount();
        });

        // Formatting toolbar buttons
        this.btnBold.addEventListener('click', () => this.formatBold());
        this.btnItalic.addEventListener('click', () => this.formatItalic());
        this.btnH1.addEventListener('click', () => this.formatHeading(1));
        this.btnH2.addEventListener('click', () => this.formatHeading(2));
        this.btnH3.addEventListener('click', () => this.formatHeading(3));

        // Keyboard shortcuts
        this.editor.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'b' || e.key === 'B') {
                    e.preventDefault();
                    this.formatBold();
                } else if (e.key === 'i' || e.key === 'I') {
                    e.preventDefault();
                    this.formatItalic();
                }
            }
        });

        // Update word count on load
        this.updateWordCount();
    }

    handleInput() {
        // Clear existing timeout
        if (this.saveTimeout) {
            clearTimeout(this.saveTimeout);
        }

        // Update status
        this.setSaveStatus('saving');

        // Set new timeout for auto-save
        this.saveTimeout = setTimeout(() => {
            this.saveCurrentChapter();
        }, this.saveDelay);
    }

    async loadChapter(chapterId) {
        try {
            this.setSaveStatus('loading');

            const chapter = await API.getChapter(chapterId);

            this.currentChapterId = chapterId;
            this.currentFrontmatter = chapter.frontmatter;

            // Populate fields
            this.titleInput.value = chapter.frontmatter.title || '';
            this.subtitleInput.value = chapter.frontmatter.subtitle || '';
            this.editor.value = chapter.content || '';

            // Enable inputs
            this.titleInput.disabled = false;
            this.subtitleInput.disabled = false;
            this.editor.disabled = false;

            // Enable formatting toolbar
            this.btnBold.disabled = false;
            this.btnItalic.disabled = false;
            this.btnH1.disabled = false;
            this.btnH2.disabled = false;
            this.btnH3.disabled = false;

            this.updateWordCount();
            this.setSaveStatus('saved');

            // Focus editor
            this.editor.focus();
        } catch (error) {
            console.error('Error loading chapter:', error);
            this.setSaveStatus('error');
            alert('Failed to load chapter: ' + error.message);
        }
    }

    async saveCurrentChapter() {
        if (!this.currentChapterId) {
            return;
        }

        try {
            // Update frontmatter with current values
            const frontmatter = {
                ...this.currentFrontmatter,
                title: this.titleInput.value,
                subtitle: this.subtitleInput.value
            };

            const content = this.editor.value;

            await API.updateChapter(this.currentChapterId, frontmatter, content);

            this.currentFrontmatter = frontmatter;
            this.setSaveStatus('saved');

            // Notify app that save was successful (e.g., to update word count in sidebar)
            if (this.onSaveCallback) {
                this.onSaveCallback();
            }
        } catch (error) {
            console.error('Error saving chapter:', error);
            this.setSaveStatus('error');
        }
    }

    clearEditor() {
        this.currentChapterId = null;
        this.currentFrontmatter = null;
        this.titleInput.value = '';
        this.subtitleInput.value = '';
        this.editor.value = '';
        this.titleInput.disabled = true;
        this.subtitleInput.disabled = true;
        this.editor.disabled = true;

        // Disable formatting toolbar
        this.btnBold.disabled = true;
        this.btnItalic.disabled = true;
        this.btnH1.disabled = true;
        this.btnH2.disabled = true;
        this.btnH3.disabled = true;

        this.setSaveStatus('ready');
        this.updateWordCount();
    }

    setSaveStatus(status) {
        this.saveStatus.className = 'status-indicator';

        switch (status) {
            case 'saving':
                this.saveStatus.classList.add('saving');
                this.saveStatus.textContent = 'Saving...';
                break;
            case 'saved':
                this.saveStatus.classList.add('saved');
                this.saveStatus.textContent = 'Saved';
                break;
            case 'error':
                this.saveStatus.textContent = 'Error saving';
                break;
            case 'loading':
                this.saveStatus.textContent = 'Loading...';
                break;
            default:
                this.saveStatus.textContent = 'Ready';
        }
    }

    updateWordCount() {
        const text = this.editor.value.trim();
        const words = text ? text.split(/\s+/).length : 0;
        this.wordCount.textContent = `${words} word${words !== 1 ? 's' : ''}`;
    }

    getContent() {
        return this.editor.value;
    }

    insertText(text) {
        const start = this.editor.selectionStart;
        const end = this.editor.selectionEnd;
        const currentValue = this.editor.value;

        this.editor.value = currentValue.substring(0, start) + text + currentValue.substring(end);

        // Move cursor after inserted text
        const newPosition = start + text.length;
        this.editor.setSelectionRange(newPosition, newPosition);
        this.editor.focus();

        // Trigger auto-save
        this.handleInput();
    }

    formatBold() {
        this.wrapSelection('**', '**', 'bold text');
    }

    formatItalic() {
        this.wrapSelection('*', '*', 'italic text');
    }

    formatHeading(level) {
        const prefix = '#'.repeat(level) + ' ';
        this.insertAtLineStart(prefix, 'Heading ' + level);
    }

    wrapSelection(before, after, placeholder) {
        const start = this.editor.selectionStart;
        const end = this.editor.selectionEnd;
        const currentValue = this.editor.value;
        const selectedText = currentValue.substring(start, end);

        let newText;
        let newCursorPos;

        if (selectedText) {
            // Wrap selected text
            newText = before + selectedText + after;
            newCursorPos = start + before.length + selectedText.length + after.length;
        } else {
            // Insert placeholder with markers
            newText = before + placeholder + after;
            newCursorPos = start + before.length + placeholder.length;
        }

        this.editor.value = currentValue.substring(0, start) + newText + currentValue.substring(end);

        // Set cursor position
        this.editor.setSelectionRange(newCursorPos, newCursorPos);
        this.editor.focus();

        // Trigger auto-save
        this.handleInput();
    }

    insertAtLineStart(prefix, placeholder) {
        const start = this.editor.selectionStart;
        const currentValue = this.editor.value;

        // Find the start of the current line
        let lineStart = start;
        while (lineStart > 0 && currentValue[lineStart - 1] !== '\n') {
            lineStart--;
        }

        // Get the current line
        let lineEnd = start;
        while (lineEnd < currentValue.length && currentValue[lineEnd] !== '\n') {
            lineEnd++;
        }

        const currentLine = currentValue.substring(lineStart, lineEnd);

        // Check if line already has a heading marker
        const headingMatch = currentLine.match(/^(#{1,6})\s/);

        let newText;
        let newCursorPos;

        if (headingMatch) {
            // Replace existing heading marker
            newText = prefix + currentLine.substring(headingMatch[0].length);
            newCursorPos = lineStart + newText.length;
        } else if (currentLine.trim()) {
            // Add heading marker to existing text
            newText = prefix + currentLine;
            newCursorPos = lineStart + newText.length;
        } else {
            // Empty line - insert placeholder
            newText = prefix + placeholder;
            newCursorPos = lineStart + prefix.length + placeholder.length;
        }

        this.editor.value = currentValue.substring(0, lineStart) + newText + currentValue.substring(lineEnd);

        // Set cursor position
        this.editor.setSelectionRange(newCursorPos, newCursorPos);
        this.editor.focus();

        // Trigger auto-save
        this.handleInput();
    }
}
