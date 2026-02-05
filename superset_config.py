# Fissio Base - Superset Configuration
# Enables embedding dashboards across Fissio platform apps
# Includes Fissio dark theme styling

import os

# =============================================================================
# Security & Authentication
# =============================================================================

SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'fissio_secret_key_change_me')

# Enable public/guest access for embedded dashboards
PUBLIC_ROLE_LIKE = "Gamma"
GUEST_ROLE_NAME = "Public"
GUEST_TOKEN_JWT_SECRET = SECRET_KEY
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_HEADER_NAME = "X-GuestToken"

# =============================================================================
# Embedding Configuration
# =============================================================================

# Enable embedded dashboards feature
FEATURE_FLAGS = {
    "EMBEDDED_SUPERSET": True,
    "EMBEDDABLE_CHARTS": True,
    "DASHBOARD_RBAC": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# Allow iframes from Fissio apps
# Update these URLs for production
TALISMAN_ENABLED = False  # Disable for local dev, enable in production with proper CSP

# For production, use:
# TALISMAN_CONFIG = {
#     "content_security_policy": {
#         "frame-ancestors": ["'self'", "http://localhost:*", "https://fissio.com", "https://*.fissio.com"]
#     }
# }

# =============================================================================
# CORS Configuration
# =============================================================================

# Enable CORS for Fissio platform apps
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "resources": ["*"],
    "origins": [
        "http://localhost:8000",   # fissio-site
        "http://localhost:3000",   # fissio-docs UI
        "http://localhost:8001",   # fissio-docs API
        "http://localhost:3001",   # fissio-crmi
        "http://localhost:8888",   # jupyter
        "https://fissio.com",      # production website
        "https://*.fissio.com",    # subdomains
    ]
}

# =============================================================================
# HTTP Headers for Embedding
# =============================================================================

HTTP_HEADERS = {
    "X-Frame-Options": "ALLOWALL",  # Allow embedding in iframes
}

# Override default to allow embedding
OVERRIDE_HTTP_HEADERS = {
    "X-Frame-Options": "ALLOWALL",
}

# =============================================================================
# Database Connections
# =============================================================================

# Allow file-based databases (DuckDB, SQLite)
PREVENT_UNSAFE_DB_CONNECTIONS = False

# =============================================================================
# Misc Settings
# =============================================================================

# Superset webserver config
SUPERSET_WEBSERVER_TIMEOUT = 300

# Enable SQL Lab
ENABLE_PROXY_FIX = True

# Row limit for queries
ROW_LIMIT = 50000
SQL_MAX_ROW = 100000

# =============================================================================
# Fissio Dark Theme
# =============================================================================

# App name shown in header
APP_NAME = "Fissio Analytics"

# Custom CSS for Fissio dark theme
CUSTOM_CSS = """
/* Fissio Dark Theme for Superset */
:root {
    --fissio-bg-primary: #0a0a0a;
    --fissio-bg-secondary: #141414;
    --fissio-bg-tertiary: #1a1a1a;
    --fissio-bg-card: #1e1e1e;
    --fissio-bg-hover: #252525;
    --fissio-text-primary: #ffffff;
    --fissio-text-secondary: #a0a0a0;
    --fissio-text-muted: #666666;
    --fissio-accent: #00d492;
    --fissio-accent-hover: #00b87a;
    --fissio-border: #2a2a2a;
}

/* Main body and backgrounds */
body {
    background-color: var(--fissio-bg-primary) !important;
    color: var(--fissio-text-primary) !important;
}

/* Navigation header */
.navbar, .navbar-default, nav.navbar {
    background-color: var(--fissio-bg-secondary) !important;
    border-bottom: 1px solid var(--fissio-border) !important;
}

.navbar-brand, .navbar-brand span {
    color: var(--fissio-text-primary) !important;
}

/* Cards and panels */
.panel, .card, .dashboard-component, .chart-container {
    background-color: var(--fissio-bg-card) !important;
    border-color: var(--fissio-border) !important;
}

/* Sidebar */
.sidebar, .ant-layout-sider, .sidenav {
    background-color: var(--fissio-bg-secondary) !important;
}

/* Buttons */
.btn-primary, .ant-btn-primary {
    background-color: var(--fissio-accent) !important;
    border-color: var(--fissio-accent) !important;
}

.btn-primary:hover, .ant-btn-primary:hover {
    background-color: var(--fissio-accent-hover) !important;
    border-color: var(--fissio-accent-hover) !important;
}

/* Links */
a {
    color: var(--fissio-accent) !important;
}

a:hover {
    color: var(--fissio-accent-hover) !important;
}

/* Tables */
.table, table {
    background-color: var(--fissio-bg-card) !important;
    color: var(--fissio-text-primary) !important;
}

.table thead th, table thead th {
    background-color: var(--fissio-bg-tertiary) !important;
    border-color: var(--fissio-border) !important;
    color: var(--fissio-text-secondary) !important;
}

.table tbody td, table tbody td {
    border-color: var(--fissio-border) !important;
}

.table-striped tbody tr:nth-of-type(odd) {
    background-color: var(--fissio-bg-tertiary) !important;
}

/* Forms and inputs */
input, select, textarea, .form-control, .ant-input, .ant-select-selector {
    background-color: var(--fissio-bg-tertiary) !important;
    border-color: var(--fissio-border) !important;
    color: var(--fissio-text-primary) !important;
}

input:focus, select:focus, textarea:focus, .form-control:focus {
    border-color: var(--fissio-accent) !important;
    box-shadow: 0 0 0 2px rgba(0, 212, 146, 0.2) !important;
}

/* Dropdowns */
.dropdown-menu, .ant-dropdown-menu, .ant-select-dropdown {
    background-color: var(--fissio-bg-card) !important;
    border-color: var(--fissio-border) !important;
}

.dropdown-menu > li > a, .ant-dropdown-menu-item {
    color: var(--fissio-text-primary) !important;
}

.dropdown-menu > li > a:hover, .ant-dropdown-menu-item:hover {
    background-color: var(--fissio-bg-hover) !important;
}

/* Modals */
.modal-content, .ant-modal-content {
    background-color: var(--fissio-bg-card) !important;
    border-color: var(--fissio-border) !important;
}

.modal-header, .ant-modal-header {
    background-color: var(--fissio-bg-secondary) !important;
    border-color: var(--fissio-border) !important;
}

.modal-title, .ant-modal-title {
    color: var(--fissio-text-primary) !important;
}

/* Dashboard grid */
.dashboard-grid, .grid-container {
    background-color: var(--fissio-bg-primary) !important;
}

/* Chart backgrounds */
.slice_container, .chart-holder {
    background-color: var(--fissio-bg-card) !important;
}

/* Text colors */
h1, h2, h3, h4, h5, h6, .h1, .h2, .h3, .h4, .h5, .h6 {
    color: var(--fissio-text-primary) !important;
}

p, span, label, .text-muted {
    color: var(--fissio-text-secondary) !important;
}

/* SQL Lab */
.SqlLab, .sql-lab-container {
    background-color: var(--fissio-bg-primary) !important;
}

.ace_editor, .ace_content {
    background-color: var(--fissio-bg-tertiary) !important;
}

/* Tabs */
.nav-tabs > li > a {
    color: var(--fissio-text-secondary) !important;
}

.nav-tabs > li.active > a, .nav-tabs > li > a:hover {
    background-color: var(--fissio-bg-card) !important;
    border-color: var(--fissio-border) !important;
    color: var(--fissio-accent) !important;
}

/* Scrollbars */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--fissio-bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--fissio-border);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--fissio-text-muted);
}

/* Loading states */
.loading, .spinner {
    border-color: var(--fissio-accent) !important;
}

/* Alerts and notifications */
.alert-info {
    background-color: rgba(0, 212, 146, 0.1) !important;
    border-color: var(--fissio-accent) !important;
    color: var(--fissio-accent) !important;
}

/* Breadcrumbs */
.breadcrumb {
    background-color: var(--fissio-bg-tertiary) !important;
}

.breadcrumb > li > a {
    color: var(--fissio-accent) !important;
}

/* Pagination */
.pagination > li > a {
    background-color: var(--fissio-bg-card) !important;
    border-color: var(--fissio-border) !important;
    color: var(--fissio-text-primary) !important;
}

.pagination > .active > a {
    background-color: var(--fissio-accent) !important;
    border-color: var(--fissio-accent) !important;
}

/* Antd overrides */
.ant-menu-dark, .ant-menu-dark .ant-menu-sub {
    background: var(--fissio-bg-secondary) !important;
}

.ant-menu-dark .ant-menu-item-selected {
    background-color: var(--fissio-accent) !important;
}

.ant-card {
    background: var(--fissio-bg-card) !important;
    border-color: var(--fissio-border) !important;
}

.ant-card-head {
    background: var(--fissio-bg-tertiary) !important;
    border-color: var(--fissio-border) !important;
    color: var(--fissio-text-primary) !important;
}

.ant-table {
    background: var(--fissio-bg-card) !important;
    color: var(--fissio-text-primary) !important;
}

.ant-table-thead > tr > th {
    background: var(--fissio-bg-tertiary) !important;
    color: var(--fissio-text-secondary) !important;
}
"""

# Logo/favicon configuration (optional - add your logo files)
# APP_ICON = "/static/assets/images/fissio-logo.png"
# FAVICONS = [{"href": "/static/assets/images/fissio-favicon.ico"}]
