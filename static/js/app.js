/**
 * Main Application Module
 * Coordinates all application functionality
 */

class MemDocApp {
    constructor() {
        this.editor = new Editor();
        this.chapters = [];
        this.prompts = null;

        // Get DOM elements
        this.chapterList = document.getElementById('chapterList');
        this.btnNewChapter = document.getElementById('btnNewChapter');
        this.promptsSidebar = document.getElementById('promptsSidebar');
        this.btnTogglePrompts = document.getElementById('btnTogglePrompts');
        this.btnClosePrompts = document.getElementById('btnClosePrompts');
        this.promptsContent = document.getElementById('promptsContent');

        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadChapters();
        await this.loadPrompts();
    }

    setupEventListeners() {
        // New chapter button
        this.btnNewChapter.addEventListener('click', () => this.handleNewChapter());

        // Toggle prompts sidebar
        this.btnTogglePrompts.addEventListener('click', () => this.togglePromptsSidebar());
        this.btnClosePrompts.addEventListener('click', () => this.togglePromptsSidebar());
    }

    async loadChapters(autoSelect = true) {
        try {
            this.chapters = await API.getChapters();
            this.renderChapterList();

            // Load first chapter if exists (only if autoSelect is true)
            if (autoSelect && this.chapters.length > 0) {
                this.selectChapter(this.chapters[0].id);
            }
        } catch (error) {
            console.error('Error loading chapters:', error);
            alert('Failed to load chapters: ' + error.message);
        }
    }

    renderChapterList() {
        if (this.chapters.length === 0) {
            this.chapterList.innerHTML = '<p class="empty-state">No chapters yet. Create your first chapter!</p>';
            return;
        }

        this.chapterList.innerHTML = this.chapters.map(chapter => `
            <div class="chapter-item" data-id="${chapter.id}">
                <div class="chapter-item-content">
                    <div class="chapter-item-title">${this.escapeHtml(chapter.file.replace(/^ch\d+-/, '').replace(/\.md$/, ''))}</div>
                </div>
                <div class="chapter-item-actions">
                    <button class="btn-edit-chapter" data-id="${chapter.id}" title="Edit chapter">
                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor">
                            <path d="M10 1l3 3-7 7H3v-3z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                    <button class="btn-delete-chapter" data-id="${chapter.id}" title="Delete chapter">
                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor">
                            <path d="M1 3h12M5 1h4M5 6v4M9 6v4M3 3l1 9h6l1-9" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            </div>
        `).join('');

        // Add click handlers for chapter selection
        this.chapterList.querySelectorAll('.chapter-item-content').forEach(item => {
            item.addEventListener('click', () => {
                const chapterId = item.parentElement.dataset.id;
                this.selectChapter(chapterId);
            });
        });

        // Add click handlers for edit buttons
        this.chapterList.querySelectorAll('.btn-edit-chapter').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const chapterId = btn.dataset.id;
                this.handleEditChapter(chapterId);
            });
        });

        // Add click handlers for delete buttons
        this.chapterList.querySelectorAll('.btn-delete-chapter').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const chapterId = btn.dataset.id;
                this.handleDeleteChapter(chapterId);
            });
        });
    }

    async selectChapter(chapterId) {
        // Update active state in UI
        this.chapterList.querySelectorAll('.chapter-item').forEach(item => {
            if (item.dataset.id === chapterId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Load chapter in editor
        await this.editor.loadChapter(chapterId);
    }

    async handleNewChapter() {
        const title = prompt('Enter chapter title:');
        if (!title) return;

        const subtitle = prompt('Enter chapter subtitle (optional):') || '';

        try {
            const result = await API.createChapter(title, subtitle);
            // Reload chapters without auto-selecting
            await this.loadChapters(false);
            // Then select the newly created chapter
            this.selectChapter(result.id);
        } catch (error) {
            console.error('Error creating chapter:', error);
            alert('Failed to create chapter: ' + error.message);
        }
    }

    async handleEditChapter(chapterId) {
        try {
            // Get current chapter data
            const chapter = await API.getChapter(chapterId);
            const currentTitle = chapter.frontmatter.title || '';
            const currentSubtitle = chapter.frontmatter.subtitle || '';

            // Prompt for new values
            const newTitle = prompt('Enter new chapter title:', currentTitle);
            if (!newTitle) return;  // User cancelled

            const newSubtitle = prompt('Enter new subtitle (optional):', currentSubtitle) || '';

            // Update chapter metadata
            await API.updateChapterMetadata(chapterId, newTitle, newSubtitle);

            // If this is the currently loaded chapter, update the editor fields
            if (this.editor.currentChapterId === chapterId) {
                this.editor.titleInput.value = newTitle;
                this.editor.subtitleInput.value = newSubtitle;
            }

            // Reload chapter list to show updated title
            const currentChapter = this.editor.currentChapterId;
            await this.loadChapters(false);
            if (currentChapter) {
                this.selectChapter(currentChapter);
            }
        } catch (error) {
            console.error('Error editing chapter:', error);
            alert('Failed to edit chapter: ' + error.message);
        }
    }

    async handleDeleteChapter(chapterId) {
        // Get chapter info for confirmation
        const chapter = this.chapters.find(ch => ch.id === chapterId);
        const chapterName = chapter ? chapter.file.replace(/^ch\d+-/, '').replace(/\.md$/, '') : 'this chapter';

        if (!confirm(`Are you sure you want to delete "${chapterName}"? This cannot be undone.`)) {
            return;
        }

        try {
            await API.deleteChapter(chapterId);

            // If we deleted the currently loaded chapter, clear the editor
            if (this.editor.currentChapterId === chapterId) {
                this.editor.clearEditor();
            }

            // Reload chapters
            await this.loadChapters();
        } catch (error) {
            console.error('Error deleting chapter:', error);
            alert('Failed to delete chapter: ' + error.message);
        }
    }

    async loadPrompts() {
        try {
            this.prompts = await API.getPrompts();
            this.renderPrompts();
        } catch (error) {
            console.error('Error loading prompts:', error);
            this.promptsContent.innerHTML = '<p class="loading">Failed to load prompts</p>';
        }
    }

    renderPrompts() {
        if (!this.prompts || !this.prompts.prompts) {
            return;
        }

        this.promptsContent.innerHTML = this.prompts.prompts.map(category => `
            <div class="prompt-category">
                <div class="prompt-category-title">${this.escapeHtml(category.category)}</div>
                ${category.questions.map(question => `
                    <div class="prompt-question" data-question="${this.escapeHtml(question)}">
                        ${this.escapeHtml(question)}
                    </div>
                `).join('')}
            </div>
        `).join('');

        // Add click handlers to prompts
        this.promptsContent.querySelectorAll('.prompt-question').forEach(prompt => {
            prompt.addEventListener('click', () => {
                const question = prompt.dataset.question;
                this.insertPrompt(question);
            });
        });
    }

    insertPrompt(question) {
        const text = `\n\n**${question}**\n\n`;
        this.editor.insertText(text);
        // Close prompts sidebar after inserting
        this.togglePromptsSidebar(false);
    }

    togglePromptsSidebar(show) {
        if (show === undefined) {
            this.promptsSidebar.classList.toggle('visible');
        } else if (show) {
            this.promptsSidebar.classList.add('visible');
        } else {
            this.promptsSidebar.classList.remove('visible');
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MemDocApp();
});
