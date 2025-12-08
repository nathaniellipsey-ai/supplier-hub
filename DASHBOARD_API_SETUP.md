# Dashboard API Setup - Quick Start

## What Was Done

✅ **Created an API for your existing dashboard** (`supplier-search-engine.html`)
✅ **Generated 5000 suppliers** using seeded random data (seed: 1962)
✅ **No changes to dashboard presentation or data structure**
✅ **Consistent, reproducible supplier data** across all sessions

## Files Created

1. **`backend/suppliers_generator.py`** - Supplier data generator
2. **`API_DOCUMENTATION.md`** - Complete API reference
3. **`START_BACKEND.bat`** - Simple batch file to start the API

## Quick Start

### Step 1: Start the Backend

**Double-click:** `START_BACKEND.bat`

Or run in PowerShell:
```powershell
cd C:\Users\n0l08i7\Documents\supplier-search-engine\backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 2: Verify It Works

Open your browser and go to:
```
http://127.0.0.1:8000/docs
```

You should see the **Swagger API documentation** with all endpoints listed and testable.

### Step 3: Use the API

**API Base URL:** `http://127.0.0.1:8000`

**Key Endpoints:**

| Endpoint | Purpose | Example |
|----------|---------|----------|
| `GET /api/dashboard/stats` | Dashboard statistics | Get supplier counts, averages, categories |
| `GET /api/dashboard/suppliers` | All suppliers (paginated) | Get suppliers 0-100 |
| `GET /api/dashboard/suppliers/search?q=lumber` | Search suppliers | Find suppliers by name/category |
| `GET /api/dashboard/suppliers/{id}` | Get supplier details | Get supplier #123 |
| `GET /api/dashboard/categories` | Get all categories | List all 10 categories |

## Data Characteristics

**5000 Suppliers across 10 categories:**
- Lumber & Wood Products (500)
- Concrete & Masonry (500)
- Steel & Metal (500)
- Electrical Supplies (500)
- Plumbing Supplies (500)
- HVAC Equipment (500)
- Roofing Materials (500)
- Windows & Doors (500)
- Paint & Finishes (500)
- Hardware & Fasteners (500)

**Each supplier has:**
- Unique name and contact info
- Products offered
- Ratings and AI scores
- Certifications
- Location, region, size
- Walmart verification status
- And more...

**All data is SEEDED** - Same everywhere, every time!

## Integrating with Your Dashboard

Your existing `supplier-search-engine.html` currently generates supplier data locally. You can optionally update it to fetch from the API:

```javascript
// Instead of generating suppliers locally:
const allSuppliers = generateSuppliers();

// Fetch from API:
fetch('http://127.0.0.1:8000/api/dashboard/suppliers?limit=5000')
  .then(r => r.json())
  .then(data => {
    const allSuppliers = data.suppliers;
    // Rest of your code stays the same!
  });
```

**BUT:** You don't need to change anything! Your dashboard works perfectly as-is.

## Troubleshooting

### Backend won't start
1. Make sure Python is installed: `python --version`
2. Check the backend folder exists: `C:\Users\n0l08i7\Documents\supplier-search-engine\backend`
3. Try running manually: `cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000`

### Can't access the API
1. Make sure the backend is running (you should see "Uvicorn running on...")
2. Wait a few seconds for it to fully start
3. Try visiting: `http://127.0.0.1:8000/health`

### Port 8000 already in use
1. Change the port in START_BACKEND.bat (e.g., 8001)
2. Update your dashboard API calls to use the new port

## Architecture

```
supplier-search-engine.html
         ↓
[Browser - No changes!]
         ↓
/api/dashboard/* endpoints
         ↓
backend/main.py (FastAPI)
         ↓
backend/suppliers_generator.py
         ↓
Seeded Random Generator (seed: 1962)
         ↓
5000 Deterministic Suppliers
```

## What's Next?

1. **Start the backend** with `START_BACKEND.bat`
2. **Open your dashboard** at `file:///C:/Users/n0l08i7/OneDrive%20-%20Walmart%20Inc/Supplier/supplier-search-engine.html`
3. **Your dashboard works unchanged!** All its local data generation continues to work
4. **Optionally update dashboard** to fetch from `/api/dashboard/suppliers` for external data source
5. **Try the API** at `http://127.0.0.1:8000/docs` to explore all endpoints

## Files

- `START_BACKEND.bat` - Quick start script
- `API_DOCUMENTATION.md` - Full API reference
- `backend/suppliers_generator.py` - Supplier generator
- `backend/main.py` - FastAPI application (modified to add new endpoints)

## Support

All endpoints are documented with examples in `API_DOCUMENTATION.md`.

For interactive testing, visit:
```
http://127.0.0.1:8000/docs
```
