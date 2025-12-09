/**
 * Authentication & User Service Client
 * 
 * Handles:
 * - Walmart SSO login
 * - Guest login
 * - Session management
 * - Favorites, Notes, Inbox
 * - Local storage persistence
 */

// Dynamic API URL based on environment
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/api'
  : `https://${window.location.hostname}/api`;

class AuthClient {
    constructor() {
        this.sessionToken = localStorage.getItem('sessionToken');
        this.currentUser = this.loadUserFromStorage();
        this.isAuthenticated = !!this.sessionToken;
        this.init();
    }

    init() {
        console.log('[AuthClient] Initialized');
        if (this.isAuthenticated) {
            this.validateSession();
        }
    }

    // ========================================================================
    // AUTHENTICATION
    // ========================================================================

    /**
     * Login with Walmart SSO
     * In production, this would be called after Azure AD validates user
     */
    async loginWithSSO(walmartId, email, name) {
        try {
            const params = new URLSearchParams({
                walmart_id: walmartId,
                email: email,
                name: name
            });
            const response = await fetch(`${API_BASE}/auth/sso?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('SSO login failed');

            const data = await response.json();
            this.setSession(data.session_token, data.user);
            return data;
        } catch (error) {
            console.error('[AuthClient] SSO login error:', error);
            throw error;
        }
    }

    /**
     * Guest login (no SSO)
     */
    async loginAsGuest(email, name) {
        try {
            const params = new URLSearchParams({
                email: email,
                name: name
            });
            const response = await fetch(`${API_BASE}/auth/guest-login?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Guest login failed');

            const data = await response.json();
            this.setSession(data.session_token, data.user);
            return data;
        } catch (error) {
            console.error('[AuthClient] Guest login error:', error);
            throw error;
        }
    }

    /**
     * Validate current session
     */
    async validateSession() {
        if (!this.sessionToken) return false;

        try {
            const response = await fetch(`${API_BASE}/auth/validate?session_token=${this.sessionToken}`);
            if (!response.ok) {
                this.clearSession();
                return false;
            }

            const data = await response.json();
            this.currentUser = data.user;
            this.saveUserToStorage();
            return true;
        } catch (error) {
            console.error('[AuthClient] Session validation error:', error);
            this.clearSession();
            return false;
        }
    }

    /**
     * Logout
     */
    async logout() {
        if (!this.sessionToken) return;

        try {
            const params = new URLSearchParams({
                session_token: this.sessionToken
            });
            await fetch(`${API_BASE}/auth/logout?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
        } catch (error) {
            console.error('[AuthClient] Logout error:', error);
        } finally {
            this.clearSession();
        }
    }

    setSession(token, user) {
        this.sessionToken = token;
        this.currentUser = user;
        this.isAuthenticated = true;
        localStorage.setItem('sessionToken', token);
        this.saveUserToStorage();
        window.dispatchEvent(new CustomEvent('auth-changed', { detail: { user, authenticated: true } }));
    }

    clearSession() {
        this.sessionToken = null;
        this.currentUser = null;
        this.isAuthenticated = false;
        localStorage.removeItem('sessionToken');
        localStorage.removeItem('currentUser');
        window.dispatchEvent(new CustomEvent('auth-changed', { detail: { authenticated: false } }));
    }

    saveUserToStorage() {
        if (this.currentUser) {
            localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
        }
    }

    loadUserFromStorage() {
        const user = localStorage.getItem('currentUser');
        return user ? JSON.parse(user) : null;
    }

    // ========================================================================
    // FAVORITES
    // ========================================================================

    async addFavorite(supplierId, supplierName) {
        if (!this.sessionToken) throw new Error('Not authenticated');

        try {
            const params = new URLSearchParams({
                session_token: this.sessionToken,
                supplier_id: supplierId,
                supplier_name: supplierName
            });
            const response = await fetch(`${API_BASE}/favorites/add?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to add favorite');
            const data = await response.json();
            window.dispatchEvent(new CustomEvent('favorite-added', { detail: { supplierId } }));
            return data;
        } catch (error) {
            console.error('[AuthClient] Add favorite error:', error);
            throw error;
        }
    }

    async removeFavorite(supplierId) {
        if (!this.sessionToken) throw new Error('Not authenticated');

        try {
            const params = new URLSearchParams({
                session_token: this.sessionToken,
                supplier_id: supplierId
            });
            const response = await fetch(`${API_BASE}/favorites/remove?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to remove favorite');
            const data = await response.json();
            window.dispatchEvent(new CustomEvent('favorite-removed', { detail: { supplierId } }));
            return data;
        } catch (error) {
            console.error('[AuthClient] Remove favorite error:', error);
            throw error;
        }
    }

    async getFavorites() {
        if (!this.sessionToken) return { count: 0, favorites: [] };

        try {
            const response = await fetch(`${API_BASE}/favorites?session_token=${this.sessionToken}`);
            if (!response.ok) throw new Error('Failed to get favorites');
            return await response.json();
        } catch (error) {
            console.error('[AuthClient] Get favorites error:', error);
            return { count: 0, favorites: [] };
        }
    }

    async isFavorite(supplierId) {
        if (!this.sessionToken) return false;

        try {
            const response = await fetch(`${API_BASE}/favorites/is-favorite?session_token=${this.sessionToken}&supplier_id=${supplierId}`);
            if (!response.ok) return false;
            const data = await response.json();
            return data.is_favorite;
        } catch (error) {
            console.error('[AuthClient] Check favorite error:', error);
            return false;
        }
    }

    // ========================================================================
    // NOTES
    // ========================================================================

    async addNote(supplierId, content) {
        if (!this.sessionToken) throw new Error('Not authenticated');

        try {
            const params = new URLSearchParams({
                session_token: this.sessionToken,
                supplier_id: supplierId,
                content: content
            });
            const response = await fetch(`${API_BASE}/notes/add?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to add note');
            const data = await response.json();
            window.dispatchEvent(new CustomEvent('note-added', { detail: { supplierId } }));
            return data;
        } catch (error) {
            console.error('[AuthClient] Add note error:', error);
            throw error;
        }
    }

    async updateNote(noteId, content) {
        if (!this.sessionToken) throw new Error('Not authenticated');

        try {
            const params = new URLSearchParams({
                session_token: this.sessionToken,
                note_id: noteId,
                content: content
            });
            const response = await fetch(`${API_BASE}/notes/update?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to update note');
            return await response.json();
        } catch (error) {
            console.error('[AuthClient] Update note error:', error);
            throw error;
        }
    }

    async deleteNote(noteId) {
        if (!this.sessionToken) throw new Error('Not authenticated');

        try {
            const params = new URLSearchParams({
                session_token: this.sessionToken,
                note_id: noteId
            });
            const response = await fetch(`${API_BASE}/notes/delete?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to delete note');
            return await response.json();
        } catch (error) {
            console.error('[AuthClient] Delete note error:', error);
            throw error;
        }
    }

    async getNotes(supplierId = null) {
        if (!this.sessionToken) return { count: 0, notes: [] };

        try {
            let url = `${API_BASE}/notes?session_token=${this.sessionToken}`;
            if (supplierId) url += `&supplier_id=${supplierId}`;

            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to get notes');
            return await response.json();
        } catch (error) {
            console.error('[AuthClient] Get notes error:', error);
            return { count: 0, notes: [] };
        }
    }

    // ========================================================================
    // INBOX
    // ========================================================================

    async getInbox(unreadOnly = false) {
        if (!this.sessionToken) return { count: 0, unread_count: 0, messages: [] };

        try {
            const url = `${API_BASE}/inbox?session_token=${this.sessionToken}&unread_only=${unreadOnly}`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to get inbox');
            return await response.json();
        } catch (error) {
            console.error('[AuthClient] Get inbox error:', error);
            return { count: 0, unread_count: 0, messages: [] };
        }
    }

    async markAsRead(messageId) {
        if (!this.sessionToken) throw new Error('Not authenticated');

        try {
            const params = new URLSearchParams({
                session_token: this.sessionToken,
                message_id: messageId
            });
            const response = await fetch(`${API_BASE}/inbox/mark-read?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to mark as read');
            return await response.json();
        } catch (error) {
            console.error('[AuthClient] Mark as read error:', error);
            throw error;
        }
    }

    async markAllAsRead() {
        if (!this.sessionToken) throw new Error('Not authenticated');

        try {
            const params = new URLSearchParams({
                session_token: this.sessionToken
            });
            const response = await fetch(`${API_BASE}/inbox/mark-all-read?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to mark all as read');
            return await response.json();
        } catch (error) {
            console.error('[AuthClient] Mark all as read error:', error);
            throw error;
        }
    }

    async deleteMessage(messageId) {
        if (!this.sessionToken) throw new Error('Not authenticated');

        try {
            const params = new URLSearchParams({
                session_token: this.sessionToken,
                message_id: messageId
            });
            const response = await fetch(`${API_BASE}/inbox/delete?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to delete message');
            return await response.json();
        } catch (error) {
            console.error('[AuthClient] Delete message error:', error);
            throw error;
        }
    }

    async getUnreadCount() {
        if (!this.sessionToken) return { unread_count: 0 };

        try {
            const response = await fetch(`${API_BASE}/inbox/unread-count?session_token=${this.sessionToken}`);
            if (!response.ok) throw new Error('Failed to get unread count');
            return await response.json();
        } catch (error) {
            console.error('[AuthClient] Get unread count error:', error);
            return { unread_count: 0 };
        }
    }
}

// Create global instance
const authClient = new AuthClient();
