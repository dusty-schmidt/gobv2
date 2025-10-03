"""
Storage interfaces and protocols for the communal brain
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Protocol
from datetime import datetime

from ..models import MemoryItem, KnowledgeItem, DeviceContext, SyncOperation


class StorageBackend(ABC):
    """Abstract base class for storage backends"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the storage backend"""
        pass

    @abstractmethod
    async def store_memory(self, memory: MemoryItem) -> None:
        """Store a memory item"""
        pass

    @abstractmethod
    async def retrieve_memories(self, query_embedding: List[float], top_k: int = 5,
                               device_filter: Optional[str] = None) -> List[MemoryItem]:
        """Retrieve similar memories using vector search"""
        pass

    @abstractmethod
    async def store_knowledge(self, knowledge: KnowledgeItem) -> None:
        """Store a knowledge item"""
        pass

    @abstractmethod
    async def retrieve_knowledge(self, query_embedding: List[float], top_k: int = 5,
                                source_filter: Optional[str] = None) -> List[KnowledgeItem]:
        """Retrieve similar knowledge using vector search"""
        pass

    @abstractmethod
    async def get_memory_by_id(self, memory_id: str) -> Optional[MemoryItem]:
        """Get a specific memory by ID"""
        pass

    @abstractmethod
    async def get_knowledge_by_id(self, knowledge_id: str) -> Optional[KnowledgeItem]:
        """Get a specific knowledge item by ID"""
        pass

    @abstractmethod
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory item"""
        pass

    @abstractmethod
    async def delete_knowledge(self, knowledge_id: str) -> bool:
        """Delete a knowledge item"""
        pass

    @abstractmethod
    async def get_memory_count(self) -> int:
        """Get total number of memories"""
        pass

    @abstractmethod
    async def get_knowledge_count(self) -> int:
        """Get total number of knowledge items"""
        pass

    @abstractmethod
    async def register_device(self, device: DeviceContext) -> None:
        """Register or update a device"""
        pass

    @abstractmethod
    async def get_device(self, device_id: str) -> Optional[DeviceContext]:
        """Get device information"""
        pass

    @abstractmethod
    async def list_devices(self) -> List[DeviceContext]:
        """List all registered devices"""
        pass

    @abstractmethod
    async def store_sync_operation(self, operation: SyncOperation) -> None:
        """Store a sync operation for later processing"""
        pass

    @abstractmethod
    async def get_pending_sync_operations(self, device_id: str) -> List[SyncOperation]:
        """Get pending sync operations for a device"""
        pass

    @abstractmethod
    async def mark_sync_operation_resolved(self, operation_id: str) -> None:
        """Mark a sync operation as resolved"""
        pass

    @abstractmethod
    async def store_conversation(self, session_id: str, conversation_data: Dict[str, Any]) -> None:
        """Store conversation data"""
        pass

    @abstractmethod
    async def load_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation data"""
        pass

    @abstractmethod
    async def list_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List conversations"""
        pass

    @abstractmethod
    async def delete_conversation(self, session_id: str) -> bool:
        """Delete a conversation"""
        pass


class StorageBackendProtocol(Protocol):
    """Protocol for storage backend interface"""

    async def initialize(self) -> None: ...
    async def close(self) -> None: ...
    async def store_memory(self, memory: MemoryItem) -> None: ...
    async def retrieve_memories(self, query_embedding: List[float], top_k: int = 5,
                               device_filter: Optional[str] = None) -> List[MemoryItem]: ...
    async def store_knowledge(self, knowledge: KnowledgeItem) -> None: ...
    async def retrieve_knowledge(self, query_embedding: List[float], top_k: int = 5,
                                source_filter: Optional[str] = None) -> List[KnowledgeItem]: ...
    async def get_memory_by_id(self, memory_id: str) -> Optional[MemoryItem]: ...
    async def get_knowledge_by_id(self, knowledge_id: str) -> Optional[KnowledgeItem]: ...
    async def delete_memory(self, memory_id: str) -> bool: ...
    async def delete_knowledge(self, knowledge_id: str) -> bool: ...
    async def get_memory_count(self) -> int: ...
    async def get_knowledge_count(self) -> int: ...
    async def register_device(self, device: DeviceContext) -> None: ...
    async def get_device(self, device_id: str) -> Optional[DeviceContext]: ...
    async def list_devices(self) -> List[DeviceContext]: ...
    async def store_sync_operation(self, operation: SyncOperation) -> None: ...
    async def get_pending_sync_operations(self, device_id: str) -> List[SyncOperation]: ...
    async def mark_sync_operation_resolved(self, operation_id: str) -> None: ...
    async def store_conversation(self, session_id: str, conversation_data: Dict[str, Any]) -> None: ...
    async def load_conversation(self, session_id: str) -> Optional[Dict[str, Any]]: ...
    async def list_conversations(self, limit: int = 50) -> List[Dict[str, Any]]: ...
    async def delete_conversation(self, session_id: str) -> bool: ...