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

        // Get DOM elements
        this.titleInput = document.getElementById('chapterTitle');
        this.subtitleInput = document.getElementById('chapterSubtitle');
        this.editor = document.getElementById('editor');
        this.saveStatus = document.getElementById('saveStatus');
        this.wordCount = document.getElementById('wordCount');

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

        // Keyboard shortcuts for formatting
        this.editor.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));

        // Update word count on load
        this.updateWordCount();
    }

    handleKeyboardShortcuts(e) {
        // Check for Ctrl/Cmd key combinations
        const isMod = e.ctrlKey || e.metaKey;

        if (!isMod) return;

        switch(e.key.toLowerCase()) {
            case 'b':
                e.preventDefault();
                this.formatSelection('**', '**', 'bold text');
                break;
            case 'i':
                e.preventDefault();
                this.formatSelection('*', '*', 'italic text');
                break;
            case 'k':
                e.preventDefault();
                this.formatSelection('[', '](https://)', 'link text');
                break;
            case 'h':
                if (e.shiftKey) {
                    e.preventDefault();
                    this.formatSelection('## ', '', 'Heading');
                }
                break;
        }
    }

    formatSelection(prefix, suffix, placeholder = '') {
        const start = this.editor.selectionStart;
        const end = this.editor.selectionEnd;
        const selectedText = this.editor.value.substring(start, end);
        const text = selectedText || placeholder;

        // Build the formatted text
        const formattedText = prefix + text + suffix;

        // Replace the selection
        this.editor.value = this.editor.value.substring(0, start) +
                           formattedText +
                           this.editor.value.substring(end);

        // Set cursor position
        if (selectedText) {
            // If there was a selection, select the formatted text
            this.editor.setSelectionRange(start, start + formattedText.length);
        } else {
            // If no selection, position cursor inside the formatting
            const cursorPos = start + prefix.length + text.length;
            this.editor.setSelectionRange(cursorPos, cursorPos - suffix.length);
        }

        this.editor.focus();
        this.handleInput();
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
}
