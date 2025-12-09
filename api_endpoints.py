#!/usr/bin/env python3
"""
Comprehensive API Endpoints for Supplier Hub
Includes all CRUD operations and advanced features
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from database_schema import (
    Supplier, Contact, SupplierEmail, SupplierNote,
    SupplierCreate, SupplierUpdate, ContactCreate
)
from csv_importer import SupplierCSVImporter, ContactCSVImporter
from email_integration import SupplierEmailManager, GmailProvider
from ai_chatbot import SupplierChatbot

router = APIRouter(prefix="/api", tags=["supplier_hub"])

# ============================================================================
# SUPPLIER ENDPOINTS
# ============================================================================

@router.get("/suppliers")
async def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_rating: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of suppliers with optional filtering
    """
    query = db.query(Supplier).filter(Supplier.is_active == True)
    
    if category:
        query = query.filter(Supplier.category.ilike(f"%{category}%"))
    
    if search:
        query = query.filter(
            (Supplier.name.ilike(f"%{search}%")) |
            (Supplier.location.ilike(f"%{search}%"))
        )
    
    if min_rating is not None:
        query = query.filter(Supplier.rating >= min_rating)
    
    total = query.count()
    suppliers = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "count": len(suppliers),
        "suppliers": [s.to_dict() for s in suppliers]
    }


@router.get("/suppliers/{supplier_id}")
async def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    Get a specific supplier
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    return supplier.to_dict()


@router.post("/suppliers")
async def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new supplier
    """
    # Check if supplier already exists
    existing = db.query(Supplier).filter(
        Supplier.name == supplier_data.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Supplier already exists")
    
    supplier = Supplier(**supplier_data.dict())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    
    return {
        "success": True,
        "supplier": supplier.to_dict(),
        "message": "Supplier created successfully"
    }


@router.put("/suppliers/{supplier_id}")
async def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a supplier
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Update fields
    update_data = supplier_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)
    
    supplier.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(supplier)
    
    return {
        "success": True,
        "supplier": supplier.to_dict(),
        "message": "Supplier updated successfully"
    }


@router.delete("/suppliers/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a supplier (soft delete)
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    supplier.is_active = False
    db.commit()
    
    return {
        "success": True,
        "message": "Supplier deleted"
    }


# ============================================================================
# CONTACT ENDPOINTS
# ============================================================================

@router.get("/suppliers/{supplier_id}/contacts")
async def get_supplier_contacts(
    supplier_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all contacts for a supplier
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    contacts = db.query(Contact).filter(
        Contact.supplier_id == supplier_id
    ).all()
    
    return [c.to_dict() for c in contacts]


@router.post("/suppliers/{supplier_id}/contacts")
async def create_contact(
    supplier_id: int,
    contact_data: ContactCreate,
    db: Session = Depends(get_db)
):
    """
    Create a contact for a supplier
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    contact = Contact(
        supplier_id=supplier_id,
        **contact_data.dict()
    )
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return {
        "success": True,
        "contact": contact.to_dict(),
        "message": "Contact created successfully"
    }


@router.put("/contacts/{contact_id}")
async def update_contact(
    contact_id: int,
    contact_data: ContactCreate,
    db: Session = Depends(get_db)
):
    """
    Update a contact
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for field, value in contact_data.dict().items():
        setattr(contact, field, value)
    
    contact.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contact)
    
    return {
        "success": True,
        "contact": contact.to_dict()
    }


@router.delete("/contacts/{contact_id}")
async def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a contact
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    
    return {"success": True, "message": "Contact deleted"}


# ============================================================================
# CSV IMPORT ENDPOINTS
# ============================================================================

@router.post("/suppliers/import/csv")
async def import_suppliers_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Bulk import suppliers from CSV file
    """
    try:
        content = await file.read()
        importer = SupplierCSVImporter()
        report = importer.import_csv(content, db)
        return report
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Import failed: {str(e)}",
            "errors": [str(e)]
        }


@router.post("/contacts/import/csv")
async def import_contacts_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Bulk import contacts from CSV file
    """
    try:
        content = await file.read()
        importer = ContactCSVImporter()
        report = importer.import_csv(content, db)
        return report
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Import failed: {str(e)}",
            "errors": [str(e)]
        }


# ============================================================================
# EMAIL ENDPOINTS
# ============================================================================

@router.post("/email/authenticate")
async def authenticate_email(
    credentials_json: str,
    db: Session = Depends(get_db)
):
    """
    Authenticate with Gmail/email provider
    """
    try:
        email_manager = SupplierEmailManager(db, GmailProvider())
        success = email_manager.email_provider.authenticate(credentials_json)
        
        return {
            "success": success,
            "message": "Email authentication successful" if success else "Authentication failed"
        }
    
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/email/sync")
async def sync_supplier_emails(
    db: Session = Depends(get_db)
):
    """
    Sync emails from all supplier contacts
    """
    try:
        email_manager = SupplierEmailManager(db)
        result = email_manager.sync_supplier_emails()
        return result
    
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/email/inbox")
async def get_supplier_inbox(
    supplier_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get supplier emails
    """
    email_manager = SupplierEmailManager(db)
    emails = email_manager.get_supplier_inbox(supplier_id)
    
    return {
        "count": len(emails),
        "emails": emails
    }


@router.put("/email/{email_id}/read")
async def mark_email_as_read(
    email_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark email as read
    """
    email_manager = SupplierEmailManager(db)
    success = email_manager.mark_email_as_read(email_id)
    
    return {"success": success}


@router.put("/email/{email_id}/archive")
async def archive_email(
    email_id: int,
    db: Session = Depends(get_db)
):
    """
    Archive email
    """
    email_manager = SupplierEmailManager(db)
    success = email_manager.archive_email(email_id)
    
    return {"success": success}


@router.put("/email/{email_id}/categorize")
async def categorize_email(
    email_id: int,
    category: str,
    db: Session = Depends(get_db)
):
    """
    Categorize email
    """
    email_manager = SupplierEmailManager(db)
    success = email_manager.categorize_email(email_id, category)
    
    return {"success": success}


# ============================================================================
# CHATBOT ENDPOINTS
# ============================================================================

@router.post("/chatbot/chat")
async def chat_with_assistant(
    message: dict,
    db: Session = Depends(get_db)
):
    """
    Chat with AI assistant
    """
    try:
        chatbot = SupplierChatbot(db)
        response = chatbot.chat(message.get('message', ''))
        return response
    
    except Exception as e:
        return {
            "message": f"I encountered an error: {str(e)}",
            "action": None,
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics
    """
    from sqlalchemy import func
    
    total = db.query(Supplier).filter(Supplier.is_active == True).count()
    verified = db.query(Supplier).filter(
        Supplier.is_active == True,
        Supplier.walmart_verified == True
    ).count()
    
    avg_rating = db.query(func.avg(Supplier.rating)).filter(
        Supplier.is_active == True
    ).scalar() or 0
    
    total_contacts = db.query(Contact).count()
    
    unread_emails = db.query(SupplierEmail).filter(
        SupplierEmail.is_read == False,
        SupplierEmail.is_archived == False
    ).count()
    
    return {
        "total_suppliers": total,
        "walmart_verified": verified,
        "average_rating": float(avg_rating),
        "total_contacts": total_contacts,
        "unread_emails": unread_emails,
        "last_updated": datetime.utcnow().isoformat()
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_db():
    """
    Database session dependency
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()