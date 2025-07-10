"""Translation engine module."""

import logging
from typing import Optional, Tuple, Dict, Any
from ..config import TRANSLATION_CONFIG, PROVIDER_CONFIGS
from .providers import ApertiumProvider, GoogleProvider, LibreTranslateProvider

logger = logging.getLogger(__name__)


class TranslationEngine:
    """Handles text translation using configurable providers."""
    
    def __init__(self, provider: str = None, source_lang: str = None, target_lang: str = None, config: Dict[str, Any] = None):
        """Initialize the translation engine.
        
        Args:
            provider: Translation provider name ('apertium', 'google', 'libretranslate')
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'es')
            config: Additional configuration options
        """
        self.provider_name = provider or TRANSLATION_CONFIG["provider"]
        self.source_lang = source_lang or TRANSLATION_CONFIG["source_lang"]
        self.target_lang = target_lang or TRANSLATION_CONFIG["target_lang"]
        self.config = config or {}
        
        # Initialize the selected provider
        self.provider = self._create_provider(self.provider_name)
        
    def _create_provider(self, provider_name: str):
        """Create and return the specified translation provider.
        
        Args:
            provider_name: Name of the provider to create
            
        Returns:
            Translation provider instance
        """
        if provider_name not in PROVIDER_CONFIGS:
            logger.error(f"Unknown provider: {provider_name}")
            # Fall back to Apertium
            provider_name = "apertium"
        
        provider_config = PROVIDER_CONFIGS[provider_name].copy()
        provider_config.update(self.config)
        
        if provider_name == "apertium":
            return ApertiumProvider(provider_config)
        elif provider_name == "google":
            return GoogleProvider(provider_config)
        elif provider_name == "libretranslate":
            return LibreTranslateProvider(provider_config)
        else:
            logger.error(f"Provider {provider_name} not implemented")
            return ApertiumProvider(PROVIDER_CONFIGS["apertium"])
        
    def translate(self, text: str) -> Tuple[bool, str]:
        """Translate text using the configured provider.
        
        Args:
            text: Text to translate
            
        Returns:
            Tuple of (success: bool, result: str)
        """
        if not text.strip():
            return False, "Empty text provided"
        
        try:
            logger.debug(f"Translating with {self.provider_name}: {text[:50]}...")
            success, result = self.provider.translate(text, self.source_lang, self.target_lang)
            
            if success:
                logger.debug(f"Translation successful: {result[:50]}...")
            else:
                logger.error(f"Translation failed: {result}")
                
            return success, result
            
        except Exception as e:
            logger.error(f"Unexpected translation error: {e}")
            return False, f"Unexpected error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if the translation provider is available.
        
        Returns:
            True if provider is available, False otherwise
        """
        try:
            return self.provider.is_available()
        except Exception as e:
            logger.error(f"Error checking provider availability: {e}")
            return False
    
    def get_word_count(self, text: str) -> int:
        """Get the word count of text.
        
        Args:
            text: Text to count words in
            
        Returns:
            Number of words
        """
        return self.provider.get_word_count(text)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider.
        
        Returns:
            Dictionary with provider information
        """
        return {
            "name": self.provider.get_name(),
            "description": self.provider.get_description(),
            "requires_internet": self.provider.requires_internet_connection(),
            "supported_languages": self.provider.get_supported_languages(),
            "available": self.provider.is_available()
        }
    
    def switch_provider(self, provider_name: str, config: Dict[str, Any] = None) -> bool:
        """Switch to a different translation provider.
        
        Args:
            provider_name: Name of the new provider
            config: Additional configuration for the new provider
            
        Returns:
            True if switch was successful, False otherwise
        """
        try:
            old_provider = self.provider_name
            self.provider_name = provider_name
            
            if config:
                self.config.update(config)
            
            self.provider = self._create_provider(provider_name)
            
            logger.info(f"Switched translation provider from {old_provider} to {provider_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch provider to {provider_name}: {e}")
            return False
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available providers.
        
        Returns:
            Dictionary with provider information
        """
        providers = {}
        
        for name, config in PROVIDER_CONFIGS.items():
            try:
                provider = self._create_provider(name)
                providers[name] = {
                    "description": provider.get_description(),
                    "requires_internet": provider.requires_internet_connection(),
                    "available": provider.is_available(),
                    "supported_languages": provider.get_supported_languages()
                }
            except Exception as e:
                logger.error(f"Error getting info for provider {name}: {e}")
                providers[name] = {
                    "description": config.get("description", "Unknown"),
                    "requires_internet": config.get("requires_internet", True),
                    "available": False,
                    "supported_languages": []
                }
        
        return providers