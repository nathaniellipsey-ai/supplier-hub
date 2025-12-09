import React, { useState } from 'react';
import { apiClient, Supplier } from '../api';
import './SearchBar.css';

interface SearchBarProps {
  onSearch: (query: string, category?: string) => Promise<void>;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Supplier[]>([]);
  const [searched, setSearched] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setLoading(true);
      const result = await apiClient.searchSuppliers(query, category || undefined);
      setResults(result.results);
      setSearched(true);
      await onSearch(query, category || undefined);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="search-form">
        <h2>Search Suppliers</h2>
        <p className="search-subtitle">Find suppliers by name, ID, or keyword</p>

        <div className="search-inputs">
          <div className="form-group">
            <label htmlFor="query">Search Query</label>
            <input
              id="query"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Electronics, ACME, etc."
              className="search-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="category">Category (Optional)</label>
            <input
              id="category"
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="e.g., Electronics, Manufacturing"
              className="search-input"
            />
          </div>

          <button type="submit" className="search-btn" disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {searched && (
        <div className="search-results">
          <h3>Results ({results.length})</h3>
          {results.length === 0 ? (
            <div className="no-results">No suppliers found matching your search</div>
          ) : (
            <div className="results-list">
              {results.map((supplier) => (
                <div key={supplier.id} className="result-item">
                  <div className="result-name">{supplier.name}</div>
                  <div className="result-details">
                    <span className="result-id">{supplier.supplier_id}</span>
                    <span className="result-category">{supplier.category}</span>
                    {supplier.city && <span className="result-location">{supplier.city}, {supplier.state}</span>}
                  </div>
                  {supplier.email && <div className="result-email">{supplier.email}</div>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
