from app_minimal import app
from fastapi.testclient import TestClient

try:
    print("Creating test client...")
    client = TestClient(app)
    
    # Test health
    print("Testing health endpoint...")
    response = client.get('/api/health')
    print(f'Health check: {response.status_code}')
    print(response.json())
    print()
    
    # Test registration
    print('Testing registration...')
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'password': 'testpass123',
        'email': 'test@example.com',
        'name': 'Test User'
    })
    print(f'Status: {response.status_code}')
    print(response.json())
    print()
    
    # Test login
    print('Testing login...')
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    print(f'Status: {response.status_code}')
    print(response.json())
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
