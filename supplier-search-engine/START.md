# Quick Start Script

## Option 1: Start Both Servers (Windows)

Create a batch file `start-all.bat`:

```batch
@echo off
echo [INFO] Starting Supplier Search Engine Full Stack...
echo.

echo [STEP 1] Starting Backend (FastAPI)...
start cmd /k "cd backend && uvicorn main:app --reload --port 8000"

echo [STEP 2] Starting Frontend (React)...
echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak
start cmd /k "cd frontend && npm run dev"

echo.
echo [SUCCESS] Both servers started!
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
pause
```

Double-click to run!

## Option 2: Manual Start (Windows)

Open two terminal windows:

**Terminal 1 - Backend:**
```cmd
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```cmd
cd frontend
npm run dev
```

## Option 3: Start on Linux/Mac

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## First Time Setup

### Backend First Time

```bash
cd backend
```

Optional - create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Start server:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend First Time

```bash
cd frontend
npm install  # Install dependencies
npm run dev # Start dev server
```

## Verify Everything Works

1. **Backend Health Check**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy", ...}`

2. **API Health Check**
   ```bash
   curl http://localhost:8000/api/health
   ```
   Should show database status

3. **API Documentation**
   Open in browser: http://localhost:8000/docs

4. **Frontend Access**
   Open in browser: http://localhost:5173

## What Each Tab Does

### Dashboard
- Shows live statistics
- Supplier count by category
- Product inventory
- Search history

### Suppliers
- Lists all suppliers
- Shows contact info
- Status indicators
- Location details

### Search
- Search by name or keyword
- Filter by category
- Live search results

### Import Data
- Pull from live sources
- Walmart suppliers
- Global suppliers
- Alibaba
- Local sample data (for testing)

## Try These Actions

1. **Check Dashboard**
   - Click Dashboard tab
   - See current statistics

2. **View Suppliers**
   - Click Suppliers tab
   - Browse all suppliers

3. **Search**
   - Click Search tab
   - Search for "Electronics"
   - Or any other keyword

4. **Import Data**
   - Click Import Data tab
   - Select "local_sample"
   - Click Import Data
   - Watch suppliers appear!

## Troubleshooting

### Backend won't start
```
Error: Port 8000 already in use
```
Solution:
```bash
uvicorn main:app --reload --port 8001  # Use different port
```

### Frontend won't start
```
Error: npm: command not found
```
Solution:
- Install Node.js from https://nodejs.org/
- Close terminal and try again

### CORS errors in frontend
- Make sure backend is running
- Check browser console for errors
- Try refreshing the page

### Database errors
```bash
# Reset database
del suppliers.db
# Backend will recreate it automatically
```

## Development Workflow

1. Backend changes auto-reload (thanks to `--reload`)
2. Frontend changes auto-refresh (thanks to Vite)
3. No need to restart servers for code changes
4. Check browser console for frontend errors
5. Check terminal for backend errors

## Next Steps

1. **Add Authentication**
   - Implement JWT tokens
   - Add login/logout
   - Protect routes

2. **Add More Data Sources**
   - Edit services.py SOURCES dict
   - Add API endpoints
   - Test with real data

3. **Deploy to Cloud**
   - Heroku, AWS, or Azure
   - Docker containerization
   - Environment variables

4. **Add Testing**
   - Unit tests
   - Integration tests
   - E2E tests

5. **Performance**
   - Database pagination
   - API caching
   - Frontend optimization

## File Locations

- **Database**: `suppliers.db`
- **Backend**: `backend/`
- **Frontend**: `frontend/`
- **Original CLI**: Root directory

## Need Help?

- Backend API docs: http://localhost:8000/docs
- Code is self-documented with comments
- Check FULLSTACK_SETUP.md for detailed info
- Check README.md for original database docs
