#!/usr/bin/env python3
"""
4Paws Deployment Agent
======================
Auto-download, update, and manage 4Paws frontend & backend releases from GitHub.
Includes portable Node.js, pnpm, and MariaDB management.
"""

import os
import sys
import json
import shutil
import zipfile
import subprocess
import requests
from pathlib import Path
from typing import Optional, Dict, List
import logging
from datetime import datetime
from dotenv import load_dotenv

# Determine base directory
# If running from Program Files (installer), use AppData for writable files
def get_base_dir():
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base = Path(sys.executable).parent
    else:
        # Running as script
        base = Path(__file__).parent.absolute()
    
    # Check if we're in Program Files (read-only location)
    base_str = str(base).lower()
    if 'program files' in base_str or 'programdata' in base_str:
        # Use installation directory for tools/apps, but AppData for logs/data
        return base
    return base

BASE_DIR = get_base_dir()

# Determine writable directory for logs and transient data
def get_writable_dir():
    base_str = str(BASE_DIR).lower()
    if 'program files' in base_str or 'programdata' in base_str:
        # Use AppData\Local for writable files
        appdata = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
        writable = appdata / '4PawsAgent'
        writable.mkdir(parents=True, exist_ok=True)
        return writable
    return BASE_DIR

WRITABLE_DIR = get_writable_dir()

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# Setup logging to writable directory
log_file = WRITABLE_DIR / 'agent.log'

# Custom handler to send logs to LogManager if available
class LogManagerHandler(logging.Handler):
    """Handler that sends logs to LogManager for Web GUI"""
    
    def __init__(self):
        super().__init__()
        self._log_manager = None
    
    def set_log_manager(self, log_manager):
        """Set the log manager instance"""
        self._log_manager = log_manager
    
    def emit(self, record):
        """Emit log to LogManager"""
        if not self._log_manager:
            return
        
        try:
            msg = self.format(record)
            
            # Filter out Flask/Werkzeug HTTP access logs
            # These are logged by werkzeug logger and contain patterns like:
            # "127.0.0.1 - - [timestamp] "GET /api/..." or "POST /socket.io/..."
            if '127.0.0.1 - -' in msg or 'GET /' in msg or 'POST /' in msg:
                return  # Don't send HTTP access logs to Web GUI
            
            # Filter out SocketIO internal logs
            if 'socket.io' in msg.lower() or 'websocket' in msg.lower():
                return
            
            # Remove the timestamp prefix since LogManager adds its own
            # Format: "2025-10-04 13:25:15,660 - INFO - message"
            # We want just the message part
            parts = msg.split(' - ', 2)
            if len(parts) >= 3:
                message = parts[2]  # Get the actual message
            else:
                message = msg
            
            # Map logging levels to LogManager levels
            level_map = {
                'INFO': 'info',
                'WARNING': 'warning',
                'ERROR': 'error',
                'CRITICAL': 'error',
                'DEBUG': 'info'
            }
            level = level_map.get(record.levelname, 'info')
            
            # Send to LogManager
            self._log_manager.log(message, level=level)
        except Exception:
            pass  # Fail silently to not break the app

# Create custom handler
log_manager_handler = LogManagerHandler()
log_manager_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(),
        log_manager_handler  # Add our custom handler
    ]
)
logger = logging.getLogger(__name__)

# Set console output to UTF-8 for emoji support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


class Config:
    """Agent configuration"""
    # GitHub repositories
    FRONTEND_REPO = "Mighty-SEA/4paws-frontend"
    BACKEND_REPO = "Mighty-SEA/4paws-backend"
    GITHUB_API = "https://api.github.com/repos"
    
    # Local directories
    BASE_DIR = BASE_DIR
    WRITABLE_DIR = WRITABLE_DIR
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


class GitHubClient:
    """Handle GitHub API interactions"""
    
    def __init__(self, repo: str):
        self.repo = repo
        self.api_url = f"{Config.GITHUB_API}/{repo}"
        # Get GitHub token from environment if available
        self.token = os.getenv('GITHUB_TOKEN', '')
        self.headers = {}
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
            logger.info("🔑 Using GitHub token for API requests")
    
    def get_latest_release(self) -> Optional[Dict]:
        """Get latest release info from GitHub"""
        try:
            url = f"{self.api_url}/releases/latest"
            logger.info(f"🔍 Checking latest release for {self.repo}...")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'tag_name': data['tag_name'],
                'name': data['name'],
                'published_at': data['published_at'],
                'assets': [
                    {
                        'name': asset['name'],
                        'download_url': asset['browser_download_url'],
                        'size': asset['size']
                    }
                    for asset in data['assets']
                    if asset['name'].endswith('.zip')
                ]
            }
        except requests.RequestException as e:
            logger.error(f"❌ Failed to fetch release info: {e}")
            return None
    
    def download_asset(self, url: str, output_path: Path) -> bool:
        """Download release asset"""
        try:
            logger.info(f"📥 Downloading from {url}...")
            response = requests.get(url, headers=self.headers, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r  Progress: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='')
            
            print()  # New line after progress
            logger.info(f"✅ Downloaded to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            return False


class VersionManager:
    """Track installed versions"""
    
    @staticmethod
    def load_versions() -> Dict:
        """Load version tracking file"""
        if Config.VERSION_FILE.exists():
            with open(Config.VERSION_FILE, 'r') as f:
                return json.load(f)
        return {
            'frontend': {'version': None, 'updated_at': None},
            'backend': {'version': None, 'updated_at': None}
        }
    
    @staticmethod
    def save_versions(versions: Dict):
        """Save version tracking file"""
        with open(Config.VERSION_FILE, 'w') as f:
            json.dump(versions, f, indent=2)
    
    @staticmethod
    def update_version(component: str, version: str):
        """Update component version"""
        versions = VersionManager.load_versions()
        versions[component] = {
            'version': version,
            'updated_at': datetime.now().isoformat()
        }
        VersionManager.save_versions(versions)


class ToolsManager:
    """Manage portable Node.js, pnpm, and MariaDB"""
    
    @staticmethod
    def setup_nodejs() -> bool:
        """Setup portable Node.js"""
        node_exe = Config.NODE_DIR / "node.exe"
        if node_exe.exists():
            logger.info("✅ Node.js already installed")
            # Verify version
            try:
                result = subprocess.run(
                    [str(node_exe), "--version"],
                    capture_output=True,
                    text=True
                )
                logger.info(f"   Version: {result.stdout.strip()}")
            except:
                pass
            return True
        
        logger.info("📦 Setting up portable Node.js...")
        logger.info("")
        logger.info("🔗 Download Link:")
        logger.info("   https://nodejs.org/dist/v20.11.0/node-v20.11.0-win-x64.zip")
        logger.info("")
        logger.info("📂 Extract to:")
        logger.info(f"   {Config.NODE_DIR}")
        logger.info("")
        logger.info("📋 Steps:")
        logger.info("   1. Download the ZIP file")
        logger.info("   2. Extract contents to tools/node/")
        logger.info("   3. Verify node.exe exists in tools/node/")
        logger.info("")
        logger.warning("⚠️  Manual setup required!")
        return False
    
    @staticmethod
    def setup_pnpm() -> bool:
        """Setup portable pnpm (standalone executable)"""
        pnpm_exe = Config.PNPM_DIR / "pnpm.exe"
        
        if pnpm_exe.exists():
            logger.info("✅ pnpm already installed")
            return True
        
        logger.info("📦 Downloading pnpm standalone...")
        
        try:
            # Get latest pnpm release from GitHub
            response = requests.get(
                "https://api.github.com/repos/pnpm/pnpm/releases/latest",
                timeout=10
            )
            response.raise_for_status()
            release_data = response.json()
            
            # Find Windows x64 asset
            asset_url = None
            for asset in release_data['assets']:
                if 'win-x64' in asset['name'] and asset['name'].endswith('.exe'):
                    asset_url = asset['browser_download_url']
                    break
            
            if not asset_url:
                raise Exception("pnpm Windows executable not found in release")
            
            logger.info(f"📥 Downloading from: {asset_url}")
            
            # Download pnpm
            Config.PNPM_DIR.mkdir(parents=True, exist_ok=True)
            response = requests.get(asset_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(pnpm_exe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info("✅ pnpm standalone downloaded successfully!")
            
            # Test pnpm
            result = subprocess.run(
                [str(pnpm_exe), "--version"],
                capture_output=True,
                text=True
            )
            logger.info(f"   pnpm version: {result.stdout.strip()}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download pnpm: {e}")
            logger.info("")
            logger.info("💡 Manual alternative:")
            logger.info("   1. Download: https://github.com/pnpm/pnpm/releases/latest")
            logger.info("   2. Get: pnpm-win-x64.exe")
            logger.info("   3. Rename to: pnpm.exe")
            logger.info(f"   4. Put in: {Config.PNPM_DIR}")
            return False
    
    @staticmethod
    def setup_mariadb() -> bool:
        """Setup portable MariaDB"""
        mysqld_exe = Config.MARIADB_DIR / "bin" / "mysqld.exe"
        if mysqld_exe.exists():
            logger.info("✅ MariaDB already installed")
            # Verify version
            try:
                mysql_exe = Config.MARIADB_DIR / "bin" / "mysql.exe"
                result = subprocess.run(
                    [str(mysql_exe), "--version"],
                    capture_output=True,
                    text=True
                )
                logger.info(f"   Version: {result.stdout.strip()}")
            except:
                pass
            return True
        
        logger.info("📦 Setting up portable MariaDB...")
        logger.info("")
        logger.info("🔗 Download Link:")
        logger.info("   https://mariadb.org/download/?t=mariadb&p=mariadb&r=11.4.2&os=windows&cpu=x86_64&pkg=zip")
        logger.info("")
        logger.info("📂 Extract to:")
        logger.info(f"   {Config.MARIADB_DIR}")
        logger.info("")
        logger.info("📋 Steps:")
        logger.info("   1. Download the ZIP file (Windows 64-bit)")
        logger.info("   2. Extract mariadb-11.x.x-winx64/ contents to tools/mariadb/")
        logger.info("   3. Verify mysqld.exe exists in tools/mariadb/bin/")
        logger.info("")
        logger.warning("⚠️  Manual setup required!")
        return False
    
    @staticmethod
    def init_mariadb() -> bool:
        """Initialize MariaDB database"""
        mysql_install_db = Config.MARIADB_DIR / "bin" / "mysql_install_db.exe"
        mysqld_exe = Config.MARIADB_DIR / "bin" / "mysqld.exe"
        
        if not mysqld_exe.exists():
            logger.error("❌ MariaDB not found!")
            return False
        
        data_dir = Config.DATA_DIR / "mariadb"
        if (data_dir / "mysql").exists():
            logger.info("✅ MariaDB already initialized")
            return True
        
        logger.info("🔧 Initializing MariaDB...")
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize data directory
            if mysql_install_db.exists():
                subprocess.run(
                    [
                        str(mysql_install_db),
                        f"--datadir={data_dir}",
                        "--default-user"
                    ],
                    check=True
                )
            else:
                # Alternative: Use mysqld --initialize
                subprocess.run(
                    [
                        str(mysqld_exe),
                        f"--datadir={data_dir}",
                        "--initialize-insecure"
                    ],
                    check=True
                )
            
            logger.info("✅ MariaDB initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize MariaDB: {e}")
            return False


class AppManager:
    """Manage frontend and backend apps"""
    
    @staticmethod
    def extract_release(zip_path: Path, extract_to: Path) -> bool:
        """Extract release ZIP"""
        try:
            logger.info(f"📂 Extracting {zip_path.name}...")
            
            # Remove old version if exists (no backup to avoid path length issues)
            if extract_to.exists():
                logger.info(f"🗑️  Removing old version...")
                try:
                    shutil.rmtree(extract_to)
                    logger.info(f"✅ Old version removed")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to remove old version: {e}")
                    logger.info("💡 Trying to extract anyway...")
            
            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            logger.info(f"✅ Extracted to {extract_to}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            return False
    
    @staticmethod
    def setup_env(app_dir: Path, app_type: str):
        """Setup .env file for app"""
        if app_type == "backend":
            # Backend uses .env
            env_path = app_dir / ".env"
            if env_path.exists():
                logger.info(f"✅ .env already exists for {app_type}")
                return
            
            logger.info(f"📝 Creating .env for {app_type}...")
            
            # Backend .env with MariaDB connection
            env_content = f"""DATABASE_URL="mysql://{Config.MARIADB_USER}:{Config.MARIADB_PASSWORD}@localhost:{Config.MARIADB_PORT}/{Config.MARIADB_DB}"
JWT_SECRET="4paws-jwt-secret-key-change-in-production"
PORT={Config.BACKEND_PORT}
NODE_ENV=production
"""
            
            with open(env_path, 'w') as f:
                f.write(env_content)
            
            logger.info(f"✅ .env created for {app_type}")
            
        else:
            # Frontend uses .env.production (for production build)
            env_prod_path = app_dir / ".env.production"
            
            if env_prod_path.exists():
                logger.info(f"✅ .env.production already exists for {app_type}")
            else:
                logger.info(f"📝 Creating .env.production for {app_type}...")
                
                # Frontend .env.production - Complete configuration for production builds
                env_prod_content = f"""# Backend API Configuration
BACKEND_API_URL=http://localhost:{Config.BACKEND_PORT}
NEXT_PUBLIC_API_BASE_URL=http://localhost:{Config.BACKEND_PORT}

# Agent API Configuration (for updates)
NEXT_PUBLIC_AGENT_URL=http://localhost:5000

# Server Configuration
NODE_ENV=production
PORT={Config.FRONTEND_PORT}
"""
                
                with open(env_prod_path, 'w') as f:
                    f.write(env_prod_content)
                
                logger.info(f"✅ .env.production created for {app_type}")
                logger.info(f"💡 Tip: Create .env.local manually for local overrides (git-ignored)")


class ProcessManager:
    """Manage running processes"""
    
    processes: Dict[str, subprocess.Popen] = {}
    
    @classmethod
    def start_mariadb(cls) -> bool:
        """Start MariaDB server"""
        if "mariadb" in cls.processes:
            logger.info("✅ MariaDB already running")
            return True
        
        mysqld_exe = Config.MARIADB_DIR / "bin" / "mysqld.exe"
        data_dir = Config.DATA_DIR / "mariadb"
        
        if not mysqld_exe.exists():
            logger.error("❌ MariaDB not found!")
            return False
        
        try:
            logger.info("🚀 Starting MariaDB...")
            process = subprocess.Popen(
                [
                    str(mysqld_exe),
                    f"--datadir={data_dir}",
                    f"--port={Config.MARIADB_PORT}",
                    "--default-storage-engine=InnoDB",
                    "--skip-grant-tables",  # Allow passwordless access for initial setup
                    "--console"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            cls.processes["mariadb"] = process
            logger.info(f"✅ MariaDB started (PID: {process.pid})")
            logger.info(f"🌐 MariaDB Port: {Config.MARIADB_PORT}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start MariaDB: {e}")
            return False
    
    @classmethod
    def start_backend(cls) -> bool:
        """Start backend server (simple mode - no install)"""
        if "backend" in cls.processes:
            logger.info("✅ Backend already running")
            return True
        
        # Use node directly instead of start.bat
        main_js = Config.BACKEND_DIR / "dist" / "src" / "main.js"
        if not main_js.exists():
            logger.error("❌ Backend build not found! Run: python agent.py install backend")
            return False
        
        # Check if node_modules exists
        if not (Config.BACKEND_DIR / "node_modules").exists():
            logger.error("❌ Dependencies not installed! Run: python agent.py setup-apps")
            return False
        
        try:
            logger.info("🚀 Starting backend...")
            
            # Prepare environment with Node.js and pnpm in PATH
            env = os.environ.copy()
            node_dir = str(Config.NODE_DIR.absolute())
            pnpm_dir = str(Config.PNPM_DIR.absolute())
            
            # Add portable tools to PATH (only for this subprocess)
            if 'PATH' in env:
                env['PATH'] = f"{node_dir};{pnpm_dir};{env['PATH']}"
            else:
                env['PATH'] = f"{node_dir};{pnpm_dir}"
            
            # Create log file path
            log_file = Config.LOGS_DIR / "backend.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Start with output redirect to log file
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    ["node", str(main_js)],
                    cwd=str(Config.BACKEND_DIR),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    env=env
                )
            
            cls.processes["backend"] = process
            logger.info(f"✅ Backend started (PID: {process.pid})")
            logger.info(f"🌐 Backend API: http://localhost:{Config.BACKEND_PORT}")
            logger.info(f"📝 Backend log: {log_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start backend: {e}")
            return False
    
    @classmethod
    def start_frontend(cls) -> bool:
        """Start frontend server (simple mode - no install)"""
        if "frontend" in cls.processes:
            logger.info("✅ Frontend already running")
            return True
        
        # Check if frontend build exists
        if not Config.FRONTEND_DIR.exists():
            logger.error("❌ Frontend not found! Run: python agent.py install frontend")
            return False
        
        # Check if node_modules exists
        if not (Config.FRONTEND_DIR / "node_modules").exists():
            logger.error("❌ Dependencies not installed! Run: python agent.py setup-apps")
            return False
        
        # Get full path to pnpm executable
        pnpm_exe = Config.PNPM_DIR / "pnpm.exe"
        if not pnpm_exe.exists():
            logger.error("❌ pnpm not found! Run: python agent.py setup")
            return False
        
        try:
            logger.info("🚀 Starting frontend...")
            
            # Prepare environment with Node.js and pnpm in PATH
            env = os.environ.copy()
            node_dir = str(Config.NODE_DIR.absolute())
            pnpm_dir = str(Config.PNPM_DIR.absolute())
            
            # Add portable tools to PATH (only for this subprocess)
            if 'PATH' in env:
                env['PATH'] = f"{node_dir};{pnpm_dir};{env['PATH']}"
            else:
                env['PATH'] = f"{node_dir};{pnpm_dir}"
            
            # Create log file path
            log_file = Config.LOGS_DIR / "frontend.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Start with output redirect to log file
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    [str(pnpm_exe), "start"],
                    cwd=str(Config.FRONTEND_DIR),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    env=env,
                    shell=False
                )
            
            cls.processes["frontend"] = process
            logger.info(f"✅ Frontend started (PID: {process.pid})")
            logger.info(f"🌐 Frontend URL: http://localhost:{Config.FRONTEND_PORT}")
            logger.info(f"📝 Frontend log: {log_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start frontend: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    @classmethod
    def stop_all(cls):
        """Stop all running processes"""
        for name, process in cls.processes.items():
            try:
                logger.info(f"⏹️  Stopping {name}...")
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"✅ {name} stopped")
            except Exception as e:
                logger.error(f"❌ Failed to stop {name}: {e}")
        
        cls.processes.clear()


class Agent:
    """Main agent orchestrator"""
    
    def __init__(self):
        self.frontend_client = GitHubClient(Config.FRONTEND_REPO)
        self.backend_client = GitHubClient(Config.BACKEND_REPO)
        
        # Create directories
        for dir_path in [Config.TOOLS_DIR, Config.APPS_DIR, Config.DATA_DIR, Config.LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def are_apps_installed(self) -> bool:
        """Check if both frontend and backend are installed"""
        return Config.FRONTEND_DIR.exists() and Config.BACKEND_DIR.exists()
    
    def auto_install_and_setup(self, progress_callback=None, log_callback=None):
        """
        Perform first-time installation and setup
        Used when apps are not installed yet
        
        Args:
            progress_callback: Optional function(progress, step, status, title, description)
                             to report progress (for installation server)
            log_callback: Optional function(message, level) to send log messages
        """
        def log(msg, level='info'):
            """Helper to log to both logger and callback"""
            if level == 'info':
                logger.info(msg)
            elif level == 'error':
                logger.error(msg)
            elif level == 'warning':
                logger.warning(msg)
            
            if log_callback:
                log_callback(msg, level)
        
        log("🚀 Starting first-time installation...")
        
        try:
            # Step 1: Download applications (0-40%)
            if progress_callback:
                progress_callback(0, 'download', 'active', 
                                'Downloading Applications', 
                                'Fetching latest releases from GitHub...')
            
            log("📥 Downloading frontend...")
            if not self.download_and_install("frontend"):
                log("❌ Failed to download frontend", 'error')
                return False
            
            if progress_callback:
                progress_callback(20, 'download', 'active')
            
            log("📥 Downloading backend...")
            if not self.download_and_install("backend"):
                log("❌ Failed to download backend", 'error')
                return False
            
            if progress_callback:
                progress_callback(40, 'download', 'completed')
            
            # Step 2: Install dependencies (40-60%)
            if progress_callback:
                progress_callback(40, 'install', 'active',
                                'Installing Dependencies',
                                'Setting up Node.js packages...')
            
            log("📦 Setting up applications...")
            if not self.setup_apps():
                log("❌ Failed to setup applications", 'error')
                return False
            
            if progress_callback:
                progress_callback(60, 'install', 'completed')
            
            # Step 3: Database is already done in setup_apps (60-80%)
            if progress_callback:
                progress_callback(80, 'database', 'completed',
                                'Database Ready',
                                'MariaDB configured and migrations complete')
            
            # Step 4: Start services (80-100%)
            if progress_callback:
                progress_callback(80, 'start', 'active',
                                'Starting Services',
                                'Launching frontend and backend...')
            
            log("🚀 Starting services...")
            if not self.start_all(skip_setup=True):
                log("❌ Failed to start services", 'error')
                return False
            
            if progress_callback:
                progress_callback(100, 'start', 'completed',
                                '✨ Installation Complete!',
                                'Your 4Paws system is ready to use')
            
            # Create desktop and start menu shortcuts
            log("🔗 Creating shortcuts...")
            try:
                from shortcut_manager import ShortcutManager
                results = ShortcutManager.create_frontend_shortcuts(port=Config.FRONTEND_PORT)
                if results['desktop']:
                    log("✅ Desktop shortcut created", 'success')
                if results['start_menu']:
                    log("✅ Start Menu shortcut created", 'success')
            except Exception as e:
                log(f"⚠️  Could not create shortcuts: {e}", 'warning')
            
            log("✅ First-time installation completed successfully!", 'success')
            return True
            
        except Exception as e:
            log(f"❌ Auto-install failed: {e}", 'error')
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def check_updates(self) -> Dict[str, Optional[str]]:
        """Check for updates on GitHub"""
        logger.info("🔍 Checking for updates...")
        
        versions = VersionManager.load_versions()
        updates = {}
        
        # Check if apps are installed
        frontend_installed = Config.FRONTEND_DIR.exists()
        backend_installed = Config.BACKEND_DIR.exists()
        
        # Check frontend
        frontend_release = self.frontend_client.get_latest_release()
        if frontend_release:
            latest = frontend_release['tag_name']
            if not frontend_installed:
                updates['frontend'] = latest
                logger.info(f"📦 Frontend not installed. Latest version available: {latest}")
            else:
                current = versions['frontend']['version']
                if current != latest:
                    updates['frontend'] = latest
                    logger.info(f"🆕 Frontend update available: {current} → {latest}")
                else:
                    logger.info(f"✅ Frontend up to date: {current}")
        
        # Check backend
        backend_release = self.backend_client.get_latest_release()
        if backend_release:
            latest = backend_release['tag_name']
            if not backend_installed:
                updates['backend'] = latest
                logger.info(f"📦 Backend not installed. Latest version available: {latest}")
            else:
                current = versions['backend']['version']
                if current != latest:
                    updates['backend'] = latest
                    logger.info(f"🆕 Backend update available: {current} → {latest}")
                else:
                    logger.info(f"✅ Backend up to date: {current}")
        
        return updates
    
    def download_and_install(self, component: str) -> bool:
        """Download and install component"""
        client = self.frontend_client if component == "frontend" else self.backend_client
        release = client.get_latest_release()
        
        if not release or not release['assets']:
            logger.error(f"❌ No release found for {component}")
            return False
        
        # Find portable ZIP
        asset = None
        for a in release['assets']:
            if 'portable' in a['name'].lower():
                asset = a
                break
        
        if not asset:
            logger.error(f"❌ No portable build found for {component}")
            return False
        
        # Download
        zip_path = Config.APPS_DIR / asset['name']
        if not client.download_asset(asset['download_url'], zip_path):
            return False
        
        # Extract
        extract_dir = Config.FRONTEND_DIR if component == "frontend" else Config.BACKEND_DIR
        if not AppManager.extract_release(zip_path, extract_dir):
            return False
        
        # Setup .env
        AppManager.setup_env(extract_dir, component)
        
        # Update version
        VersionManager.update_version(component, release['tag_name'])
        
        # Cleanup ZIP
        zip_path.unlink()
        
        logger.info(f"✅ {component.capitalize()} installed successfully!")
        return True
    
    def setup_tools(self) -> bool:
        """Setup all required tools"""
        logger.info("🔧 Setting up tools...")
        
        success = True
        success &= ToolsManager.setup_nodejs()
        success &= ToolsManager.setup_pnpm()
        success &= ToolsManager.setup_mariadb()
        success &= ToolsManager.init_mariadb()
        
        return success
    
    def setup_apps(self, component: str = "all") -> bool:
        """Setup apps: install dependencies and run migrations"""
        logger.info("🔧 Setting up applications...")
        
        # Ensure .env files exist
        if component in ["backend", "all"] and Config.BACKEND_DIR.exists():
            AppManager.setup_env(Config.BACKEND_DIR, "backend")
        if component in ["frontend", "all"] and Config.FRONTEND_DIR.exists():
            AppManager.setup_env(Config.FRONTEND_DIR, "frontend")
        
        # Start MariaDB if setting up backend (needed for migrations)
        mariadb_started = False
        if component in ["backend", "all"]:
            logger.info("🚀 Starting MariaDB for database setup...")
            if ProcessManager.start_mariadb():
                mariadb_started = True
                logger.info("✅ MariaDB started")
                # Wait for MariaDB to be ready
                import time
                time.sleep(3)
            else:
                logger.error("❌ Failed to start MariaDB!")
                return False
        
        success = True
        
        if component in ["backend", "all"]:
            success &= self._setup_backend()
        
        if component in ["frontend", "all"]:
            success &= self._setup_frontend()
        
        # Stop MariaDB if we started it
        if mariadb_started:
            logger.info("⏹️  Stopping MariaDB...")
            if "mariadb" in ProcessManager.processes:
                try:
                    ProcessManager.processes["mariadb"].terminate()
                    ProcessManager.processes["mariadb"].wait(timeout=10)
                    del ProcessManager.processes["mariadb"]
                    logger.info("✅ MariaDB stopped")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to stop MariaDB: {e}")
        
        if success:
            logger.info("✅ Application setup complete!")
        else:
            logger.error("❌ Application setup failed!")
        
        return success
    
    def _setup_backend(self) -> bool:
        """Setup backend: pnpm install + prisma generate + migrate"""
        if not Config.BACKEND_DIR.exists():
            logger.error("❌ Backend not installed! Run: python agent.py install backend")
            return False
        
        logger.info("🔧 Setting up backend...")
        
        # Get full path to pnpm executable
        pnpm_exe = Config.PNPM_DIR / "pnpm.exe"
        if not pnpm_exe.exists():
            logger.error("❌ pnpm not found! Run: python agent.py setup")
            return False
        
        # Prepare environment with Node.js in PATH
        env = os.environ.copy()
        node_dir = str(Config.NODE_DIR.absolute())
        pnpm_dir = str(Config.PNPM_DIR.absolute())
        env['PATH'] = f"{node_dir};{pnpm_dir};{env.get('PATH', '')}"
        
        try:
            # 1. Install dependencies
            logger.info("📦 Installing dependencies...")
            result = subprocess.run(
                [str(pnpm_exe), "install", "--production", "--ignore-scripts"],
                cwd=str(Config.BACKEND_DIR),
                env=env,
                capture_output=True,
                text=True,
                shell=False
            )
            if result.returncode != 0:
                logger.error(f"❌ Failed to install dependencies:")
                logger.error(result.stderr)
                return False
            logger.info("✅ Dependencies installed")
            
            # 2. Generate Prisma client
            prisma_client = Config.BACKEND_DIR / "node_modules" / ".prisma" / "client"
            if prisma_client.exists():
                logger.info("✅ Prisma client already exists, skipping generate...")
            else:
                logger.info("🔧 Generating Prisma client...")
                result = subprocess.run(
                    [str(pnpm_exe), "prisma", "generate"],
                    cwd=str(Config.BACKEND_DIR),
                    env=env,
                    capture_output=True,
                    text=True,
                    shell=False
                )
                if result.returncode != 0:
                    logger.error(f"❌ Failed to generate Prisma client:")
                    logger.error(result.stderr)
                    logger.warning("⚠️  Trying to continue anyway...")
                else:
                    logger.info("✅ Prisma client generated")
            
            # 3. Create database if not exists
            logger.info("🗄️  Creating database if not exists...")
            mysql_exe = Config.MARIADB_DIR / "bin" / "mysql.exe"
            if mysql_exe.exists():
                try:
                    # Create database command
                    create_db_sql = f"CREATE DATABASE IF NOT EXISTS {Config.MARIADB_DB};"
                    subprocess.run(
                        [
                            str(mysql_exe),
                            "-u", Config.MARIADB_USER,
                            "-P", str(Config.MARIADB_PORT),
                            "-e", create_db_sql
                        ],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    logger.info(f"✅ Database '{Config.MARIADB_DB}' ready")
                except Exception as e:
                    logger.warning(f"⚠️  Could not create database: {e}")
                    logger.info("💡 Make sure MariaDB is running")
            
            # 4. Run migrations
            logger.info("🗄️  Running database migrations...")
            result = subprocess.run(
                [str(pnpm_exe), "prisma", "migrate", "deploy"],
                cwd=str(Config.BACKEND_DIR),
                env=env,
                capture_output=True,
                text=True,
                shell=False
            )
            if result.returncode != 0:
                logger.error(f"❌ Migration failed:")
                logger.error(result.stderr)
                logger.info("💡 Make sure MariaDB is running and DATABASE_URL is correct")
                return False
            else:
                logger.info("✅ Migrations completed")
            
            logger.info("✅ Backend setup complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backend setup failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _setup_frontend(self) -> bool:
        """Setup frontend: pnpm install"""
        if not Config.FRONTEND_DIR.exists():
            logger.error("❌ Frontend not installed! Run: python agent.py install frontend")
            return False
        
        logger.info("🔧 Setting up frontend...")
        
        # Get full path to pnpm executable
        pnpm_exe = Config.PNPM_DIR / "pnpm.exe"
        if not pnpm_exe.exists():
            logger.error("❌ pnpm not found! Run: python agent.py setup")
            return False
        
        # Prepare environment with Node.js in PATH
        env = os.environ.copy()
        node_dir = str(Config.NODE_DIR.absolute())
        pnpm_dir = str(Config.PNPM_DIR.absolute())
        env['PATH'] = f"{node_dir};{pnpm_dir};{env.get('PATH', '')}"
        
        try:
            # Install dependencies
            logger.info("📦 Installing dependencies...")
            result = subprocess.run(
                [str(pnpm_exe), "install", "--production", "--ignore-scripts"],
                cwd=str(Config.FRONTEND_DIR),
                env=env,
                capture_output=True,
                text=True,
                shell=False
            )
            if result.returncode != 0:
                logger.error(f"❌ Failed to install dependencies:")
                logger.error(result.stderr)
                return False
            
            logger.info("✅ Frontend setup complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Frontend setup failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def start_all(self, skip_setup: bool = False):
        """Start all services (with optional auto-setup)"""
        logger.info("🚀 Starting all services...")
        
        # Start MariaDB first (needed for setup-apps)
        if not ProcessManager.start_mariadb():
            logger.error("❌ Failed to start MariaDB!")
            return False
        
        # Wait a bit for MariaDB to fully start
        import time
        time.sleep(3)
        
        # Auto-detect if setup needed (unless skip_setup is True)
        if not skip_setup:
            needs_setup = False
            
            if Config.BACKEND_DIR.exists() and not (Config.BACKEND_DIR / "node_modules").exists():
                logger.info("⚠️  Backend dependencies not installed")
                needs_setup = True
            
            if Config.FRONTEND_DIR.exists() and not (Config.FRONTEND_DIR / "node_modules").exists():
                logger.info("⚠️  Frontend dependencies not installed")
                needs_setup = True
            
            if needs_setup:
                logger.info("🔧 First run detected, setting up applications...")
                logger.info("💡 This will take 2-3 minutes...")
                if not self.setup_apps():
                    logger.error("❌ Setup failed! Cannot start services.")
                    ProcessManager.stop_all()
                    return False
                logger.info("")
        
        # Wait a bit for MariaDB to start
        import time
        time.sleep(5)
        
        # Start backend
        if not ProcessManager.start_backend():
            logger.error("❌ Failed to start backend!")
            return False
        
        # Wait for backend to start
        time.sleep(5)
        
        # Start frontend
        if not ProcessManager.start_frontend():
            logger.error("❌ Failed to start frontend!")
            return False
        
        logger.info("✅ All services started!")
        logger.info(f"🌐 Access app at: http://localhost:{Config.FRONTEND_PORT}")
        return True
    
    def stop_all(self):
        """Stop all services"""
        logger.info("⏹️  Stopping all services...")
        ProcessManager.stop_all()
        logger.info("✅ All services stopped")
    
    def seed_database(self, seed_type: str = "all") -> bool:
        """Seed the database with initial data"""
        if not Config.BACKEND_DIR.exists():
            logger.error("❌ Backend not installed! Run: python agent.py install backend")
            return False
        
        # Get full path to pnpm executable
        pnpm_exe = Config.PNPM_DIR / "pnpm.exe"
        if not pnpm_exe.exists():
            logger.error("❌ pnpm not found! Run: python agent.py setup")
            return False
        
        # Prepare environment with Node.js in PATH
        env = os.environ.copy()
        node_dir = str(Config.NODE_DIR.absolute())
        pnpm_dir = str(Config.PNPM_DIR.absolute())
        env['PATH'] = f"{node_dir};{pnpm_dir};{env.get('PATH', '')}"
        
        # Check if MariaDB is running
        mariadb_started = False
        if "mariadb" not in ProcessManager.processes:
            logger.info("🚀 Starting MariaDB for seeding...")
            if ProcessManager.start_mariadb():
                mariadb_started = True
                import time
                time.sleep(3)
            else:
                logger.error("❌ Failed to start MariaDB!")
                return False
        
        try:
            logger.info(f"🌱 Seeding database ({seed_type})...")
            
            # Determine which seed command to run
            valid_seeds = {
                "all": "prisma:seed",
                "services": "prisma:seed:services",
                "store-settings": "prisma:seed:store-settings",
                "pet-species": "prisma:seed:pet-species",
                "owners-pets": "prisma:seed:owners-pets",
                "products-mix": "prisma:seed:products-mix"
            }
            
            if seed_type not in valid_seeds:
                logger.error(f"❌ Unknown seed type: {seed_type}")
                logger.info(f"💡 Valid seed types: {', '.join(valid_seeds.keys())}")
                return False
            
            seed_cmd = valid_seeds[seed_type]
            
            result = subprocess.run(
                [str(pnpm_exe), "run", seed_cmd],
                cwd=str(Config.BACKEND_DIR),
                env=env,
                capture_output=True,
                text=True,
                shell=False
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Seeding failed:")
                logger.error(result.stderr)
                if result.stdout:
                    logger.info("Output:")
                    logger.info(result.stdout)
                return False
            
            # Log output
            if result.stdout:
                logger.info(result.stdout)
            
            logger.info(f"✅ Database seeded successfully ({seed_type})!")
            
            # Stop MariaDB if we started it
            if mariadb_started and "mariadb" in ProcessManager.processes:
                logger.info("⏹️  Stopping MariaDB...")
                ProcessManager.processes["mariadb"].terminate()
                ProcessManager.processes["mariadb"].wait(timeout=10)
                del ProcessManager.processes["mariadb"]
                logger.info("✅ MariaDB stopped")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Seeding failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def install_apps(self, component: str = "all") -> bool:
        """Install applications from GitHub releases"""
        try:
            if component == "all":
                logger.info("📦 Installing both frontend and backend...")
                frontend_ok = self.download_and_install("frontend")
                backend_ok = self.download_and_install("backend")
                return frontend_ok and backend_ok
            else:
                return self.download_and_install(component)
        except Exception as e:
            logger.error(f"❌ Installation failed: {e}")
            return False
    
    def update_apps(self, component: str = "all", force: bool = False) -> bool:
        """Update applications"""
        try:
            # Check for updates first
            updates = self.check_updates()
            
            if not force and not updates:
                logger.info("✅ Everything is up to date!")
                return True
            
            # Stop services before updating
            logger.info("⏹️  Stopping services for update...")
            ProcessManager.stop_all()
            
            # Install updates
            if component == "all":
                success = True
                if 'frontend' in updates or force:
                    logger.info("📥 Updating frontend...")
                    success = self.download_and_install("frontend") and success
                if 'backend' in updates or force:
                    logger.info("📥 Updating backend...")
                    success = self.download_and_install("backend") and success
                return success
            else:
                if component in updates or force:
                    logger.info(f"📥 Updating {component}...")
                    return self.download_and_install(component)
                else:
                    logger.info(f"✅ {component} is already up to date!")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Update failed: {e}")
            return False


def set_agent_log_manager(log_manager):
    """
    Set LogManager for agent logging
    This should be called from gui_server.py to enable web GUI logging
    """
    log_manager_handler.set_log_manager(log_manager)
    logger.info("📋 Agent logging connected to Web GUI")


def main():
    """Main entry point"""
    print("""
╔════════════════════════════════════════╗
║   4Paws Deployment Agent v1.0         ║
║   Auto-update & manage releases       ║
╚════════════════════════════════════════╝
    """)
    
    agent = Agent()
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python agent.py setup                    - Setup tools (Node.js, pnpm, MariaDB)")
        print("  python agent.py check                    - Check for updates from GitHub")
        print("  python agent.py install [component]      - Install frontend/backend/all")
        print("  python agent.py setup-apps [component]   - Setup apps (pnpm install + migrate)")
        print("  python agent.py seed [type]              - Seed database (all/services/etc)")
        print("  python agent.py start [--skip-setup]     - Start all services")
        print("  python agent.py stop                     - Stop all services")
        print("  python agent.py update [component] [-y]  - Update frontend/backend/all (with confirmation)")
        print("  python agent.py shortcuts create         - Create desktop and start menu shortcuts")
        print("  python agent.py shortcuts remove         - Remove shortcuts")
        print("  python agent.py shortcuts check          - Check if shortcuts exist")
        print("\nExamples:")
        print("  python agent.py check                    - Check updates only")
        print("  python agent.py update                   - Update all (asks confirmation)")
        print("  python agent.py update frontend          - Update frontend only")
        print("  python agent.py update --yes             - Update all (no confirmation)")
        print("  python agent.py shortcuts create         - Create shortcuts")
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "setup":
            agent.setup_tools()
            print("\n💡 Next steps:")
            print("  1. Download tools manually (Node.js, MariaDB)")
            print("  2. Run: python agent.py install all")
            print("  3. Run: python agent.py setup-apps")
            print("  4. Run: python agent.py start")
        
        elif command == "check":
            updates = agent.check_updates()
            if updates:
                print(f"\n🆕 {len(updates)} update(s) available!")
                for comp, version in updates.items():
                    print(f"  - {comp}: {version}")
            else:
                print("\n✅ Everything up to date!")
        
        elif command == "install":
            component = sys.argv[2] if len(sys.argv) > 2 else "all"
            
            if component in ["frontend", "all"]:
                agent.download_and_install("frontend")
            
            if component in ["backend", "all"]:
                agent.download_and_install("backend")
            
            print("\n💡 Next step:")
            print(f"  Run: python agent.py setup-apps {component if component != 'all' else ''}")
        
        elif command == "setup-apps":
            component = sys.argv[2] if len(sys.argv) > 2 else "all"
            agent.setup_apps(component)
            print("\n💡 Next step:")
            print("  Run: python agent.py start")
        
        elif command == "seed":
            seed_type = sys.argv[2] if len(sys.argv) > 2 else "all"
            agent.seed_database(seed_type)
            print("\n💡 Available seed types:")
            print("  - all (default - runs all seeds)")
            print("  - services")
            print("  - store-settings")
            print("  - pet-species")
            print("  - owners-pets")
            print("  - products-mix")
        
        elif command == "start":
            # Check for --skip-setup flag
            skip_setup = "--skip-setup" in sys.argv
            agent.start_all(skip_setup=skip_setup)
            print("\n✅ Services running. Press Ctrl+C to stop...")
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️  Stopping services...")
                agent.stop_all()
        
        elif command == "stop":
            agent.stop_all()
        
        elif command == "update":
            # Check if specific component is specified
            component = sys.argv[2] if len(sys.argv) > 2 else "all"
            
            # Get available updates
            all_updates = agent.check_updates()
            
            # Filter updates based on component
            if component != "all":
                updates = {component: all_updates[component]} if component in all_updates else {}
            else:
                updates = all_updates
            
            if not updates:
                print(f"\n✅ {component.capitalize() if component != 'all' else 'Everything'} up to date!")
                return
            
            # Show updates
            print(f"\n🆕 Updates available:")
            for comp, version in updates.items():
                current = VersionManager.load_versions()[comp]['version']
                print(f"  - {comp}: {current} → {version}")
            
            # Ask for confirmation (unless --yes flag is provided)
            if "--yes" not in sys.argv and "-y" not in sys.argv:
                response = input("\n❓ Install these updates? (y/n): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("❌ Update cancelled")
                    return
            
            # Install updates
            print(f"\n🚀 Installing {len(updates)} update(s)...")
            for component in updates.keys():
                if agent.download_and_install(component):
                    print(f"✅ {component.capitalize()} updated!")
                else:
                    print(f"❌ {component.capitalize()} update failed!")
            
            print("\n💡 Next steps:")
            print("  1. Run: python agent.py setup-apps")
            print("  2. Run: python agent.py start")
        
        elif command == "shortcuts":
            # Shortcuts management
            from shortcut_manager import ShortcutManager
            
            if len(sys.argv) < 3:
                print("\nUsage:")
                print("  python agent.py shortcuts create  - Create shortcuts")
                print("  python agent.py shortcuts remove  - Remove shortcuts")
                print("  python agent.py shortcuts check   - Check if shortcuts exist")
                return
            
            action = sys.argv[2].lower()
            
            if action == "create":
                print("🔗 Creating shortcuts...")
                results = ShortcutManager.create_frontend_shortcuts(port=Config.FRONTEND_PORT)
                
                if results['desktop'] and results['start_menu']:
                    print("\n✅ All shortcuts created successfully!")
                    print(f"  - Desktop: {ShortcutManager.get_desktop_path()}")
                    print(f"  - Start Menu: {ShortcutManager.get_start_menu_path() / '4Paws'}")
                elif results['desktop'] or results['start_menu']:
                    print("\n⚠️  Some shortcuts created")
                    if results['desktop']:
                        print(f"  ✅ Desktop: {ShortcutManager.get_desktop_path()}")
                    if results['start_menu']:
                        print(f"  ✅ Start Menu: {ShortcutManager.get_start_menu_path() / '4Paws'}")
                else:
                    print("\n❌ Failed to create shortcuts")
            
            elif action == "remove":
                print("🗑️  Removing shortcuts...")
                removed = ShortcutManager.remove_frontend_shortcuts()
                
                if removed:
                    print(f"\n✅ Removed shortcuts: {', '.join(removed)}")
                else:
                    print("\n❌ No shortcuts found to remove")
            
            elif action == "check":
                print("🔍 Checking shortcuts...")
                shortcuts = ShortcutManager.check_shortcuts_exist()
                
                print(f"\nDesktop: {'✅ Exists' if shortcuts['desktop'] else '❌ Not found'}")
                print(f"Start Menu: {'✅ Exists' if shortcuts['start_menu'] else '❌ Not found'}")
                
                if shortcuts['desktop']:
                    print(f"  📍 {ShortcutManager.get_desktop_path() / '4Paws Pet Management.url'}")
                if shortcuts['start_menu']:
                    print(f"  📍 {ShortcutManager.get_start_menu_path() / '4Paws' / '4Paws Pet Management.url'}")
            else:
                print(f"❌ Unknown shortcuts action: {action}")
        
        else:
            print(f"❌ Unknown command: {command}")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

