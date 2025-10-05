"""
Build script for creating standalone .exe files
Builds both the System Tray app and CLI agent
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}{Colors.END}\n")

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"{Colors.BLUE}▶ {description}...{Colors.END}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"{Colors.GREEN}✓ {description} completed{Colors.END}")
        return True
    else:
        print(f"{Colors.FAIL}✗ {description} failed{Colors.END}")
        print(result.stderr)
        return False

def remove_long_path(path):
    """Remove directory with long path support (Windows)"""
    import platform
    
    if platform.system() != 'Windows':
        shutil.rmtree(path)
        return
    
    # Try normal deletion first
    try:
        shutil.rmtree(path)
        return
    except PermissionError as e:
        # File is locked/in use
        print(f"{Colors.WARNING}⚠️  Permission denied (file may be running): {path}{Colors.END}")
        print(f"{Colors.WARNING}   Close any running instances and try again{Colors.END}")
        raise  # Re-raise to stop the build
    except (FileNotFoundError, OSError) as e:
        # If normal deletion fails, use robocopy trick or long path
        print(f"{Colors.WARNING}⚠️  Long path detected, using alternative method...{Colors.END}")
        
        try:
            # Method 1: Use robocopy to mirror empty directory (deletes everything)
            import tempfile
            empty_dir = tempfile.mkdtemp()
            try:
                # robocopy /MIR mirrors source to destination (empty to target = delete all)
                subprocess.run(
                    ['robocopy', empty_dir, path, '/MIR', '/NFL', '/NDL', '/NJH', '/NJS'],
                    check=False,  # robocopy returns non-zero even on success
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                # Remove the now-empty directory
                os.rmdir(path)
                os.rmdir(empty_dir)
            except:
                # Method 2: Use long path prefix \\?\
                long_path = '\\\\?\\' + os.path.abspath(path)
                try:
                    shutil.rmtree(long_path)
                except:
                    # Last resort: just ignore and continue
                    print(f"{Colors.WARNING}⚠️  Could not fully remove {path}, continuing...{Colors.END}")
        except Exception as final_error:
            print(f"{Colors.WARNING}⚠️  Could not remove {path}: {final_error}{Colors.END}")

def clean_build_dirs():
    """Clean previous build directories"""
    # Clean build and cache directories
    dirs_to_clean = ['build', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                remove_long_path(dir_name)
                print(f"{Colors.GREEN}✓ Cleaned {dir_name}/{Colors.END}")
            except PermissionError:
                print(f"{Colors.FAIL}✗ Cannot clean {dir_name} - files in use{Colors.END}")
                print(f"{Colors.WARNING}💡 Close any running 4PawsAgent.exe or related processes{Colors.END}")
                return False
    
    # Clean dist directory but preserve tools/ and tray_launcher.exe
    if os.path.exists('dist'):
        # Items to preserve (don't delete)
        preserve_items = ['tray_launcher.exe', 'tools']
        
        # Remove everything except preserved items
        for item in os.listdir('dist'):
            if item not in preserve_items:
                item_path = os.path.join('dist', item)
                try:
                    if os.path.isdir(item_path):
                        remove_long_path(item_path)
                    else:
                        os.remove(item_path)
                except PermissionError:
                    print(f"{Colors.FAIL}✗ Cannot remove {item} - file is running{Colors.END}")
                    print(f"{Colors.WARNING}💡 Close {item} and try again{Colors.END}")
                    return False
                except:
                    # Try with long path prefix
                    try:
                        os.remove('\\\\?\\' + os.path.abspath(item_path))
                    except:
                        pass
        print(f"{Colors.GREEN}✓ Cleaned dist/ (preserved tools/ and tray_launcher.exe){Colors.END}")
    
    return True

def create_spec_file():
    """Create PyInstaller spec file for tray app"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['tray_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('core', 'core'),  # Include core module
        ('agent.py', '.'),
        ('gui_server.py', '.'),
        ('installation_server.py', '.'),
        ('shortcut_manager.py', '.'),
        ('service_manager.py', '.'),
        ('tray_launcher.py', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_socketio',
        'pystray',
        'PIL',
        'psutil',
        'engineio.async_drivers.threading',
        'core',  # Add core module
        'core.config',
        'core.logger',
        'core.paths',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='4PawsAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/img/favicon.ico',  # Application icon
)
"""
    
    with open('4PawsAgent.spec', 'w') as f:
        f.write(spec_content)
    
    print(f"{Colors.GREEN}✓ Created spec file{Colors.END}")

def build_tray_exe():
    """Build the system tray application"""
    print_header("Building System Tray Application")
    
    # Create spec file
    create_spec_file()
    
    # Build
    if not run_command(
        'pyinstaller --clean 4PawsAgent.spec',
        'Building 4PawsAgent.exe'
    ):
        return False
    
    return True

def build_cli_exe():
    """Build the CLI agent"""
    print_header("Building CLI Agent")
    
    cmd = (
        'pyinstaller --onefile --console '
        '--name 4PawsAgentCLI '
        '--add-data "agent.py;." '
        'agent.py'
    )
    
    if not run_command(cmd, 'Building 4PawsAgentCLI.exe'):
        return False
    
    return True

def create_portable_package():
    """Create portable package with all necessary files"""
    print_header("Creating Portable Package")
    
    package_dir = Path('dist/4PawsAgent-Portable')
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executables
    if (Path('dist/4PawsAgent.exe')).exists():
        shutil.copy('dist/4PawsAgent.exe', package_dir / '4PawsAgent.exe')
        print(f"{Colors.GREEN}✓ Copied 4PawsAgent.exe{Colors.END}")
    
    if (Path('dist/4PawsAgentCLI.exe')).exists():
        shutil.copy('dist/4PawsAgentCLI.exe', package_dir / '4PawsAgentCLI.exe')
        print(f"{Colors.GREEN}✓ Copied 4PawsAgentCLI.exe{Colors.END}")
    
    # Copy tools folder if it exists (Node.js, pnpm, MariaDB)
    # Note: Build script preserves dist/tools/ folder to avoid re-downloading
    source_tools = Path('dist/tools')
    if not source_tools.exists():
        source_tools = Path('tools')  # Fallback to project root
    
    if source_tools.exists():
        tools_dest = package_dir / 'tools'
        if tools_dest.exists():
            print(f"{Colors.WARNING}⚠️  Tools folder already exists in package, skipping copy...{Colors.END}")
            print(f"{Colors.BLUE}▶ Checking tools contents...{Colors.END}")
            # List what's in tools
            for item in tools_dest.iterdir():
                print(f"   - {item.name}")
        else:
            print(f"{Colors.BLUE}▶ Copying tools folder (Node.js, pnpm, MariaDB)...{Colors.END}")
            print(f"   Source: {source_tools}")
            shutil.copytree(source_tools, tools_dest)
            print(f"{Colors.GREEN}✓ Copied tools/{Colors.END}")
            # List what was copied
            for item in tools_dest.iterdir():
                print(f"   ✓ {item.name}")
    else:
        print(f"{Colors.WARNING}⚠️  Tools folder not found. Will be downloaded during first run.{Colors.END}")
        print(f"{Colors.WARNING}💡 To pre-package tools: Run 'python agent.py setup' first{Colors.END}")
    
    # Copy batch files
    for bat_file in ['start.bat', 'stop.bat', 'update.bat']:
        if Path(bat_file).exists():
            shutil.copy(bat_file, package_dir / bat_file)
    
    # Create README for portable
    readme_content = """# 4Paws Agent - Portable Edition

## 🚀 Quick Start

### System Tray (Recommended)
Double-click: `4PawsAgent.exe`

Features:
- System tray icon with quick menu
- Web GUI dashboard
- Auto-start services

### Command Line
Run: `4PawsAgentCLI.exe [command]`

Available commands:
- setup              - Setup tools (Node.js, pnpm, MariaDB)
- check              - Check for updates
- install [component] - Install frontend/backend/all
- setup-apps [component] - Setup apps (dependencies + migrations)
- seed [type]        - Seed database
- start              - Start all services
- stop               - Stop all services
- update [component] - Update frontend/backend/all

## 📋 First Time Setup

1. Download and extract required tools to `tools/` folder:
   - Node.js (portable)
   - MariaDB (portable)

2. Run initial setup:
   ```
   4PawsAgentCLI.exe setup
   ```

3. Install applications:
   ```
   4PawsAgentCLI.exe install all
   ```

4. Setup applications:
   ```
   4PawsAgentCLI.exe setup-apps
   ```

5. Start system tray:
   ```
   4PawsAgent.exe
   ```

## 🌐 Access

- Web GUI: http://localhost:5000
- Frontend: http://localhost:3100
- Backend API: http://localhost:3200

## 📖 Full Documentation

See `README.md` and `GUI_GUIDE.md` in the project repository.

---
Built with ❤️ for 4Paws
"""
    
    with open(package_dir / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"{Colors.GREEN}✓ Created README.txt{Colors.END}")
    
    # Create folders structure
    for folder in ['tools', 'apps', 'data', 'logs']:
        (package_dir / folder).mkdir(exist_ok=True)
    
    print(f"{Colors.GREEN}✓ Created folder structure{Colors.END}")
    
    # Create versions.json template
    versions = {
        "frontend": {"version": "0.0.0", "installed_at": ""},
        "backend": {"version": "0.0.0", "installed_at": ""}
    }
    
    import json
    with open(package_dir / 'versions.json', 'w') as f:
        json.dump(versions, f, indent=2)
    
    print(f"{Colors.GREEN}✓ Created versions.json{Colors.END}")
    
    return True

def main():
    """Main build process"""
    print(f"""
╔════════════════════════════════════════╗
║   4Paws Agent Build Script            ║
║   Creating Standalone Executables     ║
╚════════════════════════════════════════╝
""")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print(f"{Colors.FAIL}✗ PyInstaller not found!{Colors.END}")
        print(f"{Colors.WARNING}Installing PyInstaller...{Colors.END}")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Clean previous builds
    print_header("Cleaning Previous Builds")
    if not clean_build_dirs():
        print(f"\n{Colors.FAIL}❌ Build cancelled - please close running processes first{Colors.END}")
        return 1
    
    # Build System Tray App
    if not build_tray_exe():
        print(f"\n{Colors.FAIL}Build failed!{Colors.END}")
        return 1
    
    # Build CLI Agent (optional, can be skipped)
    # build_cli_exe()
    
    # Create portable package
    create_portable_package()
    
    # Show results
    print_header("Build Complete!")
    
    exe_path = Path('dist/4PawsAgent.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"{Colors.GREEN}✓ 4PawsAgent.exe created ({size_mb:.1f} MB){Colors.END}")
        print(f"{Colors.BLUE}  Location: {exe_path.absolute()}{Colors.END}")
    
    portable_dir = Path('dist/4PawsAgent-Portable')
    if portable_dir.exists():
        print(f"\n{Colors.GREEN}✓ Portable package created{Colors.END}")
        print(f"{Colors.BLUE}  Location: {portable_dir.absolute()}{Colors.END}")
    
    print(f"""
{Colors.BOLD}Next Steps:{Colors.END}
1. Test the executable: {Colors.BLUE}dist/4PawsAgent.exe{Colors.END}
2. Distribute: {Colors.BLUE}dist/4PawsAgent-Portable/{Colors.END}

{Colors.WARNING}Note: First run will create necessary folders and config files{Colors.END}
""")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

