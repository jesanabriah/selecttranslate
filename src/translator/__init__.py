"""SelectTranslator Application.

A GTK3-based real-time translator with intelligent positioning.
"""

__version__ = "1.0.0"
__author__ = "Jorge Sanabria"
__email__ = "js@jorels.com"
__description__ = "A simple GTK3-based real-time translator"

from .config import get_config
from .ui import TranslatorWindow
from .core import TranslationEngine, DictionaryLookup, ClipboardMonitor
from .utils import setup_logging, WindowPositioner

__all__ = [
    "get_config",
    "TranslatorWindow", 
    "TranslationEngine",
    "DictionaryLookup", 
    "ClipboardMonitor",
    "setup_logging",
    "WindowPositioner"
]