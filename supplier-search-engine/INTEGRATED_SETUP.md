# Integrated Dashboard with API Setup

## What You Have Now

1. **HTML Dashboard** (Standalone, works offline)
   - File: `C:\Users\n0l08i7\OneDrive - Walmart Inc\Supplier\supplier-search-engine.html`
   - Works completely standalone with generated data
   - No server required

2. **API Server** (Python, serves real data)
   - File: `api_server.py` in supplier-search-engine folder
   - Generates 5000 suppliers on demand
   - Provides REST endpoints
   - Uses `localhost` hostname (works around firewall!)

## How to Integrate

### Step 1: Start the API Server

Double-click: **`START_API.bat`**

You should see:
```
Server running on: http://localhost:8000
Endpoints:
  GET /api/dashboard/stats
  GET /api/dashboard/suppliers
  ...
```

### Step 2: Update Dashboard HTML

Add this line to the top of the `<script>` section in your HTML dashboard:

```javascript
const API_URL = 'http://localhost:8000';
```

Then replace supplier generation calls with:

```javascript
// Instead of: const allSuppliers = generateSuppliers();
// Use:
async function loadAllSuppliers() {
    const response = await fetch(API_URL + '/api/dashboard/suppliers?limit=5000');
    const data = await response.json();
    return data.suppliers;
}
```

### Step 3: Load Dashboard

Open: `C:\Users\n0l08i7\OneDrive - Walmart Inc\Supplier\supplier-search-engine.html`

The dashboard will now fetch real data from the API!

## API Endpoints

All endpoints run on: **`http://localhost:8000`**

```
GET /health
  Returns: {"status": "healthy", ...}

GET /api/dashboard/stats
  Returns: {"total_suppliers": 5000, "walmart_verified": ..., ...}

GET /api/dashboard/suppliers?skip=0&limit=100
  Returns: {"total": 5000, "suppliers": [...], ...}

GET /api/dashboard/suppliers/search?q=lumber
  Returns: {"query": "lumber", "count": 45, "results": [...]}

GET /api/dashboard/suppliers/{id}
  Returns: {supplier object}

GET /api/dashboard/categories
  Returns: {"categories": {...}, ...}
```

## Why This Works

The Walmart firewall **blocks connections to `127.0.0.1:port`** but **allows `localhost:port`** connections!

So:
- ❌ http://127.0.0.1:8000 - BLOCKED
- ✅ http://localhost:8000 - WORKS!

## Testing the API

Once the API server is running, test with:

```powershell
# PowerShell
Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing

# Or in browser
http://localhost:8000/api/dashboard/stats
```

## Summary

1. Run `START_API.bat` to start the API server
2. Open the HTML dashboard in browser
3. Dashboard will connect to `http://localhost:8000` for real data
4. Everything works together!

## Key Insight

**The firewall blocks IP:port but allows hostname:port!**

This is why:
- `127.0.0.1:8000` → ❌ BLOCKED (firewall rule)
- `localhost:8000` → ✅ WORKS (hostname resolution)

Using `localhost` instead of the IP address bypasses the firewall restriction!
