"""
Main CommunalBrain class - central intelligence hub for all devices
"""

import asyncio
import os
import platform
import socket
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pathlib import Path

from .models import DeviceContext, DeviceTier, DeviceStatus, MemoryItem, KnowledgeItem
from .storage import StorageAbstraction, StorageConfig


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


class CommunalBrain:
    """
    Central intelligence hub that coordinates knowledge and memory across all devices.

    This is the main interface that chatbots and agents use to store and retrieve
    information from the shared intelligence pool.
    """

    def __init__(self, config: BrainConfig):
        self.config = config
        self.device_id = config.device_id or self._generate_device_id()
        self.storage = StorageAbstraction(config.storage)

        # Device context for this instance
        self.device_context = DeviceContext(
            device_id=self.device_id,
            hardware_tier=config.hardware_tier or self._detect_hardware_tier(),
            capabilities=config.capabilities or self._detect_capabilities(),
            location=config.device_location,
            hostname=self._get_hostname(),
            ip_address=self._get_ip_address(),
            status=DeviceStatus.ONLINE
        )

        # Runtime state
        self._initialized = False
        self._sync_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize the communal brain and register this device"""
        if self._initialized:
            return

        # Initialize storage
        await self.storage.initialize()

        # Register this device
        await self.storage.register_device(self.device_context)

        # Start sync task if enabled
        if self.config.enable_sync:
            self._sync_task = asyncio.create_task(self._sync_loop())

        self._initialized = True

    async def close(self) -> None:
        """Shutdown the communal brain"""
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass

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

    # Private methods

    def _generate_device_id(self) -> str:
        """Generate a unique device ID"""
        # Use hostname + MAC address for uniqueness
        hostname = self._get_hostname()
        try:
            # Get MAC address of first network interface
            import uuid
            mac = uuid.getnode()
            mac_hex = ':'.join(['{:02x}'.format((mac >> elements) & 0xff)
                               for elements in range(0, 8*6, 8)][::-1])
            return f"{hostname}_{mac_hex}"
        except:
            # Fallback to hostname + random
            return f"{hostname}_{str(uuid.uuid4())[:8]}"

    def _detect_hardware_tier(self) -> DeviceTier:
        """Auto-detect hardware tier based on system capabilities"""
        try:
            # Check CPU count
            cpu_count = len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else os.cpu_count() or 1

            # Check memory
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)

            # Simple heuristics
            if memory_gb >= 32 and cpu_count >= 8:
                return DeviceTier.SERVER
            elif memory_gb >= 16 and cpu_count >= 4:
                return DeviceTier.WORKSTATION
            elif memory_gb >= 8 and cpu_count >= 2:
                return DeviceTier.LAPTOP
            else:
                return DeviceTier.RASPBERRY_PI

        except ImportError:
            # psutil not available, use basic detection
            return DeviceTier.LAPTOP

    def _detect_capabilities(self) -> List[str]:
        """Auto-detect device capabilities"""
        capabilities = []

        try:
            import psutil

            # Memory capability
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb >= 16:
                capabilities.append('high_memory')
            elif memory_gb >= 8:
                capabilities.append('medium_memory')
            else:
                capabilities.append('low_memory')

            # CPU capability
            cpu_count = psutil.cpu_count(logical=True)
            if cpu_count >= 8:
                capabilities.append('multi_core')
            elif cpu_count >= 4:
                capabilities.append('quad_core')
            else:
                capabilities.append('low_core')

        except ImportError:
            capabilities.extend(['unknown_memory', 'unknown_cpu'])

        # GPU detection (simplified)
        try:
            import torch
            if torch.cuda.is_available():
                capabilities.append('gpu')
                capabilities.append('cuda')
        except ImportError:
            pass

        # Network capability (assume all have basic network)
        capabilities.append('network')

        return capabilities

    def _get_hostname(self) -> str:
        """Get system hostname"""
        return platform.node() or "unknown"

    def _get_ip_address(self) -> Optional[str]:
        """Get local IP address"""
        try:
            # Get the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Connect to Google DNS
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return None

    async def _update_device_heartbeat(self) -> None:
        """Update device's last seen timestamp"""
        self.device_context.last_seen = datetime.now(timezone.utc)
        await self.storage.register_device(self.device_context)

    async def _sync_loop(self) -> None:
        """Background sync loop for cross-device synchronization"""
        while True:
            try:
                await asyncio.sleep(self.config.sync_interval)
                # TODO: Implement sync logic
                # - Check for pending operations
                # - Send local changes to other devices
                # - Receive changes from other devices
                # - Resolve conflicts
                pass
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue sync loop
                print(f"Sync error: {e}")
                await asyncio.sleep(self.config.sync_interval)