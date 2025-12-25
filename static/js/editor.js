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
