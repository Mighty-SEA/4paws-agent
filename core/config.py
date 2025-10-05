"""
Configuration for 4Paws Agent
Centralized configuration management
"""

from pathlib import Path
from .paths import get_base_dir, get_writable_dir


class Config:
    """Agent configuration"""
    
    # GitHub repositories
    FRONTEND_REPO = "Mighty-SEA/4paws-frontend"
    BACKEND_REPO = "Mighty-SEA/4paws-backend"
    GITHUB_API = "https://api.github.com/repos"
    
    # Local directories
    BASE_DIR = get_base_dir()
    WRITABLE_DIR = get_writable_dir()
    TOOLS_DIR = BASE_DIR / "tools"
    APPS_DIR = BASE_DIR / "apps"
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = WRITABLE_DIR / "logs"  # Use writable dir for logs
    
    # Tool directories
    NODE_DIR = TOOLS_DIR / "node"
    PNPM_DIR = TOOLS_DIR / "pnpm"
    MARIADB_DIR = TOOLS_DIR / "mariadb"
    
    # App directories
    FRONTEND_DIR = APPS_DIR / "frontend"
    BACKEND_DIR = APPS_DIR / "backend"
    
    # Version tracking (use writable dir)
    VERSION_FILE = WRITABLE_DIR / "versions.json"
    
    # MariaDB config
    MARIADB_PORT = 3307  # Changed to 3307 to avoid conflict with existing MariaDB
    MARIADB_DB = "4paws_db"
    MARIADB_USER = "root"
    MARIADB_PASSWORD = "4paws_secure_password"
    
    # App ports
    FRONTEND_PORT = 3100
    BACKEND_PORT = 3200
