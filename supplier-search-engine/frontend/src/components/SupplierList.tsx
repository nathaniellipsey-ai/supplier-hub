import React from 'react';
import { Supplier } from '../api';
import './SupplierList.css';

interface SupplierListProps {
  suppliers: Supplier[];
  loading: boolean;
}

const SupplierList: React.FC<SupplierListProps> = ({ suppliers, loading }) => {
  if (loading) {
    return <div className="supplier-list">Loading suppliers...</div>;
  }

  if (suppliers.length === 0) {
    return (
      <div className="supplier-list">
        <div className="empty-state">
          <p>No suppliers found</p>
          <p className="subtext">Try searching or importing data from a source</p>
        </div>
      </div>
    );
  }

  return (
    <div className="supplier-list">
      <h2>Suppliers ({suppliers.length})</h2>
      <div className="suppliers-grid">
        {suppliers.map((supplier) => (
          <div key={supplier.id} className="supplier-card">
            <div className="supplier-header">
              <h3>{supplier.name}</h3>
              <span className={`status status-${supplier.status}`}>{supplier.status}</span>
            </div>

            <div className="supplier-body">
              <div className="supplier-field">
                <label>ID:</label>
                <span>{supplier.supplier_id}</span>
              </div>

              <div className="supplier-field">
                <label>Category:</label>
                <span>{supplier.category}</span>
              </div>

              {supplier.email && (
                <div className="supplier-field">
                  <label>Email:</label>
                  <span>{supplier.email}</span>
                </div>
              )}

              {supplier.phone && (
                <div className="supplier-field">
                  <label>Phone:</label>
                  <span>{supplier.phone}</span>
                </div>
              )}

              {supplier.address && (
                <div className="supplier-field">
                  <label>Address:</label>
                  <span>{supplier.address}</span>
                </div>
              )}

              {supplier.city && (
                <div className="supplier-field">
                  <label>Location:</label>
                  <span>
                    {supplier.city}, {supplier.state} {supplier.zip_code}
                  </span>
                </div>
              )}
            </div>

            <div className="supplier-footer">
              <small>Added: {new Date(supplier.created_at).toLocaleDateString()}</small>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SupplierList;
