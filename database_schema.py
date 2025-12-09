#!/usr/bin/env python3
"""
Database Schema for Supplier Hub
Defines all database tables and relationships
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# ============================================================================
# DATABASE MODELS
# ============================================================================

class Supplier(Base):
    """Supplier profile table"""
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    category = Column(String(255), index=True)
    description = Column(Text)
    website = Column(String(255))
    primary_phone = Column(String(20))
    primary_email = Column(String(255), index=True)
    location = Column(String(255), index=True)
    state = Column(String(2))
    region = Column(String(50))
    years_in_business = Column(Integer)
    company_size = Column(String(50))
    price_range = Column(String(50))
    
    # Ratings and scores
    rating = Column(Float, default=0.0)
    ai_score = Column(Float, default=0.0)
    walmart_verified = Column(Boolean, default=False)
    
    # Products
    products = Column(String)  # JSON array as string
    certifications = Column(String)  # JSON array as string
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    contacts = relationship("Contact", back_populates="supplier", cascade="all, delete-orphan")
    emails = relationship("SupplierEmail", back_populates="supplier", cascade="all, delete-orphan")
    notes = relationship("SupplierNote", back_populates="supplier", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'website': self.website,
            'primaryPhone': self.primary_phone,
            'primaryEmail': self.primary_email,
            'location': self.location,
            'state': self.state,
            'region': self.region,
            'yearsInBusiness': self.years_in_business,
            'companySize': self.company_size,
            'priceRange': self.price_range,
            'rating': self.rating,
            'aiScore': self.ai_score,
            'walmartVerified': self.walmart_verified,
            'products': self.products,
            'certifications': self.certifications,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'isActive': self.is_active,
            'contacts': [c.to_dict() for c in self.contacts] if self.contacts else [],
        }


class Contact(Base):
    """Contact person at supplier"""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    title = Column(String(100))
    email = Column(String(255), index=True)
    phone = Column(String(20))
    department = Column(String(100))
    is_primary = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    supplier = relationship("Supplier", back_populates="contacts")
    
    def to_dict(self):
        return {
            'id': self.id,
            'supplierId': self.supplier_id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'title': self.title,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'isPrimary': self.is_primary,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class SupplierEmail(Base):
    """Emails received from supplier contacts"""
    __tablename__ = "supplier_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    from_address = Column(String(255), index=True, nullable=False)
    to_address = Column(String(255), nullable=False)
    subject = Column(String(500))
    body = Column(Text)
    received_at = Column(DateTime, index=True, nullable=False)
    is_read = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=True)  # Auto-flagged from supplier contact
    category = Column(String(50))  # general, invoice, delivery, complaint, inquiry
    gmail_message_id = Column(String(255), unique=True)  # Gmail message ID for sync
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="emails")
    
    def to_dict(self):
        return {
            'id': self.id,
            'supplierId': self.supplier_id,
            'fromAddress': self.from_address,
            'toAddress': self.to_address,
            'subject': self.subject,
            'body': self.body,
            'receivedAt': self.received_at.isoformat() if self.received_at else None,
            'isRead': self.is_read,
            'isFlagged': self.is_flagged,
            'category': self.category,
            'isArchived': self.is_archived,
        }


class SupplierNote(Base):
    """User notes on suppliers"""
    __tablename__ = "supplier_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_pinned = Column(Boolean, default=False)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="notes")
    
    def to_dict(self):
        return {
            'id': self.id,
            'supplierId': self.supplier_id,
            'userEmail': self.user_email,
            'noteText': self.note_text,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'isPinned': self.is_pinned,
        }


# ============================================================================
# PYDANTIC SCHEMAS (for API validation)
# ============================================================================

class ContactCreate(BaseModel):
    """Schema for creating/updating a contact"""
    first_name: str
    last_name: str
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    is_primary: bool = False
    notes: Optional[str] = None


class SupplierCreate(BaseModel):
    """Schema for creating a supplier"""
    name: str
    category: str
    description: Optional[str] = None
    website: Optional[str] = None
    primary_phone: Optional[str] = None
    primary_email: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    years_in_business: Optional[int] = None
    company_size: Optional[str] = None
    price_range: Optional[str] = None
    products: Optional[str] = None
    certifications: Optional[str] = None


class SupplierUpdate(BaseModel):
    """Schema for updating a supplier"""
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    primary_phone: Optional[str] = None
    primary_email: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    years_in_business: Optional[int] = None
    company_size: Optional[str] = None
    price_range: Optional[str] = None
    rating: Optional[float] = None
    ai_score: Optional[float] = None
    walmart_verified: Optional[bool] = None
    products: Optional[str] = None
    certifications: Optional[str] = None
    is_active: Optional[bool] = None