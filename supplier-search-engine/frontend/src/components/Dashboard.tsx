import React from 'react';
import { DashboardStats } from '../api';
import './Dashboard.css';

interface DashboardProps {
  stats: DashboardStats | null;
  loading: boolean;
}

const Dashboard: React.FC<DashboardProps> = ({ stats, loading }) => {
  if (loading) {
    return <div className="dashboard">Loading dashboard...</div>;
  }

  if (!stats) {
    return <div className="dashboard">No data available</div>;
  }

  return (
    <div className="dashboard">
      <h2>Dashboard Overview</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{stats.total_active_suppliers}</div>
          <div className="stat-label">Active Suppliers</div>
        </div>

        <div className="stat-card">
          <div className="stat-number">{stats.total_products}</div>
          <div className="stat-label">Total Products</div>
        </div>

        <div className="stat-card">
          <div className="stat-number">{stats.total_searches}</div>
          <div className="stat-label">Total Searches</div>
        </div>

        <div className="stat-card">
          <div className="stat-number">{stats.category_breakdown.length}</div>
          <div className="stat-label">Categories</div>
        </div>
      </div>

      {stats.category_breakdown.length > 0 && (
        <div className="category-section">
          <h3>Suppliers by Category</h3>
          <div className="category-list">
            {stats.category_breakdown.map((cat, idx) => (
              <div key={idx} className="category-item">
                <span className="category-name">{cat.category}</span>
                <span className="category-count">{cat.count} suppliers</span>
                <div className="category-bar">
                  <div
                    className="category-bar-fill"
                    style={{
                      width: `${(cat.count / Math.max(...stats.category_breakdown.map(c => c.count))) * 100}%`
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
