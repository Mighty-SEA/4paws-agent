# 🚀 4Paws Quick Start Guide

## 📅 Last Updated: October 5, 2025

---

## ⚡ **Quick Start (3 Methods)**

### **Method 1: Tray App (Recommended for Users)**
```cmd
# Double-click this file:
start-tray.bat

# OR from command line:
cd C:\Users\Habiburrahman\Documents\4paws\4paws-agent
start-tray.bat
```

**What it does:**
- ✅ Opens system tray app
- ✅ Auto-starts agent server (port 5000)
- ✅ Auto-starts frontend (port 3100)
- ✅ Auto-starts backend (port 3200)
- ✅ Shows status in system tray
- ✅ Easy stop/start from tray menu

### **Method 2: All-in-One Script**
```cmd
# Double-click this file:
start-all.bat

# OR from command line:
cd C:\Users\Habiburrahman\Documents\4paws\4paws-agent
start-all.bat
```

**What it does:**
- ✅ Starts agent server in separate window
- ✅ Auto-starts frontend & backend
- ✅ Opens browser to http://localhost:3100
- ✅ Shows all service URLs

### **Method 3: Manual (For Developers)**
```cmd
# Start agent server
cd C:\Users\Habiburrahman\Documents\4paws\4paws-agent
python gui_server.py

# Agent will automatically start:
# - Frontend on port 3100
# - Backend on port 3200
# - MariaDB on port 3307
```

---

## 🎯 **Access Points**

After starting, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3100 | Main application (user interface) |
| **Backend API** | http://localhost:3200 | REST API endpoints |
| **Agent GUI** | http://localhost:5000 | Management dashboard |

---

## 🔧 **Update Button Fix**

### **Problem**: Update button (🔄) tidak bekerja

### **Root Cause**: Agent server tidak running!

### **Solution**:

1. **Start agent server** using one of the methods above
2. **Verify** agent is running:
   - Open http://localhost:5000/api/status
   - Should see JSON response (not error)
3. **Refresh** frontend page
4. **Click** update button (🔄)

### **Visual Indicators**:

| Icon | Status | Meaning |
|------|--------|---------|
| 🔄 | Green/Gray | Agent online, no updates |
| 🔄 + 🔴 | Orange + pulsing | Update available! |
| ⚠️ + ⚫ | Red + gray dot | Agent OFFLINE |
| ⏳ | Spinning | Checking for updates... |

### **If update button shows ⚠️ (Warning)**:
```
This means agent server is NOT running!

Fix:
1. Open: C:\Users\Habiburrahman\Documents\4paws\4paws-agent
2. Run: start-all.bat
   OR: python gui_server.py
3. Wait 5 seconds
4. Refresh browser
5. Button should now show 🔄
```

---

## 🐛 **Troubleshooting**

### **Issue 1: Port Already in Use**
```
Error: Address already in use (port 3100/3200/5000)
```

**Solution**:
```cmd
# Kill all Python processes
taskkill /F /IM python.exe

# Then restart
start-all.bat
```

### **Issue 2: Frontend Shows Error Page**
```
This usually means frontend is not built or not running
```

**Solution**:
```cmd
cd C:\Users\Habiburrahman\Documents\4paws\4paws-frontend
pnpm install
pnpm build
pnpm start
```

### **Issue 3: Backend API Not Responding**
```
Check backend logs
```

**Solution**:
```cmd
# View backend logs
type C:\Users\Habiburrahman\Documents\4paws\4paws-agent\logs\backend.log

# Restart backend
curl -X POST http://localhost:5000/api/stop/backend
curl -X POST http://localhost:5000/api/start/backend
```

### **Issue 4: Update Button Still Not Working**
```
Even after starting agent server
```

**Solution**:
```cmd
# 1. Clear browser cache (Ctrl+Shift+Delete)
# 2. Hard refresh (Ctrl+Shift+R)
# 3. Check browser console (F12)
# 4. Look for errors like "Failed to fetch"
```

---

## 📝 **Environment Variables (Optional)**

Create `.env.local` in frontend:

```bash
# File: C:\Users\Habiburrahman\Documents\4paws\4paws-frontend\.env.local

NEXT_PUBLIC_AGENT_URL=http://localhost:5000
NEXT_PUBLIC_API_BASE_URL=http://localhost:3200
```

Then rebuild:
```cmd
cd C:\Users\Habiburrahman\Documents\4paws\4paws-frontend
pnpm build
```

---

## 🔍 **Health Checks**

### **Check All Services**:
```cmd
# Agent (should return HTML page)
curl http://localhost:5000

# Frontend (should return HTML page)
curl http://localhost:3100

# Backend (should return JSON)
curl http://localhost:3200/api/health

# Agent API (should return JSON status)
curl http://localhost:5000/api/status
```

### **Expected Responses**:

**Agent Status** (http://localhost:5000/api/status):
```json
{
  "mariadb": {"running": true, "pid": 1234},
  "backend": {"running": true, "pid": 5678},
  "frontend": {"running": true, "pid": 9012},
  "versions": {
    "frontend": {"version": "v1.0.0"},
    "backend": {"version": "v1.0.0"}
  }
}
```

---

## 🎓 **Common Workflows**

### **Daily Use (Normal User)**:
```
1. Double-click: start-tray.bat
2. Wait for tray icon to appear
3. Right-click tray icon → "Open Frontend"
4. Start working!

To stop:
Right-click tray icon → "Exit"
```

### **Update Workflow**:
```
1. Click update button (🔄) in frontend
2. If updates available → Modal appears
3. Click "Update Now"
4. Wait 2-3 minutes (see progress)
5. Page auto-reloads
6. Done! ✨
```

### **Development Workflow**:
```
Terminal 1: python gui_server.py
Terminal 2: cd frontend && pnpm dev
Terminal 3: cd backend && pnpm start:dev

Access: http://localhost:3000 (Next.js dev server)
```

---

## 📞 **Support**

### **If you still have issues:**

1. **Check logs**:
   ```cmd
   type logs\agent.log
   type logs\frontend.log
   type logs\backend.log
   type logs\mariadb.log
   ```

2. **Check processes**:
   ```cmd
   tasklist | findstr python
   tasklist | findstr node
   ```

3. **Restart everything**:
   ```cmd
   taskkill /F /IM python.exe
   taskkill /F /IM node.exe
   start-all.bat
   ```

4. **Full reset** (if nothing works):
   ```cmd
   # Stop all
   taskkill /F /IM python.exe
   taskkill /F /IM node.exe
   
   # Clear data (CAUTION: This deletes database!)
   rmdir /S /Q data\mariadb
   
   # Reinstall
   python agent.py setup
   python agent.py install all
   python agent.py setup-apps
   start-all.bat
   ```

---

## 🎯 **Key Files**

| File | Purpose |
|------|---------|
| `start-all.bat` | Start everything at once |
| `start-tray.bat` | Start with system tray app |
| `gui_server.py` | Agent web GUI & API server |
| `agent.py` | Core agent logic |
| `UPDATE_BUTTON_FIX.md` | Update button troubleshooting |
| `QUICK_START.md` | This file |

---

## ✅ **Checklist for Working System**

Before reporting issues, verify:

- [ ] Agent server running (check http://localhost:5000)
- [ ] Frontend running (check http://localhost:3100)
- [ ] Backend running (check http://localhost:3200)
- [ ] MariaDB running (check tasklist | findstr mysqld)
- [ ] No port conflicts (no other services on 3100/3200/5000)
- [ ] Update button shows 🔄 (not ⚠️)
- [ ] Browser console has no "Failed to fetch" errors
- [ ] All 3 service logs exist and recent

---

**Status**: ✅ Complete Guide
**Version**: 1.1.0
**Last Updated**: October 5, 2025

