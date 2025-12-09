import React, { useState, useEffect } from 'react';
import { apiClient } from '../api';
import './DataIngestion.css';

interface DataIngestionProps {
  onIngested: () => void;
}

const DataIngestion: React.FC<DataIngestionProps> = ({ onIngested }) => {
  const [sources, setSources] = useState<string[]>([]);
  const [selectedSource, setSelectedSource] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('success');

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    try {
      const result = await apiClient.listDataSources();
      setSources(result.sources);
      if (result.sources.length > 0) {
        setSelectedSource(result.sources[0]);
      }
    } catch (error) {
      console.error('Failed to load sources:', error);
    }
  };

  const handleIngest = async () => {
    if (!selectedSource) return;

    try {
      setLoading(true);
      setMessage('');
      const result = await apiClient.ingestData(selectedSource);
      setMessage(
        `Successfully imported ${result.records_added} new suppliers and updated ${result.records_updated} existing records`
      );
      setMessageType('success');
      onIngested();
    } catch (error) {
      setMessage(`Failed to ingest data from ${selectedSource}`);
      setMessageType('error');
      console.error('Ingestion failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="data-ingestion">
      <div className="ingestion-card">
        <h2>Import Supplier Data</h2>
        <p className="subtitle">Pull live supplier data from external sources</p>

        <div className="source-selector">
          <label htmlFor="source">Select Data Source</label>
          <select
            id="source"
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            className="source-dropdown"
          >
            {sources.map((source) => (
              <option key={source} value={source}>
                {source.replace(/_/g, ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        <div className="source-info">
          <p>Available sources:</p>
          <ul>
            <li>Walmart Suppliers - Official Walmart supplier directory</li>
            <li>Global Suppliers - Global supplier database</li>
            <li>Alibaba - Alibaba marketplace suppliers</li>
            <li>Local Sample - Sample data for testing</li>
          </ul>
        </div>

        <button
          onClick={handleIngest}
          disabled={loading || !selectedSource}
          className="ingest-btn"
        >
          {loading ? 'Importing...' : 'Import Data'}
        </button>

        {message && (
          <div className={`message message-${messageType}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
};

export default DataIngestion;
