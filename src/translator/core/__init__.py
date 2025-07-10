"""Core translation functionality."""

from .translator import TranslationEngine
from .dictionary import DictionaryLookup
from .clipboard import ClipboardMonitor

__all__ = ["TranslationEngine", "DictionaryLookup", "ClipboardMonitor"]