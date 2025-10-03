# Universal utilities for all chatbots
# Shared utility functions and logging

import logging
import sys
from pathlib import Path

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger

def get_workspace_root() -> Path:
    """Get the workspace root directory"""
    # This assumes we're running from gob/ directory
    return Path(__file__).parent.parent

def ensure_directory(path: Path):
    """Ensure a directory exists"""
    path.mkdir(parents=True, exist_ok=True)