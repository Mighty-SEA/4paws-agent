"""
License Management System
Handles license validation with multiple layers of protection
"""

import os
import json
import logging
import requests
import hmac
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Secret key for HMAC signature (should be obfuscated in production)
LICENSE_SECRET_KEY = "4paws-license-secret-v1-2025"


class LicenseManager:
    """
    Manage license validation with 3-layer protection:
    1. Hard expiry date (cannot bypass)
    2. Online heartbeat check (must online every 30 days)
    3. Remote kill switch (suspend from server)
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            from .config import Config
            config_dir = Config.BASE_DIR
        
        self.license_file = config_dir / 'data' / 'license.dat'
        self.license_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Google Sheets API URL (set via environment variable)
        self.api_url = os.getenv('LICENSE_API_URL', '')
        
        # Support contact info
        self.support_email = os.getenv('SUPPORT_EMAIL', 'support@yourcompany.com')
        self.support_phone = os.getenv('SUPPORT_PHONE', '+62 xxx-xxx-xxxx')
    
    def check_license(self) -> Dict:
        """
        Check license validity with multiple layers
        
        Returns:
            dict: {
                'valid': bool,
                'reason': str (if invalid),
                'message': str (if invalid),
                'expiry': str (date),
                'support_email': str,
                'support_phone': str
            }
        """
        
        # Layer 1: Hard Expiry Date (MANDATORY - Cannot bypass)
        hard_expiry = os.getenv('LICENSE_EXPIRY', '2025-01-31')
        try:
            expiry_date = datetime.fromisoformat(hard_expiry)
        except ValueError:
            logger.error(f"Invalid LICENSE_EXPIRY format: {hard_expiry}")
            return self._invalid_response(
                'Invalid License',
                'License configuration error. Contact support.',
                hard_expiry
            )
        
        if datetime.now() > expiry_date:
            return self._invalid_response(
                'License Expired',
                f'Your license expired on {expiry_date.date()}. Please renew to continue.',
                str(expiry_date.date())
            )
        
        # Layer 2: Online Status Check (Try online first, then check offline days)
        online_check_success = False
        if self.api_url:
            try:
                logger.info("🌐 Attempting online license verification...")
                online_status = self._check_online()
                
                if online_status and online_status['status'] == 'suspended':
                    return self._invalid_response(
                        'License Suspended',
                        'Your license has been suspended by administrator. Please contact support.',
                        online_status.get('expiry', str(expiry_date.date()))
                    )
                
                # Update last online check timestamp
                if online_status:
                    self._update_last_online_check()
                    logger.info("✅ Online license check successful")
                    online_check_success = True
                else:
                    logger.warning("⚠️  Online check returned no data (possible network issue)")
                
            except Exception as e:
                # Offline is OK, just log and continue
                logger.warning(f"⚠️  Online check failed: {e}")
                logger.info("📴 Falling back to offline mode...")
        else:
            logger.info("📴 No LICENSE_API_URL configured, skipping online check")
        
        # Layer 3: Offline Heartbeat Check (Must online at least once every X days)
        # Only check if online check failed (to prevent blocking when just came online)
        if not online_check_success:
            last_online_check = self._get_last_online_check()
            
            # CRITICAL: If no license file exists and offline, MUST block!
            if last_online_check is None:
                logger.warning("⚠️  No license verification found. Initial online check required.")
                return self._invalid_response(
                    'Initial Verification Required',
                    'Application requires initial online verification. Please connect to internet and restart.',
                    str(expiry_date.date())
                )
            
            # Validate last_online_check is not in the future (tampering detection)
            if last_online_check > datetime.now():
                logger.warning("⚠️  License file tampering detected (future date). Blocking access.")
                return self._invalid_response(
                    'License File Tampered',
                    'License verification failed. Please connect to internet and restart.',
                    str(expiry_date.date())
                )
            
            days_offline = (datetime.now() - last_online_check).days
            max_offline_days = int(os.getenv('MAX_OFFLINE_DAYS', '30'))
            
            # Also validate days_offline is positive (additional safety)
            if days_offline < 0:
                logger.warning("⚠️  Invalid license file (negative offline days). Blocking access.")
                return self._invalid_response(
                    'License File Invalid',
                    'License verification failed. Please connect to internet and restart.',
                    str(expiry_date.date())
                )
            
            if days_offline > max_offline_days:
                return self._invalid_response(
                    'Online Verification Required',
                    f'Application requires online verification. Last check: {days_offline} days ago (max: {max_offline_days} days). Please connect to internet and restart.',
                    str(expiry_date.date())
                )
        
        # All checks passed - License is valid
        days_remaining = (expiry_date - datetime.now()).days
        logger.info(f"✅ License valid (expires: {expiry_date.date()}, {days_remaining} days remaining)")
        
        return {
            'valid': True,
            'expiry': str(expiry_date.date()),
            'days_remaining': days_remaining
        }
    
    def _check_online(self) -> Optional[Dict]:
        """Check license status from online API (Google Sheets)"""
        if not self.api_url:
            return None
        
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'status': data.get('status', 'unknown'),
                'expiry': data.get('expiry'),
                'last_payment': data.get('last_payment')
            }
        except Exception as e:
            logger.debug(f"Online check error: {e}")
            return None
    
    def _get_last_online_check(self) -> Optional[datetime]:
        """Get timestamp of last successful online check with signature verification"""
        if not self.license_file.exists():
            return None
        
        try:
            with open(self.license_file, 'r') as f:
                data = json.load(f)
                
            # Verify signature to detect tampering
            if not self._verify_signature(data):
                logger.warning("⚠️  License file signature invalid (tampered). Blocking access.")
                return None  # Treat as no file (force online check)
            
            last_check = data.get('last_online_check')
            if last_check:
                return datetime.fromisoformat(last_check)
                
        except Exception as e:
            logger.debug(f"Error reading license file: {e}")
        
        return None
    
    def _update_last_online_check(self):
        """Update timestamp of last successful online check with signature"""
        try:
            # Create new data with timestamp
            data = {
                'last_online_check': datetime.now().isoformat()
            }
            
            # Add signature to prevent tampering
            signature = self._create_signature(data)
            data['signature'] = signature
            
            # Save
            with open(self.license_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Updated last online check timestamp with signature")
        except Exception as e:
            logger.warning(f"Failed to update last online check: {e}")
    
    def _create_signature(self, data: dict) -> str:
        """Create HMAC signature for license data"""
        # Only sign the timestamp, not the signature itself
        message = data.get('last_online_check', '')
        signature = hmac.new(
            LICENSE_SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _verify_signature(self, data: dict) -> bool:
        """Verify HMAC signature of license data"""
        if 'signature' not in data:
            logger.debug("No signature found in license file")
            return False
        
        stored_signature = data.get('signature')
        expected_signature = self._create_signature(data)
        
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(stored_signature, expected_signature)
    
    def _invalid_response(self, reason: str, message: str, expiry: str) -> Dict:
        """Create invalid license response"""
        return {
            'valid': False,
            'reason': reason,
            'message': message,
            'expiry': expiry,
            'support_email': self.support_email,
            'support_phone': self.support_phone
        }
    
    @staticmethod
    def check_and_block() -> bool:
        """
        Check license and handle blocking if invalid
        Returns True if valid, False if invalid
        """
        manager = LicenseManager()
        license_status = manager.check_license()
        
        if not license_status['valid']:
            # License invalid - log error
            logger.error("╔════════════════════════════════════════╗")
            logger.error("║   🔒 LICENSE ERROR                     ║")
            logger.error("╠════════════════════════════════════════╣")
            logger.error(f"║  {license_status['reason']:<38} ║")
            logger.error("║                                        ║")
            logger.error(f"║  {license_status['message'][:38]:<38} ║")
            if len(license_status['message']) > 38:
                logger.error(f"║  {license_status['message'][38:76]:<38} ║")
            logger.error("║                                        ║")
            logger.error("║  Please contact support:               ║")
            logger.error(f"║  📧 {license_status['support_email']:<36} ║")
            logger.error(f"║  📱 {license_status['support_phone']:<36} ║")
            logger.error("╚════════════════════════════════════════╝")
            
            return False
        
        return True
    
    @staticmethod
    def start_license_page(port: int = 3100):
        """Start license expired page on specified port"""
        manager = LicenseManager()
        license_status = manager.check_license()
        
        if not license_status['valid']:
            logger.info(f"🔒 Starting license expired page on port {port}...")
            
            # Import and start license server
            try:
                from license_server import start_license_server
                
                # Define restart callback
                def restart_agent():
                    """Restart agent by spawning new process and exiting current one"""
                    import time
                    import os
                    import sys
                    import subprocess
                    from pathlib import Path
                    
                    logger.info("🔄 Restart requested from license page...")
                    logger.info("⏹️  Stopping current agent process...")
                    
                    # Stop license server first
                    from license_server import stop_license_server
                    stop_license_server()
                    
                    time.sleep(1)
                    
                    # Get agent script path and python executable
                    agent_script = Path(__file__).parent.parent / 'agent.py'
                    python_exe = sys.executable
                    
                    logger.info(f"🔄 Spawning new agent process: {python_exe} {agent_script} start")
                    
                    # Spawn new agent process (detached)
                    try:
                        if os.name == 'nt':  # Windows
                            # Use CREATE_NEW_PROCESS_GROUP to detach
                            CREATE_NO_WINDOW = 0x08000000
                            subprocess.Popen(
                                [python_exe, str(agent_script), 'start'],
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                stdin=subprocess.DEVNULL,
                                cwd=str(agent_script.parent)
                            )
                        else:  # Linux/Mac
                            subprocess.Popen(
                                [python_exe, str(agent_script), 'start'],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                stdin=subprocess.DEVNULL,
                                cwd=str(agent_script.parent),
                                start_new_session=True
                            )
                        
                        logger.info("✅ New agent process spawned successfully")
                        logger.info("⏹️  Current process will exit in 2 seconds...")
                        
                        time.sleep(2)
                        
                        # Exit current process
                        os._exit(0)
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to spawn new agent: {e}")
                        logger.info("💡 Please restart agent manually")
                
                start_license_server(port=port, license_data=license_status, on_restart=restart_agent)
                
                # Open browser
                import webbrowser
                import time
                time.sleep(1)
                webbrowser.open(f"http://localhost:{port}")
                
                logger.info(f"✅ License page available at: http://localhost:{port}")
            except Exception as e:
                logger.error(f"Failed to start license server: {e}")

