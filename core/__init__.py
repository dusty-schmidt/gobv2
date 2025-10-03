"""
Core Intelligence Framework

This package contains the shared communal brain, global configuration,
and foundational components used by all chatbot implementations in the homelab.
"""

from .brain import (
    CommunalBrain,
    BrainConfig,
    StorageAbstraction,
    StorageConfig,
    DeviceContext,
    MemoryItem,
    KnowledgeItem,
    DeviceTier,
    DeviceStatus,
    cosine_similarity,
    euclidean_distance
)

from .config import (
    GlobalConfig,
    LLMConfig,
    EmbeddingsConfig,
    load_global_config
)

from .logging import (
    configure_global_logging,
    get_logger
)

__all__ = [
    # Brain components
    'CommunalBrain',
    'BrainConfig',
    'StorageAbstraction',
    'StorageConfig',
    'DeviceContext',
    'MemoryItem',
    'KnowledgeItem',
    'DeviceTier',
    'DeviceStatus',
    'cosine_similarity',
    'euclidean_distance',

    # Global configuration
    'GlobalConfig',
    'LLMConfig',
    'EmbeddingsConfig',
    'load_global_config',

    # Global logging
    'configure_global_logging',
    'get_logger'
]

__version__ = "1.0.0"