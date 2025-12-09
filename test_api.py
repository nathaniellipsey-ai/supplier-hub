#!/usr/bin/env python3
"""Test the API endpoints."""

import json
from app import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("\n" + "="*80)
print("TESTING API ENDPOINTS")
print("="*80 + "\n")

# Test 1: Login
print("[TEST 1] POST /api/auth/login")
response = client.post("/api/auth/login", json={
    "email": "test@example.com",
    "name": "Test User",
    "walmart_id": None
})
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    session_id = response.json()["session_id"]
    print(f"\n[SUCCESS] Login works! Session ID: {session_id}\n")
else:
    print(f"\n[ERROR] Login failed with status {response.status_code}\n")

# Test 2: Get suppliers (should be empty)
print("[TEST 2] GET /api/suppliers")
response = client.get("/api/suppliers")
print(f"Status: {response.status_code}")
data = response.json()
print(f"Total suppliers: {data['total']}")
print(f"Response: {json.dumps(data, indent=2)}")

if data['total'] == 0:
    print("\n[SUCCESS] Database is empty as expected!\n")
else:
    print(f"\n[WARNING] Database has {data['total']} suppliers (should be 0)\n")

# Test 3: Add supplier
print("[TEST 3] POST /api/suppliers/add")
response = client.post("/api/suppliers/add", json={
    "name": "Test Steel Inc",
    "category": "Steel & Metal",
    "location": "Chicago IL",
    "region": "Midwest",
    "rating": 4.5,
    "aiScore": 80,
    "products": ["Steel Beams", "Rebar"],
    "certifications": ["ISO 9001"],
    "walmartVerified": True,
    "yearsInBusiness": 20,
    "projectsCompleted": 500
})
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("\n[SUCCESS] Add supplier works!\n")
else:
    print(f"\n[ERROR] Add supplier failed with status {response.status_code}\n")

# Test 4: Hardware filter
print("[TEST 4] GET /api/suppliers?fixtures_hardware=true")
response = client.get("/api/suppliers?fixtures_hardware=true")
print(f"Status: {response.status_code}")
data = response.json()
print(f"Total with hardware filter: {data['total']}")
print(f"Response: {json.dumps(data, indent=2)}")

print("\n" + "="*80)
print("ALL TESTS COMPLETED")
print("="*80 + "\n")