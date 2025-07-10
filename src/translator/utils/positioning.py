"""Window positioning utilities."""

import subprocess
import logging
from typing import Tuple, Optional
from ..config import POSITIONING_CONFIG

logger = logging.getLogger(__name__)


class WindowPositioner:
    """Handles intelligent window positioning relative to cursor."""
    
    def __init__(self, 
                 cursor_tool: str = None,
                 text_height: int = None,
                 margin: int = None,
                 title_bar_height: int = None):
        """Initialize the window positioner.
        
        Args:
            cursor_tool: Tool to get cursor position (e.g., 'xdotool')
            text_height: Height of text line in pixels
            margin: Margin around positioned window in pixels
            title_bar_height: Height of window title bar in pixels
        """
        self.cursor_tool = cursor_tool or POSITIONING_CONFIG["cursor_tool"]
        self.text_height = text_height or POSITIONING_CONFIG["text_height"]
        self.margin = margin or POSITIONING_CONFIG["margin"]
        self.title_bar_height = title_bar_height or POSITIONING_CONFIG["title_bar_height"]
        
    def get_cursor_position(self) -> Optional[Tuple[int, int]]:
        """Get current cursor position.
        
        Returns:
            Tuple of (x, y) coordinates or None if failed
        """
        try:
            result = subprocess.run(
                [self.cursor_tool, 'getmouselocation', '--shell'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                x = int(lines[0].split('=')[1])
                y = int(lines[1].split('=')[1])
                logger.debug(f"Cursor position: ({x}, {y})")
                return (x, y)
            else:
                logger.error("Failed to get cursor position")
                return None
                
        except (subprocess.TimeoutExpired, FileNotFoundError, 
                IndexError, ValueError) as e:
            logger.error(f"Error getting cursor position: {e}")
            return None
    
    def calculate_window_position(self, 
                                cursor_x: int, 
                                cursor_y: int,
                                window_width: int, 
                                window_height: int,
                                screen_width: int, 
                                screen_height: int) -> Tuple[int, int]:
        """Calculate optimal window position.
        
        Args:
            cursor_x: Cursor X coordinate
            cursor_y: Cursor Y coordinate
            window_width: Width of window to position
            window_height: Height of window to position
            screen_width: Screen width
            screen_height: Screen height
            
        Returns:
            Tuple of (new_x, new_y) coordinates
        """
        new_x = cursor_x
        screen_middle = screen_height // 2
        
        if cursor_y <= screen_middle:
            # Upper half: position window below text
            new_y = cursor_y + self.text_height + self.margin
        else:
            # Lower half: position window above text
            new_y = (cursor_y - self.text_height - window_height - 
                    (self.margin * 2) - self.title_bar_height)
        
        # Ensure window stays within screen bounds
        if new_x + window_width > screen_width:
            new_x = screen_width - window_width - 10
            
        if new_y < 0:
            new_y = self.margin
        elif new_y + window_height > screen_height:
            new_y = screen_height - window_height - self.margin
            
        logger.debug(f"Calculated window position: ({new_x}, {new_y})")
        return (new_x, new_y)
    
    def is_available(self) -> bool:
        """Check if the cursor positioning tool is available.
        
        Returns:
            True if tool is available, False otherwise
        """
        try:
            result = subprocess.run(
                [self.cursor_tool, '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False