"""Tests for translation engine."""

import pytest
from unittest.mock import patch, MagicMock
from translator.core.translator import TranslationEngine


@pytest.fixture
def translation_engine():
    """Create a translation engine instance."""
    return TranslationEngine()


def test_translation_engine_init(translation_engine):
    """Test translation engine initialization."""
    assert translation_engine.language_pair == "eng-spa"
    assert translation_engine.timeout == 10
    assert translation_engine.engine == "apertium"


def test_get_word_count(translation_engine):
    """Test word counting."""
    assert translation_engine.get_word_count("hello") == 1
    assert translation_engine.get_word_count("hello world") == 2
    assert translation_engine.get_word_count("  hello   world  ") == 2
    assert translation_engine.get_word_count("") == 1  # split() on empty string returns ['']


@patch('subprocess.run')
def test_translate_success(mock_run, translation_engine):
    """Test successful translation."""
    # Mock successful subprocess call
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "hola"
    mock_run.return_value = mock_result
    
    success, result = translation_engine.translate("hello")
    
    assert success is True
    assert result == "hola"
    
    # Verify subprocess was called correctly
    mock_run.assert_called_once_with(
        ['apertium', 'eng-spa'],
        input="hello",
        text=True,
        capture_output=True,
        timeout=10
    )


@patch('subprocess.run')
def test_translate_failure(mock_run, translation_engine):
    """Test translation failure."""
    # Mock failed subprocess call
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "Translation error"
    mock_run.return_value = mock_result
    
    success, result = translation_engine.translate("hello")
    
    assert success is False
    assert "Translation error" in result


@patch('subprocess.run')
def test_translate_timeout(mock_run, translation_engine):
    """Test translation timeout."""
    # Mock timeout
    mock_run.side_effect = subprocess.TimeoutExpired("apertium", 10)
    
    success, result = translation_engine.translate("hello")
    
    assert success is False
    assert "timeout" in result.lower()


def test_translate_empty_text(translation_engine):
    """Test translation with empty text."""
    success, result = translation_engine.translate("")
    
    assert success is False
    assert "empty" in result.lower()


@patch('subprocess.run')
def test_is_available_true(mock_run, translation_engine):
    """Test availability check when tool is available."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    
    assert translation_engine.is_available() is True


@patch('subprocess.run')
def test_is_available_false(mock_run, translation_engine):
    """Test availability check when tool is not available."""
    mock_run.side_effect = FileNotFoundError()
    
    assert translation_engine.is_available() is False