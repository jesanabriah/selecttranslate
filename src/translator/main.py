"""Main entry point for the SelectTranslate application."""

import sys
import argparse
import logging
from pathlib import Path

from .utils import setup_logging
from .ui import TranslatorWindow
from .config import get_config

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SelectTranslate - Simple GTK3-based translator for selected text"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="SelectTranslate 1.0.3"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Log file path (default: user config dir)"
    )
    
    parser.add_argument(
        "--no-console",
        action="store_true",
        help="Disable console logging"
    )
    
    parser.add_argument(
        "--config-dir",
        type=Path,
        help="Override default config directory"
    )
    
    return parser.parse_args()


def check_dependencies():
    """Check if required system dependencies are available."""
    from .core import TranslationEngine, ClipboardMonitor
    from .utils import WindowPositioner
    
    issues = []
    
    # Check translation engine
    engine = TranslationEngine()
    if not engine.is_available():
        issues.append("Apertium translation engine not found")
    
    
    # Check clipboard monitoring
    clipboard = ClipboardMonitor()
    if not clipboard.is_available():
        issues.append("Clipboard tool (xsel) not found")
    
    # Check window positioning
    positioner = WindowPositioner()
    if not positioner.is_available():
        issues.append("Window positioning tool (xdotool) not found")
    
    return issues


def main():
    """Main application entry point."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    setup_logging(
        level=args.log_level,
        log_file=args.log_file,
        console=not args.no_console
    )
    
    logger.info("Starting SelectTranslate v1.0.3")
    
    # Check system dependencies
    dependency_issues = check_dependencies()
    if dependency_issues:
        logger.warning("Some dependencies are missing:")
        for issue in dependency_issues:
            logger.warning(f"  - {issue}")
        logger.info("Application will start but some features may not work")
    
    try:
        # Create main window
        logger.info("Creating main window...")
        app = TranslatorWindow()
        
        # Show window
        app.show_all()
        logger.info("Application ready")
        
        # Print startup information
        print("🚀 SelectTranslate started")
        print("📋 Select text in any application for automatic translation")
        print("✏️ Or type directly in the application")
        
        # Start GTK main loop
        Gtk.main()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Please install required dependencies:")
        logger.error("  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()