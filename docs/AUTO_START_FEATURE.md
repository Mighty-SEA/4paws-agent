# 🚀 Auto-Start Feature - Automatic Service Startup

## 📋 Overview

Feature untuk automatically start all services (MariaDB, Backend, Frontend) saat agent dibuka, jika aplikasi sudah terinstall dan services belum berjalan.

## ✨ What's New

### Automatic Service Startup

**When**: Agent dibuka (GUI Server atau System Tray)
**Condition**: Apps installed AND services not running
**Action**: Auto-start MariaDB → Backend → Frontend

### User Experience

```
User opens agent (exe or script)
    ↓
Agent checks: Apps installed?
    ↓ Yes
Agent checks: Services running?
    ↓ No
🚀 Auto-starting services...
    ↓
✅ Services started automatically!
    ↓
User can access app immediately
```

## 🎯 Implementation

### 1. GUI Server (`gui_server.py`)

**Auto-start logic:**

```python
def start_server(port=None):
    # ... port setup ...
    
    # Check if apps installed
    if not agent.are_apps_installed():
        # First-time installation flow
        start_installation_server(port=3100)
        # ...
    else:
        # Apps installed - check if services running
        if not any(key in ProcessManager.processes for key in ['mariadb', 'backend', 'frontend']):
            print("🚀 Starting services automatically...")
            log_manager.info("🚀 Auto-starting services...")
            
            # Start in background thread
            def auto_start():
                time.sleep(2)  # Wait for GUI to initialize
                try:
                    if agent.start_all(skip_setup=True):
                        log_manager.info("✅ All services started!")
                        print("✅ All services started!")
                        print(f"🌐 Frontend: http://localhost:{Config.FRONTEND_PORT}")
                        print(f"🌐 Backend: http://localhost:{Config.BACKEND_PORT}")
                    else:
                        log_manager.warning("⚠️  Some services failed to start")
                except Exception as e:
                    log_manager.error(f"❌ Auto-start failed: {e}")
            
            start_thread = threading.Thread(target=auto_start, daemon=True)
            start_thread.start()
        else:
            print("✅ Services already running")
    
    # Start Flask server
    socketio.run(app, ...)
```

**Key Points:**
- Checks if apps installed
- Checks if services already running
- Starts in background thread (non-blocking)
- 2-second delay for GUI initialization
- Logs all actions

### 2. System Tray (`tray_app.py`)

**Auto-start method:**

```python
def auto_start_services(self):
    """Auto-start services if apps installed and not running"""
    try:
        # Check if apps are installed
        if self.agent.are_apps_installed():
            # Check if services not already running
            if not any(key in ProcessManager.processes for key in ['mariadb', 'backend', 'frontend']):
                print("🚀 Auto-starting services...")
                
                # Start in background thread
                def start_services():
                    time.sleep(3)  # Wait for GUI server
                    try:
                        if self.agent.start_all(skip_setup=True):
                            self.update_icon_color("green")
                            self.show_notification("Services Started", 
                                                  "All services are running")
                            print("✅ Services started automatically")
                        else:
                            print("⚠️  Some services failed to start")
                    except Exception as e:
                        print(f"❌ Auto-start failed: {e}")
                
                start_thread = threading.Thread(target=start_services, daemon=True)
                start_thread.start()
            else:
                print("✅ Services already running")
                self.update_icon_color("green")
        else:
            print("📦 Apps not installed yet")
    except Exception as e:
        print(f"⚠️  Auto-start check failed: {e}")
```

**Called in `run()`:**

```python
def run(self):
    # Start Web GUI server
    self.start_gui_server()
    
    # Auto-start services
    self.auto_start_services()  # ← NEW!
    
    # Start auto-check updates
    self.start_auto_check()
    
    # Create tray icon
    self.icon = pystray.Icon(...)
    self.icon.run()
```

**Key Points:**
- Updates icon color to green on success
- Shows system notification
- 3-second delay for GUI server initialization
- Graceful error handling

## 🔍 Logic Flow

### Decision Tree

```
┌─────────────────────────┐
│ Agent Starts            │
└───────────┬─────────────┘
            │
            ▼
    ┌───────────────┐
    │ Apps installed? │
    └───────┬───────┘
            │
      ┌─────┴─────┐
      │           │
     Yes         No
      │           │
      ▼           ▼
┌──────────┐  ┌──────────────────┐
│ Services │  │ Start installation│
│ running? │  │ server            │
└────┬─────┘  └──────────────────┘
     │
┌────┴────┐
│         │
Yes       No
│         │
▼         ▼
┌─────────────┐  ┌──────────────┐
│ Show "running"│  │ Auto-start   │
│ Do nothing    │  │ services     │
└─────────────┘  └──────────────┘
```

### Startup Sequence

```
1. Agent starts
2. Check apps installed → YES
3. Check services running → NO
4. Print: "🚀 Starting services automatically..."
5. Wait 2-3 seconds (GUI initialization)
6. Start MariaDB
   └─ Wait 3 seconds (database ready)
7. Start Backend
   └─ Wait 2 seconds (API ready)
8. Start Frontend
   └─ Wait 1 second (app ready)
9. Update icon to green
10. Show notification
11. Print: "✅ All services started!"
12. Display URLs
```

## 📊 Console Output

### GUI Server Mode

```
╔════════════════════════════════════════╗
║   4Paws Agent Web GUI                 ║
║   Dashboard Server                    ║
╚════════════════════════════════════════╝

🌐 Web GUI running at: http://localhost:5000
📊 Real-time monitoring enabled
🎨 Dark/Light mode available

🚀 Starting services automatically...

✅ All services started successfully!
🌐 Frontend: http://localhost:3100
🌐 Backend: http://localhost:3200

Press Ctrl+C to stop the server
```

### System Tray Mode

```
╔════════════════════════════════════════╗
║   4Paws Agent System Tray             ║
║   Running in background               ║
╚════════════════════════════════════════╝

🐾 System tray icon active
🌐 Web GUI available
🔄 Auto-update check enabled (every 6 hours)
📊 First check in 30 seconds

🚀 Auto-starting services...
✅ Services started automatically

Right-click the tray icon for options
```

## 🎯 Benefits

### Before Auto-Start

**User workflow:**
```
1. Run agent
2. Open Web GUI (http://localhost:5000)
3. Click "Start All Services"
4. Wait for services to start
5. Access frontend (http://localhost:3100)
```

**Steps**: 5
**Time**: ~1-2 minutes
**Clicks**: 2-3 clicks

### After Auto-Start

**User workflow:**
```
1. Run agent
2. Access frontend (http://localhost:3100)
```

**Steps**: 2
**Time**: ~10-15 seconds
**Clicks**: 0 clicks (fully automatic)

### Improvements

✅ **Faster** - Services start immediately
✅ **Automatic** - No manual intervention
✅ **Convenient** - Ready to use instantly
✅ **User-friendly** - Just run and go
✅ **Consistent** - Always starts services
✅ **Smart** - Only starts if needed

## ⚙️ Configuration

### Disable Auto-Start (If Needed)

Currently auto-start is always enabled. To disable:

**Option 1: Comment out the code**

In `gui_server.py`:
```python
# Auto-start services if not already running
# if not any(...):
#     ... (comment out entire block)
```

In `tray_app.py`:
```python
# Auto-start services if apps are installed
# self.auto_start_services()  # Comment this line
```

**Option 2: Add config flag (Future)**

```python
# config.py
AUTO_START_SERVICES = True  # Set to False to disable

# gui_server.py
if Config.AUTO_START_SERVICES and not any(...):
    # Auto-start logic
```

## 🔧 Troubleshooting

### Services Not Auto-Starting

**Problem**: Agent runs but services don't start

**Check:**
1. Apps installed?
   ```bash
   # Check if apps/ folder exists
   dir apps
   ```

2. Services already running?
   ```bash
   # Check processes
   tasklist | findstr "node\|mariadb"
   ```

3. Check logs:
   ```bash
   type logs\agent.log
   type logs\agent_web.log
   ```

**Solutions:**
- Ensure apps are installed
- Stop existing services first
- Check logs for errors
- Try manual start

### Services Start But Fail

**Problem**: Auto-start runs but services fail

**Check:**
1. Port conflicts:
   ```bash
   netstat -ano | findstr ":3100 :3200 :3307"
   ```

2. Dependencies missing:
   ```bash
   # Check node_modules
   dir apps\frontend\node_modules
   dir apps\backend\node_modules
   ```

3. Database issues:
   ```bash
   # Check MariaDB data
   dir data\mariadb
   ```

**Solutions:**
- Kill processes using ports
- Run setup-apps if needed
- Check database connectivity
- Review error logs

### Auto-Start Too Slow

**Problem**: Takes long time to start

**Cause**: Sequential startup (MariaDB → Backend → Frontend)

**Current timing:**
- MariaDB: ~3 seconds
- Backend: ~2 seconds
- Frontend: ~1 second
- **Total**: ~6-8 seconds

**Future optimization:**
- Parallel startup (where possible)
- Faster health checks
- Cached dependencies

## 📝 Technical Details

### Threading

**Why background thread?**
- Non-blocking (GUI server starts immediately)
- Agent remains responsive
- Can show real-time progress
- Error handling isolated

**Thread details:**
```python
start_thread = threading.Thread(
    target=auto_start,
    daemon=True  # Dies with main program
)
start_thread.start()
```

### Delays

**Why delays?**
- GUI server needs time to initialize
- Database needs time to be ready
- API needs time to start
- Prevent race conditions

**Delay timings:**
- GUI Server: 2 seconds
- System Tray: 3 seconds (GUI + tray)
- MariaDB: 3 seconds (in agent.py)
- Backend: 2 seconds (in agent.py)
- Frontend: 1 second (in agent.py)

### Process Checking

**How to check if running?**

```python
# Check if any service is running
if not any(key in ProcessManager.processes for key in ['mariadb', 'backend', 'frontend']):
    # None running - start all
```

**Alternative check:**
```python
# Check each service individually
mariadb_running = 'mariadb' in ProcessManager.processes
backend_running = 'backend' in ProcessManager.processes
frontend_running = 'frontend' in ProcessManager.processes

if not (mariadb_running and backend_running and frontend_running):
    # Some services missing - start all
```

## 🎨 User Experience

### First-Time User

```
Day 1:
User downloads 4PawsAgent.exe
User runs it
    ↓
Browser opens (installation page)
Auto-installation runs
Shortcuts created
    ↓
Installation complete!
User clicks desktop shortcut
    ↓
Frontend loads immediately ✅
```

### Returning User

```
Day 2+:
User runs 4PawsAgent.exe
    ↓
Services auto-start (5-10 seconds)
    ↓
User clicks desktop shortcut
    ↓
Frontend loads immediately ✅

OR

User just clicks desktop shortcut
(Agent already running in background)
    ↓
Frontend loads instantly ✅
```

### Power User

```
User keeps agent in system tray
Services always running
    ↓
User works on app
Agent auto-checks for updates
    ↓
Update available
User clicks update
    ↓
Services restart automatically
    ↓
Back to work ✅
```

## ✅ Summary

**What**: Auto-start services when agent opens
**When**: Apps installed, services not running
**How**: Background thread, non-blocking
**Why**: Better UX, faster access, convenience

**Benefits:**
- ✅ Zero manual steps
- ✅ Instant app access
- ✅ Automatic and smart
- ✅ User-friendly
- ✅ Always ready

**Implementation:**
- `gui_server.py` - Auto-start on server mode
- `tray_app.py` - Auto-start on tray mode
- Background threading
- Smart detection
- Graceful handling

**Result**: User just runs agent and everything works! 🚀

---

**Feature Added**: October 4, 2025

**Status**: IMPLEMENTED & READY! ✨

---

*Made with ❤️ by Mighty SEA Team*

