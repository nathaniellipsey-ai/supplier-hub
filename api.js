/**
 * API Client Module
 * Handles all communication with the backend API
 * Professional REST API client with error handling
 */

const API_BASE_URL = 'http://localhost:8000';

class SupplierAPI {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
        this.cache = new Map();
    }

    /**
     * Make API request with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                method: options.method || 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...(options.body && { body: JSON.stringify(options.body) })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`Request failed: ${endpoint}`, error);
            throw error;
        }
    }

    /**
     * Health check
     */
    async health() {
        return this.request('/health');
    }

    /**
     * Get dashboard statistics
     */
    async getDashboardStats() {
        if (this.cache.has('stats')) {
            return this.cache.get('stats');
        }
        
        const data = await this.request('/api/dashboard/stats');
        this.cache.set('stats', data);
        return data;
    }

    /**
     * Get paginated list of suppliers
     */
    async getSuppliers(skip = 0, limit = 100) {
        const params = new URLSearchParams({ skip, limit });
        return this.request(`/api/suppliers?${params}`);
    }

    /**
     * Get single supplier by ID
     */
    async getSupplier(id) {
        return this.request(`/api/suppliers/${id}`);
    }

    /**
     * Search suppliers
     */
    async searchSuppliers(query, limit = 100) {
        const params = new URLSearchParams({ q: query, limit });
        return this.request(`/api/suppliers/search/query?${params}`);
    }

    /**
     * Advanced search with filters
     */
    async advancedSearch(filters) {
        return this.request('/api/suppliers/search', {
            method: 'POST',
            body: filters
        });
    }

    /**
     * Get all categories
     */
    async getCategories() {
        if (this.cache.has('categories')) {
            return this.cache.get('categories');
        }
        
        const data = await this.request('/api/categories');
        this.cache.set('categories', data);
        return data;
    }

    /**
     * Get suppliers by category
     */
    async getSuppliersByCategory(category, limit = 1000) {
        const params = new URLSearchParams({ limit });
        return this.request(`/api/categories/${encodeURIComponent(category)}?${params}`);
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
    }
}

// Export singleton instance
const api = new SupplierAPI();
