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
     * Get writing prompts
     */
    async getPrompts() {
        const response = await fetch('/api/prompts');
        const data = await response.json();
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        return data.data;
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
    }
};
