"""
Path utilities for 4Paws Agent
Handles base directory and writable directory detection
"""

import os
import sys
from pathlib import Path


def get_base_dir() -> Path:
    """
    Get base directory (where executable/script is located)
    
    Returns:
        Path: Base directory path
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base = Path(sys.executable).parent
    else:
        # Running as script - need to go up one level from core/
        base = Path(__file__).parent.parent.absolute()
    
    # Check if we're in Program Files (read-only location)
    base_str = str(base).lower()
    if 'program files' in base_str or 'programdata' in base_str:
        # Use installation directory for tools/apps, but AppData for logs/data
        return base
    return base


def get_writable_dir() -> Path:
    """
    Get writable directory for logs and transient data
    
    If installed in Program Files, uses AppData\\Local\\4PawsAgent
    Otherwise uses the base directory
    
    Returns:
        Path: Writable directory path
    """
    base = get_base_dir()
    base_str = str(base).lower()
    
    if 'program files' in base_str or 'programdata' in base_str:
        # Use AppData\Local for writable files
        appdata = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
        writable = appdata / '4PawsAgent'
        writable.mkdir(parents=True, exist_ok=True)
        return writable
    
    return base
