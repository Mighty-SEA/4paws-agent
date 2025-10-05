"""
Logging setup for 4Paws Agent
Custom handler for Web GUI integration
"""

import sys
import logging
from pathlib import Path


class LogManagerHandler(logging.Handler):
    """Handler that sends logs to LogManager for Web GUI"""
    
    def __init__(self):
        super().__init__()
        self._log_manager = None
    
    def set_log_manager(self, log_manager):
        """Set the log manager instance"""
        self._log_manager = log_manager
    
    def emit(self, record):
        """Emit log to LogManager"""
        if not self._log_manager:
            return
        
        try:
            msg = self.format(record)
            
            # Filter out Flask/Werkzeug HTTP access logs
            # These are logged by werkzeug logger and contain patterns like:
            # "127.0.0.1 - - [timestamp] "GET /api/..." or "POST /socket.io/..."
            if '127.0.0.1 - -' in msg or 'GET /' in msg or 'POST /' in msg:
                return  # Don't send HTTP access logs to Web GUI
            
            # Filter out SocketIO internal logs
            if 'socket.io' in msg.lower() or 'websocket' in msg.lower():
                return
            
            # Remove the timestamp prefix since LogManager adds its own
            # Format: "2025-10-04 13:25:15,660 - INFO - message"
            # We want just the message part
            parts = msg.split(' - ', 2)
            if len(parts) >= 3:
                message = parts[2]  # Get the actual message
            else:
                message = msg
            
            # Map logging levels to LogManager levels
            level_map = {
                'INFO': 'info',
                'WARNING': 'warning',
                'ERROR': 'error',
                'CRITICAL': 'error',
                'DEBUG': 'info'
            }
            level = level_map.get(record.levelname, 'info')
            
            # Send to LogManager
            self._log_manager.log(message, level=level)
        except Exception:
            pass  # Fail silently to not break the app


# Global log manager handler instance
_log_manager_handler = None


def get_log_manager_handler() -> LogManagerHandler:
    """Get the global log manager handler instance"""
    global _log_manager_handler
    if _log_manager_handler is None:
        raise RuntimeError("Logging not initialized. Call setup_logging() first.")
    return _log_manager_handler


def setup_logging(log_file: Path) -> tuple:
    """
    Setup logging configuration
    
    Args:
        log_file: Path to log file
    
    Returns:
        tuple: (logger, log_manager_handler)
    """
    global _log_manager_handler
    
    # Create custom handler
    _log_manager_handler = LogManagerHandler()
    _log_manager_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    
    # Setup basic config
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(),
            _log_manager_handler  # Add our custom handler
        ]
    )
    
    # Set console output to UTF-8 for emoji support
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass
    
    logger = logging.getLogger(__name__)
    return logger, _log_manager_handler
