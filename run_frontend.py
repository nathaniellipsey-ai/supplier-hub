#!/usr/bin/env python3
"""Frontend web server that definitely works."""

import http.server
import socketserver
import os
import sys
import webbrowser

PORT = 8888
HOST = '0.0.0.0'
LOCALHOST = '127.0.0.1'

# Change to the script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        return super().end_headers()

print()
print('='*70)
print(' SUPPLIER SEARCH ENGINE - Frontend Web Server')
print('='*70)
print()
print(f'Starting server on {LOCALHOST}:{PORT}...')
print()

with socketserver.TCPServer((HOST, PORT), MyHandler) as httpd:
    print('[OK] Server is running!')
    print()
    print(f'Open your browser to:')
    print(f'  http://127.0.0.1:{PORT}/index.html')
    print()
    print(f'Backend API: http://127.0.0.1:8000')
    print()
    print(f'Press Ctrl+C to stop the server')
    print(f'{'='*70}')
    print()
    
    try:
        # Try to open browser
        webbrowser.open(f'http://127.0.0.1:{PORT}/index.html')
        print(f'Browser opening...')
        print()
    except:
        pass
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()
        print()
        print('Server stopped.')
        sys.exit(0)
