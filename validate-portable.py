#!/usr/bin/env python3
"""
Portable Validation Script
Validates and fixes paths after copying to new location
"""

import sys
import subprocess
from pathlib import Path
from core import Config

def validate_and_fix():
    """Validate installation and fix if needed"""
    print("🔍 Validating portable installation...")
    print(f"📁 Base directory: {Config.BASE_DIR}")
    print()
    
    issues = []
    fixes_applied = []
    
    # 1. Check if tools exist
    print("1️⃣ Checking tools...")
    if not (Config.NODE_DIR / "node.exe").exists():
        issues.append("❌ Node.js not found")
    else:
        print("   ✅ Node.js found")
    
    if not (Config.PNPM_DIR / "pnpm.cmd").exists():
        issues.append("❌ pnpm not found")
    else:
        print("   ✅ pnpm found")
    
    if not (Config.MARIADB_DIR / "bin" / "mysqld.exe").exists():
        issues.append("❌ MariaDB not found")
    else:
        print("   ✅ MariaDB found")
    
    # 2. Check if apps exist
    print("\n2️⃣ Checking apps...")
    backend_exists = Config.BACKEND_DIR.exists()
    frontend_exists = Config.FRONTEND_DIR.exists()
    
    if backend_exists:
        print("   ✅ Backend found")
    else:
        issues.append("❌ Backend not found")
    
    if frontend_exists:
        print("   ✅ Frontend found")
    else:
        issues.append("❌ Frontend not found")
    
    # 3. Check and regenerate Prisma client if needed
    if backend_exists:
        print("\n3️⃣ Checking Prisma client...")
        prisma_client = Config.BACKEND_DIR / "node_modules" / ".prisma" / "client"
        
        if not prisma_client.exists():
            print("   ⚠️  Prisma client not found - needs regeneration")
            issues.append("⚠️  Prisma client missing")
            
            # Auto-fix: Regenerate Prisma client
            print("   🔧 Attempting to regenerate Prisma client...")
            try:
                pnpm_exe = Config.PNPM_DIR / "pnpm.exe"
                if pnpm_exe.exists():
                    # Prepare environment
                    import os
                    env = os.environ.copy()
                    node_dir = str(Config.NODE_DIR.absolute())
                    pnpm_dir = str(Config.PNPM_DIR.absolute())
                    env['PATH'] = f"{node_dir};{pnpm_dir};{env.get('PATH', '')}"
                    
                    result = subprocess.run(
                        [str(pnpm_exe), "prisma", "generate"],
                        cwd=str(Config.BACKEND_DIR),
                        env=env,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        print("   ✅ Prisma client regenerated successfully!")
                        fixes_applied.append("✅ Prisma client regenerated")
                    else:
                        print(f"   ❌ Failed to regenerate Prisma client: {result.stderr}")
                else:
                    print("   ❌ pnpm not found, cannot regenerate")
            except Exception as e:
                print(f"   ❌ Error regenerating Prisma client: {e}")
        else:
            print("   ✅ Prisma client found")
    
    # 4. Check database
    print("\n4️⃣ Checking database...")
    mariadb_data = Config.DATA_DIR / "mariadb"
    if mariadb_data.exists() and (mariadb_data / "mysql").exists():
        print("   ✅ MariaDB data directory found")
    else:
        print("   ⚠️  MariaDB data directory not initialized")
        issues.append("⚠️  MariaDB needs initialization")
    
    # Summary
    print("\n" + "=" * 60)
    if not issues:
        print("✅ Installation is valid and ready to use!")
        if fixes_applied:
            print("\n🔧 Fixes applied:")
            for fix in fixes_applied:
                print(f"   {fix}")
    else:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"   {issue}")
        
        print("\n💡 Recommended actions:")
        print("   1. If tools are missing, run: python agent.py setup")
        print("   2. If apps are missing, run: python agent.py install all")
        print("   3. If MariaDB not initialized, run: python agent.py setup")
    
    print("=" * 60)
    
    return len(issues) == 0

if __name__ == "__main__":
    try:
        success = validate_and_fix()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

