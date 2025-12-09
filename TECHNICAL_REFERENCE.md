# Technical Reference Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    BROWSER CLIENT                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  index.html (SPA with Supplier Management)       │  │
│  │  - Search & Filter                              │  │
│  │  - Favorites Management                         │  │
│  │  - Notes System                                 │  │
│  │  - Real-time UI Updates                         │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Walmart SSO (OAuth 2.0)                        │  │
│  │  - walmart-sso-config.js (Token Management)     │  │
│  │  - PKCE Code Verification                       │  │
│  │  - Automatic Token Refresh                      │  │
│  │  - Session Persistence                          │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         ↓                              ↓
    OAuth Flow              API Requests (fetch)
         ↓                              ↓
┌─────────────────────────────────────────────────────────┐
│              WALMART OAUTH SERVER                        │
│  - auth.walmart.com/oauth/authorize                     │
│  - auth.walmart.com/oauth/token                         │
│  - api.walmart.com/v1/user/profile                      │
└─────────────────────────────────────────────────────────┘
         ↑                              ↓
         └──────────────────────────────┘
                  Callback
┌─────────────────────────────────────────────────────────┐
│                  BACKEND API (FastAPI)                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  /api/suppliers          - Get supplier list     │  │
│  │  /api/dashboard/stats    - Get dashboard stats   │  │
│  │  /api/auth/walmart-sso   - Real SSO callback    │  │
│  │  /api/favorites          - Manage favorites      │  │
│  │  /api/notes              - Manage notes          │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Database Layer                                 │  │
│  │  - Suppliers table                              │  │
│  │  - User sessions                                │  │
│  │  - Favorites/Notes (per user)                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## OAuth 2.0 Flow with PKCE

```
┌─────────────┐
│   User      │
│  Browser    │
└──────┬──────┘
       │
       │ 1. Click "Login with Walmart SSO"
       ↓
┌─────────────────────────────┐
│   index.html                 │
│   walmartSSO.startLogin()    │ 2. Generate state + PKCE code
└──────┬──────────────────────┘
       │
       │ 3. Redirect to Walmart OAuth server
       │ auth.walmart.com/oauth/authorize?client_id=xxx&state=yyy&code_challenge=zzz
       ↓
┌──────────────────────────────────┐
│   Walmart Auth Server             │
│   (User logs in here)              │ 4. User authenticates
└──────┬───────────────────────────┘
       │
       │ 5. Redirect to callback with authorization code
       │ http://localhost/auth/callback?code=abc123&state=yyy
       ↓
┌──────────────────────────────┐
│   auth-callback.html          │
│   (Callback handler)           │ 6. Validate state
│                                │ 7. Exchange code for token
└──────┬───────────────────────┘
       │
       │ 8. Call backend /api/auth/walmart-sso/token
       │ (Backend keeps client secret secure)
       ↓
┌──────────────────────────────┐
│   FastAPI Backend              │ 9. Use PKCE code_verifier
│   Token Exchange               │ 10. Get access token from Walmart
└──────┬───────────────────────┘
       │
       │ 11. Return access token to frontend
       ↓
┌──────────────────────────────┐
│   auth-callback.html          │
│   Save token to localStorage  │ 12. Session established
│   Setup auto-refresh timer    │ 13. Setup token refresh
└──────┬───────────────────────┘
       │
       │ 14. Redirect to dashboard
       ↓
┌──────────────────────────────┐
│   index.html (Logged in)      │
│   User can access all features│
└──────────────────────────────┘
```

## File Structure

```
supplier-hub/
│
├── Frontend Files
│   ├── index.html                    # Main SPA app
│   ├── favicon.svg                  # Browser tab icon
│   ├── walmart-sso-config.js        # OAuth 2.0 client
│   ├── auth-callback.html           # OAuth callback handler
│   ├── auth-client.js               # Auth helper
│   ├── help.html                    # Help documentation
│   ├── my-favorites.html            # Favorites page
│   ├── my-notes.html                # Notes page
│   ├── inbox.html                   # Inbox page
│   ├── dashboard_with_api.html      # Alternative dashboard
│   └── styles/
│
├── Backend Files
│   ├── app_minimal.py               # FastAPI server
│   ├── Procfile                     # Render deployment
│   ├── requirements.txt             # Python dependencies
│   └── validate_suppliers.py        # Data validation script
│
├── Documentation
│   ├── WALMART_SSO_SETUP.md        # SSO configuration guide
│   ├── SUPPLIER_DATA_ISSUE.md      # Critical data issue
│   ├── IMPLEMENTATION_SUMMARY.md   # Overview of changes
│   ├── TECHNICAL_REFERENCE.md      # This file
│   ├── README.md                    # Project readme
│   ├── API_DOCUMENTATION.md        # API reference
│   └── ...
│
├── Configuration
│   ├── .env                         # Environment variables (local)
│   ├── .env.example                 # Example env file
│   ├── .gitignore                   # Git ignore rules
│   └── ...
│
└── Deployment
    ├── .github/workflows/           # CI/CD pipelines
    ├── docker/                      # Docker config
    └── render.yaml                  # Render.com config
```

## Key JavaScript Classes

### WalmartSSO Class

```javascript
class WalmartSSO {
    // OAuth Flow Methods
    startLogin()                           // Initiate OAuth
    handleCallback(code, state)            // Process callback
    exchangeCodeForTokens(code)            // Get access token
    getUserProfile()                       // Fetch user data
    
    // Session Management
    saveSession()                          // Save to localStorage
    loadSession()                          // Load from storage
    setupTokenRefresh()                    // Auto-refresh setup
    refreshAccessToken()                   // Refresh tokens
    logout()                               // Clear session
    
    // Utility Methods
    isAuthenticated()                      // Check login status
    getUser()                              // Get current user
    generateRandomString(length)           // PKCE helper
    sha256(str)                            // Hash helper
    base64urlEncode(buf)                   // Encoding helper
}
```

## API Endpoints

### Suppliers

```
GET /api/suppliers
  Query: skip=0, limit=5000
  Returns: { total, skip, limit, count, suppliers: [...] }

GET /api/suppliers/search
  Query: q=string
  Returns: { count, suppliers: [...] }

GET /api/dashboard/stats
  Returns: { total_suppliers, walmart_verified, average_rating, ... }
```

### Authentication

```
POST /api/auth/walmart-sso/token
  Body: { code: string }
  Returns: { access_token, refresh_token, expires_in, ... }

GET /api/auth/validate
  Query: session_token=string
  Returns: { valid: boolean, user: {...} }

POST /api/auth/logout
  Body: { session_token: string }
  Returns: { message: "Logged out" }
```

### User Data

```
GET /api/favorites
  Headers: { Authorization: Bearer {token} }
  Returns: { favorites: [...] }

POST /api/favorites/add
  Headers: { Authorization: Bearer {token} }
  Body: { supplier_id: number, supplier_name: string }
  Returns: { success: boolean }

GET /api/notes
  Headers: { Authorization: Bearer {token} }
  Returns: { notes: {...} }

POST /api/notes/save
  Headers: { Authorization: Bearer {token} }
  Body: { supplier_id: number, note_text: string }
  Returns: { success: boolean }
```

## Environment Variables

### Development

```bash
# .env (local development)
WALMART_CLIENT_ID=your_dev_client_id
WALMART_CLIENT_SECRET=your_dev_client_secret
WALMART_REDIRECT_URI=http://localhost:8000/auth/callback
DATABASE_URL=sqlite:///./suppliers.db
DEBUG=true
ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000
```

### Production

```bash
# Render.com Environment Variables
WALMART_CLIENT_ID=your_prod_client_id
WALMART_CLIENT_SECRET=your_prod_client_secret
WALMART_REDIRECT_URI=https://supplier-hub.onrender.com/auth/callback
DATABASE_URL=postgresql://user:pass@host:5432/suppliers
DEBUG=false
ALLOWED_ORIGINS=https://supplier-hub.onrender.com
SECURE_COOKIES=true
HTTPS_ONLY=true
```

## Security Considerations

### HTTPS/SSL

- ✅ Always use HTTPS in production
- ✅ localhost HTTP is OK for development
- ✅ Let's Encrypt free SSL for Render
- ❌ Never expose OAuth credentials in URLs

### Token Management

- ✅ Store tokens in localStorage (with security caveats)
- ✅ Auto-refresh tokens before expiry
- ✅ Clear tokens on logout
- ✅ Validate token expiry on app load
- ❌ Never store tokens in URL
- ❌ Never log tokens to console in production

### OAuth Security

- ✅ Use PKCE code verification
- ✅ Validate state parameter
- ✅ Keep client secret server-side only
- ✅ Use HTTP-only cookies for sensitive data
- ✅ Validate redirect URIs exactly
- ❌ Never expose client secret in frontend code
- ❌ Never trust OAuth tokens without validation

### Data Protection

- ✅ Validate all user input
- ✅ Sanitize HTML to prevent XSS
- ✅ Use parameterized queries for DB
- ✅ Implement CORS properly
- ✅ Rate limit API endpoints
- ❌ Never store sensitive data in localStorage
- ❌ Never expose user passwords

## Deployment Checklist

### Pre-Deployment

- [ ] All tests pass
- [ ] No console errors
- [ ] No hardcoded secrets
- [ ] All dependencies updated
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] SSL certificate valid
- [ ] CORS properly configured

### Deployment

- [ ] Code pushed to main branch
- [ ] CI/CD pipeline passes
- [ ] Health check endpoint returns 200
- [ ] API endpoints respond correctly
- [ ] OAuth callback works
- [ ] Favicon displays
- [ ] No console errors in browser

### Post-Deployment

- [ ] Monitor error logs
- [ ] Check API latency
- [ ] Verify SSL certificate
- [ ] Test OAuth login flow
- [ ] Test supplier search
- [ ] Test favorites/notes
- [ ] Monitor resource usage
- [ ] Alert on error rate > 1%

## Performance Optimization

### Frontend

```javascript
// Lazy load components
const suppliers = lazy(() => import('./suppliers'));

// Cache API responses
const cache = new Map();
if (cache.has(url)) return cache.get(url);

// Debounce search
const debouncedSearch = debounce(search, 300);

// Virtual scrolling for long lists
const VirtualList = () => {};
```

### Backend

```python
# Database indexes
db.create_index('suppliers', 'category')
db.create_index('suppliers', 'name')

# Query optimization
suppliers = db.select(Supplier).limit(limit).offset(skip)

# Caching
@app.get("/api/stats")
@cache(expire=3600)  # Cache for 1 hour
def get_stats():
    ...

# Connection pooling
engine = create_engine(DATABASE_URL, pool_size=20)
```

## Troubleshooting

### OAuth Issues

**"State mismatch" error**
```
Solution: Clear sessionStorage and try again
sessionStorage.clear();
window.location.reload();
```

**"Invalid client" error**
```
Solution: Check Client ID in walmart-sso-config.js
Verify in Walmart Developer Portal
Check environment variables are loaded
```

**Redirect URI mismatch**
```
Solution: URI must EXACTLY match registered URI
No trailing slashes
Must use HTTPS in production
Check for typos
```

### API Issues

**CORS error**
```
Solution: Check CORS config in app_minimal.py
Allow-Origin header must match browser origin
Preflighted requests need OPTIONS handler
```

**Supplier data not loading**
```
Solution: Check API URL detection in index.html
Verify /api/suppliers endpoint returns data
Check browser network tab for actual request
Look for 404 or 500 errors
```

## References

- [RFC 6749 - OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
- [RFC 7636 - Proof Key for Public Clients (PKCE)](https://tools.ietf.org/html/rfc7636)
- [OWASP OAuth 2.0 Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OAuth_2_0_Cheat_Sheet.html)
- [Walmart Developer API](https://developer.walmart.com/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MDN - OAuth](https://developer.mozilla.org/en-US/docs/Glossary/OAuth)