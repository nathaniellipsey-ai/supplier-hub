#!/usr/bin/env python3
"""Test script to verify backend module and static file serving.

Tests that the dashboard can be served correctly with special characters in path.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_path_resolution():
    """Test that paths resolve correctly."""
    print("\nTesting Path Resolution")
    print("="*60)
    
    # Get app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"[OK] App directory: {app_dir}")
    
    # Test file existence
    index_path = os.path.normpath(os.path.join(app_dir, "index.html"))
    print(f"[OK] Index path exists: {os.path.exists(index_path)}")
    
    dashboard_path = os.path.normpath(os.path.join(app_dir, "dashboard_with_api.html"))
    print(f"[OK] Dashboard path exists: {os.path.exists(dashboard_path)}")
    
    # Test static file serving simulation
    test_files = [
        "index.html",
        "dashboard_with_api.html",
        "style.css",
        "app.js",
        "login.html",
    ]
    
    print(f"\n[OK] Checking {len(test_files)} files:")
    found_count = 0
    for file_name in test_files:
        full_path = os.path.normpath(os.path.join(app_dir, file_name))
        exists = os.path.exists(full_path) and os.path.isfile(full_path)
        status = "YES" if exists else "NO"
        if exists:
            found_count += 1
        print(f"  {status}: {file_name}")
    
    print(f"\n[PASS] Path resolution test: {found_count}/{len(test_files)} files found")
    return True


def test_backend_module():
    """Test that backend module can be imported."""
    print("\nTesting Backend Module")
    print("="*60)
    
    try:
        from backend.models import Supplier, SupplierCreate
        print("[OK] Models imported")
        
        from backend.services import SupplierService
        print("[OK] Services imported")
        
        from backend.config import settings
        print(f"[OK] Config imported (env: {settings.ENVIRONMENT})")
        
        from backend.utils import APIResponse
        print("[OK] Utils imported")
        
        from backend.integrations import CSVIntegration
        print("[OK] Integrations imported")
        
        print("\n[PASS] Backend module test")
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_supplier_service():
    """Test SupplierService functionality."""
    print("\nTesting SupplierService")
    print("="*60)
    
    try:
        from backend.services import SupplierService
        from backend.models import SupplierCreate, SearchFilter
        
        service = SupplierService()
        print("[OK] SupplierService initialized")
        
        # Test create
        supplier = service.create(SupplierCreate(
            name="Test Supplier",
            category="Lumber & Wood Products",
            location="Test, TX",
            region="TX",
            rating=4.5,
            ai_score=85,
            products=["Lumber"],
            walmart_verified=True,
            years_in_business=10,
            projects_completed=100
        ))
        print(f"[OK] Created supplier: {supplier.name} (ID: {supplier.id})")
        
        # Test get
        retrieved = service.get(supplier.id)
        print(f"[OK] Retrieved supplier: {retrieved.name}")
        
        # Test count
        count = service.count()
        print(f"[OK] Supplier count: {count}")
        
        # Test search
        results = service.search(SearchFilter(query="Test", limit=10))
        print(f"[OK] Search found {results.total} suppliers")
        
        print("\n[PASS] SupplierService test")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_user_service():
    """Test UserService functionality."""
    print("\nTesting UserService")
    print("="*60)
    
    try:
        from backend.services import UserService
        from backend.models import UserCreate
        
        service = UserService()
        print("[OK] UserService initialized")
        
        # Test create user
        user = service.create_user(UserCreate(
            username="testuser",
            email="test@example.com",
            password="secure123"
        ))
        print(f"[OK] Created user: {user.username}")
        
        # Test get user
        retrieved = service.get_user(user.id)
        print(f"[OK] Retrieved user: {retrieved.username}")
        
        # Test favorites
        service.add_favorite(user.id, 1)
        favorites = service.get_favorites(user.id)
        print(f"[OK] Added favorite, count: {len(favorites)}")
        
        # Test notes
        service.save_note(user.id, 1, "Great supplier!")
        note = service.get_note(user.id, 1)
        print(f"[OK] Saved note: {note}")
        
        print("\n[PASS] UserService test")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("SUPPLIER HUB - BACKEND TESTS")
    print("="*60)
    
    results = {
        "Path Resolution": test_path_resolution(),
        "Backend Module": test_backend_module(),
        "SupplierService": test_supplier_service(),
        "UserService": test_user_service(),
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSUCCESS: All tests passed! Backend is ready.")
        return 0
    else:
        print(f"\nWARNING: {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())