"""Base class for translation providers."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class TranslationProvider(ABC):
    """Abstract base class for translation providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the translation provider.
        
        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config
        self.timeout = config.get("timeout", 10)
        self.description = config.get("description", "Unknown provider")
        self.requires_internet = config.get("requires_internet", True)
        
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[bool, str]:
        """Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en', 'es')
            target_lang: Target language code (e.g., 'en', 'es')
            
        Returns:
            Tuple of (success: bool, result: str)
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the translation provider is available.
        
        Returns:
            True if provider is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes.
        
        Returns:
            List of supported language codes
        """
        pass
    
    def get_name(self) -> str:
        """Get the provider name.
        
        Returns:
            Provider name
        """
        return self.__class__.__name__.replace("Provider", "")
    
    def get_description(self) -> str:
        """Get the provider description.
        
        Returns:
            Provider description
        """
        return self.description
    
    def requires_internet_connection(self) -> bool:
        """Check if provider requires internet connection.
        
        Returns:
            True if internet is required, False otherwise
        """
        return self.requires_internet
    
    def validate_language_pair(self, source_lang: str, target_lang: str) -> bool:
        """Validate if the language pair is supported.
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            True if language pair is supported, False otherwise
        """
        supported = self.get_supported_languages()
        if "auto" in supported:
            return True
        return source_lang in supported and target_lang in supported
    
    def get_word_count(self, text: str) -> int:
        """Get the word count of text.
        
        Args:
            text: Text to count words in
            
        Returns:
            Number of words
        """
        return len(text.strip().split())
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text before translation.
        
        Args:
            text: Text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Default preprocessing: strip whitespace
        return text.strip()
    
    def postprocess_text(self, text: str) -> str:
        """Postprocess text after translation.
        
        Args:
            text: Text to postprocess
            
        Returns:
            Postprocessed text
        """
        # Default postprocessing: strip whitespace
        return text.strip()