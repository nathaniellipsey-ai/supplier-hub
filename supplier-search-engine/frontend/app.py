#!/usr/bin/env python3
"""Flask frontend for Supplier Search Engine Dashboard."""

from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Simple CORS by adding headers
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Configuration
API_BASE_URL = 'http://127.0.0.1:8000'


def get_api_data(endpoint: str, params: dict = None):
    """Fetch data from the FastAPI backend."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None


@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard view."""
    stats = get_api_data('/api/dashboard/stats')
    return render_template('dashboard.html', stats=stats)


@app.route('/suppliers')
def suppliers():
    """Suppliers list view."""
    return render_template('suppliers.html')


@app.route('/search')
def search():
    """Search view."""
    return render_template('search.html')


# API Routes (JSON responses)

@app.route('/api/stats')
def api_stats():
    """Get dashboard statistics."""
    return jsonify(get_api_data('/api/dashboard/stats'))


@app.route('/api/suppliers')
def api_suppliers():
    """Get suppliers with pagination."""
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', 20, type=int)
    data = get_api_data('/api/dashboard/suppliers', {'skip': skip, 'limit': limit})
    return jsonify(data)


@app.route('/api/suppliers/search')
def api_search():
    """Search suppliers."""
    q = request.args.get('q', '')
    data = get_api_data('/api/dashboard/suppliers/search', {'q': q})
    return jsonify(data)


@app.route('/api/suppliers/<int:supplier_id>')
def api_supplier_detail(supplier_id: int):
    """Get supplier details."""
    data = get_api_data(f'/api/dashboard/suppliers/{supplier_id}')
    return jsonify(data)


@app.route('/api/categories')
def api_categories():
    """Get all categories."""
    data = get_api_data('/api/dashboard/categories')
    return jsonify(data)


if __name__ == '__main__':
    print(f'\n{"="*70}')
    print(' SUPPLIER SEARCH ENGINE - FLASK FRONTEND')
    print(f'{"="*70}')
    print(f'\nStarting Flask frontend on http://127.0.0.1:5000')
    print(f'Backend API: {API_BASE_URL}')
    print(f'\nPress Ctrl+C to stop\n')
    
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
