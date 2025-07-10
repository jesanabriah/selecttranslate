"""Tests for configuration module."""

import pytest
from pathlib import Path
from translator.config import get_config, get_user_config_dir


def test_get_config():
    """Test configuration loading."""
    config = get_config()
    
    # Check required sections exist
    assert "app" in config
    assert "window" in config
    assert "translation" in config
    assert "dictionary" in config
    assert "clipboard" in config
    assert "positioning" in config
    assert "ui" in config
    assert "paths" in config
    
    # Check app section
    assert config["app"]["name"] == "SelectTranslator"
    assert config["app"]["version"] == "1.0.0"
    
    # Check window config
    assert config["window"]["default_width"] == 420
    assert config["window"]["default_height"] == 320
    assert config["window"]["resizable"] is False


def test_get_user_config_dir():
    """Test user config directory detection."""
    config_dir = get_user_config_dir()
    
    assert isinstance(config_dir, Path)
    assert "selecttranslate" in str(config_dir)