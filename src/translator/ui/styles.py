"""GTK style management."""

import logging
from pathlib import Path
from typing import Optional

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ..config import CSS_FILE

logger = logging.getLogger(__name__)


class StyleManager:
    """Manages GTK styles and CSS loading."""
    
    def __init__(self, css_file: Optional[Path] = None):
        """Initialize the style manager.
        
        Args:
            css_file: Path to CSS file (default: from config)
        """
        self.css_file = css_file or CSS_FILE
        self.provider: Optional[Gtk.CssProvider] = None
        
    def load_styles(self, widget: Gtk.Widget) -> bool:
        """Load and apply CSS styles to a widget.
        
        Args:
            widget: Widget to apply styles to
            
        Returns:
            True if styles loaded successfully, False otherwise
        """
        try:
            if not self.css_file.exists():
                logger.error(f"CSS file not found: {self.css_file}")
                return False
                
            # Create CSS provider
            self.provider = Gtk.CssProvider()
            
            # Load CSS from file
            self.provider.load_from_path(str(self.css_file))
            
            # Apply to screen
            screen = widget.get_screen()
            Gtk.StyleContext.add_provider_for_screen(
                screen,
                self.provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            
            logger.info(f"CSS styles loaded from: {self.css_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load CSS styles: {e}")
            return False
    
    def load_inline_styles(self, widget: Gtk.Widget, css_data: str) -> bool:
        """Load CSS styles from string data.
        
        Args:
            widget: Widget to apply styles to
            css_data: CSS data as string
            
        Returns:
            True if styles loaded successfully, False otherwise
        """
        try:
            # Create CSS provider
            self.provider = Gtk.CssProvider()
            
            # Load CSS from data
            self.provider.load_from_data(css_data.encode('utf-8'))
            
            # Apply to screen
            screen = widget.get_screen()
            Gtk.StyleContext.add_provider_for_screen(
                screen,
                self.provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            
            logger.info("Inline CSS styles loaded")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load inline CSS styles: {e}")
            return False
    
    def unload_styles(self, widget: Gtk.Widget):
        """Remove loaded styles from widget.
        
        Args:
            widget: Widget to remove styles from
        """
        if self.provider:
            try:
                screen = widget.get_screen()
                Gtk.StyleContext.remove_provider_for_screen(
                    screen,
                    self.provider
                )
                logger.info("CSS styles unloaded")
            except Exception as e:
                logger.error(f"Failed to unload styles: {e}")