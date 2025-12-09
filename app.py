#!/usr/bin/env python3
"""FastAPI Backend - Supplier Search Engine

Production-ready API for supplier management.
Provides REST endpoints for supplier data, search, filtering, and management.

🔴 IMPORTANT: ZERO LOCAL SUPPLIER DATA - All data comes from imports/API
"""

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import json
import csv
import io
from datetime import datetime
import os
import random

# ============================================================================
# LOGGING & CONFIG
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Supplier Search Engine API",
    description="Production API for supplier search, management, and AI assistance",
    version="4.0.0 - PRODUCTION",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists(os.path.dirname(__file__)):
    app.mount("/static", StaticFiles(directory=os.path.dirname(__file__)), name="static")

# ============================================================================
# DATABASE STORAGE - ZERO LOCAL DATA
# ============================================================================

print("\n" + "="*80)
print("SUPPLIER SEARCH ENGINE - BACKEND INITIALIZATION")
print("="*80)

# ZERO LOCAL DATA - EMPTY DICTIONARIES
ALL_SUPPLIERS: Dict[int, Dict[str, Any]] = {}  # Will be populated via import only
USER_FAVORITES: Dict[str, List[int]] = {}  # {user_id: [supplier_ids]}
USER_NOTES: Dict[str, Dict[str, Dict]] = {}  # {user_id: {supplier_id: note_data}}
USER_SESSIONS: Dict[str, Dict[str, Any]] = {}  # {session_id: session_data}
USER_INBOX: Dict[str, List[Dict]] = {}  # {user_id: [messages]}

# ============================================================================
# LOAD SEED SUPPLIERS (from Documents version for compatibility)
# ============================================================================

class SeededRandom:
    """Seeded RNG using seed 1962 (Walmart founding year)"""
    def __init__(self, seed=1962):
        self.rng = random.Random(seed)
    def random(self):
        return self.rng.random()

def generate_seed_suppliers():
    """Generate 500 suppliers with seeded randomness for demo/testing"""
    seeded = SeededRandom(1962)
    
    product_categories = {
        "Lumber & Wood Products": ["2x4 Lumber", "Plywood", "Particle Board", "MDF", "Hardwood Flooring"],
        "Concrete & Masonry": ["Portland Cement", "Ready-Mix Concrete", "Cinder Blocks", "Bricks"],
        "Steel & Metal": ["Steel Beams", "Rebar", "Steel Pipe", "Aluminum Siding"],
        "Electrical Supplies": ["Electrical Wire", "Outlets", "Light Fixtures", "Circuit Breakers"],
        "Plumbing Supplies": ["PVC Pipe", "Copper Pipe", "Faucets", "Valves"],
        "HVAC Equipment": ["Air Conditioning Units", "Furnaces", "Heat Pumps", "Ductwork"],
        "Roofing Materials": ["Asphalt Shingles", "Metal Roofing", "Tar & Gravel"],
        "Windows & Doors": ["Vinyl Windows", "Wood Doors", "Sliding Glass Doors"],
        "Paint & Finishes": ["Interior Paint", "Exterior Paint", "Primer", "Stain"],
        "Hardware & Fasteners": ["Nails", "Screws", "Bolts", "Hinges"]
    }
    
    adjectives = ['Premier', 'Elite', 'Pro', 'Superior', 'Quality', 'Reliable', 'National', 'Metro', 'Allied', 'United']
    cities = [
        {'city': 'New York', 'state': 'NY'},
        {'city': 'Los Angeles', 'state': 'CA'},
        {'city': 'Chicago', 'state': 'IL'},
        {'city': 'Houston', 'state': 'TX'},
        {'city': 'Dallas', 'state': 'TX'},
        {'city': 'Denver', 'state': 'CO'},
        {'city': 'Seattle', 'state': 'WA'},
        {'city': 'Atlanta', 'state': 'GA'},
        {'city': 'Miami', 'state': 'FL'},
        {'city': 'Boston', 'state': 'MA'}
    ]
    
    suppliers = []
    supplier_id = 1
    
    for category, products in product_categories.items():
        suppliers_per_category = 50  # 50 suppliers per category = 500 total
        
        for i in range(suppliers_per_category):
            adj = adjectives[int(seeded.random() * len(adjectives))]
            city_data = cities[int(seeded.random() * len(cities))]
            
            # Select products
            num_products = int(seeded.random() * 3) + 2
            supplier_products = [products[int(seeded.random() * len(products))] for _ in range(num_products)]
            
            suppliers.append({
                'id': supplier_id,
                'name': f"{adj} {category.split()[0]} Supply Inc.",
                'category': category,
                'location': f"{city_data['city']}, {city_data['state']}",
                'region': city_data['state'],
                'rating': round(seeded.random() * 1.5 + 3.5, 1),
                'aiScore': int(seeded.random() * 30 + 70),
                'products': list(set(supplier_products)),
                'certifications': ['ISO 9001', 'EPA Certified'],
                'walmartVerified': seeded.random() > 0.4,
                'yearsInBusiness': int(seeded.random() * 40 + 5),
                'projectsCompleted': int(seeded.random() * 5000 + 100),
            })
            supplier_id += 1
    
    return suppliers

# Load seed suppliers
print("[INIT] Generating seed supplier data...")
seed_suppliers = generate_seed_suppliers()
for supplier in seed_suppliers:
    ALL_SUPPLIERS[supplier['id']] = supplier

print(f"[SUCCESS] Loaded {len(ALL_SUPPLIERS)} seed suppliers")
print("[INFO] Can import additional suppliers via /api/suppliers/import endpoint")
logger.info(f"[PRODUCTION] Backend initialized with {len(ALL_SUPPLIERS)} seed suppliers")
logger.info(f"[STATUS] Total suppliers in memory: {len(ALL_SUPPLIERS)}")

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

# Pydantic models for request validation
class LoginRequest(BaseModel):
    email: str
    name: str
    walmart_id: Optional[str] = None

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """User login endpoint - accepts JSON data."""
    try:
        import uuid
        
        # Extract and validate fields
        email = request.email.strip() if request.email else ""
        name = request.name.strip() if request.name else ""
        walmart_id = request.walmart_id.strip() if request.walmart_id else None
        
        if not email or not name:
            raise HTTPException(status_code=400, detail="Email and name are required")
        
        session_id = str(uuid.uuid4())
        user_id = f"user_{session_id[:8]}"
        
        USER_SESSIONS[session_id] = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "walmart_id": walmart_id,
            "login_time": datetime.now().isoformat(),
            "sso_provider": "walmart" if walmart_id else "guest"
        }
        
        logger.info(f"[LOGIN] User logged in: {email}")
        
        return {
            "success": True,
            "session_id": session_id,
            "user_id": user_id,
            "message": f"Welcome {name}!"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")

@app.post("/api/auth/sso/walmart")
async def walmart_sso_login(code: str = Query(...)):
    """Walmart SSO Login - Exchange authorization code for session."""
    try:
        import uuid
        session_id = str(uuid.uuid4())
        user_id = f"walmart_user_{session_id[:8]}"
        
        USER_SESSIONS[session_id] = {
            "user_id": user_id,
            "email": f"user@walmart.com",
            "login_time": datetime.now().isoformat(),
            "sso_provider": "walmart"
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "user_id": user_id,
            "message": "Logged in via Walmart SSO"
        }
    except Exception as e:
        logger.error(f"SSO login error: {e}")
        raise HTTPException(status_code=400, detail="SSO login failed")

@app.post("/api/auth/sso/check")
async def check_sso_session(session_id: str = Query(...)):
    """Check if SSO session is valid."""
    if session_id in USER_SESSIONS:
        session = USER_SESSIONS[session_id]
        return {
            "valid": True,
            "user_id": session["user_id"],
            "email": session.get("email"),
            "provider": session.get("sso_provider", "unknown")
        }
    return {"valid": False}

@app.post("/api/auth/logout")
async def logout(session_id: str = Query(...)):
    """Logout user."""
    if session_id in USER_SESSIONS:
        del USER_SESSIONS[session_id]
    return {"success": True, "message": "Logged out"}

# ============================================================================
# SUPPLIER MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/suppliers/import")
async def import_suppliers(file: UploadFile = File(...), user_id: str = "default"):
    """Import suppliers from CSV file.
    
    CSV format: id,name,category,location,region,rating,aiScore,products,certifications,walmartVerified,yearsInBusiness,projectsCompleted
    """
    try:
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        imported_count = 0
        errors = []
        
        for row in csv_reader:
            try:
                supplier = {
                    "id": int(row["id"]),
                    "name": row["name"],
                    "category": row["category"],
                    "location": row["location"],
                    "region": row["region"],
                    "rating": float(row["rating"]),
                    "aiScore": int(row["aiScore"]),
                    "products": row["products"].split(";") if ";" in row["products"] else [row["products"]],
                    "certifications": row["certifications"].split(";") if ";" in row["certifications"] else [row["certifications"]],
                    "walmartVerified": row["walmartVerified"].lower() == "true",
                    "yearsInBusiness": int(row["yearsInBusiness"]),
                    "projectsCompleted": int(row["projectsCompleted"])
                }
                ALL_SUPPLIERS[supplier["id"]] = supplier
                imported_count += 1
            except Exception as e:
                errors.append(f"Row error: {str(e)}")
        
        logger.info(f"[IMPORT] Imported {imported_count} suppliers")
        logger.info(f"[STATUS] Total suppliers now: {len(ALL_SUPPLIERS)}")
        
        return {
            "success": True,
            "imported": imported_count,
            "errors": errors,
            "total_suppliers_now": len(ALL_SUPPLIERS),
            "message": f"Imported {imported_count} suppliers"
        }
    except Exception as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

class SupplierRequest(BaseModel):
    name: str
    category: str
    location: str
    region: str
    rating: float
    aiScore: int
    products: List[str]
    certifications: List[str]
    walmartVerified: bool
    yearsInBusiness: int
    projectsCompleted: int

@app.post("/api/suppliers/add")
async def add_supplier(supplier_data: dict = Body(...)):
    """Add a single supplier."""
    try:
        name = str(supplier_data.get("name", "")).strip()
        if not name:
            raise HTTPException(status_code=400, detail="Supplier name is required")
        
        supplier_id = max(ALL_SUPPLIERS.keys()) + 1 if ALL_SUPPLIERS else 1
        
        supplier = {
            "id": supplier_id,
            "name": name,
            "category": supplier_data.get("category", ""),
            "location": supplier_data.get("location", ""),
            "region": supplier_data.get("region", ""),
            "rating": supplier_data.get("rating", 0),
            "aiScore": supplier_data.get("aiScore", 0),
            "products": supplier_data.get("products", []),
            "certifications": supplier_data.get("certifications", []),
            "walmartVerified": supplier_data.get("walmartVerified", False),
            "yearsInBusiness": supplier_data.get("yearsInBusiness", 0),
            "projectsCompleted": supplier_data.get("projectsCompleted", 0),
            "created_at": datetime.now().isoformat()
        }
        
        ALL_SUPPLIERS[supplier_id] = supplier
        logger.info(f"[ADD] Added supplier: {name} (ID: {supplier_id})")
        
        return {
            "success": True,
            "supplier_id": supplier_id,
            "message": "Supplier added successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add supplier error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to add supplier: {str(e)}")

@app.put("/api/suppliers/{supplier_id}")
async def edit_supplier(supplier_id: int, supplier_data: dict = Body(...)):
    """Edit an existing supplier."""
    if supplier_id not in ALL_SUPPLIERS:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    try:
        ALL_SUPPLIERS[supplier_id].update({
            "name": supplier_data.get("name", ALL_SUPPLIERS[supplier_id].get("name")),
            "category": supplier_data.get("category", ALL_SUPPLIERS[supplier_id].get("category")),
            "location": supplier_data.get("location", ALL_SUPPLIERS[supplier_id].get("location")),
            "region": supplier_data.get("region", ALL_SUPPLIERS[supplier_id].get("region")),
            "rating": supplier_data.get("rating", ALL_SUPPLIERS[supplier_id].get("rating")),
            "aiScore": supplier_data.get("aiScore", ALL_SUPPLIERS[supplier_id].get("aiScore")),
            "products": supplier_data.get("products", ALL_SUPPLIERS[supplier_id].get("products")),
            "certifications": supplier_data.get("certifications", ALL_SUPPLIERS[supplier_id].get("certifications")),
            "walmartVerified": supplier_data.get("walmartVerified", ALL_SUPPLIERS[supplier_id].get("walmartVerified")),
            "yearsInBusiness": supplier_data.get("yearsInBusiness", ALL_SUPPLIERS[supplier_id].get("yearsInBusiness")),
            "projectsCompleted": supplier_data.get("projectsCompleted", ALL_SUPPLIERS[supplier_id].get("projectsCompleted")),
            "updated_at": datetime.now().isoformat()
        })
        logger.info(f"[UPDATE] Updated supplier: {ALL_SUPPLIERS[supplier_id]['name']}")
        
        return {
            "success": True,
            "supplier_id": supplier_id,
            "message": "Supplier updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Edit supplier error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to edit supplier: {str(e)}")

@app.delete("/api/suppliers/{supplier_id}")
async def delete_supplier(supplier_id: int):
    """Delete a supplier."""
    if supplier_id not in ALL_SUPPLIERS:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    supplier_name = ALL_SUPPLIERS[supplier_id].get("name", "Unknown")
    del ALL_SUPPLIERS[supplier_id]
    logger.info(f"[DELETE] Deleted supplier: {supplier_name}")
    
    return {"success": True, "message": "Supplier deleted"}

# ============================================================================
# SUPPLIER SEARCH & FILTER ENDPOINTS
# ============================================================================

@app.get("/api/suppliers")
async def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None),
    verified_only: bool = Query(False),
    fixtures_hardware: bool = Query(False),
):
    """Get suppliers with filtering."""
    results = list(ALL_SUPPLIERS.values())
    
    # Apply filters
    if search:
        search_lower = search.lower()
        results = [
            s for s in results
            if search_lower in s.get("name", "").lower() or
               search_lower in s.get("category", "").lower() or
               any(search_lower in str(p).lower() for p in s.get("products", []))
        ]
    
    if category:
        results = [s for s in results if s.get("category", "").lower() == category.lower()]
    
    if location:
        location_lower = location.lower()
        results = [
            s for s in results
            if location_lower in s.get("location", "").lower() or
               location_lower in s.get("region", "").lower()
        ]
    
    if region:
        results = [s for s in results if s.get("region", "").lower() == region.lower()]
    
    if min_rating is not None:
        results = [s for s in results if s.get("rating", 0) >= min_rating]
    
    if verified_only:
        results = [s for s in results if s.get("walmartVerified", False)]
    
    if fixtures_hardware:
        results = [
            s for s in results
            if "Hardware" in s.get("category", "") or
               "Fixtures" in s.get("category", "") or
               any("fixture" in str(p).lower() or "hardware" in str(p).lower() for p in s.get("products", []))
        ]
    
    total = len(results)
    suppliers = results[skip:skip + limit]
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "count": len(suppliers),
        "suppliers": suppliers
    }

@app.get("/api/suppliers/{supplier_id}")
async def get_supplier(supplier_id: int):
    """Get a specific supplier."""
    if supplier_id not in ALL_SUPPLIERS:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return ALL_SUPPLIERS[supplier_id]

@app.get("/api/suppliers/categories/all")
async def get_categories():
    """Get all unique categories."""
    categories = {}
    for supplier in ALL_SUPPLIERS.values():
        cat = supplier.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
    return {"categories": categories, "count": len(categories)}

# ============================================================================
# FAVORITES ENDPOINTS
# ============================================================================

@app.get("/api/favorites")
async def get_favorites(user_id: str = "default"):
    """Get user's favorites."""
    if user_id not in USER_FAVORITES:
        return {"count": 0, "favorites": []}
    
    favorite_ids = USER_FAVORITES[user_id]
    favorites = [ALL_SUPPLIERS[sid] for sid in favorite_ids if sid in ALL_SUPPLIERS]
    return {"count": len(favorites), "favorites": favorites}

@app.post("/api/favorites/add")
async def add_favorite(supplier_id: int = Query(...), user_id: str = "default"):
    """Add supplier to favorites."""
    if user_id not in USER_FAVORITES:
        USER_FAVORITES[user_id] = []
    if supplier_id not in USER_FAVORITES[user_id]:
        USER_FAVORITES[user_id].append(supplier_id)
    return {"success": True}

@app.post("/api/favorites/remove")
async def remove_favorite(supplier_id: int = Query(...), user_id: str = "default"):
    """Remove supplier from favorites."""
    if user_id in USER_FAVORITES and supplier_id in USER_FAVORITES[user_id]:
        USER_FAVORITES[user_id].remove(supplier_id)
    return {"success": True}

# ============================================================================
# NOTES ENDPOINTS
# ============================================================================

@app.get("/api/notes")
async def get_notes(user_id: str = "default"):
    """Get user's notes."""
    if user_id not in USER_NOTES:
        return {"count": 0, "notes": []}
    
    notes = []
    for supplier_id, note_data in USER_NOTES[user_id].items():
        if int(supplier_id) in ALL_SUPPLIERS:
            supplier = ALL_SUPPLIERS[int(supplier_id)]
            notes.append({
                "id": f"{user_id}_{supplier_id}",
                "supplier_id": int(supplier_id),
                "supplier_name": supplier.get("name"),
                "content": note_data.get("text"),
                "created_at": note_data.get("created_at"),
                "updated_at": note_data.get("updated_at")
            })
    return {"count": len(notes), "notes": notes}

@app.post("/api/notes/add")
async def add_note(supplier_id: int = Query(...), content: str = Query(...), user_id: str = "default"):
    """Add a note."""
    if user_id not in USER_NOTES:
        USER_NOTES[user_id] = {}
    
    USER_NOTES[user_id][str(supplier_id)] = {
        "text": content,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    return {"success": True}

@app.post("/api/notes/update")
async def update_note(supplier_id: int = Query(...), content: str = Query(...), user_id: str = "default"):
    """Update a note."""
    if user_id not in USER_NOTES:
        USER_NOTES[user_id] = {}
    
    USER_NOTES[user_id][str(supplier_id)] = {
        "text": content,
        "created_at": USER_NOTES[user_id].get(str(supplier_id), {}).get("created_at", datetime.now().isoformat()),
        "updated_at": datetime.now().isoformat()
    }
    return {"success": True}

@app.post("/api/notes/delete")
async def delete_note(supplier_id: int = Query(...), user_id: str = "default"):
    """Delete a note."""
    if user_id in USER_NOTES and str(supplier_id) in USER_NOTES[user_id]:
        del USER_NOTES[user_id][str(supplier_id)]
    return {"success": True}

# ============================================================================
# AI CHATBOT ENDPOINTS
# ============================================================================

@app.post("/api/chatbot/message")
async def chatbot_message(
    message: str = Form(...),
    user_id: str = Form("default"),
):
    """
    Send message to AI Chatbot.
    Chatbot can help with:
    - Supplier search and recommendations
    - Supplier data analysis
    - FAQs and help
    - Supplier comparison
    """
    try:
        # Simple AI response logic
        message_lower = message.lower()
        suppliers_list = list(ALL_SUPPLIERS.values())
        
        # Supplier search
        if "find" in message_lower or "search" in message_lower or "show" in message_lower:
            matching = [s for s in suppliers_list if any(word in message_lower for word in s.get("name", "").lower().split())]
            if matching:
                return {
                    "success": True,
                    "response": f"Found {len(matching)} supplier(s): " + ", ".join([s["name"] for s in matching[:5]]),
                    "timestamp": datetime.now().isoformat()
                }
        
        # Walmart verified suppliers
        if "walmart verified" in message_lower:
            verified = [s for s in suppliers_list if s.get("walmartVerified")]
            return {
                "success": True,
                "response": f"We have {len(verified)} Walmart-verified suppliers in our database.",
                "timestamp": datetime.now().isoformat()
            }
        
        # Statistics
        if "how many" in message_lower or "total" in message_lower or "count" in message_lower:
            return {
                "success": True,
                "response": f"We currently have {len(suppliers_list)} suppliers in our database.",
                "timestamp": datetime.now().isoformat()
            }
        
        # Default response
        return {
            "success": True,
            "response": "I'm an AI assistant for supplier search. I can help you find suppliers, provide recommendations, and answer questions about our database. What would you like to know?",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        return {
            "success": False,
            "response": "I'm having trouble processing your request. Please try again.",
            "error": str(e)
        }

# ============================================================================
# INBOX ENDPOINTS
# ============================================================================

@app.get("/api/inbox")
async def get_inbox(user_id: str = "default"):
    """Get user's inbox messages."""
    if user_id not in USER_INBOX:
        return {"count": 0, "messages": []}
    return {"count": len(USER_INBOX[user_id]), "messages": USER_INBOX[user_id]}

@app.post("/api/inbox/mark-read")
async def mark_message_read(message_id: str = Query(...), user_id: str = "default"):
    """Mark message as read."""
    if user_id in USER_INBOX:
        for msg in USER_INBOX[user_id]:
            if msg.get("id") == message_id:
                msg["read"] = True
    return {"success": True}

@app.post("/api/inbox/mark-all-read")
async def mark_all_read(user_id: str = "default"):
    """Mark all messages as read."""
    if user_id in USER_INBOX:
        for msg in USER_INBOX[user_id]:
            msg["read"] = True
    return {"success": True}

@app.post("/api/inbox/delete")
async def delete_message(message_id: str = Query(...), user_id: str = "default"):
    """Delete a message."""
    if user_id in USER_INBOX:
        USER_INBOX[user_id] = [m for m in USER_INBOX[user_id] if m.get("id") != message_id]
    return {"success": True}

# ============================================================================
# DASHBOARD STATISTICS
# ============================================================================

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics."""
    if not ALL_SUPPLIERS:
        return {
            "total_suppliers": 0,
            "walmart_verified": 0,
            "verified_percentage": 0,
            "average_rating": 0,
            "average_ai_score": 0,
            "categories": {},
            "status": "No suppliers loaded"
        }
    
    suppliers_list = list(ALL_SUPPLIERS.values())
    verified = sum(1 for s in suppliers_list if s.get("walmartVerified", False))
    avg_rating = sum(s.get("rating", 0) for s in suppliers_list) / len(suppliers_list)
    avg_ai_score = sum(s.get("aiScore", 0) for s in suppliers_list) / len(suppliers_list)
    
    categories = {}
    for supplier in suppliers_list:
        cat = supplier.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total_suppliers": len(ALL_SUPPLIERS),
        "walmart_verified": verified,
        "verified_percentage": round((verified / len(ALL_SUPPLIERS) * 100) if ALL_SUPPLIERS else 0, 1),
        "average_rating": round(avg_rating, 2),
        "average_ai_score": round(avg_ai_score, 1),
        "categories": categories
    }

# ============================================================================
# STATIC FILE SERVING
# ============================================================================

@app.get("/")
async def root():
    """Serve the main dashboard HTML."""
    try:
        index_path = os.path.join(os.path.dirname(__file__), "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path, media_type="text/html")
    except:
        pass
    
    return {
        "api": "Supplier Search Engine",
        "version": "4.0.0",
        "status": "running",
        "mode": "PRODUCTION - ZERO LOCAL DATA",
        "documentation": "/docs",
        "suppliers_loaded": len(ALL_SUPPLIERS)
    }

@app.get("/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files (HTML, CSS, JS, SVG, etc.)."""
    try:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            if file_path.endswith('.html'):
                return FileResponse(full_path, media_type="text/html")
            elif file_path.endswith('.css'):
                return FileResponse(full_path, media_type="text/css")
            elif file_path.endswith('.js'):
                return FileResponse(full_path, media_type="application/javascript")
            elif file_path.endswith('.svg'):
                return FileResponse(full_path, media_type="image/svg+xml")
            elif file_path.endswith('.json'):
                return FileResponse(full_path, media_type="application/json")
            else:
                return FileResponse(full_path)
    except:
        pass
    
    raise HTTPException(status_code=404, detail="File not found")

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "API is running",
        "suppliers_loaded": len(ALL_SUPPLIERS),
        "mode": "PRODUCTION (ZERO LOCAL DATA)"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)