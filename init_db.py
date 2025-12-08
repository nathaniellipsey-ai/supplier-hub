"""Database initialization script for Supplier Search Engine.

This script initializes a fresh SQLite database with the proper schema.
"""

import sys
from pathlib import Path
from database import SupplierDatabase


def main():
    """Initialize the database."""
    print("[INIT] Initializing Supplier Search Engine Database...")
    
    db = SupplierDatabase()
    db.init_schema()
    
    print(f"[SUCCESS] Database initialized at: {Path(db.db_path).absolute()}")
    print("\n[SCHEMA] Schema created with the following tables:")
    print("   - suppliers: Main supplier information")
    print("   - products: Products offered by suppliers")
    print("   - search_history: Search query logs for analytics")
    print("\n[INDEX] Indexes created for optimal search performance")
    print("\n[NEXT] Next steps:")
    print("   1. Use cli.py to add suppliers and products")
    print("   2. Search for suppliers in the database")
    print("   3. View dashboard statistics")


if __name__ == "__main__":
    main()
