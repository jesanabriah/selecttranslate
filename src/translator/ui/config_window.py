"""Configuration window for SelectTranslate."""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ..config import TRANSLATION_CONFIG, PROVIDER_CONFIGS, get_user_config_dir
from ..core.translator import TranslationEngine

logger = logging.getLogger(__name__)


class ConfigWindow(Gtk.Window):
    """Configuration window for SelectTranslate."""
    
    def __init__(self, parent: Gtk.Window):
        """Initialize the configuration window.
        
        Args:
            parent: Parent window
        """
        super().__init__(title="Configuración - SelectTranslate")
        
        self.parent = parent
        self.config_changes = {}
        self.engine = TranslationEngine()
        
        # Configure window
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(500, 400)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        
        # Create UI
        self._create_widgets()
        self._build_ui()
        self._load_current_config()
        
        # Connect signals
        self.connect("destroy", self._on_destroy)
        
        logger.info("Configuration window initialized")
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Notebook for tabs
        self.notebook = Gtk.Notebook()
        
        # Provider selection tab
        self._create_provider_tab()
        
        # Language selection tab
        self._create_language_tab()
        
        # Advanced settings tab
        self._create_advanced_tab()
        
        # Buttons
        self.button_box = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        self.button_box.set_layout(Gtk.ButtonBoxStyle.END)
        self.button_box.set_spacing(10)
        
        self.cancel_btn = Gtk.Button(label="Cancelar")
        self.cancel_btn.connect("clicked", self._on_cancel_clicked)
        self.button_box.add(self.cancel_btn)
        
        self.apply_btn = Gtk.Button(label="Aplicar")
        self.apply_btn.connect("clicked", self._on_apply_clicked)
        self.button_box.add(self.apply_btn)
        
        self.ok_btn = Gtk.Button(label="Aceptar")
        self.ok_btn.get_style_context().add_class("suggested-action")
        self.ok_btn.connect("clicked", self._on_ok_clicked)
        self.button_box.add(self.ok_btn)
    
    def _create_provider_tab(self):
        """Create provider selection tab."""
        # Container
        provider_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        provider_box.set_border_width(20)
        
        # Title
        title_label = Gtk.Label()
        title_label.set_markup("<b>Proveedor de Traducción</b>")
        title_label.set_halign(Gtk.Align.START)
        provider_box.pack_start(title_label, False, False, 0)
        
        # Provider selection
        providers_group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        self.provider_radios = {}
        first_radio = None
        
        for provider_name, provider_config in PROVIDER_CONFIGS.items():
            if first_radio is None:
                radio = Gtk.RadioButton.new_with_label(None, provider_name.title())
                first_radio = radio
            else:
                radio = Gtk.RadioButton.new_with_label_from_widget(first_radio, provider_name.title())
            
            # Add description
            description_label = Gtk.Label()
            description_label.set_markup(f"<small>{provider_config['description']}</small>")
            description_label.set_halign(Gtk.Align.START)
            description_label.set_margin_left(25)
            
            # Status indicator
            status_label = Gtk.Label()
            try:
                temp_engine = TranslationEngine(provider=provider_name)
                if temp_engine.is_available():
                    status_label.set_markup('<small><span color="green">✓ Disponible</span></small>')
                else:
                    status_label.set_markup('<small><span color="red">✗ No disponible</span></small>')
            except Exception:
                status_label.set_markup('<small><span color="red">✗ Error</span></small>')
            
            status_label.set_halign(Gtk.Align.START)
            status_label.set_margin_left(25)
            
            providers_group.pack_start(radio, False, False, 0)
            providers_group.pack_start(description_label, False, False, 0)
            providers_group.pack_start(status_label, False, False, 0)
            
            self.provider_radios[provider_name] = radio
            radio.connect("toggled", self._on_provider_changed)
        
        provider_box.pack_start(providers_group, False, False, 0)
        
        # Provider-specific settings
        self.provider_settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        provider_box.pack_start(self.provider_settings_box, True, True, 0)
        
        # Add to notebook
        self.notebook.append_page(provider_box, Gtk.Label(label="Proveedor"))
    
    def _create_language_tab(self):
        """Create language selection tab."""
        # Container
        lang_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        lang_box.set_border_width(20)
        
        # Title
        title_label = Gtk.Label()
        title_label.set_markup("<b>Idiomas</b>")
        title_label.set_halign(Gtk.Align.START)
        lang_box.pack_start(title_label, False, False, 0)
        
        # Language selection grid
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        
        # Source language
        source_label = Gtk.Label(label="Idioma origen:")
        source_label.set_halign(Gtk.Align.START)
        grid.attach(source_label, 0, 0, 1, 1)
        
        self.source_combo = Gtk.ComboBoxText()
        self._populate_language_combo(self.source_combo)
        grid.attach(self.source_combo, 1, 0, 1, 1)
        
        # Target language
        target_label = Gtk.Label(label="Idioma destino:")
        target_label.set_halign(Gtk.Align.START)
        grid.attach(target_label, 0, 1, 1, 1)
        
        self.target_combo = Gtk.ComboBoxText()
        self._populate_language_combo(self.target_combo)
        grid.attach(self.target_combo, 1, 1, 1, 1)
        
        # Swap button
        swap_btn = Gtk.Button(label="⇄ Intercambiar")
        swap_btn.connect("clicked", self._on_swap_languages)
        grid.attach(swap_btn, 2, 0, 1, 2)
        
        lang_box.pack_start(grid, False, False, 0)
        
        # Add to notebook
        self.notebook.append_page(lang_box, Gtk.Label(label="Idiomas"))
    
    def _create_advanced_tab(self):
        """Create advanced settings tab."""
        # Container
        advanced_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        advanced_box.set_border_width(20)
        
        # Title
        title_label = Gtk.Label()
        title_label.set_markup("<b>Configuración Avanzada</b>")
        title_label.set_halign(Gtk.Align.START)
        advanced_box.pack_start(title_label, False, False, 0)
        
        # Settings grid
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        
        # Timeout setting
        timeout_label = Gtk.Label(label="Tiempo de espera (segundos):")
        timeout_label.set_halign(Gtk.Align.START)
        grid.attach(timeout_label, 0, 0, 1, 1)
        
        self.timeout_spin = Gtk.SpinButton()
        self.timeout_spin.set_range(5, 60)
        self.timeout_spin.set_increments(1, 5)
        self.timeout_spin.set_value(TRANSLATION_CONFIG.get("timeout", 10))
        grid.attach(self.timeout_spin, 1, 0, 1, 1)
        
        # Auto-translate delay
        delay_label = Gtk.Label(label="Retraso auto-traducción (ms):")
        delay_label.set_halign(Gtk.Align.START)
        grid.attach(delay_label, 0, 1, 1, 1)
        
        self.delay_spin = Gtk.SpinButton()
        self.delay_spin.set_range(500, 10000)
        self.delay_spin.set_increments(100, 500)
        self.delay_spin.set_value(TRANSLATION_CONFIG.get("auto_translate_delay", 2000))
        grid.attach(self.delay_spin, 1, 1, 1, 1)
        
        advanced_box.pack_start(grid, False, False, 0)
        
        # Add to notebook
        self.notebook.append_page(advanced_box, Gtk.Label(label="Avanzado"))
    
    def _populate_language_combo(self, combo: Gtk.ComboBoxText):
        """Populate language combo box.
        
        Args:
            combo: Combo box to populate
        """
        # Common languages with their codes
        languages = [
            ("en", "Inglés"),
            ("es", "Español"),
            ("fr", "Francés"),
            ("de", "Alemán"),
            ("it", "Italiano"),
            ("pt", "Portugués"),
            ("ru", "Ruso"),
            ("ja", "Japonés"),
            ("ko", "Coreano"),
            ("zh", "Chino"),
            ("ar", "Árabe"),
            ("hi", "Hindi"),
            ("nl", "Holandés"),
            ("pl", "Polaco"),
            ("sv", "Sueco"),
            ("da", "Danés"),
            ("no", "Noruego"),
            ("fi", "Finlandés"),
            ("ca", "Catalán"),
            ("eu", "Euskera"),
            ("gl", "Gallego"),
        ]
        
        for code, name in languages:
            combo.append(code, name)
    
    def _load_current_config(self):
        """Load current configuration into widgets."""
        from ..config import get_config
        
        # Get current configuration (includes user overrides)
        current_config = get_config()
        translation_config = current_config.get("translation", {})
        
        # Load provider selection
        current_provider = translation_config.get("provider", "apertium")
        if current_provider in self.provider_radios:
            self.provider_radios[current_provider].set_active(True)
        
        # Load language selection
        source_lang = translation_config.get("source_lang", "en")
        target_lang = translation_config.get("target_lang", "es")
        
        self.source_combo.set_active_id(source_lang)
        self.target_combo.set_active_id(target_lang)
        
        # Load advanced settings
        self.timeout_spin.set_value(translation_config.get("timeout", 10))
        self.delay_spin.set_value(translation_config.get("auto_translate_delay", 2000))
        
        # Store current config for provider settings loading
        self.current_full_config = current_config
        
        # Update provider settings
        self._update_provider_settings()
    
    def _update_provider_settings(self):
        """Update provider-specific settings based on selection."""
        # Clear existing settings
        for child in self.provider_settings_box.get_children():
            self.provider_settings_box.remove(child)
        
        # Get selected provider
        selected_provider = None
        for provider_name, radio in self.provider_radios.items():
            if radio.get_active():
                selected_provider = provider_name
                break
        
        if not selected_provider:
            return
        
        # Add provider-specific settings
        settings_label = Gtk.Label()
        settings_label.set_markup(f"<b>Configuración de {selected_provider.title()}</b>")
        settings_label.set_halign(Gtk.Align.START)
        self.provider_settings_box.pack_start(settings_label, False, False, 0)
        
        if selected_provider == "google":
            self._add_google_settings()
        elif selected_provider == "libretranslate":
            self._add_libretranslate_settings()
        elif selected_provider == "apertium":
            self._add_apertium_settings()
        
        self.provider_settings_box.show_all()
    
    def _add_google_settings(self):
        """Add Google Translate specific settings."""
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        
        # API Key
        api_label = Gtk.Label(label="API Key (opcional):")
        api_label.set_halign(Gtk.Align.START)
        grid.attach(api_label, 0, 0, 1, 1)
        
        self.google_api_entry = Gtk.Entry()
        self.google_api_entry.set_placeholder_text("Opcional - para mayor límite de uso")
        self.google_api_entry.set_visibility(False)  # Hide text for security
        grid.attach(self.google_api_entry, 1, 0, 1, 1)
        
        self.provider_settings_box.pack_start(grid, False, False, 0)
    
    def _add_libretranslate_settings(self):
        """Add LibreTranslate specific settings."""
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        
        # Service URL
        url_label = Gtk.Label(label="URL del servicio:")
        url_label.set_halign(Gtk.Align.START)
        grid.attach(url_label, 0, 0, 1, 1)
        
        self.libretranslate_url_entry = Gtk.Entry()
        self.libretranslate_url_entry.set_text(PROVIDER_CONFIGS["libretranslate"]["service_url"])
        grid.attach(self.libretranslate_url_entry, 1, 0, 1, 1)
        
        # API Key
        api_label = Gtk.Label(label="API Key (opcional):")
        api_label.set_halign(Gtk.Align.START)
        grid.attach(api_label, 0, 1, 1, 1)
        
        self.libretranslate_api_entry = Gtk.Entry()
        self.libretranslate_api_entry.set_placeholder_text("Opcional - para instancias privadas")
        self.libretranslate_api_entry.set_visibility(False)
        grid.attach(self.libretranslate_api_entry, 1, 1, 1, 1)
        
        self.provider_settings_box.pack_start(grid, False, False, 0)
    
    def _add_apertium_settings(self):
        """Add Apertium specific settings."""
        info_label = Gtk.Label()
        info_label.set_markup("<i>Apertium es un sistema de traducción local que no requiere configuración adicional.</i>")
        info_label.set_line_wrap(True)
        info_label.set_halign(Gtk.Align.START)
        self.provider_settings_box.pack_start(info_label, False, False, 0)
    
    def _build_ui(self):
        """Build the user interface."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)
        
        # Add notebook
        main_box.pack_start(self.notebook, True, True, 0)
        
        # Add buttons
        main_box.pack_start(self.button_box, False, False, 10)
    
    def _on_provider_changed(self, radio):
        """Handle provider selection change."""
        if radio.get_active():
            self._update_provider_settings()
    
    def _on_swap_languages(self, button):
        """Handle language swap button click."""
        source_id = self.source_combo.get_active_id()
        target_id = self.target_combo.get_active_id()
        
        if source_id and target_id:
            self.source_combo.set_active_id(target_id)
            self.target_combo.set_active_id(source_id)
    
    def _on_cancel_clicked(self, button):
        """Handle cancel button click."""
        self.destroy()
    
    def _on_apply_clicked(self, button):
        """Handle apply button click."""
        self._save_config()
    
    def _on_ok_clicked(self, button):
        """Handle OK button click."""
        self._save_config()
        self.destroy()
    
    def _save_config(self):
        """Save configuration changes."""
        try:
            # Get selected provider
            selected_provider = None
            for provider_name, radio in self.provider_radios.items():
                if radio.get_active():
                    selected_provider = provider_name
                    break
            
            # Get language selection
            source_lang = self.source_combo.get_active_id()
            target_lang = self.target_combo.get_active_id()
            
            # Build config
            new_config = {
                "provider": selected_provider,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "timeout": int(self.timeout_spin.get_value()),
                "auto_translate_delay": int(self.delay_spin.get_value())
            }
            
            # Add provider-specific settings
            provider_config = {}
            if selected_provider == "google" and hasattr(self, 'google_api_entry'):
                api_key = self.google_api_entry.get_text()
                if api_key:
                    provider_config["api_key"] = api_key
            elif selected_provider == "libretranslate":
                if hasattr(self, 'libretranslate_url_entry'):
                    provider_config["service_url"] = self.libretranslate_url_entry.get_text()
                if hasattr(self, 'libretranslate_api_entry'):
                    api_key = self.libretranslate_api_entry.get_text()
                    if api_key:
                        provider_config["api_key"] = api_key
            
            # Save to user config
            self._save_user_config(new_config, provider_config)
            
            # Update parent window's translation engine
            self._update_parent_engine(new_config, provider_config)
            
            logger.info(f"Configuration saved: {new_config}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            # Show error dialog
            error_dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error al guardar la configuración"
            )
            error_dialog.format_secondary_text(str(e))
            error_dialog.run()
            error_dialog.destroy()
    
    def _save_user_config(self, config: Dict[str, Any], provider_config: Dict[str, Any]):
        """Save configuration to user config file.
        
        Args:
            config: Main configuration
            provider_config: Provider-specific configuration
        """
        config_dir = get_user_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / "config.json"
        
        # Load existing config or create new
        if config_file.exists():
            with open(config_file, 'r') as f:
                user_config = json.load(f)
        else:
            user_config = {}
        
        # Update configuration
        user_config["translation"] = config
        if provider_config:
            if "providers" not in user_config:
                user_config["providers"] = {}
            user_config["providers"][config["provider"]] = provider_config
        
        # Save configuration
        with open(config_file, 'w') as f:
            json.dump(user_config, f, indent=2)
    
    def _update_parent_engine(self, config: Dict[str, Any], provider_config: Dict[str, Any]):
        """Update parent window's translation engine.
        
        Args:
            config: Main configuration
            provider_config: Provider-specific configuration
        """
        try:
            # Create new engine with updated config
            new_engine = TranslationEngine(
                provider=config["provider"],
                source_lang=config["source_lang"],
                target_lang=config["target_lang"],
                config=provider_config
            )
            
            # Update parent's engine
            self.parent.translation_engine = new_engine
            
            logger.info(f"Updated translation engine to {config['provider']}")
            
        except Exception as e:
            logger.error(f"Error updating translation engine: {e}")
    
    def _on_destroy(self, widget):
        """Handle window destruction."""
        logger.info("Configuration window destroyed")