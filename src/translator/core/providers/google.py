"""Google Translate provider implementation."""

import json
import logging
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List, Tuple, Any

from .base import TranslationProvider

logger = logging.getLogger(__name__)


class GoogleProvider(TranslationProvider):
    """Google Translate provider using free web API."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Google Translate provider.
        
        Args:
            config: Provider configuration
        """
        super().__init__(config)
        # Use free web API endpoint instead of paid API
        self.service_url = "https://translate.googleapis.com/translate_a/single"
        self.api_key = config.get("api_key")  # Optional for free tier
        
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[bool, str]:
        """Translate text using Google Translate free API.
        
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
            logger.debug(f"Translating with Google: {text[:50]}...")
            
            # Prepare parameters for free API
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            
            # Build URL
            url = f"{self.service_url}?{urllib.parse.urlencode(params)}"
            
            # Make request
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'SelectTranslate/1.0')
            
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if response.status == 200:
                    result = response.read().decode('utf-8')
                    translation = self._parse_response(result)
                    
                    if translation:
                        translation = self.postprocess_text(translation)
                        logger.debug(f"Google translation successful: {translation[:50]}...")
                        return True, translation
                    else:
                        logger.error("Failed to parse Google Translate response")
                        return False, "Failed to parse translation response"
                else:
                    logger.error(f"Google Translate API error: {response.status}")
                    return False, f"API error: {response.status}"
                    
        except urllib.error.URLError as e:
            logger.error(f"Network error accessing Google Translate: {e}")
            return False, f"Network error: {str(e)}"
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Google Translate response: {e}")
            return False, "Invalid response format"
        except Exception as e:
            logger.error(f"Unexpected error with Google Translate: {e}")
            return False, f"Unexpected error: {str(e)}"
    
    def _parse_response(self, response_text: str) -> str:
        """Parse Google Translate API response.
        
        Args:
            response_text: Raw response text
            
        Returns:
            Translated text or empty string if parsing fails
        """
        try:
            # Google's free API returns a JSON array
            data = json.loads(response_text)
            
            if data and isinstance(data, list) and len(data) > 0:
                # First element contains translation segments
                segments = data[0]
                if segments and isinstance(segments, list):
                    # Combine all translation segments
                    translation_parts = []
                    for segment in segments:
                        if isinstance(segment, list) and len(segment) > 0:
                            translation_parts.append(segment[0])
                    
                    return ''.join(translation_parts)
            
            return ""
            
        except (json.JSONDecodeError, IndexError, TypeError) as e:
            logger.error(f"Error parsing Google Translate response: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check if Google Translate is available.
        
        Returns:
            True if available, False otherwise
        """
        try:
            # Test with a simple translation
            test_url = f"{self.service_url}?client=gtx&sl=en&tl=es&dt=t&q=hello"
            request = urllib.request.Request(test_url)
            request.add_header('User-Agent', 'SelectTranslate/1.0')
            
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status == 200
                
        except Exception:
            return False
    
    def get_supported_languages(self) -> List[str]:
        """Get supported language codes.
        
        Returns:
            List of supported language codes
        """
        # Google Translate supports many languages
        return [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
            "ar", "hi", "th", "vi", "tr", "pl", "nl", "sv", "da", "no",
            "fi", "el", "he", "fa", "ur", "bn", "ta", "te", "mr", "gu",
            "kn", "ml", "pa", "or", "as", "ne", "si", "my", "km", "lo",
            "ka", "am", "sw", "mg", "eu", "ca", "gl", "cy", "ga", "mt",
            "is", "lv", "lt", "et", "sl", "sk", "cs", "hu", "ro", "bg",
            "hr", "sr", "bs", "mk", "sq", "az", "be", "ka", "hy", "eo",
            "la", "cy", "yi", "zu", "xh", "af", "sq", "eu", "be", "bg",
            "ca", "zh-cn", "zh-tw", "hr", "cs", "da", "nl", "en", "et",
            "tl", "fi", "fr", "gl", "ka", "de", "el", "gu", "ht", "ha",
            "haw", "iw", "hi", "hmn", "hu", "is", "ig", "id", "ga", "it",
            "ja", "jw", "kn", "kk", "km", "ko", "ku", "ky", "lo", "la",
            "lv", "lt", "lb", "mk", "mg", "ms", "ml", "mt", "mi", "mr",
            "mn", "my", "ne", "no", "ps", "fa", "pl", "pt", "pa", "ro",
            "ru", "sm", "gd", "sr", "st", "sn", "sd", "si", "sk", "sl",
            "so", "es", "su", "sw", "sv", "tg", "ta", "te", "th", "tr",
            "uk", "ur", "uz", "vi", "cy", "xh", "yi", "yo", "zu"
        ]