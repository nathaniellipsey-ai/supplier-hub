"""Sample data loader for Supplier Search Engine.

Populates the database with example suppliers and products for testing.
"""

from database import SupplierDatabase


def load_sample_data():
    """Load sample suppliers and products into the database."""
    db = SupplierDatabase()
    
    # Sample suppliers
    suppliers = [
        {
            'supplier_id': 'ACME001',
            'name': 'ACME Electronics Corp',
            'email': 'sales@acme.com',
            'phone': '(408) 555-1234',
            'address': '100 Tech Drive',
            'city': 'San Jose',
            'state': 'CA',
            'zip_code': '95110',
            'country': 'USA',
            'category': 'Electronics',
            'status': 'active'
        },
        {
            'supplier_id': 'CHEM001',
            'name': 'ChemCorp Solutions',
            'email': 'info@chemcorp.com',
            'phone': '(713) 555-5678',
            'address': '500 Chemical Lane',
            'city': 'Houston',
            'state': 'TX',
            'zip_code': '77002',
            'country': 'USA',
            'category': 'Chemicals',
            'status': 'active'
        },
        {
            'supplier_id': 'MECH001',
            'name': 'MechTech Manufacturing',
            'email': 'contact@mechtech.com',
            'phone': '(412) 555-9012',
            'address': '200 Industrial Blvd',
            'city': 'Pittsburgh',
            'state': 'PA',
            'zip_code': '15219',
            'country': 'USA',
            'category': 'Manufacturing',
            'status': 'active'
        },
        {
            'supplier_id': 'SOFT001',
            'name': 'SoftWare Solutions Inc',
            'email': 'support@swsolutions.com',
            'phone': '(206) 555-3456',
            'address': '300 Cloud Street',
            'city': 'Seattle',
            'state': 'WA',
            'zip_code': '98101',
            'country': 'USA',
            'category': 'Software',
            'status': 'active'
        },
        {
            'supplier_id': 'PACK001',
            'name': 'PackageMasters Ltd',
            'email': 'orders@packagemasters.com',
            'phone': '(847) 555-7890',
            'address': '400 Logistics Way',
            'city': 'Chicago',
            'state': 'IL',
            'zip_code': '60601',
            'country': 'USA',
            'category': 'Packaging',
            'status': 'active'
        }
    ]
    
    # Sample products
    products = [
        {
            'supplier_id': 1,
            'product_code': 'LAPTOP-2025-PRO',
            'product_name': 'Professional Workstation Laptop',
            'description': 'High-performance laptop with RTX 4070, 32GB RAM',
            'unit_cost': 2499.99,
            'lead_time_days': 7,
            'min_order_qty': 5
        },
        {
            'supplier_id': 1,
            'product_code': 'MONITOR-4K-32',
            'product_name': '4K Monitor 32 inch',
            'description': '32" 4K UHD Monitor with USB-C',
            'unit_cost': 799.99,
            'lead_time_days': 5,
            'min_order_qty': 3
        },
        {
            'supplier_id': 2,
            'product_code': 'CHEM-ACRYLIC-50L',
            'product_name': 'Industrial Acrylic Coating',
            'description': 'High-grade acrylic coating - 50L drum',
            'unit_cost': 450.00,
            'lead_time_days': 14,
            'min_order_qty': 2
        },
        {
            'supplier_id': 2,
            'product_code': 'CHEM-SOLVENT-25L',
            'product_name': 'Organic Solvent Mix',
            'description': 'Premium organic solvent - 25L container',
            'unit_cost': 175.50,
            'lead_time_days': 10,
            'min_order_qty': 4
        },
        {
            'supplier_id': 3,
            'product_code': 'GEAR-MOTOR-EX100',
            'product_name': 'Electric Gear Motor',
            'description': '5HP Electric Gear Motor with controller',
            'unit_cost': 1200.00,
            'lead_time_days': 21,
            'min_order_qty': 1
        },
        {
            'supplier_id': 3,
            'product_code': 'BEARING-INDUSTRIAL-SKF',
            'product_name': 'Industrial Bearing Set',
            'description': 'SKF quality industrial bearings set',
            'unit_cost': 350.00,
            'lead_time_days': 7,
            'min_order_qty': 6
        },
        {
            'supplier_id': 4,
            'product_code': 'LIC-OFFICE-365',
            'product_name': 'Microsoft Office 365 License',
            'description': '1-year Microsoft Office 365 license',
            'unit_cost': 69.99,
            'lead_time_days': 1,
            'min_order_qty': 10
        },
        {
            'supplier_id': 4,
            'product_code': 'CLOUD-STORAGE-1TB',
            'product_name': 'Cloud Storage Plan 1TB',
            'description': 'Annual cloud storage subscription',
            'unit_cost': 99.99,
            'lead_time_days': 0,
            'min_order_qty': 1
        },
        {
            'supplier_id': 5,
            'product_code': 'BOX-CORRUG-A4-500',
            'product_name': 'Corrugated Cardboard Box',
            'description': 'A4 corrugated boxes - pack of 500',
            'unit_cost': 45.00,
            'lead_time_days': 3,
            'min_order_qty': 10
        },
        {
            'supplier_id': 5,
            'product_code': 'WRAP-BUBBLE-ROLL',
            'product_name': 'Bubble Wrap Roll',
            'description': 'Protective bubble wrap - 100m roll',
            'unit_cost': 22.50,
            'lead_time_days': 2,
            'min_order_qty': 5
        }
    ]
    
    print("[LOAD] Loading sample suppliers...")
    for supplier_data in suppliers:
        supplier_id = db.add_supplier(supplier_data)
        print(f"  [OK] {supplier_data['name']} (ID: {supplier_id})")
    
    print("\n[LOAD] Loading sample products...")
    for product_data in products:
        product_id = db.add_product(product_data)
        print(f"  [OK] {product_data['product_name']} (ID: {product_id})")
    
    # Display statistics
    stats = db.get_statistics()
    print("\n[COMPLETE] Sample data loaded successfully!")
    print(f"  Total suppliers: {stats['total_active_suppliers']}")
    print(f"  Total products: {stats['total_products']}")


if __name__ == "__main__":
    load_sample_data()
