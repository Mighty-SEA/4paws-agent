"""
4Paws Agent Tray Launcher
Launches tray app in user session when service is running
"""

import os
import sys
import subprocess
import time
import socket
from pathlib import Path

def is_service_running():
    """Check if 4PawsAgent service is running"""
    try:
        result = subprocess.run(
            ['sc', 'query', '4PawsAgent'],
            capture_output=True,
            text=True,
            shell=True
        )
        return result.returncode == 0 and "RUNNING" in result.stdout
    except:
        return False

def is_agent_running():
    """Check if agent is running (port 5000)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        return result == 0
    except:
        return False

def main():
    """Launch tray app if service is running"""
    print("""
╔════════════════════════════════════════╗
║   4Paws Agent Tray Launcher          ║
║   User Interface for Service         ║
╚════════════════════════════════════════╝
""")
    
    # Check if service is running
    if not is_service_running():
        print("❌ 4PawsAgent service is not running")
        print("\nTo start the service:")
        print("  python agent.py service start")
        print("  or")
        print("  sc start 4PawsAgent")
        input("\nPress Enter to exit...")
        return
    
    print("✅ 4PawsAgent service is running")
    
    # Wait for agent to be ready
    print("⏳ Waiting for agent to be ready...")
    max_wait = 30  # 30 seconds
    for i in range(max_wait):
        if is_agent_running():
            print("✅ Agent is ready!")
            break
        time.sleep(1)
        print(f"   Waiting... ({i+1}/{max_wait})")
    else:
        print("❌ Agent not responding after 30 seconds")
        print("   Check service logs or restart service")
        input("\nPress Enter to exit...")
        return
    
    # Launch tray app
    print("🚀 Launching tray application...")
    try:
        tray_script = Path(__file__).parent / "tray_app.py"
        subprocess.Popen([sys.executable, str(tray_script)])
        print("✅ Tray application launched!")
        print("\nLook for the 4Paws icon in your system tray")
        print("Right-click the icon for options")
    except Exception as e:
        print(f"❌ Failed to launch tray app: {e}")
        input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
