/**
 * UI Components Module
 * Reusable React-like components for building the interface
 * Professional component architecture
 */

class Component {
    constructor(props = {}) {
        this.props = props;
        this.state = {};
        this.element = null;
    }

    render() {
        throw new Error('render() must be implemented');
    }

    mount(selector) {
        const container = document.querySelector(selector);
        if (!container) throw new Error(`Container not found: ${selector}`);
        
        container.innerHTML = this.render();
        this.element = container;
        this.afterMount();
    }

    afterMount() {}
    
    setState(newState) {
        this.state = { ...this.state, ...newState };
    }
}

// ============================================================================
// DASHBOARD COMPONENT
// ============================================================================

class Dashboard extends Component {
    async afterMount() {
        try {
            const stats = await api.getDashboardStats();
            this.renderStats(stats);
        } catch (error) {
            console.error('Failed to load dashboard stats:', error);
            this.showError('Failed to load dashboard statistics');
        }
    }

    renderStats(stats) {
        const statsContainer = document.getElementById('stats-grid');
        if (!statsContainer) return;

        statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-label">Total Suppliers</div>
                <div class="stat-value">${stats.total_suppliers.toLocaleString()}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Walmart Verified</div>
                <div class="stat-value">${stats.walmart_verified}</div>
                <div class="stat-subtitle">${stats.verified_percentage}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Rating</div>
                <div class="stat-value">⭐ ${stats.average_rating}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg AI Score</div>
                <div class="stat-value">${stats.average_ai_score}</div>
            </div>
        `;

        const categoriesContainer = document.getElementById('categories-grid');
        if (categoriesContainer) {
            const categoryItems = Object.entries(stats.categories)
                .sort((a, b) => b[1] - a[1])
                .map(([name, count]) => `
                    <div class="category-item">
                        <div class="category-name">${name}</div>
                        <div class="category-count">${count}</div>
                    </div>
                `)
                .join('');
            categoriesContainer.innerHTML = categoryItems;
        }
    }

    showError(message) {
        const container = document.getElementById('stats-grid');
        if (container) {
            container.innerHTML = `<div class="error-message">${message}</div>`;
        }
    }

    render() {
        return `
            <div class="dashboard-section">
                <h1>Dashboard</h1>
                <div id="stats-grid" class="stats-grid"></div>
                <h2>Categories</h2>
                <div id="categories-grid" class="categories-grid"></div>
            </div>
        `;
    }
}

// ============================================================================
// SUPPLIER LIST COMPONENT
// ============================================================================

class SupplierList extends Component {
    constructor(props = {}) {
        super(props);
        this.state = {
            suppliers: [],
            total: 0,
            currentPage: 0,
            pageSize: 20,
            loading: true,
            error: null
        };
    }

    async afterMount() {
        await this.loadSuppliers();
    }

    async loadSuppliers() {
        try {
            this.setState({ loading: true });
            const skip = this.state.currentPage * this.state.pageSize;
            const data = await api.getSuppliers(skip, this.state.pageSize);
            
            this.setState({
                suppliers: data.suppliers,
                total: data.total,
                loading: false
            });
            
            this.renderTable();
            this.renderPagination();
        } catch (error) {
            this.setState({ error: error.message, loading: false });
            this.showError(`Failed to load suppliers: ${error.message}`);
        }
    }

    renderTable() {
        const tbody = document.querySelector('#suppliers-table tbody');
        if (!tbody) return;

        tbody.innerHTML = this.state.suppliers.map(supplier => `
            <tr class="supplier-row">
                <td>${supplier.id}</td>
                <td><strong>${supplier.name}</strong></td>
                <td>${supplier.category}</td>
                <td>${supplier.location}</td>
                <td>⭐ ${supplier.rating}</td>
                <td>${supplier.aiScore}</td>
                <td>${supplier.walmartVerified ? '✓ Verified' : '-'}</td>
            </tr>
        `).join('');
    }

    renderPagination() {
        const paginationContainer = document.getElementById('pagination');
        if (!paginationContainer) return;

        const totalPages = Math.ceil(this.state.total / this.state.pageSize);
        const currentPage = this.state.currentPage + 1;

        let html = `<div class="pagination">`;
        
        if (this.state.currentPage > 0) {
            html += `<button onclick="window.appState.suppliers.previousPage()">← Previous</button>`;
        }
        
        html += `<span>Page ${currentPage} of ${totalPages}</span>`;
        
        if (currentPage < totalPages) {
            html += `<button onclick="window.appState.suppliers.nextPage()">Next →</button>`;
        }
        
        html += `</div>`;
        paginationContainer.innerHTML = html;
    }

    nextPage() {
        const totalPages = Math.ceil(this.state.total / this.state.pageSize);
        if (this.state.currentPage + 1 < totalPages) {
            this.setState({ currentPage: this.state.currentPage + 1 });
            this.loadSuppliers();
            window.scrollTo(0, 0);
        }
    }

    previousPage() {
        if (this.state.currentPage > 0) {
            this.setState({ currentPage: this.state.currentPage - 1 });
            this.loadSuppliers();
            window.scrollTo(0, 0);
        }
    }

    showError(message) {
        const container = document.getElementById('suppliers-table');
        if (container) {
            container.innerHTML = `<div class="error-message">${message}</div>`;
        }
    }

    render() {
        return `
            <div class="suppliers-section">
                <h1>Suppliers</h1>
                <table id="suppliers-table" class="suppliers-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Category</th>
                            <th>Location</th>
                            <th>Rating</th>
                            <th>AI Score</th>
                            <th>Verified</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <div id="pagination"></div>
            </div>
        `;
    }
}

// ============================================================================
// SEARCH COMPONENT
// ============================================================================

class SearchSuppliers extends Component {
    constructor(props = {}) {
        super(props);
        this.state = {
            results: [],
            query: '',
            searching: false
        };
    }

    async afterMount() {
        const input = document.getElementById('search-input');
        const button = document.getElementById('search-button');
        
        if (input && button) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.search();
            });
            button.addEventListener('click', () => this.search());
        }
    }

    async search() {
        const input = document.getElementById('search-input');
        const query = input?.value.trim();
        
        if (!query) {
            this.showError('Please enter a search term');
            return;
        }

        try {
            this.setState({ searching: true });
            const data = await api.searchSuppliers(query, 100);
            
            this.setState({
                results: data.results,
                query: query,
                searching: false
            });
            
            this.renderResults();
        } catch (error) {
            this.setState({ searching: false });
            this.showError(`Search failed: ${error.message}`);
        }
    }

    renderResults() {
        const resultsContainer = document.getElementById('search-results');
        if (!resultsContainer) return;

        if (this.state.results.length === 0) {
            resultsContainer.innerHTML = '<div class="message">No results found</div>';
            return;
        }

        resultsContainer.innerHTML = this.state.results.map(supplier => `
            <div class="supplier-card">
                <h3>${supplier.name}</h3>
                <div class="card-info">
                    <span class="badge">${supplier.category}</span>
                    <span class="location">📍 ${supplier.location}</span>
                </div>
                <div class="card-details">
                    <p><strong>Rating:</strong> ⭐ ${supplier.rating}</p>
                    <p><strong>AI Score:</strong> ${supplier.aiScore}</p>
                    <p><strong>Products:</strong> ${supplier.products.join(', ') || 'N/A'}</p>
                    ${supplier.walmartVerified ? '<p class="verified">✓ Walmart Verified</p>' : ''}
                </div>
            </div>
        `).join('');
    }

    showError(message) {
        const resultsContainer = document.getElementById('search-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = `<div class="error-message">${message}</div>`;
        }
    }

    render() {
        return `
            <div class="search-section">
                <h1>Search Suppliers</h1>
                <div class="search-bar">
                    <input 
                        type="text" 
                        id="search-input" 
                        placeholder="Search by name, category, or products..." 
                        class="search-input"
                    />
                    <button id="search-button" class="search-button">Search</button>
                </div>
                <div id="search-results"></div>
            </div>
        `;
    }
}

// Export components
const Components = { Dashboard, SupplierList, SearchSuppliers };
