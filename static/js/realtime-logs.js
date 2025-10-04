/**
 * Real-Time Logs JavaScript
 * Handles WebSocket connection and log display
 */

// Use global socket from app.js (don't create new one)
let autoScroll = true;
let logs = [];
let currentFilter = '';
const actions = new Set();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeRealtimeLogs();
});

function initializeRealtimeLogs() {
    // Check if socket exists (from app.js)
    if (typeof socket === 'undefined') {
        console.error('Socket.io not loaded!');
        addSystemLog('❌ Failed to connect - Socket.io not available');
        return;
    }
    
    // Connection handling
    socket.on('connect', () => {
        console.log('✅ Connected to agent (realtime-logs)');
        addSystemLog('✅ Connected to agent');
        loadExistingLogs();
    });
    
    socket.on('disconnect', () => {
        console.log('❌ Disconnected from agent');
        addSystemLog('❌ Disconnected from agent. Reconnecting...');
    });
    
    socket.on('log_entry', (data) => {
        addLogEntry(data);
    });
    
    // Apply theme
    applyTerminalTheme();
}

// Add system log
function addSystemLog(message) {
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const entry = {
        timestamp: timestamp,
        level: 'info',
        message: message,
        full_text: `[${timestamp}] ${message}`
    };
    addLogEntry(entry);
}

// Load existing logs from server
async function loadExistingLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        
        if (data.success) {
            logs = data.logs;
            renderLogs();
            
            // Update action filter
            data.logs.forEach(log => {
                if (log.action) actions.add(log.action);
            });
            updateActionFilter();
        }
    } catch (error) {
        console.error('Failed to load logs:', error);
    }
}

// Add log entry
function addLogEntry(entry) {
    logs.push(entry);
    
    // Add action to filter
    if (entry.action && !actions.has(entry.action)) {
        actions.add(entry.action);
        updateActionFilter();
    }
    
    // Render if matches filter
    if (!currentFilter || entry.action === currentFilter) {
        appendLogToDOM(entry);
    }
}

// Append log to DOM
function appendLogToDOM(entry) {
    const terminal = document.getElementById('logsTerminal');
    const logDiv = document.createElement('div');
    logDiv.className = `log-entry ${entry.level}`;
    
    let html = `<span class="log-timestamp">[${entry.timestamp}]</span>`;
    if (entry.action) {
        html += `<span class="log-action-tag">${entry.action}</span>`;
    }
    html += `<span>${entry.message}</span>`;
    
    logDiv.innerHTML = html;
    terminal.appendChild(logDiv);
    
    // Auto-scroll
    if (autoScroll) {
        terminal.scrollTop = terminal.scrollHeight;
    }
}

// Render all logs
function renderLogs() {
    const terminal = document.getElementById('logsTerminal');
    terminal.innerHTML = '';
    
    const filteredLogs = currentFilter 
        ? logs.filter(log => log.action === currentFilter)
        : logs;
    
    filteredLogs.forEach(entry => appendLogToDOM(entry));
}

// Update action filter dropdown
function updateActionFilter() {
    const filterSelect = document.getElementById('actionFilter');
    const currentValue = filterSelect.value;
    
    filterSelect.innerHTML = '<option value="">All Actions</option>';
    Array.from(actions).sort().forEach(action => {
        const option = document.createElement('option');
        option.value = action;
        option.textContent = action;
        if (action === currentValue) option.selected = true;
        filterSelect.appendChild(option);
    });
}

// Filter logs by action
function filterLogs() {
    currentFilter = document.getElementById('actionFilter').value;
    renderLogs();
}

// Toggle auto-scroll
function toggleAutoScroll() {
    autoScroll = !autoScroll;
    const icon = document.getElementById('autoScrollIcon');
    icon.textContent = autoScroll ? '📌' : '📍';
    
    if (autoScroll) {
        const terminal = document.getElementById('logsTerminal');
        terminal.scrollTop = terminal.scrollHeight;
    }
}

// Clear logs
async function clearLogs() {
    if (!confirm('Are you sure you want to clear all logs?')) return;
    
    try {
        const response = await fetch('/api/logs/clear', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            logs = [];
            document.getElementById('logsTerminal').innerHTML = '';
            addSystemLog('🗑️ Logs cleared');
        }
    } catch (error) {
        alert('Failed to clear logs: ' + error.message);
    }
}

// Apply theme to terminal
function applyTerminalTheme() {
    const terminal = document.getElementById('logsTerminal');
    if (!terminal) return;
    
    const theme = localStorage.getItem('theme') || 'dark';
    
    if (theme === 'light') {
        terminal.classList.add('light');
    } else {
        terminal.classList.remove('light');
    }
}

// Export functions for global access
window.filterLogs = filterLogs;
window.toggleAutoScroll = toggleAutoScroll;
window.clearLogs = clearLogs;

