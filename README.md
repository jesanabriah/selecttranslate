# SelectTranslate

A modern, professional GTK3-based real-time translator with intelligent positioning and elegant design.

## Features

- **Multiple Translation Providers**: Support for Apertium (offline), Google Translate (online), and LibreTranslate (open source)
- **Real-time Translation**: Automatic translation using configurable translation engines
- **Intelligent Positioning**: Smart window positioning that doesn't cover selected text
- **Clipboard Monitoring**: Automatic translation of selected text from any application using xsel
- **Modern UI**: Beautiful gradient design with responsive GTK3 interface
- **Professional Architecture**: Modular, well-documented, and tested codebase
- **Configurable**: Hierarchical configuration system with user overrides


## Requirements

### System Dependencies

The application requires the following system tools:

```bash
# Ubuntu/Debian
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 apertium apertium-eng-spa xsel xdotool

# Fedora
sudo dnf install python3-gobject gtk3-devel apertium xsel xdotool

# Arch Linux
sudo pacman -S python-gobject gtk3 apertium xsel xdotool
```

### Python Dependencies

- Python 3.8+
- PyGObject >= 3.36.0

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/jesanabriah/selecttranslate
cd selecttranslate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run directly with PYTHONPATH:
```bash
PYTHONPATH=src python3 -m translator.main
```

### Development Installation

For development, install with dev dependencies:

```bash
pip install -r requirements-dev.txt
pip install -e .
```

## Usage

### Command Line

Run the application:
```bash
PYTHONPATH=src python3 -m translator.main
```

### Command Line Options

```bash
selecttranslate --help

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set logging level (default: INFO)
  --log-file LOG_FILE   Log file path (default: user config dir)
  --no-console          Disable console logging
  --config-dir CONFIG_DIR
                        Override default config directory
```

### Using the Application

1. **Manual Translation**: Type text in the "Origen" field and click the translate button (🔄)
2. **Automatic Selection**: Select any text in any application - it will be automatically translated
3. **Clear Content**: Click the clear button (🗑️) to reset all fields

## Project Structure

```
selecttranslate/
├── src/translator/          # Main application package
│   ├── core/               # Core business logic
│   │   ├── translator.py   # Translation engine
│   │   └── clipboard.py    # Clipboard monitoring
│   ├── ui/                 # User interface
│   │   ├── main_window.py  # Main window
│   │   └── styles.py       # Style management
│   ├── utils/              # Utilities
│   │   ├── positioning.py  # Window positioning
│   │   └── logging_config.py # Logging setup
│   ├── config.py           # Configuration
│   └── main.py             # Entry point
├── tests/                  # Test suite
├── docs/                   # Documentation
├── assets/                 # Assets (CSS, images)
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Development

### Setting Up Development Environment

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=translator

# Run specific test file
pytest tests/test_translation.py
```

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
pre-commit install
```

## Configuration

The application uses a hierarchical configuration system:

1. **Default Config**: Built-in defaults in `config.py`
2. **User Config**: `~/.config/selecttranslate/` (Linux)
3. **Command Line**: Override via command line arguments

### Configuration Options

Key configuration sections:

- **Window**: Size, positioning, appearance
- **Translation**: Engine settings, timeouts, language pairs
- **Clipboard**: Monitoring intervals and text limits
- **UI**: Styling, spacing, button sizes

## Architecture

The application follows a clean, modular architecture:

### Core Components

- **TranslationEngine**: Handles text translation via multiple providers (Apertium, Google, LibreTranslate)
- **ClipboardMonitor**: Monitors clipboard for text selections using xsel
- **WindowPositioner**: Intelligent window positioning using xdotool

### UI Components

- **TranslatorWindow**: Main application window
- **StyleManager**: CSS style management
- **Layout System**: Dynamic layout switching

### Utilities

- **Logging**: Structured logging with file and console output
- **Configuration**: Centralized configuration management

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests and quality checks
5. Commit with clear messages
6. Push and create a pull request

### Commit Message Format

```
type(scope): description

- feat: new feature
- fix: bug fix
- docs: documentation
- style: formatting
- refactor: code refactoring
- test: adding tests
- chore: maintenance
```

## Troubleshooting

### Common Issues

1. **GTK Import Error**: Install `python3-gi` and GTK development packages
2. **Translation Not Working**: Install `apertium` and language pairs
3. **Clipboard Not Working**: Install `xsel`
4. **Positioning Issues**: Install `xdotool`

### Debug Mode

Run with debug logging for troubleshooting:

```bash
selecttranslate --log-level DEBUG
```

### Log Files

Logs are stored in:
- Linux: `~/.config/selecttranslate/translator.log`
- Check console output for immediate feedback

## License

This project is licensed under the GNU General Public License v3 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Apertium**: Offline translation engine
- **Google Translate**: Online translation service
- **LibreTranslate**: Open source translation service
- **GTK**: GUI framework
- **PyGObject**: Python GTK bindings

## Changelog

### Version 1.0.0
- Initial professional release
- Modular architecture
- Comprehensive test suite
- Professional documentation
- CI/CD ready structure