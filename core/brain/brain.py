"""
Main CommunalBrain class - central intelligence hub for all devices
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from .models import DeviceContext, DeviceStatus, MemoryItem, KnowledgeItem
from .storage import StorageAbstraction
from .components.config import BrainConfig
from .components.device import DeviceManager
from .components.sync import SyncManager
from ..agents.summarizer import SummarizerAgent


class CommunalBrain:
    """
    Central intelligence hub that coordinates knowledge and memory across all devices.

    This is the main interface that chatbots and agents use to store and retrieve
    information from the shared intelligence pool.
    """

    def __init__(self, config: BrainConfig):
        self.config = config
        self.device_id = config.device_id or DeviceManager.generate_device_id()
        self.storage = StorageAbstraction(config.storage)

        # Device context for this instance
        self.device_context = DeviceManager.create_device_context(
            device_id=self.device_id,
            device_name=config.device_name,
            location=config.device_location,
            hardware_tier=config.hardware_tier,
            capabilities=config.capabilities if config.capabilities else None
        )
        self.device_context.status = DeviceStatus.ONLINE

        # Runtime state
        self._initialized = False
        self.sync_manager = SyncManager(self)
        self.summarizer: Optional[SummarizerAgent] = None

    async def initialize(self) -> None:
        """Initialize the communal brain and register this device"""
        if self._initialized:
            return

        # Initialize storage
        await self.storage.initialize()

        # Register this device
        await self.storage.register_device(self.device_context)

        # Initialize summarizer if enabled
        if self.config.enable_summarizer:
            from pathlib import Path
            data_dir = Path(__file__).parent.parent / "data"
            self.summarizer = SummarizerAgent(data_dir, self.config.summarizer)

            # Start background monitoring
            await self.summarizer.start_background_monitoring()

            # Run startup summarization check
            await self.summarizer.summarize_on_startup()

        # Start sync manager if enabled
        if self.config.enable_sync:
            await self.sync_manager.start()

        self._initialized = True

    async def close(self) -> None:
        """Shutdown the communal brain"""
        # Stop sync manager
        await self.sync_manager.stop()

        # Stop summarizer if running
        if self.summarizer:
            await self.summarizer.stop_background_monitoring()

        await self.storage.close()
        self._initialized = False

    async def store_memory(self, user_message: str, bot_response: str,
                          embedding: List[float], context: str = "",
                          tags: Optional[List[str]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a conversation memory in the communal brain

        Args:
            user_message: The user's message
            bot_response: The bot's response
            embedding: Vector embedding of the conversation
            context: Additional context about this memory
            tags: Optional tags for categorization
            metadata: Optional additional metadata

        Returns:
            Memory ID
        """
        memory_id = str(uuid.uuid4())

        memory = MemoryItem(
            id=memory_id,
            user_message=user_message,
            bot_response=bot_response,
            embedding=embedding,
            device_id=self.device_id,
            context=context,
            tags=tags or [],
            metadata=metadata or {}
        )

        await self.storage.store_memory(memory)

        # Update device last seen
        await self._update_device_heartbeat()

        return memory_id

    async def retrieve_memories(self, query_embedding: List[float],
                               top_k: int = 5,
                               device_filter: Optional[str] = None,
                               min_similarity: float = 0.0) -> List[MemoryItem]:
        """
        Retrieve similar memories from the communal brain

        Args:
            query_embedding: Vector embedding of the query
            top_k: Number of memories to retrieve
            device_filter: Optional filter for specific device
            min_similarity: Minimum similarity threshold

        Returns:
            List of similar memories
        """
        memories = await self.storage.retrieve_memories(
            query_embedding, top_k * 2, device_filter  # Get more for filtering
        )

        # Filter by similarity threshold
        filtered_memories = [
            memory for memory in memories
            if memory.relevance_score >= min_similarity
        ]

        return filtered_memories[:top_k]

    async def store_knowledge(self, content: str, embedding: List[float],
                             source: str, chunk_index: int = 0, total_chunks: int = 1,
                             tags: Optional[List[str]] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store knowledge in the communal brain

        Args:
            content: The knowledge content
            embedding: Vector embedding of the content
            source: Source of the knowledge (file path, URL, etc.)
            chunk_index: Index of this chunk (for chunked content)
            total_chunks: Total number of chunks
            tags: Optional tags
            metadata: Optional metadata

        Returns:
            Knowledge ID
        """
        knowledge_id = str(uuid.uuid4())

        knowledge = KnowledgeItem(
            id=knowledge_id,
            content=content,
            embedding=embedding,
            source=source,
            device_id=self.device_id,
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            tags=tags or [],
            metadata=metadata or {}
        )

        await self.storage.store_knowledge(knowledge)

        # Update device last seen
        await self._update_device_heartbeat()

        return knowledge_id

    async def retrieve_knowledge(self, query_embedding: List[float],
                                top_k: int = 5,
                                source_filter: Optional[str] = None,
                                min_similarity: float = 0.0) -> List[KnowledgeItem]:
        """
        Retrieve similar knowledge from the communal brain

        Args:
            query_embedding: Vector embedding of the query
            top_k: Number of knowledge items to retrieve
            source_filter: Optional filter for specific source
            min_similarity: Minimum similarity threshold

        Returns:
            List of similar knowledge items
        """
        knowledge_items = await self.storage.retrieve_knowledge(
            query_embedding, top_k * 2, source_filter
        )

        # Filter by similarity threshold
        filtered_items = [
            item for item in knowledge_items
            if item.relevance_score >= min_similarity
        ]

        return filtered_items[:top_k]

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory store"""
        memory_count = await self.storage.get_memory_count()
        knowledge_count = await self.storage.get_knowledge_count()
        devices = await self.storage.list_devices()

        return {
            'memory_count': memory_count,
            'knowledge_count': knowledge_count,
            'device_count': len(devices),
            'devices': [device.to_dict() for device in devices],
            'this_device': self.device_context.to_dict()
        }

    async def list_devices(self) -> List[DeviceContext]:
        """Get list of all registered devices"""
        return await self.storage.list_devices()

    async def get_device(self, device_id: str) -> Optional[DeviceContext]:
        """Get information about a specific device"""
        return await self.storage.get_device(device_id)

    async def update_device_context(self, **updates) -> None:
        """Update this device's context information"""
        for key, value in updates.items():
            if hasattr(self.device_context, key):
                setattr(self.device_context, key, value)

        # Re-register with updated context
        await self.storage.register_device(self.device_context)

    # Summarizer methods

    async def check_context_size(self, context_text: str) -> Tuple[bool, Optional[str]]:
        """Check if context is too large and return suggested summary if needed"""
        if self.summarizer:
            return await self.summarizer.check_context_size(context_text)
        return False, None

    async def manual_summarize_file(self, filepath: Path) -> bool:
        """Manually trigger summarization of a specific conversation file"""
        if self.summarizer:
            return await self.summarizer.manual_summarize_file(filepath)
        return False

    async def get_summarizer_stats(self) -> Optional[Dict]:
        """Get summarizer statistics"""
        if self.summarizer:
            return self.summarizer.get_stats()
        return None
    async def store_conversation(self, session_id: str, conversation_data: Dict[str, Any]) -> None:
        """Store conversation data in the communal brain

        Args:
            session_id: Unique conversation session ID
            conversation_data: Conversation data dictionary
        """
        await self.storage.store_conversation(session_id, conversation_data)

    async def load_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation data from the communal brain

        Args:
            session_id: Unique conversation session ID

        Returns:
            Conversation data dictionary or None if not found
        """
        return await self.storage.load_conversation(session_id)

    async def list_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent conversations

        Args:
            limit: Maximum number of conversations to return

        Returns:
            List of conversation metadata
        """
        return await self.storage.list_conversations(limit)

    async def delete_conversation(self, session_id: str) -> bool:
        """Delete a conversation from the communal brain

        Args:
            session_id: Unique conversation session ID

        Returns:
            True if deleted, False if not found
        """
        return await self.storage.delete_conversation(session_id)

    async def trigger_startup_summarization(self) -> None:
        """Manually trigger startup summarization check"""
        if self.summarizer:
            await self.summarizer.summarize_on_startup()

    # Private methods

    async def _update_device_heartbeat(self) -> None:
        """Update device's last seen timestamp"""
        self.device_context.last_seen = datetime.now(timezone.utc)
        await self.storage.register_device(self.device_context)