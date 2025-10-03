"""
Storage abstraction layer that manages multiple storage backends
"""

from typing import Dict, Optional

from .interfaces import StorageBackend
from .config import StorageConfig


class StorageAbstraction:
    """Main storage abstraction that manages multiple backends"""

    def __init__(self, config: StorageConfig):
        self.config = config
        self.backends: Dict[str, StorageBackend] = {}

        # Initialize backends
        from .backends.sqlite import SQLiteBackend
        self.backends['local'] = SQLiteBackend(config)

        # TODO: Add remote PostgreSQL backend
        # if config.remote_host:
        #     self.backends['remote'] = PostgreSQLBackend(config)

        # TODO: Add cache backend
        # if config.cache_host:
        #     if config.cache_type == 'redis':
        #         self.backends['cache'] = RedisBackend(config)
        #     else:
        #         self.backends['cache'] = MemcachedBackend(config)

    async def initialize(self) -> None:
        """Initialize all configured backends"""
        for backend in self.backends.values():
            await backend.initialize()

    async def close(self) -> None:
        """Close all backends"""
        for backend in self.backends.values():
            await backend.close()

    async def _get_primary_backend(self) -> StorageBackend:
        """Get the primary backend for operations"""
        return self.backends[self.config.primary_backend]

    async def _get_cache_backend(self) -> Optional[StorageBackend]:
        """Get cache backend if available"""
        return self.backends.get('cache')

    # Delegate methods to appropriate backends
    async def store_memory(self, memory):
        primary = await self._get_primary_backend()
        await primary.store_memory(memory)

        # Also store in cache if available
        cache = await self._get_cache_backend()
        if cache:
            await cache.store_memory(memory)

    async def retrieve_memories(self, query_embedding, top_k: int = 5, device_filter=None):
        # Try cache first
        cache = await self._get_cache_backend()
        if cache:
            cached_result = await cache.retrieve_memories(query_embedding, top_k, device_filter)
            if cached_result:
                return cached_result

        # Fallback to primary
        primary = await self._get_primary_backend()
        result = await primary.retrieve_memories(query_embedding, top_k, device_filter)

        # Cache the result
        if cache and result:
            for memory in result:
                await cache.store_memory(memory)

        return result

    async def store_knowledge(self, knowledge):
        primary = await self._get_primary_backend()
        await primary.store_knowledge(knowledge)

        cache = await self._get_cache_backend()
        if cache:
            await cache.store_knowledge(knowledge)

    async def retrieve_knowledge(self, query_embedding, top_k: int = 5, source_filter=None):
        cache = await self._get_cache_backend()
        if cache:
            cached_result = await cache.retrieve_knowledge(query_embedding, top_k, source_filter)
            if cached_result:
                return cached_result

        primary = await self._get_primary_backend()
        result = await primary.retrieve_knowledge(query_embedding, top_k, source_filter)

        if cache and result:
            for knowledge in result:
                await cache.store_knowledge(knowledge)

        return result

    # Delegate other methods to primary backend
    async def get_memory_by_id(self, memory_id: str):
        primary = await self._get_primary_backend()
        return await primary.get_memory_by_id(memory_id)

    async def get_knowledge_by_id(self, knowledge_id: str):
        primary = await self._get_primary_backend()
        return await primary.get_knowledge_by_id(knowledge_id)

    async def delete_memory(self, memory_id: str):
        primary = await self._get_primary_backend()
        return await primary.delete_memory(memory_id)

    async def delete_knowledge(self, knowledge_id: str):
        primary = await self._get_primary_backend()
        return await primary.delete_knowledge(knowledge_id)

    async def get_memory_count(self):
        primary = await self._get_primary_backend()
        return await primary.get_memory_count()

    async def get_knowledge_count(self):
        primary = await self._get_primary_backend()
        return await primary.get_knowledge_count()

    async def register_device(self, device):
        primary = await self._get_primary_backend()
        await primary.register_device(device)

    async def get_device(self, device_id: str):
        primary = await self._get_primary_backend()
        return await primary.get_device(device_id)

    async def list_devices(self):
        primary = await self._get_primary_backend()
        return await primary.list_devices()

    async def store_sync_operation(self, operation):
        primary = await self._get_primary_backend()
        await primary.store_sync_operation(operation)

    async def get_pending_sync_operations(self, device_id: str):
        primary = await self._get_primary_backend()
        return await primary.get_pending_sync_operations(device_id)

    async def mark_sync_operation_resolved(self, operation_id: str):
        primary = await self._get_primary_backend()
        await primary.mark_sync_operation_resolved(operation_id)

    async def store_conversation(self, session_id: str, conversation_data):
        primary = await self._get_primary_backend()
        await primary.store_conversation(session_id, conversation_data)

    async def load_conversation(self, session_id: str):
        primary = await self._get_primary_backend()
        return await primary.load_conversation(session_id)

    async def list_conversations(self, limit: int = 50):
        primary = await self._get_primary_backend()
        return await primary.list_conversations(limit)

    async def delete_conversation(self, session_id: str):
        primary = await self._get_primary_backend()
        return await primary.delete_conversation(session_id)