/**
 * Walmart SSO (Single Sign-On) Configuration
 * Integrates with Walmart's OAuth 2.0 authentication system
 */

const WALMART_SSO_CONFIG = {
    // ⚠️ PRODUCTION VALUES - Replace with your actual Walmart credentials
    clientId: 'YOUR_WALMART_CLIENT_ID',
    clientSecret: 'YOUR_WALMART_CLIENT_SECRET', // Never expose in frontend!
    redirectUri: `${window.location.origin}/auth/callback`,
    
    // Walmart OAuth endpoints
    authorizationEndpoint: 'https://auth.walmart.com/oauth/authorize',
    tokenEndpoint: 'https://auth.walmart.com/oauth/token',
    userInfoEndpoint: 'https://api.walmart.com/v1/user/profile',
    logoutEndpoint: 'https://auth.walmart.com/oauth/logout',
    
    // Scopes
    scopes: [
        'openid',           // Required for OpenID Connect
        'profile',          // User profile info
        'email',            // Email address
        'supplier_id'       // Walmart Supplier ID (if applicable)
    ],
    
    // Session configuration
    sessionTimeout: 7 * 24 * 60 * 60 * 1000, // 7 days in milliseconds
    tokenRefreshBuffer: 5 * 60 * 1000, // Refresh 5 minutes before expiry
};

/**
 * WalmartSSO Class
 * Handles OAuth 2.0 flow for Walmart authentication
 */
class WalmartSSO {
    constructor(config) {
        this.config = config;
        this.user = null;
        this.tokens = null;
        this.refreshTimer = null;
    }
    
    /**
     * Initiate Walmart SSO login
     * Redirects user to Walmart's authentication page
     */
    startLogin() {
        // Generate state and PKCE code
        const state = this.generateRandomString(32);
        const codeVerifier = this.generateRandomString(43);
        const codeChallenge = this.base64urlEncode(await this.sha256(codeVerifier));
        
        // Store for callback validation
        sessionStorage.setItem('oauth_state', state);
        sessionStorage.setItem('oauth_code_verifier', codeVerifier);
        
        // Build authorization URL
        const params = new URLSearchParams({
            client_id: this.config.clientId,
            redirect_uri: this.config.redirectUri,
            response_type: 'code',
            scope: this.config.scopes.join(' '),
            state: state,
            code_challenge: codeChallenge,
            code_challenge_method: 'S256',
            nonce: this.generateRandomString(32), // For ID token validation
        });
        
        // Redirect to Walmart SSO
        window.location.href = `${this.config.authorizationEndpoint}?${params.toString()}`;
    }
    
    /**
     * Handle OAuth callback
     * Called after user authenticates at Walmart
     */
    async handleCallback(code, state) {
        try {
            // Validate state
            const storedState = sessionStorage.getItem('oauth_state');
            if (state !== storedState) {
                throw new Error('State mismatch - possible CSRF attack');
            }
            
            // Exchange code for tokens
            const tokens = await this.exchangeCodeForTokens(code);
            this.tokens = tokens;
            
            // Get user profile
            this.user = await this.getUserProfile();
            
            // Store session
            this.saveSession();
            
            // Setup auto-refresh
            this.setupTokenRefresh();
            
            console.log('✅ Walmart SSO Login Successful:', this.user);
            return this.user;
            
        } catch (error) {
            console.error('❌ Walmart SSO Callback Error:', error);
            throw error;
        }
    }
    
    /**
     * Exchange authorization code for access token
     */
    async exchangeCodeForTokens(code) {
        const codeVerifier = sessionStorage.getItem('oauth_code_verifier');
        
        const response = await fetch(this.config.tokenEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                grant_type: 'authorization_code',
                code: code,
                client_id: this.config.clientId,
                client_secret: this.config.clientSecret,
                redirect_uri: this.config.redirectUri,
                code_verifier: codeVerifier,
            }),
        });
        
        if (!response.ok) {
            throw new Error(`Token exchange failed: ${response.status}`);
        }
        
        return await response.json();
    }
    
    /**
     * Get authenticated user's profile
     */
    async getUserProfile() {
        const response = await fetch(this.config.userInfoEndpoint, {
            headers: {
                'Authorization': `Bearer ${this.tokens.access_token}`,
            },
        });
        
        if (!response.ok) {
            throw new Error(`User profile fetch failed: ${response.status}`);
        }
        
        return await response.json();
    }
    
    /**
     * Save session to localStorage
     */
    saveSession() {
        const session = {
            user: this.user,
            tokens: this.tokens,
            expiresAt: Date.now() + (this.tokens.expires_in * 1000),
        };
        localStorage.setItem('walmart_sso_session', JSON.stringify(session));
    }
    
    /**
     * Load saved session from localStorage
     */
    loadSession() {
        const session = localStorage.getItem('walmart_sso_session');
        if (session) {
            const parsed = JSON.parse(session);
            // Check if session is still valid
            if (parsed.expiresAt > Date.now()) {
                this.user = parsed.user;
                this.tokens = parsed.tokens;
                return true;
            } else {
                localStorage.removeItem('walmart_sso_session');
            }
        }
        return false;
    }
    
    /**
     * Refresh access token
     */
    async refreshAccessToken() {
        try {
            const response = await fetch(this.config.tokenEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    grant_type: 'refresh_token',
                    refresh_token: this.tokens.refresh_token,
                    client_id: this.config.clientId,
                    client_secret: this.config.clientSecret,
                }),
            });
            
            if (!response.ok) {
                throw new Error('Token refresh failed');
            }
            
            this.tokens = await response.json();
            this.saveSession();
            return this.tokens;
        } catch (error) {
            console.error('Token refresh failed, re-login required:', error);
            this.logout();
            throw error;
        }
    }
    
    /**
     * Setup automatic token refresh
     */
    setupTokenRefresh() {
        if (this.refreshTimer) clearTimeout(this.refreshTimer);
        
        const timeUntilExpiry = this.tokens.expires_in * 1000 - this.config.tokenRefreshBuffer;
        this.refreshTimer = setTimeout(() => {
            this.refreshAccessToken().then(() => this.setupTokenRefresh());
        }, timeUntilExpiry);
    }
    
    /**
     * Logout user
     */
    logout() {
        // Clear local session
        localStorage.removeItem('walmart_sso_session');
        this.user = null;
        this.tokens = null;
        
        if (this.refreshTimer) clearTimeout(this.refreshTimer);
        
        // Redirect to Walmart logout
        const params = new URLSearchParams({
            client_id: this.config.clientId,
            logout_uri: window.location.origin,
        });
        
        window.location.href = `${this.config.logoutEndpoint}?${params.toString()}`;
    }
    
    /**
     * Check if user is logged in
     */
    isAuthenticated() {
        return !!this.user && !!this.tokens;
    }
    
    /**
     * Get current user
     */
    getUser() {
        return this.user;
    }
    
    /**
     * Helper: Generate random string
     */
    generateRandomString(length) {
        const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
        let result = '';
        const values = new Uint8Array(length);
        crypto.getRandomValues(values);
        for (let i = 0; i < length; i++) {
            result += charset[values[i] % charset.length];
        }
        return result;
    }
    
    /**
     * Helper: SHA256 hash
     */
    async sha256(str) {
        const encoder = new TextEncoder();
        const data = encoder.encode(str);
        return await crypto.subtle.digest('SHA-256', data);
    }
    
    /**
     * Helper: Base64URL encode
     */
    base64urlEncode(buf) {
        return btoa(String.fromCharCode.apply(null, new Uint8Array(buf)))
            .replace(/\+/g, '-')
            .replace(/\//g, '_')
            .replace(/=/g, '');
    }
}

// Export for use in app
const walmartSSO = new WalmartSSO(WALMART_SSO_CONFIG);