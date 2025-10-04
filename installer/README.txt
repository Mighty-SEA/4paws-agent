╔════════════════════════════════════════╗
║     4Paws Agent - Installation         ║
║        Complete Setup Package          ║
╚════════════════════════════════════════╝

Thank you for installing 4Paws Agent!

WHAT'S INCLUDED
═══════════════
✓ 4Paws Agent Application
✓ Node.js v22.20.0 (Portable)
✓ MariaDB 12.0.2 (Portable)
✓ All required dependencies

GETTING STARTED
═══════════════
1. Launch "4Paws Agent" from Start Menu or Desktop
2. The system tray icon will appear
3. Right-click the tray icon for options:
   - Open Web GUI (http://localhost:5000)
   - Start/Stop Services
   - Check Updates

FIRST TIME SETUP
════════════════
When you first start the agent:

1. It will automatically download the latest releases from GitHub:
   - Frontend (4paws-frontend)
   - Backend (4paws-backend)

2. Install dependencies (this takes 2-5 minutes)

3. Start services:
   - MariaDB Database (port 3307)
   - Backend API (port 3200)
   - Frontend Web (port 3100)

4. Access the application at: http://localhost:3100

SYSTEM TRAY MENU
════════════════
Right-click the paw icon in system tray:

🌐 Open Web GUI       - Monitor & control via web interface
▶️ Start All Services - Start MariaDB, Backend, Frontend
⏹️ Stop All Services  - Stop all running services
🎨 Open Frontend      - Open http://localhost:3100
🔧 Open Backend API   - Open http://localhost:3200
🔄 Check Updates      - Check for new releases on GitHub
❌ Quit               - Exit agent (stops all services)

WEB GUI DASHBOARD
═════════════════
The Web GUI provides:
- Real-time service status
- Live logs monitoring
- System metrics (CPU, Memory, Disk)
- One-click start/stop controls
- Update notifications
- Dark/Light theme toggle

FEATURES
════════
✓ Auto-download releases from GitHub
✓ Automatic updates when available
✓ One-click start/stop all services
✓ Web-based dashboard
✓ System tray integration
✓ Database seeding tools
✓ Service logs monitoring
✓ Portable - no system modifications

INSTALLED LOCATIONS
═══════════════════
Program Files:     C:\Program Files\4PawsAgent\
Node.js:          C:\Program Files\4PawsAgent\tools\node\
MariaDB:          C:\Program Files\4PawsAgent\tools\mariadb\
Applications:     C:\Program Files\4PawsAgent\apps\
Database:         C:\Program Files\4PawsAgent\data\mariadb\
Logs:             C:\Program Files\4PawsAgent\logs\

TROUBLESHOOTING
═══════════════
If you encounter issues:

1. Check logs in: C:\Program Files\4PawsAgent\logs\
   - agent.log - Main agent log
   - backend.log - Backend service log
   - frontend.log - Frontend service log
   - mariadb.log - Database log

2. Windows Firewall:
   - Allow Node.js when prompted
   - Allow 4PawsAgent.exe when prompted

3. Port conflicts:
   If ports 3100, 3200, or 3307 are in use, you can change them
   in the agent configuration.

4. Antivirus:
   Some antivirus may flag portable tools.
   Add exception for: C:\Program Files\4PawsAgent\

UNINSTALLING
════════════
To uninstall:
1. Go to Settings > Apps > Apps & features
2. Find "4Paws Agent"
3. Click Uninstall
4. Choose whether to keep database files

Or run: C:\Program Files\4PawsAgent\Uninstall.exe

SUPPORT
═══════
For help and updates:
- GitHub: https://github.com/Mighty-SEA/4paws-frontend
- GitHub: https://github.com/Mighty-SEA/4paws-backend
- Check Web GUI for system status
- View logs for detailed error messages

DATABASE SEEDING
════════════════
To seed the database with sample data:
1. Open Web GUI
2. Click "Seed Database"
3. Choose what to seed:
   - All (complete sample data)
   - Users
   - Services
   - Products
   - Pets & Owners

UPDATING
════════
The agent automatically checks for updates:
1. Click "Check Updates" in tray menu
2. If updates available, click "Update"
3. Services will restart automatically

Or use Web GUI:
1. Open Web GUI
2. Check "Updates" section
3. Click "Install Update" if available

TECHNICAL INFO
══════════════
MariaDB:
- Port: 3307 (default)
- User: root
- Password: 4paws_secure_password
- Database: 4paws_db

Backend API:
- Port: 3200
- Swagger docs: http://localhost:3200/api

Frontend:
- Port: 3100
- URL: http://localhost:3100

Web GUI:
- Port: 5000 (auto-increment if busy)
- URL: http://localhost:5000

CREDITS
═══════
Built with:
- Python
- Node.js & pnpm
- MariaDB
- Flask & Flask-SocketIO
- PyStray (System Tray)
- PyInstaller (Executable)
- NSIS (Installer)

═══════════════════════════════════════════
Version: 1.0.0
Built: October 2025
License: MIT
═══════════════════════════════════════════

Enjoy using 4Paws Agent! 🐾

