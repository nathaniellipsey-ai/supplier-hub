import React, { useState, useEffect } from 'react';
import { apiClient, Supplier, DashboardStats } from './api';
import SupplierList from './components/SupplierList';
import SearchBar from './components/SearchBar';
import Dashboard from './components/Dashboard';
import DataIngestion from './components/DataIngestion';
import './App.css';

type TabType = 'dashboard' | 'suppliers' | 'search' | 'ingest';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const stats = await apiClient.getDashboardStats();
      setStats(stats);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadSuppliers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.listSuppliers(0, 100);
      setSuppliers(data);
    } catch (err) {
      setError('Failed to load suppliers');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query: string, category?: string) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiClient.searchSuppliers(query, category);
      setSuppliers(result.results);
    } catch (err) {
      setError('Search failed');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDataIngested = () => {
    // Reload stats after data ingestion
    loadDashboardData();
    loadSuppliers();
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Supplier Search Engine Dashboard</h1>
        <p className="subtitle">Live Data Integration & Management</p>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('dashboard');
            loadDashboardData();
          }}
        >
          Dashboard
        </button>
        <button
          className={`nav-btn ${activeTab === 'suppliers' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('suppliers');
            loadSuppliers();
          }}
        >
          Suppliers
        </button>
        <button
          className={`nav-btn ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          Search
        </button>
        <button
          className={`nav-btn ${activeTab === 'ingest' ? 'active' : ''}`}
          onClick={() => setActiveTab('ingest')}
        >
          Import Data
        </button>
      </nav>

      {error && <div className="error-banner">{error}</div>}
      {loading && <div className="loading-banner">Loading...</div>}

      <main className="app-content">
        {activeTab === 'dashboard' && <Dashboard stats={stats} loading={loading} />}
        {activeTab === 'suppliers' && <SupplierList suppliers={suppliers} loading={loading} />}
        {activeTab === 'search' && <SearchBar onSearch={handleSearch} />}
        {activeTab === 'ingest' && <DataIngestion onIngested={handleDataIngested} />}
      </main>

      <footer className="app-footer">
        <p>Supplier Search Engine v1.0 | Powered by FastAPI & React</p>
      </footer>
    </div>
  );
}

export default App;
