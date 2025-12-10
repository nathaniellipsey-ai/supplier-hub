#!/usr/bin/env python3
"""Serve frontend HTML from the same FastAPI app."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Create a new app that serves the frontend
app = FastAPI()

# Mount the parent directory as static files
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html_file = os.path.join(parent_dir, 'index.html')

print(f'Looking for HTML at: {html_file}')
print(f'File exists: {os.path.exists(html_file)}')

# Serve the index.html file
@app.get('/', include_in_schema=False)
@app.get('/index.html', include_in_schema=False)
async def serve_frontend():
    if os.path.exists(html_file):
        return FileResponse(html_file, media_type='text/html')
    return {'error': 'Frontend not found'}

if __name__ == '__main__':
    print(f'\n{"="*60}')
    print('Frontend Server')
    print(f'{"="*60}')
    print(f'\nServing frontend from: {html_file}')
    print(f'Open browser to: http://127.0.0.1:9000/index.html')
    print(f'{"="*60}\n')
    
    uvicorn.run(app, host='127.0.0.1', port=9000)
