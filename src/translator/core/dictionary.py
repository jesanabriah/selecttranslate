"""Dictionary lookup module."""

import subprocess
import logging
from typing import Optional, Tuple
from ..config import DICTIONARY_CONFIG

logger = logging.getLogger(__name__)


class DictionaryLookup:
    """Handles dictionary lookups for word definitions."""
    
    def __init__(self, command: str = None, timeout: int = None):
        """Initialize the dictionary lookup.
        
        Args:
            command: Dictionary command to use
            timeout: Timeout for lookup requests in seconds
        """
        self.command = command or DICTIONARY_CONFIG["command"]
        self.timeout = timeout or DICTIONARY_CONFIG["timeout"]
        self.max_lines = DICTIONARY_CONFIG["max_lines"]
        self.skip_lines = DICTIONARY_CONFIG["skip_lines"]
        
    def lookup(self, word: str, language: str = None) -> Tuple[bool, str]:
        """Look up a word definition.
        
        Args:
            word: Word to look up
            language: Language code to search in (e.g., 'es' for Spanish)
            
        Returns:
            Tuple of (success: bool, definition: str)
        """
        if not word.strip():
            return False, "Empty word provided"
            
        try:
            logger.debug(f"Looking up definition for: {word} (language: {language})")
            
            # Build command with language-specific database if specified
            cmd = [self.command]
            if language:
                # Try to use language-specific dictionary database
                database = self._get_language_database(language, 'definition')
                if database:
                    cmd.extend(["-d", database])
            
            cmd.append(word.strip())
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                definition = self._parse_definition(result.stdout)
                if definition:
                    logger.debug(f"Definition found: {definition[:50]}...")
                    # Add language note if we searched in a specific language
                    if language and language != 'en':
                        definition = f"[Definición en {self._get_language_name(language)}]\n{definition}"
                    return True, definition
                else:
                    logger.debug("No definition found in output")
                    # If language-specific lookup failed, try English fallback
                    if language and language != 'en':
                        return self._fallback_lookup(word, language)
                    return False, "No definition found"
            else:
                logger.debug(f"Dictionary lookup failed for: {word}")
                # If language-specific lookup failed, try English fallback
                if language and language != 'en':
                    return self._fallback_lookup(word, language)
                return False, "Definition not found"
                
        except subprocess.TimeoutExpired:
            logger.error(f"Dictionary lookup timeout after {self.timeout} seconds")
            return False, "Lookup timeout"
        except FileNotFoundError:
            logger.error(f"{self.command} not found. Please install dict.")
            return False, f"{self.command} not installed"
        except Exception as e:
            logger.error(f"Unexpected dictionary error: {e}")
            return False, f"Unexpected error: {str(e)}"
    
    def _get_language_database(self, language: str, lookup_type: str = 'definition') -> Optional[str]:
        """Get dictionary database name for a language.
        
        Args:
            language: Language code (e.g., 'es', 'fr', 'de')
            lookup_type: Type of lookup ('definition' for monolingual, 'translation' for bilingual)
            
        Returns:
            Database name for the language or None if not found
        """
        # Only use monolingual dictionaries for definitions
        # If a monolingual dictionary doesn't exist for a language, return None
        monolingual_databases = {
            'en': 'gcide',  # The Collaborative International Dictionary of English
            # Add other monolingual dictionaries here when available
            # 'es': 'spanish-monolingual-dict',  # Would need to be installed
            # 'fr': 'french-monolingual-dict',   # Would need to be installed
            # etc.
        }
        
        return monolingual_databases.get(language)
    
    def _get_language_name(self, language: str) -> str:
        """Get human-readable language name.
        
        Args:
            language: Language code
            
        Returns:
            Human-readable language name
        """
        language_names = {
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'nl': 'Nederlands',
            'sv': 'Svenska',
            'da': 'Dansk',
            'no': 'Norsk',
            'fi': 'Suomi',
            'pl': 'Polski',
            'cs': 'Čeština',
            'hu': 'Magyar',
            'ro': 'Română',
            'bg': 'Български',
            'hr': 'Hrvatski',
            'sk': 'Slovenčina',
            'sl': 'Slovenščina',
            'et': 'Eesti',
            'lv': 'Latviešu',
            'lt': 'Lietuvių',
            'el': 'Ελληνικά',
            'tr': 'Türkçe',
            'ar': 'العربية',
            'he': 'עברית',
            'hi': 'हिन्दी',
            'ja': '日本語',
            'ko': '한국어',
            'zh': '中文',
            'th': 'ไทย',
            'vi': 'Tiếng Việt',
        }
        
        return language_names.get(language, language.upper())
    
    def _fallback_lookup(self, word: str, original_language: str) -> Tuple[bool, str]:
        """Fallback lookup in English when language-specific lookup fails.
        
        Args:
            word: Word to look up
            original_language: Original language attempted
            
        Returns:
            Tuple of (success: bool, definition: str)
        """
        try:
            logger.debug(f"Attempting English fallback for: {word}")
            
            # Try lookup without language specification (defaults to English)
            result = subprocess.run(
                [self.command, word],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                definition = self._parse_definition(result.stdout)
                if definition:
                    # Add note about fallback
                    lang_name = self._get_language_name(original_language)
                    fallback_note = f"[No hay diccionario específico para {lang_name}. Definición en inglés]\n"
                    return True, fallback_note + definition
            
            return False, f"No definition found for '{word}'"
            
        except Exception as e:
            logger.error(f"Error in fallback lookup: {e}")
            return False, f"Error in fallback lookup: {str(e)}"
    
    def lookup_dual(self, original_word: str, translated_word: str, 
                   source_lang: str, target_lang: str) -> Tuple[bool, str]:
        """Look up definitions for both original and translated words using only monolingual dictionaries.
        
        Args:
            original_word: Original word in source language
            translated_word: Translated word in target language
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'es')
            
        Returns:
            Tuple of (success: bool, combined_definition: str)
        """
        definitions = []
        any_success = False
        
        # Look up original word definition (only if monolingual dictionary exists)
        if self._get_language_database(source_lang):
            original_success, original_def = self.lookup(original_word, source_lang)
            if original_success:
                any_success = True
                source_lang_name = self._get_language_name(source_lang)
                definitions.append(f"📖 {original_word} ({source_lang_name}):\n{original_def}")
        else:
            logger.debug(f"No monolingual dictionary available for {source_lang}")
        
        # Look up translated word definition (only if monolingual dictionary exists)
        if self._get_language_database(target_lang):
            translated_success, translated_def = self.lookup(translated_word, target_lang)
            if translated_success:
                any_success = True
                target_lang_name = self._get_language_name(target_lang)
                definitions.append(f"📖 {translated_word} ({target_lang_name}):\n{translated_def}")
        else:
            logger.debug(f"No monolingual dictionary available for {target_lang}")
        
        if definitions:
            # Join definitions with separator
            separator = "\n\n" + "─" * 50 + "\n\n"
            combined_definition = separator.join(definitions)
            return True, combined_definition
        else:
            # Build a helpful message about what dictionaries are missing
            missing_dicts = []
            if not self._get_language_database(source_lang):
                missing_dicts.append(f"{self._get_language_name(source_lang)} ({source_lang})")
            if not self._get_language_database(target_lang):
                missing_dicts.append(f"{self._get_language_name(target_lang)} ({target_lang})")
            
            if missing_dicts:
                missing_str = " y ".join(missing_dicts)
                return False, f"No hay diccionarios monolingües disponibles para: {missing_str}"
            else:
                return False, f"No se encontraron definiciones para '{original_word}' o '{translated_word}'"
    
    def _parse_definition(self, output: str) -> Optional[str]:
        """Parse dictionary output to extract definition.
        
        Args:
            output: Raw dictionary output
            
        Returns:
            Parsed definition or None if not found
        """
        if not output.strip():
            return None
            
        lines = output.split('\n')
        
        # Skip header lines and extract content lines
        content_lines = []
        for line in lines[self.skip_lines:self.skip_lines + self.max_lines]:
            stripped_line = line.strip()
            if stripped_line:
                content_lines.append(stripped_line)
        
        if content_lines:
            return ' '.join(content_lines)
        else:
            return None
    
    def is_available(self) -> bool:
        """Check if the dictionary tool is available.
        
        Returns:
            True if tool is available, False otherwise
        """
        try:
            result = subprocess.run(
                [self.command, "--version"],
                capture_output=True,
                timeout=5
            )
            # dict --version returns 1 but still works, check if output contains version info
            if result.returncode == 0 or (result.stdout and b"dict" in result.stdout):
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        try:
            # Some dict implementations don't support --version
            result = subprocess.run(
                [self.command],
                capture_output=True,
                timeout=5
            )
            return True  # If it runs without error, it's available
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False