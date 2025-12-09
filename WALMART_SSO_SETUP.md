# Walmart SSO (Single Sign-On) Setup Guide

## Overview

This supplier hub integrates with **Walmart's OAuth 2.0 authentication system** to provide secure, credential-based login for Walmart employees and partners.

## Prerequisites

1. **Walmart Developer Account** - Register at https://developer.walmart.com
2. **OAuth 2.0 Client Credentials** - Obtain from Walmart Developer Portal
3. **HTTPS Domain** - SSO requires HTTPS in production (localhost HTTP is OK for development)
4. **Backend Proxy** - Token exchange requires a backend service (cannot be done from frontend)

## Step 1: Register Application with Walmart

1. Go to https://developer.walmart.com
2. Sign in with your Walmart credentials
3. Navigate to **My Apps** → **Create New App**
4. Fill in application details:
   - **App Name:** Supplier Hub
   - **App Type:** Web Application
   - **Description:** Supplier search and management platform
   
5. Configure OAuth Settings:
   - **Redirect URIs:** 
     - Development: `http://localhost:8000/auth/callback`
     - Production: `https://yourdomain.com/auth/callback`
   - **Scopes:** `openid profile email supplier_id`
   - **Token Endpoint Auth Method:** POST

6. **Save** and copy your credentials:
   - **Client ID** - Public identifier
   - **Client Secret** - Keep this secret! (Use environment variables, never hardcode)

## Step 2: Update Configuration

### Frontend Configuration (walmart-sso-config.js)

```javascript
const WALMART_SSO_CONFIG = {
    clientId: 'YOUR_CLIENT_ID_HERE',  // Replace with your Client ID
    clientSecret: 'YOUR_CLIENT_SECRET_HERE',  // Use backend service only!
    redirectUri: `${window.location.origin}/auth/callback`,
    
    // Walmart endpoints (no changes needed)
    authorizationEndpoint: 'https://auth.walmart.com/oauth/authorize',
    tokenEndpoint: 'https://auth.walmart.com/oauth/token',
    userInfoEndpoint: 'https://api.walmart.com/v1/user/profile',
    logoutEndpoint: 'https://auth.walmart.com/oauth/logout',
};
```

### Backend Service (Python/FastAPI)

Create a backend endpoint to handle token exchange (NEVER do this from frontend):

```python
# app_minimal.py
from fastapi import HTTPException
import httpx
import os

@app.post("/api/auth/walmart-sso/token")
async def walmart_sso_token_exchange(code: str):
    """
    Exchange authorization code for access token.
    This MUST run on the backend to keep client secret secure.
    """
    client_id = os.getenv('WALMART_CLIENT_ID')
    client_secret = os.getenv('WALMART_CLIENT_SECRET')  # Never expose this!
    redirect_uri = os.getenv('WALMART_REDIRECT_URI')
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://auth.walmart.com/oauth/token',
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uri': redirect_uri,
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail='Token exchange failed')
            
            return response.json()
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
```

## Step 3: Environment Variables

Create a `.env` file (never commit this!):

```bash
# .env
WALMART_CLIENT_ID=your_client_id
WALMART_CLIENT_SECRET=your_client_secret  # KEEP THIS SECRET!
WALMART_REDIRECT_URI=https://yourdomain.com/auth/callback
```

Load in your app:

```python
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv('WALMART_CLIENT_ID')
```

## Step 4: Test SSO Flow

1. **Start your server:**
   ```bash
   python -m uvicorn app_minimal:app --host 0.0.0.0 --port 8000
   ```

2. **Open dashboard:**
   ```
   http://localhost:8000
   ```

3. **Click "Login with Walmart SSO"**
   - You'll be redirected to Walmart's authentication page
   - Login with your Walmart credentials
   - Accept permission scope
   - You'll be redirected back to `/auth/callback`

4. **Verify authentication:**
   - Check browser console for logs
   - Session should be saved to `localStorage`
   - You should see your Walmart profile data

## Step 5: Production Deployment

### HTTPS/SSL

1. Obtain SSL certificate (Let's Encrypt, CloudFlare, etc.)
2. Configure your web server for HTTPS
3. Update `WALMART_REDIRECT_URI` to production domain

### Environment Variables on Render

1. Go to your Render service settings
2. Add environment variables:
   ```
   WALMART_CLIENT_ID = your_production_client_id
   WALMART_CLIENT_SECRET = your_production_client_secret
   WALMART_REDIRECT_URI = https://yourdomain.onrender.com/auth/callback
   ```

### Update Walmart Developer Portal

1. Go to your Walmart app settings
2. Update Redirect URI to production:
   ```
   https://yourdomain.onrender.com/auth/callback
   ```

## OAuth Flow Diagram

```
┌─────────────┐      1. User clicks "Login with Walmart SSO"
│   Browser   │
│   (App)     │
└─────┬───────┘
      │
      │ 2. Redirects to Walmart auth
      ▼
┌─────────────────────────┐
│ Walmart Auth Server     │  3. User logs in & grants permission
│ auth.walmart.com        │
└─────────┬───────────────┘
          │
          │ 4. Redirects to callback with authorization code
          ▼
      ┌────────────────────┐
      │ /auth/callback     │
      │ 5. Exchanges code  │
      │ for access token   │  6. Calls backend token endpoint
      │ (frontend)         │     (keeps secret secure)
      └────────┬───────────┘
               │
               │ 7. Backend returns access token
               │
               ▼
          ┌─────────────┐
          │  Dashboard  │
          │  Logged In  │
          └─────────────┘
```

## Troubleshooting

### "State mismatch" Error
- The OAuth state parameter doesn't match
- Check that sessionStorage is enabled
- Clear browser cache and try again

### "Invalid client" Error
- Your Client ID or Client Secret is wrong
- Verify in Walmart Developer Portal
- Ensure environment variables are loaded

### Token Refresh Not Working
- Check that your backend token endpoint is correct
- Verify network requests in browser DevTools
- Check server logs for errors

### Redirect URI Mismatch
- The redirect URI must EXACTLY match what's registered
- No trailing slashes
- Must use HTTPS in production
- Check for typos

## Security Best Practices

✅ **DO:**
- Store client secret in environment variables
- Use HTTPS in production
- Validate state parameter
- Use PKCE (Proof Key for Code Exchange)
- Validate OAuth tokens
- Implement token refresh
- Use secure session storage

❌ **DON'T:**
- Hardcode secrets in code
- Expose client secret to frontend
- Skip state validation
- Use HTTP in production
- Trust unvalidated tokens
- Store passwords
- Log sensitive data

## References

- [Walmart Developer Portal](https://developer.walmart.com)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [PKCE RFC 7636](https://tools.ietf.org/html/rfc7636)
- [Walmart API Documentation](https://developer.walmart.com/api)

## Support

For issues with Walmart SSO:
1. Check the troubleshooting section above
2. Review Walmart Developer Documentation
3. Contact Walmart Developer Support
4. Check application logs for detailed error messages