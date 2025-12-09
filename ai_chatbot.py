#!/usr/bin/env python3
"""
AI Chatbot for Supplier Hub
Provides intelligent suggestions and performs supplier-related actions
"""

import os
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum
import re

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from database_schema import Supplier, Contact, SupplierEmail, SupplierNote
from sqlalchemy.orm import Session


class ActionType(str, Enum):
    """Types of actions the chatbot can perform"""
    INFO_REQUEST = "info_request"
    CREATE_SUPPLIER = "create_supplier"
    UPDATE_SUPPLIER = "update_supplier"
    ADD_CONTACT = "add_contact"
    SEND_EMAIL = "send_email"
    CREATE_NOTE = "create_note"
    SEARCH_SUPPLIER = "search_supplier"
    SUGGEST_SUPPLIER = "suggest_supplier"
    ANALYZE_EMAILS = "analyze_emails"
    GET_STATS = "get_stats"
    UNKNOWN = "unknown"


class ChatbotAction:
    """Represents an action to be performed"""
    
    def __init__(self, action_type: ActionType, params: Dict = None, confidence: float = 1.0):
        self.action_type = action_type
        self.params = params or {}
        self.confidence = confidence
        self.result = None
        self.error = None
    
    def to_dict(self) -> Dict:
        return {
            'type': self.action_type.value,
            'params': self.params,
            'confidence': self.confidence,
            'result': self.result,
            'error': self.error,
        }


class SupplierChatbot:
    """
    AI-powered chatbot for supplier management
    
    Features:
    - Answer supplier-related questions
    - Suggest suppliers based on criteria
    - Create/update suppliers
    - Manage contacts
    - Analyze emails
    - Provide insights and recommendations
    """
    
    SYSTEM_PROMPT = """You are an intelligent supplier management assistant for a Walmart supplier hub. 
    Your role is to:
    1. Help users find and manage suppliers
    2. Answer questions about suppliers and their contacts
    3. Suggest suppliers based on criteria (category, location, rating, etc.)
    4. Help create and update supplier profiles
    5. Analyze supplier emails and communications
    6. Provide recommendations for supplier improvements
    7. Offer insights on supplier performance and patterns
    
    When users ask about suppliers, be specific and factual. When suggesting actions,
    explain why they would be beneficial. Always ask for clarification if needed.
    """
    
    def __init__(self, db: Session, api_key: str = None):
        self.db = db
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.conversation_history = []
        
        if OPENAI_AVAILABLE and self.api_key:
            openai.api_key = self.api_key
            self.ai_enabled = True
        else:
            self.ai_enabled = False
    
    def chat(self, user_message: str) -> Dict:
        """
        Process user message and return response
        """
        # Add to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Parse intent and extract action
        action = self._parse_intent(user_message)
        
        # Execute action if recognized
        action_result = self._execute_action(action)
        
        # Generate response
        response = self._generate_response(user_message, action, action_result)
        
        # Add response to history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
        return {
            'message': response,
            'action': action.to_dict() if action else None,
            'timestamp': datetime.utcnow().isoformat(),
        }
    
    def _parse_intent(self, user_message: str) -> Optional[ChatbotAction]:
        """
        Parse user message to determine intent and action
        """
        message_lower = user_message.lower()
        
        # Search for suppliers
        if any(keyword in message_lower for keyword in ['find', 'search', 'show me', 'list', 'which suppliers']):
            # Extract category or location if present
            params = self._extract_search_params(user_message)
            return ChatbotAction(ActionType.SEARCH_SUPPLIER, params)
        
        # Create new supplier
        if any(keyword in message_lower for keyword in ['add supplier', 'create supplier', 'new supplier', 'register supplier']):
            params = self._extract_supplier_params(user_message)
            return ChatbotAction(ActionType.CREATE_SUPPLIER, params)
        
        # Update supplier
        if any(keyword in message_lower for keyword in ['update supplier', 'modify supplier', 'edit supplier', 'change supplier']):
            params = self._extract_supplier_params(user_message)
            return ChatbotAction(ActionType.UPDATE_SUPPLIER, params)
        
        # Add contact
        if any(keyword in message_lower for keyword in ['add contact', 'new contact', 'add person', 'add representative']):
            params = self._extract_contact_params(user_message)
            return ChatbotAction(ActionType.ADD_CONTACT, params)
        
        # Suggest suppliers
        if any(keyword in message_lower for keyword in ['suggest', 'recommend', 'what supplier', 'which supplier should']):
            params = self._extract_search_params(user_message)
            return ChatbotAction(ActionType.SUGGEST_SUPPLIER, params)
        
        # Analyze emails
        if any(keyword in message_lower for keyword in ['analyze', 'email', 'emails from', 'recent communication']):
            params = self._extract_email_params(user_message)
            return ChatbotAction(ActionType.ANALYZE_EMAILS, params)
        
        # Get statistics
        if any(keyword in message_lower for keyword in ['stats', 'statistics', 'how many', 'total suppliers']):
            return ChatbotAction(ActionType.GET_STATS, {})
        
        # Default to info request
        return ChatbotAction(ActionType.INFO_REQUEST, {'query': user_message})
    
    def _extract_search_params(self, message: str) -> Dict:
        """
        Extract search parameters from message
        """
        params = {}
        
        # Extract category
        categories = ['lumber', 'concrete', 'electrical', 'plumbing', 'hardware', 'materials', 'equipment']
        for cat in categories:
            if cat in message.lower():
                params['category'] = cat
                break
        
        # Extract location/state
        states = ['california', 'texas', 'florida', 'new york', 'pa', 'texas']
        for state in states:
            if state in message.lower():
                params['location'] = state
                break
        
        # Extract rating preference
        if 'highly rated' in message.lower() or 'top rated' in message.lower():
            params['min_rating'] = 4.5
        elif 'good' in message.lower():
            params['min_rating'] = 4.0
        
        return params
    
    def _extract_supplier_params(self, message: str) -> Dict:
        """
        Extract supplier parameters from message
        """
        params = {}
        
        # Extract name
        # Simple pattern: "Company Name Inc" or "name: XYZ"
        name_match = re.search(r'(?:name:|called|named|company:)\s+([A-Z][A-Za-z0-9\s&]+)', message)
        if name_match:
            params['name'] = name_match.group(1).strip()
        
        # Extract category
        categories = ['lumber', 'concrete', 'electrical', 'plumbing', 'hardware', 'materials']
        for cat in categories:
            if cat in message.lower():
                params['category'] = cat
                break
        
        # Extract location
        if 'location:' in message.lower():
            loc_match = re.search(r'location:\s+([A-Za-z\s,]+?)(?:phone|email|$)', message)
            if loc_match:
                params['location'] = loc_match.group(1).strip()
        
        # Extract phone
        phone_match = re.search(r'(?:phone:|ph:|tel:)\s+([\d\-\s\(\)\+]+)', message)
        if phone_match:
            params['phone'] = phone_match.group(1).strip()
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message)
        if email_match:
            params['email'] = email_match.group(0)
        
        return params
    
    def _extract_contact_params(self, message: str) -> Dict:
        """
        Extract contact parameters from message
        """
        params = {}
        
        # Extract supplier name
        if 'at ' in message.lower():
            at_match = re.search(r'at\s+([A-Z][A-Za-z0-9\s&]+?)(?:\s+(?:with|phone|email)|$)', message)
            if at_match:
                params['supplier_name'] = at_match.group(1).strip()
        
        # Extract names
        name_match = re.search(r'(?:name:|contact:)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)', message)
        if name_match:
            params['first_name'] = name_match.group(1)
            params['last_name'] = name_match.group(2)
        
        # Extract title/role
        title_match = re.search(r'(?:title:|role:|position:)\s+([^,]+?)(?:,|$)', message)
        if title_match:
            params['title'] = title_match.group(1).strip()
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message)
        if email_match:
            params['email'] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(r'(?:phone:|tel:)\s+([\d\-\s\(\)\+]+)', message)
        if phone_match:
            params['phone'] = phone_match.group(1).strip()
        
        return params
    
    def _extract_email_params(self, message: str) -> Dict:
        """
        Extract email analysis parameters
        """
        params = {}
        
        # Extract supplier name
        if 'from ' in message.lower():
            from_match = re.search(r'from\s+([A-Z][A-Za-z0-9\s&]+?)(?:\s+(?:emails|messages|contact)|$)', message)
            if from_match:
                params['supplier_name'] = from_match.group(1).strip()
        
        # Extract time period
        if 'last' in message.lower():
            period_match = re.search(r'last\s+(\d+)\s+(days?|weeks?|months?)', message)
            if period_match:
                params['days'] = int(period_match.group(1))
        
        return params
    
    def _execute_action(self, action: ChatbotAction) -> Optional[Dict]:
        """
        Execute the action and return result
        """
        if not action:
            return None
        
        try:
            if action.action_type == ActionType.SEARCH_SUPPLIER:
                return self._search_suppliers(action.params)
            
            elif action.action_type == ActionType.SUGGEST_SUPPLIER:
                return self._suggest_suppliers(action.params)
            
            elif action.action_type == ActionType.GET_STATS:
                return self._get_statistics()
            
            elif action.action_type == ActionType.ANALYZE_EMAILS:
                return self._analyze_supplier_emails(action.params)
            
            # Other actions are created but not auto-executed (need user confirmation)
            return None
        
        except Exception as e:
            action.error = str(e)
            return None
    
    def _search_suppliers(self, params: Dict) -> Dict:
        """
        Search for suppliers
        """
        query = self.db.query(Supplier).filter(Supplier.is_active == True)
        
        if 'category' in params:
            query = query.filter(Supplier.category.ilike(f"%{params['category']}%"))
        
        if 'location' in params:
            query = query.filter(Supplier.location.ilike(f"%{params['location']}%"))
        
        if 'min_rating' in params:
            query = query.filter(Supplier.rating >= params['min_rating'])
        
        suppliers = query.limit(10).all()
        
        return {
            'count': len(suppliers),
            'suppliers': [{
                'id': s.id,
                'name': s.name,
                'category': s.category,
                'rating': s.rating,
                'location': s.location
            } for s in suppliers]
        }
    
    def _suggest_suppliers(self, params: Dict) -> Dict:
        """
        Suggest suppliers based on criteria
        """
        # Similar to search but with recommendations
        results = self._search_suppliers(params)
        
        # Add reasoning
        suggestions = []
        for supplier in results['suppliers']:
            suggestions.append({
                **supplier,
                'reason': f"Good match for {params.get('category', 'your needs')} "
                         f"in {params.get('location', 'your area')} with a rating of {supplier['rating']}/5"
            })
        
        return {
            'count': len(suggestions),
            'suggestions': suggestions
        }
    
    def _get_statistics(self) -> Dict:
        """
        Get supplier statistics
        """
        total = self.db.query(Supplier).filter(Supplier.is_active == True).count()
        verified = self.db.query(Supplier).filter(
            Supplier.is_active == True,
            Supplier.walmart_verified == True
        ).count()
        avg_rating = self.db.query(Supplier).filter(
            Supplier.is_active == True
        ).with_entities(
            __import__('sqlalchemy').func.avg(Supplier.rating)
        ).scalar() or 0
        
        # Count by category
        from sqlalchemy import func
        by_category = self.db.query(
            Supplier.category,
            func.count(Supplier.id)
        ).filter(Supplier.is_active == True).group_by(Supplier.category).all()
        
        return {
            'total_suppliers': total,
            'walmart_verified': verified,
            'average_rating': float(avg_rating),
            'by_category': {
                cat: count for cat, count in by_category
            }
        }
    
    def _analyze_supplier_emails(self, params: Dict) -> Dict:
        """
        Analyze emails from suppliers
        """
        query = self.db.query(SupplierEmail).filter(
            SupplierEmail.is_flagged == True,
            SupplierEmail.is_archived == False
        )
        
        if 'supplier_name' in params:
            query = query.join(Supplier).filter(
                Supplier.name.ilike(f"%{params['supplier_name']}%")
            )
        
        emails = query.order_by(SupplierEmail.received_at.desc()).limit(20).all()
        
        # Analyze
        by_category = {}
        unread_count = 0
        
        for email in emails:
            cat = email.category or 'general'
            by_category[cat] = by_category.get(cat, 0) + 1
            if not email.is_read:
                unread_count += 1
        
        return {
            'total_emails': len(emails),
            'unread_count': unread_count,
            'by_category': by_category,
            'recent_emails': [{
                'from': email.from_address,
                'subject': email.subject,
                'received_at': email.received_at.isoformat()
            } for email in emails[:5]]
        }
    
    def _generate_response(self, user_message: str, action: ChatbotAction, action_result: Dict) -> str:
        """
        Generate response to user
        """
        if self.ai_enabled:
            return self._generate_ai_response(user_message, action, action_result)
        else:
            return self._generate_template_response(action, action_result)
    
    def _generate_ai_response(self, user_message: str, action: ChatbotAction, action_result: Dict) -> str:
        """
        Generate response using OpenAI
        """
        try:
            context = f"""
User asked: {user_message}
Action identified: {action.action_type.value if action else 'unknown'}
Action result: {json.dumps(action_result, default=str) if action_result else 'None'}
"""
            
            messages = self.conversation_history + [{
                'role': 'user',
                'content': context
            }]
            
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=messages,
                system=self.SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=500
            )
            
            return response['choices'][0]['message']['content']
        
        except Exception as e:
            return self._generate_template_response(action, action_result)
    
    def _generate_template_response(self, action: ChatbotAction, action_result: Dict) -> str:
        """
        Generate response using templates (fallback)
        """
        if not action:
            return "I'm not sure how to help with that. Could you clarify what you'd like to do?"
        
        if action.action_type == ActionType.SEARCH_SUPPLIER and action_result:
            count = action_result.get('count', 0)
            if count == 0:
                return "I didn't find any suppliers matching your criteria. Would you like to try different filters?"
            else:
                suppliers = action_result.get('suppliers', [])
                response = f"Found {count} suppliers:\n"
                for s in suppliers[:5]:
                    response += f"- {s['name']} ({s['category']}) - Rating: {s['rating']}/5\n"
                return response
        
        elif action.action_type == ActionType.SUGGEST_SUPPLIER and action_result:
            suggestions = action_result.get('suggestions', [])
            if not suggestions:
                return "I couldn't find any suppliers matching your criteria."
            response = "Here are my suggestions:\n"
            for s in suggestions[:3]:
                response += f"- {s['name']}: {s['reason']}\n"
            return response
        
        elif action.action_type == ActionType.GET_STATS and action_result:
            return f"""Supplier Statistics:
- Total Active Suppliers: {action_result.get('total_suppliers', 0)}
- Walmart Verified: {action_result.get('walmart_verified', 0)}
- Average Rating: {action_result.get('average_rating', 0):.2f}/5.0

By Category:
{json.dumps(action_result.get('by_category', {}), indent=2)}"""
        
        elif action.action_type == ActionType.ANALYZE_EMAILS and action_result:
            return f"""Email Analysis:
- Total Supplier Emails: {action_result.get('total_emails', 0)}
- Unread: {action_result.get('unread_count', 0)}

By Category:
{json.dumps(action_result.get('by_category', {}), indent=2)}

Recent Emails:
{json.dumps(action_result.get('recent_emails', []), indent=2, default=str)}"""
        
        return "Action identified. How would you like to proceed?"