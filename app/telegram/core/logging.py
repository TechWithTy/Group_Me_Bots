"""
Logging configuration for the Telegram API service.
"""
from __future__ import annotations

import logging
import sys
from typing import Dict, Any

from app.telegram.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""

    # Create logger
    logger = logging.getLogger("app.telegram")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Set up specific loggers for different components
    loggers_config: Dict[str, Dict[str, Any]] = {
        "app.telegram.api": {"level": "INFO"},
        "app.telegram.core": {"level": "INFO"},
        "app.telegram.services": {"level": "INFO"},
        "uvicorn": {"level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"level": "WARNING"},
    }

    for logger_name, config in loggers_config.items():
        component_logger = logging.getLogger(logger_name)
        component_logger.setLevel(config["level"])

        # Add console handler if not already added
        if not component_logger.handlers:
            component_logger.addHandler(console_handler)
            component_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"app.telegram.{name}")
