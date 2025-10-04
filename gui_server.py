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

# Add agent.py to path
sys.path.insert(0, str(Path(__file__).parent))
from agent import Agent, ProcessManager, Config, VersionManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '4paws-agent-secret'
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
            success = agent.start_all(skip_setup=True)
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

