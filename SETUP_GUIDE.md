# 🚀 Quick Setup Guide

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Download & Setup Portable Tools

### A. Node.js Portable

1. Visit: https://nodejs.org/dist/v20.11.0/
2. Download: `node-v20.11.0-win-x64.zip`
3. Extract to: `tools/node/`
4. Verify: `tools/node/node.exe` exists

### B. MariaDB Portable

1. Visit: https://mariadb.org/download/
2. Download: MariaDB 11.x Windows 64-bit ZIP
3. Extract to: `tools/mariadb/`
4. Verify: `tools/mariadb/bin/mysqld.exe` exists

### C. Run Setup

```bash
python agent.py setup
```

This will:
- ✅ Verify Node.js installation
- ✅ Auto-install pnpm
- ✅ Initialize MariaDB database

---

## Step 3: Install Apps

```bash
# Install both frontend and backend
python agent.py install all
```

This will:
1. 📥 Download latest releases from GitHub
2. 📂 Extract to `apps/frontend` and `apps/backend`
3. 📝 Auto-create `.env` files
4. ✅ Ready to run!

---

## Step 4: Start Services

### Option A: Using Python

```bash
python agent.py start
```

### Option B: Using Batch File (Double-click)

```
start.bat
```

---

## Step 5: Access the App

Open browser and go to:

**http://localhost:3100**

---

## 📊 Services Overview

| Service | Port | URL |
|---------|------|-----|
| **Frontend** | 3100 | http://localhost:3100 |
| **Backend API** | 3200 | http://localhost:3200 |
| **MariaDB** | 3307 | localhost:3307 |

---

## 🔄 Update Workflow

### Check for Updates

```bash
python agent.py check
```

### Install Updates

```bash
python agent.py update
```

Or double-click: `update.bat`

---

## ⏹️ Stop Services

### Option A: Using Python

```bash
python agent.py stop
```

### Option B: Using Batch File

```
stop.bat
```

### Option C: Press Ctrl+C

If running in foreground, press `Ctrl+C` to stop.

---

## 🛠️ Troubleshooting

### "Python is not recognized"

Install Python 3.8+: https://www.python.org/downloads/

Make sure to check "Add Python to PATH" during installation.

### "pip is not recognized"

```bash
python -m ensurepip --upgrade
```

### "Node.js not found"

Make sure you extracted Node.js to the correct location:
- Path: `4paws-agent/tools/node/`
- File must exist: `tools/node/node.exe`

### "MariaDB not found"

Make sure you extracted MariaDB to the correct location:
- Path: `4paws-agent/tools/mariadb/`
- File must exist: `tools/mariadb/bin/mysqld.exe`

### Port Already in Use

**Find what's using the port:**

```bash
# Check port 3100 (frontend)
netstat -ano | findstr :3100

# Check port 3200 (backend)
netstat -ano | findstr :3200

# Check port 3307 (mariadb)
netstat -ano | findstr :3307
```

**Kill the process:**

```bash
taskkill /PID <PID_NUMBER> /F
```

---

## 📁 Final Directory Structure

After complete setup:

```
4paws-agent/
├── agent.py                    # Main agent
├── start.bat                   # Quick start
├── stop.bat                    # Quick stop
├── update.bat                  # Quick update
├── requirements.txt            # Python deps
├── versions.json              # Version tracking
│
├── tools/                     # ✅ Manual setup
│   ├── node/
│   │   ├── node.exe           # ✅ Downloaded
│   │   ├── npm.cmd
│   │   └── pnpm.cmd           # ✅ Auto-installed
│   └── mariadb/
│       └── bin/
│           ├── mysqld.exe     # ✅ Downloaded
│           ├── mysql.exe
│           └── ...
│
├── apps/                      # ✅ Auto-installed
│   ├── frontend/              # ✅ From GitHub
│   │   ├── .next/
│   │   ├── .env              # ✅ Auto-created
│   │   ├── start.bat
│   │   └── ...
│   └── backend/               # ✅ From GitHub
│       ├── dist/
│       ├── prisma/
│       ├── .env              # ✅ Auto-created
│       ├── start.bat
│       └── ...
│
├── data/                      # ✅ Auto-created
│   └── mariadb/              # ✅ Database files
│
└── logs/                      # ✅ Auto-created
    ├── agent.log
    ├── frontend.log
    └── backend.log
```

---

## ✅ Checklist

Before first run, verify:

- [ ] Python 3.8+ installed
- [ ] `pip install -r requirements.txt` completed
- [ ] Node.js extracted to `tools/node/node.exe`
- [ ] MariaDB extracted to `tools/mariadb/bin/mysqld.exe`
- [ ] `python agent.py setup` completed successfully
- [ ] `python agent.py install all` completed successfully

Now you can run `start.bat`! 🚀

---

## 🎉 Success!

If everything works, you should see:

```
🚀 Starting all services...
✅ MariaDB started (PID: 1234)
🌐 MariaDB Port: 3307
✅ Backend started (PID: 5678)
🌐 Backend API: http://localhost:3200
✅ Frontend started (PID: 9012)
🌐 Frontend URL: http://localhost:3100
✅ All services started!
🌐 Access app at: http://localhost:3100

✅ Services running. Press Ctrl+C to stop...
```

---

**Happy deploying!** 🎊

