"""Main application window."""

import logging
import threading
from typing import Optional

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from ..config import get_config, POSITIONING_CONFIG
from ..core import TranslationEngine, ClipboardMonitor
from ..utils import WindowPositioner
from .styles import StyleManager

logger = logging.getLogger(__name__)


class TranslatorWindow(Gtk.Window):
    """Main translator application window."""
    
    def __init__(self):
        """Initialize the translator window."""
        self.config = get_config()
        window_config = self.config["window"]
        
        super().__init__(title=window_config["title"])
        
        # Initialize components
        translation_config = self.config["translation"]
        self.translation_engine = TranslationEngine(
            provider=translation_config["provider"],
            source_lang=translation_config["source_lang"],
            target_lang=translation_config["target_lang"]
        )
        self.clipboard_monitor = ClipboardMonitor()
        self.window_positioner = WindowPositioner()
        self.style_manager = StyleManager()
        
        # State variables
        self.monitoring = True
        self.timer_id: Optional[int] = None
        
        # Configure window
        self._setup_window()
        
        # Create UI elements
        self._create_widgets()
        
        # Apply styles
        self._apply_styles()
        
        # Build interface
        self._build_ui()
        
        # Start clipboard monitoring
        self._start_clipboard_monitoring()
        
        logger.info("Translator window initialized")
    
    def _setup_window(self):
        """Configure window properties."""
        window_config = self.config["window"]
        
        self.set_default_size(
            window_config["default_width"],
            window_config["default_height"]
        )
        self.set_resizable(window_config["resizable"])
        self.set_size_request(
            window_config["default_width"],
            window_config["default_height"]
        )
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(0)
        
        # Connect destroy signal
        self.connect("destroy", self._on_destroy)
    
    def _create_widgets(self):
        """Create all UI widgets."""
        ui_config = self.config["ui"]
        
        # Menu bar
        self._create_menu_bar()
        
        # Text views
        self.text_view = Gtk.TextView()
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_view.get_style_context().add_class("text-input")
        self.text_buffer = self.text_view.get_buffer()
        self.text_buffer.connect("changed", self._on_text_changed)
        
        self.translation_text = Gtk.TextView()
        self.translation_text.set_editable(False)
        self.translation_text.set_wrap_mode(Gtk.WrapMode.WORD)
        self.translation_text.get_style_context().add_class("translation-output")
        
        
        # Buttons
        button_size = ui_config["button_size"]
        
        self.translate_btn = Gtk.Button(label="🔄")
        self.translate_btn.get_style_context().add_class("btn-primary")
        self.translate_btn.connect("clicked", self._on_translate_clicked)
        self.translate_btn.set_size_request(button_size, button_size)
        
        self.clear_btn = Gtk.Button(label="🗑️")
        self.clear_btn.connect("clicked", self._on_clear_clicked)
        self.clear_btn.set_size_request(button_size, button_size)
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        self.menu_bar = Gtk.MenuBar()
        
        # File menu
        file_menu = Gtk.Menu()
        file_menu_item = Gtk.MenuItem(label="Archivo")
        file_menu_item.set_submenu(file_menu)
        
        # Configuration menu item
        config_item = Gtk.MenuItem(label="Configuración...")
        config_item.connect("activate", self._on_config_clicked)
        file_menu.append(config_item)
        
        # Separator
        separator = Gtk.SeparatorMenuItem()
        file_menu.append(separator)
        
        # Exit menu item
        exit_item = Gtk.MenuItem(label="Salir")
        exit_item.connect("activate", self._on_exit_clicked)
        file_menu.append(exit_item)
        
        self.menu_bar.append(file_menu_item)
        
        # Help menu
        help_menu = Gtk.Menu()
        help_menu_item = Gtk.MenuItem(label="Ayuda")
        help_menu_item.set_submenu(help_menu)
        
        # About menu item
        about_item = Gtk.MenuItem(label="Acerca de...")
        about_item.connect("activate", self._on_about_clicked)
        help_menu.append(about_item)
        
        self.menu_bar.append(help_menu_item)
    
    def _apply_styles(self):
        """Apply CSS styles to the window."""
        try:
            # Try to load from file first, fallback to inline if needed
            if not self.style_manager.load_styles(self):
                logger.warning("Could not load CSS file, using inline styles")
                self._load_fallback_styles()
        except Exception as e:
            logger.error(f"Failed to apply styles: {e}")
            self._load_fallback_styles()
    
    def _load_fallback_styles(self):
        """Load fallback inline styles if CSS file fails."""
        fallback_css = """
        window { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 10px; padding: 16px; border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            border: 2px solid #8b5cf6;
        }
        .section-title { font-size: 12px; font-weight: 600; color: #e2e8f0; }
        .text-input {
            background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
            color: #f7fafc; border: 2px solid #68d391; border-radius: 8px;
            padding: 10px; font-size: 13px;
        }
        .translation-output {
            background: linear-gradient(135deg, #065f46 0%, #047857 100%);
            color: #d1fae5; border: 2px solid #10b981; border-radius: 8px;
            padding: 10px; font-size: 13px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white; border: none; padding: 8px; border-radius: 8px;
        }
        """
        self.style_manager.load_inline_styles(self, fallback_css)
    
    def _build_ui(self):
        """Build the user interface layout."""
        ui_config = self.config["ui"]
        spacing = ui_config["spacing"]
        
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)
        
        # Add menu bar
        main_box.pack_start(self.menu_bar, False, False, 0)
        
        # Main card
        main_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=spacing)
        main_card.get_style_context().add_class("card")
        main_box.pack_start(main_card, True, True, 0)
        
        # Create simple layout only
        self._create_simple_layout()
        
        # Add rows directly to main card
        main_card.pack_start(self.text_row, True, True, 0)
        main_card.pack_start(self.translation_row, True, True, 0)
    
    
    def _create_simple_layout(self):
        """Create simple two-row layout."""
        ui_config = self.config["ui"]
        spacing = ui_config["spacing"]
        
        # Row 1: Origin text + translate button
        self.text_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, 
            spacing=spacing
        )
        
        text_label = Gtk.Label(label="Origen:")
        text_label.get_style_context().add_class("section-title")
        self.text_row.pack_start(text_label, False, False, 0)
        
        text_scroll = Gtk.ScrolledWindow()
        text_scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC, 
            Gtk.PolicyType.AUTOMATIC
        )
        text_scroll.add(self.text_view)
        self.text_row.pack_start(text_scroll, True, True, 0)
        self.text_row.pack_start(self.translate_btn, False, False, 0)
        
        # Row 2: Translation + clear button
        self.translation_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, 
            spacing=spacing
        )
        
        translation_label = Gtk.Label(label="Salida:")
        translation_label.get_style_context().add_class("section-title")
        self.translation_row.pack_start(translation_label, False, False, 0)
        
        translation_scroll = Gtk.ScrolledWindow()
        translation_scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC, 
            Gtk.PolicyType.AUTOMATIC
        )
        translation_scroll.add(self.translation_text)
        self.translation_row.pack_start(translation_scroll, True, True, 0)
        self.translation_row.pack_start(self.clear_btn, False, False, 0)
    
    
    
    def _on_text_changed(self, buffer):
        """Handle text buffer changes."""
        # Cancel previous timer
        if self.timer_id:
            GLib.source_remove(self.timer_id)
        
        # Set new timer for auto-translation
        delay = self.config["translation"]["auto_translate_delay"]
        self.timer_id = GLib.timeout_add(delay, self._auto_translate)
    
    def _auto_translate(self):
        """Perform automatic translation after delay."""
        text = self._get_text_content()
        
        if text and len(text) > 1:
            self._translate_text(text)
        
        self.timer_id = None
        return False  # Don't repeat timer
    
    def _on_translate_clicked(self, button):
        """Handle translate button click."""
        text = self._get_text_content()
        
        if text:
            self._translate_text(text)
        else:
            logger.warning("No text to translate")
    
    def _on_clear_clicked(self, button):
        """Handle clear button click."""
        self.text_buffer.set_text("")
        self.translation_text.get_buffer().set_text("")
        logger.info("Content cleared")
    
    def _get_text_content(self) -> str:
        """Get current text content from buffer."""
        start_iter = self.text_buffer.get_start_iter()
        end_iter = self.text_buffer.get_end_iter()
        return self.text_buffer.get_text(start_iter, end_iter, True).strip()
    
    def _translate_text(self, text: str):
        """Translate text in background thread."""
        def translate_worker():
            logger.info(f"Translating text: {text[:50]}...")
            
            # Translate text
            success, translation = self.translation_engine.translate(text)
            
            # Update UI in main thread
            GLib.idle_add(self._update_translation_ui, translation)
        
        # Run translation in background thread
        thread = threading.Thread(target=translate_worker, daemon=True)
        thread.start()
    
    def _update_translation_ui(self, translation: str):
        """Update UI with translation results."""
        # Update translation text
        self.translation_text.get_buffer().set_text(translation)
        
        logger.info("Translation UI updated")
        return False  # Don't repeat
    
    def _start_clipboard_monitoring(self):
        """Start monitoring clipboard for text selections."""
        def on_selection(text: str):
            logger.info(f"Text selected: {text[:50]}...")
            GLib.idle_add(self._handle_selection, text)
        
        if self.clipboard_monitor.start_monitoring(on_selection):
            logger.info("Clipboard monitoring started")
        else:
            logger.warning("Could not start clipboard monitoring")
    
    def _handle_selection(self, text: str):
        """Handle text selection from clipboard."""
        self.text_buffer.set_text(text)
        self._translate_text(text)
        self._position_near_cursor()
        return False  # Don't repeat
    
    def _position_near_cursor(self):
        """Position window near cursor intelligently."""
        try:
            cursor_pos = self.window_positioner.get_cursor_position()
            if not cursor_pos:
                self.set_position(Gtk.WindowPosition.CENTER)
                return
            
            cursor_x, cursor_y = cursor_pos
            
            # Get screen dimensions
            screen = self.get_screen()
            screen_width = screen.get_width()
            screen_height = screen.get_height()
            
            # Get window dimensions
            window_config = self.config["window"]
            window_width = window_config["default_width"]
            window_height = window_config["default_height"]
            
            # Calculate position
            new_x, new_y = self.window_positioner.calculate_window_position(
                cursor_x, cursor_y,
                window_width, window_height,
                screen_width, screen_height
            )
            
            # Move window
            self.move(new_x, new_y)
            
            # Bring to front temporarily
            self.present()
            self.set_keep_above(True)
            
            # Remove keep above after delay
            keep_above_duration = POSITIONING_CONFIG["keep_above_duration"]
            GLib.timeout_add(
                keep_above_duration,
                lambda: self.set_keep_above(False)
            )
            
        except Exception as e:
            logger.error(f"Error positioning window: {e}")
            self.set_position(Gtk.WindowPosition.CENTER)
    
    def _on_config_clicked(self, widget):
        """Handle configuration menu item click."""
        from .config_window import ConfigWindow
        config_window = ConfigWindow(self)
        config_window.show_all()
    
    def _on_exit_clicked(self, widget):
        """Handle exit menu item click."""
        self._on_destroy(widget)
    
    def _on_about_clicked(self, widget):
        """Handle about menu item click."""
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for(self)
        about_dialog.set_modal(True)
        about_dialog.set_program_name("SelectTranslate")
        about_dialog.set_version("1.0.0")
        about_dialog.set_comments("Simple translator for selected text")
        about_dialog.set_website("https://github.com/jesanabriah/selecttranslate")
        about_dialog.set_website_label("GitHub Repository")
        about_dialog.set_authors(["Jorge Sanabria"])
        about_dialog.set_copyright("© 2025 Jorge Sanabria")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.run()
        about_dialog.destroy()
    
    def _on_destroy(self, widget):
        """Handle window destruction."""
        self.monitoring = False
        self.clipboard_monitor.stop_monitoring()
        logger.info("Translator window destroyed")
        Gtk.main_quit()


def main():
    """Main entry point for the application."""
    from ..utils import setup_logging
    
    # Set up logging
    setup_logging(level="INFO", console=True)
    
    logger.info("Starting SelectTranslator")
    
    # Create and show main window
    app = TranslatorWindow()
    app.show_all()
    
    # Check dependencies
    logger.info("Checking system dependencies...")
    if not app.translation_engine.is_available():
        logger.warning("Translation engine not available")
    if not app.clipboard_monitor.is_available():
        logger.warning("Clipboard monitoring not available")
    if not app.window_positioner.is_available():
        logger.warning("Window positioning not available")
    
    logger.info("Application ready")
    
    try:
        Gtk.main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    main()