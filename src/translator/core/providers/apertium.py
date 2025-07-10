"""Apertium provider implementation."""

import subprocess
import logging
from typing import Dict, List, Tuple, Any

from .base import TranslationProvider

logger = logging.getLogger(__name__)


class ApertiumProvider(TranslationProvider):
    """Apertium provider for local offline translation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Apertium provider.
        
        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.engine = config.get("engine", "apertium")
        self.language_pair = config.get("language_pair", "eng-spa")
        
    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[bool, str]:
        """Translate text using Apertium.
        
        Args:
            text: Text to translate
            source_lang: Source language code (converted to Apertium format)
            target_lang: Target language code (converted to Apertium format)
            
        Returns:
            Tuple of (success: bool, result: str)
        """
        if not text.strip():
            return False, "Empty text provided"
        
        # Preprocess text
        text = self.preprocess_text(text)
        
        # Convert language codes to Apertium format
        apertium_pair = self._convert_to_apertium_pair(source_lang, target_lang)
        if not apertium_pair:
            return False, f"Unsupported language pair: {source_lang}-{target_lang}"
        
        try:
            logger.debug(f"Translating with Apertium ({apertium_pair}): {text[:50]}...")
            
            result = subprocess.run(
                [self.engine, apertium_pair],
                input=text,
                text=True,
                capture_output=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                translation = result.stdout.strip()
                translation = self.postprocess_text(translation)
                logger.debug(f"Apertium translation successful: {translation[:50]}...")
                return True, translation
            else:
                error_msg = result.stderr.strip() or "Translation failed"
                logger.error(f"Apertium translation failed: {error_msg}")
                return False, f"Translation error: {error_msg}"
                
        except subprocess.TimeoutExpired:
            logger.error(f"Apertium translation timeout after {self.timeout} seconds")
            return False, "Translation timeout"
        except FileNotFoundError:
            logger.error(f"{self.engine} not found. Please install Apertium.")
            return False, f"{self.engine} not installed"
        except Exception as e:
            logger.error(f"Unexpected Apertium error: {e}")
            return False, f"Unexpected error: {str(e)}"
    
    def _convert_to_apertium_pair(self, source_lang: str, target_lang: str) -> str:
        """Convert language codes to Apertium pair format.
        
        Args:
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'es')
            
        Returns:
            Apertium language pair (e.g., 'eng-spa') or empty string if unsupported
        """
        # Language code mappings
        lang_map = {
            'en': 'eng',
            'es': 'spa',
            'fr': 'fra',
            'de': 'deu',
            'it': 'ita',
            'pt': 'por',
            'ca': 'cat',
            'eu': 'eus',
            'gl': 'glg',
            'oc': 'oci',
            'ar': 'ara',
            'mt': 'mlt',
            'cy': 'cym',
            'br': 'bre',
            'is': 'isl',
            'mk': 'mkd',
            'bg': 'bul',
            'hr': 'hrv',
            'sl': 'slv',
            'sr': 'srp',
            'bs': 'bos',
            'sq': 'sqi',
            'ro': 'ron',
            'ru': 'rus',
            'be': 'bel',
            'uk': 'ukr',
            'kk': 'kaz',
            'ky': 'kir',
            'uz': 'uzb',
            'tt': 'tat',
            'ba': 'bak',
            'crh': 'crh',
            'nog': 'nog',
            'kum': 'kum',
            'kaa': 'kaa',
        }
        
        apertium_source = lang_map.get(source_lang, source_lang)
        apertium_target = lang_map.get(target_lang, target_lang)
        
        # Check if this specific pair is supported
        pair = f"{apertium_source}-{apertium_target}"
        reverse_pair = f"{apertium_target}-{apertium_source}"
        
        supported_pairs = self._get_apertium_pairs()
        
        if pair in supported_pairs:
            return pair
        elif reverse_pair in supported_pairs:
            return reverse_pair
        else:
            # Try with the default pair format
            return self.language_pair
    
    def _get_apertium_pairs(self) -> List[str]:
        """Get available Apertium language pairs.
        
        Returns:
            List of available language pairs
        """
        try:
            result = subprocess.run(
                [self.engine, "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                pairs = []
                for line in result.stdout.strip().split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        pairs.append(line)
                return pairs
            else:
                # Return default pairs if command fails
                return ["eng-spa", "spa-eng", "eng-fra", "fra-eng", "eng-cat", "cat-eng"]
                
        except Exception:
            # Return default pairs if command fails
            return ["eng-spa", "spa-eng", "eng-fra", "fra-eng", "eng-cat", "cat-eng"]
    
    def is_available(self) -> bool:
        """Check if Apertium is available.
        
        Returns:
            True if available, False otherwise
        """
        try:
            result = subprocess.run(
                [self.engine, "-V"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_supported_languages(self) -> List[str]:
        """Get supported language codes.
        
        Returns:
            List of supported language codes
        """
        # Extract unique languages from available pairs
        pairs = self._get_apertium_pairs()
        languages = set()
        
        # Language code mappings (reverse of _convert_to_apertium_pair)
        apertium_to_iso = {
            'eng': 'en',
            'spa': 'es',
            'fra': 'fr',
            'deu': 'de',
            'ita': 'it',
            'por': 'pt',
            'cat': 'ca',
            'eus': 'eu',
            'glg': 'gl',
            'oci': 'oc',
            'ara': 'ar',
            'mlt': 'mt',
            'cym': 'cy',
            'bre': 'br',
            'isl': 'is',
            'mkd': 'mk',
            'bul': 'bg',
            'hrv': 'hr',
            'slv': 'sl',
            'srp': 'sr',
            'bos': 'bs',
            'sqi': 'sq',
            'ron': 'ro',
            'rus': 'ru',
            'bel': 'be',
            'ukr': 'uk',
            'kaz': 'kk',
            'kir': 'ky',
            'uzb': 'uz',
            'tat': 'tt',
            'bak': 'ba',
            'crh': 'crh',
            'nog': 'nog',
            'kum': 'kum',
            'kaa': 'kaa',
        }
        
        for pair in pairs:
            if '-' in pair:
                source, target = pair.split('-', 1)
                # Convert to ISO codes
                if source in apertium_to_iso:
                    languages.add(apertium_to_iso[source])
                if target in apertium_to_iso:
                    languages.add(apertium_to_iso[target])
        
        return sorted(list(languages)) if languages else ['en', 'es', 'fr', 'de', 'it', 'pt', 'ca']