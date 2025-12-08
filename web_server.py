#!/usr/bin/env python3
"""Standalone web server for the frontend."""

import socket
import os
from pathlib import Path

PORT = 8080
HOST = '127.0.0.1'

def get_mime_type(filename):
    """Get MIME type for file."""
    if filename.endswith('.html'):
        return 'text/html'
    elif filename.endswith('.css'):
        return 'text/css'
    elif filename.endswith('.js'):
        return 'application/javascript'
    elif filename.endswith('.json'):
        return 'application/json'
    else:
        return 'application/octet-stream'

def handle_request(request_data):
    """Handle HTTP request."""
    try:
        request_line = request_data.split(b'\r\n')[0].decode('utf-8')
        method, path, protocol = request_line.split(' ')
        
        # Default to index.html for root
        if path == '/':
            path = '/index.html'
        
        # Remove leading slash
        filepath = path.lstrip('/')
        full_path = os.path.join(os.path.dirname(__file__), filepath)
        
        # Security: prevent directory traversal
        if '..' in filepath:
            response = b'HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\n\r\n<h1>403 Forbidden</h1>'
            return response
        
        # Check if file exists
        if os.path.exists(full_path) and os.path.isfile(full_path):
            with open(full_path, 'rb') as f:
                content = f.read()
            
            mime_type = get_mime_type(filepath)
            response = f'HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\nContent-Length: {len(content)}\r\nAccess-Control-Allow-Origin: *\r\nCache-Control: no-store\r\n\r\n'.encode() + content
            return response
        else:
            response = b'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>'
            return response
    except Exception as e:
        print(f'Error handling request: {e}')
        response = b'HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\n\r\n<h1>500 Server Error</h1>'
        return response

def main():
    """Run the web server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        
        print(f'\n{"="*60}')
        print(f'Web Server Started!')
        print(f'{"="*60}')
        print(f'\nOpen your browser to:')
        print(f'  http://{HOST}:{PORT}/index.html')
        print(f'\nPress Ctrl+C to stop')
        print(f'{"="*60}\n')
        
        while True:
            client_socket, addr = server_socket.accept()
            try:
                request_data = client_socket.recv(4096)
                response = handle_request(request_data)
                client_socket.sendall(response)
            finally:
                client_socket.close()
    except KeyboardInterrupt:
        print('\n\nServer stopped.')
    except Exception as e:
        print(f'Server error: {e}')
    finally:
        server_socket.close()

if __name__ == '__main__':
    main()
