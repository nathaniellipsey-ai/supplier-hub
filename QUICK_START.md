# 🚀 QUICK START GUIDE - Advanced Features

## What's New

Your supplier hub now has 6 major new features implemented and ready to integrate:

1. ✅ **Editable Supplier Profiles** - Modify any supplier information
2. ✅ **Contact Management** - Add unlimited contacts per supplier
3. ✅ **Email Integration** - Gmail auto-flagging of supplier emails
4. ✅ **Create Suppliers** - Add new suppliers manually
5. ✅ **CSV Import** - Bulk import hundreds of suppliers
6. ✅ **AI Chatbot** - Ask questions about suppliers

---

## 📦 Files You Now Have

### Core Python Modules (Backend)
```
✅ database_schema.py       - Database models for suppliers, contacts, emails
✅ csv_importer.py          - CSV parsing and bulk import logic
✅ email_integration.py      - Gmail OAuth and email flagging
✅ ai_chatbot.py            - AI assistant for supplier queries
✅ api_endpoints.py         - All REST API endpoints (20+)
```

### Frontend
```
✅ supplier-modals.html     - UI modals, forms, and chatbot widget
```

### Documentation
```
✅ FEATURE_GUIDE.md         - Complete user guide (500+ lines)
✅ ADVANCED_FEATURES_IMPLEMENTATION.md - Technical details
✅ QUICK_START.md           - This file
```

---

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (2 min)

```bash
pip install sqlalchemy pandas google-auth google-auth-oauthlib google-api-python-client openai
```

Or update your `requirements.txt`:
```
sqlalchemy>=2.0
pandas>=1.5
python-multipart>=0.0.5
google-auth>=2.20
google-auth-oauthlib
google-api-python-client
openai>=0.27
python-dotenv>=0.20
```

### Step 2: Add Files to Your Project (1 min)

Copy these files to your supplier-hub directory:
```
database_schema.py
csv_importer.py
email_integration.py
ai_chatbot.py
api_endpoints.py
supplier-modals.html
```

### Step 3: Update app_minimal.py (2 min)

```python
# At the top of app_minimal.py, add:

from database_schema import Base, Supplier, Contact, SupplierEmail, SupplierNote
from api_endpoints import router as supplier_router

# Create tables (near where you create other tables)
Base.metadata.create_all(bind=engine)

# Include the new router (near other app.include_router calls)
app.include_router(supplier_router)
```

### Step 4: Add Modal HTML to index.html

Before the closing `</body>` tag in your HTML:

```html
<!-- Include supplier management modals and chatbot -->
<script>
    // Load the modals HTML
    fetch('supplier-modals.html')
        .then(r => r.text())
        .then(html => document.body.insertAdjacentHTML('beforeend', html));
</script>
```

### Step 5: Test!

Start your server:
```bash
python -m uvicorn app_minimal:app --reload
```

Visit `http://localhost:8000` and look for new buttons:
- "Edit" button on supplier cards
- "Manage Contacts" button
- "Add New Supplier" button
- "Import Suppliers" button
- "🤖 Supplier Assistant" chatbot (bottom-right)

---

## 🎯 Basic Usage

### Edit a Supplier
1. Click any supplier card
2. Click "📝 Edit" button
3. Modify fields
4. Click "Save Changes"

### Add a Contact
1. Click supplier → "Manage Contacts"
2. Fill in contact details
3. Click "Add Contact"

### Import Suppliers
1. Prepare CSV file (see CSV format below)
2. Click "Import Suppliers"
3. Select file
4. Done! Suppliers are in database

### Chat with AI
1. Click "🤖" chatbot in bottom-right
2. Type question like:
   - "Find suppliers in Texas"
   - "Show me highly-rated lumber suppliers"
   - "What's our average supplier rating?"
3. Chatbot responds with info or executes action

---

## 📋 CSV Import Format

Create a file `suppliers.csv`:

```csv
name,category,website,phone,email,location,contact_first_name,contact_last_name,contact_title,contact_email
ABC Lumber,Lumber,https://abc-lumber.com,555-0001,info@abc-lumber.com,New York,John,Smith,Sales,john@abc-lumber.com
XYZ Concrete,Concrete,https://xyz-concrete.com,555-0002,sales@xyz-concrete.com,Texas,Jane,Doe,Manager,jane@xyz-concrete.com
```

Then import via the UI.

---

## 📧 Email Integration (Optional)

### Setup Gmail Auto-Flagging

1. **Get Gmail Credentials:**
   - Go to https://console.cloud.google.com
   - Create new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download credentials.json

2. **Add to Environment:**
   ```bash
   export GMAIL_CREDENTIALS_JSON=/path/to/credentials.json
   ```

3. **Use in App:**
   - Click "Connect Email"
   - Authenticate with Google
   - System starts syncing
   - Supplier emails appear in inbox

---

## 🤖 AI Chatbot (Optional)

### Enable AI Features

1. **Get OpenAI Key:**
   - Go to https://platform.openai.com/api_keys
   - Create new secret key

2. **Add to Environment:**
   ```bash
   export OPENAI_API_KEY=sk-...
   ```

3. **Use Chatbot:**
   - Click "🤖" icon (bottom-right)
   - Ask questions in natural language
   - Get intelligent responses

---

## 🔗 API Examples

### Search Suppliers

```javascript
fetch('/api/suppliers?category=Lumber&min_rating=4.0')
    .then(r => r.json())
    .then(data => console.log(data.suppliers))
```

### Create Supplier

```javascript
fetch('/api/suppliers', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: 'New Company',
        category: 'Lumber',
        website: 'https://newco.com'
    })
})
```

### Add Contact

```javascript
fetch('/api/suppliers/123/contacts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        title: 'Sales Manager'
    })
})
```

### Chat with Bot

```javascript
fetch('/api/chatbot/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Find suppliers in Texas' })
})
    .then(r => r.json())
    .then(data => console.log(data.message))
```

---

## 🐛 Troubleshooting

### "Module not found: database_schema"
- Make sure all .py files are in the same directory as app_minimal.py
- Or add to PYTHONPATH

### "Modals not showing"
- Make sure supplier-modals.html is in the same directory
- Check browser console for errors
- Ensure script is loading before index.html closes body

### "Email integration not working"
- Check Google OAuth credentials file exists
- Verify GMAIL_CREDENTIALS_JSON env var is set
- Check Gmail API is enabled in Google Cloud Console

### "Chatbot giving empty responses"
- Check OPENAI_API_KEY is set (optional)
- Chatbot works without it (template responses)
- Check database has suppliers loaded

---

## 📚 Learn More

- **User Guide:** Read `FEATURE_GUIDE.md` for detailed instructions
- **Technical Details:** See `ADVANCED_FEATURES_IMPLEMENTATION.md`
- **API Docs:** Check api_endpoints.py for all endpoints
- **Database:** See database_schema.py for table structure

---

## ✨ Key Features Summary

| Feature | Status | Time to Setup |
|---------|--------|---------------|
| Editable Profiles | ✅ Ready | Instant |
| Contact Management | ✅ Ready | Instant |
| CSV Import | ✅ Ready | Instant |
| Email Integration | ✅ Ready | 5 min (optional) |
| AI Chatbot | ✅ Ready | 2 min (optional) |

---

## 🎉 You're All Set!

Your advanced supplier management system is ready to use. Start with:

1. **Try editing a supplier** → Click any supplier, hit Edit
2. **Add some contacts** → Manage Contacts, add names
3. **Import sample data** → Use CSV import with example
4. **Chat with bot** → Ask "Find suppliers in [state]"

Enjoy your enhanced Supplier Hub! 🚀

---

## 💬 Need Help?

Check these resources:

1. **FEATURE_GUIDE.md** - Complete user & admin guide
2. **ADVANCED_FEATURES_IMPLEMENTATION.md** - Technical architecture
3. **api_endpoints.py** - All available API endpoints
4. **database_schema.py** - Database model definitions

Happy supplying! 🎯