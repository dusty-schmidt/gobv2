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

from .interfaces import (
    StorageProtocol,
    SummarizerProtocol,
    LLMClientProtocol,
    EmbeddingsClientProtocol,
    VectorSearchProtocol,
    DeviceRegistryProtocol,
    SyncManagerProtocol,
    ConversationStorageProtocol
)

from .agents import (
    SummarizerAgent,
    SummarizerConfig
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
    'get_logger',

    # Protocol interfaces
    'StorageProtocol',
    'SummarizerProtocol',
    'LLMClientProtocol',
    'EmbeddingsClientProtocol',
    'VectorSearchProtocol',
    'DeviceRegistryProtocol',
    'SyncManagerProtocol',
    'ConversationStorageProtocol',

    # Agents
    'SummarizerAgent',
    'SummarizerConfig'
]

__version__ = "1.0.0"