# How to Access Your Supplier Search Engine Dashboard

## Quick Start

### Option 1: Use the Swagger UI (FASTEST) ✅
**Status:** This works RIGHT NOW

Open your browser and go to:
```
http://127.0.0.1:8000/docs
```

This gives you an interactive dashboard where you can:
- View all API endpoints
- Test them live
- Import sample data
- Search suppliers
- View statistics

---

### Option 2: Run the Frontend Server
**Status:** Works but requires running a command

**On Windows, create a batch file with this content and run it:**

```batch
@echo off
cd /d "%~dp0"
start http://127.0.0.1:8888/index.html
python -m http.server 8888
pause
```

Save this as `START_FRONTEND.bat` in the supplier-search-engine folder and double-click it.

Or run in PowerShell:
```powershell
cd C:\Users\n0l08i7\Documents\supplier-search-engine
python -m http.server 8888
```

Then open: `http://127.0.0.1:8888/index.html`

---

## Backend Status

✅ **Backend API:** Running on `http://127.0.0.1:8000`
✅ **Database:** `suppliers.db` with sample data
✅ **Health Check:** `http://127.0.0.1:8000/health`

---

## Troubleshooting

If you get "connection refused":

1. **Check if backend is running:**
   ```
   curl http://127.0.0.1:8000/health
   ```
   You should see JSON response.

2. **Try the Swagger UI first:**
   ```
   http://127.0.0.1:8000/docs
   ```
   This will definitely work.

3. **For the HTML frontend:**
   - Make sure you're not trying multiple ports at once
   - Kill any old Python processes: `taskkill /F /IM python.exe`
   - Restart with the batch file above

---

## API Endpoints

```
GET  /health                          - Health check
GET  /api/suppliers                   - List all suppliers
GET  /api/suppliers/{id}              - Get specific supplier
GET  /api/suppliers/search/{query}    - Search suppliers
GET  /api/dashboard/stats             - Dashboard statistics
POST /api/data/ingest?source=local    - Import sample data
```
