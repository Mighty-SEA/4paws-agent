"""
Preview Installation Page
Start the installation server for testing/preview without actual installation
"""

import sys
from pathlib import Path

# Add agent to path
sys.path.insert(0, str(Path(__file__).parent))

from installation_server import start_installation_server, get_installation_server
import time
import webbrowser

def main():
    """Start installation server for preview"""
    print("""
╔════════════════════════════════════════╗
║   Installation Page Preview           ║
║   Testing Mode                        ║
╚════════════════════════════════════════╝

Starting installation page preview...
This is for TESTING ONLY - no actual installation will occur.

""")
    
    # Start installation server
    port = 3100
    print(f"🚀 Starting installation server on port {port}...")
    server = start_installation_server(port=port)
    
    if not server:
        print("❌ Failed to start installation server!")
        return
    
    print(f"✅ Installation server started!")
    print(f"🌐 Preview URL: http://localhost:{port}")
    print()
    print("=" * 50)
    print("Preview Mode Features:")
    print("  • See the installation page design")
    print("  • Test WebSocket connection")
    print("  • View progress animations")
    print("  • Check responsive layout")
    print()
    print("To test progress updates:")
    print("  • Open browser DevTools → Console")
    print("  • Run commands below in Python console")
    print("=" * 50)
    print()
    
    # Open browser
    time.sleep(1)
    print("🌐 Opening browser...")
    webbrowser.open(f"http://localhost:{port}")
    
    print()
    print("=" * 50)
    print("Test Commands (run in Python console):")
    print("=" * 50)
    print("""
# Get server instance
from installation_server import get_installation_server
server = get_installation_server(port=3100)

# Test log messages
server.send_log("📥 Downloading frontend...", "info")
server.send_log("✅ Download complete!", "success")
server.send_log("⚠️  Warning message", "warning")
server.send_log("❌ Error message", "error")

# Test progress updates
server.send_progress(10, "download", "active", "Downloading", "Fetching files...")
server.send_progress(30, "download", "active", "Downloading", "Progress...")
server.send_progress(40, "download", "completed", "Download Complete", "Files ready")

server.send_progress(40, "install", "active", "Installing", "Setting up packages...")
server.send_progress(60, "install", "completed")

server.send_progress(60, "database", "active", "Database Setup", "Running migrations...")
server.send_progress(80, "database", "completed")

server.send_progress(80, "start", "active", "Starting Services", "Launching apps...")
server.send_progress(100, "start", "completed")

# Test completion
server.send_complete()
""")
    print("=" * 50)
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Keep server running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping server...")
        server.stop()
        print("✅ Server stopped")

if __name__ == "__main__":
    main()

