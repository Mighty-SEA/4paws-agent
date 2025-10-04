"""
4Paws Agent Web GUI Server
Web-based dashboard for managing 4Paws deployment agent
"""

import os
import sys
import json
import socket
import psutil
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Add agent.py to path
sys.path.insert(0, str(Path(__file__).parent))
from agent import Agent, ProcessManager, Config, VersionManager, set_agent_log_manager
from log_manager import init_log_manager, get_log_manager
from installation_server import start_installation_server, stop_installation_server, get_installation_server
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = '4paws-agent-secret'

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3100", "http://localhost:3200"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

socketio = SocketIO(app, cors_allowed_origins="*")

# Global agent instance
agent = Agent()

# Initialize log manager
log_file = Path(__file__).parent / 'logs' / 'agent_web.log'
log_manager = init_log_manager(log_file, socketio)

# Connect agent logging to web GUI
set_agent_log_manager(log_manager)

# Reduce Flask logging verbosity (disable HTTP access logs in Web GUI)
import logging as flask_logging
flask_logging.getLogger('werkzeug').setLevel(flask_logging.WARNING)

# Update check cache (1 hour)
UPDATE_CHECK_CACHE = {
    'last_check': None,
    'result': None,
    'cache_duration': 3600  # 1 hour in seconds
}

def find_available_port(start_port=5000):
    """Find available port starting from start_port"""
    port = start_port
    while port < start_port + 100:  # Try up to 100 ports
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            port += 1
    raise RuntimeError(f"No available ports found from {start_port} to {start_port + 100}")

def get_process_status(name):
    """Check if a process is running"""
    if name in ProcessManager.processes:
        try:
            proc = ProcessManager.processes[name]
            if proc.poll() is None:
                return {
                    'running': True,
                    'pid': proc.pid,
                    'cpu': psutil.Process(proc.pid).cpu_percent(interval=0.1),
                    'memory': psutil.Process(proc.pid).memory_info().rss / 1024 / 1024  # MB
                }
        except:
            pass
    return {'running': False, 'pid': None, 'cpu': 0, 'memory': 0}

@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')

@app.route('/logs')
def logs():
    """Render logs page"""
    return render_template('logs.html')

@app.route('/api/status')
def api_status():
    """Get current status of all services"""
    versions = VersionManager.load_versions()
    
    return jsonify({
        'mariadb': get_process_status('mariadb'),
        'backend': get_process_status('backend'),
        'frontend': get_process_status('frontend'),
        'versions': versions,
        'ports': {
            'mariadb': Config.MARIADB_PORT,
            'backend': Config.BACKEND_PORT,
            'frontend': Config.FRONTEND_PORT
        },
        'paths': {
            'frontend': str(Config.FRONTEND_DIR.absolute()) if Config.FRONTEND_DIR.exists() else 'Not installed',
            'backend': str(Config.BACKEND_DIR.absolute()) if Config.BACKEND_DIR.exists() else 'Not installed',
            'mariadb': str(Config.MARIADB_DIR.absolute()) if Config.MARIADB_DIR.exists() else 'Not installed',
            'data': str(Config.DATA_DIR.absolute())
        },
        'system': {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
        }
    })

@app.route('/api/start/<service>', methods=['POST'])
def api_start(service):
    """Start a service"""
    try:
        log_manager.start_action(f'start-{service}')
        log_manager.info(f"🚀 Starting {service}...")
        
        if service == 'all':
            # Don't skip setup - let auto-detect handle it
            success = agent.start_all(skip_setup=False)
        elif service == 'mariadb':
            success = ProcessManager.start_mariadb()
        elif service == 'backend':
            success = ProcessManager.start_backend()
        elif service == 'frontend':
            success = ProcessManager.start_frontend()
        else:
            log_manager.error(f"Unknown service: {service}")
            return jsonify({'success': False, 'error': f'Unknown service: {service}'}), 400
        
        if success:
            log_manager.success(f"✅ {service} started successfully")
        else:
            log_manager.error(f"❌ Failed to start {service}")
        
        log_manager.end_action(f'start-{service}', success)
        return jsonify({'success': success})
    except Exception as e:
        log_manager.error(f"❌ Error starting {service}: {str(e)}")
        log_manager.end_action(f'start-{service}', False)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop/<service>', methods=['POST'])
def api_stop(service):
    """Stop a service"""
    try:
        log_manager.start_action(f'stop-{service}')
        log_manager.info(f"⏹️ Stopping {service}...")
        
        if service == 'all':
            agent.stop_all()
            log_manager.success(f"✅ All services stopped")
            log_manager.end_action(f'stop-{service}', True)
            return jsonify({'success': True})
        elif service in ['mariadb', 'backend', 'frontend']:
            if service in ProcessManager.processes:
                ProcessManager.processes[service].terminate()
                ProcessManager.processes[service].wait(timeout=10)
                del ProcessManager.processes[service]
            log_manager.success(f"✅ {service} stopped")
            log_manager.end_action(f'stop-{service}', True)
            return jsonify({'success': True})
        else:
            log_manager.error(f"Unknown service: {service}")
            return jsonify({'success': False, 'error': f'Unknown service: {service}'}), 400
    except Exception as e:
        log_manager.error(f"❌ Error stopping {service}: {str(e)}")
        log_manager.end_action(f'stop-{service}', False)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/updates')
def api_updates():
    """Check for updates"""
    try:
        updates = agent.check_updates()
        return jsonify({'updates': updates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs/<service>')
def api_logs(service):
    """Get service logs"""
    try:
        log_file = Config.LOGS_DIR / f'{service}.log'
        if not log_file.exists():
            return jsonify({'logs': ''})
        
        # Read last 100 lines
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            return jsonify({'logs': ''.join(lines[-100:])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/install/<component>', methods=['POST'])
def api_install(component):
    """Install frontend/backend/all"""
    try:
        log_manager.start_action(f'install-{component}')
        log_manager.info(f"📦 Installing {component}...")
        
        success = agent.install_apps(component)
        
        if success:
            log_manager.success(f"✅ {component} installed successfully")
        else:
            log_manager.error(f"❌ Failed to install {component}")
        
        log_manager.end_action(f'install-{component}', success)
        return jsonify({'success': success})
    except Exception as e:
        log_manager.error(f"❌ Error installing {component}: {str(e)}")
        log_manager.end_action(f'install-{component}', False)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/update/<component>', methods=['POST'])
def api_update(component):
    """Update frontend/backend/all"""
    try:
        # Get force flag from request
        data = request.get_json() or {}
        force = data.get('force', False)
        
        log_manager.start_action(f'update-{component}')
        log_manager.info(f"🔄 Updating {component}...")
        
        if component == 'all':
            success = agent.update_apps('all', force=force)
        else:
            success = agent.update_apps(component, force=force)
        
        if success:
            log_manager.success(f"✅ {component} updated successfully")
        else:
            log_manager.error(f"❌ Failed to update {component}")
        
        log_manager.end_action(f'update-{component}', success)
        return jsonify({'success': success})
    except Exception as e:
        log_manager.error(f"❌ Error updating {component}: {str(e)}")
        log_manager.end_action(f'update-{component}', False)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/setup/<component>', methods=['POST'])
def api_setup(component):
    """Setup apps (install dependencies, migrate, etc)"""
    try:
        log_manager.start_action(f'setup-{component}')
        log_manager.info(f"⚙️ Setting up {component}...")
        
        success = agent.setup_apps(component)
        
        if success:
            log_manager.success(f"✅ {component} setup completed")
        else:
            log_manager.error(f"❌ Failed to setup {component}")
        
        log_manager.end_action(f'setup-{component}', success)
        return jsonify({'success': success})
    except Exception as e:
        log_manager.error(f"❌ Error setting up {component}: {str(e)}")
        log_manager.end_action(f'setup-{component}', False)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/seed', methods=['POST'])
def api_seed():
    """Seed database"""
    try:
        data = request.get_json() or {}
        seed_type = data.get('type', 'all')
        
        log_manager.start_action(f'seed-{seed_type}')
        log_manager.info(f"🌱 Seeding database ({seed_type})...")
        
        success = agent.seed_database(seed_type)
        
        if success:
            log_manager.success(f"✅ Database seeded successfully ({seed_type})")
        else:
            log_manager.error(f"❌ Failed to seed database ({seed_type})")
        
        log_manager.end_action(f'seed-{seed_type}', success)
        return jsonify({'success': success})
    except Exception as e:
        log_manager.error(f"❌ Error seeding database: {str(e)}")
        log_manager.end_action(f'seed-{seed_type}', False)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/check-tools')
def api_check_tools():
    """Check if portable tools are installed"""
    try:
        tools_status = {
            'node': (Config.NODE_DIR / 'node.exe').exists(),
            'pnpm': (Config.PNPM_DIR / 'pnpm.cmd').exists(),
            'mariadb': (Config.MARIADB_DIR / 'bin' / 'mysqld.exe').exists()
        }
        
        apps_status = {
            'frontend': Config.FRONTEND_DIR.exists(),
            'backend': Config.BACKEND_DIR.exists()
        }
        
        return jsonify({
            'tools': tools_status,
            'apps': apps_status,
            'all_tools_ready': all(tools_status.values()),
            'all_apps_installed': all(apps_status.values())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update/check')
def api_update_check():
    """Check for updates (for application integration) - Cached for 1 hour"""
    try:
        import time
        current_time = time.time()
        
        # Check if cache is valid (less than 1 hour old)
        if (UPDATE_CHECK_CACHE['last_check'] is not None and 
            UPDATE_CHECK_CACHE['result'] is not None and
            (current_time - UPDATE_CHECK_CACHE['last_check']) < UPDATE_CHECK_CACHE['cache_duration']):
            
            # Return cached result (NO LOG - too verbose)
            cached_result = UPDATE_CHECK_CACHE['result']
            cached_age = int(current_time - UPDATE_CHECK_CACHE['last_check'])
            
            return jsonify({
                **cached_result,
                'cached': True,
                'cache_age': cached_age,
                'next_check_in': UPDATE_CHECK_CACHE['cache_duration'] - cached_age
            })
        
        # Cache expired or doesn't exist, perform new check
        # Only log REAL checks (when actually calling GitHub API)
        log_manager.info("🔍 Checking for updates from GitHub...")
        versions = VersionManager.load_versions()
        updates = agent.check_updates()
        
        result = {
            'current': {
                'frontend': versions['frontend']['version'],
                'backend': versions['backend']['version']
            },
            'latest': updates if updates else {},
            'has_update': bool(updates),
            'details': {
                'frontend': {
                    'current': versions['frontend']['version'],
                    'latest': updates.get('frontend') if updates else None,
                    'has_update': 'frontend' in updates if updates else False
                },
                'backend': {
                    'current': versions['backend']['version'],
                    'latest': updates.get('backend') if updates else None,
                    'has_update': 'backend' in updates if updates else False
                }
            },
            'cached': False
        }
        
        # Update cache
        UPDATE_CHECK_CACHE['last_check'] = current_time
        UPDATE_CHECK_CACHE['result'] = result
        
        # Log result only (not cache info)
        if result['has_update']:
            log_manager.info(f"🆕 Updates available! (cached for 1 hour)")
        else:
            log_manager.success(f"✅ All up to date (cached for 1 hour)")
        
        return jsonify(result)
    except Exception as e:
        log_manager.error(f"❌ Update check failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/update/check/clear-cache', methods=['POST'])
def api_update_check_clear_cache():
    """Clear update check cache (force fresh check on next request)"""
    try:
        UPDATE_CHECK_CACHE['last_check'] = None
        UPDATE_CHECK_CACHE['result'] = None
        log_manager.success("✅ Update check cache cleared")
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared. Next check will be fresh.'
        })
    except Exception as e:
        log_manager.error(f"❌ Failed to clear cache: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/update/start', methods=['POST'])
def api_update_start():
    """Start update process (non-blocking with WebSocket notifications)"""
    try:
        data = request.get_json() or {}
        component = data.get('component', 'all')
        
        # Clear update cache since we're updating
        UPDATE_CHECK_CACHE['last_check'] = None
        UPDATE_CHECK_CACHE['result'] = None
        
        # Start update in background thread
        import threading
        thread = threading.Thread(
            target=perform_update_with_notifications,
            args=(component,),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Update started',
            'websocket_channel': 'update_progress'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def start_loading_server(port=3100, page='update_loading.html'):
    """Start simple HTTP server for update loading page"""
    import http.server
    import socketserver
    import threading
    
    class LoadingHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, loading_page=page, **kwargs):
            self.loading_page = loading_page
            super().__init__(*args, **kwargs)
            
        def do_GET(self):
            if self.path == '/' or self.path == '/index.html':
                # Serve loading page
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                loading_file = Path(__file__).parent / self.loading_page
                with open(loading_file, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                super().do_GET()
        
        def log_message(self, format, *args):
            pass  # Suppress logs
    
    try:
        # Create handler factory with loading_page parameter
        handler = lambda *args, **kwargs: LoadingHandler(*args, loading_page=page, **kwargs)
        server = socketserver.TCPServer(("", port), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server
    except Exception as e:
        print(f"Failed to start loading server on port {port}: {e}")
        return None

def perform_update_with_notifications(component):
    """Background update with WebSocket notifications"""
    try:
        import time
        
        # Step 1: Stopping services and starting loading pages
        socketio.emit('update_status', {
            'status': 'stopping_services',
            'message': 'Stopping services...',
            'progress': 10
        })
        
        # Stop all services
        ProcessManager.stop_all()
        time.sleep(2)
        
        # Start loading servers on both ports
        frontend_loading_server = start_loading_server(port=3100, page='update_loading.html')
        backend_loading_server = start_loading_server(port=3200, page='update_loading_backend.html')
        time.sleep(1)
        
        # Step 2: Downloading
        socketio.emit('update_status', {
            'status': 'downloading',
            'message': 'Downloading updates from GitHub...',
            'progress': 30
        })
        time.sleep(1)
        
        # Step 3: Install updates
        socketio.emit('update_status', {
            'status': 'extracting',
            'message': 'Extracting and installing updates...',
            'progress': 50
        })
        
        success = agent.update_apps(component, force=True)
        
        if not success:
            socketio.emit('update_status', {
                'status': 'failed',
                'message': 'Update failed! Please check logs.',
                'progress': 0
            })
            return
        
        # Step 4: Setup apps (install dependencies & migrations)
        socketio.emit('update_status', {
            'status': 'setup',
            'message': 'Installing dependencies and running migrations...',
            'progress': 70
        })
        
        # Run setup for updated components
        if not agent.setup_apps(component):
            socketio.emit('update_status', {
                'status': 'failed',
                'message': 'Setup failed! Please check logs.',
                'progress': 0
            })
            return
        
        # Step 5: Shutdown loading servers and restart services
        socketio.emit('update_status', {
            'status': 'restarting',
            'message': 'Starting services...',
            'progress': 90
        })
        
        # Shutdown loading servers
        if frontend_loading_server:
            frontend_loading_server.shutdown()
            frontend_loading_server.server_close()
        
        if backend_loading_server:
            backend_loading_server.shutdown()
            backend_loading_server.server_close()
        
        time.sleep(2)
        
        # Start services (skip setup since we just did it)
        agent.start_all(skip_setup=True)
        
        # Wait for services to start
        time.sleep(5)
        
        # Step 6: Completed
        socketio.emit('update_status', {
            'status': 'completed',
            'message': 'Update completed successfully!',
            'progress': 100
        })
        
    except Exception as e:
        # Cleanup loading servers on error
        try:
            if 'frontend_loading_server' in locals() and frontend_loading_server:
                frontend_loading_server.shutdown()
                frontend_loading_server.server_close()
        except:
            pass
        
        try:
            if 'backend_loading_server' in locals() and backend_loading_server:
                backend_loading_server.shutdown()
                backend_loading_server.server_close()
        except:
            pass
            
        socketio.emit('update_status', {
            'status': 'failed',
            'message': f'Update failed: {str(e)}',
            'progress': 0
        })

# ============================================================================
# Log Management API Endpoints
# ============================================================================

@app.route('/api/logs')
def api_get_logs():
    """Get log entries from buffer"""
    action = request.args.get('action')
    limit = request.args.get('limit', type=int)
    
    logs = log_manager.get_logs(action=action, limit=limit)
    
    return jsonify({
        'success': True,
        'logs': logs,
        'count': len(logs),
        'current_action': log_manager.get_current_action()
    })

@app.route('/api/logs/download')
def api_download_logs():
    """Download full log file"""
    from flask import send_file
    
    if not log_manager.log_file or not log_manager.log_file.exists():
        return jsonify({
            'success': False,
            'error': 'Log file not found'
        }), 404
    
    return send_file(
        log_manager.log_file,
        mimetype='text/plain',
        as_attachment=True,
        download_name='4paws-agent.log'
    )

@app.route('/api/logs/clear', methods=['POST'])
def api_clear_logs():
    """Clear log buffer"""
    log_manager.clear_logs()
    return jsonify({
        'success': True,
        'message': 'Logs cleared successfully'
    })

@app.route('/api/logs/current-action')
def api_current_action():
    """Get currently running action"""
    action = log_manager.get_current_action()
    return jsonify({
        'success': True,
        'action': action
    })

# ============================================================================
# WebSocket Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'data': 'Connected to 4Paws Agent'})
    log_manager.info("🔌 New client connected to Web GUI")

@socketio.on('request_status')
def handle_status_request():
    """Send status update via WebSocket"""
    status = api_status().get_json()
    emit('status_update', status)

def run_auto_install():
    """
    Run auto-installation in background thread
    This is called when apps are not installed yet
    """
    install_server = get_installation_server(port=3100)
    
    def progress_callback(progress, step=None, status=None, title=None, description=None):
        """Send progress updates to installation page"""
        install_server.send_progress(progress, step, status, title, description)
    
    def log_callback(message, level='info'):
        """Send log messages to installation page"""
        install_server.send_log(message, level)
    
    # Wait a bit for server to start
    time.sleep(2)
    
    # Run installation
    log_callback("🚀 Starting first-time installation...", "info")
    success = agent.auto_install_and_setup(progress_callback, log_callback)
    
    if success:
        log_callback("✅ Installation completed successfully!", "success")
        install_server.send_complete()
        
        # Wait a bit before stopping installation server
        time.sleep(3)
        
        # Stop installation server
        stop_installation_server()
        log_manager.success("✅ First-time installation complete! Frontend now running on port 3100")
    else:
        log_callback("❌ Installation failed. Please check logs.", "error")
        log_manager.error("❌ Auto-installation failed")

def start_server(port=None):
    """Start the Flask server"""
    if port is None:
        port = find_available_port(5000)
    
    # Check if this is first-time installation
    if not agent.are_apps_installed():
        print(f"""
╔════════════════════════════════════════╗
║   4Paws First-Time Installation       ║
║   Please Wait...                      ║
╚════════════════════════════════════════╝

🚀 Apps not detected - starting auto-installation
📦 User access: http://localhost:3100 (Installation Progress)
🔧 Admin access: http://localhost:{port} (Maintenance GUI)

This will take 5-10 minutes...
Opening browser in 2 seconds...
""")
        
        # Start installation server on port 3100
        log_manager.info("🚀 Starting installation server on port 3100...")
        start_installation_server(port=3100)
        time.sleep(1)
        
        # Open browser to installation page
        import webbrowser
        log_manager.info("🌐 Opening browser to http://localhost:3100...")
        time.sleep(1)
        webbrowser.open("http://localhost:3100")
        
        # Start auto-installation in background thread
        install_thread = threading.Thread(target=run_auto_install, daemon=True)
        install_thread.start()
        
        log_manager.info("✅ Installation server started. User can access: http://localhost:3100")
        log_manager.info(f"ℹ️  Maintenance GUI available at: http://localhost:{port}")
    else:
        print(f"""
╔════════════════════════════════════════╗
║   4Paws Agent Web GUI                 ║
║   Dashboard Server                    ║
╚════════════════════════════════════════╝

🌐 Web GUI running at: http://localhost:{port}
📊 Real-time monitoring enabled
🎨 Dark/Light mode available

Press Ctrl+C to stop the server
""")
    
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    start_server()

