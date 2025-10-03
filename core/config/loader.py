"""
Configuration loader for the global gob ecosystem.
Provides utilities for loading and managing global configuration.
"""

from .models import GlobalConfig, load_global_config


def get_global_config() -> GlobalConfig:
    """Get the global configuration instance"""
    return GlobalConfig()


def reload_global_config() -> GlobalConfig:
    """Reload global configuration from sources"""
    # Force reload by creating new instance
    return GlobalConfig()