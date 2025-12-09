# LOGIN TROUBLESHOOTING GUIDE

## Issue: Login fails even with email and name

### Step 1: Check Browser Console

1. Open browser (Chrome, Firefox, Edge)
2. Press `F12` to open Developer Tools
3. Click "Console" tab
4. Try logging in
5. Look for any error messages in red

**Common errors:**
- `Failed to fetch` - Server not running
- `404` - Wrong URL
- `CORS` - Cross-origin issue
- `TypeError` - JavaScript error

### Step 2: Check Network Tab

1. Open Developer Tools (F12)
2. Click "Network" tab
3. Try logging in
4. Look for the `auth/login` request
5. Click on it and check:
   - **Status**: Should be 200 (success) or 400 (bad request)
   - **Response**: Should show JSON response

If status is `5xx` (500, 502, 503), the server crashed.

### Step 3: Verify Server is Running

Run this in PowerShell:

```powershell
# Test if server is responding
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
```

Should return:
```json
{
    "status": "healthy",
    "message": "API is running",
    "suppliers_loaded": 0,
    "mode": "PRODUCTION (ZERO LOCAL DATA)"
}
```

If it fails:
1. Server is not running
2. Run: `python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload`

### Step 4: Test Login Endpoint Directly

Run this in PowerShell:

```powershell
$body = @{
    email = "test@example.com"
    name = "Test User"
    walmart_id = $null
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" `
    -Method POST `
    -Headers @{'Content-Type' = 'application/json'} `
    -Body $body `
    -UseBasicParsing | Select-Object StatusCode, Content
```

**Expected response:**
```
StatusCode : 200
Content    : {"success":true,"session_id":"xxx","user_id":"user_xxx","message":"Welcome Test User!"}
```

If you get error:
- Check error message in Content
- Email or name might be invalid
- Server might have crashed

### Step 5: Check Browser Requirements

✅ Make sure:
- JavaScript is ENABLED
- Cookies/LocalStorage is ENABLED
- Not in Private/Incognito mode
- Using http://localhost:8000 (NOT https)
- Port 8000 is not blocked by firewall

### Step 6: Verify Login Form Validation

The login form requires:
- ✅ Email: Valid email format (must contain @)
- ✅ Name: At least 1 character
- ✅ Walmart ID: Optional

**Try these test values:**

| Email | Name | Expected Result |
|-------|------|---|
| test@example.com | John Doe | Should login |
| invalid | John Doe | Error: invalid email |
| test@example.com | | Error: name required |
| test@walmart.com | Test User | Should login |

### Step 7: Check Actual Server Logs

When you run the server, you should see logs like:

```
[LOGIN] User logged in: test@example.com
```

If you don't see this, the request never reached the server.

If you see an error in red, that's the problem.

### Step 8: Clear Browser Cache

1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty cache and hard refresh"
4. OR just press Ctrl+Shift+Delete
5. Try again

### Step 9: Try Guest Login Instead

If email/name login doesn't work, try:

1. Click "Continue as Guest"
2. This should automatically login
3. If this also fails, server is down or CORS is blocked

### Step 10: Check CORS

If you see CORS errors in console:

```
Access to XMLHttpRequest at 'http://localhost:8000/api/auth/login' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```

This means:
- You're accessing from wrong origin
- Visit http://localhost:8000 (not another port or IP)

---

## Common Solutions

### Solution 1: Server Not Running

```bash
cd "C:\Users\n0l08i7\Desktop\New folder\supplier-hub"
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Solution 2: Wrong URL

❌ Wrong:
- http://localhost:3000
- https://localhost:8000
- http://127.0.0.1:8001
- http://localhost:8000/dashboard

✅ Correct:
- http://localhost:8000

### Solution 3: Invalid Email Format

❌ Invalid:
- test@
- @example.com
- test
- test example.com

✅ Valid:
- test@example.com
- user@company.com
- john.doe@walmart.com

### Solution 4: Empty Name

✅ Valid:
- John Doe
- Test User
- (any text, even just "a")

❌ Invalid:
- (blank/empty)

### Solution 5: JavaScript Error

If you see red errors in console:

1. Open DevTools (F12)
2. Copy the error message
3. Check if it's syntax or network error
4. Try:
   - Hard refresh (Ctrl+Shift+R)
   - Clear cache
   - Restart browser
   - Restart server

### Solution 6: Firewall/Port Blocked

If connection is refused:

```
Error: connect ECONNREFUSED 127.0.0.1:8000
```

Either:
1. Port 8000 is blocked by firewall
2. Server is not running
3. Server crashed

Try:
```bash
# Check if port 8000 is in use
netstat -an | findstr "8000"

# Or try a different port
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

---

## Debug Checklist

- [ ] Server is running (see "Uvicorn running" message)
- [ ] Visiting http://localhost:8000 (not https or different port)
- [ ] Email is valid format (contains @)
- [ ] Name is not empty
- [ ] Browser console shows no JavaScript errors
- [ ] Network tab shows 200 status for login request
- [ ] /health endpoint returns 200
- [ ] Try guest login (to isolate form vs server issue)
- [ ] Cleared browser cache
- [ ] JavaScript is enabled
- [ ] LocalStorage is enabled (not private mode)

---

## If Still Not Working

1. **Screenshot** the error message and browser console
2. **Screenshot** the Network tab response
3. **Copy** the server logs when you try to login
4. Check that your project folder hasn't been moved
5. Restart everything:
   ```bash
   # Stop server (Ctrl+C)
   # Close browser
   # Run: python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   # Open fresh browser
   # Visit http://localhost:8000
   ```

---

**Last resort:** Run the test script to confirm API works:
```bash
python test_api.py
```

If test passes but login doesn't, it's a frontend issue.
If test fails, it's a backend issue.