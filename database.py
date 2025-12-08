"""SQLite database module for Supplier Search Engine dashboard.

Handles all database initialization, schema creation, and operations
for managing supplier data.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from datetime import datetime


class SupplierDatabase:
    """SQLite database handler for Supplier Search Engine."""

    def __init__(self, db_path: str = "suppliers.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Create database file if it doesn't exist."""
        if not os.path.exists(self.db_path):
            Path(self.db_path).touch()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_schema(self) -> None:
        """Initialize database schema.
        
        Creates all necessary tables for the supplier search engine.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Suppliers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    city TEXT,
                    state TEXT,
                    zip_code TEXT,
                    country TEXT,
                    category TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'pending'))
                )
            """)
            
            # Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_id INTEGER NOT NULL,
                    product_code TEXT UNIQUE NOT NULL,
                    product_name TEXT NOT NULL,
                    description TEXT,
                    unit_cost REAL,
                    lead_time_days INTEGER,
                    min_order_qty INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
                )
            """)
            
            # Search history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_query TEXT NOT NULL,
                    results_count INTEGER,
                    user_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_supplier_name 
                ON suppliers(name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_supplier_category 
                ON suppliers(category)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_product_supplier 
                ON products(supplier_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_search_history_date 
                ON search_history(created_at)
            """)

    def add_supplier(self, supplier_data: Dict[str, Any]) -> int:
        """Add a new supplier to the database.
        
        Args:
            supplier_data: Dictionary containing supplier information
            
        Returns:
            int: ID of the newly created supplier
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO suppliers 
                (supplier_id, name, email, phone, address, city, state, zip_code, country, category, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                supplier_data.get('supplier_id'),
                supplier_data.get('name'),
                supplier_data.get('email'),
                supplier_data.get('phone'),
                supplier_data.get('address'),
                supplier_data.get('city'),
                supplier_data.get('state'),
                supplier_data.get('zip_code'),
                supplier_data.get('country'),
                supplier_data.get('category'),
                supplier_data.get('status', 'active')
            ))
            return cursor.lastrowid

    def search_suppliers(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for suppliers by name or category.
        
        Args:
            query: Search query string
            category: Optional category filter
            
        Returns:
            List of supplier records matching the search
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT * FROM suppliers 
                    WHERE (name LIKE ? OR supplier_id LIKE ?)
                    AND category = ? AND status = 'active'
                    ORDER BY name ASC
                """, (f"%{query}%", f"%{query}%", category))
            else:
                cursor.execute("""
                    SELECT * FROM suppliers 
                    WHERE (name LIKE ? OR supplier_id LIKE ?) 
                    AND status = 'active'
                    ORDER BY name ASC
                """, (f"%{query}%", f"%{query}%"))
            
            return [dict(row) for row in cursor.fetchall()]

    def add_product(self, product_data: Dict[str, Any]) -> int:
        """Add a product to a supplier.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            int: ID of the newly created product
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products 
                (supplier_id, product_code, product_name, description, unit_cost, lead_time_days, min_order_qty)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data.get('supplier_id'),
                product_data.get('product_code'),
                product_data.get('product_name'),
                product_data.get('description'),
                product_data.get('unit_cost'),
                product_data.get('lead_time_days'),
                product_data.get('min_order_qty')
            ))
            return cursor.lastrowid

    def get_supplier_products(self, supplier_id: int) -> List[Dict[str, Any]]:
        """Get all products from a specific supplier.
        
        Args:
            supplier_id: ID of the supplier
            
        Returns:
            List of products from that supplier
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM products 
                WHERE supplier_id = ?
                ORDER BY product_name ASC
            """, (supplier_id,))
            return [dict(row) for row in cursor.fetchall()]

    def log_search(self, query: str, results_count: int, user_id: Optional[str] = None) -> None:
        """Log a search query for analytics.
        
        Args:
            query: The search query
            results_count: Number of results returned
            user_id: Optional user identifier
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO search_history (search_query, results_count, user_id)
                VALUES (?, ?, ?)
            """, (query, results_count, user_id))

    def get_statistics(self) -> Dict[str, Any]:
        """Get dashboard statistics.
        
        Returns:
            Dictionary containing various statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as total FROM suppliers WHERE status = 'active'")
            total_suppliers = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM products")
            total_products = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM search_history")
            total_searches = cursor.fetchone()['total']
            
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM suppliers 
                WHERE status = 'active'
                GROUP BY category
                ORDER BY count DESC
            """)
            category_breakdown = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total_active_suppliers': total_suppliers,
                'total_products': total_products,
                'total_searches': total_searches,
                'category_breakdown': category_breakdown
            }
