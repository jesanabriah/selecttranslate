# SelectTranslate - Makefile

.PHONY: help install install-dev install-system-deps install-dev-tools check-deps test lint format clean build build-deb install-build-deps package docs run

# Default target
help:
	@echo "SelectTranslate - Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  install           Install system dependencies"
	@echo "  install-dev       Install system dependencies and development tools"
	@echo "  install-system-deps Install system packages (PyGObject, Apertium, etc.)"
	@echo "  install-dev-tools Install development tools (pytest, black, etc.)"
	@echo "  check-deps        Check if all dependencies are available"
	@echo "  test              Run test suite"
	@echo "  test-cov          Run tests with coverage report"
	@echo "  lint              Run code linting"
	@echo "  format            Format code with black and isort"
	@echo "  type-check        Run type checking with mypy"
	@echo "  clean             Clean build artifacts"
	@echo "  build             Build distribution packages"
	@echo "  build-deb         Build Debian package"
	@echo "  install-build-deps Install Debian build dependencies"
	@echo "  package           Build and show Debian package"
	@echo "  docs              Build documentation"
	@echo "  run               Run the application"
	@echo "  run-debug         Run with debug logging"

# Installation
install:
	@echo "Installing system dependencies..."
	@make install-system-deps
	@echo "Application ready to run with: make run"

install-dev:
	@echo "Installing system dependencies and development tools..."
	@make install-system-deps
	@make install-dev-tools

# Testing
test:
	pytest

test-cov:
	pytest --cov=translator --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/

# Maintenance
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .tox/
	rm -rf .nox/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name "*.so" -delete
	find . -type f -name "*.egg" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name "*~" -delete
	find . -type f -name "*.swp" -delete
	find . -type f -name "*.swo" -delete

build: clean
	python3 -m build

# Debian package building
build-deb: clean
	@echo "Building Debian package..."
	dpkg-buildpackage -us -uc -b

install-build-deps:
	@echo "Installing Debian build dependencies..."
	sudo apt install -y debhelper python3-all python3-setuptools python3-stdeb dh-python

package: build-deb
	@echo "Debian package built successfully!"
	@echo "Package files:"
	@ls -la ../selecttranslate*.deb || true

# Documentation
docs:
	@echo "Building documentation..."
	@echo "Documentation source in docs/ directory"

# Running
run:
	PYTHONPATH=src python3 -m translator.main

run-debug:
	PYTHONPATH=src python3 -m translator.main --log-level DEBUG

# Development helpers
check: lint type-check test
	@echo "All checks passed!"

# System Dependencies
install-system-deps:
	@echo "Installing system dependencies..."
	@if command -v apt >/dev/null 2>&1; then \
		echo "Detected Debian/Ubuntu system"; \
		sudo apt update && sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 apertium apertium-eng-spa dict xsel xdotool; \
	elif command -v dnf >/dev/null 2>&1; then \
		echo "Detected Fedora system"; \
		sudo dnf install -y python3-gobject gtk3-devel apertium dict xsel xdotool; \
	elif command -v pacman >/dev/null 2>&1; then \
		echo "Detected Arch Linux system"; \
		sudo pacman -S --needed python-gobject gtk3 apertium dict xsel xdotool; \
	else \
		echo "Unsupported system. Please install manually:"; \
		echo "Python GTK3 bindings, Apertium, dict, xsel, xdotool"; \
	fi

install-dev-tools:
	@echo "Installing development tools..."
	@if command -v apt >/dev/null 2>&1; then \
		sudo apt install -y python3-pytest python3-pytest-cov python3-black python3-flake8 python3-mypy; \
	elif command -v dnf >/dev/null 2>&1; then \
		sudo dnf install -y python3-pytest python3-pytest-cov python3-black python3-flake8 python3-mypy; \
	elif command -v pacman >/dev/null 2>&1; then \
		sudo pacman -S --needed python-pytest python-pytest-cov python-black python-flake8 python-mypy; \
	else \
		echo "Please install development tools manually"; \
	fi

check-deps:
	@echo "Checking system dependencies..."
	@python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('✓ PyGObject and GTK3 available')" || echo "✗ PyGObject/GTK3 missing"
	@command -v apertium >/dev/null 2>&1 && echo "✓ Apertium available" || echo "✗ Apertium missing"
	@command -v dict >/dev/null 2>&1 && echo "✓ dict available" || echo "✗ dict missing"
	@command -v xsel >/dev/null 2>&1 && echo "✓ xsel available" || echo "✗ xsel missing"
	@command -v xdotool >/dev/null 2>&1 && echo "✓ xdotool available" || echo "✗ xdotool missing"