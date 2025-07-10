"""Configuration module for the SelectTranslate application."""

import os
from pathlib import Path
from typing import Dict, Any

# Application metadata
APP_NAME = "SelectTranslate"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A simple GTK3-based translator that translates selected text instantly"

# Window configuration
WINDOW_CONFIG = {
    "default_width": 420,
    "default_height": 320,
    "resizable": False,
    "title": "SelectTranslate",
}

# Translation configuration
TRANSLATION_CONFIG = {
    "provider": "apertium",  # Options: "apertium", "google", "libretranslate"
    "language_pair": "eng-spa",
    "source_lang": "en",
    "target_lang": "es", 
    "auto_translate_delay": 2000,  # milliseconds
    "timeout": 10,  # seconds
}

# Translation provider configurations
PROVIDER_CONFIGS = {
    "apertium": {
        "engine": "apertium",
        "language_pair": "eng-spa",
        "timeout": 10,
        "description": "Local offline translation using Apertium",
        "requires_internet": False,
        "supported_pairs": ["eng-spa", "spa-eng", "eng-fra", "fra-eng"]
    },
    "google": {
        "api_key": None,  # Set in user config if needed
        "service_url": "https://translate.googleapis.com/translate_v2",
        "timeout": 15,
        "description": "Google Translate API (requires API key for high volume)",
        "requires_internet": True,
        "supported_pairs": "auto"  # Google supports many language pairs
    },
    "libretranslate": {
        "service_url": "https://libretranslate.de/translate", 
        "api_key": None,  # Optional for some instances
        "timeout": 15,
        "description": "LibreTranslate - Free and open source translation",
        "requires_internet": True,
        "supported_pairs": "auto"
    }
}

# Dictionary configuration
DICTIONARY_CONFIG = {
    "command": "dict",
    "timeout": 5,  # seconds
    "max_lines": 8,  # lines to extract from dict output
    "skip_lines": 2,  # lines to skip from beginning
}

# Clipboard monitoring configuration
CLIPBOARD_CONFIG = {
    "command": "xsel",
    "polling_interval": 0.5,  # seconds
    "min_length": 1,
    "max_length": 500,
}

# Positioning configuration
POSITIONING_CONFIG = {
    "cursor_tool": "xdotool",
    "text_height": 25,  # pixels
    "margin": 15,  # pixels
    "title_bar_height": 30,  # pixels
    "keep_above_duration": 3000,  # milliseconds
}

# UI styling
UI_CONFIG = {
    "spacing": 6,
    "button_size": 35,
    "card_padding": 16,
    "card_margin": 10,
    "border_radius": 12,
}

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
DOCS_DIR = PROJECT_ROOT / "docs"

# CSS file path
CSS_FILE = ASSETS_DIR / "styles.css"

def get_config() -> Dict[str, Any]:
    """Get the complete application configuration."""
    config = {
        "app": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "description": APP_DESCRIPTION,
        },
        "window": WINDOW_CONFIG,
        "translation": TRANSLATION_CONFIG.copy(),
        "dictionary": DICTIONARY_CONFIG,
        "clipboard": CLIPBOARD_CONFIG,
        "positioning": POSITIONING_CONFIG,
        "ui": UI_CONFIG,
        "paths": {
            "project_root": PROJECT_ROOT,
            "assets": ASSETS_DIR,
            "docs": DOCS_DIR,
            "css": CSS_FILE,
        },
    }
    
    # Load user configuration if it exists
    user_config = load_user_config()
    if user_config:
        # Merge user config with default config
        if "translation" in user_config:
            config["translation"].update(user_config["translation"])
        if "providers" in user_config:
            # Update provider configs with user settings
            for provider_name, provider_settings in user_config["providers"].items():
                if provider_name in PROVIDER_CONFIGS:
                    PROVIDER_CONFIGS[provider_name].update(provider_settings)
    
    return config

def load_user_config() -> Dict[str, Any]:
    """Load user configuration from file.
    
    Returns:
        User configuration dictionary or empty dict if not found
    """
    import json
    
    config_dir = get_user_config_dir()
    config_file = config_dir / "config.json"
    
    if not config_file.exists():
        return {}
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        # Log error but don't fail
        print(f"Warning: Could not load user config: {e}")
        return {}

def get_user_config_dir() -> Path:
    """Get the user configuration directory."""
    if os.name == "posix":
        config_home = os.environ.get("XDG_CONFIG_HOME")
        if config_home:
            return Path(config_home) / "selecttranslate"
        else:
            return Path.home() / ".config" / "selecttranslate"
    else:
        return Path.home() / ".selecttranslate"