# 🤖 4Paws Deployment Agent

Auto-download, update, and manage 4Paws frontend & backend releases from GitHub with portable Node.js, pnpm, and MariaDB.

## ✨ Features

- 🔄 **Auto-update from GitHub Releases**
- 📦 **Portable Node.js & pnpm** (no system installation)
- 🦋 **Portable MariaDB** (no system installation, better than MySQL)
- 🚀 **One-command start/stop** for all services
- 📊 **Version tracking** and rollback support
- 🔍 **Update checker** with smart notifications
- 📝 **Auto-configuration** of .env files
- 🌐 **Web GUI Dashboard** for monitoring and control
- 🖥️ **System Tray Application** for quick access
- 🔒 **Single Instance Lock** prevents multiple instances

---

## 📋 Requirements

- **Python 3.8+**
- **Windows 10/11** (tested on Windows)
- **Internet connection** (for downloading releases)

---

## 🚀 Quick Start

### 1. Install Python Dependencies

```bash
cd 4paws-agent
pip install -r requirements.txt
```

### 2. Configure GitHub Token (Optional but Recommended)

To avoid GitHub API rate limits (60 requests/hour without token), create a Personal Access Token:

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Classic"**
3. Select scope: `public_repo` (read-only access)
4. Copy the generated token
5. Create `.env` file in `4paws-agent/`:

```bash
# Copy example file
cp env.example .env

# Edit .env and add your token
GITHUB_TOKEN=ghp_yourTokenHere123456789
```

**Benefits:**
- ✅ Increases rate limit from 60 to 5,000 requests/hour
- ✅ Prevents "rate limit exceeded" errors
- ✅ Faster and more reliable update checks

### 3. Setup Portable Tools

```bash
python agent.py setup
```

This will guide you to:
- Download **Node.js Portable** → Extract to `tools/node/`
- Download **MariaDB Portable** → Extract to `tools/mariadb/`
- pnpm will be auto-installed

**Download Links:**
- Node.js: https://nodejs.org/dist/ (get `node-v20.x.x-win-x64.zip`)
- MariaDB: https://mariadb.org/download/ (get Windows 64-bit ZIP)

### 4. Install Apps

```bash
# Install both frontend and backend
python agent.py install all

# Or install individually
python agent.py install frontend
python agent.py install backend
```

### 5. Start Services

```bash
python agent.py start
```

This will:
1. ✅ Start MariaDB (port 3307)
2. ✅ Start Backend API (port 3200)
3. ✅ Start Frontend (port 3100)

**Access the app:** http://localhost:3100

---

## 📖 Usage

### Check for Updates

```bash
python agent.py check
```

Output:
```
🔍 Checking for updates...
✅ Frontend up to date: 0.0.1
✅ Backend up to date: 0.0.1
```

### Install Updates

```bash
# Check and install updates automatically
python agent.py update
```

### Stop Services

```bash
python agent.py stop
```

---

## 📂 Directory Structure

```
4paws-agent/
├── agent.py              # Main agent script
├── requirements.txt      # Python dependencies
├── versions.json         # Installed versions tracking
├── agent.log             # Agent logs
│
├── tools/                # Portable tools (not in git)
│   ├── node/            # Node.js portable
│   ├── pnpm/            # pnpm (auto-installed)
│   └── mariadb/         # MariaDB portable
│
├── apps/                 # Installed apps (not in git)
│   ├── frontend/        # 4Paws frontend
│   └── backend/         # 4Paws backend
│
├── data/                 # App data (not in git)
│   └── mariadb/         # MariaDB database files
│
└── logs/                 # Service logs (not in git)
```

---

## 🔧 Configuration

### App Ports (in `agent.py`)

```python
FRONTEND_PORT = 3100
BACKEND_PORT = 3200
MARIADB_PORT = 3307  # Changed to avoid conflict with system MariaDB
```

### MariaDB Credentials

```python
MARIADB_DB = "4paws_db"
MARIADB_USER = "root"
MARIADB_PASSWORD = "4paws_secure_password"
```

### GitHub Repositories

```python
FRONTEND_REPO = "Mighty-SEA/4paws-frontend"
BACKEND_REPO = "Mighty-SEA/4paws-backend"
```

---

## 🛠️ Commands Reference

| Command | Description |
|---------|-------------|
| `python agent.py setup` | Setup portable tools (Node.js, pnpm, MariaDB) |
| `python agent.py check` | Check for updates from GitHub |
| `python agent.py install [component]` | Install frontend/backend/all |
| `python agent.py start` | Start all services (MariaDB + Backend + Frontend) |
| `python agent.py stop` | Stop all running services |
| `python agent.py update` | Check and install updates automatically |

---

## 📊 Version Tracking

Installed versions are tracked in `versions.json`:

```json
{
  "frontend": {
    "version": "0.0.1",
    "updated_at": "2025-10-03T22:54:00"
  },
  "backend": {
    "version": "0.0.1",
    "updated_at": "2025-10-03T22:54:00"
  }
}
```

---

## 🔍 Troubleshooting

### "Node.js not found"

1. Download Node.js portable: https://nodejs.org/dist/v20.11.0/node-v20.11.0-win-x64.zip
2. Extract to `tools/node/`
3. Verify `tools/node/node.exe` exists

### "MariaDB not found"

1. Download MariaDB ZIP: https://mariadb.org/download/
2. Extract to `tools/mariadb/`
3. Verify `tools/mariadb/bin/mysqld.exe` exists
4. Run `python agent.py setup` again

### "Port already in use"

Check what's using the port:

```bash
# Windows
netstat -ano | findstr :3100
netstat -ano | findstr :3200
netstat -ano | findstr :3307

# Kill process by PID
taskkill /PID <PID> /F
```

### Check Logs

```bash
# Agent log
type agent.log

# Service logs
type logs\backend.log
type logs\frontend.log
type logs\mariadb.log
```

---

## 🔄 Update Workflow

The agent follows this update workflow:

1. **Check GitHub** for latest releases
2. **Compare** with installed versions
3. **Download** new release ZIP
4. **Backup** old version to `.backup/`
5. **Extract** new version
6. **Update** version tracking
7. **Restart** services

---

## 🚨 Known Issues

1. **Windows Firewall** may block Node.js - Allow when prompted
2. **Antivirus** may flag portable tools - Add exception
3. **First run** takes 2-5 minutes for dependency installation

---

## 📧 Support

For issues or questions, check:
- Agent logs: `agent.log`
- GitHub Issues: https://github.com/Mighty-SEA/4paws-frontend/issues

---

## 📄 License

MIT License - See main repository for details

---

**Last Updated:** October 4, 2025  
**Version:** 1.0.0

