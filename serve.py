#!/usr/bin/env python3
"""Simple HTTP server to serve the frontend."""

import http.server
import socketserver
import os
import sys

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        return super().end_headers()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"\n{'='*60}")
    print(f"Frontend Server Started!")
    print(f"{'='*60}")
    print(f"\nOpen your browser to:")
    print(f"  http://127.0.0.1:{PORT}/index.html")
    print(f"  or")
    print(f"  http://localhost:{PORT}/index.html")
    print(f"\nPress Ctrl+C to stop the server")
    print(f"{'='*60}\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
