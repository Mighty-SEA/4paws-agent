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

# Import core modules
from core import Config, setup_logging, get_log_manager_handler

# Load environment variables from .env file
load_dotenv(Config.BASE_DIR / '.env')

# Setup logging to writable directory
log_file = Config.WRITABLE_DIR / 'agent.log'
logger, log_manager_handler = setup_logging(log_file)


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
    
    def get_latest_release(self, max_retries: int = 3) -> Optional[Dict]:
        """Get latest release info from GitHub with retry logic"""
        import time
        
        url = f"{self.api_url}/releases/latest"
        
        for attempt in range(1, max_retries + 1):
            try:
                if attempt == 1:
                    logger.info(f"🔍 Checking latest release for {self.repo}...")
                else:
                    logger.info(f"🔄 Retry attempt {attempt}/{max_retries} for {self.repo}...")
                
                response = requests.get(url, headers=self.headers, timeout=15)
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
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 2, 4, 8 seconds
                    logger.warning(f"⚠️  Network error (attempt {attempt}/{max_retries}): {str(e)[:100]}")
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed after {max_retries} attempts: Network connection error")
                    logger.error(f"💡 Check your internet connection or try again later")
                    return None
            except requests.exceptions.Timeout as e:
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"⚠️  Request timeout (attempt {attempt}/{max_retries})")
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed after {max_retries} attempts: Request timeout")
                    logger.error(f"💡 GitHub API might be slow, try again later")
                    return None
            except requests.exceptions.HTTPError as e:
                # Don't retry on HTTP errors (404, 403, etc) - these won't fix with retry
                logger.error(f"❌ HTTP Error: {e}")
                if e.response.status_code == 403:
                    logger.error(f"💡 Rate limit exceeded. Use GITHUB_TOKEN or wait 1 hour")
                return None
            except requests.RequestException as e:
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"⚠️  Request failed (attempt {attempt}/{max_retries}): {str(e)[:100]}")
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    def download_asset(self, url: str, output_path: Path, max_retries: int = 3) -> bool:
        """Download release asset with retry logic"""
        import time
        
        for attempt in range(1, max_retries + 1):
            try:
                if attempt == 1:
                    logger.info(f"📥 Downloading from {url}...")
                else:
                    logger.info(f"🔄 Download retry attempt {attempt}/{max_retries}...")
                
                response = requests.get(url, headers=self.headers, stream=True, timeout=60)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Download with progress
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
                
                # Verify download completed
                if total_size > 0 and downloaded < total_size:
                    raise Exception(f"Incomplete download: {downloaded}/{total_size} bytes")
                
                logger.info(f"✅ Downloaded to {output_path}")
                return True
                
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries:
                    wait_time = 3 ** attempt  # 3, 9, 27 seconds
                    logger.warning(f"⚠️  Download failed (attempt {attempt}/{max_retries}): {str(e)[:100]}")
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    
                    # Clean up partial download
                    if output_path.exists():
                        try:
                            output_path.unlink()
                        except:
                            pass
                    
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Download failed after {max_retries} attempts")
                    logger.error(f"💡 Check your internet connection and try again")
                    return False
                    
            except requests.exceptions.HTTPError as e:
                # Don't retry on HTTP errors
                logger.error(f"❌ Download failed: HTTP {e.response.status_code}")
                return False
                
            except Exception as e:
                if attempt < max_retries:
                    wait_time = 3 ** attempt
                    logger.warning(f"⚠️  Download error (attempt {attempt}/{max_retries}): {str(e)[:100]}")
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    
                    # Clean up partial download
                    if output_path.exists():
                        try:
                            output_path.unlink()
                        except:
                            pass
                    
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Download failed after {max_retries} attempts: {e}")
                    return False
        
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


class NetworkUtils:
    """Network utility functions"""
    
    @staticmethod
    def test_connectivity(url: str = "https://registry.npmjs.org/", timeout: int = 5) -> bool:
        """Test network connectivity to a URL"""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def get_best_registry() -> str:
        """Test and return the fastest npm registry"""
        registries = [
            ("https://registry.npmjs.org/", "Official npm"),
            ("https://registry.npmmirror.com/", "npmmirror (China)"),
            ("https://registry.npm.taobao.org/", "Taobao (China)"),
        ]
        
        logger.info("🔍 Testing npm registries for best connection...")
        fastest = None
        fastest_time = float('inf')
        
        for url, name in registries:
            try:
                import time
                start = time.time()
                response = requests.head(url, timeout=3)
                elapsed = time.time() - start
                
                if response.status_code == 200 and elapsed < fastest_time:
                    fastest = url
                    fastest_time = elapsed
                    logger.info(f"   ✅ {name}: {elapsed:.2f}s")
                else:
                    logger.info(f"   ⚠️  {name}: timeout or error")
            except:
                logger.info(f"   ❌ {name}: unreachable")
        
        if fastest:
            logger.info(f"✅ Selected: {fastest} ({fastest_time:.2f}s)")
            return fastest
        else:
            logger.warning("⚠️  All registries unreachable, using default")
            return "https://registry.npmjs.org/"


class DiskUtils:
    """Disk utility functions"""
    
    @staticmethod
    def get_free_space(path: Path) -> int:
        """Get free disk space in bytes"""
        import shutil
        stat = shutil.disk_usage(path)
        return stat.free
    
    @staticmethod
    def check_disk_space(path: Path, required_gb: float = 5.0) -> bool:
        """Check if there's enough disk space"""
        try:
            free_bytes = DiskUtils.get_free_space(path)
            free_gb = free_bytes / (1024 ** 3)
            
            logger.info(f"💾 Disk space check: {free_gb:.2f} GB free")
            
            if free_gb < required_gb:
                logger.error(f"❌ Insufficient disk space!")
                logger.error(f"   Required: {required_gb:.2f} GB")
                logger.error(f"   Available: {free_gb:.2f} GB")
                logger.error(f"   Free up at least {required_gb - free_gb:.2f} GB")
                return False
            
            logger.info(f"✅ Sufficient disk space ({free_gb:.2f} GB)")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Could not check disk space: {e}")
            return True  # Don't block if check fails


class ToolsManager:
    """Manage portable Node.js, pnpm, and MariaDB"""
    
    @staticmethod
    def setup_pnpm_config():
        """Configure pnpm for optimal performance"""
        try:
            pnpm_exe = ToolsManager.get_pnpm_path() / "pnpm.exe"
            if not pnpm_exe.exists():
                return
            
            logger.info("🔧 Configuring pnpm for optimal performance...")
            
            # Get best registry
            best_registry = NetworkUtils.get_best_registry()
            
            # Configure pnpm
            configs = [
                ("registry", best_registry),
                ("store-dir", str(Config.DATA_DIR / "pnpm-store")),
                ("network-timeout", "300000"),  # 5 minutes
                ("fetch-retries", "3"),
                ("fetch-retry-mintimeout", "10000"),
                ("fetch-retry-maxtimeout", "60000"),
            ]
            
            env = os.environ.copy()
            node_dir = str(ToolsManager.get_node_path().absolute())
            pnpm_dir = str(ToolsManager.get_pnpm_path().absolute())
            env['PATH'] = f"{node_dir};{pnpm_dir};{env.get('PATH', '')}"
            
            for key, value in configs:
                try:
                    subprocess.run(
                        [str(pnpm_exe), "config", "set", key, value],
                        env=env,
                        capture_output=True,
                        timeout=10,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    logger.info(f"   ✅ Set {key}")
                except:
                    logger.warning(f"   ⚠️  Could not set {key}")
            
            logger.info("✅ pnpm configuration complete")
            
        except Exception as e:
            logger.warning(f"⚠️  Could not configure pnpm: {e}")
    
    @staticmethod
    def get_node_path():
        """Get the actual Node.js path, trying multiple locations"""
        possible_paths = [
            Config.NODE_DIR,  # Standard path
            Config.TOOLS_DIR / "node-v22.20.0-win-x64",  # Versioned folder
            Config.TOOLS_DIR / "node",  # Direct node folder
        ]
        
        for path in possible_paths:
            if (path / "node.exe").exists():
                return path
        
        return Config.NODE_DIR  # Fallback to default
    
    @staticmethod
    def get_mariadb_path():
        """Get the actual MariaDB path, trying multiple locations"""
        possible_paths = [
            Config.MARIADB_DIR,  # Standard path
            Config.TOOLS_DIR / "mariadb-12.0.2-winx64",  # Versioned folder
            Config.TOOLS_DIR / "mariadb",  # Direct mariadb folder
        ]
        
        for path in possible_paths:
            if (path / "bin" / "mysqld.exe").exists():
                return path
        
        return Config.MARIADB_DIR  # Fallback to default
    
    @staticmethod
    def get_pnpm_path():
        """Get the actual pnpm path, trying multiple locations"""
        # Try to find pnpm in Node.js global modules
        node_path = ToolsManager.get_node_path()
        possible_paths = [
            Config.PNPM_DIR,  # Standard path
            node_path / "node_modules" / "pnpm" / "bin",  # Global install
            node_path / "node_modules" / ".bin",  # npm global bin
        ]
        
        for path in possible_paths:
            if (path / "pnpm.exe").exists():
                return path
        
        return Config.PNPM_DIR  # Fallback to default
    
    @staticmethod
    def setup_nodejs() -> bool:
        """Setup portable Node.js"""
        node_path = ToolsManager.get_node_path()
        node_exe = node_path / "node.exe"
        
        if node_exe.exists():
            logger.info("✅ Node.js already installed")
            # Verify version
            try:
                result = subprocess.run(
                    [str(node_exe), "--version"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
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
    def setup_pnpm(max_retries: int = 3) -> bool:
        """Setup portable pnpm (standalone executable) with retry logic"""
        import time
        
        pnpm_path = ToolsManager.get_pnpm_path()
        pnpm_exe = pnpm_path / "pnpm.exe"
        
        if pnpm_exe.exists():
            logger.info("✅ pnpm already installed")
            return True
        
        logger.info("📦 Downloading pnpm standalone...")
        
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    logger.info(f"🔄 Retry attempt {attempt}/{max_retries}...")
                
                # Get latest pnpm release from GitHub with retry
                response = requests.get(
                    "https://api.github.com/repos/pnpm/pnpm/releases/latest",
                    timeout=15
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
                pnpm_path = ToolsManager.get_pnpm_path()
                pnpm_path.mkdir(parents=True, exist_ok=True)
                response = requests.get(asset_url, stream=True, timeout=60)
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
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                logger.info(f"   pnpm version: {result.stdout.strip()}")
                
                return True
                
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"⚠️  Network error (attempt {attempt}/{max_retries})")
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    
                    # Clean up partial download
                    if pnpm_exe.exists():
                        try:
                            pnpm_exe.unlink()
                        except:
                            pass
                    
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed to download pnpm after {max_retries} attempts")
                    logger.info("")
                    logger.info("💡 Manual alternative:")
                    logger.info("   1. Download: https://github.com/pnpm/pnpm/releases/latest")
                    logger.info("   2. Get: pnpm-win-x64.exe")
                    logger.info("   3. Rename to: pnpm.exe")
                    logger.info(f"   4. Put in: {ToolsManager.get_pnpm_path()}")
                    return False
                    
            except Exception as e:
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"⚠️  Error (attempt {attempt}/{max_retries}): {str(e)[:100]}")
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    
                    # Clean up partial download
                    if pnpm_exe.exists():
                        try:
                            pnpm_exe.unlink()
                        except:
                            pass
                    
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed to download pnpm: {e}")
                    logger.info("")
                    logger.info("💡 Manual alternative:")
                    logger.info("   1. Download: https://github.com/pnpm/pnpm/releases/latest")
                    logger.info("   2. Get: pnpm-win-x64.exe")
                    logger.info("   3. Rename to: pnpm.exe")
                    logger.info(f"   4. Put in: {ToolsManager.get_pnpm_path()}")
                    return False
        
        return False
    
    @staticmethod
    def setup_mariadb() -> bool:
        """Setup portable MariaDB"""
        mariadb_path = ToolsManager.get_mariadb_path()
        mysqld_exe = mariadb_path / "bin" / "mysqld.exe"
        if mysqld_exe.exists():
            logger.info("✅ MariaDB already installed")
            # Verify version
            try:
                mariadb_path = ToolsManager.get_mariadb_path()
                mysql_exe = mariadb_path / "bin" / "mysql.exe"
                result = subprocess.run(
                    [str(mysql_exe), "--version"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
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
        mariadb_path = ToolsManager.get_mariadb_path()
        mysql_install_db = mariadb_path / "bin" / "mysql_install_db.exe"
        mysqld_exe = mariadb_path / "bin" / "mysqld.exe"
        
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
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                # Alternative: Use mysqld --initialize
                subprocess.run(
                    [
                        str(mysqld_exe),
                        f"--datadir={data_dir}",
                        "--initialize-insecure"
                    ],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
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
        """Extract release ZIP while preserving node_modules"""
        try:
            logger.info(f"📂 Extracting {zip_path.name}...")
            
            # Preserve node_modules if exists (to avoid re-downloading dependencies)
            node_modules_backup = None
            if extract_to.exists():
                node_modules_path = extract_to / "node_modules"
                if node_modules_path.exists():
                    logger.info(f"💾 Backing up node_modules...")
                    node_modules_backup = extract_to.parent / f"{extract_to.name}_node_modules_temp"
                    try:
                        shutil.move(str(node_modules_path), str(node_modules_backup))
                        logger.info(f"✅ node_modules backed up")
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to backup node_modules: {e}")
                        node_modules_backup = None
                
                # Remove old version
                logger.info(f"🗑️  Removing old version...")
                try:
                    shutil.rmtree(extract_to)
                    logger.info(f"✅ Old version removed")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to remove old version: {e}")
                    logger.info("💡 Trying to extract anyway...")
            
            # Extract new version
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            # Restore node_modules
            if node_modules_backup and node_modules_backup.exists():
                logger.info(f"♻️  Restoring node_modules...")
                try:
                    restored_path = extract_to / "node_modules"
                    shutil.move(str(node_modules_backup), str(restored_path))
                    logger.info(f"✅ node_modules restored (update will be faster!)")
                    logger.info(f"💡 Running 'pnpm install' to sync any new dependencies...")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to restore node_modules: {e}")
                    # Cleanup backup
                    try:
                        shutil.rmtree(node_modules_backup)
                    except:
                        pass
            
            logger.info(f"✅ Extracted to {extract_to}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            # Cleanup backup if exists
            if node_modules_backup and node_modules_backup.exists():
                try:
                    logger.info(f"🧹 Cleaning up backup...")
                    shutil.rmtree(node_modules_backup)
                except:
                    pass
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
    installation_in_progress: bool = False  # Flag to prevent auto-check during installation
    
    @staticmethod
    def kill_process_on_port(port: int) -> bool:
        """Kill any process using the specified port (Windows only)"""
        try:
            import psutil
            
            # Get current process info to avoid killing ourselves
            current_pid = os.getpid()
            current_process_name = psutil.Process(current_pid).name().lower()
            
            killed = False
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    # Check if process has any connections on the target port
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            proc_pid = proc.info['pid']
                            proc_name = proc.info['name']
                            
                            # Skip if it's our own process (installation server, gui server, etc)
                            if proc_pid == current_pid:
                                logger.info(f"ℹ️  Port {port} is used by current process, skipping kill")
                                return True
                            
                            # Skip if it's another instance of our agent
                            if '4pawsagent' in proc_name.lower() or 'python' in proc_name.lower():
                                # Could be our GUI server or installation server
                                logger.info(f"ℹ️  Port {port} is used by {proc_name} (likely our own server), skipping kill")
                                return True
                            
                            logger.info(f"🔪 Killing {proc_name} (PID {proc_pid}) on port {port}")
                            
                            # Use taskkill for force kill on Windows
                            if sys.platform == 'win32':
                                subprocess.run(
                                    ['taskkill', '/F', '/PID', str(proc_pid)],
                                    capture_output=True,
                                    timeout=5,
                                    creationflags=subprocess.CREATE_NO_WINDOW
                                )
                            else:
                                proc.kill()
                            
                            killed = True
                            logger.info(f"✅ Killed process on port {port}")
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutError):
                    continue
            
            if not killed:
                logger.info(f"ℹ️  No process found on port {port}")
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Could not check/kill port {port}: {e}")
            return False
    
    @classmethod
    def start_mariadb(cls) -> bool:
        """Start MariaDB server"""
        # Kill any existing process on MariaDB port first
        logger.info(f"🔍 Checking port {Config.MARIADB_PORT}...")
        cls.kill_process_on_port(Config.MARIADB_PORT)
        
        if "mariadb" in cls.processes:
            # Check if process is actually still running
            try:
                proc = cls.processes["mariadb"]
                if proc.poll() is None:  # Process is still running
                    logger.info("✅ MariaDB already running")
                    return True
                else:
                    # Process died, remove it
                    logger.warning("⚠️  MariaDB process died, restarting...")
                    del cls.processes["mariadb"]
            except:
                del cls.processes["mariadb"]
        
        mariadb_path = ToolsManager.get_mariadb_path()
        mysqld_exe = mariadb_path / "bin" / "mysqld.exe"
        
        if not mysqld_exe.exists():
            logger.error("❌ MariaDB not found!")
            logger.error(f"   Expected: {mysqld_exe}")
            return False
        
        data_dir = Config.DATA_DIR / "mariadb"
        
        # Ensure data directory exists before starting
        if not data_dir.exists():
            logger.error(f"❌ MariaDB data directory not initialized!")
            logger.error(f"   Expected: {data_dir}")
            logger.error(f"🔧 Please run: python agent.py setup")
            logger.error(f"   This will initialize MariaDB data directory")
            return False
        
        try:
            logger.info("🚀 Starting MariaDB...")
            
            # Create log file path for MariaDB
            log_file = Config.LOGS_DIR / "mariadb.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Start with output redirect to log file (prevents buffer issues)
            # Use CREATE_NEW_PROCESS_GROUP so we can kill the entire process tree later
            creation_flags = subprocess.CREATE_NO_WINDOW
            if sys.platform == 'win32':
                creation_flags |= subprocess.CREATE_NEW_PROCESS_GROUP
            
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    [
                        str(mysqld_exe),
                        f"--datadir={data_dir}",
                        f"--port={Config.MARIADB_PORT}",
                        "--default-storage-engine=InnoDB",
                        "--skip-grant-tables",  # Allow passwordless access for initial setup
                        "--console"
                    ],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    creationflags=creation_flags
                )
            
            # Wait and verify MariaDB is actually ready
            import time
            logger.info("⏳ Waiting for MariaDB to be ready...")
            
            # Wait up to 10 seconds for MariaDB to start accepting connections
            max_wait = 10
            connected = False
            for i in range(max_wait):
                time.sleep(1)
                
                # Check if process crashed
                if process.poll() is not None:
                    logger.error(f"❌ MariaDB failed to start (exit code: {process.returncode})")
                    logger.error(f"📝 Log file: {log_file}")
                    break
                
                # Try to connect to MariaDB
                try:
                    mysql_exe = mariadb_path / "bin" / "mysql.exe"
                    test_result = subprocess.run(
                        [str(mysql_exe), "-u", Config.MARIADB_USER, "-P", str(Config.MARIADB_PORT), "-e", "SELECT 1;"],
                        capture_output=True,
                        timeout=2,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    if test_result.returncode == 0:
                        connected = True
                        logger.info(f"✅ MariaDB is ready (took {i+1}s)")
                        break
                except:
                    pass  # Try again
            
            if not connected and process.poll() is None:
                logger.warning(f"⚠️  MariaDB started but connection test timed out")
                logger.warning(f"   Process is running, continuing anyway...")
            
            if process.poll() is not None:
                
                # Read and display last lines from log file for debugging
                try:
                    if log_file.exists() and log_file.stat().st_size > 0:
                        logger.error("📋 Last 20 lines from MariaDB log:")
                        logger.error("-" * 60)
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            # Show last 20 lines or all if less than 20
                            for line in lines[-20:]:
                                logger.error(f"   {line.rstrip()}")
                        logger.error("-" * 60)
                    else:
                        logger.error("⚠️  Log file is empty or doesn't exist")
                except Exception as e:
                    logger.error(f"⚠️  Could not read log file: {e}")
                
                # Common causes and solutions
                logger.error("💡 Common causes:")
                logger.error("   1. Port 3307 already in use")
                logger.error("   2. Data directory corruption")
                logger.error("   3. Insufficient permissions")
                logger.error("   4. Missing required DLL files")
                logger.error("")
                logger.error("🔧 Suggested actions:")
                logger.error("   1. Check if another MariaDB/MySQL is running on port 3307")
                logger.error("   2. Try: taskkill /F /IM mysqld.exe")
                logger.error(f"   3. Delete data directory: {data_dir}")
                logger.error("   4. Run: python agent.py setup (to reinitialize)")
                
                return False
            
            cls.processes["mariadb"] = process
            logger.info(f"✅ MariaDB started (PID: {process.pid})")
            logger.info(f"🌐 MariaDB Port: {Config.MARIADB_PORT}")
            logger.info(f"📝 MariaDB log: {log_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start MariaDB: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    @classmethod
    def start_backend(cls) -> bool:
        """Start backend server (simple mode - no install)"""
        # Kill any existing process on backend port first
        logger.info(f"🔍 Checking port {Config.BACKEND_PORT}...")
        cls.kill_process_on_port(Config.BACKEND_PORT)
        
        if "backend" in cls.processes:
            # Check if process is actually still running
            try:
                proc = cls.processes["backend"]
                if proc.poll() is None:  # Process is still running
                    logger.info("✅ Backend already running")
                    return True
                else:
                    # Process died, remove it
                    logger.warning("⚠️  Backend process died, restarting...")
                    del cls.processes["backend"]
            except:
                del cls.processes["backend"]
        
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
            node_dir = str(ToolsManager.get_node_path().absolute())
            pnpm_dir = str(ToolsManager.get_pnpm_path().absolute())
            
            # Add portable tools to PATH (only for this subprocess)
            if 'PATH' in env:
                env['PATH'] = f"{node_dir};{pnpm_dir};{env['PATH']}"
            else:
                env['PATH'] = f"{node_dir};{pnpm_dir}"
            
            # Create log file path
            log_file = Config.LOGS_DIR / "backend.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Use CREATE_NEW_PROCESS_GROUP so we can kill the entire process tree later
            creation_flags = subprocess.CREATE_NO_WINDOW
            if sys.platform == 'win32':
                creation_flags |= subprocess.CREATE_NEW_PROCESS_GROUP
            
            # Get full path to node.exe
            node_exe = ToolsManager.get_node_path() / "node.exe"
            if not node_exe.exists():
                logger.error(f"❌ Node.js not found at: {node_exe}")
                logger.error("💡 Run: python agent.py setup")
                return False
            
            # Start with output redirect to log file
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    [str(node_exe), str(main_js)],
                    cwd=str(Config.BACKEND_DIR),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    env=env,
                    creationflags=creation_flags
                )
            
            # Wait a bit and check if process is still running
            import time
            time.sleep(2)
            
            if process.poll() is not None:
                logger.error(f"❌ Backend failed to start (exit code: {process.returncode})")
                logger.error(f"📝 Check log: {log_file}")
                return False
            
            cls.processes["backend"] = process
            logger.info(f"✅ Backend started (PID: {process.pid})")
            logger.info(f"🌐 Backend API: http://localhost:{Config.BACKEND_PORT}")
            logger.info(f"📝 Backend log: {log_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start backend: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    @classmethod
    def start_frontend(cls) -> bool:
        """Start frontend server (simple mode - no install)"""
        # Kill any existing process on frontend port first
        logger.info(f"🔍 Checking port {Config.FRONTEND_PORT}...")
        cls.kill_process_on_port(Config.FRONTEND_PORT)
        
        if "frontend" in cls.processes:
            # Check if process is actually still running
            try:
                proc = cls.processes["frontend"]
                if proc.poll() is None:  # Process is still running
                    logger.info("✅ Frontend already running")
                    return True
                else:
                    # Process died, remove it
                    logger.warning("⚠️  Frontend process died, restarting...")
                    del cls.processes["frontend"]
            except:
                del cls.processes["frontend"]
        
        # Check if frontend build exists
        if not Config.FRONTEND_DIR.exists():
            logger.error("❌ Frontend not found! Run: python agent.py install frontend")
            return False
        
        # Check if node_modules exists
        if not (Config.FRONTEND_DIR / "node_modules").exists():
            logger.error("❌ Dependencies not installed! Run: python agent.py setup-apps")
            return False
        
        # Get full path to pnpm executable
        pnpm_path = ToolsManager.get_pnpm_path()
        pnpm_exe = pnpm_path / "pnpm.exe"
        if not pnpm_exe.exists():
            logger.error("❌ pnpm not found! Run: python agent.py setup")
            return False
        
        try:
            logger.info("🚀 Starting frontend...")
            
            # Prepare environment with Node.js and pnpm in PATH
            env = os.environ.copy()
            node_dir = str(ToolsManager.get_node_path().absolute())
            pnpm_dir = str(ToolsManager.get_pnpm_path().absolute())
            
            # Add portable tools to PATH (only for this subprocess)
            if 'PATH' in env:
                env['PATH'] = f"{node_dir};{pnpm_dir};{env['PATH']}"
            else:
                env['PATH'] = f"{node_dir};{pnpm_dir}"
            
            # Create log file path
            log_file = Config.LOGS_DIR / "frontend.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Use CREATE_NEW_PROCESS_GROUP so we can kill the entire process tree later
            creation_flags = subprocess.CREATE_NO_WINDOW
            if sys.platform == 'win32':
                creation_flags |= subprocess.CREATE_NEW_PROCESS_GROUP
            
            # Start with output redirect to log file
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    [str(pnpm_exe), "start"],
                    cwd=str(Config.FRONTEND_DIR),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    env=env,
                    shell=False,
                    creationflags=creation_flags
                )
            
            # Wait a bit and check if process is still running
            import time
            time.sleep(2)
            
            if process.poll() is not None:
                logger.error(f"❌ Frontend failed to start (exit code: {process.returncode})")
                logger.error(f"📝 Check log: {log_file}")
                return False
            
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
        """Stop all running processes (including child processes)"""
        import time
        
        # Check if there are any processes to stop
        if not cls.processes:
            logger.info("ℹ️  No services running")
            return
        
        # Create a copy of items to avoid dictionary changed size during iteration
        processes_to_stop = list(cls.processes.items())
        
        # Count actually running processes
        running_count = 0
        for name, process in processes_to_stop:
            if process.poll() is None:
                running_count += 1
        
        if running_count == 0:
            logger.info("ℹ️  All services already stopped")
            cls.processes.clear()
            return
        
        logger.info(f"⏹️  Stopping {running_count} running service(s)...")
        
        for name, process in processes_to_stop:
            try:
                # Check if process is still running
                if process.poll() is not None:
                    logger.info(f"ℹ️  {name} already stopped")
                    continue
                
                logger.info(f"⏹️  Stopping {name}...")
                
                # On Windows, kill the entire process tree (parent + all children)
                # Because we started with CREATE_NEW_PROCESS_GROUP, taskkill /T will work properly
                if sys.platform == 'win32':
                    try:
                        # Use taskkill with /T flag to terminate process tree
                        result = subprocess.run(
                            ['taskkill', '/F', '/T', '/PID', str(process.pid)],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        
                        if result.returncode == 0:
                            logger.info(f"✅ {name} stopped (including all child processes)")
                        else:
                            # taskkill failed, try process.kill() as fallback
                            logger.warning(f"⚠️  taskkill returned {result.returncode}, using fallback...")
                            process.kill()
                            process.wait(timeout=5)
                            logger.info(f"✅ {name} stopped (fallback method)")
                            
                    except subprocess.TimeoutExpired:
                        logger.warning(f"⚠️  taskkill timeout for {name}, force killing...")
                        process.kill()
                        process.wait(timeout=5)
                        logger.info(f"✅ {name} force killed")
                    except Exception as e:
                        logger.warning(f"⚠️  Error stopping {name}: {e}, trying fallback...")
                        try:
                            process.kill()
                            process.wait(timeout=5)
                            logger.info(f"✅ {name} stopped (fallback)")
                        except:
                            pass
                else:
                    # On Linux/Mac, try graceful termination first
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                        logger.info(f"✅ {name} stopped gracefully")
                    except subprocess.TimeoutExpired:
                        # Process didn't terminate gracefully, force kill
                        logger.warning(f"⚠️  {name} didn't stop gracefully, forcing...")
                        process.kill()
                        process.wait(timeout=5)
                        logger.info(f"✅ {name} force stopped")
                    
            except Exception as e:
                logger.error(f"❌ Failed to stop {name}: {e}")
                # Final fallback attempt
                try:
                    if sys.platform == 'win32':
                        subprocess.run(
                            ['taskkill', '/F', '/T', '/PID', str(process.pid)],
                            capture_output=True,
                            timeout=5,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    else:
                        process.kill()
                except:
                    pass
        
        # Clear all processes
        cls.processes.clear()
        logger.info("✅ All services have been stopped")


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
        
        # Set flag to prevent auto-check updates during installation
        ProcessManager.installation_in_progress = True
        
        log("🚀 Starting first-time installation...")
        log("")
        log("🔍 Pre-installation checks...")
        
        # Check disk space
        if not DiskUtils.check_disk_space(Config.BASE_DIR, required_gb=5.0):
            log("❌ Insufficient disk space!", 'error')
            return False
        
        # Check network connectivity
        log("🌐 Testing network connectivity...")
        if not NetworkUtils.test_connectivity():
            log("❌ No internet connection!", 'error')
            log("💡 Please check your internet connection and try again", 'warning')
            return False
        log("✅ Network connectivity OK")
        log("")
        
        try:
            # Step 0: Setup tools first (Node.js, pnpm, MariaDB) (0-20%)
            if progress_callback:
                progress_callback(0, 'tools', 'active',
                                'Setting Up Tools',
                                'Installing Node.js, pnpm, and MariaDB...')
            
            log("🔧 Setting up required tools...")
            if not self.setup_tools():
                log("❌ Failed to setup tools", 'error')
                log("💡 Tools include: Node.js, pnpm, MariaDB", 'warning')
                return False
            
            if progress_callback:
                progress_callback(20, 'tools', 'completed')
            
            # Step 1: Download applications (20-40%)
            if progress_callback:
                progress_callback(20, 'download', 'active', 
                                'Downloading Applications', 
                                'Fetching latest releases from GitHub...')
            
            log("📥 Downloading frontend...")
            if not self.download_and_install("frontend"):
                log("❌ Failed to download frontend", 'error')
                return False
            
            if progress_callback:
                progress_callback(30, 'download', 'active')
            
            log("📥 Downloading backend...")
            if not self.download_and_install("backend"):
                log("❌ Failed to download backend", 'error')
                return False
            
            if progress_callback:
                progress_callback(40, 'download', 'completed')
            
            # Step 2: Install dependencies (40-75%)
            if progress_callback:
                progress_callback(40, 'install', 'active',
                                'Installing Dependencies',
                                'Setting up backend dependencies...')
            
            log("📦 Setting up applications...")
            
            # Setup with granular progress updates
            if not self._setup_apps_with_progress("all", progress_callback, log):
                log("❌ Failed to setup applications", 'error')
                return False
            
            if progress_callback:
                progress_callback(75, 'install', 'completed')
            
            # Step 3: Database is already done in setup_apps (75-80%)
            if progress_callback:
                progress_callback(80, 'database', 'completed',
                                'Database Ready',
                                'MariaDB configured and migrations complete')
            
            # Step 4: Start services (80-95%)
            if progress_callback:
                progress_callback(80, 'start', 'active',
                                'Starting Services',
                                'Launching MariaDB, backend, and frontend...')
            
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
        finally:
            # Clear flag after installation completes (success or fail)
            ProcessManager.installation_in_progress = False
    
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
        
        # Configure pnpm after setup
        if success:
            ToolsManager.setup_pnpm_config()
        
        success &= ToolsManager.setup_mariadb()
        success &= ToolsManager.init_mariadb()
        
        return success
    
    def setup_apps(self, component: str = "all") -> bool:
        """Setup apps: install dependencies and run migrations"""
        return self._setup_apps_with_progress(component, None, logger.info)
    
    def _setup_apps_with_progress(self, component: str, progress_callback, log):
        """Setup apps with granular progress updates"""
        log("🔧 Setting up applications...")
        
        # Enable verbose mode for web interface (always show detailed logs during first install)
        self._web_log_callback = log  # Store for use in subprocess calls
        
        # Ensure .env files exist
        if component in ["backend", "all"] and Config.BACKEND_DIR.exists():
            AppManager.setup_env(Config.BACKEND_DIR, "backend")
        if component in ["frontend", "all"] and Config.FRONTEND_DIR.exists():
            AppManager.setup_env(Config.FRONTEND_DIR, "frontend")
        
        # Start MariaDB if setting up backend (needed for migrations)
        mariadb_started = False
        if component in ["backend", "all"]:
            log("🚀 Starting MariaDB for database setup...")
            if ProcessManager.start_mariadb():
                mariadb_started = True
                log("✅ MariaDB started")
                # Wait for MariaDB to be ready
                import time
                time.sleep(3)
            else:
                log("❌ Failed to start MariaDB!", 'error')
                return False
        
        success = True
        
        if component in ["backend", "all"]:
            if progress_callback:
                progress_callback(42, 'install', 'active', 'Backend Setup', 'Installing backend dependencies...')
            success &= self._setup_backend_with_heartbeat(log_callback=log)
            if progress_callback:
                progress_callback(55, 'install', 'active', 'Backend Setup', 'Backend dependencies installed')
        
        if component in ["frontend", "all"]:
            if progress_callback:
                progress_callback(60, 'install', 'active', 'Frontend Setup', 'Installing frontend dependencies...')
            success &= self._setup_frontend_with_heartbeat(log_callback=log)
            if progress_callback:
                progress_callback(75, 'install', 'active', 'Frontend Setup', 'Frontend dependencies installed')
        
        # Stop MariaDB if we started it
        if mariadb_started:
            log("⏹️  Stopping MariaDB...")
            if "mariadb" in ProcessManager.processes:
                try:
                    ProcessManager.processes["mariadb"].terminate()
                    ProcessManager.processes["mariadb"].wait(timeout=10)
                    del ProcessManager.processes["mariadb"]
                    log("✅ MariaDB stopped")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to stop MariaDB: {e}")
        
        if success:
            log("✅ Application setup complete!")
        else:
            log("❌ Application setup failed!", 'error')
        
        return success
    
    def _run_with_heartbeat(self, cmd, cwd, env, operation_name: str, timeout: int = 300, verbose: bool = False, log_callback=None) -> subprocess.CompletedProcess:
        """Run a subprocess with heartbeat logging every 15 seconds and optional real-time output"""
        import threading
        import time
        
        if verbose:
            # Run with real-time output capture, pass log_callback
            return self._run_with_realtime_output(cmd, cwd, env, operation_name, timeout, log_callback)
        
        # Flag to stop heartbeat
        stop_heartbeat = threading.Event()
        elapsed_time = [0]  # Use list to allow modification in nested function
        
        def heartbeat():
            """Log a heartbeat message every 15 seconds"""
            while not stop_heartbeat.is_set():
                stop_heartbeat.wait(15)  # Wait 15 seconds or until stopped
                if not stop_heartbeat.is_set():
                    elapsed_time[0] += 15
                    logger.info(f"   ⏳ Still {operation_name}... ({elapsed_time[0]}s elapsed)")
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
        heartbeat_thread.start()
        
        try:
            # Run the subprocess
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                shell=False,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result
        except subprocess.TimeoutExpired as e:
            logger.error(f"⏱️  Operation timed out after {timeout}s")
            logger.error(f"💡 This usually means:")
            logger.error(f"   1. Very slow internet connection")
            logger.error(f"   2. npm registry server is slow")
            logger.error(f"   3. Antivirus is scanning files")
            logger.error(f"   4. Disk I/O is very slow")
            logger.error(f"")
            logger.error(f"🔧 Suggested fixes:")
            logger.error(f"   1. Try again with better internet connection")
            logger.error(f"   2. Temporarily disable antivirus during installation")
            logger.error(f"   3. Use: pnpm config set registry https://registry.npmmirror.com/")
            raise
        finally:
            # Stop heartbeat
            stop_heartbeat.set()
            heartbeat_thread.join(timeout=1)
    
    def _run_with_realtime_output(self, cmd, cwd, env, operation_name: str, timeout: int = 300, log_callback=None) -> subprocess.CompletedProcess:
        """Run subprocess with real-time output logging (for verbose mode)"""
        import threading
        import time
        import queue
        
        def log_msg(msg, level='info'):
            """Helper to log both to logger and callback"""
            if level == 'info':
                logger.info(msg)
            elif level == 'error':
                logger.error(msg)
            elif level == 'warning':
                logger.warning(msg)
            
            # Also send to callback if provided
            if log_callback:
                log_callback(msg, level)
        
        log_msg(f"📋 Running: {' '.join(str(c) for c in cmd)}")
        log_msg(f"📂 Working dir: {cwd}")
        log_msg(f"⏳ Starting {operation_name} (verbose mode)...")
        
        # Create process
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
            bufsize=1,
            universal_newlines=True
        )
        
        # Queue for output lines
        output_queue = queue.Queue()
        output_lines = []
        
        def read_output():
            """Read output lines and put in queue"""
            for line in process.stdout:
                output_queue.put(line)
                output_lines.append(line)
            process.stdout.close()
        
        # Start output reader thread
        reader_thread = threading.Thread(target=read_output, daemon=True)
        reader_thread.start()
        
        # Monitor output and timeout
        start_time = time.time()
        last_log_time = start_time
        
        try:
            while True:
                # Check if process finished
                if process.poll() is not None:
                    break
                
                # Check timeout
                if time.time() - start_time > timeout:
                    process.kill()
                    raise subprocess.TimeoutExpired(cmd, timeout)
                
                # Log output lines
                try:
                    line = output_queue.get(timeout=1)
                    # Only log important lines to avoid spam
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in [
                        'progress', 'downloading', 'error', 'warn', 'warning',
                        'fetching', 'reused', 'added', 'packages',
                        'resolving', 'building', 'lockfile', 'deprecated'
                    ]):
                        # Clean up the line for better display
                        clean_line = line.strip()
                        if clean_line:
                            # Add appropriate emoji based on content
                            if 'error' in line_lower:
                                log_msg(f"   ❌ {clean_line}", 'error')
                            elif 'warn' in line_lower:
                                log_msg(f"   ⚠️  {clean_line}", 'warning')
                            elif 'progress' in line_lower or 'resolving' in line_lower:
                                log_msg(f"   🔄 {clean_line}", 'info')
                            elif 'downloading' in line_lower or 'fetching' in line_lower:
                                log_msg(f"   📥 {clean_line}", 'info')
                            elif 'added' in line_lower or 'reused' in line_lower:
                                log_msg(f"   ✅ {clean_line}", 'success')
                            else:
                                log_msg(f"   📦 {clean_line}", 'info')
                    last_log_time = time.time()
                except queue.Empty:
                    # No output for 1 second, check if we should log heartbeat
                    if time.time() - last_log_time > 15:
                        elapsed = int(time.time() - start_time)
                        log_msg(f"   ⏳ Still {operation_name}... ({elapsed}s elapsed)", 'info')
                        last_log_time = time.time()
            
            # Wait for reader thread
            reader_thread.join(timeout=1)
            
            # Create result object
            returncode = process.returncode
            stdout = ''.join(output_lines)
            
            # Create CompletedProcess-like object
            class Result:
                def __init__(self, returncode, stdout):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = ""
            
            return Result(returncode, stdout)
            
        except subprocess.TimeoutExpired:
            logger.error(f"⏱️  Operation timed out after {timeout}s")
            logger.error(f"💡 This usually means:")
            logger.error(f"   1. Very slow internet connection")
            logger.error(f"   2. npm registry server is slow")
            logger.error(f"   3. Antivirus is scanning files")
            logger.error(f"   4. Disk I/O is very slow")
            logger.error(f"")
            logger.error(f"🔧 Suggested fixes:")
            logger.error(f"   1. Try again with better internet connection")
            logger.error(f"   2. Temporarily disable antivirus during installation")
            logger.error(f"   3. Use: pnpm config set registry https://registry.npmmirror.com/")
            raise
    
    def _setup_backend_with_heartbeat(self, log_callback=None) -> bool:
        """Setup backend with heartbeat logs during long operations"""
        return self._setup_backend(log_callback=log_callback)
    
    def _setup_frontend_with_heartbeat(self, log_callback=None) -> bool:
        """Setup frontend with heartbeat logs during long operations"""
        return self._setup_frontend(log_callback=log_callback)
    
    def _setup_backend(self, log_callback=None) -> bool:
        """Setup backend: pnpm install + prisma generate + migrate"""
        if not Config.BACKEND_DIR.exists():
            logger.error("❌ Backend not installed! Run: python agent.py install backend")
            return False
        
        logger.info("🔧 Setting up backend...")
        
        # Use web log callback if provided (for first-time install web interface)
        use_log_callback = log_callback if log_callback else None
        
        # Get full path to pnpm executable
        pnpm_path = ToolsManager.get_pnpm_path()
        pnpm_exe = pnpm_path / "pnpm.exe"
        if not pnpm_exe.exists():
            logger.error("❌ pnpm not found! Run: python agent.py setup")
            return False
        
        # Prepare environment with Node.js in PATH
        env = os.environ.copy()
        node_dir = str(ToolsManager.get_node_path().absolute())
        pnpm_dir = str(ToolsManager.get_pnpm_path().absolute())
        env['PATH'] = f"{node_dir};{pnpm_dir};{env.get('PATH', '')}"
        
        try:
            # 1. Install dependencies with retry
            # Check if verbose mode is enabled (CLI mode) or web callback exists (web mode)
            verbose_mode = os.getenv('PNPM_VERBOSE', '0') == '1' or os.getenv('VERBOSE', '0') == '1'
            # Always use verbose for web interface during first install to show progress
            force_verbose = use_log_callback is not None
            
            logger.info("📦 Installing dependencies...")
            if verbose_mode or force_verbose:
                msg = "📋 Verbose mode enabled - showing detailed pnpm output..."
                logger.info(msg)
                if use_log_callback:
                    use_log_callback(msg, 'info')
            logger.info("⏳ This may take 1-5 minutes on normal connections, up to 30 minutes on very slow connections...")
            
            max_retries = 2
            for attempt in range(1, max_retries + 1):
                try:
                    if attempt > 1:
                        logger.info(f"🔄 Retry attempt {attempt}/{max_retries}...")
                        # Cleanup partial node_modules on retry
                        node_modules = Config.BACKEND_DIR / "node_modules"
                        if node_modules.exists():
                            logger.info("🧹 Cleaning up partial installation...")
                            try:
                                shutil.rmtree(node_modules)
                                logger.info("✅ Cleanup complete")
                            except Exception as e:
                                logger.warning(f"⚠️  Could not cleanup: {e}")
                    
                    result = self._run_with_heartbeat(
                        [str(pnpm_exe), "install", "--production", "--ignore-scripts"],
                        str(Config.BACKEND_DIR),
                        env,
                        "installing backend dependencies",
                        timeout=1800,  # Increased to 1800s (30 minutes) for very slow connections
                        verbose=verbose_mode or force_verbose,  # Enable verbose if CLI mode or web interface
                        log_callback=use_log_callback  # Pass callback for web interface
                    )
                    if result.returncode != 0:
                        if attempt < max_retries:
                            logger.warning(f"⚠️  Installation failed (attempt {attempt}/{max_retries})")
                            logger.info("⏳ Waiting 5 seconds before retry...")
                            import time
                            time.sleep(5)
                            continue
                        else:
                            logger.error(f"❌ Failed to install dependencies after {max_retries} attempts:")
                            logger.error(result.stderr)
                            return False
                    
                    logger.info("✅ Dependencies installed")
                    break
                    
                except subprocess.TimeoutExpired:
                    if attempt < max_retries:
                        logger.warning(f"⏱️  Installation timeout (attempt {attempt}/{max_retries})")
                        logger.info("⏳ Waiting 10 seconds before retry...")
                        import time
                        time.sleep(10)
                        continue
                    else:
                        logger.error(f"❌ Installation timed out after {max_retries} attempts")
                        raise
            
            # 2. Generate Prisma client
            prisma_client = Config.BACKEND_DIR / "node_modules" / ".prisma" / "client"
            if prisma_client.exists():
                logger.info("✅ Prisma client already exists, skipping generate...")
            else:
                logger.info("🔧 Generating Prisma client...")
                logger.info("⏳ This may take 1-5 minutes on normal connections, up to 30 minutes on very slow connections...")
                result = self._run_with_heartbeat(
                    [str(pnpm_exe), "prisma", "generate"],
                    str(Config.BACKEND_DIR),
                    env,
                    "generating Prisma client",
                    timeout=1800  # Increased to 1800s (30 minutes) for very slow connections
                )
                if result.returncode != 0:
                    logger.error(f"❌ Failed to generate Prisma client:")
                    logger.error(result.stderr)
                    logger.warning("⚠️  Trying to continue anyway...")
                else:
                    logger.info("✅ Prisma client generated")
            
            # 3. Create database if not exists
            logger.info("🗄️  Creating database if not exists...")
            mariadb_path = ToolsManager.get_mariadb_path()
            mysql_exe = mariadb_path / "bin" / "mysql.exe"
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
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
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
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode != 0:
                logger.error(f"❌ Migration failed:")
                logger.error(result.stderr)
                logger.info("💡 Make sure MariaDB is running and DATABASE_URL is correct")
                return False
            else:
                logger.info("✅ Migrations completed")
            
            # 5. Check if database needs seeding (first-time install only)
            logger.info("🔍 Checking if database needs seeding...")
            needs_seeding = False
            
            # Check if User table is empty (indicates first-time setup)
            try:
                mariadb_path = ToolsManager.get_mariadb_path()
                mysql_exe = mariadb_path / "bin" / "mysql.exe"
                check_result = subprocess.run(
                    [
                        str(mysql_exe),
                        "-u", Config.MARIADB_USER,
                        "-P", str(Config.MARIADB_PORT),
                        Config.MARIADB_DB,
                        "-e", "SELECT COUNT(*) FROM User;"
                    ],
                    capture_output=True,
                    text=True,
                    shell=False,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if check_result.returncode == 0:
                    # Parse output to get count
                    output_lines = check_result.stdout.strip().split('\n')
                    if len(output_lines) > 1:
                        count = int(output_lines[1].strip())
                        if count == 0:
                            needs_seeding = True
                            logger.info("✅ Database is empty - will seed initial data")
                        else:
                            logger.info(f"ℹ️  Database already has {count} user(s) - skipping seeding")
                else:
                    # If query fails, assume table doesn't exist yet (first time)
                    needs_seeding = True
                    logger.info("ℹ️  User table not found - will seed initial data")
            except Exception as e:
                logger.warning(f"⚠️  Could not check database state: {e}")
                logger.info("ℹ️  Will attempt seeding anyway...")
                needs_seeding = True
            
            # Run seed for first-time installation (users and services only)
            if needs_seeding:
                logger.info("🌱 Seeding initial data (users & services)...")
                seed_file = Config.BACKEND_DIR / "prisma" / "seed-first-install.ts"
                if seed_file.exists():
                    result = subprocess.run(
                        [str(pnpm_exe), "exec", "ts-node", str(seed_file)],
                        cwd=str(Config.BACKEND_DIR),
                        env=env,
                        capture_output=True,
                        text=True,
                        shell=False,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    if result.returncode != 0:
                        logger.warning(f"⚠️  Seeding failed (this is non-critical):")
                        logger.warning(result.stderr)
                        logger.info("💡 You can manually run seed later with: pnpm prisma:seed")
                    else:
                        logger.info("✅ Initial data seeded")
                        # Show credentials from seed output
                        if result.stdout:
                            for line in result.stdout.split('\n'):
                                if 'Master:' in line or 'Admin:' in line or 'Default credentials:' in line:
                                    logger.info(f"   {line.strip()}")
                else:
                    logger.warning("⚠️  Seed file not found, skipping seeding")
            else:
                logger.info("✅ Database already initialized - skipping seeding")
            
            logger.info("✅ Backend setup complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backend setup failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _setup_frontend(self, log_callback=None) -> bool:
        """Setup frontend: pnpm install"""
        if not Config.FRONTEND_DIR.exists():
            logger.error("❌ Frontend not installed! Run: python agent.py install frontend")
            return False
        
        logger.info("🔧 Setting up frontend...")
        
        # Use web log callback if provided (for first-time install web interface)
        use_log_callback = log_callback if log_callback else None
        
        # Get full path to pnpm executable
        pnpm_path = ToolsManager.get_pnpm_path()
        pnpm_exe = pnpm_path / "pnpm.exe"
        if not pnpm_exe.exists():
            logger.error("❌ pnpm not found! Run: python agent.py setup")
            return False
        
        # Prepare environment with Node.js in PATH
        env = os.environ.copy()
        node_dir = str(ToolsManager.get_node_path().absolute())
        pnpm_dir = str(ToolsManager.get_pnpm_path().absolute())
        env['PATH'] = f"{node_dir};{pnpm_dir};{env.get('PATH', '')}"
        
        try:
            # Install dependencies with retry
            # Check if verbose mode is enabled (CLI mode) or web callback exists (web mode)
            verbose_mode = os.getenv('PNPM_VERBOSE', '0') == '1' or os.getenv('VERBOSE', '0') == '1'
            # Always use verbose for web interface during first install to show progress
            force_verbose = use_log_callback is not None
            
            logger.info("📦 Installing dependencies...")
            if verbose_mode or force_verbose:
                msg = "📋 Verbose mode enabled - showing detailed pnpm output..."
                logger.info(msg)
                if use_log_callback:
                    use_log_callback(msg, 'info')
            logger.info("⏳ This may take 2-5 minutes on normal connections, up to 30 minutes on very slow connections...")
            
            max_retries = 2
            for attempt in range(1, max_retries + 1):
                try:
                    if attempt > 1:
                        logger.info(f"🔄 Retry attempt {attempt}/{max_retries}...")
                        # Cleanup partial node_modules on retry
                        node_modules = Config.FRONTEND_DIR / "node_modules"
                        if node_modules.exists():
                            logger.info("🧹 Cleaning up partial installation...")
                            try:
                                shutil.rmtree(node_modules)
                                logger.info("✅ Cleanup complete")
                            except Exception as e:
                                logger.warning(f"⚠️  Could not cleanup: {e}")
                    
                    result = self._run_with_heartbeat(
                        [str(pnpm_exe), "install", "--production", "--ignore-scripts"],
                        str(Config.FRONTEND_DIR),
                        env,
                        "installing frontend dependencies",
                        timeout=1800,  # Increased to 1800s (30 minutes) for very slow connections
                        verbose=verbose_mode or force_verbose,  # Enable verbose if CLI mode or web interface
                        log_callback=use_log_callback  # Pass callback for web interface
                    )
                    if result.returncode != 0:
                        if attempt < max_retries:
                            logger.warning(f"⚠️  Installation failed (attempt {attempt}/{max_retries})")
                            logger.info("⏳ Waiting 5 seconds before retry...")
                            import time
                            time.sleep(5)
                            continue
                        else:
                            logger.error(f"❌ Failed to install dependencies after {max_retries} attempts:")
                            logger.error(result.stderr)
                            return False
                    
                    logger.info("✅ Frontend dependencies installed")
                    break
                    
                except subprocess.TimeoutExpired:
                    if attempt < max_retries:
                        logger.warning(f"⏱️  Installation timeout (attempt {attempt}/{max_retries})")
                        logger.info("⏳ Waiting 10 seconds before retry...")
                        import time
                        time.sleep(10)
                        continue
                    else:
                        logger.error(f"❌ Installation timed out after {max_retries} attempts")
                        raise
            
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
        
        # Check license before starting services
        from core import LicenseManager
        
        if not LicenseManager.check_and_block():
            # License invalid - start license expired page
            logger.info("🔒 Starting license expired page instead of services...")
            LicenseManager.start_license_page(port=3100)
            return False
        
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
                
                # Start MariaDB for setup
                if not ProcessManager.start_mariadb():
                    logger.error("❌ Failed to start MariaDB for setup!")
                    return False
                
                if not self.setup_apps():
                    logger.error("❌ Setup failed! Cannot start services.")
                    ProcessManager.stop_all()
                    return False
                
                # Stop MariaDB after setup
                ProcessManager.stop_all()
                logger.info("✅ Setup complete, starting services...")
        
        # Start MariaDB first (already includes 2s wait + verification)
        if not ProcessManager.start_mariadb():
            logger.error("❌ Failed to start MariaDB!")
            return False
        
        # Small delay to ensure MariaDB is ready to accept connections
        import time
        time.sleep(3)
        
        # Start backend (already includes 2s wait + verification)
        if not ProcessManager.start_backend():
            logger.error("❌ Failed to start backend!")
            logger.error("💡 Check logs/backend.log for details")
            return False
        
        # Small delay to ensure backend is ready
        time.sleep(2)
        
        # Start frontend (already includes 2s wait + verification)
        if not ProcessManager.start_frontend():
            logger.error("❌ Failed to start frontend!")
            logger.error("💡 Check logs/frontend.log for details")
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
        pnpm_path = ToolsManager.get_pnpm_path()
        pnpm_exe = pnpm_path / "pnpm.exe"
        if not pnpm_exe.exists():
            logger.error("❌ pnpm not found! Run: python agent.py setup")
            return False
        
        # Prepare environment with Node.js in PATH
        env = os.environ.copy()
        node_dir = str(ToolsManager.get_node_path().absolute())
        pnpm_dir = str(ToolsManager.get_pnpm_path().absolute())
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
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW
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
    handler = get_log_manager_handler()
    handler.set_log_manager(log_manager)
    logger.info("📋 Agent logging connected to Web GUI")


def main():
    """Main entry point"""
    # Check if verbose mode is enabled
    verbose_enabled = os.getenv('PNPM_VERBOSE', '0') == '1' or os.getenv('VERBOSE', '0') == '1'
    
    print("""
╔════════════════════════════════════════╗
║   4Paws Deployment Agent v1.1         ║
║   Auto-update & manage releases       ║
╚════════════════════════════════════════╝
    """)
    
    if verbose_enabled:
        print("🔊 VERBOSE MODE ENABLED")
        print("   • Showing detailed pnpm output")
        print("   • Real-time installation progress")
        print("")
    
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
        print("  python agent.py service install          - Install as Windows service (requires admin)")
        print("  python agent.py service uninstall        - Uninstall Windows service (requires admin)")
        print("  python agent.py service status           - Check service status")
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
        
        elif command == "service":
            # Service management
            from service_manager import ServiceManager
            import ctypes
            
            if len(sys.argv) < 3:
                print("\nUsage:")
                print("  python agent.py service install    - Install as Windows service")
                print("  python agent.py service uninstall  - Uninstall Windows service")
                print("  python agent.py service start      - Start service")
                print("  python agent.py service stop       - Stop service")
                print("  python agent.py service status     - Check service status")
                return
            
            action = sys.argv[2].lower()
            
            # Check admin rights for install/uninstall/start/stop
            if action in ['install', 'uninstall', 'start', 'stop']:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
                if not is_admin:
                    print("\n❌ Administrator rights required!")
                    print("\nPlease run as administrator:")
                    print("  1. Right-click Command Prompt or PowerShell")
                    print("  2. Select 'Run as administrator'")
                    print("  3. Run the command again")
                    return
            
            if action == "install":
                if ServiceManager.install_service():
                    print("\n✅ Service installed successfully!")
                    print("\nThe service will:")
                    print("  ✅ Start automatically on Windows startup")
                    print("  ✅ Auto-start applications (Frontend, Backend, MariaDB)")
                    print("  ✅ Run in background")
                    print("  ✅ Restart automatically if it crashes")
                    print("\nTo start now:")
                    print("  python agent.py service start")
                else:
                    print("\n❌ Failed to install service")
            
            elif action == "uninstall":
                if ServiceManager.uninstall_service():
                    print("\n✅ Service uninstalled successfully!")
                    print("\nThe agent will no longer:")
                    print("  • Start automatically on boot")
                    print("  • Run as a background service")
                else:
                    print("\n❌ Failed to uninstall service")
            
            elif action == "start":
                ServiceManager.start_service()
            
            elif action == "stop":
                ServiceManager.stop_service()
            
            elif action == "status":
                status = ServiceManager.get_service_status()
                installed = ServiceManager.is_service_installed()
                
                print(f"\n4Paws Agent Service Status:")
                print(f"  Installed: {'✅ Yes' if installed else '❌ No'}")
                print(f"  Status: {status}")
                
                if installed and status == "Running":
                    print(f"\n  🌐 Web GUI: http://localhost:5000")
                    print(f"  🌐 Frontend: http://localhost:{Config.FRONTEND_PORT}")
                    print(f"  🌐 Backend: http://localhost:{Config.BACKEND_PORT}")
            else:
                print(f"❌ Unknown service action: {action}")
        
        else:
            print(f"❌ Unknown command: {command}")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

