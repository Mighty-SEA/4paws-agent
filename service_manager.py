"""
Windows Service Manager for 4Paws Agent
Manages agent as a Windows service for auto-start on boot
"""

import os
import sys
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ServiceManager:
    """Manages Windows service installation and removal"""
    
    SERVICE_NAME = "4PawsAgent"
    SERVICE_DISPLAY_NAME = "4Paws Deployment Agent"
    SERVICE_DESCRIPTION = "Manages 4Paws Pet Management System services (Frontend, Backend, MariaDB)"
    
    @staticmethod
    def get_executable_path():
        """Get path to the executable"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return sys.executable
        else:
            # Running as script - use python with tray_app.py
            return f'"{sys.executable}" "{Path(__file__).parent / "tray_app.py"}"'
    
    @staticmethod
    def is_service_installed():
        """Check if service is installed"""
        try:
            result = subprocess.run(
                ['sc', 'query', ServiceManager.SERVICE_NAME],
                capture_output=True,
                text=True,
                shell=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to check service: {e}")
            return False
    
    @staticmethod
    def install_service():
        """Install agent as Windows service"""
        try:
            if ServiceManager.is_service_installed():
                print(f"⚠️  Service '{ServiceManager.SERVICE_NAME}' is already installed")
                return True
            
            exe_path = ServiceManager.get_executable_path()
            
            print(f"📦 Installing Windows service...")
            print(f"   Name: {ServiceManager.SERVICE_NAME}")
            print(f"   Path: {exe_path}")
            
            # Create service
            result = subprocess.run(
                [
                    'sc', 'create', ServiceManager.SERVICE_NAME,
                    'binPath=', exe_path,
                    'DisplayName=', ServiceManager.SERVICE_DISPLAY_NAME,
                    'start=', 'auto'
                ],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode != 0:
                print(f"❌ Failed to create service: {result.stderr}")
                return False
            
            # Set description
            subprocess.run(
                [
                    'sc', 'description', ServiceManager.SERVICE_NAME,
                    ServiceManager.SERVICE_DESCRIPTION
                ],
                shell=True
            )
            
            # Set failure actions (restart on failure)
            subprocess.run(
                [
                    'sc', 'failure', ServiceManager.SERVICE_NAME,
                    'reset=', '86400',  # Reset after 24 hours
                    'actions=', 'restart/60000/restart/60000/restart/60000'  # Restart after 1 minute
                ],
                shell=True
            )
            
            print(f"✅ Service installed successfully!")
            print(f"   Service will start automatically on boot")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install service: {e}")
            logger.error(f"Service installation failed: {e}")
            return False
    
    @staticmethod
    def uninstall_service():
        """Uninstall Windows service"""
        try:
            if not ServiceManager.is_service_installed():
                print(f"⚠️  Service '{ServiceManager.SERVICE_NAME}' is not installed")
                return True
            
            print(f"🗑️  Uninstalling Windows service...")
            
            # Stop service first
            ServiceManager.stop_service()
            
            # Delete service
            result = subprocess.run(
                ['sc', 'delete', ServiceManager.SERVICE_NAME],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode != 0:
                print(f"❌ Failed to delete service: {result.stderr}")
                return False
            
            print(f"✅ Service uninstalled successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to uninstall service: {e}")
            logger.error(f"Service uninstallation failed: {e}")
            return False
    
    @staticmethod
    def start_service():
        """Start the service"""
        try:
            if not ServiceManager.is_service_installed():
                print(f"❌ Service '{ServiceManager.SERVICE_NAME}' is not installed")
                return False
            
            print(f"▶️  Starting service...")
            
            result = subprocess.run(
                ['sc', 'start', ServiceManager.SERVICE_NAME],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode != 0:
                # Check if already running
                if "already running" in result.stdout.lower():
                    print(f"✅ Service is already running")
                    return True
                print(f"❌ Failed to start service: {result.stderr}")
                return False
            
            print(f"✅ Service started successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start service: {e}")
            logger.error(f"Service start failed: {e}")
            return False
    
    @staticmethod
    def stop_service():
        """Stop the service"""
        try:
            if not ServiceManager.is_service_installed():
                print(f"⚠️  Service '{ServiceManager.SERVICE_NAME}' is not installed")
                return True
            
            print(f"⏹️  Stopping service...")
            
            result = subprocess.run(
                ['sc', 'stop', ServiceManager.SERVICE_NAME],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode != 0:
                # Check if already stopped
                if "not started" in result.stdout.lower() or "not running" in result.stdout.lower():
                    print(f"✅ Service is already stopped")
                    return True
                print(f"⚠️  Failed to stop service: {result.stderr}")
                return False
            
            print(f"✅ Service stopped successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to stop service: {e}")
            logger.error(f"Service stop failed: {e}")
            return False
    
    @staticmethod
    def get_service_status():
        """Get service status"""
        try:
            result = subprocess.run(
                ['sc', 'query', ServiceManager.SERVICE_NAME],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode != 0:
                return "Not Installed"
            
            output = result.stdout.lower()
            
            if "running" in output:
                return "Running"
            elif "stopped" in output:
                return "Stopped"
            elif "start_pending" in output:
                return "Starting"
            elif "stop_pending" in output:
                return "Stopping"
            else:
                return "Unknown"
                
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            return "Error"


def main():
    """CLI for service management"""
    import argparse
    
    # Check admin rights
    import ctypes
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    if not is_admin:
        print("""
╔════════════════════════════════════════╗
║   Administrator Rights Required       ║
╚════════════════════════════════════════╝

⚠️  Managing Windows services requires administrator privileges.

Please run this command as administrator:
1. Right-click Command Prompt or PowerShell
2. Select "Run as administrator"
3. Run the command again

""")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description='Manage 4Paws Agent as Windows service')
    parser.add_argument('action', choices=['install', 'uninstall', 'start', 'stop', 'status'],
                       help='Service action to perform')
    
    args = parser.parse_args()
    
    print("""
╔════════════════════════════════════════╗
║   4Paws Service Manager               ║
╚════════════════════════════════════════╝
""")
    
    if args.action == 'install':
        if ServiceManager.install_service():
            print("""
💡 Service installed successfully!

Next steps:
  1. Service will start automatically on next boot
  2. To start now: python service_manager.py start
  3. To check status: python service_manager.py status

The service will:
  ✅ Start automatically on Windows startup
  ✅ Auto-start all applications (Frontend, Backend, MariaDB)
  ✅ Run in background without console window
  ✅ Restart automatically if it crashes
""")
        else:
            sys.exit(1)
    
    elif args.action == 'uninstall':
        if ServiceManager.uninstall_service():
            print("""
✅ Service uninstalled successfully!

The agent will no longer:
  • Start automatically on boot
  • Run as a background service

You can still run the agent manually:
  • Double-click 4PawsAgent.exe
  • Or: python tray_app.py
""")
        else:
            sys.exit(1)
    
    elif args.action == 'start':
        ServiceManager.start_service()
    
    elif args.action == 'stop':
        ServiceManager.stop_service()
    
    elif args.action == 'status':
        status = ServiceManager.get_service_status()
        installed = ServiceManager.is_service_installed()
        
        print(f"Service Name: {ServiceManager.SERVICE_NAME}")
        print(f"Display Name: {ServiceManager.SERVICE_DISPLAY_NAME}")
        print(f"Installed: {'✅ Yes' if installed else '❌ No'}")
        print(f"Status: {status}")
        
        if installed:
            if status == "Running":
                print("""
✅ Service is running

Applications status:
  • Check Web GUI: http://localhost:5000
  • Frontend: http://localhost:3100
  • Backend: http://localhost:3200
""")
            elif status == "Stopped":
                print("""
⏹️  Service is stopped

To start: python service_manager.py start
""")


if __name__ == '__main__':
    main()

