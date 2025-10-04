// WebSocket connection (global for other scripts)
var socket = io();

// State
let currentLogService = 'agent';
let autoRefresh = true;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    refreshStatus();
    startAutoRefresh();
});

// WebSocket events
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('status_update', (data) => {
    updateStatus(data);
});

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon();
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const newTheme = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const theme = document.documentElement.getAttribute('data-theme');
    const icon = document.querySelector('.theme-icon');
    icon.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// Status Management
async function refreshStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateStatus(data);
    } catch (error) {
        console.error('Error fetching status:', error);
    }
}

function updateStatus(data) {
    // Update system metrics
    document.getElementById('cpu-usage').textContent = `${data.system.cpu.toFixed(1)}%`;
    document.getElementById('memory-usage').textContent = `${data.system.memory.toFixed(1)}%`;
    document.getElementById('disk-usage').textContent = `${data.system.disk.toFixed(1)}%`;
    
    // Update services (compact view)
    updateServiceStatusCompact('mariadb', data.mariadb, data.ports.mariadb);
    updateServiceStatusCompact('backend', data.backend, data.ports.backend, data.versions.backend);
    updateServiceStatusCompact('frontend', data.frontend, data.ports.frontend, data.versions.frontend);
    
    // Update paths (compact view)
    if (data.paths) {
        const frontendPathEl = document.getElementById('frontend-path-compact');
        const backendPathEl = document.getElementById('backend-path-compact');
        const mariadbPathEl = document.getElementById('mariadb-path-compact');
        
        if (frontendPathEl) frontendPathEl.textContent = `📁 ${data.paths.frontend}`;
        if (backendPathEl) backendPathEl.textContent = `📁 ${data.paths.backend}`;
        if (mariadbPathEl) mariadbPathEl.textContent = `📁 ${data.paths.mariadb}`;
    }
}

// Update compact service status
function updateServiceStatusCompact(service, status, port, version = null) {
    const statusBadge = document.getElementById(`${service}-status-mini`);
    const pidElement = document.getElementById(`${service}-pid-compact`);
    const cpuElement = document.getElementById(`${service}-cpu-compact`);
    const memoryElement = document.getElementById(`${service}-memory-compact`);
    
    if (!statusBadge) return; // Element not found, skip
    
    if (status.running) {
        statusBadge.textContent = 'Running';
        statusBadge.className = 'status-badge-mini running';
        if (pidElement) pidElement.textContent = status.pid;
        if (cpuElement) cpuElement.textContent = `${status.cpu.toFixed(1)}%`;
        if (memoryElement) memoryElement.textContent = `${status.memory.toFixed(1)} MB`;
    } else {
        statusBadge.textContent = 'Stopped';
        statusBadge.className = 'status-badge-mini stopped';
        if (pidElement) pidElement.textContent = '--';
        if (cpuElement) cpuElement.textContent = '--';
        if (memoryElement) memoryElement.textContent = '--';
    }
    
    if (version) {
        const versionElement = document.getElementById(`${service}-version-compact`);
        if (versionElement) {
            versionElement.textContent = version.version || '--';
        }
    }
}

function updateServiceStatus(service, status, port, version = null) {
    const card = document.getElementById(`${service}-card`);
    const statusBadge = document.getElementById(`${service}-status`);
    const pidElement = document.getElementById(`${service}-pid`);
    const cpuElement = document.getElementById(`${service}-cpu`);
    const memoryElement = document.getElementById(`${service}-memory`);
    const portElement = document.getElementById(`${service}-port`);
    
    if (!card) return; // Element not found, skip
    
    if (status.running) {
        card.classList.add('service-running');
        card.classList.remove('service-stopped');
        statusBadge.textContent = 'Running';
        statusBadge.className = 'status-badge status-running';
        pidElement.textContent = status.pid;
        cpuElement.textContent = `${status.cpu.toFixed(1)}%`;
        memoryElement.textContent = `${status.memory.toFixed(1)} MB`;
    } else {
        card.classList.remove('service-running');
        card.classList.add('service-stopped');
        statusBadge.textContent = 'Stopped';
        statusBadge.className = 'status-badge status-stopped';
        pidElement.textContent = '--';
        cpuElement.textContent = '--';
        memoryElement.textContent = '--';
    }
    
    portElement.textContent = port;
    
    if (version) {
        const versionElement = document.getElementById(`${service}-version`);
        if (versionElement) {
            versionElement.textContent = version.version || '--';
        }
    }
}

// Service Control
async function startService(service) {
    showLoading(`Starting ${service}...`);
    try {
        const response = await fetch(`/api/start/${service}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${service} started successfully`, 'success');
            setTimeout(refreshStatus, 2000);
        } else {
            showNotification(`Failed to start ${service}: ${data.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        showNotification(`Error starting ${service}: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function stopService(service) {
    showLoading(`Stopping ${service}...`);
    try {
        const response = await fetch(`/api/stop/${service}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${service} stopped successfully`, 'success');
            setTimeout(refreshStatus, 1000);
        } else {
            showNotification(`Failed to stop ${service}: ${data.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        showNotification(`Error stopping ${service}: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function startAll() {
    await startService('all');
}

async function stopAll() {
    if (!confirm('Are you sure you want to stop all services?')) {
        return;
    }
    await stopService('all');
}

// Install Apps
async function installApp(component) {
    closeModal('installModal');
    showLoading(`Installing ${component}... This may take a few minutes.`);
    
    try {
        const response = await fetch(`/api/install/${component}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${component} installed successfully!`, 'success');
            setTimeout(refreshStatus, 2000);
        } else {
            showNotification(`Failed to install ${component}: ${data.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        showNotification(`Error installing ${component}: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// Setup Apps
async function setupApp(component) {
    closeModal('setupModal');
    showLoading(`Setting up ${component}... Installing dependencies and running migrations.`);
    
    try {
        const response = await fetch(`/api/setup/${component}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${component} setup completed successfully!`, 'success');
            setTimeout(refreshStatus, 2000);
        } else {
            showNotification(`Failed to setup ${component}: ${data.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        showNotification(`Error setting up ${component}: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// Seed Database
async function seedDatabase(type) {
    closeModal('seedModal');
    showLoading(`Seeding database with ${type} data...`);
    
    try {
        const response = await fetch('/api/seed', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type })
        });
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Database seeded with ${type} successfully!`, 'success');
        } else {
            showNotification(`Failed to seed database: ${data.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        showNotification(`Error seeding database: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// Updates
async function checkUpdates() {
    showLoading('Checking for updates...');
    try {
        const response = await fetch('/api/updates');
        const data = await response.json();
        
        if (data.updates && (data.updates.frontend || data.updates.backend)) {
            displayUpdates(data.updates);
        } else {
            showNotification('No updates available. Everything is up to date!', 'info');
        }
    } catch (error) {
        showNotification(`Error checking updates: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

function displayUpdates(updates) {
    const section = document.getElementById('updates-section');
    const content = document.getElementById('updates-content');
    
    let html = '<div class="updates-list">';
    
    if (updates.frontend) {
        html += `
            <div class="update-card">
                <h3>🎨 Frontend Update Available</h3>
                <p>Current: ${updates.frontend.current || 'Not installed'}</p>
                <p>Latest: ${updates.frontend.latest}</p>
                <button class="btn btn-primary" onclick="updateComponent('frontend')">Update Frontend</button>
            </div>
        `;
    }
    
    if (updates.backend) {
        html += `
            <div class="update-card">
                <h3>🔧 Backend Update Available</h3>
                <p>Current: ${updates.backend.current || 'Not installed'}</p>
                <p>Latest: ${updates.backend.latest}</p>
                <button class="btn btn-primary" onclick="updateComponent('backend')">Update Backend</button>
            </div>
        `;
    }
    
    html += `
        <div class="update-card">
            <h3>📦 Update All</h3>
            <button class="btn btn-success" onclick="updateComponent('all')">Update Everything</button>
        </div>
    </div>`;
    
    content.innerHTML = html;
    section.style.display = 'block';
}

async function updateComponent(component) {
    if (!confirm(`Are you sure you want to update ${component}? Services will be restarted.`)) {
        return;
    }
    
    showLoading(`Updating ${component}... This may take a few minutes.`);
    
    try {
        const response = await fetch(`/api/update/${component}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ force: true })
        });
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${component} updated successfully!`, 'success');
            document.getElementById('updates-section').style.display = 'none';
            setTimeout(refreshStatus, 2000);
        } else {
            showNotification(`Failed to update ${component}: ${data.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        showNotification(`Error updating ${component}: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// Logs
async function showLogs(service) {
    currentLogService = service;
    
    // Update tab active state
    document.querySelectorAll('.log-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Fetch logs
    try {
        const response = await fetch(`/api/logs/${service}`);
        const data = await response.json();
        document.getElementById('logs-output').textContent = data.logs || 'No logs available';
        
        // Auto-scroll to bottom
        const logsOutput = document.getElementById('logs-output');
        logsOutput.scrollTop = logsOutput.scrollHeight;
    } catch (error) {
        document.getElementById('logs-output').textContent = `Error loading logs: ${error.message}`;
    }
}

// Modal Management
function showInstallModal() {
    document.getElementById('installModal').style.display = 'flex';
}

function showSetupModal() {
    document.getElementById('setupModal').style.display = 'flex';
}

function showSeedModal() {
    document.getElementById('seedModal').style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Click outside modal to close
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Loading Indicator (in terminal instead of fullscreen)
function showLoading(text = 'Processing...') {
    // Add loading indicator to terminal
    const terminal = document.getElementById('logsTerminal');
    if (!terminal) return;
    
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'terminal-loading';
    loadingDiv.className = 'log-entry info';
    loadingDiv.innerHTML = `
        <span class="log-timestamp">[${getCurrentTime()}]</span>
        <span class="loading-spinner-inline">⏳</span>
        <span>${text}</span>
    `;
    terminal.appendChild(loadingDiv);
    
    // Auto-scroll
    terminal.scrollTop = terminal.scrollHeight;
}

function hideLoading() {
    // Remove loading indicator from terminal
    const loadingDiv = document.getElementById('terminal-loading');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

// Notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Show with animation
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Auto Refresh
function startAutoRefresh() {
    setInterval(() => {
        if (autoRefresh) {
            refreshStatus();
            if (currentLogService) {
                // Refresh logs silently
                fetch(`/api/logs/${currentLogService}`)
                    .then(r => r.json())
                    .then(data => {
                        const output = document.getElementById('logs-output');
                        const wasAtBottom = output.scrollHeight - output.scrollTop === output.clientHeight;
                        output.textContent = data.logs || 'No logs available';
                        if (wasAtBottom) {
                            output.scrollTop = output.scrollHeight;
                        }
                    })
                    .catch(() => {});
            }
        }
    }, 3000); // Refresh every 3 seconds
}

// External Links
function openFrontend() {
    window.open('http://localhost:3100', '_blank');
}

function openBackend() {
    window.open('http://localhost:3200', '_blank');
}
