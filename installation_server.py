"""
Installation Server Module
Serves a beautiful installation progress page on port 3100 during first-time setup
"""

from flask import Flask, render_template_string
from flask_socketio import SocketIO
import threading
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class InstallationServer:
    """Serves installation progress page on port 3100 during first-time setup"""
    
    def __init__(self, port=3100):
        self.port = port
        self.app = None
        self.socketio = None
        self.server_thread = None
        self.is_running = False
        
    def create_app(self):
        """Create Flask app for installation page"""
        # Use the same static folder as main GUI
        static_folder = Path(__file__).parent / 'static'
        app = Flask(__name__, static_folder=str(static_folder))
        app.config['SECRET_KEY'] = 'installation-secret-key'
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        # Installation page HTML template
        INSTALL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>4Paws Installation</title>
    
    <!-- Favicons -->
    <link rel="icon" type="image/x-icon" href="/static/img/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/img/favicon-32x32.png">
    
    <!-- SocketIO -->
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            margin: 0;
            overflow: hidden;
        }
        
        .container {
            background: white;
            border-radius: 16px;
            padding: 32px;
            max-width: 580px;
            width: 100%;
            max-height: 90vh;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.5s ease-out;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .logo {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .logo-image {
            width: 64px;
            height: auto;
            margin-bottom: 12px;
            animation: fadeIn 0.8s ease-out;
        }
        
        .logo h1 {
            font-size: 24px;
            color: #667eea;
            margin-bottom: 6px;
            font-weight: 600;
        }
        
        .logo p {
            color: #666;
            font-size: 14px;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: scale(0.8);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        .status {
            text-align: center;
            margin-bottom: 16px;
        }
        
        .status h2 {
            color: #333;
            font-size: 16px;
            margin-bottom: 4px;
            font-weight: 600;
        }
        
        .status p {
            color: #999;
            font-size: 12px;
        }
        
        .progress-container {
            background: #f0f0f0;
            border-radius: 8px;
            height: 32px;
            overflow: hidden;
            margin-bottom: 16px;
            position: relative;
        }
        
        .progress-bar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            width: 0%;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 12px;
        }
        
        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: 600;
            font-size: 12px;
            color: #333;
            z-index: 1;
            text-shadow: 0 0 3px rgba(255, 255, 255, 0.8);
        }
        
        .logs-container {
            background: #1e1e1e;
            border-radius: 8px;
            padding: 12px;
            height: 180px;
            overflow-y: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 11px;
            line-height: 1.4;
            margin-bottom: 16px;
            flex-shrink: 0;
        }
        
        .log-entry {
            color: #d4d4d4;
            margin-bottom: 3px;
            white-space: pre-wrap;
            word-break: break-all;
        }
        
        .log-entry.info { color: #4fc3f7; }
        .log-entry.success { color: #81c784; }
        .log-entry.warning { color: #ffb74d; }
        .log-entry.error { color: #e57373; }
        
        .spinner {
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .steps {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            flex-shrink: 0;
        }
        
        .step {
            flex: 1;
            text-align: center;
            padding: 8px 6px;
            background: #f9f9f9;
            border-radius: 6px;
            border-bottom: 3px solid #ddd;
            transition: all 0.3s ease;
        }
        
        .step.active {
            border-bottom-color: #667eea;
            background: #f0f4ff;
        }
        
        .step.completed {
            border-bottom-color: #81c784;
            background: #f1f8f4;
        }
        
        .step .icon {
            font-size: 18px;
            margin-bottom: 4px;
            display: block;
        }
        
        .step .text h3 {
            font-size: 11px;
            color: #333;
            margin: 0;
            font-weight: 600;
            line-height: 1.2;
        }
        
        .footer {
            text-align: center;
            color: #999;
            font-size: 10px;
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid #eee;
            flex-shrink: 0;
        }
        
        .completion-message {
            display: none;
            text-align: center;
            padding: 16px;
            background: #f1f8f4;
            border-radius: 8px;
            border-left: 3px solid #81c784;
            margin-bottom: 16px;
        }
        
        .completion-message.show {
            display: block;
            animation: slideIn 0.5s ease-out;
        }
        
        .completion-message h3 {
            color: #2e7d32;
            font-size: 16px;
            margin-bottom: 6px;
            font-weight: 600;
        }
        
        .completion-message p {
            color: #666;
            font-size: 12px;
        }
        
        /* Scrollbar styling */
        .logs-container::-webkit-scrollbar {
            width: 6px;
        }
        
        .logs-container::-webkit-scrollbar-track {
            background: #2d2d2d;
            border-radius: 3px;
        }
        
        .logs-container::-webkit-scrollbar-thumb {
            background: #555;
            border-radius: 3px;
        }
        
        .logs-container::-webkit-scrollbar-thumb:hover {
            background: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="/static/img/4-PAWS-Petcare.png" alt="4Paws Logo" class="logo-image">
            <h1>4Paws Installation</h1>
            <p>Setting up your pet management system...</p>
        </div>
        
        <div class="completion-message" id="completionMessage">
            <h3>✨ Installation Complete!</h3>
            <p>Redirecting to your application in a few seconds...</p>
        </div>
        
        <div class="status">
            <div class="spinner" id="spinner"></div>
            <h2 id="statusTitle">Initializing Installation...</h2>
            <p id="statusDescription">Please wait while we set everything up</p>
        </div>
        
        <div class="progress-container">
            <div class="progress-bar" id="progressBar"></div>
            <div class="progress-text" id="progressText">0%</div>
        </div>
        
        <div class="steps" id="steps">
            <div class="step" data-step="download">
                <div class="icon">⏳</div>
                <div class="text">
                    <h3>Download</h3>
                </div>
            </div>
            <div class="step" data-step="install">
                <div class="icon">⏳</div>
                <div class="text">
                    <h3>Install</h3>
                </div>
            </div>
            <div class="step" data-step="database">
                <div class="icon">⏳</div>
                <div class="text">
                    <h3>Database</h3>
                </div>
            </div>
            <div class="step" data-step="start">
                <div class="icon">⏳</div>
                <div class="text">
                    <h3>Start</h3>
                </div>
            </div>
        </div>
        
        <div class="logs-container" id="logsContainer">
            <div class="log-entry info">[--:--:--] 🚀 Installation starting...</div>
        </div>
        
        <div class="footer">
            <p>4Paws Management System • First-Time Setup</p>
        </div>
    </div>
    
    <script>
        const socket = io();
        const logsContainer = document.getElementById('logsContainer');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const statusTitle = document.getElementById('statusTitle');
        const statusDescription = document.getElementById('statusDescription');
        const spinner = document.getElementById('spinner');
        const completionMessage = document.getElementById('completionMessage');
        
        let currentProgress = 0;
        
        // Listen for installation logs
        socket.on('installation_log', function(data) {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${data.level || 'info'}`;
            logEntry.textContent = data.message;
            logsContainer.appendChild(logEntry);
            
            // Auto-scroll to bottom
            logsContainer.scrollTop = logsContainer.scrollHeight;
        });
        
        // Listen for progress updates
        socket.on('installation_progress', function(data) {
            currentProgress = data.progress;
            progressBar.style.width = currentProgress + '%';
            progressText.textContent = currentProgress + '%';
            
            if (data.step) {
                updateStep(data.step, data.status || 'active');
            }
            
            if (data.title) {
                statusTitle.textContent = data.title;
            }
            
            if (data.description) {
                statusDescription.textContent = data.description;
            }
        });
        
        // Listen for completion
        socket.on('installation_complete', function(data) {
            currentProgress = 100;
            progressBar.style.width = '100%';
            progressText.textContent = '100%';
            
            statusTitle.textContent = '✨ Installation Complete!';
            statusDescription.textContent = 'Your system is ready. Redirecting...';
            
            spinner.style.display = 'none';
            completionMessage.classList.add('show');
            
            // Mark all steps as completed
            document.querySelectorAll('.step').forEach(step => {
                step.classList.add('completed');
                step.querySelector('.icon').textContent = '✅';
            });
            
            // Auto-refresh after 3 seconds
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        });
        
        function updateStep(stepName, status) {
            const step = document.querySelector(`.step[data-step="${stepName}"]`);
            if (!step) return;
            
            // Remove all status classes
            step.classList.remove('active', 'completed');
            
            if (status === 'active') {
                step.classList.add('active');
                step.querySelector('.icon').textContent = '🔄';
            } else if (status === 'completed') {
                step.classList.add('completed');
                step.querySelector('.icon').textContent = '✅';
            }
        }
        
        // Connection status
        socket.on('connect', function() {
            console.log('Connected to installation server');
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from installation server');
        });
    </script>
</body>
</html>
        """
        
        @app.route('/')
        def installation_page():
            """Serve the installation progress page"""
            return render_template_string(INSTALL_TEMPLATE)
        
        return app, socketio
    
    def start(self):
        """Start the installation server"""
        if self.is_running:
            logger.warning("Installation server is already running")
            return
        
        try:
            self.app, self.socketio = self.create_app()
            self.is_running = True
            
            # Run in separate thread
            def run_server():
                logger.info(f"🚀 Starting installation server on port {self.port}")
                # Disable Flask's request logging
                import logging as flask_logging
                flask_logging.getLogger('werkzeug').setLevel(flask_logging.ERROR)
                
                self.socketio.run(
                    self.app,
                    host='127.0.0.1',
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    allow_unsafe_werkzeug=True
                )
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            logger.info(f"✅ Installation server started on http://localhost:{self.port}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start installation server: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop the installation server"""
        if not self.is_running:
            return
        
        try:
            logger.info("🛑 Stopping installation server...")
            
            # Send shutdown signal to Flask
            if self.socketio:
                self.socketio.stop()
            
            self.is_running = False
            logger.info("✅ Installation server stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping installation server: {e}")
    
    def send_log(self, message, level='info'):
        """Send a log message to connected clients"""
        if self.socketio and self.is_running:
            self.socketio.emit('installation_log', {
                'message': message,
                'level': level
            })
    
    def send_progress(self, progress, step=None, status=None, title=None, description=None):
        """Send progress update to connected clients"""
        if self.socketio and self.is_running:
            data = {'progress': progress}
            if step:
                data['step'] = step
            if status:
                data['status'] = status
            if title:
                data['title'] = title
            if description:
                data['description'] = description
            
            self.socketio.emit('installation_progress', data)
    
    def send_complete(self):
        """Send installation complete signal"""
        if self.socketio and self.is_running:
            self.socketio.emit('installation_complete', {})

# Global installation server instance
_installation_server = None

def get_installation_server(port=3100):
    """Get or create the global installation server instance"""
    global _installation_server
    if _installation_server is None:
        _installation_server = InstallationServer(port)
    return _installation_server

def start_installation_server(port=3100):
    """Start the installation server"""
    server = get_installation_server(port)
    server.start()
    return server

def stop_installation_server():
    """Stop the installation server"""
    global _installation_server
    if _installation_server:
        _installation_server.stop()
        _installation_server = None

