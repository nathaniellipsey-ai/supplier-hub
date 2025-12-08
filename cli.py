"""Command-line interface for Supplier Search Engine.

Provides interactive tools to manage suppliers and search the database.
"""

import argparse
import json
from typing import Optional
from database import SupplierDatabase


class SupplierCLI:
    """CLI interface for supplier management."""

    def __init__(self, db_path: str = "suppliers.db"):
        """Initialize CLI with database.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db = SupplierDatabase(db_path)

    def add_supplier(self, args) -> None:
        """Add a new supplier.
        
        Args:
            args: Parsed command arguments
        """
        supplier_data = {
            'supplier_id': args.supplier_id,
            'name': args.name,
            'email': args.email,
            'phone': args.phone,
            'address': args.address,
            'city': args.city,
            'state': args.state,
            'zip_code': args.zip_code,
            'country': args.country,
            'category': args.category,
            'status': args.status
        }
        
        supplier_id = self.db.add_supplier(supplier_data)
        print(f"[SUCCESS] Supplier added successfully! ID: {supplier_id}")
        print(f"   Name: {args.name}")
        print(f"   Category: {args.category}")

    def search_suppliers(self, args) -> None:
        """Search for suppliers.
        
        Args:
            args: Parsed command arguments
        """
        results = self.db.search_suppliers(args.query, args.category)
        
        if not results:
            print(f"[INFO] No suppliers found matching '{args.query}'")
            return
        
        print(f"\n[RESULTS] Found {len(results)} supplier(s):\n")
        for supplier in results:
            print(f"  >> {supplier['name']}")
            print(f"     ID: {supplier['supplier_id']}")
            print(f"     Category: {supplier['category']}")
            print(f"     Email: {supplier['email']}")
            print(f"     Phone: {supplier['phone']}")
            print(f"     Location: {supplier['city']}, {supplier['state']} {supplier['zip_code']}")
            print()
        
        # Log the search
        self.db.log_search(args.query, len(results))

    def add_product(self, args) -> None:
        """Add a product to a supplier.
        
        Args:
            args: Parsed command arguments
        """
        product_data = {
            'supplier_id': args.supplier_id,
            'product_code': args.product_code,
            'product_name': args.product_name,
            'description': args.description,
            'unit_cost': args.unit_cost,
            'lead_time_days': args.lead_time_days,
            'min_order_qty': args.min_order_qty
        }
        
        product_id = self.db.add_product(product_data)
        print(f"[SUCCESS] Product added successfully! ID: {product_id}")
        print(f"   Product: {args.product_name}")
        print(f"   Code: {args.product_code}")
        print(f"   Unit Cost: ${args.unit_cost}")

    def list_products(self, args) -> None:
        """List all products from a supplier.
        
        Args:
            args: Parsed command arguments
        """
        products = self.db.get_supplier_products(args.supplier_id)
        
        if not products:
            print(f"[INFO] No products found for supplier ID {args.supplier_id}")
            return
        
        print(f"\n[PRODUCTS] List ({len(products)} total):\n")
        for product in products:
            print(f"  * {product['product_name']}")
            print(f"    Code: {product['product_code']}")
            print(f"    Cost: ${product['unit_cost']:.2f}")
            print(f"    Lead Time: {product['lead_time_days']} days")
            print(f"    Min Order: {product['min_order_qty']} units")
            print()

    def show_statistics(self, args) -> None:
        """Display dashboard statistics.
        
        Args:
            args: Parsed command arguments
        """
        stats = self.db.get_statistics()
        
        print("\n[DASHBOARD] Supplier Search Engine Dashboard Statistics\n")
        print(f"  [SUPPLIERS] Active Suppliers: {stats['total_active_suppliers']}")
        print(f"  [PRODUCTS] Total Products: {stats['total_products']}")
        print(f"  [SEARCHES] Total Searches: {stats['total_searches']}")
        
        if stats['category_breakdown']:
            print("\n  [CATEGORIES] Suppliers by Category:")
            for cat in stats['category_breakdown']:
                print(f"     - {cat['category']}: {cat['count']} suppliers")
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Supplier Search Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a supplier
  python cli.py add-supplier --supplier-id SUP001 --name "ABC Corp" --category "Electronics"
  
  # Search for suppliers
  python cli.py search --query "ABC" --category "Electronics"
  
  # Add a product
  python cli.py add-product --supplier-id 1 --product-code "PROD001" --product-name "Laptop"
  
  # View statistics
  python cli.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add supplier command
    add_supplier_parser = subparsers.add_parser('add-supplier', help='Add a new supplier')
    add_supplier_parser.add_argument('--supplier-id', required=True, help='Unique supplier ID')
    add_supplier_parser.add_argument('--name', required=True, help='Supplier name')
    add_supplier_parser.add_argument('--email', default='', help='Email address')
    add_supplier_parser.add_argument('--phone', default='', help='Phone number')
    add_supplier_parser.add_argument('--address', default='', help='Street address')
    add_supplier_parser.add_argument('--city', default='', help='City')
    add_supplier_parser.add_argument('--state', default='', help='State/Province')
    add_supplier_parser.add_argument('--zip-code', default='', help='Postal code')
    add_supplier_parser.add_argument('--country', default='USA', help='Country')
    add_supplier_parser.add_argument('--category', default='General', help='Product category')
    add_supplier_parser.add_argument('--status', default='active', choices=['active', 'inactive', 'pending'],
                                    help='Supplier status')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for suppliers')
    search_parser.add_argument('--query', '-q', required=True, help='Search query')
    search_parser.add_argument('--category', '-c', help='Filter by category')
    
    # Add product command
    add_product_parser = subparsers.add_parser('add-product', help='Add a product')
    add_product_parser.add_argument('--supplier-id', type=int, required=True, help='Supplier ID')
    add_product_parser.add_argument('--product-code', required=True, help='Product code')
    add_product_parser.add_argument('--product-name', required=True, help='Product name')
    add_product_parser.add_argument('--description', default='', help='Product description')
    add_product_parser.add_argument('--unit-cost', type=float, default=0.0, help='Unit cost')
    add_product_parser.add_argument('--lead-time-days', type=int, default=0, help='Lead time in days')
    add_product_parser.add_argument('--min-order-qty', type=int, default=1, help='Minimum order quantity')
    
    # List products command
    list_products_parser = subparsers.add_parser('list-products', help='List products from a supplier')
    list_products_parser.add_argument('--supplier-id', type=int, required=True, help='Supplier ID')
    
    # Statistics command
    stats_parser = subparsers.add_parser('stats', help='Display dashboard statistics')
    
    args = parser.parse_args()
    cli = SupplierCLI()
    
    if args.command == 'add-supplier':
        cli.add_supplier(args)
    elif args.command == 'search':
        cli.search_suppliers(args)
    elif args.command == 'add-product':
        cli.add_product(args)
    elif args.command == 'list-products':
        cli.list_products(args)
    elif args.command == 'stats':
        cli.show_statistics(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
