# Render Dashboard Configuration Fix

**Problem:** Render is still using `app_standalone:app` instead of `app:app`  
**Cause:** Dashboard settings are overriding the render.yaml file  
**Solution:** Change the Start Command directly in Render's web dashboard  
**Status:** ✅ READY TO FIX

---

## The Issue

Even though we created `render.yaml`, Render's web dashboard settings are overriding it. The dashboard is configured to use `app_standalone:app` which doesn't exist.

---

## Quick Fix (2 Minutes)

### Step 1: Open Render Dashboard

1. Go to: https://dashboard.render.com
2. Sign in with your account
3. Click on your **supplier-hub** service

### Step 2: Find Settings

1. Click the **Settings** tab (or gear icon)
2. Scroll down to find **Start Command**

### Step 3: Change Start Command

**Find:** 
```
Start Command (if left blank, Procfile or render.yaml will be used)
```

**Current value (wrong):**
```
python -m uvicorn app_standalone:app --host 0.0.0.0 --port $PORT
```

**Change to (correct):**
```
python -m uvicorn app:app --host 0.0.0.0 --port $PORT
```

**Steps:**
1. Click in the **Start Command** field
2. Clear the existing text (Ctrl+A, Delete)
3. Paste the new command:
   ```
   python -m uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
4. Click **Save**

### Step 4: Redeploy

1. Go to the **Deploys** tab
2. Click **Trigger deploy**
3. Select **Clear build cache** (important!)
4. Click **Deploy latest commit**
5. Wait 2-3 minutes for build to complete

---

## Visual Guide

```
Render Dashboard
    ↓
Click "supplier-hub" service
    ↓
Go to "Settings" tab
    ↓
Scroll to "Start Command" field
    ↓
Change from:
  python -m uvicorn app_standalone:app --host 0.0.0.0 --port $PORT
    ↓
Change to:
  python -m uvicorn app:app --host 0.0.0.0 --port $PORT
    ↓
Click "Save"
    ↓
Go to "Deploys" tab
    ↓
Click "Trigger deploy"
    ↓
Wait for build to complete
    ↓
Dashboard is LIVE! ✅
```

---

## What Each Option Means

| Option | Meaning | Status |
|--------|---------|--------|
| `app:app` | Use FastAPI app from app.py | ✅ CORRECT |
| `app_standalone:app` | Use app_standalone.py (doesn't exist) | ❌ WRONG |
| `main:app` | Use app from main.py | ❌ WRONG |

---

## Expected Results

**When Build Completes:**
```
==> Running 'python -m uvicorn app:app --host 0.0.0.0 --port $PORT'
INFO:     Application startup complete
```

**Your Dashboard Will Be Live At:**
```
https://supplier-hub.onrender.com
```

---

## Troubleshooting

### Build Still Fails

1. Check the Start Command again:
   - Should be: `python -m uvicorn app:app --host 0.0.0.0 --port $PORT`
   - Verify no typos

2. Clear Build Cache:
   - Go to Deploys tab
   - Click Trigger deploy
   - Check "Clear build cache"
   - Deploy

3. Check Logs:
   - Click your service
   - Click Logs tab
   - Look for error messages
   - Copy error and search for solution

### Module Not Found

If you see: `ModuleNotFoundError: No module named 'fastapi'`

1. Check requirements.txt has fastapi
2. Verify build completed successfully
3. Check Build Log for errors

### Port Issues

If you see: `OSError: [Errno 48] Address already in use`

1. Verify Start Command uses: `--port $PORT`
2. Don't hardcode port numbers
3. Let Render set the port

---

## Files Involved

✅ **app.py** - Main FastAPI application (this is what we're running)
✅ **requirements.txt** - All dependencies (already installed)
✅ **render.yaml** - Backup configuration (created earlier)
✅ **Procfile** - Fallback configuration (exists)

---

## Summary

**Problem:** Start Command in Render dashboard set to wrong value

**Solution:** Change Start Command to use `app:app`

**Steps:** 
1. Go to Render dashboard
2. Find supplier-hub service
3. Click Settings
4. Find Start Command field
5. Change to: `python -m uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Save
7. Redeploy

**Time:** 2 minutes

**Result:** Dashboard goes live! 🚀

---

## Need Help?

If you get stuck:

1. **Verify app.py exists:**
   ```bash
   ls app.py
   ```
   Should show: `app.py`

2. **Check Render dashboard logs:**
   - Go to your service
   - Click "Logs" tab
   - Look for error messages

3. **Verify Start Command:**
   - Go to Settings
   - Confirm it says: `python -m uvicorn app:app --host 0.0.0.0 --port $PORT`
   - No typos

---

**You've got this!** 🎉

Once you change the Start Command and redeploy, your dashboard will be live!