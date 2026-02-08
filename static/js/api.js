/**
 * API Communication Module
 * Handles all API calls to the Flask backend
 */

const API = {
    /**
     * Get memoir metadata
     */
    async getMemoir() {
        const response = await fetch('/api/memoir');
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
    },

    /**
     * Update memoir metadata
     */
    async updateMemoir(metadata) {
        const response = await fetch('/api/memoir', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(metadata)
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    },

    /**
     * Get list of chapters
     */
    async getChapters() {
        const response = await fetch('/api/chapters');
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
    },

    /**
     * Get a specific chapter
     */
    async getChapter(chapterId) {
        const response = await fetch(`/api/chapters/${chapterId}`);
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
    },

    /**
     * Create a new chapter
     */
    async createChapter(title, subtitle = '') {
        const response = await fetch('/api/chapters', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, subtitle })
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
    },

    /**
     * Update a chapter
     */
    async updateChapter(chapterId, frontmatter, content) {
        const response = await fetch(`/api/chapters/${chapterId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ frontmatter, content })
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    },

    /**
     * Update chapter metadata (title, subtitle)
     */
    async updateChapterMetadata(chapterId, title, subtitle = '') {
        const response = await fetch(`/api/chapters/${chapterId}/metadata`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, subtitle })
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    },

    /**
     * Reorder a chapter (move up or down)
     */
    async reorderChapter(chapterId, direction) {
        const response = await fetch(`/api/chapters/${chapterId}/reorder`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ direction })
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    },

    /**
     * Delete a chapter
     */
    async deleteChapter(chapterId) {
        const response = await fetch(`/api/chapters/${chapterId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    },


    /**
     * Get word count statistics
     */
    async getStatistics() {
        const response = await fetch('/api/statistics');
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
    },

    /**
     * Update cover page data
     */
    async updateCover(coverData) {
        // Get current memoir data
        const memoir = await this.getMemoir();

        // Update cover section
        memoir.cover = coverData;

        // Save memoir metadata
        return await this.updateMemoir(memoir);
    },

    /**
     * Get application settings
     */
    async getSettings() {
        const response = await fetch('/api/settings');
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
    },

    /**
     * Validate a data directory path
     */
    async validateDataPath(path) {
        const response = await fetch('/api/settings/validate-path', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path })
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
    },

    /**
     * Migrate data to new directory
     */
    async migrateData(newPath, keepBackup = true) {
        const response = await fetch('/api/settings/migrate-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                new_path: newPath,
                keep_backup: keepBackup
            })
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
    },

    /**
     * Update user preferences
     */
    async updatePreferences(preferences) {
        const response = await fetch('/api/settings/preferences', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(preferences)
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    },

    /**
     * Open native folder picker dialog
     */
    async browseFolder(initialDir = null) {
        const response = await fetch('/api/settings/browse-folder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ initial_dir: initialDir })
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    },

    // ========== Update System ==========

    /**
     * Get current version information
     */
    async getVersion() {
        const response = await fetch('/api/version');
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
    },

    /**
     * Check for available updates from GitHub
     */
    async checkForUpdates() {
        const response = await fetch('/api/updates/check');
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
    },

    /**
     * Start downloading an update
     */
    async startUpdateDownload(downloadUrl) {
        const response = await fetch('/api/updates/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ download_url: downloadUrl })
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    },

    /**
     * Get download progress status
     */
    async getDownloadStatus() {
        const response = await fetch('/api/updates/download/status');
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
    },

    /**
     * Install downloaded update and restart application
     */
    async installUpdate() {
        const response = await fetch('/api/updates/install', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    },

    /**
     * Get list of available version backups
     */
    async getUpdateBackups() {
        const response = await fetch('/api/updates/backups');
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
    },

    /**
     * Rollback to a previous version
     */
    async rollbackToVersion(version) {
        const response = await fetch('/api/updates/rollback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ version })
        });
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data;
    }
};
