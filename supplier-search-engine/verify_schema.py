"""Verify database schema and display information."""

from database import SupplierDatabase


def main():
    """Display database schema information."""
    db = SupplierDatabase()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print("[SCHEMA] Database Tables:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"\n  Table: {table_name}")
            for col in columns:
                col_id, col_name, col_type, not_null, default, pk = col
                pk_marker = " [PK]" if pk else ""
                print(f"    - {col_name}: {col_type}{pk_marker}")
        
        # Get indexes
        cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        indexes = cursor.fetchall()
        
        if indexes:
            print("\n[INDEXES] Database Indexes:")
            for index in indexes:
                index_name, table_name = index
                print(f"  - {index_name} (on {table_name})")
        
        # Get data stats
        print("\n[STATS] Current Data:")
        cursor.execute("SELECT COUNT(*) FROM suppliers")
        supplier_count = cursor.fetchone()[0]
        print(f"  - Suppliers: {supplier_count}")
        
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"  - Products: {product_count}")
        
        cursor.execute("SELECT COUNT(*) FROM search_history")
        search_count = cursor.fetchone()[0]
        print(f"  - Search History: {search_count}")


if __name__ == "__main__":
    main()
