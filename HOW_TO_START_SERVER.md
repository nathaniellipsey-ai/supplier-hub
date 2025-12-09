# HOW TO START THE SUPPLIER HUB SERVER

## The Problem You Saw

You got an error about `ModuleNotFoundError: No module named 'backend'`

This happens when using the `--reload` flag with uvicorn. The solution is to **remove the `--reload` flag** when starting the server.

---

## CORRECT WAY TO START

### Option 1: Command Line (Recommended)

Open PowerShell or Command Prompt:

```powershell
cd "C:\Users\n0l08i7\Desktop\New folder\supplier-hub"
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

**DO NOT add `--reload`**

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
```

### Option 2: Batch File

Double-click: `RUN_SERVER.bat`

This will start the server without reload.

---

## After Server Starts

1. **Visit the application:**
   ```
   http://localhost:8000
   ```

2. **You should see:** Login page ✅

3. **API documentation:**
   ```
   http://localhost:8000/docs
   ```

4. **To stop server:** Press `CTRL+C` in the terminal

---

## What NOT To Do

❌ **DON'T use:**
```powershell
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag causes the error you saw.

---

## Why This Happens

Uvicorn with `--reload` uses a file watcher that:
1. Detects file changes
2. Tries to reload the module
3. Gets confused by the directory structure
4. Tries to import a 'backend' module that doesn't exist

**Solution:** Remove `--reload`

The server still works fine without auto-reload. Just restart it manually when you make changes.

---

## If You Want Auto-Reload

If you really want auto-reload for development:

```powershell
cd "C:\Users\n0l08i7\Desktop\New folder\supplier-hub"
python -m uvicorn app:app --reload --reload-dirs . --host 0.0.0.0 --port 8000
```

But the simple version without `--reload` is safer.

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError: No module named 'backend' | Remove `--reload` flag |
| Port 8000 already in use | Use different port: `--port 8001` |
| Can't access http://localhost:8000 | Make sure server is running (look for "Uvicorn running" message) |
| Server crashes on startup | Run: `python -c "from app import app; print('[OK]'"` to check imports |

---

## THE CORRECT COMMAND

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

**That's it! No `--reload`, no other flags needed.** ✅

---

## Next: Test Login

Once server is running:

1. Visit: `http://localhost:8000`
2. Login with:
   - Email: `test@example.com`
   - Name: `Test User`
   - Walmart ID: (leave blank)
3. Click Login

You should be redirected to the dashboard! 🎉

---

**Server is ready to go!** 🚀