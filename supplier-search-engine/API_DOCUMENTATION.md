# Supplier Search Engine - API Documentation

## Overview

This API provides backend services for the Supplier Search Engine dashboard (`supplier-search-engine.html`). The API generates 5000 suppliers using a seeded random number generator (seed: 1962 - Walmart's founding year) to ensure consistent, reproducible data.

## Quick Start

### 1. Start the Backend

**Option A: Double-click the batch file**
```
START_BACKEND.bat
```

**Option B: Run in PowerShell/CMD**
```powershell
cd C:\Users\n0l08i7\Documents\supplier-search-engine
.\START_BACKEND.bat
```

**Option C: Manual**
```powershell
cd C:\Users\n0l08i7\Documents\supplier-search-engine\backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Access the API

**Interactive API Explorer (Swagger UI):**
```
http://127.0.0.1:8000/docs
```

**Health Check:**
```
http://127.0.0.1:8000/health
```

## Dashboard API Endpoints

All endpoints return 5000 seeded suppliers with consistent data across all sessions.

### Get Dashboard Statistics
```
GET /api/dashboard/stats
```

**Response:**
```json
{
  "total_suppliers": 5000,
  "walmart_verified": 1423,
  "verified_percentage": 28.5,
  "average_rating": 4.2,
  "average_ai_score": 80.1,
  "categories": {
    "Lumber & Wood Products": 500,
    "Concrete & Masonry": 500,
    ...
  },
  "regions": {
    "Northeast": 625,
    "Midwest": 625,
    ...
  },
  "total_categories": 10,
  "total_regions": 4
}
```

### Get All Suppliers (Paginated)
```
GET /api/dashboard/suppliers?skip=0&limit=100
```

**Query Parameters:**
- `skip` (int, default: 0) - Number of suppliers to skip
- `limit` (int, default: 100, max: 500) - Number of suppliers to return

**Response:**
```json
{
  "total": 5000,
  "skip": 0,
  "limit": 100,
  "suppliers": [
    {
      "id": 1,
      "name": "Premier Lumber Inc.",
      "category": "Lumber & Wood Products",
      "location": "New York, NY",
      "rating": 4.5,
      "aiScore": 85,
      "walmartVerified": true,
      "website": "https://www.premierlumber.com",
      "email": "sales@premierlumber.com",
      "phone": "(555) 123-4567",
      "products": ["2x4 Lumber", "Plywood"],
      "certifications": ["ISO 9001"],
      "size": "Large (251-1000)",
      "priceRange": "Mid-Range ($$)",
      "yearsInBusiness": 25,
      "projectsCompleted": 3421,
      "employees": 450,
      "responseTime": "4 hours",
      "minOrder": "$5,000",
      "paymentTerms": "Net 30"
    },
    ...
  ]
}
```

### Search Suppliers
```
GET /api/dashboard/suppliers/search?q=lumber
```

**Query Parameters:**
- `q` (string, required) - Search query (name or category)

**Response:**
```json
{
  "query": "lumber",
  "count": 45,
  "results": [
    {
      "id": 1,
      "name": "Premier Lumber Inc.",
      ...
    },
    ...
  ]
}
```

### Get Supplier by ID
```
GET /api/dashboard/suppliers/123
```

**Response:**
```json
{
  "id": 123,
  "name": "Premier Lumber Inc.",
  "category": "Lumber & Wood Products",
  ...
}
```

### Get Suppliers by Category
```
GET /api/dashboard/suppliers/by-category?category=Lumber%20%26%20Wood%20Products
```

**Query Parameters:**
- `category` (string, required) - The category name

**Response:**
```json
{
  "category": "Lumber & Wood Products",
  "count": 500,
  "results": [...]
}
```

### Get All Categories
```
GET /api/dashboard/categories
```

**Response:**
```json
{
  "categories": {
    "Lumber & Wood Products": 500,
    "Concrete & Masonry": 500,
    "Steel & Metal": 500,
    "Electrical Supplies": 500,
    "Plumbing Supplies": 500,
    "HVAC Equipment": 500,
    "Roofing Materials": 500,
    "Windows & Doors": 500,
    "Paint & Finishes": 500,
    "Hardware & Fasteners": 500
  },
  "total_categories": 10
}
```

## Using with the Dashboard

The HTML dashboard (`supplier-search-engine.html`) can be updated to use these API endpoints instead of generating data locally. Update your dashboard JavaScript to fetch from:

```javascript
// Get all suppliers
fetch('http://127.0.0.1:8000/api/dashboard/suppliers')
  .then(r => r.json())
  .then(data => {
    const suppliers = data.suppliers; // Array of supplier objects
    // Use suppliers...
  });

// Get statistics
fetch('http://127.0.0.1:8000/api/dashboard/stats')
  .then(r => r.json())
  .then(stats => {
    document.getElementById('totalSuppliersCount').textContent = stats.total_suppliers;
    document.getElementById('verifiedCount').textContent = stats.walmart_verified;
  });

// Search suppliers
fetch('http://127.0.0.1:8000/api/dashboard/suppliers/search?q=lumber')
  .then(r => r.json())
  .then(results => console.log(results));
```

## Data Structure

Each supplier object contains:

```typescript
interface Supplier {
  id: number;                      // Unique supplier ID
  name: string;                    // Supplier name
  description: string;             // About the supplier
  website: string;                 // Website URL
  email: string;                   // Contact email
  phone: string;                   // Contact phone
  address: string;                 // Street address
  city: string;                    // City
  state: string;                   // State code (e.g., "NY")
  category: string;                // Product category
  products: string[];              // Products offered
  location: string;                // "City, State"
  region: string;                  // Geographic region
  rating: number;                  // 3.5-5.0 star rating
  aiScore: number;                 // 70-100 AI match score
  certifications: string[];        // ISO, OSHA, etc.
  size: string;                    // Company size category
  priceRange: string;              // $ to $$$$ 
  yearsInBusiness: number;         // Years operating
  projectsCompleted: number;       // Total projects
  walmartVerified: boolean;        // Walmart verification
  employees: number;               // Employee count
  responseTime: string;            // Response time (e.g., "4 hours")
  minOrder: string;                // Minimum order amount
  paymentTerms: string;            // Payment terms
}
```

## Seeded Data

All supplier data is generated using a seeded random number generator with seed `1962` (Walmart's founding year). This means:

✅ **Consistent:** The same 5000 suppliers are generated every time  
✅ **Reproducible:** All users see identical data  
✅ **Realistic:** Suppliers have varied names, locations, ratings, etc.  
✅ **Deterministic:** No external API calls or database required  

## Error Handling

All endpoints return standard HTTP status codes:

- `200` - Success
- `404` - Supplier/Category not found
- `400` - Invalid query parameters
- `500` - Server error

## CORS

The API has CORS enabled for:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:8080`
- `http://localhost:8080`

You can add more origins as needed by modifying `main.py`.

## Example curl Commands

```bash
# Get stats
curl http://127.0.0.1:8000/api/dashboard/stats

# Get all suppliers (first 10)
curl http://127.0.0.1:8000/api/dashboard/suppliers?skip=0&limit=10

# Search suppliers
curl "http://127.0.0.1:8000/api/dashboard/suppliers/search?q=lumber"

# Get supplier by ID
curl http://127.0.0.1:8000/api/dashboard/suppliers/1

# Get categories
curl http://127.0.0.1:8000/api/dashboard/categories
```

## Health Check

```
GET /health

Response:
{
  "status": "healthy",
  "message": "Supplier Search Engine API is running",
  "version": "1.0.0"
}
```

## Interactive API Docs

Once the backend is running, visit:
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

These provide interactive documentation where you can test endpoints directly in your browser.
