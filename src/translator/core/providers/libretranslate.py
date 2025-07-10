"""LibreTranslate provider implementation."""

import json
import logging
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List, Tuple, Any

from .base import TranslationProvider

logger = logging.getLogger(__name__)


class LibreTranslateProvider(TranslationProvider):
    """LibreTranslate provider for free and open source translation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the LibreTranslate provider.
        
        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.service_url = config.get("service_url", "https://libretranslate.de/translate")
        self.api_key = config.get("api_key")  # Optional for some instances
        
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[bool, str]:
        """Translate text using LibreTranslate API.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Tuple of (success: bool, result: str)
        """
        if not text.strip():
            return False, "Empty text provided"
        
        # Preprocess text
        text = self.preprocess_text(text)
        
        try:
            logger.debug(f"Translating with LibreTranslate: {text[:50]}...")
            
            # Prepare request data
            data = {
                'q': text,
                'source': source_lang,
                'target': target_lang
            }
            
            # Add API key if available
            if self.api_key:
                data['api_key'] = self.api_key
            
            # Encode data
            post_data = urllib.parse.urlencode(data).encode('utf-8')
            
            # Create request
            request = urllib.request.Request(
                self.service_url,
                data=post_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'SelectTranslate/1.0'
                }
            )
            
            # Make request
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if response.status == 200:
                    result = response.read().decode('utf-8')
                    translation = self._parse_response(result)
                    
                    if translation:
                        translation = self.postprocess_text(translation)
                        logger.debug(f"LibreTranslate translation successful: {translation[:50]}...")
                        return True, translation
                    else:
                        logger.error("Failed to parse LibreTranslate response")
                        return False, "Failed to parse translation response"
                else:
                    logger.error(f"LibreTranslate API error: {response.status}")
                    return False, f"API error: {response.status}"
                    
        except urllib.error.URLError as e:
            logger.error(f"Network error accessing LibreTranslate: {e}")
            return False, f"Network error: {str(e)}"
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LibreTranslate response: {e}")
            return False, "Invalid response format"
        except Exception as e:
            logger.error(f"Unexpected error with LibreTranslate: {e}")
            return False, f"Unexpected error: {str(e)}"
    
    def _parse_response(self, response_text: str) -> str:
        """Parse LibreTranslate API response.
        
        Args:
            response_text: Raw response text
            
        Returns:
            Translated text or empty string if parsing fails
        """
        try:
            data = json.loads(response_text)
            
            if isinstance(data, dict) and 'translatedText' in data:
                return data['translatedText']
            
            return ""
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Error parsing LibreTranslate response: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check if LibreTranslate is available.
        
        Returns:
            True if available, False otherwise
        """
        try:
            # Test with a simple translation
            data = {
                'q': 'hello',
                'source': 'en',
                'target': 'es'
            }
            
            if self.api_key:
                data['api_key'] = self.api_key
            
            post_data = urllib.parse.urlencode(data).encode('utf-8')
            
            request = urllib.request.Request(
                self.service_url,
                data=post_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'SelectTranslate/1.0'
                }
            )
            
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status == 200
                
        except Exception:
            return False
    
    def get_supported_languages(self) -> List[str]:
        """Get supported language codes.
        
        Returns:
            List of supported language codes
        """
        # LibreTranslate supports these languages (may vary by instance)
        return [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
            "ar", "hi", "nl", "pl", "sv", "da", "no", "fi", "el", "he",
            "tr", "cs", "hu", "ro", "bg", "hr", "sl", "sk", "lt", "lv",
            "et", "mt", "ga", "cy", "eu", "ca", "gl", "eo", "la", "fa",
            "ur", "bn", "ta", "te", "mr", "gu", "kn", "ml", "pa", "or",
            "as", "ne", "si", "my", "km", "lo", "ka", "am", "sw", "mg",
            "af", "sq", "az", "be", "bs", "mk", "mn", "sr", "uk", "uz",
            "vi", "th", "tl", "is", "lb", "jw", "su", "yo", "zu", "xh",
            "sn", "ig", "ha", "st", "so", "zu"
        ]