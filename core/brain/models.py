"""
Data models for the communal brain system
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from enum import Enum


class DeviceTier(Enum):
    """Hardware tiers for devices in the homelab"""
    RASPBERRY_PI = "raspberry_pi"
    LAPTOP = "laptop"
    WORKSTATION = "workstation"
    SERVER = "server"
    CLOUD = "cloud"


class DeviceStatus(Enum):
    """Device connection status"""
    ONLINE = "online"
    OFFLINE = "offline"
    SYNCING = "syncing"
    ERROR = "error"


@dataclass
class DeviceContext:
    """Context information for a device in the communal brain network"""
    device_id: str
    hardware_tier: DeviceTier
    capabilities: List[str] = field(default_factory=list)  # ['gpu', 'high_memory', 'fast_network']
    specialization: Optional[str] = None  # 'research', 'coding', 'analysis', 'general'
    location: str = "unknown"  # physical location in homelab
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: DeviceStatus = DeviceStatus.ONLINE
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization"""
        return {
            'device_id': self.device_id,
            'hardware_tier': self.hardware_tier.value,
            'capabilities': self.capabilities,
            'specialization': self.specialization,
            'location': self.location,
            'ip_address': self.ip_address,
            'hostname': self.hostname,
            'last_seen': self.last_seen.isoformat(),
            'status': self.status.value,
            'version': self.version,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceContext':
        """Create from dictionary"""
        data_copy = data.copy()
        data_copy['hardware_tier'] = DeviceTier(data_copy['hardware_tier'])
        data_copy['status'] = DeviceStatus(data_copy['status'])
        data_copy['last_seen'] = datetime.fromisoformat(data_copy['last_seen'])
        return cls(**data_copy)


@dataclass
class MemoryItem:
    """A memory item in the communal brain"""
    id: str
    user_message: str
    bot_response: str
    embedding: List[float]
    device_id: str
    context: str = ""  # Additional context about this memory
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    relevance_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'user_message': self.user_message,
            'bot_response': self.bot_response,
            'embedding': self.embedding,
            'device_id': self.device_id,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'relevance_score': self.relevance_score,
            'tags': self.tags,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Create from dictionary"""
        data_copy = data.copy()
        data_copy['timestamp'] = datetime.fromisoformat(data_copy['timestamp'])
        return cls(**data_copy)


@dataclass
class KnowledgeItem:
    """A knowledge item in the communal brain"""
    id: str
    content: str
    embedding: List[float]
    source: str  # File path, URL, or device that provided this knowledge
    device_id: str
    chunk_index: int = 0  # For chunked documents
    total_chunks: int = 1
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    relevance_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'content': self.content,
            'embedding': self.embedding,
            'source': self.source,
            'device_id': self.device_id,
            'chunk_index': self.chunk_index,
            'total_chunks': self.total_chunks,
            'timestamp': self.timestamp.isoformat(),
            'relevance_score': self.relevance_score,
            'tags': self.tags,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeItem':
        """Create from dictionary"""
        data_copy = data.copy()
        data_copy['timestamp'] = datetime.fromisoformat(data_copy['timestamp'])
        return cls(**data_copy)


@dataclass
class SyncOperation:
    """Represents a synchronization operation between devices"""
    operation_id: str
    operation_type: str  # 'create', 'update', 'delete'
    item_type: str  # 'memory', 'knowledge', 'device'
    item_id: str
    device_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'operation_id': self.operation_id,
            'operation_type': self.operation_type,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'device_id': self.device_id,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'resolved': self.resolved
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncOperation':
        """Create from dictionary"""
        data_copy = data.copy()
        data_copy['timestamp'] = datetime.fromisoformat(data_copy['timestamp'])
        return cls(**data_copy)