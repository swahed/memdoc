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

    async loadChapters() {
        try {
            this.chapters = await API.getChapters();
            this.renderChapterList();

            // Load first chapter if exists
            if (this.chapters.length > 0) {
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
                <div class="chapter-item-title">${this.escapeHtml(chapter.file.replace(/^ch\d+-/, '').replace(/\.md$/, ''))}</div>
            </div>
        `).join('');

        // Add click handlers
        this.chapterList.querySelectorAll('.chapter-item').forEach(item => {
            item.addEventListener('click', () => {
                const chapterId = item.dataset.id;
                this.selectChapter(chapterId);
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
            await this.loadChapters();
            this.selectChapter(result.id);
        } catch (error) {
            console.error('Error creating chapter:', error);
            alert('Failed to create chapter: ' + error.message);
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
