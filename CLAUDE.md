# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

SelectTranslate is a GTK3-based desktop application that provides real-time translation of selected text. It monitors clipboard selection and automatically translates text using configurable translation providers, with intelligent window positioning that avoids covering the selected text.

## Core Architecture

### Component Structure
- **Translation Engine** (`src/translator/core/translator.py`): Manages translation providers (Apertium, Google, LibreTranslate)
- **Clipboard Monitor** (`src/translator/core/clipboard.py`): Monitors text selection using xsel
- **Dictionary Lookup** (`src/translator/core/dictionary.py`): Provides word definitions using dict command
- **Window Positioning** (`src/translator/utils/positioning.py`): Intelligent window placement using xdotool
- **UI Components** (`src/translator/ui/`): GTK3-based interface with dynamic layouts

### Configuration System
- Central configuration in `src/translator/config.py` with hierarchical overrides
- User config directory: `~/.config/selecttranslate/config.json`
- Provider-specific configurations for different translation engines

## Development Commands

### Running the Application
```bash
# Development run
make run
# OR
PYTHONPATH=src python3 -m translator.main

# Debug mode
make run-debug
```

### Testing
```bash
# Run all tests
make test
# OR
pytest

# Run with coverage
make test-cov
# OR
pytest --cov=translator --cov-report=html --cov-report=term

# Run specific test
pytest tests/test_translation.py
```

### Code Quality
```bash
# Run all checks
make check

# Individual checks
make lint        # flake8 + black --check + isort --check
make format      # black + isort
make type-check  # mypy src/
```

### Building
```bash
# Clean build
make build

# Debian package
make build-deb
```

## Dependencies

### System Dependencies
The application requires several system tools:
- `python3-gi` - GTK3 Python bindings
- `apertium` - Translation engine
- `dict` - Dictionary lookup
- `xsel` - Clipboard monitoring
- `xdotool` - Window positioning

Install with: `make install-system-deps`

### Translation Providers
- **Apertium**: Local offline translation (primary)
- **Google**: Online API-based (requires API key)
- **LibreTranslate**: Open source online translation

## Key Implementation Details

### Threading Model
The application uses threading for:
- Clipboard monitoring (separate thread)
- Translation requests (avoid UI blocking)
- Window positioning calculations

### Configuration Architecture
- Base configuration in `config.py`
- Provider-specific configs in `PROVIDER_CONFIGS`
- Runtime configuration merging with user overrides

### UI State Management
- Dynamic layouts for single words vs phrases
- Intelligent window positioning based on cursor location
- CSS-based styling with gradient themes

## Testing Strategy

Tests are organized by functionality:
- `test_config.py` - Configuration system tests
- `test_translation.py` - Translation engine tests
- Core components have availability checks for system dependencies

## Common Development Patterns

### Adding New Translation Providers
1. Create provider class in `src/translator/core/providers/`
2. Inherit from `BaseProvider`
3. Add configuration to `PROVIDER_CONFIGS`
4. Update `TranslationEngine._create_provider()`

### Error Handling
- Graceful degradation when system tools are missing
- Comprehensive logging with structured messages
- User-friendly error messages in UI

### Dependency Checking
All core components implement `is_available()` method to check system dependencies at runtime.