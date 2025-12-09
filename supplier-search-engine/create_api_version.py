#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create an API-integrated version of the HTML dashboard."""

import os
import shutil
from datetime import datetime
import sys

# Fix encoding for Windows console
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Source and destination files
source_html = r'C:\Users\n0l08i7\OneDrive - Walmart Inc\Supplier\supplier-search-engine.html'
dest_html = r'C:\Users\n0l08i7\Documents\supplier-search-engine\dashboard_with_api.html'

if not os.path.exists(source_html):
    print(f"ERROR: Source file not found: {source_html}")
    exit(1)

print(f"Reading: {source_html}")
with open(source_html, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find where to inject the API code
# Look for the section that generates suppliers
api_code = '''
// API URL - point to the Python API server
const API_URL = 'http://localhost:8000';
let USE_API = false; // Set to true to use API instead of local generation

// Function to load suppliers from API
async function loadSuppliersFromAPI(skip = 0, limit = 5000) {
    try {
        const response = await fetch(`${API_URL}/api/dashboard/suppliers?skip=${skip}&limit=${limit}`);
        if (!response.ok) throw new Error('API Error');
        const data = await response.json();
        return data.suppliers || [];
    } catch (error) {
        console.warn('API load failed, using local generation:', error);
        USE_API = false;
        return null;
    }
}

// Function to load dashboard stats from API
async function loadStatsFromAPI() {
    try {
        const response = await fetch(`${API_URL}/api/dashboard/stats`);
        if (!response.ok) throw new Error('API Error');
        const data = await response.json();
        return data;
    } catch (error) {
        console.warn('API stats load failed:', error);
        return null;
    }
}

// Function to search suppliers from API
async function searchSuppliersFromAPI(query) {
    try {
        const response = await fetch(`${API_URL}/api/dashboard/suppliers/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('API Error');
        const data = await response.json();
        return data.results || [];
    } catch (error) {
        console.warn('API search failed:', error);
        return null;
    }
}
'''

# Insert the API code right after the opening <script> tag
if '<script>' in html_content:
    # Find the first script tag
    script_pos = html_content.find('<script>')
    script_end = script_pos + len('<script>')
    
    # Insert API code after the opening script tag
    html_content = html_content[:script_end] + '\n' + api_code + html_content[script_end:]
    
    print("[OK] Injected API connection code")
else:
    print("WARNING: Could not find <script> tag")

# Save to new file
print(f"\nSaving to: {dest_html}")
with open(dest_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("[OK] Created API-integrated version")
print(f"\nNext steps:")
print(f"1. Start the API server: python api_server.py (or use START_API.bat)")
print(f"2. Open in browser: file:///{dest_html.replace(chr(92), '/')}")
print(f"3. To enable API, find 'USE_API = false' in the file and change to 'true'")
print(f"\nThe API endpoints are available at: http://localhost:8000")
