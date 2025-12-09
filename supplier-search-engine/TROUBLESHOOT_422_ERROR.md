# Troubleshooting 422 Error

## What is 422?
422 Unprocessable Entity - The request was well-formed but the server could not process it due to validation errors.

## Common Causes

### 1. Server Not Running
**Problem:** No server is listening on port 8000
**Solution:**
```bash
cd "C:\Users\n0l08i7\Desktop\New folder\supplier-hub\supplier-search-engine"
python app_minimal.py
```
Wait for: `[SUCCESS] Generated 5000 suppliers`

### 2. Missing Dependencies
**Problem:** FastAPI, Uvicorn, or Pydantic not installed
**Solution:**
```bash
pip install fastapi uvicorn pydantic
```

### 3. CORS Issues
**Problem:** Browser blocking requests from different origin
**Solution:** Check browser console (F12 → Console tab) for CORS errors
The backend already handles CORS, but verify you're accessing from the same origin.

### 4. Invalid Request Data
**Problem:** Missing or malformed JSON in the request
**Solution:** 
- Make sure all form fields are filled
- Check browser Network tab (F12 → Network → look for auth/register or auth/login requests)
- Verify the JSON payload looks correct

### 5. API Path Issue
**Problem:** Frontend sending request to wrong endpoint
**Solution:**
- Check that API_BASE = '/api' in index_login.html
- Endpoints should be: `/api/auth/register`, `/api/auth/login`, etc.

## Step-by-Step Debugging

### Step 1: Verify Server is Running
```bash
# In a terminal:
cd "C:\Users\n0l08i7\Desktop\New folder\supplier-hub\supplier-search-engine"
python app_minimal.py

# You should see:
# [INFO] Starting Supplier Search Engine API...
# [INFO] Generating suppliers with seeded RNG...
# [SUCCESS] Generated 5000 suppliers
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

If the server won't start, check the error message!

### Step 2: Test with Browser Developer Tools
1. Open http://localhost:8000
2. Press F12 to open Developer Tools
3. Go to Console tab
4. Go to Network tab
5. Try to register or login
6. Look at the network request:
   - URL should be: http://localhost:8000/api/auth/register or /api/auth/login
   - Status should show the actual response code
   - Response body will show the error details

### Step 3: Check the Request Payload
In Network tab, click on the failed request and look at "Request" → "Payload":

**For Login, should be:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**For Registration, should be:**
```json
{
  "username": "your_username",
  "password": "your_password",
  "email": "your@email.com",
  "name": "Your Name"
}
```

### Step 4: Test with curl
If you have curl installed:

```bash
# Test login (this should fail because no user exists yet)
curl -X POST http://localhost:8000/api/auth/login ^^
  -H "Content-Type: application/json" ^^
  -d "{\"username\":\"test\",\"password\":\"test123\"}"

# Test registration
curl -X POST http://localhost:8000/api/auth/register ^^
  -H "Content-Type: application/json" ^^
  -d "{\"username\":\"test\",\"password\":\"test123\",\"email\":\"test@test.com\",\"name\":\"Test User\"}"
```

### Step 5: Check Server Console
Look at the server terminal window where app_minimal.py is running:
- Any error messages?
- Any traceback?
- Copy the full error and search for it

## Common 422 Scenarios

### Scenario 1: Empty Form Submitted
**Error:** `422 Unprocessable Entity`
**Cause:** Form fields are empty
**Solution:** Fill in ALL fields before clicking register/login

### Scenario 2: Password Too Short
**Error:** 422 (JavaScript validation should catch this first)
**Cause:** Password less than 8 characters
**Solution:** Use a password with 8+ characters

### Scenario 3: Wrong Field Names
**Error:** 422 with field validation error
**Cause:** Frontend sending wrong JSON field names
**Solution:** Check index_login.html JavaScript matches backend Pydantic model

## Backend Validation

The backend expects:

**LoginRequest:**
```python
class LoginRequest(BaseModel):
    username: str    # required, string
    password: str    # required, string
```

**RegisterRequest:**
```python
class RegisterRequest(BaseModel):
    username: str    # required, string
    password: str    # required, string
    email: str       # required, string
    name: str        # required, string
```

All fields are REQUIRED. Missing any field = 422 error.

## If All Else Fails

1. Check browser console (F12 → Console) for JavaScript errors
2. Check network tab for actual response body
3. Restart the server: `python app_minimal.py`
4. Clear browser cache and cookies
5. Try a different browser
6. Check if port 8000 is in use: `netstat -ano | findstr :8000`

## Get Help

When reporting the issue, include:
1. The full error message from Network tab
2. The Request payload (JSON being sent)
3. The Response body (what the server returned)
4. The server console output
5. Browser console errors (if any)

## Quick Checklist

- [ ] Server running? (`python app_minimal.py`)
- [ ] Port 8000 accessible? (`http://localhost:8000`)
- [ ] All form fields filled?
- [ ] Password 8+ characters?
- [ ] Network tab shows actual error details?
- [ ] Server console has any errors?
- [ ] Dependencies installed? (`pip install fastapi uvicorn pydantic`)
- [ ] Browser console has errors? (F12)

---

## Example: Complete Debugging Session

```
1. Open terminal
2. cd "C:\Users\n0l08i7\Desktop\New folder\supplier-hub\supplier-search-engine"
3. python app_minimal.py
4. Open http://localhost:8000 in browser
5. Press F12 → Network tab
6. Fill in registration form completely
7. Click Register
8. Look at Network tab → find the auth/register request
9. Click on it and check Response body
10. If 422, look at error details
11. Copy the exact error message
12. Check if request payload matches expected format
```

## Still Stuck?

The 422 error means the backend received the request but couldn't process it.
Check:
1. Are all required fields being sent?
2. Are field names spelled correctly?
3. Is the JSON valid?
4. Are all strings being sent (not numbers or booleans)?

Each detail matters for validation!
