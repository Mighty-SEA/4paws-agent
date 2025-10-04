"""
Shortcut Manager for 4Paws Agent
Creates desktop and start menu shortcuts to the frontend application
"""

import os
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ShortcutManager:
    """Manages desktop and start menu shortcuts"""
    
    @staticmethod
    def create_url_shortcut(url, name, location):
        """Create a .url shortcut file for web application"""
        try:
            # Create .url file content
            shortcut_content = f"""[InternetShortcut]
URL={url}
IconIndex=0
IconFile={Path(__file__).parent / 'static' / 'img' / 'favicon.ico'}
"""
            
            # Create shortcut file
            shortcut_path = Path(location) / f"{name}.url"
            shortcut_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(shortcut_path, 'w') as f:
                f.write(shortcut_content)
            
            logger.info(f"✅ Created shortcut: {shortcut_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create shortcut at {location}: {e}")
            return False
    
    @staticmethod
    def get_desktop_path():
        """Get user's desktop path"""
        if os.name == 'nt':  # Windows
            return Path(os.path.expanduser("~")) / "Desktop"
        else:
            return Path(os.path.expanduser("~")) / "Desktop"
    
    @staticmethod
    def get_start_menu_path():
        """Get start menu programs path"""
        if os.name == 'nt':  # Windows
            # Try user start menu first
            start_menu = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            if not start_menu.exists():
                # Fallback to all users
                start_menu = Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            return start_menu
        else:
            return Path(os.path.expanduser("~")) / ".local" / "share" / "applications"
    
    @staticmethod
    def create_frontend_shortcuts(port=3100):
        """Create shortcuts to frontend application"""
        url = f"http://localhost:{port}"
        name = "4Paws Pet Management"
        
        results = {
            'desktop': False,
            'start_menu': False
        }
        
        # Create desktop shortcut
        try:
            desktop_path = ShortcutManager.get_desktop_path()
            if desktop_path.exists():
                results['desktop'] = ShortcutManager.create_url_shortcut(url, name, desktop_path)
                if results['desktop']:
                    print(f"✅ Desktop shortcut created: {desktop_path / f'{name}.url'}")
            else:
                logger.warning(f"⚠️  Desktop path not found: {desktop_path}")
        except Exception as e:
            logger.error(f"❌ Failed to create desktop shortcut: {e}")
        
        # Create start menu shortcut
        try:
            start_menu_path = ShortcutManager.get_start_menu_path() / "4Paws"
            if ShortcutManager.create_url_shortcut(url, name, start_menu_path):
                results['start_menu'] = True
                print(f"✅ Start Menu shortcut created: {start_menu_path / f'{name}.url'}")
        except Exception as e:
            logger.error(f"❌ Failed to create start menu shortcut: {e}")
        
        return results
    
    @staticmethod
    def remove_frontend_shortcuts():
        """Remove frontend shortcuts"""
        name = "4Paws Pet Management"
        removed = []
        
        # Remove desktop shortcut
        try:
            desktop_path = ShortcutManager.get_desktop_path()
            shortcut = desktop_path / f"{name}.url"
            if shortcut.exists():
                shortcut.unlink()
                removed.append('desktop')
                logger.info(f"✅ Removed desktop shortcut")
        except Exception as e:
            logger.error(f"❌ Failed to remove desktop shortcut: {e}")
        
        # Remove start menu shortcut
        try:
            start_menu_path = ShortcutManager.get_start_menu_path() / "4Paws"
            shortcut = start_menu_path / f"{name}.url"
            if shortcut.exists():
                shortcut.unlink()
                removed.append('start_menu')
                logger.info(f"✅ Removed start menu shortcut")
                
                # Remove folder if empty
                if start_menu_path.exists() and not any(start_menu_path.iterdir()):
                    start_menu_path.rmdir()
                    logger.info(f"✅ Removed empty folder: {start_menu_path}")
        except Exception as e:
            logger.error(f"❌ Failed to remove start menu shortcut: {e}")
        
        return removed
    
    @staticmethod
    def check_shortcuts_exist():
        """Check if shortcuts exist"""
        name = "4Paws Pet Management"
        
        desktop_path = ShortcutManager.get_desktop_path() / f"{name}.url"
        start_menu_path = ShortcutManager.get_start_menu_path() / "4Paws" / f"{name}.url"
        
        return {
            'desktop': desktop_path.exists(),
            'start_menu': start_menu_path.exists()
        }


def main():
    """CLI for shortcut manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage 4Paws shortcuts')
    parser.add_argument('action', choices=['create', 'remove', 'check'], 
                       help='Action to perform')
    parser.add_argument('--port', type=int, default=3100,
                       help='Frontend port (default: 3100)')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        print("🔗 Creating shortcuts...")
        results = ShortcutManager.create_frontend_shortcuts(args.port)
        
        if results['desktop'] and results['start_menu']:
            print("\n✅ All shortcuts created successfully!")
        elif results['desktop'] or results['start_menu']:
            print("\n⚠️  Some shortcuts created")
        else:
            print("\n❌ Failed to create shortcuts")
    
    elif args.action == 'remove':
        print("🗑️  Removing shortcuts...")
        removed = ShortcutManager.remove_frontend_shortcuts()
        
        if removed:
            print(f"\n✅ Removed shortcuts: {', '.join(removed)}")
        else:
            print("\n❌ No shortcuts found to remove")
    
    elif args.action == 'check':
        print("🔍 Checking shortcuts...")
        shortcuts = ShortcutManager.check_shortcuts_exist()
        
        print(f"\nDesktop: {'✅ Exists' if shortcuts['desktop'] else '❌ Not found'}")
        print(f"Start Menu: {'✅ Exists' if shortcuts['start_menu'] else '❌ Not found'}")


if __name__ == '__main__':
    main()

