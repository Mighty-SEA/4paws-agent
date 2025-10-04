# 🐾 4Paws Deployment Agent

**Automated deployment and management agent for 4Paws Pet Management System**

## 📋 Overview

4Paws Agent adalah sistem manajemen otomatis untuk deploy dan mengelola aplikasi 4Paws Pet Management (frontend + backend). Agent ini menangani instalasi, update, database migrations, dan service management secara otomatis.

## ✨ Key Features

### 🚀 First-Time Installation
- **Otomatis download** aplikasi dari GitHub Releases
- **Setup environment** (Node.js, pnpm, MariaDB portable)
- **Database migration** dan seeding otomatis
- **Browser auto-open** ke installation page
- **Desktop & Start Menu shortcuts** otomatis dibuat

### 🔄 Auto-Update System
- **Check updates** dari GitHub Releases
- **Frontend-triggered updates** dengan real-time progress
- **Seamless update** tanpa "connection lost"
- **Dedicated loading pages** selama update
- **Auto-restart services** setelah update

### 🎨 Web GUI (Port 5000)
- **Real-time dashboard** untuk monitoring
- **Service management** (start/stop/restart)
- **Update management** dengan progress tracking
- **Real-time logs viewer** seperti terminal
- **Dark/Light mode** support

### 🔔 System Tray Application
- **Quick actions** untuk manage services
- **Status indicators** (running/stopped/update available)
- **Background running** tanpa console window
- **One-click access** ke Web GUI

### 📱 Shortcuts
- **Desktop shortcut** untuk quick access
- **Start Menu** integration
- **Custom 4Paws icon**
- **Direct link** ke frontend (port 3100)

## 🚀 Quick Start

### First-Time Installation

1. **Run the agent:**
   ```bash
   python gui_server.py
   # or
   4PawsAgent.exe
   ```

2. **Browser opens automatically** ke http://localhost:3100

3. **Installation page shows:**
   - Download progress
   - Installation steps
   - Real-time logs
   - Auto-refresh when done

4. **Shortcuts created automatically:**
   - Desktop: `4Paws Pet Management.url`
   - Start Menu: `Programs → 4Paws → 4Paws Pet Management`

5. **Done!** Access app via shortcuts or http://localhost:3100

## 📦 Installation Methods

### Method 1: Standalone Executable (Recommended)

```bash
# Download 4PawsAgent.exe from releases
# Double-click to run
# Browser opens automatically
```

### Method 2: Python Script

```bash
# Clone repository
git clone https://github.com/Mighty-SEA/4paws-agent.git
cd 4paws-agent

# Install dependencies
pip install -r requirements.txt

# Run agent
python gui_server.py
```

### Method 3: System Tray App

```bash
# Run tray application
python tray_app.py

# Right-click system tray icon:
# - Open Web GUI
# - Start/Stop Services
# - Check for Updates
# - Exit
```

## 🎯 Usage

### Web GUI (Port 5000)

Access dashboard at http://localhost:5000

**Features:**
- Service status monitoring
- Start/Stop/Restart services
- Check and install updates
- View real-time logs
- Database seeding
- Environment configuration

### CLI Commands

```bash
# Setup tools (first time)
python agent.py setup

# Check for updates
python agent.py check

# Install applications
python agent.py install [frontend|backend|all]

# Setup applications
python agent.py setup-apps [frontend|backend|all]

# Seed database
python agent.py seed [all|services|pet-species|etc]

# Start services
python agent.py start [--skip-setup]

# Stop services
python agent.py stop

# Update applications
python agent.py update [frontend|backend|all] [--yes]

# Manage shortcuts
python agent.py shortcuts create
python agent.py shortcuts remove
python agent.py shortcuts check
```

### Update from Frontend

Click **Update button** in topbar (frontend app):
- Shows update info modal
- Displays real-time progress
- Auto-restarts services
- Seamless transition

## 🏗️ Architecture

```
4paws-agent/
├── agent.py                    # Core agent logic
├── gui_server.py              # Web GUI server (Flask + SocketIO)
├── tray_app.py                # System tray application
├── installation_server.py     # First-time installation server
├── shortcut_manager.py        # Desktop/Start Menu shortcuts
├── build-exe.py               # Build standalone .exe
├── installer.nsi              # NSIS installer script
├── requirements.txt           # Python dependencies
│
├── apps/                      # Installed applications
│   ├── frontend/             # Next.js frontend
│   └── backend/              # NestJS backend
│
├── tools/                     # Portable tools
│   ├── node/                 # Node.js portable
│   ├── pnpm/                 # pnpm package manager
│   └── mariadb/              # MariaDB portable
│
├── templates/                 # Web GUI HTML templates
│   ├── index.html
│   └── components/           # Modular components
│
├── static/                    # Static assets
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript
│   └── img/                  # Images & icons
│
├── logs/                      # Application logs
│   ├── agent.log
│   ├── frontend.log
│   ├── backend.log
│   └── mariadb.log
│
└── docs/                      # Documentation (25+ guides)
    ├── README.md             # Main docs index
    ├── SETUP_GUIDE.md
    ├── BUILD_GUIDE.md
    └── ... (see docs folder)
```

## 📚 Documentation

Semua dokumentasi ada di folder `docs/`:

### 🚀 Getting Started
- [`SETUP_GUIDE.md`](docs/SETUP_GUIDE.md) - Initial setup guide
- [`FIRST_TIME_INSTALLATION_GUIDE.md`](docs/FIRST_TIME_INSTALLATION_GUIDE.md) - Auto-installation system
- [`GUI_GUIDE.md`](docs/GUI_GUIDE.md) - Web GUI usage

### 🔄 Updates & Maintenance
- [`UPDATE_FEATURE_INTEGRATION.md`](docs/UPDATE_FEATURE_INTEGRATION.md) - Update system overview
- [`UPDATE_CHECK_OPTIMIZATION.md`](docs/UPDATE_CHECK_OPTIMIZATION.md) - Caching & optimization
- [`UPDATE_INTEGRATION_GUIDE.md`](docs/UPDATE_INTEGRATION_GUIDE.md) - Frontend integration

### 🎨 UI & UX
- [`INSTALLATION_PAGE_UPDATE.md`](docs/INSTALLATION_PAGE_UPDATE.md) - Compact installation page
- [`MODULAR_DASHBOARD_GUIDE.md`](docs/MODULAR_DASHBOARD_GUIDE.md) - Dashboard components
- [`BRANDING_UPDATE.md`](docs/BRANDING_UPDATE.md) - Logo & branding
- [`ICON_UPDATE.md`](docs/ICON_UPDATE.md) - Icon system
- [`SHORTCUTS_FEATURE.md`](docs/SHORTCUTS_FEATURE.md) - Desktop shortcuts

### 📝 Logs & Monitoring
- [`LOG_SYSTEM_GUIDE.md`](docs/LOG_SYSTEM_GUIDE.md) - LogManager system
- [`LOGGING_INTEGRATION.md`](docs/LOGGING_INTEGRATION.md) - Integration guide
- [`CLEAN_LOGS_GUIDE.md`](docs/CLEAN_LOGS_GUIDE.md) - Clean log display
- [`CHANGELOG_LOGS.md`](docs/CHANGELOG_LOGS.md) - Changelog

### 🔧 Configuration
- [`ENV_CONFIGURATION_GUIDE.md`](docs/ENV_CONFIGURATION_GUIDE.md) - Environment variables
- [`ENV_FILES_EXPLAINED.md`](docs/ENV_FILES_EXPLAINED.md) - .env files guide
- [`GITHUB_TOKEN_SETUP.md`](docs/GITHUB_TOKEN_SETUP.md) - GitHub API token

### 🏗️ Build & Deploy
- [`BUILD_GUIDE.md`](docs/BUILD_GUIDE.md) - Build standalone .exe
- [`INSTALLER_GUIDE.md`](docs/INSTALLER_GUIDE.md) - Create installer
- [`IMPLEMENTATION_SUMMARY.md`](docs/IMPLEMENTATION_SUMMARY.md) - Technical details

### 📊 Summary & Overview
- [`COMPACT_INSTALLATION_SUMMARY.md`](docs/COMPACT_INSTALLATION_SUMMARY.md) - Complete summary
- [`INSTALLATION_PAGE_PREVIEW.md`](docs/INSTALLATION_PAGE_PREVIEW.md) - Preview & demo
- [`DEMO_SCREENSHOTS.md`](docs/DEMO_SCREENSHOTS.md) - Visual guide

## 🔧 Configuration

### Environment Variables

**Backend** (`.env`):
```env
DATABASE_URL="mysql://root:password@localhost:3307/4paws_db"
JWT_SECRET="your-secret-key"
PORT=3200
NODE_ENV=production
```

**Frontend** (`.env.production`):
```env
BACKEND_API_URL=http://localhost:3200
NEXT_PUBLIC_API_BASE_URL=http://localhost:3200
NEXT_PUBLIC_AGENT_URL=http://localhost:5000
NODE_ENV=production
PORT=3100
```

### Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3100 | Next.js application |
| Backend | 3200 | NestJS API |
| MariaDB | 3307 | Database server |
| Agent GUI | 5000 | Web dashboard |

### GitHub Token

For unlimited API access, set token:

**File**: `4paws-agent/.env`
```env
GITHUB_TOKEN=ghp_your_token_here
```

See [`docs/GITHUB_TOKEN_SETUP.md`](docs/GITHUB_TOKEN_SETUP.md) for details.

## 🧪 Development

### Run in Development

```bash
# Start Web GUI
python gui_server.py

# Start System Tray
python tray_app.py

# CLI commands
python agent.py [command]
```

### Build Executable

```bash
# Build standalone .exe
python build-exe.py

# Output: dist/4PawsAgent.exe
```

### Create Installer

```bash
# Build installer (requires NSIS)
makensis installer.nsi

# Output: dist/4PawsSetup.exe
```

### Preview Installation Page

```bash
# Static preview
python preview_installation.py

# Demo simulation
python demo_installation.py
```

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10 or higher
- **RAM**: 4 GB
- **Disk**: 2 GB free space
- **Network**: Internet connection (for updates)

### Recommended
- **OS**: Windows 11
- **RAM**: 8 GB
- **Disk**: 5 GB free space
- **Screen**: 1366×768 or higher

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port
netstat -ano | findstr :3100

# Kill process
taskkill /PID [PID] /F
```

### Services Not Starting

```bash
# Check logs
type logs\agent.log
type logs\frontend.log
type logs\backend.log

# Restart services
python agent.py stop
python agent.py start
```

### Updates Not Working

```bash
# Clear update cache
# Access Web GUI → Settings → Clear Cache

# Or manually:
python agent.py check
python agent.py update --yes
```

### Shortcuts Not Working

```bash
# Remove and recreate
python agent.py shortcuts remove
python agent.py shortcuts create

# Check shortcuts
python agent.py shortcuts check
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Mighty SEA Team** - *Initial work*

## 🙏 Acknowledgments

- Next.js team for amazing framework
- NestJS team for robust backend
- MariaDB for reliable database
- Flask team for simple web framework

## 📞 Support

- **Issues**: https://github.com/Mighty-SEA/4paws-agent/issues
- **Docs**: See `docs/` folder
- **Email**: support@4paws.com

## 🎉 Features Highlight

✅ **Zero Configuration** - Works out of the box
✅ **Portable** - No installation needed
✅ **Auto-Update** - Always up to date
✅ **Real-Time Monitoring** - Live dashboard
✅ **One-Click Access** - Desktop shortcuts
✅ **Professional UI** - Modern & clean
✅ **Comprehensive Logs** - Full transparency
✅ **System Tray** - Background operation
✅ **Seamless Updates** - No downtime
✅ **Multi-Platform** - Windows ready

---

**Made with ❤️ by Mighty SEA Team**

🐾 **4Paws Pet Management System** - Making pet care management easy!

