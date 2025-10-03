"""
Global configuration system for all chatbots and agents in the gob ecosystem.
Centralizes model configuration and other global settings.
"""

from .models import GlobalConfig, LLMConfig, EmbeddingsConfig
from .loader import load_global_config

__all__ = ['GlobalConfig', 'LLMConfig', 'EmbeddingsConfig', 'load_global_config']