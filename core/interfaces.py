"""
Protocol interfaces for the communal brain system.

These protocols define the contracts that different components must follow,
enabling dependency injection and proper testing.
"""

from typing import Protocol, List, Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime


class MemoryItem:
    """Data model for memory items"""
    id: str
    user_message: str
    bot_response: str
    embedding: List[float]
    device_id: str
    context: str
    timestamp: datetime
    relevance_score: float = 0.0
    tags: List[str] = []


class KnowledgeItem:
    """Data model for knowledge items"""
    id: str
    content: str
    source: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: datetime


class StorageProtocol(Protocol):
    """Protocol for storage backends"""

    async def store_memory(self, memory: MemoryItem) -> None:
        """Store a memory item"""
        ...

    async def retrieve_memories(self, query_embedding: List[float], top_k: int = 5) -> List[MemoryItem]:
        """Retrieve similar memories by embedding"""
        ...

    async def store_knowledge(self, knowledge: KnowledgeItem) -> None:
        """Store a knowledge item"""
        ...

    async def retrieve_knowledge(self, query_embedding: List[float], top_k: int = 3) -> List[KnowledgeItem]:
        """Retrieve similar knowledge by embedding"""
        ...

    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        ...


class SummarizerProtocol(Protocol):
    """Protocol for summarization agents"""

    async def summarize(self, text: str) -> str:
        """Summarize the given text"""
        ...

    async def check_context_size(self, context: str) -> Tuple[bool, Optional[str]]:
        """Check if context is too large and return suggested summary"""
        ...

    async def start_background_monitoring(self) -> None:
        """Start background monitoring for summarization tasks"""
        ...

    async def stop_background_monitoring(self) -> None:
        """Stop background monitoring"""
        ...


class LLMClientProtocol(Protocol):
    """Protocol for LLM API clients"""

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate a response from the LLM"""
        ...


class EmbeddingsClientProtocol(Protocol):
    """Protocol for embeddings clients"""

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        ...

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        ...


class VectorSearchProtocol(Protocol):
    """Protocol for vector similarity search"""

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        ...

    def find_similar(
        self,
        query_embedding: List[float],
        embeddings: List[List[float]],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Tuple[int, float]]:
        """Find most similar embeddings to query"""
        ...


class DeviceRegistryProtocol(Protocol):
    """Protocol for device management and context tracking"""

    def get_device_id(self) -> str:
        """Get unique device identifier"""
        ...

    def register_device(self, device_info: Dict[str, Any]) -> None:
        """Register device capabilities and information"""
        ...

    def get_device_context(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get context information for a device"""
        ...

    def update_device_status(self, device_id: str, status: str) -> None:
        """Update device online/offline status"""
        ...


class SyncManagerProtocol(Protocol):
    """Protocol for cross-device synchronization"""

    async def broadcast_change(self, item: Any, source_device: str) -> None:
        """Broadcast changes to other devices"""
        ...

    async def handle_incoming_change(self, item: Any, source_device: str) -> None:
        """Handle changes received from other devices"""
        ...

    async def resolve_conflict(self, local_item: Any, remote_item: Any) -> Any:
        """Resolve conflicts between local and remote items"""
        ...


class ConversationStorageProtocol(Protocol):
    """Protocol for persistent conversation storage"""

    def save_conversation(self, session_id: str, messages: List[Dict[str, Any]], device_id: str) -> None:
        """Save conversation to persistent storage"""
        ...

    def load_conversation(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Load conversation from persistent storage"""
        ...

    def list_conversations(self, device_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent conversations"""
        ...

    def cleanup_old_conversations(self, max_age_days: int = 30) -> int:
        """Remove conversations older than specified days"""
        ...