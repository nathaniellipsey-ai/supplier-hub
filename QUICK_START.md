# Supplier Hub - Quick Start Guide

**Status:** READY TO RUN  
**Backend:** FastAPI (app.py)  
**Frontend:** HTML/CSS/JS (dashboard_with_api.html)  
**API:** RESTful endpoints at /api/*  
**Data:** 500 suppliers (seeded, consistent)  

---

## Local Development (2 minutes)

### Option 1: Windows (Batch File)

```bash
cd supplier-hub
start_server.bat
```

Then open: http://localhost:8000

### Option 2: Command Line

```bash
cd supplier-hub

# Install dependencies (first time only)
pip install -r requirements.txt

# Start server
python -m uvicorn app:app --reload --port 8000
```

Then open: http://localhost:8000

### Option 3: Python

```bash
cd supplier-hub
python app.py
```

---

## What You'll See

### Server Startup
```
================================================================================
SUPPLIER HUB - STARTING SERVER
================================================================================

Server will be available at:
  • Dashboard:  http://localhost:8000
  • API Docs:   http://localhost:8000/api/docs
  • ReDoc:      http://localhost:8000/api/redoc

API Endpoints:
  • GET  /api/suppliers
  • GET  /api/suppliers/{id}
  • GET  /api/categories
  • GET  /api/regions
  • GET  /api/stats

================================================================================
```

### Dashboard
Open http://localhost:8000 and you'll see:
- **Top**: Stats bar with total suppliers, verified count, avg rating, avg AI score
- **Left**: Filter sidebar (category, region, certifications, rating, AI score)
- **Center**: Supplier cards with name, rating, AI score, products
- **Bottom**: Pagination controls

---

## API Endpoints

### Get Suppliers
```bash
GET http://localhost:8000/api/suppliers?skip=0&limit=50&search=lumber

Query Parameters:
  - skip: Offset for pagination (default: 0)
  - limit: Number of results (default: 50, max: 500)
  - search: Search suppliers, products, categories
  - category: Filter by category
  - region: Filter by region
  - verified_only: Only verified suppliers (true/false)
  - min_rating: Minimum rating (0-5)
  - min_ai_score: Minimum AI score (0-100)
```

### Get Single Supplier
```bash
GET http://localhost:8000/api/suppliers/1
```

### Get Stats
```bash
GET http://localhost:8000/api/stats
```

### Get Categories
```bash
GET http://localhost:8000/api/categories
```

### Get Regions
```bash
GET http://localhost:8000/api/regions
```

---

## Architecture

```
supplier-hub/
├── app.py                   <- FastAPI server (MAIN BACKEND)
├── suppliers.py             <- Supplier data generator (seeded)
├── requirements.txt         <- Python dependencies
├── Procfile                 <- Deployment config
├── runtime.txt              <- Python version
│
├── dashboard_with_api.html  <- Main frontend (MAIN FRONTEND)
├── help.html                <- Help page
├── my-favorites.html        <- Favorites page
├── my-notes.html            <- Notes page
├── inbox.html               <- Inbox page
│
├── style.css                <- Styling
├── app.js                   <- App logic
├── components.js            <- Component logic
├── auth-client.js           <- Auth logic
├── api.js                   <- API client
└── walmart-sso-config.js    <- SSO config
```

---

## Files

### Backend
- **app.py** - FastAPI application with all API endpoints
  - Entry point: `app` FastAPI instance
  - Generates 500 seeded suppliers on startup
  - Provides /api/* endpoints
  - Serves static HTML/CSS/JS files
  - Ready for production

- **suppliers.py** - Supplier data generator
  - Seeded with 1962 (Walmart founding year)
  - Generates consistent data
  - 10 product categories
  - 9 regions
  - Random but reproducible

### Frontend
- **dashboard_with_api.html** - Main dashboard interface
  - Displays suppliers from API
  - Search and filter functionality
  - Favorites and notes features
  - Responsive design

### Configuration
- **requirements.txt** - Python dependencies
- **Procfile** - For Render/Heroku deployment
- **runtime.txt** - Python version specification

---

## Testing

### Test Backend
```bash
# Check API is working
curl http://localhost:8000/api/health

# Get suppliers
curl "http://localhost:8000/api/suppliers?limit=5"

# Get stats
curl http://localhost:8000/api/stats
```

### Test Frontend
1. Open http://localhost:8000
2. Dashboard should load
3. Suppliers should appear
4. Filters should work
5. Search should work

---

## Deployment

### Render.com

1. Push code to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. On Render Dashboard:
   - New Web Service
   - Connect GitHub repository
   - Configure:
     - Build: `pip install -r requirements.txt`
     - Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - Deploy

3. Your dashboard will be live at:
   ```
   https://supplier-hub.onrender.com
   ```

### Heroku

```bash
heroku login
heroku create supplier-hub
git push heroku main
heroku open
```

---

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Use different port
python -m uvicorn app:app --port 8001
```

### "Static files not found"
- Make sure HTML/CSS/JS files are in same directory as app.py
- Check file names match (case-sensitive on Linux)

### "API not responding"
- Check server is running
- Check http://localhost:8000/api/health returns {"status": "ok"}
- Check browser console for errors

---

## Features

- **500 Suppliers** - Seeded random data (everyone sees same)
- **Search** - By name, product, category
- **Filters** - Category, region, certifications, rating, AI score
- **Pagination** - Load more suppliers
- **Favorites** - Save suppliers (localStorage)
- **Notes** - Add personal notes (localStorage)
- **Inbox** - Messages placeholder
- **Responsive** - Works on desktop, tablet, mobile
- **Production Ready** - Proper error handling and logging

---

## Next Steps

1. **Local**: Run `python app.py` and test
2. **Git**: Push to GitHub
3. **Deploy**: Deploy to Render or Heroku
4. **Share**: Get your live URL and share
5. **Enjoy**: You have a live supplier search engine!

---

## Questions?

Check:
- `/api/docs` - Interactive API documentation
- `/api/redoc` - ReDoc API documentation
- This README file
- Source code comments

---

**Happy coding!** 🚀