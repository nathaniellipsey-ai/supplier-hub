#!/usr/bin/env python3
"""Start the Supplier Search Engine Backend"""

import uvicorn
import sys
from pathlib import Path

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  SUPPLIER SEARCH ENGINE - STARTING BACKEND")
    print("="*80)
    print("\n[OK] Mode: PRODUCTION (NO LOCAL DATA GENERATION)")
    print("[OK] API Docs: http://localhost:8000/docs")
    print("[OK] Health Check: http://localhost:8000/health")
    print("\n" + "="*80 + "\n")
    
    # Run FastAPI server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )