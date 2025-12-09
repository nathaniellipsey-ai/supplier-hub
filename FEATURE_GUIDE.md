# Supplier Hub - Advanced Features Guide

## 🚀 New Features Implemented

This guide covers the major new features added to the Supplier Hub platform.

---

## 1. 📝 EDITABLE SUPPLIER PROFILES

### Feature Overview

Every supplier profile can now be fully edited. Click on any supplier and access the edit interface.

### How to Use

1. **Find a supplier** in the search results
2. **Click on the supplier card** to view details
3. **Click "Edit Profile" button** in the modal
4. **Update any fields** you want to change:
   - Basic info (name, category, website, phone, email)
   - Company details (size, years in business, price range)
   - Ratings and verification status
5. **Click "Save Changes"** to commit

### Editable Fields

```
Basic Information:
- Name (required)
- Category
- Website URL
- Email address
- Phone number
- Location
- Description

Company Information:
- Years in Business
- Company Size (Solo, Small, Medium, Large)
- Price Range ($, $$, $$$, $$$$)

Rating & Verification:
- Rating (0-5.0 scale)
- AI Score (0-100)
- Walmart Verified checkbox
```

### Database Schema

Suppliers are stored with these editable fields:
```python
Supplier(
    id, name, category, description,
    website, primary_phone, primary_email,
    location, state, region,
    years_in_business, company_size, price_range,
    rating, ai_score, walmart_verified,
    products, certifications,
    created_at, updated_at, is_active
)
```

---

## 2. 👥 MULTIPLE CONTACT MANAGEMENT

### Feature Overview

Add and manage multiple contacts per supplier. Each contact can have their own title, email, phone, and notes.

### How to Use

1. **Click on a supplier**
2. **Click "Manage Contacts" button**
3. **Add new contacts:**
   - First Name (required)
   - Last Name (required)
   - Title/Role (e.g., "Sales Manager")
   - Department (e.g., "Sales", "Support")
   - Email address
   - Phone number
   - Check "Mark as Primary Contact" if needed
4. **Submit** to add contact
5. **Edit or delete** existing contacts in the list

### Contact Information

Each contact stores:
```python
Contact(
    id, supplier_id,
    first_name, last_name,
    title, email, phone,
    department,
    is_primary,  # Marks the main contact
    notes,
    created_at, updated_at
)
```

### Why Multiple Contacts?

- Different people for different departments
- Sales contact, support contact, billing contact, etc.
- Separate communication channels
- Better email routing and tracking
- Complete organizational mapping

---

## 3. 📧 EMAIL INTEGRATION & INBOX

### Feature Overview

Connected email inbox that **automatically flags emails** from your supplier contacts. Only supplier-related emails appear.

### How It Works

1. **Authentication:**
   - Connect your Gmail/email account via OAuth
   - Grant permission to read emails
   - Secure, read-only access

2. **Email Syncing:**
   - System tracks all supplier contact emails
   - Periodic sync pulls new emails
   - Emails matched against contact database

3. **Auto-Flagging:**
   - Any email from a known supplier contact = flagged
   - Flagged emails appear in supplier inbox
   - Regular emails hidden (not in supplier hub)

### Email Features

✅ **View supplier emails** in dedicated inbox
✅ **Mark as read** to track what you've seen
✅ **Archive emails** to clean up inbox
✅ **Categorize emails:**
   - General
   - Invoice
   - Delivery
   - Complaint
   - Inquiry

✅ **Email metadata:**
   - From address (linked to supplier contact)
   - Subject line
   - Received date/time
   - Associated supplier

### API Endpoints

```
POST   /api/email/authenticate    - Connect email account
POST   /api/email/sync            - Sync new emails from suppliers
GET    /api/email/inbox           - Get supplier emails
GET    /api/email/inbox?supplier_id=123  - Get emails from specific supplier
PUT    /api/email/{id}/read       - Mark email as read
PUT    /api/email/{id}/archive    - Archive email
PUT    /api/email/{id}/categorize - Set email category
```

### Example Flow

```
1. Setup email integration (one-time)
   ↓
2. Add supplier contacts with email addresses
   ↓
3. System starts monitoring those emails
   ↓
4. Email arrives from supplier contact
   ↓
5. System auto-flags it
   ↓
6. Email appears in Supplier Hub inbox
   ↓
7. You read, categorize, or archive
```

---

## 4. ➕ CREATE NEW SUPPLIERS

### Feature Overview

Manually create new supplier profiles directly in the app.

### How to Use

1. **Click "Add New Supplier" button** in toolbar
2. **Fill in supplier details:**
   - Name (required)
   - Category
   - Website
   - Email
   - Phone
   - Location
   - Description
3. **Click "Create Supplier"**
4. **Add contacts** afterward

### Quick Start

Minimum required fields to create:
- **Name** - Supplier company name

Optional fields (add later):
- Category, website, email, phone, location, description

---

## 5. 📊 BULK IMPORT SUPPLIERS

### Feature Overview

Import hundreds of suppliers at once from CSV or Excel files.

### CSV Format

**Required columns:**
- `name` - Supplier company name

**Optional columns:**
- `category` - Product category
- `website` - Company website URL
- `phone` - Business phone
- `email` - Business email
- `location` - City/State
- `state` - State code
- `region` - Region name
- `years_in_business` - Number
- `company_size` - Solo, Small, Medium, Large
- `price_range` - $, $$, $$$, $$$$
- `rating` - 0-5
- `products` - JSON array as string
- `certifications` - JSON array as string

**Contact columns (optional):**
- `contact_first_name`
- `contact_last_name`
- `contact_title`
- `contact_email`
- `contact_phone`
- `contact_department`

### Example CSV

```csv
name,category,website,phone,email,location,contact_first_name,contact_last_name,contact_title,contact_email
"ABC Lumber Co","Lumber","https://abc-lumber.com","555-0001","info@abc-lumber.com","New York","John","Smith","Sales Manager","john@abc-lumber.com"
"XYZ Concrete","Concrete","https://xyz-concrete.com","555-0002","sales@xyz-concrete.com","Texas","Jane","Doe","Account Executive","jane@xyz-concrete.com"
```

### How to Import

1. **Prepare CSV file** with supplier data
2. **Click "Import Suppliers" button**
3. **Upload CSV file**
4. **Review results:**
   - Created count
   - Updated count
   - Error messages
5. **Data is saved automatically**

### Import Processing

- ✅ **Deduplication:** If supplier name exists, updates instead of creates
- ✅ **Error handling:** Continues on errors, reports them
- ✅ **Contact creation:** Creates primary contact if contact columns provided
- ✅ **Transactions:** All-or-nothing, no partial imports
- ✅ **Validation:** Type checking, format validation

### Import Contacts

Separate CSV import for adding contacts to existing suppliers:

```csv
supplier_name,first_name,last_name,title,email,phone,department
"ABC Lumber Co","John","Smith","Sales Manager","john@abc-lumber.com","555-0001","Sales"
"ABC Lumber Co","Jane","Wilson","Support","jane@abc-lumber.com","555-0002","Support"
```

---

## 6. 🤖 AI CHATBOT ASSISTANT

### Feature Overview

Intelligent chatbot that:
- Answers supplier questions
- Searches suppliers based on criteria
- Suggests suppliers
- Analyzes emails
- Provides recommendations
- Helps manage suppliers

### How to Use

1. **Click chatbot icon** (bottom-right of screen)
2. **Type your question** in the input box
3. **Chat operates on context:**
   - Understands supplier-related queries
   - Extracts parameters from natural language
   - Provides relevant information

### Example Questions

**Search & Discovery:**
- "Find suppliers in the lumber category"
- "Show me highly-rated electrical suppliers in Texas"
- "List suppliers near New York"
- "What suppliers do we have for concrete?"

**Analysis:**
- "How many suppliers do we have?"
- "What's our average supplier rating?"
- "Analyze recent emails from ABC Lumber"
- "Show me unread emails from suppliers"

**Create/Update:**
- "Create a new supplier named XYZ Inc in the plumbing category"
- "Add John Smith from ABC Lumber as a contact"
- "Update ABC Lumber with a new phone number"

**Recommendations:**
- "Suggest a good electrical supplier in California"
- "Find suppliers rated 4.5 or higher"
- "Which suppliers should we work with more?"

### AI Capabilities

✅ **Intent Recognition**
- Understands supplier-related queries
- Extracts parameters (category, location, rating, etc.)
- Performs appropriate actions

✅ **Search & Filter**
- Filters by category
- Filters by location
- Filters by rating
- Combines multiple filters

✅ **Analysis**
- Email analysis and categorization
- Supplier statistics
- Performance metrics
- Trend identification

✅ **Natural Language**
- Conversational responses
- Context-aware suggestions
- Explanations of recommendations

### Chatbot Actions

```python
ActionType.SEARCH_SUPPLIER      # Find suppliers
ActionType.SUGGEST_SUPPLIER     # Recommend suppliers
ActionType.CREATE_SUPPLIER      # Create new supplier
ActionType.ADD_CONTACT          # Add contact person
ActionType.ANALYZE_EMAILS       # Analyze supplier emails
ActionType.GET_STATS            # Get statistics
ActionType.INFO_REQUEST         # Answer questions
```

### API Integration

```
POST /api/chatbot/chat
Body: { "message": "Find suppliers in Texas" }
Response: {
    "message": "AI response",
    "action": { "type": "search", "params": {...} },
    "timestamp": "2024-01-15T10:30:00"
}
```

---

## 7. 🔄 WORKFLOW EXAMPLES

### Example 1: Add a New Supplier with Contacts

```
1. Click "Add New Supplier"
2. Enter:
   - Name: "Premium Building Materials"
   - Category: "Lumber"
   - Website: https://premiumbuilding.com
   - Email: info@premiumbuilding.com
   - Phone: 555-7890
   - Location: Los Angeles, CA
3. Click "Create Supplier"
4. Click "Manage Contacts"
5. Add Contact 1:
   - John Smith, Sales Manager, john@premiumbuilding.com
6. Add Contact 2:
   - Jane Wilson, Support Lead, jane@premiumbuilding.com
7. Close modal
8. Supplier is ready with contacts!
```

### Example 2: Bulk Import with Contacts

```
1. Prepare CSV file with supplier data and contacts
2. Click "Import Suppliers"
3. Upload CSV
4. System creates suppliers and contacts
5. Reviews shows:
   - Created: 50 suppliers
   - Updated: 10 existing
   - Created: 75 contacts
6. All data is in system
```

### Example 3: Track Supplier Communication

```
1. Setup email integration (Gmail)
2. Add supplier contact emails
3. Email arrives from supplier
4. System auto-flags it
5. Read email in Supplier Hub inbox
6. Categorize as "Invoice" or "Inquiry"
7. Archive when done
8. All communication tracked per supplier
```

### Example 4: Find & Request Info via Chatbot

```
User: "Find me highly-rated concrete suppliers in Texas"
↓
Chatbot: "Found 12 suppliers:
- Concrete Pro: Rating 4.8/5, 25 years in business
- TXConcrete: Rating 4.6/5, 18 years in business
- ..."
↓
User: "Add their contacts to follow up"
↓
Chatbot: "Which suppliers? Or I can search for their contact info"
↓
User: "Add John from Concrete Pro"
↓
Chatbot: "Added John Smith (john@concretepro.com) to Concrete Pro"
```

---

## 8. 📈 DATABASE SCHEMA OVERVIEW

### Tables

```
suppliers
├── Basic Info (name, category, website, location)
├── Contact Info (phone, email)
├── Company Details (years_in_business, size, price_range)
├── Ratings (rating, ai_score, walmart_verified)
└── Timestamps (created_at, updated_at)
    ↓ relationships ↓
    
contacts (per supplier)
├── Person info (first_name, last_name, title)
├── Contact Info (email, phone)
├── Department
├── is_primary flag
└── Timestamps
    ↓ used for ↓
    
supplier_emails (auto-flagged)
├── Email metadata (from, to, subject, body)
├── Received timestamp
├── Read status
├── Is flagged (always true)
├── Category (general, invoice, etc.)
└── Gmail ID (for sync)
    
supplier_notes (user-created)
├── Note text
├── User email (who created)
├── Is pinned
└── Timestamps
```

---

## 9. 🔧 SETUP INSTRUCTIONS

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Update requirements.txt:**
   ```
   fastapi
   sqlalchemy
   pandas
   python-multipart
   google-auth-httplib2
   google-auth-oauthlib
   google-auth
   google-api-python-client
   openai  # Optional for AI features
   python-dotenv
   ```

3. **Include modals in HTML:**
   ```html
   <!-- In index.html before closing body -->
   <script src="supplier-modals.html"></script>
   ```

4. **Setup database:**
   ```python
   # In app_minimal.py
   from database_schema import Base
   Base.metadata.create_all(bind=engine)
   ```

5. **Configure email (optional):**
   - Download Google OAuth credentials
   - Set GMAIL_CREDENTIALS_JSON path
   - Users authenticate when needed

### Environment Variables

```bash
# .env
OPENAI_API_KEY=sk-...  # For AI chatbot
GMAIL_CREDENTIALS_JSON=/path/to/credentials.json
```

---

## 10. 📱 API REFERENCE

### Suppliers

```
GET    /api/suppliers                    - List all
GET    /api/suppliers/{id}               - Get one
POST   /api/suppliers                    - Create
PUT    /api/suppliers/{id}               - Update
DELETE /api/suppliers/{id}               - Delete
POST   /api/suppliers/import/csv         - Bulk import
```

### Contacts

```
GET    /api/suppliers/{id}/contacts      - List contacts
POST   /api/suppliers/{id}/contacts      - Create contact
PUT    /api/contacts/{id}                - Update contact
DELETE /api/contacts/{id}                - Delete contact
POST   /api/contacts/import/csv          - Bulk import
```

### Email

```
POST   /api/email/authenticate           - Setup email
POST   /api/email/sync                   - Sync emails
GET    /api/email/inbox                  - Get emails
PUT    /api/email/{id}/read              - Mark read
PUT    /api/email/{id}/archive           - Archive
PUT    /api/email/{id}/categorize        - Categorize
```

### Chatbot

```
POST   /api/chatbot/chat                 - Chat with AI
```

### Dashboard

```
GET    /api/dashboard/stats              - Get statistics
```

---

## 11. ✅ BEST PRACTICES

### Supplier Management

- ✅ Keep supplier info updated
- ✅ Add all contacts with email addresses
- ✅ Use consistent naming conventions
- ✅ Categorize suppliers clearly
- ✅ Maintain ratings as relationships develop

### Email Integration

- ✅ Always add contact emails for tracking
- ✅ Categorize emails for organization
- ✅ Archive handled communications
- ✅ Review unread emails regularly
- ✅ Use email categories for filtering

### Bulk Import

- ✅ Clean data before import
- ✅ Use consistent formats
- ✅ Test with small sample first
- ✅ Review error reports
- ✅ Validate imported data

### Chatbot Usage

- ✅ Use natural language
- ✅ Ask clear questions
- ✅ Provide context when needed
- ✅ Review suggestions critically
- ✅ Use for discovery and analysis

---

## 🎯 Summary

You now have a complete supplier management system with:

✅ Editable supplier profiles
✅ Multiple contacts per supplier
✅ Email integration and auto-flagging
✅ Manual supplier creation
✅ Bulk CSV import
✅ AI chatbot assistant
✅ Comprehensive API
✅ Full CRUD operations

Enjoy your enhanced Supplier Hub! 🚀