"""
Enhanced Log Manager for 4Paws Agent
Provides real-time log streaming, action tracking, and persistent storage
"""

import os
import logging
from datetime import datetime
from collections import deque
from threading import Lock
from typing import Optional, List, Dict
from pathlib import Path

class LogManager:
    """Central log manager with WebSocket broadcasting"""
    
    def __init__(self, max_buffer_size: int = 1000, log_file: Optional[Path] = None):
        """
        Initialize LogManager
        
        Args:
            max_buffer_size: Maximum number of log lines to keep in memory
            log_file: Path to persistent log file
        """
        self.buffer = deque(maxlen=max_buffer_size)
        self.buffer_lock = Lock()
        self.log_file = log_file
        self.socketio = None
        self.current_action: Optional[str] = None
        self.action_start_time: Optional[datetime] = None
        
        # Setup file logging
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def set_socketio(self, socketio):
        """Set SocketIO instance for real-time broadcasting"""
        self.socketio = socketio
    
    def start_action(self, action: str):
        """Mark the start of an action"""
        self.current_action = action
        self.action_start_time = datetime.now()
        self.log(f"▶️ Starting action: {action}", level='action', action=action)
    
    def end_action(self, action: str, success: bool = True):
        """Mark the end of an action"""
        if self.action_start_time:
            duration = (datetime.now() - self.action_start_time).total_seconds()
            status = "✅ Completed" if success else "❌ Failed"
            self.log(f"{status}: {action} (took {duration:.1f}s)", 
                    level='success' if success else 'error', 
                    action=action)
        
        self.current_action = None
        self.action_start_time = None
        
        # Broadcast action status
        if self.socketio:
            self.socketio.emit('action_status', {
                'action': action,
                'status': 'completed' if success else 'failed',
                'duration': duration if self.action_start_time else 0
            })
    
    def log(self, message: str, level: str = 'info', action: Optional[str] = None):
        """
        Add a log entry
        
        Args:
            message: Log message
            level: Log level (info, success, warning, error, action)
            action: Associated action name (optional)
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        action_tag = f"[{action}]" if action else ""
        
        # Emoji mapping
        emoji_map = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'action': '▶️'
        }
        
        # Create log entry
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'action': action or self.current_action,
            'message': message,
            'full_text': f"[{timestamp}] {action_tag} {message}"
        }
        
        # Add to buffer
        with self.buffer_lock:
            self.buffer.append(log_entry)
        
        # Write to file
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry['full_text'] + '\n')
            except Exception as e:
                print(f"Failed to write to log file: {e}")
        
        # Broadcast via WebSocket
        if self.socketio:
            self.socketio.emit('log_entry', log_entry)
        
        # Also log to console
        print(log_entry['full_text'])
    
    def info(self, message: str, action: Optional[str] = None):
        """Log info message"""
        self.log(message, level='info', action=action)
    
    def success(self, message: str, action: Optional[str] = None):
        """Log success message"""
        self.log(message, level='success', action=action)
    
    def warning(self, message: str, action: Optional[str] = None):
        """Log warning message"""
        self.log(message, level='warning', action=action)
    
    def error(self, message: str, action: Optional[str] = None):
        """Log error message"""
        self.log(message, level='error', action=action)
    
    def get_logs(self, action: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        Get log entries from buffer
        
        Args:
            action: Filter by action name (optional)
            limit: Maximum number of entries to return (optional)
        
        Returns:
            List of log entries
        """
        with self.buffer_lock:
            logs = list(self.buffer)
        
        # Filter by action if specified
        if action:
            logs = [log for log in logs if log.get('action') == action]
        
        # Apply limit
        if limit:
            logs = logs[-limit:]
        
        return logs
    
    def get_current_action(self) -> Optional[Dict]:
        """Get information about currently running action"""
        if not self.current_action:
            return None
        
        duration = 0
        if self.action_start_time:
            duration = (datetime.now() - self.action_start_time).total_seconds()
        
        return {
            'action': self.current_action,
            'start_time': self.action_start_time.isoformat() if self.action_start_time else None,
            'duration': duration
        }
    
    def clear_logs(self):
        """Clear log buffer"""
        with self.buffer_lock:
            self.buffer.clear()
        self.log("🗑️ Log buffer cleared", level='info')
    
    def get_log_file_content(self, lines: int = 1000) -> str:
        """
        Get content from log file
        
        Args:
            lines: Number of lines to read from end of file
        
        Returns:
            Log file content
        """
        if not self.log_file or not self.log_file.exists():
            return ""
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except Exception as e:
            return f"Error reading log file: {e}"


# Create global log manager instance
# This will be initialized by gui_server.py
log_manager: Optional[LogManager] = None


def init_log_manager(log_file: Path, socketio=None) -> LogManager:
    """Initialize global log manager"""
    global log_manager
    log_manager = LogManager(max_buffer_size=1000, log_file=log_file)
    if socketio:
        log_manager.set_socketio(socketio)
    return log_manager


def get_log_manager() -> Optional[LogManager]:
    """Get global log manager instance"""
    return log_manager

