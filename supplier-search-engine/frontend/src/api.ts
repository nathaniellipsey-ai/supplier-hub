"""API client for communicating with the backend.

Handles all HTTP requests to the FastAPI backend.
"""

import axios, { AxiosInstance } from 'axios';

interface Supplier {
  id: number;
  supplier_id: string;
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  category: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface Product {
  id: number;
  supplier_id: number;
  product_code: string;
  product_name: string;
  description?: string;
  unit_cost: number;
  lead_time_days: number;
  min_order_qty: number;
  created_at: string;
}

interface SearchResult {
  query: string;
  results_count: number;
  results: Supplier[];
}

interface DashboardStats {
  total_active_suppliers: number;
  total_products: number;
  total_searches: number;
  category_breakdown: Array<{
    category: string;
    count: number;
  }>;
}

interface SupplierCreate {
  supplier_id: string;
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  category: string;
  status?: string;
}

interface ProductCreate {
  supplier_id: number;
  product_code: string;
  product_name: string;
  description?: string;
  unit_cost: number;
  lead_time_days: number;
  min_order_qty: number;
}

class APIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });
  }

  // Health & Status
  async getHealth(): Promise<{ status: string; message: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  async getAPIHealth(): Promise<any> {
    const response = await this.client.get('/api/health');
    return response.data;
  }

  // Suppliers
  async listSuppliers(
    skip: number = 0,
    limit: number = 50,
    category?: string,
    status?: string
  ): Promise<Supplier[]> {
    const response = await this.client.get('/api/suppliers', {
      params: { skip, limit, category, status },
    });
    return response.data;
  }

  async getSupplier(id: number): Promise<Supplier> {
    const response = await this.client.get(`/api/suppliers/${id}`);
    return response.data;
  }

  async createSupplier(supplier: SupplierCreate): Promise<{ id: number; message: string }> {
    const response = await this.client.post('/api/suppliers', supplier);
    return response.data;
  }

  async searchSuppliers(query: string, category?: string): Promise<SearchResult> {
    const response = await this.client.get(`/api/suppliers/search/${query}`, {
      params: { category },
    });
    return response.data;
  }

  // Products
  async getSupplierProducts(supplierId: number): Promise<Product[]> {
    const response = await this.client.get(`/api/suppliers/${supplierId}/products`);
    return response.data;
  }

  async createProduct(product: ProductCreate): Promise<{ id: number; message: string }> {
    const response = await this.client.post('/api/products', product);
    return response.data;
  }

  // Analytics
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.client.get('/api/dashboard/stats');
    return response.data;
  }

  // Data Ingestion
  async listDataSources(): Promise<{ sources: string[]; count: number }> {
    const response = await this.client.get('/api/data/sources');
    return response.data;
  }

  async ingestData(source: string): Promise<{
    message: string;
    source: string;
    records_added: number;
    records_updated: number;
  }> {
    const response = await this.client.post('/api/data/ingest', null, {
      params: { source },
    });
    return response.data;
  }
}

export const apiClient = new APIClient();
export type { Supplier, Product, SearchResult, DashboardStats, SupplierCreate, ProductCreate };
