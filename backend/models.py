"""Data models for Supplier Hub.

Defines Pydantic models for type safety and validation.
Follows SOLID principles with single responsibility per model.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SupplierCategory(str, Enum):
    """Supplier category enumeration."""
    LUMBER = "Lumber & Wood Products"
    CONCRETE = "Concrete & Masonry"
    STEEL = "Steel & Metal"
    ELECTRICAL = "Electrical Supplies"
    PLUMBING = "Plumbing Supplies"
    HVAC = "HVAC Equipment"
    ROOFING = "Roofing Materials"
    WINDOWS_DOORS = "Windows & Doors"
    PAINT = "Paint & Finishes"
    HARDWARE = "Hardware & Fasteners"


class SupplierBase(BaseModel):
    """Base supplier model with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    category: SupplierCategory
    location: str = Field(..., min_length=1, max_length=255)
    region: str = Field(..., min_length=2, max_length=2)  # State code
    rating: float = Field(..., ge=0, le=5)
    ai_score: int = Field(..., ge=0, le=100)


class Supplier(SupplierBase):
    """Complete supplier model."""
    id: int
    products: List[str]
    certifications: List[str]
    walmart_verified: bool
    years_in_business: int
    projects_completed: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SupplierCreate(SupplierBase):
    """Model for creating new suppliers."""
    products: List[str] = Field(..., min_items=1)
    certifications: List[str] = []
    walmart_verified: bool = False
    years_in_business: int = Field(..., ge=0)
    projects_completed: int = Field(..., ge=0)

    @validator('products')
    def validate_products(cls, v):
        """Ensure products are non-empty strings."""
        if not all(isinstance(p, str) and p.strip() for p in v):
            raise ValueError('All products must be non-empty strings')
        return [p.strip() for p in v]


class UserBase(BaseModel):
    """Base user model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=255)


class User(UserBase):
    """Complete user model."""
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    favorites: List[int] = []
    notes: Dict[int, str] = {}


class UserCreate(UserBase):
    """Model for creating new users."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Model for updating user information."""
    email: Optional[str] = None
    username: Optional[str] = None


class FavoriteAction(BaseModel):
    """Model for favorite toggling."""
    supplier_id: int
    action: str = Field(..., pattern="^(add|remove)$")


class Note(BaseModel):
    """User note on a supplier."""
    supplier_id: int
    content: str = Field(..., min_length=1, max_length=5000)
    created_at: Optional[datetime] = None


class SearchFilter(BaseModel):
    """Search filter parameters."""
    query: Optional[str] = None
    category: Optional[SupplierCategory] = None
    region: Optional[str] = None
    min_rating: float = Field(0.0, ge=0, le=5)
    min_ai_score: int = Field(0, ge=0, le=100)
    walmart_verified_only: bool = False
    limit: int = Field(50, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class SearchResult(BaseModel):
    """Search results with pagination."""
    total: int
    limit: int
    offset: int
    items: List[Supplier]

    @property
    def has_next(self) -> bool:
        """Check if there are more results."""
        return self.offset + self.limit < self.total


class HealthStatus(BaseModel):
    """API health status."""
    status: str
    version: str
    timestamp: datetime
    suppliers_count: int