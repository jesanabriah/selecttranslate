"""Logging configuration utilities."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from ..config import get_user_config_dir


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True
) -> None:
    """Set up application logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (default: user config dir)
        console: Whether to log to console
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler
    if log_file is None:
        log_dir = get_user_config_dir()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "translator.log"
    
    try:
        # Use rotating file handler to prevent large log files
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        logging.info(f"Logging configured. Level: {level}, File: {log_file}")
        
    except (OSError, PermissionError) as e:
        # If file logging fails, just use console
        logging.warning(f"Could not set up file logging: {e}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)