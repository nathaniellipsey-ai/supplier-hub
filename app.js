/**
 * Main Application Controller
 * Manages routing, state, and component lifecycle
 * Professional application architecture
 */

class App {
    constructor() {
        this.currentView = null;
        this.appState = {
            dashboard: null,
            suppliers: null,
            search: null,
            theme: 'light'
        };
        this.routes = {
            'dashboard': () => this.showDashboard(),
            'suppliers': () => this.showSuppliers(),
            'search': () => this.showSearch()
        };
    }

    /**
     * Initialize the application
     */
    async init() {
        console.log('Initializing Supplier Search Engine...');
        
        // Check API connectivity
        try {
            const health = await api.health();
            console.log('API is healthy:', health);
        } catch (error) {
            console.warn('API unavailable, using local mode:', error);
        }

        // Set up routing
        this.setupRouting();
        
        // Load initial view
        const initialView = window.location.hash.slice(1) || 'dashboard';
        this.navigate(initialView);

        // Set up event listeners
        this.setupEventListeners();
    }

    /**
     * Set up hash-based routing
     */
    setupRouting() {
        window.addEventListener('hashchange', () => {
            const view = window.location.hash.slice(1) || 'dashboard';
            this.navigate(view);
        });
    }

    /**
     * Set up global event listeners
     */
    setupEventListeners() {
        // Navigation clicks
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = link.getAttribute('href').slice(1);
                this.navigate(view);
            });
        });
    }

    /**
     * Navigate to a view
     */
    navigate(viewName) {
        const handler = this.routes[viewName];
        if (handler) {
            handler();
            window.location.hash = viewName;
        }
    }

    /**
     * Show dashboard view
     */
    showDashboard() {
        this.clearView();
        this.appState.dashboard = new Dashboard();
        this.appState.dashboard.mount('#app-content');
        this.updateActiveNav('dashboard');
    }

    /**
     * Show suppliers view
     */
    showSuppliers() {
        this.clearView();
        this.appState.suppliers = new SupplierList();
        this.appState.suppliers.mount('#app-content');
        this.updateActiveNav('suppliers');
        
        // Expose suppliers instance to global scope for pagination
        window.appState = this.appState;
    }

    /**
     * Show search view
     */
    showSearch() {
        this.clearView();
        this.appState.search = new SearchSuppliers();
        this.appState.search.mount('#app-content');
        this.updateActiveNav('search');
    }

    /**
     * Clear current view
     */
    clearView() {
        const content = document.getElementById('app-content');
        if (content) {
            content.innerHTML = '';
        }
    }

    /**
     * Update active navigation indicator
     */
    updateActiveNav(viewName) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${viewName}`) {
                link.classList.add('active');
            }
        });
    }

    /**
     * Show loading indicator
     */
    showLoading() {
        const content = document.getElementById('app-content');
        if (content) {
            content.innerHTML = '<div class="loading"><span>Loading...</span></div>';
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const content = document.getElementById('app-content');
        if (content) {
            content.innerHTML = `<div class="error-message">${message}</div>`;
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
    window.app.init();
});
