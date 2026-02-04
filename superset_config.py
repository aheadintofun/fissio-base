# Fissio Base - Superset Configuration
# Enables embedding dashboards across Fissio platform apps

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
