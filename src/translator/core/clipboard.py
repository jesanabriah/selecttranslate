"""Clipboard monitoring module."""

import subprocess
import threading
import time
import logging
from typing import Callable, Optional
from ..config import CLIPBOARD_CONFIG

logger = logging.getLogger(__name__)


class ClipboardMonitor:
    """Monitors clipboard for text selections."""
    
    def __init__(self, 
                 command: str = None, 
                 polling_interval: float = None,
                 min_length: int = None,
                 max_length: int = None):
        """Initialize the clipboard monitor.
        
        Args:
            command: Clipboard command to use (e.g., 'xsel')
            polling_interval: How often to check clipboard in seconds
            min_length: Minimum text length to consider
            max_length: Maximum text length to consider
        """
        self.command = command or CLIPBOARD_CONFIG["command"]
        self.polling_interval = polling_interval or CLIPBOARD_CONFIG["polling_interval"]
        self.min_length = min_length or CLIPBOARD_CONFIG["min_length"]
        self.max_length = max_length or CLIPBOARD_CONFIG["max_length"]
        
        self.monitoring = False
        self.last_selection = ""
        self.callback: Optional[Callable[[str], None]] = None
        self.monitor_thread: Optional[threading.Thread] = None
        
    def start_monitoring(self, callback: Callable[[str], None]) -> bool:
        """Start monitoring clipboard for changes.
        
        Args:
            callback: Function to call when new text is selected
            
        Returns:
            True if monitoring started successfully, False otherwise
        """
        if self.monitoring:
            logger.warning("Clipboard monitoring is already running")
            return False
            
        if not self.is_available():
            logger.error(f"Clipboard tool {self.command} is not available")
            return False
            
        self.callback = callback
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Clipboard monitoring started")
        return True
    
    def stop_monitoring(self):
        """Stop clipboard monitoring."""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=1.0)
            logger.info("Clipboard monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop running in background thread."""
        while self.monitoring:
            try:
                current_selection = self._get_selection()
                
                if (current_selection and
                    current_selection != self.last_selection and
                    self.min_length <= len(current_selection) <= self.max_length):
                    
                    logger.debug(f"New selection detected: {current_selection[:50]}...")
                    self.last_selection = current_selection
                    
                    if self.callback:
                        self.callback(current_selection)
                        
            except Exception as e:
                logger.error(f"Error in clipboard monitoring: {e}")
                
            time.sleep(self.polling_interval)
    
    def _get_selection(self) -> Optional[str]:
        """Get current clipboard selection.
        
        Returns:
            Selected text or None if no selection/error
        """
        try:
            result = subprocess.run(
                [self.command, '-o'],
                capture_output=True,
                text=True,
                timeout=1
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
    
    def is_available(self) -> bool:
        """Check if the clipboard tool is available.
        
        Returns:
            True if tool is available, False otherwise
        """
        try:
            result = subprocess.run(
                [self.command, '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            try:
                # Try with help flag
                result = subprocess.run(
                    [self.command, '--help'],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode in [0, 1]  # Some tools return 1 for help
            except (FileNotFoundError, subprocess.TimeoutExpired):
                return False