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
        this.btnClearFormat = document.getElementById('btnClearFormat');
        this.btnH1 = document.getElementById('btnH1');
        this.btnH2 = document.getElementById('btnH2');
        this.btnH3 = document.getElementById('btnH3');
        this.btnInsertImage = document.getElementById('btnInsertImage');
        this.btnPreview = document.getElementById('btnPreview');
        this.btnExportPDF = document.getElementById('btnExportPDF');

        // Image upload state
        this.currentImageData = null;

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
        this.btnClearFormat.addEventListener('click', () => this.clearFormatting());
        this.btnH1.addEventListener('click', () => this.formatHeading(1));
        this.btnH2.addEventListener('click', () => this.formatHeading(2));
        this.btnH3.addEventListener('click', () => this.formatHeading(3));
        this.btnInsertImage.addEventListener('click', () => this.openImageModal());

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

        // Drag and drop for images
        this.editor.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.editor.classList.add('drag-over');
        });

        this.editor.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.editor.classList.remove('drag-over');
        });

        this.editor.addEventListener('drop', (e) => {
            e.preventDefault();
            this.editor.classList.remove('drag-over');

            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type.startsWith('image/')) {
                this.handleImageFile(files[0]);
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
            this.btnClearFormat.disabled = false;
            this.btnH1.disabled = false;
            this.btnH2.disabled = false;
            this.btnH3.disabled = false;
            this.btnInsertImage.disabled = false;
            this.btnPreview.disabled = false;
            this.btnExportPDF.disabled = false;

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
        this.btnClearFormat.disabled = true;
        this.btnH1.disabled = true;
        this.btnH2.disabled = true;
        this.btnH3.disabled = true;
        this.btnInsertImage.disabled = true;
        this.btnPreview.disabled = true;
        this.btnExportPDF.disabled = true;

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

    clearFormatting() {
        const start = this.editor.selectionStart;
        const end = this.editor.selectionEnd;
        const currentValue = this.editor.value;
        const selectedText = currentValue.substring(start, end);

        if (!selectedText) {
            // No selection - do nothing or show a message
            return;
        }

        // Remove markdown formatting
        let cleanText = selectedText;

        // Remove bold (**text** or __text__)
        cleanText = cleanText.replace(/\*\*(.+?)\*\*/g, '$1');
        cleanText = cleanText.replace(/__(.+?)__/g, '$1');

        // Remove italic (*text* or _text_)
        cleanText = cleanText.replace(/\*(.+?)\*/g, '$1');
        cleanText = cleanText.replace(/_(.+?)_/g, '$1');

        // Remove headings (# at start of line)
        cleanText = cleanText.replace(/^#{1,6}\s+/gm, '');

        // Remove strikethrough (~~text~~)
        cleanText = cleanText.replace(/~~(.+?)~~/g, '$1');

        // Remove inline code (`text`)
        cleanText = cleanText.replace(/`(.+?)`/g, '$1');

        // Replace selection with cleaned text
        this.editor.value = currentValue.substring(0, start) + cleanText + currentValue.substring(end);

        // Restore selection
        this.editor.setSelectionRange(start, start + cleanText.length);
        this.editor.focus();

        // Trigger auto-save
        this.handleInput();
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

    // === Image Upload Methods ===

    openImageModal() {
        const modal = document.getElementById('imageUploadModal');
        const dropzone = document.getElementById('uploadDropzone');
        const preview = document.getElementById('uploadPreview');
        const fileInput = document.getElementById('imageFileInput');

        // Reset modal state
        dropzone.hidden = false;
        preview.hidden = true;
        this.currentImageData = null;
        document.getElementById('btnInsertImageToEditor').disabled = true;
        document.getElementById('imageCaption').value = '';
        document.getElementById('imagePosition').value = 'center';
        document.getElementById('imageSize').value = 'medium';

        // Show modal
        modal.classList.add('visible');

        // Setup event listeners (only once)
        if (!this.imageModalInitialized) {
            this.setupImageModalListeners();
            this.imageModalInitialized = true;
        }
    }

    setupImageModalListeners() {
        const modal = document.getElementById('imageUploadModal');
        const dropzone = document.getElementById('uploadDropzone');
        const fileInput = document.getElementById('imageFileInput');
        const btnClose = document.getElementById('btnCloseImageModal');
        const btnCancel = document.getElementById('btnCancelUpload');
        const btnInsert = document.getElementById('btnInsertImageToEditor');

        // Close modal
        btnClose.addEventListener('click', () => this.closeImageModal());
        btnCancel.addEventListener('click', () => this.closeImageModal());

        // Click to browse
        dropzone.addEventListener('click', () => fileInput.click());

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleImageFile(e.target.files[0]);
            }
        });

        // Drag and drop on dropzone
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('drag-over');
        });

        dropzone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-over');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-over');

            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type.startsWith('image/')) {
                this.handleImageFile(files[0]);
            }
        });

        // Insert image button
        btnInsert.addEventListener('click', () => this.insertImageToEditor());
    }

    closeImageModal() {
        const modal = document.getElementById('imageUploadModal');
        modal.classList.remove('visible');
    }

    async handleImageFile(file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file (JPG, PNG, GIF, WebP)');
            return;
        }

        // Validate file size (20MB max)
        const maxSize = 20 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('Image file is too large. Maximum size is 20MB.');
            return;
        }

        try {
            // Show modal if not already open
            const modal = document.getElementById('imageUploadModal');
            if (!modal.classList.contains('visible')) {
                this.openImageModal();
            }

            // Upload image
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/images/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.currentImageData = result.data;
                this.showImagePreview(file, result.data);
            } else {
                alert('Failed to upload image: ' + result.message);
            }
        } catch (error) {
            console.error('Error uploading image:', error);
            alert('Failed to upload image: ' + error.message);
        }
    }

    showImagePreview(file, imageData) {
        const dropzone = document.getElementById('uploadDropzone');
        const preview = document.getElementById('uploadPreview');
        const previewImage = document.getElementById('previewImage');
        const infoFilename = document.getElementById('infoFilename');
        const infoFileSize = document.getElementById('infoFileSize');
        const infoDimensions = document.getElementById('infoDimensions');
        const warningsContainer = document.getElementById('imageWarnings');
        const btnInsert = document.getElementById('btnInsertImageToEditor');

        // Hide dropzone, show preview
        dropzone.hidden = true;
        preview.hidden = false;

        // Show image preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
        };
        reader.readAsDataURL(file);

        // Show image info
        infoFilename.textContent = imageData.filename;
        infoFileSize.textContent = imageData.size_mb.toFixed(2) + ' MB';
        infoDimensions.textContent = imageData.dimensions;

        // Show warnings
        warningsContainer.innerHTML = '';
        if (imageData.warnings && imageData.warnings.length > 0) {
            imageData.warnings.forEach(warning => {
                const warningDiv = document.createElement('div');
                warningDiv.className = 'warning-item warning-warning';
                warningDiv.textContent = '⚠️ ' + warning;
                warningsContainer.appendChild(warningDiv);
            });
        }

        // Check resolution and add appropriate warning
        if (!imageData.resolution_ok) {
            const resolutionWarning = document.createElement('div');
            resolutionWarning.className = 'warning-item warning-error';
            resolutionWarning.textContent = '⚠️ Low resolution! Image may not print well. Minimum 300 DPI recommended.';
            warningsContainer.insertBefore(resolutionWarning, warningsContainer.firstChild);
        } else {
            const resolutionSuccess = document.createElement('div');
            resolutionSuccess.className = 'warning-item warning-success';
            resolutionSuccess.textContent = '✓ Good quality for printing';
            warningsContainer.appendChild(resolutionSuccess);
        }

        // Enable insert button
        btnInsert.disabled = false;
    }

    insertImageToEditor() {
        if (!this.currentImageData) {
            return;
        }

        const caption = document.getElementById('imageCaption').value;
        const position = document.getElementById('imagePosition').value;
        const size = document.getElementById('imageSize').value;

        // Generate markdown
        const markdown = this.generateImageMarkdown(
            this.currentImageData.path,
            caption,
            position,
            size
        );

        // Insert into editor at cursor position
        this.insertText('\n\n' + markdown + '\n\n');

        // Close modal
        this.closeImageModal();
    }

    generateImageMarkdown(imagePath, caption, position, size) {
        let markdown = `![${caption}](${imagePath})\n`;
        markdown += `{: .img-${position} .img-${size}}`;

        if (caption) {
            markdown += `\n\n*${caption}*`;
        }

        return markdown;
    }
}
