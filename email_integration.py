#!/usr/bin/env python3
"""
Email Integration Module
Handles Gmail/Outlook integration and email flagging
"""

import os
import base64
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from database_schema import SupplierEmail, Contact, Supplier
from sqlalchemy.orm import Session


class EmailProvider(ABC):
    """
    Abstract base class for email providers
    """
    
    @abstractmethod
    def authenticate(self, credentials_json: str) -> bool:
        """Authenticate with email provider"""
        pass
    
    @abstractmethod
    def get_emails(self, supplier_emails: List[str]) -> List[Dict]:
        """Get emails from supplier contacts"""
        pass
    
    @abstractmethod
    def mark_as_read(self, message_id: str) -> bool:
        """Mark email as read"""
        pass
    
    @abstractmethod
    def archive_email(self, message_id: str) -> bool:
        """Archive email"""
        pass
    
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email"""
        pass


class GmailProvider(EmailProvider):
    """
    Gmail integration using Google API
    """
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    def authenticate(self, credentials_json: str) -> bool:
        """
        Authenticate with Gmail
        credentials_json: Path to credentials.json from Google Cloud Console
        """
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_json, self.SCOPES)
            self.credentials = flow.run_local_server(port=0)
            self.service = build('gmail', 'v1', credentials=self.credentials)
            return True
        except Exception as e:
            print(f"Gmail authentication failed: {str(e)}")
            return False
    
    def get_emails(self, supplier_emails: List[str], max_results: int = 50) -> List[Dict]:
        """
        Get emails from supplier contacts
        supplier_emails: List of email addresses to filter
        """
        if not self.service:
            return []
        
        try:
            emails = []
            
            # Build query to find emails from supplier contacts
            query_parts = [f'from:{email}' for email in supplier_emails]
            query = ' OR '.join(query_parts)
            
            # Get messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get full message details
            for msg in messages:
                full_msg = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                email_data = self._parse_message(full_msg)
                emails.append(email_data)
            
            return emails
        
        except HttpError as error:
            print(f"Gmail API error: {error}")
            return []
    
    def _parse_message(self, message: Dict) -> Dict:
        """
        Parse Gmail message
        """
        try:
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_addr = next((h['value'] for h in headers if h['name'] == 'From'), '')
            to_addr = next((h['value'] for h in headers if h['name'] == 'To'), '')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Get message body
            body = self._get_message_body(message)
            
            # Parse date
            try:
                # Gmail date format: Mon, 15 May 2023 14:30:00 +0000
                received_at = datetime.strptime(date_str.split('+')[0].split('-')[0].strip(), 
                                               '%a, %d %b %Y %H:%M:%S')
            except:
                received_at = datetime.utcnow()
            
            return {
                'message_id': message['id'],
                'from_address': from_addr,
                'to_address': to_addr,
                'subject': subject,
                'body': body,
                'received_at': received_at,
                'is_read': 'UNREAD' not in message.get('labels', [])
            }
        except Exception as e:
            print(f"Error parsing message: {e}")
            return {}
    
    def _get_message_body(self, message: Dict) -> str:
        """
        Extract message body
        """
        try:
            payload = message['payload']
            
            # Check for parts
            if 'parts' in payload:
                # Multipart message
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part.get('body', {}).get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
                # If no plain text, try HTML
                for part in payload['parts']:
                    if part['mimeType'] == 'text/html':
                        data = part.get('body', {}).get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                # Single part message
                data = payload.get('body', {}).get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            
            return ''
        except Exception as e:
            print(f"Error extracting body: {e}")
            return ''
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark email as read
        """
        if not self.service:
            return False
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking as read: {e}")
            return False
    
    def archive_email(self, message_id: str) -> bool:
        """
        Archive email
        """
        if not self.service:
            return False
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error archiving: {e}")
            return False
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send email
        """
        if not self.service:
            return False
        
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False


class SupplierEmailManager:
    """
    Manages supplier email integration and flagging
    """
    
    def __init__(self, db: Session, email_provider: EmailProvider = None):
        self.db = db
        self.email_provider = email_provider or GmailProvider()
    
    def sync_supplier_emails(self) -> Dict:
        """
        Sync emails from all supplier contacts
        """
        # Get all supplier contact emails
        contacts = self.db.query(Contact).filter(Contact.email.isnot(None)).all()
        supplier_emails = [c.email for c in contacts if c.email]
        
        if not supplier_emails:
            return {'success': False, 'message': 'No supplier emails to sync'}
        
        try:
            # Get emails from provider
            emails = self.email_provider.get_emails(supplier_emails)
            
            # Save to database
            synced = 0
            for email_data in emails:
                if self._save_email(email_data):
                    synced += 1
            
            return {
                'success': True,
                'synced': synced,
                'message': f"Synced {synced} emails from supplier contacts"
            }
        
        except Exception as e:
            return {'success': False, 'message': f"Sync failed: {str(e)}"}
    
    def _save_email(self, email_data: Dict) -> bool:
        """
        Save email to database if not already saved
        """
        try:
            # Check if email already exists
            if self.db.query(SupplierEmail).filter(
                SupplierEmail.gmail_message_id == email_data.get('message_id')
            ).first():
                return False
            
            # Find supplier from contact email
            from_email = email_data.get('from_address', '').split('<')[-1].rstrip('>')
            contact = self.db.query(Contact).filter(
                Contact.email == from_email
            ).first()
            
            if not contact:
                return False
            
            # Create email record
            supplier_email = SupplierEmail(
                supplier_id=contact.supplier_id,
                contact_id=contact.id,
                from_address=from_email,
                to_address=email_data.get('to_address', ''),
                subject=email_data.get('subject', ''),
                body=email_data.get('body', ''),
                received_at=email_data.get('received_at', datetime.utcnow()),
                is_read=email_data.get('is_read', False),
                is_flagged=True,  # Auto-flag supplier emails
                gmail_message_id=email_data.get('message_id'),
            )
            
            self.db.add(supplier_email)
            self.db.commit()
            return True
        
        except Exception as e:
            print(f"Error saving email: {e}")
            return False
    
    def get_supplier_inbox(self, supplier_id: Optional[int] = None) -> List[Dict]:
        """
        Get supplier emails (optionally filtered by supplier)
        """
        query = self.db.query(SupplierEmail).filter(
            SupplierEmail.is_flagged == True,
            SupplierEmail.is_archived == False
        )
        
        if supplier_id:
            query = query.filter(SupplierEmail.supplier_id == supplier_id)
        
        # Order by most recent
        query = query.order_by(SupplierEmail.received_at.desc())
        
        emails = query.all()
        return [e.to_dict() for e in emails]
    
    def mark_email_as_read(self, email_id: int) -> bool:
        """
        Mark email as read
        """
        email = self.db.query(SupplierEmail).filter(
            SupplierEmail.id == email_id
        ).first()
        
        if not email:
            return False
        
        email.is_read = True
        self.db.commit()
        return True
    
    def archive_email(self, email_id: int) -> bool:
        """
        Archive email
        """
        email = self.db.query(SupplierEmail).filter(
            SupplierEmail.id == email_id
        ).first()
        
        if not email:
            return False
        
        email.is_archived = True
        self.db.commit()
        return True
    
    def categorize_email(self, email_id: int, category: str) -> bool:
        """
        Categorize email
        """
        valid_categories = ['general', 'invoice', 'delivery', 'complaint', 'inquiry']
        
        if category not in valid_categories:
            return False
        
        email = self.db.query(SupplierEmail).filter(
            SupplierEmail.id == email_id
        ).first()
        
        if not email:
            return False
        
        email.category = category
        self.db.commit()
        return True