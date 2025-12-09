"""Business logic services for supplier management.

Handles core operations including supplier management, product management,
search, and data ingestion from live sources.
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class SupplierService:
    """Service for supplier operations."""

    def __init__(self, db):
        """Initialize supplier service.
        
        Args:
            db: SupplierDatabase instance
        """
        self.db = db

    def list_suppliers(
        self,
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List suppliers with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            category: Filter by category
            status: Filter by status
            
        Returns:
            List of supplier records
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM suppliers WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            elif status is None:
                query += " AND status = 'active'"
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY name ASC LIMIT ? OFFSET ?"
            params.extend([limit, skip])
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_supplier(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        """Get supplier by ID.
        
        Args:
            supplier_id: Database ID of supplier
            
        Returns:
            Supplier record or None
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_supplier(self, supplier_data: Dict[str, Any]) -> int:
        """Create a new supplier.
        
        Args:
            supplier_data: Supplier information
            
        Returns:
            ID of created supplier
        """
        return self.db.add_supplier(supplier_data)

    def get_statistics(self) -> Dict[str, Any]:
        """Get dashboard statistics.
        
        Returns:
            Statistics dictionary
        """
        return self.db.get_statistics()


class ProductService:
    """Service for product operations."""

    def __init__(self, db):
        """Initialize product service.
        
        Args:
            db: SupplierDatabase instance
        """
        self.db = db

    def get_supplier_products(self, supplier_id: int) -> List[Dict[str, Any]]:
        """Get all products from a supplier.
        
        Args:
            supplier_id: Supplier database ID
            
        Returns:
            List of product records
        """
        return self.db.get_supplier_products(supplier_id)

    def create_product(self, product_data: Dict[str, Any]) -> int:
        """Create a new product.
        
        Args:
            product_data: Product information
            
        Returns:
            ID of created product
        """
        return self.db.add_product(product_data)


class SearchService:
    """Service for search operations."""

    def __init__(self, db):
        """Initialize search service.
        
        Args:
            db: SupplierDatabase instance
        """
        self.db = db

    def search_suppliers(
        self,
        query: str,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for suppliers.
        
        Args:
            query: Search query
            category: Optional category filter
            
        Returns:
            List of matching suppliers
        """
        results = self.db.search_suppliers(query, category)
        self.db.log_search(query, len(results))
        return results


class DataIngestionService:
    """Service for ingesting live data from external sources."""

    # Available data sources with their configurations
    SOURCES = {
        'walmart_suppliers': {
            'url': 'https://api.walmart.com/suppliers',
            'description': 'Walmart supplier directory',
            'enabled': True
        },
        'global_suppliers': {
            'url': 'https://api.globalsuppliers.com/v1/suppliers',
            'description': 'Global supplier database',
            'enabled': True
        },
        'alibaba': {
            'url': 'https://api.alibaba.com/suppliers',
            'description': 'Alibaba suppliers',
            'enabled': True
        },
        'local_sample': {
            'url': None,
            'description': 'Local sample data generator',
            'enabled': True
        }
    }

    def __init__(self, db):
        """Initialize data ingestion service.
        
        Args:
            db: SupplierDatabase instance
        """
        self.db = db

    def get_available_sources(self) -> List[str]:
        """Get list of available data sources.
        
        Returns:
            List of source names
        """
        return [name for name, config in self.SOURCES.items() if config['enabled']]

    async def ingest_from_source(self, source: str) -> Dict[str, Any]:
        """Ingest data from a specified source.
        
        Args:
            source: Name of the data source
            
        Returns:
            Ingestion result with counts
        """
        if source not in self.SOURCES:
            raise ValueError(f"Unknown source: {source}")
        
        if source == 'local_sample':
            return await self._ingest_local_sample()
        else:
            return await self._ingest_from_api(source)

    async def _ingest_from_api(self, source: str) -> Dict[str, Any]:
        """Ingest data from external API.
        
        Args:
            source: Name of the data source
            
        Returns:
            Ingestion result
        """
        config = self.SOURCES[source]
        url = config['url']
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Process and insert data
                added = 0
                updated = 0
                
                suppliers = data.get('suppliers', []) if isinstance(data, dict) else data
                
                for supplier_data in suppliers:
                    try:
                        self.db.add_supplier({
                            'supplier_id': f"{source}_{supplier_data.get('id', '')}",
                            'name': supplier_data.get('name', 'Unknown'),
                            'email': supplier_data.get('email'),
                            'phone': supplier_data.get('phone'),
                            'address': supplier_data.get('address'),
                            'city': supplier_data.get('city'),
                            'state': supplier_data.get('state'),
                            'zip_code': supplier_data.get('zip_code'),
                            'country': supplier_data.get('country', 'USA'),
                            'category': supplier_data.get('category', 'General'),
                            'status': 'active'
                        })
                        added += 1
                    except Exception as e:
                        logger.warning(f"Error ingesting supplier from {source}: {e}")
                        updated += 1
                
                return {'records_added': added, 'records_updated': updated}
        
        except Exception as e:
            logger.error(f"Error ingesting from {source}: {e}")
            raise

    async def _ingest_local_sample(self) -> Dict[str, Any]:
        """Ingest local sample data.
        
        Returns:
            Ingestion result
        """
        sample_suppliers = [
            {
                'supplier_id': 'ONLINE_TECH001',
                'name': 'Online Tech Supply Co',
                'email': 'sales@onlinetech.com',
                'phone': '(555) 001-0001',
                'address': '123 Tech Plaza',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94105',
                'country': 'USA',
                'category': 'Electronics',
                'status': 'active'
            },
            {
                'supplier_id': 'CLOUD_SERVICES001',
                'name': 'Cloud Services Global',
                'email': 'info@cloudglobal.com',
                'phone': '(555) 002-0002',
                'address': '456 Cloud Lane',
                'city': 'Seattle',
                'state': 'WA',
                'zip_code': '98101',
                'country': 'USA',
                'category': 'Software',
                'status': 'active'
            },
            {
                'supplier_id': 'INDUSTRIAL_PARTS001',
                'name': 'Industrial Parts Distribution',
                'email': 'orders@industrialparts.com',
                'phone': '(555) 003-0003',
                'address': '789 Factory Road',
                'city': 'Detroit',
                'state': 'MI',
                'zip_code': '48201',
                'country': 'USA',
                'category': 'Manufacturing',
                'status': 'active'
            }
        ]
        
        added = 0
        for supplier_data in sample_suppliers:
            try:
                self.db.add_supplier(supplier_data)
                added += 1
            except Exception as e:
                logger.warning(f"Error adding sample supplier: {e}")
        
        return {'records_added': added, 'records_updated': 0}
