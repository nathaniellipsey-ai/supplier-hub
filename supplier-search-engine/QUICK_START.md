# Quick Start Guide - Supplier Search Engine

## Setup (One-time)

```bash
cd C:\Users\n0l08i7\Documents\supplier-search-engine
python init_db.py
python sample_data.py  # Load sample suppliers and products
```

## Common Commands

### 1. Add a New Supplier

```bash
python cli.py add-supplier \
  --supplier-id "NEWCORP001" \
  --name "New Corp Industries" \
  --email "contact@newcorp.com" \
  --phone "555-9999" \
  --address "123 Main St" \
  --city "New York" \
  --state "NY" \
  --zip-code "10001" \
  --country "USA" \
  --category "Electronics"
```

### 2. Search for Suppliers

```bash
# Search by name
python cli.py search --query "ACME"

# Search with category filter
python cli.py search --query "Electronics" --category "Electronics"

# Search by supplier ID
python cli.py search --query "ACME001"
```

### 3. Add Products to a Supplier

```bash
python cli.py add-product \
  --supplier-id 1 \
  --product-code "WIDGET-001" \
  --product-name "Premium Widget" \
  --description "High-quality widget for industrial use" \
  --unit-cost 99.99 \
  --lead-time-days 5 \
  --min-order-qty 10
```

### 4. List Products from a Supplier

```bash
python cli.py list-products --supplier-id 1
```

### 5. View Dashboard Statistics

```bash
python cli.py stats
```

Output shows:
- Number of active suppliers
- Total products in database
- Total searches performed
- Breakdown by category

## Using the Database Module in Python

```python
from database import SupplierDatabase

# Initialize
db = SupplierDatabase()

# Add supplier
supplier_id = db.add_supplier({
    'supplier_id': 'MYSUP001',
    'name': 'My Supplier',
    'email': 'contact@mysup.com',
    'category': 'Electronics'
})

# Search
results = db.search_suppliers('My')
for supplier in results:
    print(f"{supplier['name']} - {supplier['category']}")

# Add product
product_id = db.add_product({
    'supplier_id': supplier_id,
    'product_code': 'PROD001',
    'product_name': 'Product Name',
    'unit_cost': 99.99
})

# Get products from supplier
products = db.get_supplier_products(supplier_id)

# Get statistics
stats = db.get_statistics()
print(f"Total suppliers: {stats['total_active_suppliers']}")
```

## Database Location

**File:** `C:\Users\n0l08i7\Documents\supplier-search-engine\suppliers.db`

You can also open this with any SQLite client:

```bash
# Using command-line SQLite
sqlite3 suppliers.db

# Then you can run SQL queries like:
# SELECT * FROM suppliers;
# SELECT * FROM products WHERE supplier_id = 1;
```

## Project Structure

```
supplier-search-engine/
├── database.py          # Core database module
├── cli.py               # Command-line interface
├── init_db.py           # Database initialization
├── sample_data.py       # Sample data loader
├── suppliers.db         # SQLite database file
├── requirements.txt     # Python dependencies (none!)
├── README.md            # Full documentation
└── QUICK_START.md       # This file
```

## Notes

- **No dependencies needed!** Uses only Python's built-in `sqlite3` module
- Database is persisted in `suppliers.db`
- All searches are logged in the `search_history` table
- Suppliers can be marked as `active`, `inactive`, or `pending`
- All database changes are committed automatically
- Foreign keys enforce data integrity (delete supplier = delete products)

## Troubleshooting

**Q: Database file doesn't exist**
A: Run `python init_db.py` to create a fresh database

**Q: Getting "UNIQUE constraint failed" error**
A: You're trying to add a supplier with a supplier_id that already exists

**Q: Getting encoding errors on Windows**
A: The CLI handles encoding automatically. Use `python cli.py --help` for usage

**Q: Want to reset the database**
A: Delete `suppliers.db` and run `python init_db.py` again
