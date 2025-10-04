# 🚀 First-Time Installation System

## Overview

The 4Paws Agent now includes an **automatic first-time installation system** that provides a beautiful, user-friendly experience when setting up the application for the first time.

## How It Works

### 1. **Detection**
When the agent starts, it checks if frontend and backend applications are installed:
```python
if not agent.are_apps_installed():
    # Start first-time installation flow
```

### 2. **Installation Server (Port 3100)**
If apps are not installed, the agent:
- Starts a dedicated **Installation Page Server** on port **3100**
- This is the SAME port where the frontend will run later
- Users only need to remember ONE port: **3100**

### 3. **Installation Process**
The installation page shows:
- Real-time progress bar (0-100%)
- Step-by-step indicators:
  - ⏳ Downloading Applications
  - ⏳ Installing Dependencies
  - ⏳ Setting Up Database
  - ⏳ Starting Services
- Live log output (terminal-style)
- Status messages and descriptions

### 4. **Completion & Transition**
When installation completes:
- Installation server on port 3100 **stops**
- Frontend application **starts** on port 3100
- Page **auto-refreshes**
- User sees the actual frontend application!

## User Experience Flow

```
User Opens: http://localhost:3100
        ↓
  [No Apps Detected]
        ↓
┌─────────────────────────────────────┐
│  Installation Progress Page         │
│  (Port 3100)                        │
│                                     │
│  🐾 4Paws Installation              │
│  [████████░░░░░░] 45%              │
│                                     │
│  ✅ Downloading...                  │
│  🔄 Installing dependencies...      │
│  ⏳ Setting up database...          │
│                                     │
│  [Terminal logs...]                 │
└─────────────────────────────────────┘
        ↓
  [Installation Complete]
        ↓
  [Page Auto-Refresh]
        ↓
┌─────────────────────────────────────┐
│  Frontend Application               │
│  (Port 3100)                        │
│                                     │
│  🐾 4Paws Dashboard                 │
│  [Your actual application]          │
└─────────────────────────────────────┘
```

## Technical Architecture

### Components

1. **`installation_server.py`**
   - Flask server for installation progress page
   - WebSocket support for real-time updates
   - Beautiful gradient UI with animations
   - Terminal-style log viewer

2. **`agent.py` - `auto_install_and_setup()`**
   - Automated installation orchestrator
   - Downloads frontend & backend from GitHub
   - Installs dependencies (pnpm install)
   - Sets up database (migrations)
   - Starts all services
   - Progress reporting via callbacks

3. **`gui_server.py` - `start_server()`**
   - Detects if apps are installed
   - Starts installation server if needed
   - Runs auto-install in background thread
   - Maintains admin GUI on port 5000

### Port Usage

| Port | Purpose | When Active |
|------|---------|-------------|
| **3100** | Installation Page | During first-time setup |
| **3100** | Frontend Application | After installation complete |
| **3200** | Backend API | After installation complete |
| **3307** | MariaDB | Always (when agent running) |
| **5000** | Admin/Maintenance GUI | Always (agent dashboard) |

### Key Features

✅ **Single Port for Users**: Users only access port 3100
✅ **Auto-Detection**: Agent automatically detects first-time setup
✅ **Real-Time Progress**: WebSocket-based live updates
✅ **Beautiful UI**: Modern gradient design with animations
✅ **Terminal Logs**: See exactly what's happening
✅ **Auto-Refresh**: Seamless transition to frontend
✅ **Background Installation**: Non-blocking operation
✅ **Error Handling**: Clear error messages if something fails

## Installation Steps (Automated)

The system automatically performs these steps:

### Step 1: Download Applications (0-40%)
- Fetches latest frontend release from GitHub
- Fetches latest backend release from GitHub
- Downloads and extracts portable builds

### Step 2: Install Dependencies (40-60%)
- Runs `pnpm install` for backend
- Runs `pnpm install` for frontend
- Generates Prisma client

### Step 3: Setup Database (60-80%)
- Starts MariaDB
- Creates database schema
- Runs Prisma migrations

### Step 4: Start Services (80-100%)
- Starts MariaDB on port 3307
- Starts Backend on port 3200
- Starts Frontend on port 3100

## Installation Time

**Expected Duration**: 5-10 minutes
- Download: 1-2 minutes
- Dependencies: 3-5 minutes (depends on internet speed)
- Database: 30 seconds
- Starting: 30 seconds

## Admin Access During Installation

While installation is running:
- **User Access**: http://localhost:3100 (Installation Progress)
- **Admin Access**: http://localhost:5000 (Maintenance Dashboard)

The maintenance GUI (port 5000) allows admins to:
- View detailed logs
- Monitor system resources
- Check installation progress
- Access advanced controls

But regular users should just use port **3100**.

## After Installation

Once installation completes:
- User accesses: **http://localhost:3100** (Frontend App)
- Backend API: **http://localhost:3200**
- Admin GUI: **http://localhost:5000** (for maintenance)

## Error Handling

If installation fails:
- Error message shown on installation page
- Detailed logs available in admin GUI
- Agent logs written to `logs/agent.log`
- User can retry by restarting the agent

## Code Example

### Starting the Agent
```python
# gui_server.py
if not agent.are_apps_installed():
    # Start installation server on port 3100
    start_installation_server(port=3100)
    
    # Run auto-installation in background
    install_thread = threading.Thread(target=run_auto_install, daemon=True)
    install_thread.start()
```

### Progress Callbacks
```python
def progress_callback(progress, step, status, title, description):
    """Send progress updates to installation page"""
    install_server.send_progress(progress, step, status, title, description)

def log_callback(message, level):
    """Send log messages to installation page"""
    install_server.send_log(message, level)

# Run installation with callbacks
agent.auto_install_and_setup(progress_callback, log_callback)
```

### Installation Server
```python
# installation_server.py
server = InstallationServer(port=3100)
server.start()

# Send updates
server.send_progress(50, 'install', 'active', 
                    'Installing Dependencies', 
                    'Setting up packages...')
server.send_log('📦 Installing dependencies...', 'info')

# Complete
server.send_complete()
server.stop()
```

## WebSocket Events

### Client → Server
- `connect`: Initial connection

### Server → Client
- `installation_log`: Log message
  ```json
  {
    "message": "📥 Downloading frontend...",
    "level": "info"
  }
  ```
- `installation_progress`: Progress update
  ```json
  {
    "progress": 45,
    "step": "install",
    "status": "active",
    "title": "Installing Dependencies",
    "description": "Setting up packages..."
  }
  ```
- `installation_complete`: Installation finished
  ```json
  {}
  ```

## Customization

### Modify Progress Steps
Edit `installation_server.py` template:
```html
<div class="step" data-step="your-step">
    <div class="icon">⏳</div>
    <div class="text">
        <h3>Your Step Name</h3>
        <p>Step description</p>
    </div>
</div>
```

### Adjust Progress Percentages
Edit `agent.py` - `auto_install_and_setup()`:
```python
if progress_callback:
    progress_callback(50, 'your-step', 'active',
                    'Your Step Title',
                    'Your step description')
```

### Custom Styling
Edit `installation_server.py` - `<style>` section:
```css
body {
    background: linear-gradient(135deg, #your-color 0%, #your-color 100%);
}
```

## Testing

### Simulate First-Time Installation
```bash
# Remove apps to trigger first-time flow
rm -rf apps/backend
rm -rf apps/frontend

# Start agent
python gui_server.py

# Open browser
http://localhost:3100
```

### Monitor Progress
- Installation page: http://localhost:3100
- Admin dashboard: http://localhost:5000
- Terminal logs: Real-time agent output

## Troubleshooting

### Installation Page Not Loading
- Check if port 3100 is available
- Verify agent started successfully
- Check logs: `logs/agent.log`

### Installation Stuck
- Check internet connection (for GitHub downloads)
- Verify tools are installed (Node.js, pnpm, MariaDB)
- Check admin GUI (port 5000) for errors

### Auto-Refresh Not Working
- Wait 3 seconds after "Installation Complete"
- Manually refresh the page
- Check if frontend started successfully

### Installation Failed
- Check `logs/agent.log` for errors
- Verify all prerequisites installed
- Check GitHub API rate limits
- Retry installation

## Benefits

### For Users
✅ **Simple**: Just open http://localhost:3100
✅ **Visual**: See progress in real-time
✅ **Transparent**: Know exactly what's happening
✅ **Automatic**: No manual steps required
✅ **Seamless**: Smooth transition to app

### For Developers
✅ **Maintainable**: Modular code structure
✅ **Extensible**: Easy to add more steps
✅ **Debuggable**: Detailed logging
✅ **Testable**: Can simulate scenarios
✅ **Reusable**: Installation server can be used for updates too

## Future Enhancements

Potential improvements:
- [ ] Retry failed steps automatically
- [ ] Pause/Resume installation
- [ ] Installation speed optimization
- [ ] Pre-download verification
- [ ] Rollback on failure
- [ ] Installation profiles (minimal/full)
- [ ] Multi-language support
- [ ] Dark/Light theme toggle

## Summary

The First-Time Installation System provides:
- **Automatic detection** of new installations
- **Beautiful UI** on port 3100 showing progress
- **Real-time updates** via WebSocket
- **Seamless transition** to frontend app
- **Single port** for user access (3100)
- **Admin access** for troubleshooting (5000)

Users never need to access port 5000 - they just open **http://localhost:3100** and see either:
1. Installation progress (first time)
2. Frontend application (after setup)

Perfect! 🎉

