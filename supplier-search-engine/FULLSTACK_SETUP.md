# Full-Stack Supplier Search Engine Setup Guide

## Architecture Overview

This is a modern full-stack application with three main components:

```
┌─────────────────────────────────────────────────────────────┐
│                   React Frontend (Port 5173)                 │
│  - Dashboard with live statistics                           │
│  - Supplier search and filtering                            │
│  - Data ingestion interface                                 │
│  - Responsive UI with Vite                                  │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/REST API
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                     │
│  - RESTful API endpoints                                    │
│  - Data services layer                                      │
│  - Live data integration                                    │
│  - CORS enabled for frontend                                │
└─────────────────┬───────────────────────────────────────────┘
                  │ SQL Queries
                  ▼
┌─────────────────────────────────────────────────────────────┐
│            SQLite Database (suppliers.db)                   │
│  - 3 tables: suppliers, products, search_history           │
│  - 4 indexes for optimal performance                        │
│  - Foreign key constraints and data validation              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Start the Backend

```bash
# Navigate to backend directory
cd backend

# Install dependencies
uvicorn main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 2. Start the Frontend

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### 3. That's it!

Browse to `http://localhost:5173` and start using the dashboard!

## Backend Setup (Detailed)

### Install Python Dependencies

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Or use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Available API Endpoints

#### Health & Status
- `GET /health` - Basic health check
- `GET /api/health` - Database health check

#### Suppliers
- `GET /api/suppliers` - List all suppliers with pagination
- `GET /api/suppliers/{id}` - Get specific supplier
- `POST /api/suppliers` - Create new supplier
- `GET /api/suppliers/search/{query}` - Search suppliers

#### Products
- `GET /api/suppliers/{supplier_id}/products` - Get supplier's products
- `POST /api/products` - Create new product

#### Analytics
- `GET /api/dashboard/stats` - Get dashboard statistics

#### Data Ingestion
- `GET /api/data/sources` - List available data sources
- `POST /api/data/ingest?source=<source_name>` - Import data

### Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI
Visit `http://localhost:8000/redoc` for ReDoc documentation

## Frontend Setup (Detailed)

### Install Node Dependencies

```bash
cd frontend
npm install
```

This installs:
- React 18
- TypeScript 5
- Vite 5 (build tool)
- Axios (HTTP client)

### Available Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run TypeScript type checking
npm run type-check

# Lint code
npm run lint
```

### Project Structure

```
frontend/
├── src/
│   ├── api.ts                    # API client
│   ├── App.tsx                   # Main app component
│   ├── App.css                   # Global styles
│   ├── main.tsx                  # React entry point
│   ├── index.css                 # Base styles
│   └── components/
│       ├── Dashboard.tsx         # Dashboard stats component
│       ├── Dashboard.css
│       ├── SupplierList.tsx      # Supplier list component
│       ├── SupplierList.css
│       ├── SearchBar.tsx         # Search component
│       ├── SearchBar.css
│       ├── DataIngestion.tsx     # Data import component
│       └── DataIngestion.css
├── index.html                    # HTML template
├── package.json                  # Dependencies
├── tsconfig.json                 # TypeScript config
└── vite.config.ts                # Vite config
```

## Backend Structure

```
backend/
├── main.py                       # FastAPI app with all routes
├── models.py                     # Pydantic data models
├── services.py                   # Business logic services
├── database.py                   # SQLite database wrapper
└── requirements.txt              # Python dependencies
```

## Database

The SQLite database is created automatically when you first run the backend.

### Schema

**suppliers table**
- id (PK)
- supplier_id (UNIQUE)
- name
- email, phone, address, city, state, zip_code, country
- category
- status (active/inactive/pending)
- created_at, updated_at

**products table**
- id (PK)
- supplier_id (FK)
- product_code (UNIQUE)
- product_name
- description
- unit_cost
- lead_time_days
- min_order_qty
- created_at

**search_history table**
- id (PK)
- search_query
- results_count
- user_id
- created_at

## Live Data Integration

The system can pull data from multiple sources:

### Available Sources

1. **walmart_suppliers** - Walmart supplier directory
2. **global_suppliers** - Global supplier database
3. **alibaba** - Alibaba marketplace
4. **local_sample** - Sample data (for testing)

### How to Ingest Data

Using the UI:
1. Click "Import Data" tab
2. Select a data source
3. Click "Import Data"

Using the API:
```bash
curl -X POST "http://localhost:8000/api/data/ingest?source=local_sample"
```

## Features

### Dashboard
- Real-time statistics
- Supplier count by category
- Product inventory
- Search analytics

### Supplier Management
- Browse all suppliers
- Search by name, ID, or keyword
- Filter by category
- View detailed supplier information

### Data Integration
- Import from multiple sources
- Automatic duplicate detection
- Status tracking

### Search & Analytics
- Full-text search
- Category filtering
- Search history logging
- Performance metrics

## Development Tips

### Backend Development

```bash
# Run with auto-reload on code changes
uvicorn main:app --reload

# Specific port
uvicorn main:app --reload --port 8001

# With logging
uvicorn main:app --reload --log-level debug
```

### Frontend Development

```bash
# Development with hot module replacement
npm run dev

# Open in browser: http://localhost:5173
```

### Common Issues

**CORS errors in frontend**
- Make sure backend is running on port 8000
- Check that CORS is enabled in main.py

**Database locked errors**
- Close other processes accessing the database
- Delete suppliers.db and restart backend

**Port already in use**
- Change port in uvicorn: `--port 8001`
- Change frontend port in vite.config.ts

## Production Deployment

### Build Frontend
```bash
cd frontend
npm run build
# Output in frontend/dist/
```

### Run Backend in Production
```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Docker Support

Create a Dockerfile:
```dockerfile
FROM python:3.11
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

Build and run:
```bash
docker build -t supplier-engine .
docker run -p 8000:8000 supplier-engine
```

## Testing

### Backend Tests

```bash
# Add pytest to requirements.txt
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Frontend Tests

```bash
npm install --save-dev vitest @testing-library/react
npm run test
```

## Environment Variables

Create a `.env` file in the backend directory:

```
DATABASE_PATH=suppliers.db
PORT=8000
DEBUG=False
```

Frontend .env:
```
VITE_API_URL=http://localhost:8000
```

## Performance Optimization

### Backend
- Database indexes on search columns
- Connection pooling via context managers
- Async/await for I/O operations
- Pagination for large result sets

### Frontend
- Code splitting via Vite
- CSS modules for style isolation
- Lazy loading of components
- Memoization where appropriate

## Security Considerations

1. **CORS**: Currently allows localhost only
2. **Input Validation**: All inputs validated with Pydantic
3. **SQL Injection**: Protected via parameterized queries
4. **Error Handling**: Generic errors returned to client

For production, add:
- Authentication (JWT)
- Rate limiting
- HTTPS
- Input sanitization
- CSRF protection

## Monitoring & Logging

Backend logs to console by default.

To add file logging:

```python
import logging.handlers
handler = logging.handlers.RotatingFileHandler('app.log')
logger.addHandler(handler)
```

## Support & Troubleshooting

Common issues and solutions are documented in the comments throughout the code.

For issues:
1. Check API health: `curl http://localhost:8000/api/health`
2. Check browser console for frontend errors
3. Enable debug logging in backend
4. Check database integrity: run `verify_schema.py`
