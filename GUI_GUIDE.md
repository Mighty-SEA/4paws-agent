# 4Paws Agent Web GUI & System Tray Guide

## 🎨 Overview

The 4Paws Agent now includes a modern Web GUI and System Tray application for easy management of your deployment.

## 📦 Features

### Web GUI (Dashboard)
- ✅ **Real-time Monitoring** - Live status of all services
- ✅ **Service Control** - Start/Stop individual services or all at once
- ✅ **Dark/Light Mode** - Toggle between themes
- ✅ **System Metrics** - CPU, Memory, and Disk usage
- ✅ **Logs Viewer** - View service logs in real-time
- ✅ **Update Checker** - Check for new releases from GitHub
- ✅ **Auto-refresh** - Status updates every 5 seconds

### System Tray
- ✅ **Quick Actions** - Right-click menu for common tasks
- ✅ **Notifications** - System notifications for important events
- ✅ **Background Running** - Minimized to system tray
- ✅ **Auto-start** - Option to start with Windows
- ✅ **Status Indicator** - Icon color shows service status

## 🚀 Quick Start

### Method 1: System Tray (Recommended)
```bash
python tray_app.py
```

**What happens:**
1. System tray icon appears (🐾)
2. Web GUI server starts automatically
3. Right-click icon for menu

**Menu Options:**
- 🌐 Open Web GUI - Opens dashboard in browser
- ▶️ Start All Services - Starts MariaDB, Backend, Frontend
- ⏹️ Stop All Services - Stops all running services
- 🎨 Open Frontend - Opens frontend app (http://localhost:3100)
- 🔧 Open Backend API - Opens backend API (http://localhost:3200)
- 🔄 Check Updates - Check for new releases
- ❌ Quit - Exit the tray app

### Method 2: Web GUI Only
```bash
python gui_server.py
```

**Features:**
- Runs on http://localhost:5000 (auto-detects if 5000 is busy)
- If port 5000 is taken, tries 5001, 5002, etc.
- Access from any browser on the same network

## 🖥️ Web GUI Interface

### Dashboard Layout

```
┌────────────────────────────────────────────────────┐
│ 🐾 4Paws Agent Dashboard        🌙 Refresh         │
├────────────────────────────────────────────────────┤
│ CPU: 5.2%    Memory: 45%    Disk: 60%             │
├────────────────────────────────────────────────────┤
│ [▶️ Start All] [⏹️ Stop All] [🔄 Check Updates]   │
├────────────────────────────────────────────────────┤
│ ┌────────────┐ ┌────────────┐ ┌────────────┐     │
│ │ MariaDB    │ │ Backend    │ │ Frontend   │     │
│ │ Status: ●  │ │ Status: ●  │ │ Status: ●  │     │
│ │ Port: 3307 │ │ Port: 3200 │ │ Port: 3100 │     │
│ │ CPU: 2.1%  │ │ CPU: 3.5%  │ │ CPU: 4.2%  │     │
│ │ Mem: 50MB  │ │ Mem: 120MB │ │ Mem: 80MB  │     │
│ │ [Start]... │ │ [Start]... │ │ [Start]... │     │
│ └────────────┘ └────────────┘ └────────────┘     │
└────────────────────────────────────────────────────┘
```

### Theme Toggle
- Click 🌙/☀️ icon in top-right
- Preference is saved to localStorage
- Smooth transitions between themes

### Service Cards
Each service shows:
- **Status Badge** - Green (●) = Running, Gray (●) = Stopped
- **Process ID** - PID of running process
- **Port** - Service port number
- **CPU Usage** - Real-time CPU percentage
- **Memory** - RAM usage in MB
- **Version** - Current installed version (Backend/Frontend only)

### Actions
- **Start** - Start individual service
- **Stop** - Stop individual service
- **Logs** - View service logs (last 100 lines)
- **Open** - Open frontend in new tab (Frontend only)

## 📊 Features Detail

### Real-time Monitoring
- WebSocket connection for instant updates
- Auto-refresh every 5 seconds
- Manual refresh button available

### Log Viewer
1. Click **Logs** button on any service card
2. Modal opens with last 100 lines
3. Formatted with syntax colors
4. Scrollable content

### Update Checker
1. Click **Check Updates** button
2. Fetches latest releases from GitHub
3. Shows available updates with version numbers
4. Instructions to install updates via CLI

### Notifications
- Success messages (green)
- Error messages (red)
- Info messages (blue)
- Auto-dismiss after 3 seconds

## ⚙️ Configuration

### Change Web GUI Port
By default, the Web GUI auto-detects available ports starting from 5000.

To force a specific port:
```python
# In gui_server.py, change:
start_server(port=5000)  # Your desired port
```

### Auto-start on Windows
To make the tray app start with Windows:

1. Press `Win + R`
2. Type `shell:startup` and press Enter
3. Create shortcut to `tray_app.py`:
   - Right-click → New → Shortcut
   - Target: `pythonw.exe C:\path\to\4paws-agent\tray_app.py`
   - Name: `4Paws Agent`

**Note:** Use `pythonw.exe` (not `python.exe`) to run without console window.

### Custom Icon Colors
Edit `tray_app.py` to change icon colors:
```python
# In create_icon_image() method:
fill = (255, 255, 255, 255)  # White
fill = (46, 204, 113, 255)   # Green (running)
fill = (149, 165, 166, 255)  # Gray (stopped)
```

## 🔧 Troubleshooting

### Port Already in Use
**Problem:** Port 5000 is already taken

**Solution:** The server automatically finds next available port (5001, 5002, etc.)

### Services Won't Start from GUI
**Problem:** Services fail to start via Web GUI

**Solution:**
1. Check if `node_modules` are installed
2. Run `python agent.py setup-apps` first
3. Check logs for errors

### Tray Icon Not Showing
**Problem:** System tray icon doesn't appear

**Solution:**
1. Check Windows notification settings
2. Restart `explorer.exe` process
3. Run as Administrator if needed

### Theme Not Saving
**Problem:** Dark/Light mode resets on page reload

**Solution:**
1. Check browser localStorage is enabled
2. Clear browser cache and try again

## 🎯 Tips & Best Practices

### For Development
- Use Web GUI for detailed monitoring
- Check logs frequently during development
- Use system tray for quick start/stop

### For Production
- Set tray app to auto-start
- Monitor system metrics regularly
- Check updates weekly

### Remote Access
Web GUI is accessible from other devices on the same network:
```
http://<your-ip>:5000
```

Find your IP:
```bash
ipconfig  # Windows
```

## 📝 API Endpoints

The Web GUI uses these API endpoints (for custom integrations):

- `GET /api/status` - Get service status
- `POST /api/start/<service>` - Start service (all/mariadb/backend/frontend)
- `POST /api/stop/<service>` - Stop service
- `GET /api/updates` - Check for updates
- `GET /api/logs/<service>` - Get service logs

Example:
```bash
curl http://localhost:5000/api/status
```

## 🔐 Security Notes

- Web GUI runs on localhost by default
- No authentication required (local use)
- For remote access, consider:
  - Using reverse proxy (nginx)
  - Adding basic auth
  - Using HTTPS

## 📱 Mobile Access

Access the Web GUI from mobile devices:
1. Connect to same WiFi network
2. Open browser
3. Navigate to `http://<pc-ip>:5000`
4. Enjoy mobile-responsive interface

## 🆘 Support

For issues or questions:
1. Check logs: `logs/agent.log`
2. Review this guide
3. Check GitHub Issues

---

**Enjoy your new Web GUI! 🎉**

