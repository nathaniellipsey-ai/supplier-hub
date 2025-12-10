"""Core business logic services for Supplier Hub.

Implements SOLID principles with clear separation of concerns.
Each service has a single responsibility.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import random

from .models import (
    Supplier, SupplierCreate, SupplierCategory,
    User, UserCreate, UserUpdate,
    SearchFilter, SearchResult,
    Note, FavoriteAction
)

logger = logging.getLogger(__name__)


class SupplierService:
    """Manages supplier data operations.
    
    Responsibilities:
    - Create/read/update/delete suppliers
    - Search and filter suppliers
    - Validate supplier data
    """

    def __init__(self):
        """Initialize supplier service with empty storage."""
        self._suppliers: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
        logger.info("[SupplierService] Initialized")

    def create(self, supplier_data: SupplierCreate) -> Supplier:
        """Create a new supplier."""
        supplier_dict = supplier_data.dict()
        supplier_dict['id'] = self._next_id
        supplier_dict['created_at'] = datetime.now()
        supplier_dict['updated_at'] = datetime.now()
        
        self._suppliers[self._next_id] = supplier_dict
        self._next_id += 1
        
        logger.info(f"[SupplierService] Created supplier: {supplier_dict['name']}")
        return Supplier(**supplier_dict)

    def get(self, supplier_id: int) -> Optional[Supplier]:
        """Get supplier by ID."""
        if supplier_id in self._suppliers:
            return Supplier(**self._suppliers[supplier_id])
        return None

    def get_all(self) -> List[Supplier]:
        """Get all suppliers."""
        return [Supplier(**s) for s in self._suppliers.values()]

    def update(self, supplier_id: int, updates: Dict[str, Any]) -> Optional[Supplier]:
        """Update supplier data."""
        if supplier_id not in self._suppliers:
            return None
        
        supplier = self._suppliers[supplier_id]
        supplier.update(updates)
        supplier['updated_at'] = datetime.now()
        
        logger.info(f"[SupplierService] Updated supplier {supplier_id}")
        return Supplier(**supplier)

    def delete(self, supplier_id: int) -> bool:
        """Delete a supplier."""
        if supplier_id in self._suppliers:
            del self._suppliers[supplier_id]
            logger.info(f"[SupplierService] Deleted supplier {supplier_id}")
            return True
        return False

    def search(self, filters: SearchFilter) -> SearchResult:
        """Search suppliers with filters."""
        results = self._suppliers.values()
        
        # Apply filters
        if filters.query:
            q = filters.query.lower()
            results = [
                s for s in results 
                if q in s['name'].lower() or q in ' '.join(s.get('products', [])).lower()
            ]
        
        if filters.category:
            results = [s for s in results if s['category'] == filters.category]
        
        if filters.region:
            results = [s for s in results if s['region'] == filters.region]
        
        if filters.min_rating:
            results = [s for s in results if s['rating'] >= filters.min_rating]
        
        if filters.min_ai_score:
            results = [s for s in results if s['ai_score'] >= filters.min_ai_score]
        
        if filters.walmart_verified_only:
            results = [s for s in results if s['walmart_verified']]
        
        # Pagination
        total = len(results)
        items = results[filters.offset:filters.offset + filters.limit]
        
        return SearchResult(
            total=total,
            limit=filters.limit,
            offset=filters.offset,
            items=[Supplier(**s) for s in items]
        )

    def count(self) -> int:
        """Get total supplier count."""
        return len(self._suppliers)


class UserService:
    """Manages user data and preferences.
    
    Responsibilities:
    - User account management
    - Favorites management
    - Notes management
    """

    def __init__(self):
        """Initialize user service."""
        self._users: Dict[str, Dict[str, Any]] = {}
        self._user_favorites: Dict[str, List[int]] = {}
        self._user_notes: Dict[str, Dict[int, str]] = {}
        logger.info("[UserService] Initialized")

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        user_id = user_data.email  # Use email as unique ID
        
        user_dict = {
            'id': user_id,
            'username': user_data.username,
            'email': user_data.email,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'is_active': True
        }
        
        self._users[user_id] = user_dict
        self._user_favorites[user_id] = []
        self._user_notes[user_id] = {}
        
        logger.info(f"[UserService] Created user: {user_data.username}")
        return User(
            **user_dict,
            favorites=[],
            notes={}
        )

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        if user_id not in self._users:
            return None
        
        user_dict = self._users[user_id].copy()
        user_dict['favorites'] = self._user_favorites.get(user_id, [])
        user_dict['notes'] = self._user_notes.get(user_id, {})
        
        return User(**user_dict)

    def update_user(self, user_id: str, updates: UserUpdate) -> Optional[User]:
        """Update user information."""
        if user_id not in self._users:
            return None
        
        user = self._users[user_id]
        if updates.username:
            user['username'] = updates.username
        if updates.email:
            user['email'] = updates.email
        
        user['updated_at'] = datetime.now()
        
        logger.info(f"[UserService] Updated user: {user_id}")
        return self.get_user(user_id)

    def add_favorite(self, user_id: str, supplier_id: int) -> bool:
        """Add supplier to favorites."""
        if user_id not in self._users:
            return False
        
        if supplier_id not in self._user_favorites[user_id]:
            self._user_favorites[user_id].append(supplier_id)
            logger.info(f"[UserService] Added favorite: user={user_id}, supplier={supplier_id}")
        return True

    def remove_favorite(self, user_id: str, supplier_id: int) -> bool:
        """Remove supplier from favorites."""
        if user_id not in self._users:
            return False
        
        if supplier_id in self._user_favorites[user_id]:
            self._user_favorites[user_id].remove(supplier_id)
            logger.info(f"[UserService] Removed favorite: user={user_id}, supplier={supplier_id}")
        return True

    def get_favorites(self, user_id: str) -> List[int]:
        """Get user's favorite suppliers."""
        return self._user_favorites.get(user_id, [])

    def save_note(self, user_id: str, supplier_id: int, content: str) -> bool:
        """Save note for a supplier."""
        if user_id not in self._users:
            return False
        
        self._user_notes[user_id][supplier_id] = content
        logger.info(f"[UserService] Saved note: user={user_id}, supplier={supplier_id}")
        return True

    def get_note(self, user_id: str, supplier_id: int) -> Optional[str]:
        """Get note for a supplier."""
        return self._user_notes.get(user_id, {}).get(supplier_id)

    def get_all_notes(self, user_id: str) -> Dict[int, str]:
        """Get all notes for a user."""
        return self._user_notes.get(user_id, {})


class DataService:
    """Manages data import and export operations.
    
    Responsibilities:
    - Data import from various formats
    - Data export
    - Data validation
    """

    def __init__(self, supplier_service: SupplierService):
        """Initialize data service."""
        self.supplier_service = supplier_service
        logger.info("[DataService] Initialized")

    def import_suppliers_from_list(self, suppliers: List[Dict[str, Any]]) -> int:
        """Import suppliers from list of dictionaries."""
        count = 0
        for supplier_data in suppliers:
            try:
                # Convert snake_case to camelCase
                normalized = self._normalize_supplier_data(supplier_data)
                supplier_create = SupplierCreate(**normalized)
                self.supplier_service.create(supplier_create)
                count += 1
            except Exception as e:
                logger.error(f"[DataService] Error importing supplier: {str(e)}")
                continue
        
        logger.info(f"[DataService] Imported {count} suppliers")
        return count

    def _normalize_supplier_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize supplier data to expected format."""
        return {
            'name': data.get('name', 'Unknown'),
            'category': data.get('category', SupplierCategory.HARDWARE),
            'location': data.get('location', 'Unknown'),
            'region': data.get('region', 'XX'),
            'rating': float(data.get('rating', 3.5)),
            'ai_score': int(data.get('ai_score', 70)),
            'products': data.get('products', []),
            'certifications': data.get('certifications', []),
            'walmart_verified': bool(data.get('walmart_verified', False)),
            'years_in_business': int(data.get('years_in_business', 0)),
            'projects_completed': int(data.get('projects_completed', 0)),
        }

    def export_suppliers(self, supplier_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """Export suppliers as list of dictionaries."""
        suppliers = self.supplier_service.get_all()
        
        if supplier_ids:
            suppliers = [s for s in suppliers if s.id in supplier_ids]
        
        return [s.dict() for s in suppliers]