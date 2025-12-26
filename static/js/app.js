/**
 * Main Application Module
 * Coordinates all application functionality
 */

class MemDocApp {
    constructor() {
        this.editor = new Editor();
        this.chapters = [];
        this.prompts = null;
        this.coverData = null;
        this.coverImageFile = null;

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
        this.setupEditorCallbacks();
        this.setupPreviewExport();
        this.setupCoverPage();
        await this.loadChapters();
        await this.loadPrompts();
    }

    setupEditorCallbacks() {
        // Set callback to refresh chapter list after save (to update word counts)
        this.editor.onSaveCallback = async () => {
            const currentChapter = this.editor.currentChapterId;
            if (currentChapter) {
                // Reload chapters without auto-selecting to preserve current chapter
                await this.loadChapters(false);

                // Restore active state for current chapter
                this.chapterList.querySelectorAll('.chapter-item').forEach(item => {
                    if (item.dataset.id === currentChapter) {
                        item.classList.add('active');
                    } else {
                        item.classList.remove('active');
                    }
                });
            }
        };
    }

    setupEventListeners() {
        // New chapter button
        this.btnNewChapter.addEventListener('click', () => this.handleNewChapter());

        // Cover page button
        document.getElementById('btnCoverPage').addEventListener('click', () => this.openCoverPageModal());

        // Settings button
        document.getElementById('btnSettings').addEventListener('click', () => this.openSettingsModal());

        // Full memoir preview button
        document.getElementById('btnFullPreview').addEventListener('click', () => this.showMemoirPreview());

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
            alert(i18n.t('failedToLoadChapters') + ': ' + error.message);
        }
    }

    renderChapterList() {
        if (this.chapters.length === 0) {
            this.chapterList.innerHTML = `<p class="empty-state">${i18n.t('noChaptersYet')}</p>`;
            return;
        }

        this.chapterList.innerHTML = this.chapters.map((chapter, index) => `
            <div class="chapter-item" data-id="${chapter.id}">
                <div class="chapter-item-buttons">
                    <div class="chapter-item-move-buttons">
                        ${index > 0 ? `
                            <button class="btn-move-chapter" data-id="${chapter.id}" data-direction="up" title="${i18n.t('moveUp')}">
                                <svg width="12" height="12" viewBox="0 0 14 14" fill="none" stroke="currentColor">
                                    <path d="M7 11V3M4 6l3-3 3 3" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>
                            </button>
                        ` : '<span style="width: 20px; display: inline-block;"></span>'}
                        ${index < this.chapters.length - 1 ? `
                            <button class="btn-move-chapter" data-id="${chapter.id}" data-direction="down" title="${i18n.t('moveDown')}">
                                <svg width="12" height="12" viewBox="0 0 14 14" fill="none" stroke="currentColor">
                                    <path d="M7 3v8M4 8l3 3 3-3" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>
                            </button>
                        ` : '<span style="width: 20px; display: inline-block;"></span>'}
                    </div>
                    <div class="chapter-item-edit-buttons">
                        <button class="btn-edit-chapter" data-id="${chapter.id}" title="${i18n.t('editChapter')}">
                            <svg width="12" height="12" viewBox="0 0 14 14" fill="none" stroke="currentColor">
                                <path d="M10 1l3 3-7 7H3v-3z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                        <button class="btn-delete-chapter" data-id="${chapter.id}" title="${i18n.t('deleteChapter')}">
                            <svg width="12" height="12" viewBox="0 0 14 14" fill="none" stroke="currentColor">
                                <path d="M1 3h12M5 1h4M5 6v4M9 6v4M3 3l1 9h6l1-9" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="chapter-item-content">
                    <div class="chapter-item-title" title="${this.escapeHtml(chapter.title || i18n.t('untitledChapter'))}">${this.escapeHtml(chapter.title || i18n.t('untitledChapter'))}</div>
                    <div class="chapter-item-footer">
                        ${chapter.subtitle ? `
                            <div class="chapter-item-subtitle" title="${this.escapeHtml(chapter.subtitle)}">${this.escapeHtml(chapter.subtitle)}</div>
                        ` : '<div></div>'}
                        <div class="chapter-item-wordcount">${chapter.wordCount || 0}</div>
                    </div>
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

        // Add click handlers for move buttons
        this.chapterList.querySelectorAll('.btn-move-chapter').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const chapterId = btn.dataset.id;
                const direction = btn.dataset.direction;
                this.handleReorderChapter(chapterId, direction);
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
        const title = prompt(i18n.t('enterChapterTitle'));
        if (!title) return;

        const subtitle = prompt(i18n.t('enterChapterSubtitle')) || '';

        try {
            const result = await API.createChapter(title, subtitle);
            // Reload chapters without auto-selecting
            await this.loadChapters(false);
            // Then select the newly created chapter
            this.selectChapter(result.id);
        } catch (error) {
            console.error('Error creating chapter:', error);
            alert(i18n.t('failedToCreateChapter') + ': ' + error.message);
        }
    }

    async handleEditChapter(chapterId) {
        try {
            // Get current chapter data
            const chapter = await API.getChapter(chapterId);
            const currentTitle = chapter.frontmatter.title || '';
            const currentSubtitle = chapter.frontmatter.subtitle || '';

            // Prompt for new values
            const newTitle = prompt(i18n.t('enterNewChapterTitle'), currentTitle);
            if (!newTitle) return;  // User cancelled

            const newSubtitle = prompt(i18n.t('enterNewSubtitle'), currentSubtitle) || '';

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
            alert(i18n.t('failedToEditChapter') + ': ' + error.message);
        }
    }

    async handleReorderChapter(chapterId, direction) {
        try {
            await API.reorderChapter(chapterId, direction);

            // Reload chapters list
            const currentChapter = this.editor.currentChapterId;
            await this.loadChapters(false);
            if (currentChapter) {
                this.selectChapter(currentChapter);
            }
        } catch (error) {
            console.error('Error reordering chapter:', error);
            alert(i18n.t('failedToReorderChapter') + ': ' + error.message);
        }
    }

    async handleDeleteChapter(chapterId) {
        // Get chapter info for confirmation
        const chapter = this.chapters.find(ch => ch.id === chapterId);
        const chapterName = chapter ? (chapter.title || i18n.t('untitledChapter')) : i18n.t('untitledChapter');

        if (!confirm(`"${chapterName}" ${i18n.t('deleteChapterMessage')}`)) {
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
            alert(i18n.t('failedToDeleteChapter') + ': ' + error.message);
        }
    }

    async loadPrompts() {
        try {
            this.prompts = await API.getPrompts();
            this.renderPrompts();
        } catch (error) {
            console.error('Error loading prompts:', error);
            this.promptsContent.innerHTML = `<p class="loading">${i18n.t('failedToLoadPrompts')}</p>`;
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

    // === Preview & Export Methods ===

    setupPreviewExport() {
        // Get preview modal elements
        this.previewModal = document.getElementById('previewModal');
        this.previewModalTitle = document.getElementById('previewModalTitle');
        this.previewFrame = document.getElementById('previewFrame');
        this.btnPreview = document.getElementById('btnPreview');
        this.btnClosePreview = document.getElementById('btnClosePreview');
        this.btnClosePreviewBottom = document.getElementById('btnClosePreviewBottom');
        this.btnExportFromPreview = document.getElementById('btnExportFromPreview');

        // Add event listeners
        this.btnPreview.addEventListener('click', () => this.showPreview());
        this.btnClosePreview.addEventListener('click', () => this.closePreview());
        this.btnClosePreviewBottom.addEventListener('click', () => this.closePreview());
        this.btnExportFromPreview.addEventListener('click', () => {
            this.closePreview();
            this.exportPDF();
        });
    }

    async showPreview() {
        if (!this.editor.currentChapterId) {
            return;
        }

        try {
            // Update modal title
            this.previewModalTitle.textContent = i18n.t('chapterPreview');

            // Mark that we're previewing a chapter
            this.previewingFullMemoir = false;

            // Show modal
            this.previewModal.classList.add('visible');

            // Load preview in iframe
            this.previewFrame.src = `/api/chapters/${this.editor.currentChapterId}/preview`;
        } catch (error) {
            console.error('Error showing preview:', error);
            alert(i18n.t('failedToShowPreview') + ': ' + error.message);
            this.closePreview();
        }
    }

    async showMemoirPreview() {
        try {
            // Update modal title
            this.previewModalTitle.textContent = i18n.t('previewFullMemoir');

            // Mark that we're previewing the full memoir
            this.previewingFullMemoir = true;

            // Show modal
            this.previewModal.classList.add('visible');

            // Load full memoir preview in iframe
            this.previewFrame.src = '/api/memoir/preview';
        } catch (error) {
            console.error('Error showing memoir preview:', error);
            alert(i18n.t('failedToShowMemoirPreview') + ': ' + error.message);
            this.closePreview();
        }
    }

    closePreview() {
        this.previewModal.classList.remove('visible');
        // Clear iframe src to stop loading
        this.previewFrame.src = '';
    }

    async exportPDF() {
        try {
            // Determine which endpoint to use based on preview mode
            const endpoint = this.previewingFullMemoir
                ? '/api/memoir/export/pdf'
                : `/api/chapters/${this.editor.currentChapterId}/export/pdf`;

            if (!this.previewingFullMemoir && !this.editor.currentChapterId) {
                return;
            }

            // Fetch PDF file
            const response = await fetch(endpoint);

            // Check if response is an error (JSON) or success (PDF file)
            const contentType = response.headers.get('content-type');

            if (!response.ok) {
                // Error response - check if it's a dependency error
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    if (errorData.type === 'dependency_error') {
                        // Show helpful modal with installation instructions
                        this.showPDFDependencyError(errorData.message);
                    } else {
                        alert(i18n.t('failedToExportPDF') + ': ' + errorData.message);
                    }
                } else {
                    alert(i18n.t('failedToExportPDF') + '. Bitte versuche es erneut.');
                }
                return;
            }

            // Success - download the PDF
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            // Get filename from Content-Disposition header if available
            const disposition = response.headers.get('Content-Disposition');
            let filename = 'chapter.pdf';
            if (disposition && disposition.includes('filename=')) {
                filename = disposition.split('filename=')[1].replace(/"/g, '');
            }

            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Show success message
            alert(i18n.t('pdfExportedSuccessfully'));
        } catch (error) {
            console.error('Error exporting PDF:', error);
            alert(i18n.t('failedToExportPDF') + ': ' + error.message);
        }
    }

    showPDFDependencyError(message) {
        // Create modal overlay if it doesn't exist
        let modal = document.getElementById('pdfErrorModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'pdfErrorModal';
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 600px;">
                    <div class="modal-header">
                        <h3>${i18n.t('pdfExportNotAvailable')}</h3>
                        <button class="btn-close-modal" id="btnClosePdfError">&times;</button>
                    </div>
                    <div class="modal-body">
                        <pre style="white-space: pre-wrap; font-family: inherit; background: #f5f5f5; padding: 1rem; border-radius: 4px; line-height: 1.6;">${this.escapeHtml(message)}</pre>
                    </div>
                    <div class="modal-actions">
                        <button class="btn-primary" id="btnOkPdfError">OK</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            // Add event listeners
            modal.querySelector('#btnClosePdfError').addEventListener('click', () => {
                modal.classList.remove('visible');
            });
            modal.querySelector('#btnOkPdfError').addEventListener('click', () => {
                modal.classList.remove('visible');
            });
            // Close on overlay click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('visible');
                }
            });
        } else {
            // Update message if modal already exists
            const messageEl = modal.querySelector('pre');
            if (messageEl) {
                messageEl.textContent = message;
            }
        }

        // Show modal
        modal.classList.add('visible');
    }

    // === Cover Page Methods ===

    setupCoverPage() {
        // Get DOM elements
        this.coverModal = document.getElementById('coverPageModal');
        this.coverTitleInput = document.getElementById('coverTitleInput');
        this.coverSubtitleInput = document.getElementById('coverSubtitleInput');
        this.coverAuthorInput = document.getElementById('coverAuthorInput');
        this.coverImageInput = document.getElementById('coverImageInput');
        this.btnChooseCoverImage = document.getElementById('btnChooseCoverImage');
        this.btnRemoveCoverImage = document.getElementById('btnRemoveCoverImage');
        this.coverImagePreview = document.getElementById('coverImagePreview');
        this.coverImagePreviewImg = document.getElementById('coverImagePreviewImg');
        this.coverColorInput = document.getElementById('coverColorInput');
        this.suggestedColorsContainer = document.getElementById('suggestedColors');
        this.colorSuggestionsDiv = document.getElementById('colorSuggestions');

        // Preview elements
        this.coverPreviewTitle = document.getElementById('coverPreviewTitle');
        this.coverPreviewSubtitle = document.getElementById('coverPreviewSubtitle');
        this.coverPreviewAuthor = document.getElementById('coverPreviewAuthor');
        this.coverPreviewImage = document.getElementById('coverPreviewImage');
        this.coverPreview = document.getElementById('coverPreview');

        // Add event listeners
        document.getElementById('btnCloseCoverModal').addEventListener('click', () => this.closeCoverPageModal());
        document.getElementById('btnCancelCover').addEventListener('click', () => this.closeCoverPageModal());
        document.getElementById('btnSaveCover').addEventListener('click', () => this.saveCoverPage());

        this.btnChooseCoverImage.addEventListener('click', () => this.coverImageInput.click());
        this.btnRemoveCoverImage.addEventListener('click', () => this.removeCoverImage());
        this.coverImageInput.addEventListener('change', (e) => this.handleCoverImageSelect(e));

        // Live preview updates
        this.coverTitleInput.addEventListener('input', () => this.updateCoverPreview());
        this.coverSubtitleInput.addEventListener('input', () => this.updateCoverPreview());
        this.coverAuthorInput.addEventListener('input', () => this.updateCoverPreview());
        this.coverColorInput.addEventListener('input', () => this.updateCoverPreview());
    }

    async openCoverPageModal() {
        try {
            // Load current cover data
            const memoir = await API.getMemoir();
            this.coverData = memoir.cover || {};

            // Populate form
            this.coverTitleInput.value = this.coverData.title || '';
            this.coverSubtitleInput.value = this.coverData.subtitle || '';
            this.coverAuthorInput.value = this.coverData.author || '';
            this.coverColorInput.value = this.coverData.backgroundColor || '#f5f5f5';

            // Load cover image if exists
            if (this.coverData.image) {
                // Extract filename from path (e.g., "data/images/photo.jpg" -> "photo.jpg")
                const filename = this.coverData.image.split('/').pop();
                const imagePath = `/api/images/${filename}`;

                this.coverImagePreviewImg.src = imagePath;
                this.coverImagePreview.style.display = 'block';
                this.btnChooseCoverImage.style.display = 'none';
                this.btnRemoveCoverImage.style.display = 'inline-block';

                // Update preview
                this.coverPreviewImage.style.backgroundImage = `url(${imagePath})`;
                this.coverPreviewImage.style.display = 'block';
            } else {
                this.coverImageFile = null;
                this.coverImagePreview.style.display = 'none';
                this.btnChooseCoverImage.style.display = 'inline-block';
                this.btnRemoveCoverImage.style.display = 'none';
                this.coverPreviewImage.style.display = 'none';
            }

            // Update preview
            this.updateCoverPreview();

            // Show modal
            this.coverModal.classList.add('visible');
        } catch (error) {
            console.error('Error loading cover data:', error);
            alert(i18n.t('failedToLoadCover') + ': ' + error.message);
        }
    }

    closeCoverPageModal() {
        this.coverModal.classList.remove('visible');
        this.coverImageFile = null;
    }

    handleCoverImageSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate image
        if (!file.type.startsWith('image/')) {
            alert(i18n.t('pleaseSelectImageFile'));
            return;
        }

        this.coverImageFile = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            this.coverImagePreviewImg.src = e.target.result;
            this.coverImagePreview.style.display = 'block';
            this.btnChooseCoverImage.style.display = 'none';
            this.btnRemoveCoverImage.style.display = 'inline-block';

            // Update live preview
            this.coverPreviewImage.style.backgroundImage = `url(${e.target.result})`;
            this.coverPreviewImage.style.display = 'block';

            // Extract and suggest colors
            this.extractColorsFromImage(e.target.result);
        };
        reader.readAsDataURL(file);
    }

    removeCoverImage() {
        this.coverImageFile = null;
        this.coverImageInput.value = '';
        this.coverImagePreview.style.display = 'none';
        this.btnChooseCoverImage.style.display = 'inline-block';
        this.btnRemoveCoverImage.style.display = 'none';
        this.coverPreviewImage.style.display = 'none';

        // Hide color suggestions
        this.suggestedColorsContainer.style.display = 'none';

        // Mark for deletion if there was an existing image
        if (this.coverData && this.coverData.image) {
            this.coverData.deleteImage = true;
        }
    }

    updateCoverPreview() {
        const title = this.coverTitleInput.value || i18n.t('coverTitlePlaceholder');
        const subtitle = this.coverSubtitleInput.value;
        const author = this.coverAuthorInput.value || i18n.t('coverAuthorPlaceholder');
        const backgroundColor = this.coverColorInput.value;

        this.coverPreviewTitle.textContent = title;
        this.coverPreviewSubtitle.textContent = subtitle;
        this.coverPreviewSubtitle.style.display = subtitle ? 'block' : 'none';
        this.coverPreviewAuthor.textContent = author;

        // Update background color
        this.coverPreview.style.background = backgroundColor;
    }

    async saveCoverPage() {
        try {
            const coverData = {
                title: this.coverTitleInput.value,
                subtitle: this.coverSubtitleInput.value,
                author: this.coverAuthorInput.value,
                backgroundColor: this.coverColorInput.value
            };

            // Upload cover image if selected
            if (this.coverImageFile) {
                const formData = new FormData();
                formData.append('file', this.coverImageFile);

                const uploadResponse = await fetch('/api/images/upload', {
                    method: 'POST',
                    body: formData
                });

                const uploadResult = await uploadResponse.json();
                if (uploadResult.status === 'success') {
                    coverData.image = uploadResult.data.path;
                } else {
                    throw new Error('Failed to upload cover image');
                }
            } else if (this.coverData && this.coverData.deleteImage) {
                // Remove image
                coverData.image = null;
            } else if (this.coverData && this.coverData.image) {
                // Keep existing image
                coverData.image = this.coverData.image;
            }

            // Save cover data
            await API.updateCover(coverData);

            alert(i18n.t('coverSaved'));
            this.closeCoverPageModal();
        } catch (error) {
            console.error('Error saving cover:', error);
            alert(i18n.t('failedToSaveCover') + ': ' + error.message);
        }
    }

    // === Settings Modal Methods ===

    async openSettingsModal() {
        const modal = document.getElementById('settingsModal');
        await this.loadSettings();
        modal.classList.add('visible');

        // Setup event listeners
        document.getElementById('btnCloseSettings').addEventListener('click', () => this.closeSettingsModal());
        document.getElementById('btnCancelSettings').addEventListener('click', () => this.closeSettingsModal());
        document.getElementById('btnBrowseFolder').addEventListener('click', () => this.browseFolder());
        document.getElementById('btnStartMigration').addEventListener('click', () => this.startMigration());
    }

    closeSettingsModal() {
        const modal = document.getElementById('settingsModal');
        modal.classList.remove('visible');

        // Reset UI
        document.getElementById('newDataPath').value = '';
        document.getElementById('pathValidationResult').innerHTML = '';
        document.getElementById('migrationOptions').style.display = 'none';
        document.getElementById('migrationProgress').style.display = 'none';
    }

    async loadSettings() {
        try {
            const settings = await API.getSettings();

            document.getElementById('currentDataPath').textContent = settings.data_directory;
            document.getElementById('dataSize').textContent = `${settings.data_size_mb.toFixed(2)} MB`;
            document.getElementById('fileCount').textContent = settings.file_count;
        } catch (error) {
            console.error('Error loading settings:', error);
            alert('Fehler beim Laden der Einstellungen: ' + error.message);
        }
    }

    async browseFolder() {
        try {
            // Get current path as initial directory
            const pathInput = document.getElementById('newDataPath');
            const currentPath = pathInput.value.trim() || null;

            // Call API to open folder picker for PARENT directory
            const result = await API.browseFolder(currentPath);

            if (result.status === 'success' && result.path) {
                // Store parent path and show subfolder prompt
                this.selectedParentFolder = result.path;
                this.showSubfolderPrompt();
            }
            // If cancelled, do nothing
        } catch (error) {
            console.error('Error opening folder picker:', error);
            alert('Fehler beim Öffnen des Dateiauswahldialogs: ' + error.message);
        }
    }

    showSubfolderPrompt() {
        const modal = document.getElementById('subfolderPrompt');
        const parentPathDisplay = document.getElementById('selectedParentPath');
        const subfolderInput = document.getElementById('subfolderName');
        const previewCode = document.getElementById('fullPathPreview');

        // Show parent path
        parentPathDisplay.textContent = this.selectedParentFolder;

        // Reset to default subfolder name
        subfolderInput.value = 'MemDoc';

        // Update preview
        const updatePreview = () => {
            const subfolder = subfolderInput.value.trim() || 'MemDoc';
            const separator = this.selectedParentFolder.includes('\\') ? '\\' : '/';
            previewCode.textContent = `${this.selectedParentFolder}${separator}${subfolder}`;
        };
        updatePreview();

        // Update preview on input
        subfolderInput.oninput = updatePreview;

        // Show modal
        modal.style.display = 'flex';

        // Focus input and select text
        setTimeout(() => {
            subfolderInput.focus();
            subfolderInput.select();
        }, 100);

        // Setup event listeners
        document.getElementById('btnCancelSubfolder').onclick = () => this.closeSubfolderPrompt();
        document.getElementById('btnConfirmSubfolder').onclick = () => this.confirmSubfolder();

        // Allow Enter key to confirm
        subfolderInput.onkeydown = (e) => {
            if (e.key === 'Enter') {
                this.confirmSubfolder();
            } else if (e.key === 'Escape') {
                this.closeSubfolderPrompt();
            }
        };
    }

    closeSubfolderPrompt() {
        const modal = document.getElementById('subfolderPrompt');
        modal.style.display = 'none';
        this.selectedParentFolder = null;
    }

    confirmSubfolder() {
        const subfolderInput = document.getElementById('subfolderName');
        const subfolder = subfolderInput.value.trim() || 'MemDoc';
        const separator = this.selectedParentFolder.includes('\\') ? '\\' : '/';
        const fullPath = `${this.selectedParentFolder}${separator}${subfolder}`;

        // Update the path input field
        const pathInput = document.getElementById('newDataPath');
        pathInput.value = fullPath;

        // Clear any previous validation results
        const resultDiv = document.getElementById('pathValidationResult');
        resultDiv.textContent = '';
        resultDiv.className = 'validation-message';

        // Enable migrate button (will auto-validate on click)
        const migrateButton = document.getElementById('btnStartMigration');
        migrateButton.disabled = false;
        migrateButton.title = 'Daten zu diesem Ordner verschieben (validiert automatisch)';

        // Close the prompt
        this.closeSubfolderPrompt();
    }

    async validateNewPath() {
        const pathInput = document.getElementById('newDataPath');
        const path = pathInput.value.trim();
        const resultDiv = document.getElementById('pathValidationResult');
        const migrateButton = document.getElementById('btnStartMigration');

        if (!path) {
            resultDiv.innerHTML = '<span class="error">Bitte gib einen Pfad ein</span>';
            resultDiv.className = 'validation-message error';
            migrateButton.disabled = true;
            migrateButton.title = 'Bitte erst einen Ordner auswählen';
            return false;
        }

        try {
            resultDiv.innerHTML = '<span class="loading">Prüfe Pfad...</span>';
            resultDiv.className = 'validation-message loading';

            const result = await API.validateDataPath(path);

            if (result.is_valid) {
                resultDiv.innerHTML = `<span class="success">✓ ${result.message}</span>`;
                resultDiv.className = 'validation-message success';
                migrateButton.disabled = false;
                migrateButton.title = 'Daten zu diesem Ordner verschieben';
                return true;
            } else {
                resultDiv.innerHTML = `<span class="error">✗ ${result.message}</span>`;
                resultDiv.className = 'validation-message error';
                migrateButton.disabled = true;
                migrateButton.title = `Pfad ungültig: ${result.message}`;
                return false;
            }
        } catch (error) {
            resultDiv.innerHTML = `<span class="error">Fehler: ${error.message}</span>`;
            resultDiv.className = 'validation-message error';
            migrateButton.disabled = true;
            migrateButton.title = 'Fehler bei der Validierung';
            return false;
        }
    }

    async startMigration() {
        const path = document.getElementById('newDataPath').value.trim();
        const keepBackup = document.getElementById('keepBackup').checked;
        const progressDiv = document.getElementById('migrationProgress');
        const optionsDiv = document.getElementById('migrationOptions');
        const resultDiv = document.getElementById('pathValidationResult');

        // Always validate first
        resultDiv.innerHTML = '<span class="loading">Prüfe Pfad...</span>';
        resultDiv.className = 'validation-message loading';

        const isValid = await this.validateNewPath();
        if (!isValid) {
            return;
        }

        if (!confirm(
            'Möchtest du deine Memoiren wirklich verschieben?\n\n' +
            `Neuer Speicherort: ${path}\n` +
            `Backup behalten: ${keepBackup ? 'Ja' : 'Nein'}\n\n` +
            'Die Anwendung wird nach dem Verschieben neu gestartet.'
        )) {
            return;
        }

        try {
            optionsDiv.style.display = 'none';
            progressDiv.style.display = 'block';

            document.getElementById('migrationStatus').textContent = 'Verschiebe Dateien...';
            document.getElementById('migrationProgressBar').style.width = '50%';

            const result = await API.migrateData(path, keepBackup);

            document.getElementById('migrationProgressBar').style.width = '100%';
            document.getElementById('migrationStatus').textContent =
                `Erfolgreich! ${result.files_copied} Dateien kopiert. Starte neu...`;

            // Wait 2 seconds then reload
            setTimeout(() => {
                window.location.reload();
            }, 2000);

        } catch (error) {
            progressDiv.style.display = 'none';
            optionsDiv.style.display = 'block';
            alert('Migration fehlgeschlagen: ' + error.message);
        }
    }

    // === Color Extraction Methods ===

    extractColorsFromImage(imageDataUrl) {
        const img = new Image();
        img.onload = () => {
            // Create canvas to extract pixel data
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            // Resize for faster processing
            const maxSize = 100;
            const scale = Math.min(maxSize / img.width, maxSize / img.height);
            canvas.width = img.width * scale;
            canvas.height = img.height * scale;

            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

            // Get pixel data
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const pixels = imageData.data;

            // Extract dominant colors
            const colors = this.getDominantColors(pixels, 5);

            // Show suggestions
            this.showColorSuggestions(colors);
        };
        img.src = imageDataUrl;
    }

    getDominantColors(pixels, count = 5) {
        const colorMap = {};
        const step = 4; // Sample every 4th pixel for performance

        // Count colors (simplified - group similar colors)
        for (let i = 0; i < pixels.length; i += step * 4) {
            const r = pixels[i];
            const g = pixels[i + 1];
            const b = pixels[i + 2];
            const a = pixels[i + 3];

            // Skip transparent pixels
            if (a < 128) continue;

            // Quantize color (group similar colors)
            const qr = Math.round(r / 32) * 32;
            const qg = Math.round(g / 32) * 32;
            const qb = Math.round(b / 32) * 32;

            const key = `${qr},${qg},${qb}`;
            colorMap[key] = (colorMap[key] || 0) + 1;
        }

        // Sort by frequency
        const sortedColors = Object.entries(colorMap)
            .sort((a, b) => b[1] - a[1])
            .slice(0, count);

        // Convert to hex colors
        return sortedColors.map(([rgb]) => {
            const [r, g, b] = rgb.split(',').map(Number);
            return this.rgbToHex(r, g, b);
        });
    }

    rgbToHex(r, g, b) {
        return '#' + [r, g, b].map(x => {
            const hex = x.toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        }).join('');
    }

    showColorSuggestions(colors) {
        // Clear previous suggestions
        this.colorSuggestionsDiv.innerHTML = '';

        // Create color buttons
        colors.forEach(color => {
            const button = document.createElement('button');
            button.className = 'color-suggestion-btn';
            button.style.backgroundColor = color;
            button.title = color;
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.coverColorInput.value = color;
                this.updateCoverPreview();
            });
            this.colorSuggestionsDiv.appendChild(button);
        });

        // Show suggestions
        this.suggestedColorsContainer.style.display = 'block';
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MemDocApp();
});
