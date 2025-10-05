"""
Build script for 4Paws Agent Tray Launcher
Creates a standalone executable for the tray launcher
"""

import os
import sys
import shutil
from pathlib import Path

def clean_build_dirs():
    """Clean previous build directories"""
    # Clean build and cache directories
    dirs_to_clean = ['build', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"✓ Cleaned {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Clean dist directory but preserve existing files
    if os.path.exists('dist'):
        # Only remove tray_launcher related files
        tray_files = ['tray_launcher.exe', 'tray_launcher.spec']
        for item in os.listdir('dist'):
            if item in tray_files:
                item_path = os.path.join('dist', item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
        print(f"✓ Cleaned dist/ (preserved existing files)")

def build_tray_launcher():
    """Build tray launcher executable"""
    print("""
╔════════════════════════════════════════╗
║   4Paws Tray Launcher Build Script   ║
║   Creating Standalone Executable     ║
╚════════════════════════════════════════╝
""")
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create PyInstaller spec file
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['tray_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
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
    name='tray_launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/img/favicon.ico',
)
'''
    
    with open('tray_launcher.spec', 'w') as f:
        f.write(spec_content)
    
    print("✓ Created spec file")
    
    # Build executable
    print("▶ Building tray_launcher.exe...")
    os.system('pyinstaller tray_launcher.spec --clean')
    
    if os.path.exists('dist/tray_launcher.exe'):
        print("✓ Building tray_launcher.exe completed")
        return True
    else:
        print("❌ Build failed")
        return False

def main():
    """Main build process"""
    try:
        if build_tray_launcher():
            print("""
✅ Tray Launcher Build Complete!

Files created:
  📁 dist/tray_launcher.exe

Usage:
  • Copy tray_launcher.exe to your installation directory
  • Run it to launch tray interface when service is running
  • Creates shortcut in Start Menu during installation

The tray launcher will:
  ✅ Check if 4PawsAgent service is running
  ✅ Wait for agent to be ready (port 5000)
  ✅ Launch tray application in user session
  ✅ Provide system tray interface for service management
""")
        else:
            print("❌ Build failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
