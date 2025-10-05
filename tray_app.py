"""
4Paws Agent System Tray Application
Provides system tray icon with quick actions for managing the agent
"""

import os
import sys
import webbrowser
import subprocess
import threading
import socket
import time
from pathlib import Path
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# Add agent.py to path
sys.path.insert(0, str(Path(__file__).parent))
from agent import ProcessManager, Agent
from gui_server import start_server, find_available_port

class TrayApp:
    def __init__(self):
        self.icon = None
        self.gui_server = None
        self.gui_port = None
        self.lock_socket = None
        self.agent = Agent()
        self.check_update_thread = None
        self.auto_check_enabled = True
        self.update_available = False
        
    def acquire_lock(self):
        """Acquire single instance lock using socket"""
        try:
            # Try to bind to a specific port as lock
            # Port 59999 is used as a lock mechanism
            self.lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.lock_socket.bind(('127.0.0.1', 59999))
            return True
        except OSError:
            # Port already in use = another instance is running
            return False
    
    def release_lock(self):
        """Release single instance lock"""
        if self.lock_socket:
            try:
                self.lock_socket.close()
            except:
                pass
            self.lock_socket = None
    
    def create_icon_image(self, color="white"):
        """Load icon from file or create fallback"""
        try:
            # Try to load favicon.ico
            icon_path = Path(__file__).parent / "static" / "img" / "favicon.ico"
            if icon_path.exists():
                image = Image.open(icon_path)
                # Resize if needed
                if image.size != (64, 64):
                    image = image.resize((64, 64), Image.Resampling.LANCZOS)
                
                # Apply color tint for status indication
                if color != "white":
                    # Create a colored overlay
                    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
                    draw = ImageDraw.Draw(overlay)
                    
                    if color == "green":
                        tint = (46, 204, 113, 100)  # Green for running
                    elif color == "yellow":
                        tint = (243, 156, 18, 100)  # Yellow for update available
                    else:
                        tint = (149, 165, 166, 100)  # Gray for stopped
                    
                    # Draw colored circle in corner as status indicator
                    draw.ellipse([48, 48, 62, 62], fill=tint)
                    image = Image.alpha_composite(image.convert('RGBA'), overlay)
                
                return image
        except Exception as e:
            print(f"Warning: Could not load icon from file: {e}")
        
        # Fallback: Create a simple paw icon
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw paw
        if color == "white":
            fill = (255, 255, 255, 255)
        elif color == "green":
            fill = (46, 204, 113, 255)  # Green for running
        elif color == "yellow":
            fill = (243, 156, 18, 255)  # Yellow for update available
        else:
            fill = (149, 165, 166, 255)  # Gray for stopped
        
        # Main pad
        draw.ellipse([20, 30, 44, 54], fill=fill)
        
        # Toes
        draw.ellipse([15, 15, 27, 27], fill=fill)
        draw.ellipse([28, 12, 40, 24], fill=fill)
        draw.ellipse([41, 15, 53, 27], fill=fill)
        
        return image
    
    def update_icon_color(self, color="white"):
        """Update icon color based on service status"""
        if self.icon:
            self.icon.icon = self.create_icon_image(color)
    
    def start_gui_server(self):
        """Start the Web GUI server in background"""
        if self.gui_server is None:
            def run_server():
                self.gui_port = find_available_port(5000)
                start_server(self.gui_port)
            
            self.gui_server = threading.Thread(target=run_server, daemon=True)
            self.gui_server.start()
            return True
        return False
    
    def auto_start_services(self):
        """Auto-start services if apps are installed and not running"""
        try:
            # Check if apps are installed
            if self.agent.are_apps_installed():
                # Check if services are not already running
                if not any(key in ProcessManager.processes for key in ['mariadb', 'backend', 'frontend']):
                    print("🚀 Auto-starting services...")
                    
                    # Start services in background thread
                    def start_services():
                        import time
                        time.sleep(3)  # Wait for GUI server to initialize
                        try:
                            if self.agent.start_all(skip_setup=True):
                                self.update_icon_color("green")
                                self.show_notification("Services Started", "All services are running")
                                print("✅ Services started automatically")
                            else:
                                print("⚠️  Some services failed to start")
                        except Exception as e:
                            print(f"❌ Auto-start failed: {e}")
                    
                    start_thread = threading.Thread(target=start_services, daemon=True)
                    start_thread.start()
                else:
                    print("✅ Services already running")
                    self.update_icon_color("green")
            else:
                print("📦 Apps not installed yet")
        except Exception as e:
            print(f"⚠️  Auto-start check failed: {e}")
    
    def open_web_gui(self, icon, item):
        """Open Web GUI in browser"""
        if self.gui_port is None:
            self.start_gui_server()
            # Wait a bit for server to start
            import time
            time.sleep(2)
        
        webbrowser.open(f'http://localhost:{self.gui_port or 5000}')
    
    def start_all_services(self, icon, item):
        """Start all services"""
        try:
            # Use agent.py CLI
            subprocess.Popen(['python', 'agent.py', 'start', '--skip-setup'], 
                           cwd=str(Path(__file__).parent),
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.update_icon_color("green")
            self.show_notification("Services Started", "All services have been started")
        except Exception as e:
            self.show_notification("Error", f"Failed to start services: {str(e)}")
    
    def stop_all_services(self, icon, item):
        """Stop all services"""
        try:
            ProcessManager.stop_all()
            self.update_icon_color("gray")
            self.show_notification("Services Stopped", "All services have been stopped")
        except Exception as e:
            self.show_notification("Error", f"Failed to stop services: {str(e)}")
    
    def check_updates_manual(self, icon, item):
        """Manual check for updates (opens console)"""
        try:
            subprocess.Popen(['python', 'agent.py', 'check'],
                           cwd=str(Path(__file__).parent),
                           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        except Exception as e:
            self.show_notification("Error", f"Failed to check updates: {str(e)}")
    
    def check_updates_background(self):
        """Background check for updates (silent)"""
        try:
            # Skip if installation is in progress
            from agent import ProcessManager
            if ProcessManager.installation_in_progress:
                print("ℹ️  Skipping auto-check: Installation in progress")
                return
            
            updates = self.agent.check_updates()
            
            if updates:
                # Updates available
                self.update_available = True
                update_list = []
                if 'frontend' in updates:
                    update_list.append(f"Frontend: {updates['frontend']}")
                if 'backend' in updates:
                    update_list.append(f"Backend: {updates['backend']}")
                
                message = "Updates available!\n" + "\n".join(update_list)
                self.show_notification("Updates Available", message)
                
                # Change icon color to indicate update
                self.update_icon_color("yellow")
            else:
                self.update_available = False
                
        except Exception as e:
            print(f"Error checking updates: {e}")
    
    def auto_check_updates_loop(self):
        """Background thread to periodically check for updates"""
        # Check on startup after 30 seconds
        time.sleep(30)
        self.check_updates_background()
        
        # Then check every 6 hours
        while self.auto_check_enabled:
            time.sleep(6 * 60 * 60)  # 6 hours
            if self.auto_check_enabled:
                # Check will be skipped if installation is in progress
                self.check_updates_background()
    
    def start_auto_check(self):
        """Start auto-check update thread"""
        if self.check_update_thread is None or not self.check_update_thread.is_alive():
            self.check_update_thread = threading.Thread(
                target=self.auto_check_updates_loop,
                daemon=True
            )
            self.check_update_thread.start()
    
    def install_updates(self, icon, item):
        """Install available updates"""
        if not self.update_available:
            self.show_notification("No Updates", "No updates available")
            return
        
        try:
            self.show_notification("Installing Updates", "Downloading and installing updates...")
            
            # Run update in background
            subprocess.Popen(['python', 'agent.py', 'update', '--yes'],
                           cwd=str(Path(__file__).parent),
                           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            
            self.update_available = False
            self.update_icon_color("white")
        except Exception as e:
            self.show_notification("Error", f"Failed to install updates: {str(e)}")
    
    def open_frontend(self, icon, item):
        """Open frontend in browser"""
        webbrowser.open('http://localhost:3100')
    
    def open_backend(self, icon, item):
        """Open backend API in browser"""
        webbrowser.open('http://localhost:3200')
    
    def show_notification(self, title, message):
        """Show system notification"""
        if self.icon:
            self.icon.notify(message, title)
    
    def quit_app(self, icon, item):
        """Quit the application"""
        print("\n🛑 Quitting 4Paws Agent...")
        
        # Stop all services
        try:
            print("⏹️  Stopping all services...")
            ProcessManager.stop_all()
            print("✅ Services stopped")
        except Exception as e:
            print(f"⚠️  Error stopping services: {e}")
            # Force kill any remaining processes
            try:
                import psutil
                current_pid = os.getpid()
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        proc_pid = proc.info['pid']
                        # Kill mysqld and node processes (but not ourselves)
                        if proc_pid != current_pid and ('mysqld' in proc_name or 'node' in proc_name):
                            print(f"🔪 Force killing {proc.info['name']} (PID {proc_pid})")
                            proc.kill()
                    except:
                        pass
            except Exception as cleanup_error:
                print(f"⚠️  Cleanup error: {cleanup_error}")
        
        # Release lock
        self.release_lock()
        
        # Stop icon
        print("✅ Quit complete")
        icon.stop()
    
    def create_menu(self):
        """Create system tray menu"""
        return pystray.Menu(
            item('🌐 Open Web GUI', self.open_web_gui),
            pystray.Menu.SEPARATOR,
            item('▶️ Start All Services', self.start_all_services),
            item('⏹️ Stop All Services', self.stop_all_services),
            pystray.Menu.SEPARATOR,
            item('🎨 Open Frontend', self.open_frontend),
            item('🔧 Open Backend API', self.open_backend),
            pystray.Menu.SEPARATOR,
            item('🔄 Check Updates', self.check_updates_manual),
            item('📥 Install Updates', self.install_updates, enabled=lambda _: self.update_available),
            pystray.Menu.SEPARATOR,
            item('❌ Quit', self.quit_app)
        )
    
    def run(self):
        """Run the system tray application"""
        # Check for single instance
        if not self.acquire_lock():
            print("""
╔════════════════════════════════════════╗
║   4Paws Agent Already Running!        ║
╚════════════════════════════════════════╝

❌ Another instance of 4Paws Agent is already running.
🔍 Check your system tray for the existing icon.

Press any key to exit...
""")
            input()
            sys.exit(1)
        
        try:
            # Start Web GUI server in background
            self.start_gui_server()
            
            # Auto-start services if apps are installed
            self.auto_start_services()
            
            # Start auto-check updates thread
            self.start_auto_check()
            
            # Create and run system tray icon
            self.icon = pystray.Icon(
                '4Paws Agent',
                self.create_icon_image(),
                '4Paws Deployment Agent',
                self.create_menu()
            )
            
            print("""
╔════════════════════════════════════════╗
║   4Paws Agent System Tray             ║
║   Running in background               ║
╚════════════════════════════════════════╝

🐾 System tray icon active
🌐 Web GUI available
🔄 Auto-update check enabled (every 6 hours)
📊 First check in 30 seconds

Right-click the tray icon for options
""")
            
            self.icon.run()
        finally:
            # Stop auto-check thread
            self.auto_check_enabled = False
            
            # Always release lock on exit
            self.release_lock()

if __name__ == '__main__':
    app = TrayApp()
    app.run()

