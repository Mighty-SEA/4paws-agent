"""
Prepare files for NSIS installer build
This script copies all necessary files to the installer directory
"""

import os
import sys
import shutil
from pathlib import Path

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BLUE}{'=' * 50}")
    print(f"  {text}")
    print(f"{'=' * 50}{Colors.END}\n")

def check_prerequisites():
    """Check if all required files exist"""
    print_header("Checking Prerequisites")
    
    # Define paths
    base_dir = Path(__file__).parent.parent
    dist_dir = base_dir / "dist"
    assets_dir = base_dir / "installer" / "assets"
    
    required_files = {
        "4PawsAgent.exe": dist_dir / "4PawsAgent.exe",
        "Node.js ZIP": assets_dir / "node-v22.20.0-win-x64.zip",
        "MariaDB ZIP": assets_dir / "mariadb-12.0.2-winx64.zip",
        "pnpm.exe": assets_dir / "pnpm.exe"
    }
    
    all_ok = True
    for name, path in required_files.items():
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"{Colors.GREEN}✓{Colors.END} {name}: {size_mb:.1f} MB")
        else:
            print(f"{Colors.RED}✗{Colors.END} {name}: NOT FOUND at {path}")
            all_ok = False
    
    if not all_ok:
        print(f"\n{Colors.RED}ERROR: Some required files are missing!{Colors.END}")
        print("\nPlease ensure:")
        print("1. Run 'python build-exe.py' first to create 4PawsAgent.exe")
        print("2. Place node-v22.20.0-win-x64.zip in installer/assets/")
        print("3. Place mariadb-12.0.2-winx64.zip in installer/assets/")
        return False
    
    return True

def prepare_installer_files():
    """Copy files to installer directory for NSIS"""
    print_header("Preparing Installer Files")
    
    base_dir = Path(__file__).parent.parent
    installer_dir = base_dir / "installer"
    dist_dir = base_dir / "dist"
    assets_dir = installer_dir / "assets"
    
    # Copy executable to installer dir
    exe_src = dist_dir / "4PawsAgent.exe"
    exe_dst = installer_dir / "4PawsAgent.exe"
    
    print(f"📦 Copying 4PawsAgent.exe...")
    shutil.copy2(exe_src, exe_dst)
    print(f"{Colors.GREEN}✓{Colors.END} Copied executable")
    
    # Copy ZIP files to installer dir (NSIS needs them in same dir)
    node_src = assets_dir / "node-v22.20.0-win-x64.zip"
    node_dst = installer_dir / "node-temp.zip"
    
    print(f"📦 Copying Node.js ZIP...")
    shutil.copy2(node_src, node_dst)
    print(f"{Colors.GREEN}✓{Colors.END} Copied Node.js")
    
    mariadb_src = assets_dir / "mariadb-12.0.2-winx64.zip"
    mariadb_dst = installer_dir / "mariadb-temp.zip"
    
    print(f"📦 Copying MariaDB ZIP...")
    shutil.copy2(mariadb_src, mariadb_dst)
    print(f"{Colors.GREEN}✓{Colors.END} Copied MariaDB")
    
    # Copy pnpm.exe to installer dir
    pnpm_src = assets_dir / "pnpm.exe"
    pnpm_dst = installer_dir / "pnpm.exe"
    
    print(f"📦 Copying pnpm.exe...")
    shutil.copy2(pnpm_src, pnpm_dst)
    print(f"{Colors.GREEN}✓{Colors.END} Copied pnpm")
    
    print(f"\n{Colors.GREEN}✓ All files prepared!{Colors.END}")
    
    return True

def print_next_steps():
    """Print instructions for building installer"""
    print_header("Next Steps")
    
    print("Files are ready for NSIS installer build!")
    print("\n" + "=" * 50)
    print("TO BUILD THE INSTALLER:")
    print("=" * 50)
    
    print(f"\n{Colors.BOLD}Option 1: Using NSIS GUI{Colors.END}")
    print("1. Download NSIS from: https://nsis.sourceforge.io/Download")
    print("2. Install NSIS")
    print("3. Right-click installer/installer.nsi")
    print("4. Select 'Compile NSIS Script'")
    print("5. Wait for compilation (2-5 minutes)")
    print("6. Output: dist/4PawsAgent-Setup.exe (~145 MB)")
    
    print(f"\n{Colors.BOLD}Option 2: Using NSIS Command Line{Colors.END}")
    print("1. Install NSIS")
    print("2. Add NSIS to PATH")
    print("3. Run: makensis installer/installer.nsi")
    
    print(f"\n{Colors.BOLD}Option 3: Using build script{Colors.END}")
    print("1. Run: python build-installer.bat")
    print("   (This will auto-detect NSIS and compile)")
    
    print("\n" + "=" * 50)
    print(f"{Colors.YELLOW}⚠️  IMPORTANT:{Colors.END}")
    print("=" * 50)
    print("- NSIS must be installed to build the installer")
    print("- Compilation takes 2-5 minutes (compressing 145 MB)")
    print("- Result will be ~145 MB installer executable")
    print("- Installer includes Node.js + MariaDB bundled")
    
    print(f"\n{Colors.GREEN}📦 Ready to build installer!{Colors.END}\n")

def main():
    """Main function"""
    print(f"""
{Colors.BOLD}╔════════════════════════════════════════╗
║   4Paws Agent Installer Preparation   ║
║      Preparing NSIS Build Files       ║
╚════════════════════════════════════════╝{Colors.END}
""")
    
    # Check prerequisites
    if not check_prerequisites():
        return 1
    
    # Prepare files
    if not prepare_installer_files():
        return 1
    
    # Print next steps
    print_next_steps()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

