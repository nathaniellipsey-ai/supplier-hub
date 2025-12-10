# Supplier Hub Backend Module

🚀 **Production-ready backend module** for the Supplier Hub application.

## Overview

The backend module provides clean, composable services for:
- 🏢 Supplier management (CRUD operations)
- 👥 User account management and preferences
- 🔍 Advanced search and filtering
- 💾 Data import/export (CSV, JSON)
- 📧 Email and notification integrations
- 📊 Analytics and reporting

## Architecture

Follows **SOLID principles** with clear separation of concerns:

```
backend/
├── __init__.py           # Package initialization
├── models.py             # Pydantic data models (type safety)
├── services.py           # Business logic (SupplierService, UserService, DataService)
├── config.py             # Configuration management (settings, environment)
├── utils.py              # Utility functions (logging, validation, helpers)
├── integrations.py       # External service integrations
└── README.md             # This file
```

### Design Patterns Used

1. **Service Layer Pattern** - Business logic isolated in service classes
2. **Dependency Injection** - Services receive dependencies via constructor
3. **Factory Pattern** - IntegrationManager creates and manages integrations
4. **Singleton Pattern** - Configuration and logging setup

## Modules

### `models.py` - Data Models

Defines Pydantic models for type safety and validation:

```python
from backend.models import Supplier, SupplierCreate, SearchFilter

# Create supplier
supplier_data = SupplierCreate(
    name="Premier Supply Inc",
    category="Lumber & Wood Products",
    location="New York, NY",
    region="NY",
    rating=4.5,
    ai_score=85,
    products=["2x4 Lumber", "Plywood"],
    certifications=["ISO 9001"],
    walmart_verified=True,
    years_in_business=20,
    projects_completed=5000
)
```

### `services.py` - Business Logic

#### SupplierService
Manages supplier CRUD operations and search:

```python
from backend.services import SupplierService
from backend.models import SearchFilter

service = SupplierService()

# Create supplier
supplier = service.create(supplier_data)

# Search with filters
filters = SearchFilter(
    query="lumber",
    category="Lumber & Wood Products",
    min_rating=4.0,
    min_ai_score=80,
    limit=50
)
results = service.search(filters)
print(f"Found {results.total} suppliers")
print(f"Page has {len(results.items)} items")
print(f"Has next page: {results.has_next}")
```

#### UserService
Manages user accounts, favorites, and notes:

```python
from backend.services import UserService
from backend.models import UserCreate

user_service = UserService()

# Create user
user_data = UserCreate(
    username="john_doe",
    email="john@example.com",
    password="secure_password"
)
user = user_service.create_user(user_data)

# Manage favorites
user_service.add_favorite(user.id, supplier_id=123)
favorites = user_service.get_favorites(user.id)

# Manage notes
user_service.save_note(user.id, supplier_id=123, content="Great quality!")
note = user_service.get_note(user.id, supplier_id=123)
```

#### DataService
Handles data import/export operations:

```python
from backend.services import DataService, SupplierService

supplier_service = SupplierService()
data_service = DataService(supplier_service)

# Import suppliers from list
suppliers_data = [
    {
        'name': 'Supplier 1',
        'category': 'Lumber & Wood Products',
        'location': 'New York, NY',
        'region': 'NY',
        'rating': 4.5,
        'ai_score': 85,
        'products': ['Lumber'],
        'walmart_verified': True,
        'years_in_business': 20,
        'projects_completed': 5000
    }
]

count = data_service.import_suppliers_from_list(suppliers_data)
print(f"Imported {count} suppliers")

# Export suppliers
exported = data_service.export_suppliers()
print(f"Exported {len(exported)} suppliers")
```

### `config.py` - Configuration

Manage application settings with environment variables:

```python
from backend.config import settings

print(f"Environment: {settings.ENVIRONMENT}")
print(f"Debug: {settings.DEBUG}")
print(f"API Version: {settings.API_VERSION}")
print(f"Default page size: {settings.DEFAULT_PAGE_SIZE}")

if settings.is_production():
    print("Running in production mode")
```

**Environment Variables:**
- `ENVIRONMENT` - `development`, `staging`, or `production` (default: `development`)
- `DEBUG` - Enable debug mode (default: `true` in development)
- `HOST` - Server host (default: `127.0.0.1`)
- `PORT` - Server port (default: `8000`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `CORS_ORIGINS` - Comma-separated CORS origins

### `utils.py` - Utility Functions

Helper functions and response builders:

```python
from backend.utils import (
    setup_logging,
    validate_email,
    paginate,
    APIResponse,
    sanitize_dict
)

# Setup logging
setup_logging(log_level="DEBUG")

# Validate email
if validate_email("user@example.com"):
    print("Valid email")

# Paginate results
items = list(range(100))
paginated, total, page, pages = paginate(items, page=1, per_page=10)
print(f"Page 1 of {pages}")

# Create API response
response = APIResponse.success(
    data={"id": 1, "name": "Supplier"},
    message="Supplier created",
    code=201
)

# Paginated response
response = APIResponse.paginated(
    items=suppliers,
    total=100,
    page=1,
    per_page=50
)
```

### `integrations.py` - External Services

Manage integrations with third-party services:

```python
from backend.integrations import (
    CSVIntegration,
    EmailIntegration,
    NotificationIntegration,
    IntegrationManager
)

# CSV Integration
csv_integration = CSVIntegration()
csv_integration.connect()
rows = csv_integration.parse_csv(csv_content)
csv_output = csv_integration.generate_csv(rows)

# Notification Integration
notif_service = NotificationIntegration()
notif_service.connect()
notif_service.send_notification(
    user_id="user123",
    message="New supplier available!",
    notification_type="info"
)
user_notifications = notif_service.get_user_notifications("user123")

# Email Integration
email_service = EmailIntegration(
    smtp_server="smtp.gmail.com",
    smtp_port=587
)
email_service.connect()
email_service.send_email(
    to="supplier@example.com",
    subject="New Order",
    body="You have a new order"
)

# Integration Manager (manage all integrations)
manager = IntegrationManager()
manager.register(csv_integration)
manager.register(email_service)
manager.register(notif_service)

manager.connect_all()
health = manager.health_check_all()
print(health)  # {"CSVIntegration": True, "EmailIntegration": True, ...}
```

## Quick Start

### Installation

```bash
# Navigate to project root
cd supplier-hub

# Create virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install fastapi uvicorn pydantic
```

### Usage Example

```python
from backend.services import SupplierService, UserService, DataService
from backend.models import SupplierCreate, UserCreate, SearchFilter

# Initialize services
supplier_service = SupplierService()
user_service = UserService()
data_service = DataService(supplier_service)

# Create a user
user = user_service.create_user(UserCreate(
    username="alice",
    email="alice@example.com",
    password="secure123"
))

# Create suppliers
for i in range(10):
    supplier = supplier_service.create(SupplierCreate(
        name=f"Supplier {i}",
        category="Lumber & Wood Products",
        location="New York, NY",
        region="NY",
        rating=4.0 + (i * 0.1),
        ai_score=70 + i,
        products=["Lumber", "Wood"],
        certifications=["ISO 9001"],
        walmart_verified=i % 2 == 0,
        years_in_business=5 + i,
        projects_completed=100 + (i * 50)
    ))

# Search suppliers
results = supplier_service.search(SearchFilter(
    query="lumber",
    min_rating=4.0,
    limit=5
))
print(f"Found {results.total} suppliers")
for supplier in results.items:
    print(f"  - {supplier.name} ({supplier.rating} stars)")

# Add to favorites
for supplier in results.items:
    user_service.add_favorite(user.id, supplier.id)

# Get user preferences
favorites = user_service.get_favorites(user.id)
print(f"User has {len(favorites)} favorite suppliers")
```

## Testing

Create a test file `test_backend.py`:

```python
from backend.services import SupplierService
from backend.models import SupplierCreate, SearchFilter

def test_supplier_creation():
    service = SupplierService()
    
    supplier = service.create(SupplierCreate(
        name="Test Supplier",
        category="Lumber & Wood Products",
        location="Test City, TX",
        region="TX",
        rating=4.5,
        ai_score=85,
        products=["Test Product"],
        walmart_verified=True,
        years_in_business=10,
        projects_completed=1000
    ))
    
    assert supplier.id == 1
    assert supplier.name == "Test Supplier"
    assert supplier.rating == 4.5
    print("✓ Supplier creation test passed")

def test_search():
    service = SupplierService()
    
    # Create test suppliers
    for i in range(3):
        service.create(SupplierCreate(
            name=f"Test Supplier {i}",
            category="Lumber & Wood Products",
            location="Test City, TX",
            region="TX",
            rating=4.0 + i,
            ai_score=70 + i,
            products=["Lumber"],
            walmart_verified=True,
            years_in_business=10,
            projects_completed=1000
        ))
    
    # Search
    results = service.search(SearchFilter(query="Test", limit=10))
    assert results.total == 3
    print("✓ Search test passed")

if __name__ == "__main__":
    test_supplier_creation()
    test_search()
    print("\n✅ All tests passed!")
```

Run tests:
```bash
python test_backend.py
```

## Best Practices

1. **Always use type hints** - Makes code more maintainable
2. **Validate inputs** - Use Pydantic models for automatic validation
3. **Handle errors gracefully** - Catch exceptions and log them
4. **Keep services focused** - Single responsibility principle
5. **Use dependency injection** - Easier to test and maintain
6. **Follow DRY** - Don't repeat yourself
7. **Document public APIs** - Use docstrings
8. **Unit test core logic** - Especially services
9. **Log important events** - For debugging and monitoring
10. **Use configuration** - Don't hardcode values

## Extending the Backend

### Adding a New Service

```python
# backend/services.py
class ReportingService:
    """Generate supplier reports and analytics."""
    
    def __init__(self, supplier_service: SupplierService):
        self.supplier_service = supplier_service
    
    def get_supplier_statistics(self) -> Dict[str, Any]:
        """Get statistics about all suppliers."""
        suppliers = self.supplier_service.get_all()
        
        if not suppliers:
            return {}
        
        ratings = [s.rating for s in suppliers]
        ai_scores = [s.ai_score for s in suppliers]
        
        return {
            'total_suppliers': len(suppliers),
            'avg_rating': sum(ratings) / len(ratings),
            'avg_ai_score': sum(ai_scores) / len(ai_scores),
            'verified_count': sum(1 for s in suppliers if s.walmart_verified),
        }
```

### Adding a New Integration

```python
# backend/integrations.py
class SlackIntegration(BaseIntegration):
    """Send notifications to Slack."""
    
    def __init__(self, webhook_url: str):
        super().__init__("SlackIntegration")
        self.webhook_url = webhook_url
    
    def connect(self) -> bool:
        # Verify webhook URL
        self.is_connected = True
        return True
    
    def send_message(self, message: str, channel: str = "#general") -> bool:
        """Send message to Slack channel."""
        if not self.is_connected:
            return False
        
        # Call Slack API
        logger.info(f"[{self.name}] Sent message to {channel}")
        return True
```

## Performance Considerations

- **In-memory storage** - Current implementation uses dictionaries (fast, but not persistent)
- **For production** - Integrate with a database (PostgreSQL, MongoDB)
- **Caching** - Consider adding Redis for frequently accessed data
- **Indexing** - Add database indexes for common search patterns
- **Pagination** - Always paginate large result sets

## Security Notes

- **Validate all inputs** - Use Pydantic models
- **Sanitize outputs** - Remove sensitive data before returning
- **Error handling** - Don't expose internal details in error messages
- **Logging** - Don't log passwords or sensitive data
- **CORS** - Configure properly for production
- **Rate limiting** - Consider adding rate limiting for APIs

## License

Copyright © 2025 Walmart Inc. All rights reserved.

## Support

For issues or questions, please refer to the main Supplier Hub documentation.