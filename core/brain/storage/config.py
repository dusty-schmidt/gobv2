"""
Storage configuration management - compatibility layer
"""

from typing import Optional
from pathlib import Path

# Import from global config for consistency
from ...config.models import StorageConfig as GlobalStorageConfig


# Alias for backward compatibility
StorageConfig = GlobalStorageConfig