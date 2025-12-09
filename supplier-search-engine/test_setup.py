#!/usr/bin/env python3
"""Test that the API setup is working correctly."""

import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("\n" + "="*70)
print(" TESTING SUPPLIER SEARCH ENGINE SETUP")
print("="*70 + "\n")

# Test 1: Import supplier generator
print("[TEST 1] Importing SupplierGenerator...")
try:
    from suppliers_generator import SupplierGenerator
    print("  [OK] SupplierGenerator imported successfully\n")
except Exception as e:
    print(f"  [FAIL] Error importing: {e}\n")
    sys.exit(1)

# Test 2: Generate suppliers
print("[TEST 2] Generating 5000 suppliers...")
try:
    generator = SupplierGenerator()
    suppliers = generator.generate_suppliers()
    print(f"  [OK] Generated {len(suppliers)} suppliers\n")
except Exception as e:
    print(f"  [FAIL] Error generating: {e}\n")
    sys.exit(1)

# Test 3: Verify supplier data
print("[TEST 3] Verifying supplier data...")
try:
    if len(suppliers) != 5000:
        raise Exception(f"Expected 5000 suppliers, got {len(suppliers)}")
    
    first_supplier = suppliers[0]
    required_fields = ['id', 'name', 'category', 'rating', 'aiScore', 'walmartVerified', 'products']
    for field in required_fields:
        if field not in first_supplier:
            raise Exception(f"Missing field: {field}")
    
    print(f"  [OK] Supplier data is complete\n")
except Exception as e:
    print(f"  [FAIL] {e}\n")
    sys.exit(1)

# Test 4: Check API files exist
print("[TEST 4] Checking required files...")
try:
    files = [
        'api_server.py',
        'START_API.bat',
        'dashboard_with_api.html',
        'INTEGRATED_SETUP.md',
        'API_INTEGRATION_COMPLETE.md'
    ]
    
    base_dir = os.path.dirname(__file__)
    for file in files:
        filepath = os.path.join(base_dir, file)
        if not os.path.exists(filepath):
            raise Exception(f"Missing file: {file}")
    
    print(f"  [OK] All required files present\n")
except Exception as e:
    print(f"  [FAIL] {e}\n")
    sys.exit(1)

# Test 5: Verify HTML file
print("[TEST 5] Checking HTML dashboard...")
try:
    html_file = r'C:\Users\n0l08i7\OneDrive - Walmart Inc\Supplier\supplier-search-engine.html'
    if not os.path.exists(html_file):
        raise Exception(f"Original HTML not found at: {html_file}")
    
    api_html_file = os.path.join(base_dir, 'dashboard_with_api.html')
    if not os.path.exists(api_html_file):
        raise Exception(f"API-integrated HTML not found at: {api_html_file}")
    
    print(f"  [OK] Both HTML dashboards found\n")
except Exception as e:
    print(f"  [FAIL] {e}\n")
    sys.exit(1)

# Test 6: Verify sample supplier data
print("[TEST 6] Checking sample supplier data...")
try:
    first = suppliers[0]
    print(f"  Supplier 1:")
    print(f"    Name: {first['name']}")
    print(f"    Category: {first['category']}")
    print(f"    Rating: {first['rating']}")
    print(f"    AI Score: {first['aiScore']}")
    print(f"    Walmart Verified: {first['walmartVerified']}")
    print(f"  [OK] Sample data looks good\n")
except Exception as e:
    print(f"  [FAIL] {e}\n")
    sys.exit(1)

# Summary
print("="*70)
print(" ALL TESTS PASSED! ✓")
print("="*70)
print("\nSetup is complete and ready to use!\n")
print("Next steps:")
print("1. Run: START_API.bat (or python api_server.py)")
print("2. Open: dashboard_with_api.html in browser")
print("3. API will be available at: http://localhost:8000\n")
print("="*70 + "\n")
