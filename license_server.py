"""
License Expired Server
Serves a simple page when license is expired
Similar to installation server but for license expiry
"""

from flask import Flask, render_template_string, jsonify
from pathlib import Path
import threading
import logging
import os
import sys
import subprocess

# Disable Flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# Global license info
license_info = {
    'valid': False,
    'reason': 'Expired',
    'expiry': None,
    'message': None,
    'support_email': 'support@yourcompany.com',
    'support_phone': '+62 xxx-xxx-xxxx'
}

# Restart callback
restart_callback = None

@app.route('/')
def index():
    """Serve license expired page"""
    html_file = Path(__file__).parent / 'license_expired.html'
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return render_template_string(html_content)

@app.route('/api/license-status')
def license_status():
    """API endpoint for license status"""
    return jsonify(license_info)

@app.route('/api/restart', methods=['POST'])
def restart_agent():
    """API endpoint to restart agent"""
    try:
        # Call restart callback if set
        if restart_callback:
            # Run in separate thread to not block response
            threading.Thread(target=restart_callback, daemon=True).start()
            return jsonify({
                'success': True,
                'message': 'Agent restart initiated'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Restart not available'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Global server instance
_server = None
_server_thread = None

def start_license_server(port=3100, license_data=None, on_restart=None):
    """Start the license expired server"""
    global _server, _server_thread, license_info, restart_callback
    
    if _server is not None:
        print(f"⚠️  License server already running on port {port}")
        return
    
    # Update license info if provided
    if license_data:
        license_info.update(license_data)
    
    # Set restart callback
    if on_restart:
        restart_callback = on_restart
    
    print(f"🔒 Starting license expired page on port {port}...")
    
    def run_server():
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    
    _server_thread = threading.Thread(target=run_server, daemon=True)
    _server_thread.start()
    
    print(f"✅ License page available at: http://localhost:{port}")

def stop_license_server():
    """Stop the license server"""
    global _server, _server_thread
    
    # Flask doesn't have easy way to stop, but daemon thread will die with main process
    _server = None
    _server_thread = None
    print("⏹️  License server stopped")

def update_license_info(license_data):
    """Update license information"""
    global license_info
    license_info.update(license_data)

if __name__ == '__main__':
    # Test server
    start_license_server(port=3100, license_data={
        'valid': False,
        'reason': 'License Expired',
        'expiry': '2025-01-31',
        'message': 'Your license expired on 2025-01-31. Please contact support to renew.',
        'support_email': 'support@4paws.com',
        'support_phone': '+62 812-3456-7890'
    })
    
    print("\n📱 Test the page at: http://localhost:3100")
    print("Press Ctrl+C to stop\n")
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️  Stopping server...")
        stop_license_server()

