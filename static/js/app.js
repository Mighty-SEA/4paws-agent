// WebSocket connection
const socket = io();

// Theme Management
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update icon
    const icon = document.querySelector('.theme-icon');
    icon.textContent = newTheme === 'dark' ? '🌙' : '☀️';
}

// Load saved theme
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const icon = document.querySelector('.theme-icon');
    icon.textContent = savedTheme === 'dark' ? '🌙' : '☀️';
}

// Notification
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification show ${type}`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Refresh Status
async function refreshStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        showNotification('Failed to fetch status', 'error');
    }
}

// Update UI with status data
function updateUI(data) {
    // Update system info
    document.getElementById('cpu-usage').textContent = data.system.cpu.toFixed(1) + '%';
    document.getElementById('memory-usage').textContent = data.system.memory.toFixed(1) + '%';
    document.getElementById('disk-usage').textContent = data.system.disk.toFixed(1) + '%';
    
    // Update services
    updateServiceCard('mariadb', data.mariadb, data.ports.mariadb, null);
    updateServiceCard('backend', data.backend, data.ports.backend, data.versions.backend.version);
    updateServiceCard('frontend', data.frontend, data.ports.frontend, data.versions.frontend.version);
}

// Update individual service card
function updateServiceCard(service, status, port, version) {
    const statusBadge = document.getElementById(`${service}-status`);
    const pidElement = document.getElementById(`${service}-pid`);
    const portElement = document.getElementById(`${service}-port`);
    const cpuElement = document.getElementById(`${service}-cpu`);
    const memoryElement = document.getElementById(`${service}-memory`);
    
    if (status.running) {
        statusBadge.className = 'status-badge running';
        pidElement.textContent = status.pid;
        cpuElement.textContent = status.cpu.toFixed(1) + '%';
        memoryElement.textContent = status.memory.toFixed(1) + ' MB';
    } else {
        statusBadge.className = 'status-badge stopped';
        pidElement.textContent = 'Not running';
        cpuElement.textContent = '--';
        memoryElement.textContent = '--';
    }
    
    portElement.textContent = port;
    
    if (version) {
        const versionElement = document.getElementById(`${service}-version`);
        if (versionElement) {
            versionElement.textContent = version;
        }
    }
}

// Start Service
async function startService(service) {
    try {
        const response = await fetch(`/api/start/${service}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${service} started successfully`, 'success');
            setTimeout(refreshStatus, 1000);
        } else {
            showNotification(`Failed to start ${service}: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification(`Error starting ${service}`, 'error');
    }
}

// Stop Service
async function stopService(service) {
    try {
        const response = await fetch(`/api/stop/${service}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${service} stopped successfully`, 'success');
            setTimeout(refreshStatus, 1000);
        } else {
            showNotification(`Failed to stop ${service}: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification(`Error stopping ${service}`, 'error');
    }
}

// Start All
async function startAll() {
    showNotification('Starting all services...', 'info');
    await startService('all');
}

// Stop All
async function stopAll() {
    showNotification('Stopping all services...', 'info');
    await stopService('all');
}

// View Logs
async function viewLogs(service) {
    const modal = document.getElementById('logs-modal');
    const title = document.getElementById('logs-title');
    const content = document.getElementById('logs-content');
    
    title.textContent = `${service.toUpperCase()} Logs`;
    content.textContent = 'Loading logs...';
    modal.classList.add('show');
    
    try {
        const response = await fetch(`/api/logs/${service}`);
        const data = await response.json();
        
        if (data.logs) {
            content.textContent = data.logs || 'No logs available';
        } else {
            content.textContent = 'Error loading logs: ' + data.error;
        }
    } catch (error) {
        content.textContent = 'Error loading logs';
    }
}

// Close Logs Modal
function closeLogs() {
    document.getElementById('logs-modal').classList.remove('show');
}

// Check Updates
async function checkUpdates() {
    const modal = document.getElementById('updates-modal');
    const content = document.getElementById('updates-content');
    
    content.textContent = 'Checking for updates...';
    modal.classList.add('show');
    
    try {
        const response = await fetch('/api/updates');
        const data = await response.json();
        
        if (data.updates && Object.keys(data.updates).length > 0) {
            let html = '<div style="padding: 20px;">';
            html += '<h4 style="margin-bottom: 15px;">🆕 Updates Available:</h4>';
            
            for (const [component, version] of Object.entries(data.updates)) {
                html += `<div style="padding: 10px; background: var(--bg-secondary); border-radius: 8px; margin-bottom: 10px;">`;
                html += `<strong>${component}:</strong> Update to ${version}`;
                html += `</div>`;
            }
            
            html += '<p style="margin-top: 15px; color: var(--text-secondary);">Run <code>python agent.py update</code> to install updates.</p>';
            html += '</div>';
            content.innerHTML = html;
        } else {
            content.innerHTML = '<div style="padding: 20px; text-align: center;">✅ All services are up to date!</div>';
        }
    } catch (error) {
        content.textContent = 'Error checking updates: ' + error;
    }
}

// Close Updates Modal
function closeUpdates() {
    document.getElementById('updates-modal').classList.remove('show');
}

// Open Frontend App
function openApp() {
    window.open('http://localhost:3100', '_blank');
}

// WebSocket event handlers
socket.on('connect', () => {
    console.log('Connected to server');
    refreshStatus();
});

socket.on('status_update', (data) => {
    updateUI(data);
});

// Close modals on outside click
window.onclick = function(event) {
    const logsModal = document.getElementById('logs-modal');
    const updatesModal = document.getElementById('updates-modal');
    
    if (event.target === logsModal) {
        closeLogs();
    }
    if (event.target === updatesModal) {
        closeUpdates();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadTheme();
    refreshStatus();
    
    // Auto-refresh every 5 seconds
    setInterval(refreshStatus, 5000);
});

