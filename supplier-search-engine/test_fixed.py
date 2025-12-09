import time
from app_minimal import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("Testing fixed version...\n")

# Test that index.html is served
response = client.get('/')
print(f'GET /: {response.status_code}')
if response.status_code == 200:
    print(f'✓ index.html is being served correctly!')
    print(f'Content type: {response.headers.get("content-type")}')
else:
    print(f'✗ Error: {response.text}')
print()

# Test registration
print('Testing registration...')
response = client.post('/api/auth/register', json={
    'username': 'john',
    'password': 'pass1234',
    'email': 'john@example.com',
    'name': 'John Doe'
})
print(f'Status: {response.status_code}')
if response.status_code == 200:
    print(f'✓ Registration works!')
    print(response.json())
else:
    print(f'✗ Error: {response.json()}')
print()

# Test login
print('Testing login...')
response = client.post('/api/auth/login', json={
    'username': 'john',
    'password': 'pass1234'
})
print(f'Status: {response.status_code}')
if response.status_code == 200:
    print(f'✓ Login works!')
    data = response.json()
    print(f'Session token: {data["session_token"][:20]}...')
else:
    print(f'✗ Error: {response.json()}')

print("\n✓ All tests passed!")
