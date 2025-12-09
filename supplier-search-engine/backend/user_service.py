#!/usr/bin/env python3
"""User Management Service

Handles user authentication, favorites, notes, inbox, and preferences.
Includes Walmart SSO integration.
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
import json
import hashlib
from enum import Enum

# ============================================================================
# DATA MODELS
# ============================================================================

class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"

class User:
    """User object."""
    def __init__(self, email: str, name: str, walmart_id: Optional[str] = None, role: UserRole = UserRole.USER):
        self.email = email
        self.name = name
        self.walmart_id = walmart_id  # Walmart employee ID from SSO
        self.role = role
        self.created_at = datetime.now()
        self.last_login = None
        self.is_sso = walmart_id is not None
        
    def to_dict(self):
        return {
            "email": self.email,
            "name": self.name,
            "walmart_id": self.walmart_id,
            "role": self.role.value,
            "is_sso": self.is_sso,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class Favorite:
    """Favorite supplier."""
    def __init__(self, user_email: str, supplier_id: int, supplier_name: str):
        self.user_email = user_email
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.created_at = datetime.now()
        
    def to_dict(self):
        return {
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier_name,
            "created_at": self.created_at.isoformat()
        }

class Note:
    """Note on a supplier."""
    def __init__(self, user_email: str, supplier_id: int, content: str):
        self.id = hashlib.md5(f"{user_email}-{supplier_id}-{datetime.now()}".encode()).hexdigest()[:8]
        self.user_email = user_email
        self.supplier_id = supplier_id
        self.content = content
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def to_dict(self):
        return {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class InboxMessage:
    """Message in user inbox."""
    def __init__(self, user_email: str, subject: str, message: str, sender: str = "System", msg_type: str = "info"):
        self.id = hashlib.md5(f"{user_email}-{subject}-{datetime.now()}".encode()).hexdigest()[:8]
        self.user_email = user_email
        self.subject = subject
        self.message = message
        self.sender = sender
        self.msg_type = msg_type  # info, warning, alert, success
        self.created_at = datetime.now()
        self.read = False
        
    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "message": self.message,
            "sender": self.sender,
            "type": self.msg_type,
            "created_at": self.created_at.isoformat(),
            "read": self.read
        }

# ============================================================================
# USER SERVICE
# ============================================================================

class UserService:
    """Service for managing users, favorites, notes, and inbox."""
    
    def __init__(self):
        # In-memory storage (replace with database in production)
        self.users: Dict[str, User] = {}
        self.favorites: Dict[str, List[Favorite]] = {}  # user_email -> [Favorite]
        self.notes: Dict[str, List[Note]] = {}  # user_email -> [Note]
        self.inbox: Dict[str, List[InboxMessage]] = {}  # user_email -> [InboxMessage]
        self.sessions: Dict[str, Dict] = {}  # session_token -> {user_email, expires}
        
    # ========================================================================
    # AUTHENTICATION
    # ========================================================================
    
    def register_user(self, email: str, name: str, walmart_id: Optional[str] = None) -> User:
        """Register a new user (from SSO or manual registration)."""
        if email in self.users:
            return self.users[email]
        
        role = UserRole.USER
        if walmart_id and self._is_walmart_manager(walmart_id):
            role = UserRole.MANAGER
        
        user = User(email, name, walmart_id, role)
        self.users[email] = user
        self.favorites[email] = []
        self.notes[email] = []
        self.inbox[email] = []
        
        # Add welcome message
        welcome_msg = InboxMessage(
            email,
            "Welcome to Supplier Hub",
            f"Welcome {name}! Start exploring suppliers and managing your favorites.",
            sender="Walmart Supplier Hub",
            msg_type="success"
        )
        self.inbox[email].append(welcome_msg)
        
        return user
    
    def login_sso(self, walmart_id: str, email: str, name: str) -> tuple[User, str]:
        """Handle Walmart SSO login.
        
        In production, this would validate against Azure AD or similar.
        For now, we trust the SSO provider has already validated the user.
        """
        user = self.register_user(email, name, walmart_id)
        user.last_login = datetime.now()
        
        # Create session
        session_token = hashlib.sha256(f"{email}-{datetime.now()}".encode()).hexdigest()
        self.sessions[session_token] = {
            "user_email": email,
            "expires": (datetime.now() + timedelta(days=7)).isoformat(),
            "sso": True
        }
        
        return user, session_token
    
    def validate_session(self, session_token: str) -> Optional[User]:
        """Validate a session token and return user."""
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        expires = datetime.fromisoformat(session["expires"])
        
        if datetime.now() > expires:
            del self.sessions[session_token]
            return None
        
        user_email = session["user_email"]
        return self.users.get(user_email)
    
    def logout(self, session_token: str) -> bool:
        """Logout user by removing session."""
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False
    
    # ========================================================================
    # FAVORITES
    # ========================================================================
    
    def add_favorite(self, user_email: str, supplier_id: int, supplier_name: str) -> bool:
        """Add supplier to favorites."""
        if user_email not in self.favorites:
            self.favorites[user_email] = []
        
        # Check if already favorited
        if any(f.supplier_id == supplier_id for f in self.favorites[user_email]):
            return False
        
        favorite = Favorite(user_email, supplier_id, supplier_name)
        self.favorites[user_email].append(favorite)
        
        # Add inbox notification
        msg = InboxMessage(
            user_email,
            f"{supplier_name} added to favorites",
            f"You favorited {supplier_name}. You can view all favorites in your preferences.",
            sender="Walmart Supplier Hub",
            msg_type="info"
        )
        self.inbox[user_email].append(msg)
        
        return True
    
    def remove_favorite(self, user_email: str, supplier_id: int) -> bool:
        """Remove supplier from favorites."""
        if user_email not in self.favorites:
            return False
        
        self.favorites[user_email] = [
            f for f in self.favorites[user_email]
            if f.supplier_id != supplier_id
        ]
        return True
    
    def get_favorites(self, user_email: str) -> List[Dict]:
        """Get user's favorite suppliers."""
        if user_email not in self.favorites:
            return []
        return [f.to_dict() for f in self.favorites[user_email]]
    
    def is_favorite(self, user_email: str, supplier_id: int) -> bool:
        """Check if supplier is favorited."""
        if user_email not in self.favorites:
            return False
        return any(f.supplier_id == supplier_id for f in self.favorites[user_email])
    
    # ========================================================================
    # NOTES
    # ========================================================================
    
    def add_note(self, user_email: str, supplier_id: int, content: str) -> Dict:
        """Add note to supplier."""
        if user_email not in self.notes:
            self.notes[user_email] = []
        
        note = Note(user_email, supplier_id, content)
        self.notes[user_email].append(note)
        
        return note.to_dict()
    
    def update_note(self, user_email: str, note_id: str, content: str) -> Optional[Dict]:
        """Update existing note."""
        if user_email not in self.notes:
            return None
        
        for note in self.notes[user_email]:
            if note.id == note_id:
                note.content = content
                note.updated_at = datetime.now()
                return note.to_dict()
        
        return None
    
    def delete_note(self, user_email: str, note_id: str) -> bool:
        """Delete a note."""
        if user_email not in self.notes:
            return False
        
        initial_length = len(self.notes[user_email])
        self.notes[user_email] = [n for n in self.notes[user_email] if n.id != note_id]
        return len(self.notes[user_email]) < initial_length
    
    def get_notes(self, user_email: str, supplier_id: Optional[int] = None) -> List[Dict]:
        """Get user's notes, optionally filtered by supplier."""
        if user_email not in self.notes:
            return []
        
        notes = self.notes[user_email]
        if supplier_id:
            notes = [n for n in notes if n.supplier_id == supplier_id]
        
        return [n.to_dict() for n in notes]
    
    # ========================================================================
    # INBOX
    # ========================================================================
    
    def get_inbox(self, user_email: str, unread_only: bool = False) -> List[Dict]:
        """Get user's inbox messages."""
        if user_email not in self.inbox:
            return []
        
        messages = self.inbox[user_email]
        if unread_only:
            messages = [m for m in messages if not m.read]
        
        # Sort by newest first
        messages = sorted(messages, key=lambda m: m.created_at, reverse=True)
        return [m.to_dict() for m in messages]
    
    def mark_as_read(self, user_email: str, message_id: str) -> bool:
        """Mark message as read."""
        if user_email not in self.inbox:
            return False
        
        for msg in self.inbox[user_email]:
            if msg.id == message_id:
                msg.read = True
                return True
        
        return False
    
    def mark_all_as_read(self, user_email: str) -> int:
        """Mark all messages as read. Returns count of updated messages."""
        if user_email not in self.inbox:
            return 0
        
        count = sum(1 for m in self.inbox[user_email] if not m.read)
        for msg in self.inbox[user_email]:
            msg.read = True
        
        return count
    
    def delete_message(self, user_email: str, message_id: str) -> bool:
        """Delete message from inbox."""
        if user_email not in self.inbox:
            return False
        
        initial_length = len(self.inbox[user_email])
        self.inbox[user_email] = [m for m in self.inbox[user_email] if m.id != message_id]
        return len(self.inbox[user_email]) < initial_length
    
    def get_unread_count(self, user_email: str) -> int:
        """Get count of unread messages."""
        if user_email not in self.inbox:
            return 0
        return sum(1 for m in self.inbox[user_email] if not m.read)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _is_walmart_manager(self, walmart_id: str) -> bool:
        """Check if user is a Walmart manager based on ID.
        
        In production, this would check against Walmart's directory service.
        For now, we check if the ID starts with 'M' (mock implementation).
        """
        return walmart_id.startswith('M') if walmart_id else False
    
    def get_user(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.users.get(email)

# Create global instance
user_service = UserService()
