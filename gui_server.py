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
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Add agent.py to path
sys.path.insert(0, str(Path(__file__).parent))
from agent import Agent, ProcessManager, Config, VersionManager

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
            return jsonify({'success': False, 'error': f'Unknown service: {service}'}), 400
        
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop/<service>', methods=['POST'])
def api_stop(service):
    """Stop a service"""
    try:
        if service == 'all':
            agent.stop_all()
            return jsonify({'success': True})
        elif service in ['mariadb', 'backend', 'frontend']:
            if service in ProcessManager.processes:
                ProcessManager.processes[service].terminate()
                ProcessManager.processes[service].wait(timeout=10)
                del ProcessManager.processes[service]
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': f'Unknown service: {service}'}), 400
    except Exception as e:
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
        success = agent.install_apps(component)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/update/<component>', methods=['POST'])
def api_update(component):
    """Update frontend/backend/all"""
    try:
        # Get force flag from request
        data = request.get_json() or {}
        force = data.get('force', False)
        
        if component == 'all':
            success = agent.update_apps('all', force=force)
        else:
            success = agent.update_apps(component, force=force)
        
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/setup/<component>', methods=['POST'])
def api_setup(component):
    """Setup apps (install dependencies, migrate, etc)"""
    try:
        success = agent.setup_apps(component)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/seed', methods=['POST'])
def api_seed():
    """Seed database"""
    try:
        data = request.get_json() or {}
        seed_type = data.get('type', 'all')
        
        success = agent.seed_database(seed_type)
        return jsonify({'success': success})
    except Exception as e:
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
    """Check for updates (for application integration)"""
    try:
        versions = VersionManager.load_versions()
        updates = agent.check_updates()
        
        return jsonify({
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
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update/start', methods=['POST'])
def api_update_start():
    """Start update process (non-blocking with WebSocket notifications)"""
    try:
        data = request.get_json() or {}
        component = data.get('component', 'all')
        
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

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'data': 'Connected to 4Paws Agent'})

@socketio.on('request_status')
def handle_status_request():
    """Send status update via WebSocket"""
    status = api_status().get_json()
    emit('status_update', status)

def start_server(port=None):
    """Start the Flask server"""
    if port is None:
        port = find_available_port(5000)
    
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

