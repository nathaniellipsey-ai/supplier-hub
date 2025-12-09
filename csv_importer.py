#!/usr/bin/env python3
"""
CSV Importer for Supplier Data
Handles bulk import of suppliers from CSV/Excel files
"""

import csv
import json
from io import StringIO, BytesIO
from typing import List, Dict, Tuple
from datetime import datetime
import pandas as pd
from database_schema import Supplier, Contact, Base
from sqlalchemy.orm import Session


class SupplierCSVImporter:
    """
    Handles CSV/Excel import of supplier data
    
    Expected CSV columns:
    - name (required)
    - category
    - description
    - website
    - primary_phone
    - primary_email
    - location
    - state
    - region
    - years_in_business
    - company_size
    - price_range
    - products (JSON array as string)
    - certifications (JSON array as string)
    - rating (0-5)
    - walmart_verified (yes/no or true/false)
    
    Optional contact columns (will create contact for each):
    - contact_first_name
    - contact_last_name
    - contact_title
    - contact_email
    - contact_phone
    - contact_department
    """
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.created = 0
        self.updated = 0
        self.failed = 0
    
    def import_csv(self, file_content: bytes, db: Session) -> Dict:
        """
        Import suppliers from CSV content
        """
        try:
            # Try reading as UTF-8
            try:
                text = file_content.decode('utf-8')
            except UnicodeDecodeError:
                # Try latin-1 as fallback
                text = file_content.decode('latin-1')
            
            # Use pandas for more robust CSV handling
            df = pd.read_csv(StringIO(text))
            
            # Validate required columns
            if 'name' not in df.columns:
                raise ValueError("CSV must have 'name' column")
            
            # Process each row
            for idx, row in df.iterrows():
                try:
                    self._import_row(row, db, idx)
                except Exception as e:
                    self.failed += 1
                    self.errors.append(f"Row {idx + 1}: {str(e)}")
            
            # Commit all changes
            db.commit()
            
            return self._get_report()
        
        except Exception as e:
            self.errors.append(f"Import failed: {str(e)}")
            return self._get_report()
    
    def _import_row(self, row: pd.Series, db: Session, row_idx: int) -> None:
        """
        Import a single row
        """
        name = str(row.get('name', '')).strip()
        
        if not name:
            raise ValueError("Supplier name is required")
        
        # Check if supplier exists
        existing = db.query(Supplier).filter(Supplier.name == name).first()
        
        if existing:
            # Update existing
            self._update_supplier(existing, row, db)
            self.updated += 1
        else:
            # Create new
            self._create_supplier(row, db)
            self.created += 1
    
    def _create_supplier(self, row: pd.Series, db: Session) -> Supplier:
        """
        Create a new supplier
        """
        supplier = Supplier(
            name=str(row.get('name', '')).strip(),
            category=str(row.get('category', '')).strip() or None,
            description=str(row.get('description', '')).strip() or None,
            website=str(row.get('website', '')).strip() or None,
            primary_phone=str(row.get('primary_phone', '')).strip() or None,
            primary_email=str(row.get('primary_email', '')).strip() or None,
            location=str(row.get('location', '')).strip() or None,
            state=str(row.get('state', '')).strip() or None,
            region=str(row.get('region', '')).strip() or None,
            years_in_business=self._parse_int(row.get('years_in_business')),
            company_size=str(row.get('company_size', '')).strip() or None,
            price_range=str(row.get('price_range', '')).strip() or None,
            rating=self._parse_float(row.get('rating'), 0.0),
            ai_score=self._parse_float(row.get('ai_score'), 0.0),
            walmart_verified=self._parse_bool(row.get('walmart_verified')),
            products=str(row.get('products', '')).strip() or None,
            certifications=str(row.get('certifications', '')).strip() or None,
        )
        
        db.add(supplier)
        db.flush()  # Get the ID without committing
        
        # Create contact if contact fields present
        self._create_contact_if_present(supplier, row, db)
        
        return supplier
    
    def _update_supplier(self, supplier: Supplier, row: pd.Series, db: Session) -> None:
        """
        Update an existing supplier
        """
        # Update fields that are present in CSV
        if 'category' in row.index and pd.notna(row['category']):
            supplier.category = str(row['category']).strip()
        if 'description' in row.index and pd.notna(row['description']):
            supplier.description = str(row['description']).strip()
        if 'website' in row.index and pd.notna(row['website']):
            supplier.website = str(row['website']).strip()
        if 'primary_phone' in row.index and pd.notna(row['primary_phone']):
            supplier.primary_phone = str(row['primary_phone']).strip()
        if 'primary_email' in row.index and pd.notna(row['primary_email']):
            supplier.primary_email = str(row['primary_email']).strip()
        if 'location' in row.index and pd.notna(row['location']):
            supplier.location = str(row['location']).strip()
        if 'rating' in row.index and pd.notna(row['rating']):
            supplier.rating = self._parse_float(row['rating'], supplier.rating)
        
        supplier.updated_at = datetime.utcnow()
        
        # Create contact if contact fields present
        self._create_contact_if_present(supplier, row, db)
    
    def _create_contact_if_present(self, supplier: Supplier, row: pd.Series, db: Session) -> None:
        """
        Create a contact for the supplier if contact fields are present
        """
        contact_first_name = str(row.get('contact_first_name', '')).strip() or None
        contact_last_name = str(row.get('contact_last_name', '')).strip() or None
        contact_email = str(row.get('contact_email', '')).strip() or None
        
        # Only create contact if we have at least a first or last name
        if contact_first_name or contact_last_name:
            contact = Contact(
                supplier_id=supplier.id,
                first_name=contact_first_name or 'Unknown',
                last_name=contact_last_name or 'Contact',
                title=str(row.get('contact_title', '')).strip() or None,
                email=contact_email,
                phone=str(row.get('contact_phone', '')).strip() or None,
                department=str(row.get('contact_department', '')).strip() or None,
                is_primary=True,
            )
            db.add(contact)
    
    def _parse_int(self, value) -> int or None:
        """
        Parse integer value
        """
        try:
            if pd.isna(value):
                return None
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return None
    
    def _parse_float(self, value, default=0.0) -> float:
        """
        Parse float value
        """
        try:
            if pd.isna(value):
                return default
            return float(str(value).strip())
        except (ValueError, TypeError):
            return default
    
    def _parse_bool(self, value) -> bool:
        """
        Parse boolean value
        """
        if pd.isna(value):
            return False
        str_val = str(value).strip().lower()
        return str_val in ['true', 'yes', '1', 'y', 'on']
    
    def _get_report(self) -> Dict:
        """
        Get import report
        """
        return {
            'success': self.failed == 0,
            'created': self.created,
            'updated': self.updated,
            'failed': self.failed,
            'total': self.created + self.updated + self.failed,
            'errors': self.errors,
            'warnings': self.warnings,
            'message': f"Import complete: {self.created} created, {self.updated} updated, {self.failed} failed"
        }


class ContactCSVImporter:
    """
    Handles CSV import of contact data for existing suppliers
    
    Expected CSV columns:
    - supplier_name (required) - must match existing supplier
    - first_name (required)
    - last_name (required)
    - title
    - email
    - phone
    - department
    - is_primary (yes/no or true/false)
    """
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.created = 0
        self.failed = 0
    
    def import_csv(self, file_content: bytes, db: Session) -> Dict:
        """
        Import contacts from CSV content
        """
        try:
            # Try reading as UTF-8
            try:
                text = file_content.decode('utf-8')
            except UnicodeDecodeError:
                text = file_content.decode('latin-1')
            
            df = pd.read_csv(StringIO(text))
            
            # Validate required columns
            required = ['supplier_name', 'first_name', 'last_name']
            missing = [col for col in required if col not in df.columns]
            if missing:
                raise ValueError(f"CSV missing required columns: {', '.join(missing)}")
            
            # Process each row
            for idx, row in df.iterrows():
                try:
                    self._import_contact_row(row, db, idx)
                except Exception as e:
                    self.failed += 1
                    self.errors.append(f"Row {idx + 1}: {str(e)}")
            
            db.commit()
            return self._get_report()
        
        except Exception as e:
            self.errors.append(f"Import failed: {str(e)}")
            return self._get_report()
    
    def _import_contact_row(self, row: pd.Series, db: Session, row_idx: int) -> None:
        """
        Import a single contact row
        """
        supplier_name = str(row.get('supplier_name', '')).strip()
        first_name = str(row.get('first_name', '')).strip()
        last_name = str(row.get('last_name', '')).strip()
        
        if not supplier_name:
            raise ValueError("Supplier name is required")
        if not first_name:
            raise ValueError("First name is required")
        
        # Find supplier
        supplier = db.query(Supplier).filter(Supplier.name == supplier_name).first()
        if not supplier:
            raise ValueError(f"Supplier '{supplier_name}' not found")
        
        # Create contact
        contact = Contact(
            supplier_id=supplier.id,
            first_name=first_name,
            last_name=last_name,
            title=str(row.get('title', '')).strip() or None,
            email=str(row.get('email', '')).strip() or None,
            phone=str(row.get('phone', '')).strip() or None,
            department=str(row.get('department', '')).strip() or None,
            is_primary=self._parse_bool(row.get('is_primary')),
        )
        db.add(contact)
        self.created += 1
    
    def _parse_bool(self, value) -> bool:
        if pd.isna(value):
            return False
        str_val = str(value).strip().lower()
        return str_val in ['true', 'yes', '1', 'y', 'on']
    
    def _get_report(self) -> Dict:
        return {
            'success': self.failed == 0,
            'created': self.created,
            'failed': self.failed,
            'total': self.created + self.failed,
            'errors': self.errors,
            'warnings': self.warnings,
            'message': f"Import complete: {self.created} contacts created, {self.failed} failed"
        }