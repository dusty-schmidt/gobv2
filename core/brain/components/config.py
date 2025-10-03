"""
Brain configuration classes
"""

from dataclasses import dataclass, field
from typing import List, Optional

from ..models import DeviceTier
from ...config.models import StorageConfig
from ...agents.summarizer import SummarizerConfig


@dataclass
class BrainConfig:
    """Configuration for the communal brain"""
    storage: StorageConfig = field(default_factory=StorageConfig)

    # Device identification
    device_id: Optional[str] = None  # Auto-generated if None
    device_name: Optional[str] = None  # Auto-detected if None
    device_location: str = "unknown"

    # Device capabilities (auto-detected)
    hardware_tier: Optional[DeviceTier] = None
    capabilities: List[str] = field(default_factory=list)

    # Sync settings
    enable_sync: bool = True
    sync_interval: int = 30  # seconds
    max_offline_queue: int = 1000

    # Cache settings
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour

    # Brain settings
    max_memory_items: int = 10000
    max_knowledge_items: int = 50000
    auto_cleanup_threshold: float = 0.8  # Cleanup when 80% full

    # Summarizer settings
    enable_summarizer: bool = True
    summarizer: SummarizerConfig = field(default_factory=SummarizerConfig)