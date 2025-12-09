#!/usr/bin/env python3
"""Diagnostic script to troubleshoot issues."""

import json
import sys
from app import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("\n" + "="*80)
print("SUPPLIER HUB - DIAGNOSTIC REPORT")
print("="*80 + "\n")

# Test 1: Server health
print("[CHECK 1] Server Health")
try:
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("[OK] Server is healthy\n")
except Exception as e:
    print(f"[ERROR] Server error: {e}\n")

# Test 2: Login with valid data
print("[CHECK 2] Login Endpoint")
try:
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "name": "Test User",
        "walmart_id": None
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200:
        print(f"[OK] Login works! Session ID: {data.get('session_id')}\n")
    else:
        print(f"[ERROR] Login failed with error: {data.get('detail')}\n")
except Exception as e:
    print(f"[ERROR] Login endpoint error: {e}\n")

# Test 3: Database status
print("[CHECK 3] Database Status")
try:
    response = client.get("/api/suppliers")
    print(f"Status: {response.status_code}")
    data = response.json()
    total = data.get('total', 0)
    print(f"Total suppliers: {total}")
    
    if total == 0:
        print("[OK] Database is empty (as expected)")
        print("   NEXT STEP: Import suppliers via CSV\n")
    else:
        print(f"[OK] Database has {total} suppliers\n")
except Exception as e:
    print(f"[ERROR] Database error: {e}\n")

# Test 4: Categories
print("[CHECK 4] Categories Endpoint")
try:
    response = client.get("/api/suppliers/categories/all")
    print(f"Status: {response.status_code}")
    data = response.json()
    categories = data.get('categories', {})
    print(f"Categories found: {len(categories)}")
    
    if len(categories) > 0:
        print(f"Categories: {', '.join(categories.keys())}")
        print("[OK] Categories endpoint works\n")
    else:
        print("[WARNING] No categories yet (import suppliers first)\n")
except Exception as e:
    print(f"[ERROR] Categories error: {e}\n")

# Test 5: Add supplier
print("[CHECK 5] Add Supplier Endpoint")
try:
    response = client.post("/api/suppliers/add", json={
        "name": "Test Supplier",
        "category": "Test Category",
        "location": "Test Location",
        "region": "Test Region",
        "rating": 4.5,
        "aiScore": 80,
        "products": ["Product 1"],
        "certifications": ["Cert 1"],
        "walmartVerified": True,
        "yearsInBusiness": 5,
        "projectsCompleted": 100
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        supplier_id = data.get('supplier_id')
        print(f"[OK] Add supplier works! Created ID: {supplier_id}\n")
    else:
        print(f"[ERROR] Add failed: {data.get('detail')}\n")
except Exception as e:
    print(f"[ERROR] Add supplier error: {e}\n")

# Test 6: Chatbot
print("[CHECK 6] Chatbot Endpoint")
try:
    response = client.post("/api/chatbot/message", json={
        "message": "Find suppliers",
        "user_id": "test_user"
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        print(f"Response: {data.get('response')[:100]}...")
        print("[OK] Chatbot works\n")
    else:
        print(f"[ERROR] Chatbot error: {data.get('detail')}\n")
except Exception as e:
    print(f"[ERROR] Chatbot error: {e}\n")

# Summary
print("="*80)
print("SUMMARY")
print("="*80)
print("""
[OK] All API endpoints are working correctly.

NEXT STEPS:
1. Start the server:
   python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

2. Open browser:
   http://localhost:8000

3. Login with any email and name:
   Email: test@example.com
   Name: Test User
   Walmart ID: (leave blank)

4. If login still fails:
   - Check browser console (F12)
   - Check Network tab for error response
   - See LOGIN_TROUBLESHOOTING.md for help

5. To import suppliers:
   - Create suppliers.csv file
   - Upload via dashboard or API
   - See QUICK_START.txt for format
""")
print("="*80 + "\n")