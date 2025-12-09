#!/usr/bin/env python3
"""Pydantic models for request/response validation.

Defines all data structures for the API using Pydantic for:
- Type validation
- Serialization/deserialization
- Auto API documentation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# ============================================================================
# SUPPLIER MODEL
# ============================================================================

class SupplierResponse(BaseModel):
    """Supplier response model."""
    id: int = Field(..., description="Unique supplier ID")
    name: str = Field(..., description="Company name")
    category: str = Field(..., description="Product category")
    location: str = Field(..., description="Geographic location")
    region: str = Field(..., description="Region")
    rating: float = Field(..., ge=0, le=5, description="Customer rating 0-5")
    aiScore: int = Field(..., ge=0, le=100, description="AI quality score 0-100")
    products: List[str] = Field(default=[], description="Products offered")
    certifications: List[str] = Field(default=[], description="Industry certifications")
    employeeCount: int = Field(default=0, description="Number of employees")
    yearFounded: int = Field(default=2000, description="Year company was founded")
    walmartVerified: bool = Field(default=False, description="Walmart verified supplier")
    responseTime: int = Field(default=24, description="Typical response time in hours")
    description: str = Field(default="", description="Company description")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Premier Lumber Inc.",
                "category": "Lumber & Wood Products",
                "location": "Portland, OR",
                "region": "West",
                "rating": 4.5,
                "aiScore": 92,
                "products": ["Dimensional Lumber", "Plywood"],
                "certifications": ["FSC", "ISO 9001"],
                "employeeCount": 250,
                "yearFounded": 1995,
                "walmartVerified": True,
                "responseTime": 24,
                "description": "Leading supplier of sustainable lumber products"
            }
        }

# ============================================================================
# SEARCH MODELS
# ============================================================================

class SearchRequest(BaseModel):
    """Advanced search request model."""
    query: Optional[str] = Field(None, description="Text search query")
    category: Optional[str] = Field(None, description="Filter by category")
    location: Optional[str] = Field(None, description="Filter by location")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating")
    walmart_verified: Optional[bool] = Field(None, description="Only Walmart verified")
    limit: int = Field(100, ge=1, le=500, description="Max results")

# ============================================================================
# DASHBOARD MODELS
# ============================================================================

class DashboardStats(BaseModel):
    """Dashboard statistics model."""
    total_suppliers: int = Field(..., description="Total number of suppliers")
    walmart_verified: int = Field(..., description="Number of Walmart verified suppliers")
    verified_percentage: float = Field(..., description="Percentage of verified suppliers")
    average_rating: float = Field(..., description="Average supplier rating")
    average_ai_score: float = Field(..., description="Average AI quality score")
    categories: Dict[str, int] = Field(..., description="Supplier count by category")
    total_categories: int = Field(..., description="Total number of categories")
    
    class Config:
        schema_extra = {
            "example": {
                "total_suppliers": 5000,
                "walmart_verified": 1423,
                "verified_percentage": 28.5,
                "average_rating": 4.2,
                "average_ai_score": 80.1,
                "categories": {
                    "Lumber & Wood Products": 500,
                    "Concrete & Masonry": 500
                },
                "total_categories": 10
            }
        }

# ============================================================================
# SUPPLIER LIST MODEL
# ============================================================================

class SupplierList(BaseModel):
    """Paginated supplier list model."""
    total: int = Field(..., description="Total number of suppliers")
    skip: int = Field(..., description="Number skipped")
    limit: int = Field(..., description="Limit per page")
    count: int = Field(..., description="Actual count in this response")
    suppliers: List[dict] = Field(..., description="List of suppliers")
    
    class Config:
        schema_extra = {
            "example": {
                "total": 5000,
                "skip": 0,
                "limit": 100,
                "count": 100,
                "suppliers": []
            }
        }

# ============================================================================
# CATEGORIES MODEL
# ============================================================================

class CategoriesResponse(BaseModel):
    """Categories response model."""
    categories: Dict[str, int] = Field(..., description="Category names and supplier counts")
    total_categories: int = Field(..., description="Total number of categories")
    
    class Config:
        schema_extra = {
            "example": {
                "categories": {
                    "Lumber & Wood Products": 500,
                    "Concrete & Masonry": 500,
                    "Electrical & Lighting": 500
                },
                "total_categories": 10
            }
        }

# ============================================================================
# FILTER MODELS
# ============================================================================

class SupplierCreate(BaseModel):
    """Model for creating a new supplier (for future use)."""
    name: str
    category: str
    location: str
    region: str
    description: Optional[str] = None

class SupplierUpdate(BaseModel):
    """Model for updating supplier data (for future use)."""
    name: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None

# ============================================================================
# ERROR MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.now, description="When error occurred")
