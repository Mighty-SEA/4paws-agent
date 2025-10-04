# 📦 4Paws Agent Installer Build Guide

Complete guide for building the Windows installer with bundled Node.js and MariaDB.

---

## 📋 Prerequisites

### Required Files

All files must be in place before building:

```
4paws-agent/
├── installer/
│   └── assets/
│       ├── node-v22.20.0-win-x64.zip      ✓ (35 MB)
│       └── mariadb-12.0.2-winx64.zip      ✓ (95 MB)
```

### Required Software

1. **Python 3.8+** - Already installed
2. **NSIS (Nullsoft Scriptable Install System)**
   - Download: https://nsis.sourceforge.io/Download
   - Version: 3.x or later
   - Install to default location

---

## 🚀 Quick Build

### One-Command Build

```bash
python build-installer.bat
```

This will:
1. ✅ Build `4PawsAgent.exe` using PyInstaller
2. ✅ Prepare installer files
3. ✅ Detect NSIS installation
4. ✅ Compile installer
5. ✅ Output: `dist/4PawsAgent-Setup.exe` (~145 MB)

**Build time:** 5-10 minutes

---

## 📝 Step-by-Step Build

### Step 1: Build Executable

```bash
python build-exe.py
```

Output:
- `dist/4PawsAgent.exe` (15 MB)
- `dist/4PawsAgent-Portable/` (portable package)

### Step 2: Prepare Installer Files

```bash
python installer/prepare-installer.py
```

This copies:
- ✅ `4PawsAgent.exe` → `installer/`
- ✅ Node.js ZIP → `installer/node-temp.zip`
- ✅ MariaDB ZIP → `installer/mariadb-temp.zip`

### Step 3: Install NSIS (if not installed)

**Download & Install:**
1. Go to: https://nsis.sourceforge.io/Download
2. Download NSIS 3.x installer
3. Run installer (use default settings)
4. NSIS will be installed to: `C:\Program Files (x86)\NSIS\`

**Verify Installation:**
```bash
"C:\Program Files (x86)\NSIS\makensis.exe" /VERSION
```

### Step 4: Compile Installer

**Option A: Command Line**
```bash
"C:\Program Files (x86)\NSIS\makensis.exe" installer/installer.nsi
```

**Option B: GUI**
1. Right-click `installer/installer.nsi`
2. Select "Compile NSIS Script"
3. Wait for compilation (3-5 minutes)

**Option C: Automated Script**
```bash
build-installer.bat
```

### Step 5: Test Installer

```bash
dist/4PawsAgent-Setup.exe
```

Follow installation wizard:
1. Accept license
2. Choose install location
3. Select Start Menu folder
4. Wait for installation (~2-3 minutes)
5. Launch application

---

## 📦 What's Included in Installer

### Bundled Components

| Component | Version | Size | Purpose |
|-----------|---------|------|---------|
| 4Paws Agent | 1.0.0 | 15 MB | Main application |
| Node.js Portable | v22.20.0 | 35 MB | JavaScript runtime |
| MariaDB Portable | v12.0.2 | 95 MB | Database server |

**Total Installer Size:** ~145 MB (compressed)

### Installation Actions

The installer automatically:

1. ✅ Extracts Node.js to `tools/node/`
2. ✅ Extracts MariaDB to `tools/mariadb/`
3. ✅ Initializes MariaDB database
4. ✅ Creates folder structure
5. ✅ Creates Start Menu shortcuts
6. ✅ Registers in Add/Remove Programs
7. ✅ Creates uninstaller

### Default Installation Path

```
C:\Program Files\4PawsAgent\
├── 4PawsAgent.exe           # Main application
├── README.txt               # User guide
├── Uninstall.exe            # Uninstaller
├── tools/
│   ├── node/                # Node.js v22.20.0
│   └── mariadb/             # MariaDB v12.0.2
├── apps/                    # Installed applications
├── data/
│   └── mariadb/             # Database files
└── logs/                    # Application logs
```

---

## 🔧 Installer Features

### User Experience

- ✅ Professional installer UI
- ✅ License agreement
- ✅ Custom installation path
- ✅ Start Menu integration
- ✅ Progress indicators
- ✅ Automatic extraction (~3 minutes)
- ✅ Option to launch on finish

### Uninstaller Features

- ✅ Complete removal of application
- ✅ Option to keep or delete database
- ✅ Stops all running services
- ✅ Removes registry entries
- ✅ Removes Start Menu shortcuts

### Registry Integration

**Stored in Registry:**
```
HKLM\Software\4PawsAgent
├── InstallDir: "C:\Program Files\4PawsAgent"
└── Start Menu Folder: "4PawsAgent"

HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\4PawsAgent
├── DisplayName: "4Paws Agent"
├── DisplayVersion: "1.0.0"
├── Publisher: "4Paws"
├── UninstallString: "..."
└── DisplayIcon: "..."
```

---

## 🛠️ Customization

### Modify Installer Script

Edit `installer/installer.nsi`:

**Change version:**
```nsis
VIProductVersion "1.0.0.0"
```

**Change default install location:**
```nsis
InstallDir "$PROGRAMFILES64\4PawsAgent"
```

**Change installer name:**
```nsis
OutFile "..\dist\4PawsAgent-Setup.exe"
```

### Update Asset Versions

If updating Node.js or MariaDB versions:

1. Replace ZIP files in `installer/assets/`:
   - `node-v<NEW_VERSION>-win-x64.zip`
   - `mariadb-<NEW_VERSION>-winx64.zip`

2. Update `installer.nsi` - change folder names:
   ```nsis
   Rename "$INSTDIR\tools\node-v22.20.0-win-x64" "$INSTDIR\tools\node"
   Rename "$INSTDIR\tools\mariadb-12.0.2-winx64" "$INSTDIR\tools\mariadb"
   ```

3. Update `prepare-installer.py` - change file names:
   ```python
   "Node.js ZIP": assets_dir / "node-v22.20.0-win-x64.zip",
   "MariaDB ZIP": assets_dir / "mariadb-12.0.2-winx64.zip"
   ```

---

## 🧪 Testing Checklist

### Pre-Build Testing

- [ ] `4PawsAgent.exe` runs standalone
- [ ] Node.js and MariaDB ZIPs are valid
- [ ] All files are in correct locations
- [ ] NSIS is installed and accessible

### Post-Build Testing

- [ ] Installer runs without errors
- [ ] Installation completes successfully
- [ ] Start Menu shortcuts created
- [ ] Application launches from Start Menu
- [ ] System tray icon appears
- [ ] Web GUI accessible
- [ ] Services start correctly
- [ ] Database initializes properly
- [ ] Uninstaller works correctly
- [ ] Reinstall over existing works

### Test Scenarios

**Clean Install:**
```bash
# On fresh Windows install or VM
1. Run 4PawsAgent-Setup.exe
2. Follow wizard with defaults
3. Launch from Start Menu
4. Test all features
```

**Upgrade Install:**
```bash
# With existing installation
1. Run new installer
2. Should detect old version
3. Uninstall old → Install new
4. Data should be preserved
```

**Uninstall:**
```bash
# From Add/Remove Programs
1. Find "4Paws Agent"
2. Click Uninstall
3. Choose "Keep Database" or "Delete"
4. Verify complete removal
```

---

## 📊 Build Output

### Expected Files

After successful build:

```
dist/
├── 4PawsAgent.exe              # Standalone executable (15 MB)
├── 4PawsAgent-Setup.exe        # Windows installer (145 MB)
└── 4PawsAgent-Portable/        # Portable package
```

### File Sizes

| File | Size | Type |
|------|------|------|
| `4PawsAgent.exe` | ~15 MB | Standalone executable |
| `4PawsAgent-Setup.exe` | ~145 MB | Windows installer |
| `4PawsAgent-Portable.zip` | ~15 MB | Portable package |

---

## 🚨 Troubleshooting

### NSIS Not Found

**Error:**
```
NSIS is not installed on this system
```

**Solution:**
1. Download NSIS: https://nsis.sourceforge.io/Download
2. Install to default location
3. Restart command prompt
4. Run build again

### ZIP Extraction Fails

**Error:**
```
Failed to extract Node.js/MariaDB
```

**Solution:**
1. Verify ZIP files are not corrupted
2. Re-download from official sources
3. Check ZIP file names match exactly
4. Ensure enough disk space (2+ GB)

### Installer Too Large

**Issue:** Installer > 200 MB

**Solutions:**
- Use higher NSIS compression: `/SOLID lzma`
- Reduce included assets
- Use 7-Zip LZMA2 compression on ZIPs first

### Installation Fails

**Common causes:**
1. Insufficient permissions → Run as Administrator
2. Antivirus blocking → Add exception
3. Disk space low → Free up space
4. Path too long → Install to shorter path

---

## 📤 Distribution

### For End Users

**Simple distribution:**
```
1. Upload 4PawsAgent-Setup.exe to:
   - GitHub Releases
   - Company server
   - Cloud storage

2. Users download and run
3. No additional dependencies needed
```

**Distribution checklist:**
- [ ] Test on clean Windows machine
- [ ] Verify antivirus doesn't flag it
- [ ] Include user guide (README.txt)
- [ ] Provide support contact
- [ ] List system requirements

### System Requirements

**For End Users:**
- Windows 10/11 (64-bit)
- 2 GB RAM minimum
- 2 GB free disk space
- Internet connection (for downloading releases)
- Administrator rights (for installation)

---

## 🔄 Version Updates

### Creating New Version

1. Update version in files:
   - `installer/installer.nsi` → `VIProductVersion`
   - `build-exe.py` → version string
   - `README.md` → version info

2. Rebuild:
   ```bash
   python build-installer.bat
   ```

3. Test new installer

4. Create GitHub release:
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

5. Upload `4PawsAgent-Setup.exe` to release

---

## 📞 Support

### For Build Issues

Check:
1. `build.log` - PyInstaller output
2. NSIS compiler output
3. File sizes and checksums

### For Installation Issues

Check:
1. Windows Event Viewer
2. Installation log (if created)
3. User permissions

---

## 📄 License

The installer includes:
- 4Paws Agent (MIT License)
- Node.js (MIT License)
- MariaDB (GPL v2)

See `LICENSE.txt` for details.

---

**Build Date:** October 2025  
**Version:** 1.0.0  
**NSIS Version:** 3.x  

---

Happy building! 🚀

