#!/usr/bin/env python3
"""Minimal API server for supplier data using high port (unlikely to be blocked)."""

import socket
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from suppliers_generator import SupplierGenerator

# Port to use - using 'localhost' hostname instead of IP (firewall allows hostname!)
PORT = 8000
HOST = 'localhost'

# Generate suppliers once
print("Generating 5000 suppliers...")
generator = SupplierGenerator()
all_suppliers = generator.generate_suppliers()
print(f"Generated {len(all_suppliers)} suppliers")

def get_stats():
    """Get dashboard statistics."""
    verified_count = sum(1 for s in all_suppliers if s['walmartVerified'])
    avg_rating = sum(s['rating'] for s in all_suppliers) / len(all_suppliers) if all_suppliers else 0
    avg_ai_score = sum(s['aiScore'] for s in all_suppliers) / len(all_suppliers) if all_suppliers else 0
    
    categories = {}
    for supplier in all_suppliers:
        cat = supplier['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    regions = {}
    for supplier in all_suppliers:
        reg = supplier['region']
        regions[reg] = regions.get(reg, 0) + 1
    
    return {
        'total_suppliers': len(all_suppliers),
        'walmart_verified': verified_count,
        'verified_percentage': round((verified_count / len(all_suppliers) * 100) if all_suppliers else 0, 1),
        'average_rating': round(avg_rating, 2),
        'average_ai_score': round(avg_ai_score, 1),
        'categories': categories,
        'regions': regions,
        'total_categories': len(categories),
        'total_regions': len(regions)
    }

def get_suppliers(skip=0, limit=100):
    """Get suppliers with pagination."""
    return {
        'total': len(all_suppliers),
        'skip': skip,
        'limit': limit,
        'suppliers': all_suppliers[skip:skip+limit]
    }

def search_suppliers(query):
    """Search suppliers."""
    q_lower = query.lower()
    results = [
        s for s in all_suppliers
        if q_lower in s['name'].lower() or q_lower in s['category'].lower() or 
           any(q_lower in p.lower() for p in s['products'])
    ]
    return {
        'query': query,
        'count': len(results),
        'results': results[:100]
    }

def get_categories():
    """Get all categories."""
    categories = {}
    for supplier in all_suppliers:
        cat = supplier['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        'categories': categories,
        'total_categories': len(categories)
    }

def handle_request(request_line, body):
    """Handle incoming HTTP request."""
    try:
        # Parse request line
        parts = request_line.split(' ')
        method = parts[0]
        path = parts[1] if len(parts) > 1 else '/'
        
        # Handle OPTIONS (preflight CORS)
        if method == 'OPTIONS':
            response = (
                'HTTP/1.1 200 OK\r\n'
                'Access-Control-Allow-Origin: *\r\n'
                'Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n'
                'Access-Control-Allow-Headers: Content-Type\r\n'
                'Content-Length: 0\r\n'
                '\r\n'
            )
            return response.encode()
        
        # Route handlers
        if path == '/api/dashboard/stats':
            data = get_stats()
        elif path.startswith('/api/dashboard/suppliers/search?q='):
            query = path.split('q=')[1].replace('%20', ' ')
            data = search_suppliers(query)
        elif path.startswith('/api/dashboard/suppliers?'):
            # Parse skip and limit
            skip = 0
            limit = 100
            if 'skip=' in path:
                skip = int(path.split('skip=')[1].split('&')[0])
            if 'limit=' in path:
                limit = int(path.split('limit=')[1].split('&')[0])
            data = get_suppliers(skip, limit)
        elif path == '/api/dashboard/categories':
            data = get_categories()
        elif path.startswith('/api/dashboard/suppliers/'):
            supplier_id = int(path.split('/')[-1])
            supplier = next((s for s in all_suppliers if s['id'] == supplier_id), None)
            if supplier:
                data = supplier
            else:
                return b'HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n\r\n{"error": "Not found"}'
        elif path == '/health':
            data = {'status': 'healthy', 'message': 'API is running', 'version': '1.0.0'}
        else:
            return b'HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n\r\n{"error": "Not found"}'
        
        # JSON response
        json_str = json.dumps(data)
        response = (
            'HTTP/1.1 200 OK\r\n'
            'Access-Control-Allow-Origin: *\r\n'
            'Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n'
            'Access-Control-Allow-Headers: Content-Type\r\n'
            'Content-Type: application/json\r\n'
            f'Content-Length: {len(json_str)}\r\n'
            '\r\n'
        )
        return (response + json_str).encode()
    
    except Exception as e:
        print(f'Error: {e}')
        return b'HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\n\r\n{"error": "Server error"}'

def run_server():
    """Run the HTTP server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        
        print(f'\n{"="*70}')
        print(' SUPPLIER API SERVER')
        print(f'{"="*70}')
        print(f'\nServer running on: http://{HOST}:{PORT}')
        print(f'\nEndpoints:')
        print(f'  GET /api/dashboard/stats           - Dashboard statistics')
        print(f'  GET /api/dashboard/suppliers       - All suppliers')
        print(f'  GET /api/dashboard/suppliers/search?q=... - Search')
        print(f'  GET /api/dashboard/categories      - Categories')
        print(f'\nAdd this to your HTML dashboard:')
        print(f'  const API_URL = "http://{HOST}:{PORT}";')
        print(f'\nPress Ctrl+C to stop')
        print(f'{"="*70}\n')
        
        while True:
            client_socket, addr = server_socket.accept()
            try:
                # Read request
                request_data = client_socket.recv(4096).decode('utf-8', errors='ignore')
                lines = request_data.split('\r\n')
                request_line = lines[0] if lines else ''
                body = '\r\n'.join(lines[lines.index('') + 1:]) if '' in lines else ''
                
                # Handle request
                response = handle_request(request_line, body)
                client_socket.sendall(response)
            except Exception as e:
                print(f'Error handling request: {e}')
            finally:
                client_socket.close()
    
    except OSError as e:
        print(f'\nError: Could not bind to {HOST}:{PORT}')
        print(f'Details: {e}')
        print(f'\nTrying alternative port 18888...')
        # Try alternative port
        try:
            server_socket.bind((HOST, 18888))
            server_socket.listen(5)
            print(f'Server running on: http://{HOST}:18888')
            # Continue with same loop...
            while True:
                client_socket, addr = server_socket.accept()
                try:
                    request_data = client_socket.recv(4096).decode('utf-8', errors='ignore')
                    lines = request_data.split('\r\n')
                    request_line = lines[0] if lines else ''
                    body = '\r\n'.join(lines[lines.index('') + 1:]) if '' in lines else ''
                    response = handle_request(request_line, body)
                    client_socket.sendall(response)
                finally:
                    client_socket.close()
        except Exception as e2:
            print(f'Failed on port 18888 too: {e2}')
            sys.exit(1)
    except KeyboardInterrupt:
        print('\n\nServer stopped.')
    finally:
        server_socket.close()

if __name__ == '__main__':
    run_server()
