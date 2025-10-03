"""
Storage abstraction layer for the communal brain

Supports multiple storage backends:
- Local SQLite (current implementation)
- Remote PostgreSQL (for communal storage)
- Redis/Memcached (for caching)
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from .models import MemoryItem, KnowledgeItem, DeviceContext, SyncOperation, DeviceTier, DeviceStatus


@dataclass
class StorageConfig:
    """Configuration for storage backends"""
    primary_backend: str = "local"  # 'local', 'remote', 'cache'

    # Local SQLite config
    local_db_path: str = "chatbot.db"

    # Remote PostgreSQL config
    remote_host: Optional[str] = None
    remote_port: int = 5432
    remote_database: Optional[str] = None
    remote_user: Optional[str] = None
    remote_password: Optional[str] = None

    # Cache config (Redis/Memcached)
    cache_host: Optional[str] = None
    cache_port: Optional[int] = None
    cache_type: str = "redis"  # 'redis' or 'memcached'

    # General config
    enable_wal: bool = True
    cache_size: int = -64000  # 64MB for SQLite
    connection_pool_size: int = 10


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
        pass


class SQLiteBackend(StorageBackend):
    """SQLite backend - maintains compatibility with current implementation"""

    def __init__(self, config: StorageConfig):
        self.config = config
        self.db_path = Path(config.local_db_path)
        self._connection = None
        self._embedding_dim = 1536  # Default, should be configurable

    async def initialize(self) -> None:
        """Initialize SQLite database with required tables"""
        import sqlite3
        import aiosqlite

        # Create tables if they don't exist
        async with aiosqlite.connect(self.db_path) as db:
            # Enable WAL mode for better concurrency
            if self.config.enable_wal:
                await db.execute("PRAGMA journal_mode=WAL")
                await db.execute(f"PRAGMA cache_size={self.config.cache_size}")

            # Memories table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    device_id TEXT NOT NULL,
                    context TEXT,
                    timestamp TEXT NOT NULL,
                    relevance_score REAL DEFAULT 0.0,
                    tags TEXT,  -- JSON array
                    metadata TEXT,  -- JSON object
                    created_at REAL
                )
            """)

            # Knowledge table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    source TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    chunk_index INTEGER DEFAULT 0,
                    total_chunks INTEGER DEFAULT 1,
                    timestamp TEXT NOT NULL,
                    relevance_score REAL DEFAULT 0.0,
                    tags TEXT,  -- JSON array
                    metadata TEXT,  -- JSON object
                    created_at REAL
                )
            """)

            # Devices table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    hardware_tier TEXT NOT NULL,
                    capabilities TEXT,  -- JSON array
                    specialization TEXT,
                    location TEXT,
                    ip_address TEXT,
                    hostname TEXT,
                    last_seen TEXT NOT NULL,
                    status TEXT NOT NULL,
                    version TEXT,
                    metadata TEXT,  -- JSON object
                    created_at REAL
                )
            """)

            # Sync operations table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sync_operations (
                    operation_id TEXT PRIMARY KEY,
                    operation_type TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT,  -- JSON object
                    resolved INTEGER DEFAULT 0,
                    created_at REAL
                )
            """)

            # Conversations table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    chatbot_name TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT NOT NULL,
                    metadata TEXT,  -- JSON object
                    turns TEXT,  -- JSON array of conversation turns
                    created_at REAL,
                    updated_at REAL
                )
            """)

            # Create indexes for performance
            await db.execute("CREATE INDEX IF NOT EXISTS idx_memories_device ON memories(device_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_device ON knowledge(device_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge(source)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_sync_device ON sync_operations(device_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_sync_resolved ON sync_operations(resolved)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_conversations_device ON conversations(device_id)")

            await db.commit()

    async def close(self) -> None:
        """Close database connection"""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def store_memory(self, memory: MemoryItem) -> None:
        """Store a memory item"""
        import aiosqlite
        import json

        async with aiosqlite.connect(self.db_path) as db:
            # Convert embedding to bytes
            embedding_bytes = self._embedding_to_bytes(memory.embedding)

            await db.execute("""
                INSERT OR REPLACE INTO memories
                (id, user_message, bot_response, embedding, device_id, context,
                 timestamp, relevance_score, tags, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id,
                memory.user_message,
                memory.bot_response,
                embedding_bytes,
                memory.device_id,
                memory.context,
                memory.timestamp.isoformat(),
                memory.relevance_score,
                json.dumps(memory.tags),
                json.dumps(memory.metadata),
                memory.timestamp.timestamp()
            ))
            await db.commit()

    async def retrieve_memories(self, query_embedding: List[float], top_k: int = 5,
                               device_filter: Optional[str] = None) -> List[MemoryItem]:
        """Retrieve similar memories using cosine similarity"""
        import aiosqlite
        import json
        from .vector_search import cosine_similarity

        async with aiosqlite.connect(self.db_path) as db:
            # Build query
            query = """
                SELECT id, user_message, bot_response, embedding, device_id, context,
                       timestamp, relevance_score, tags, metadata
                FROM memories
            """
            params = []

            if device_filter:
                query += " WHERE device_id = ?"
                params.append(device_filter)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(top_k * 10)  # Get more for similarity ranking

            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()

            memories = []
            for row in rows:
                embedding = self._bytes_to_embedding(row[3])
                similarity = cosine_similarity(query_embedding, embedding)

                memory = MemoryItem(
                    id=row[0],
                    user_message=row[1],
                    bot_response=row[2],
                    embedding=embedding,
                    device_id=row[4],
                    context=row[5] or "",
                    timestamp=datetime.fromisoformat(row[6]),
                    relevance_score=similarity,
                    tags=json.loads(row[8]) if row[8] else [],
                    metadata=json.loads(row[9]) if row[9] else {}
                )
                memories.append(memory)

            # Sort by similarity and return top_k
            memories.sort(key=lambda x: x.relevance_score, reverse=True)
            return memories[:top_k]

    async def store_knowledge(self, knowledge: KnowledgeItem) -> None:
        """Store a knowledge item"""
        import aiosqlite
        import json

        async with aiosqlite.connect(self.db_path) as db:
            embedding_bytes = self._embedding_to_bytes(knowledge.embedding)

            await db.execute("""
                INSERT OR REPLACE INTO knowledge
                (id, content, embedding, source, device_id, chunk_index, total_chunks,
                 timestamp, relevance_score, tags, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                knowledge.id,
                knowledge.content,
                embedding_bytes,
                knowledge.source,
                knowledge.device_id,
                knowledge.chunk_index,
                knowledge.total_chunks,
                knowledge.timestamp.isoformat(),
                knowledge.relevance_score,
                json.dumps(knowledge.tags),
                json.dumps(knowledge.metadata),
                knowledge.timestamp.timestamp()
            ))
            await db.commit()

    async def retrieve_knowledge(self, query_embedding: List[float], top_k: int = 5,
                                source_filter: Optional[str] = None) -> List[KnowledgeItem]:
        """Retrieve similar knowledge using cosine similarity"""
        import aiosqlite
        import json
        from .vector_search import cosine_similarity

        async with aiosqlite.connect(self.db_path) as db:
            query = """
                SELECT id, content, embedding, source, device_id, chunk_index, total_chunks,
                       timestamp, relevance_score, tags, metadata
                FROM knowledge
            """
            params = []

            if source_filter:
                query += " WHERE source = ?"
                params.append(source_filter)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(top_k * 10)

            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()

            knowledge_items = []
            for row in rows:
                embedding = self._bytes_to_embedding(row[2])
                similarity = cosine_similarity(query_embedding, embedding)

                item = KnowledgeItem(
                    id=row[0],
                    content=row[1],
                    embedding=embedding,
                    source=row[3],
                    device_id=row[4],
                    chunk_index=row[5],
                    total_chunks=row[6],
                    timestamp=datetime.fromisoformat(row[7]),
                    relevance_score=similarity,
                    tags=json.loads(row[9]) if row[9] else [],
                    metadata=json.loads(row[10]) if row[10] else {}
                )
                knowledge_items.append(item)

            knowledge_items.sort(key=lambda x: x.relevance_score, reverse=True)
            return knowledge_items[:top_k]

    async def get_memory_by_id(self, memory_id: str) -> Optional[MemoryItem]:
        """Get a specific memory by ID"""
        import aiosqlite
        import json

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id, user_message, bot_response, embedding, device_id, context,
                       timestamp, relevance_score, tags, metadata
                FROM memories WHERE id = ?
            """, (memory_id,))

            row = await cursor.fetchone()
            if not row:
                return None

            return MemoryItem(
                id=row[0],
                user_message=row[1],
                bot_response=row[2],
                embedding=self._bytes_to_embedding(row[3]),
                device_id=row[4],
                context=row[5] or "",
                timestamp=datetime.fromisoformat(row[6]),
                relevance_score=row[7],
                tags=json.loads(row[8]) if row[8] else [],
                metadata=json.loads(row[9]) if row[9] else {}
            )

    async def get_knowledge_by_id(self, knowledge_id: str) -> Optional[KnowledgeItem]:
        """Get a specific knowledge item by ID"""
        import aiosqlite
        import json

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id, content, embedding, source, device_id, chunk_index, total_chunks,
                       timestamp, relevance_score, tags, metadata
                FROM knowledge WHERE id = ?
            """, (knowledge_id,))

            row = await cursor.fetchone()
            if not row:
                return None

            return KnowledgeItem(
                id=row[0],
                content=row[1],
                embedding=self._bytes_to_embedding(row[2]),
                source=row[3],
                device_id=row[4],
                chunk_index=row[5],
                total_chunks=row[6],
                timestamp=datetime.fromisoformat(row[7]),
                relevance_score=row[8],
                tags=json.loads(row[9]) if row[9] else [],
                metadata=json.loads(row[10]) if row[10] else {}
            )

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory item"""
        import aiosqlite

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def delete_knowledge(self, knowledge_id: str) -> bool:
        """Delete a knowledge item"""
        import aiosqlite

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM knowledge WHERE id = ?", (knowledge_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def get_memory_count(self) -> int:
        """Get total number of memories"""
        import aiosqlite

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM memories")
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def get_knowledge_count(self) -> int:
        """Get total number of knowledge items"""
        import aiosqlite

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM knowledge")
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def register_device(self, device: DeviceContext) -> None:
        """Register or update a device"""
        import aiosqlite
        import json

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO devices
                (device_id, hardware_tier, capabilities, specialization, location,
                 ip_address, hostname, last_seen, status, version, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                device.device_id,
                device.hardware_tier.value,
                json.dumps(device.capabilities),
                device.specialization,
                device.location,
                device.ip_address,
                device.hostname,
                device.last_seen.isoformat(),
                device.status.value,
                device.version,
                json.dumps(device.metadata),
                device.last_seen.timestamp()
            ))
            await db.commit()

    async def get_device(self, device_id: str) -> Optional[DeviceContext]:
        """Get device information"""
        import aiosqlite
        import json

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT device_id, hardware_tier, capabilities, specialization, location,
                       ip_address, hostname, last_seen, status, version, metadata
                FROM devices WHERE device_id = ?
            """, (device_id,))

            row = await cursor.fetchone()
            if not row:
                return None

            return DeviceContext(
                device_id=row[0],
                hardware_tier=DeviceTier(row[1]),
                capabilities=json.loads(row[2]) if row[2] else [],
                specialization=row[3],
                location=row[4],
                ip_address=row[5],
                hostname=row[6],
                last_seen=datetime.fromisoformat(row[7]),
                status=DeviceStatus(row[8]),
                version=row[9],
                metadata=json.loads(row[10]) if row[10] else {}
            )

    async def list_devices(self) -> List[DeviceContext]:
        """List all registered devices"""
        import aiosqlite
        import json

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT device_id, hardware_tier, capabilities, specialization, location,
                       ip_address, hostname, last_seen, status, version, metadata
                FROM devices ORDER BY last_seen DESC
            """)

            rows = await cursor.fetchall()
            devices = []

            for row in rows:
                device = DeviceContext(
                    device_id=row[0],
                    hardware_tier=DeviceTier(row[1]),
                    capabilities=json.loads(row[2]) if row[2] else [],
                    specialization=row[3],
                    location=row[4],
                    ip_address=row[5],
                    hostname=row[6],
                    last_seen=datetime.fromisoformat(row[7]),
                    status=DeviceStatus(row[8]),
                    version=row[9],
                    metadata=json.loads(row[10]) if row[10] else {}
                )
                devices.append(device)

            return devices

    async def store_sync_operation(self, operation: SyncOperation) -> None:
        """Store a sync operation for later processing"""
        import aiosqlite
        import json

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO sync_operations
                (operation_id, operation_type, item_type, item_id, device_id,
                 timestamp, data, resolved, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                operation.operation_id,
                operation.operation_type,
                operation.item_type,
                operation.item_id,
                operation.device_id,
                operation.timestamp.isoformat(),
                json.dumps(operation.data),
                1 if operation.resolved else 0,
                operation.timestamp.timestamp()
            ))
            await db.commit()

    async def get_pending_sync_operations(self, device_id: str) -> List[SyncOperation]:
        """Get pending sync operations for a device"""
        import aiosqlite
        import json

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT operation_id, operation_type, item_type, item_id, device_id,
                       timestamp, data, resolved
                FROM sync_operations
                WHERE device_id = ? AND resolved = 0
                ORDER BY created_at ASC
            """, (device_id,))

            rows = await cursor.fetchall()
            operations = []

            for row in rows:
                operation = SyncOperation(
                    operation_id=row[0],
                    operation_type=row[1],
                    item_type=row[2],
                    item_id=row[3],
                    device_id=row[4],
                    timestamp=datetime.fromisoformat(row[5]),
                    data=json.loads(row[6]) if row[6] else {},
                    resolved=bool(row[7])
                )
                operations.append(operation)

            return operations

    async def mark_sync_operation_resolved(self, operation_id: str) -> None:
        """Mark a sync operation as resolved"""
        import aiosqlite

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE sync_operations SET resolved = 1 WHERE operation_id = ?
            """, (operation_id,))
            await db.commit()

    async def store_conversation(self, session_id: str, conversation_data: Dict[str, Any]) -> None:
        """Store conversation data"""
        import aiosqlite
        import json

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO conversations
                (session_id, chatbot_name, device_id, start_time, end_time, status, metadata, turns, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                conversation_data.get('chatbot_name', 'unknown'),
                conversation_data.get('device_id', 'unknown'),
                conversation_data.get('start_time', ''),
                conversation_data.get('end_time'),
                conversation_data.get('status', 'unknown'),
                json.dumps(conversation_data.get('metadata', {})),
                json.dumps(conversation_data.get('turns', [])),
                conversation_data.get('timestamp', '').replace('T', ' ').replace('Z', '') if conversation_data.get('timestamp') else None,
                conversation_data.get('timestamp', '').replace('T', ' ').replace('Z', '') if conversation_data.get('timestamp') else None
            ))
            await db.commit()

    async def load_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation data"""
        import aiosqlite
        import json

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT session_id, chatbot_name, device_id, start_time, end_time, status, metadata, turns
                FROM conversations WHERE session_id = ?
            """, (session_id,))

            row = await cursor.fetchone()
            if not row:
                return None

            return {
                'session_id': row[0],
                'chatbot_name': row[1],
                'device_id': row[2],
                'start_time': row[3],
                'end_time': row[4],
                'status': row[5],
                'metadata': json.loads(row[6]) if row[6] else {},
                'turns': json.loads(row[7]) if row[7] else []
            }

    async def list_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List conversations"""
        import aiosqlite
        import json

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT session_id, chatbot_name, device_id, start_time, end_time, status, metadata, turns
                FROM conversations ORDER BY created_at DESC LIMIT ?
            """, (limit,))

            rows = await cursor.fetchall()
            conversations = []

            for row in rows:
                conversations.append({
                    'session_id': row[0],
                    'chatbot_name': row[1],
                    'device_id': row[2],
                    'start_time': row[3],
                    'end_time': row[4],
                    'status': row[5],
                    'metadata': json.loads(row[6]) if row[6] else {},
                    'turns': json.loads(row[7]) if row[7] else []
                })

            return conversations

    async def delete_conversation(self, session_id: str) -> bool:
        """Delete a conversation"""
        import aiosqlite

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            await db.commit()
            return cursor.rowcount > 0

    def _embedding_to_bytes(self, embedding: List[float]) -> bytes:
        """Convert embedding list to bytes for storage"""
        import struct
        return struct.pack(f'{len(embedding)}f', *embedding)

    def _bytes_to_embedding(self, data: bytes) -> List[float]:
        """Convert bytes back to embedding list"""
        import struct
        return list(struct.unpack(f'{len(data)//4}f', data))


class StorageAbstraction:
    """Main storage abstraction that manages multiple backends"""

    def __init__(self, config: StorageConfig):
        self.config = config
        self.backends: Dict[str, StorageBackend] = {}

        # Initialize backends
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
    async def store_memory(self, memory: MemoryItem) -> None:
        primary = await self._get_primary_backend()
        await primary.store_memory(memory)

        # Also store in cache if available
        cache = await self._get_cache_backend()
        if cache:
            await cache.store_memory(memory)

    async def retrieve_memories(self, query_embedding: List[float], top_k: int = 5,
                               device_filter: Optional[str] = None) -> List[MemoryItem]:
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

    async def store_knowledge(self, knowledge: KnowledgeItem) -> None:
        primary = await self._get_primary_backend()
        await primary.store_knowledge(knowledge)

        cache = await self._get_cache_backend()
        if cache:
            await cache.store_knowledge(knowledge)

    async def retrieve_knowledge(self, query_embedding: List[float], top_k: int = 5,
                                source_filter: Optional[str] = None) -> List[KnowledgeItem]:
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
    async def get_memory_by_id(self, memory_id: str) -> Optional[MemoryItem]:
        primary = await self._get_primary_backend()
        return await primary.get_memory_by_id(memory_id)

    async def get_knowledge_by_id(self, knowledge_id: str) -> Optional[KnowledgeItem]:
        primary = await self._get_primary_backend()
        return await primary.get_knowledge_by_id(knowledge_id)

    async def delete_memory(self, memory_id: str) -> bool:
        primary = await self._get_primary_backend()
        return await primary.delete_memory(memory_id)

    async def delete_knowledge(self, knowledge_id: str) -> bool:
        primary = await self._get_primary_backend()
        return await primary.delete_knowledge(knowledge_id)

    async def get_memory_count(self) -> int:
        primary = await self._get_primary_backend()
        return await primary.get_memory_count()

    async def get_knowledge_count(self) -> int:
        primary = await self._get_primary_backend()
        return await primary.get_knowledge_count()

    async def register_device(self, device: DeviceContext) -> None:
        primary = await self._get_primary_backend()
        await primary.register_device(device)

    async def get_device(self, device_id: str) -> Optional[DeviceContext]:
        primary = await self._get_primary_backend()
        return await primary.get_device(device_id)

    async def list_devices(self) -> List[DeviceContext]:
        primary = await self._get_primary_backend()
        return await primary.list_devices()

    async def store_sync_operation(self, operation: SyncOperation) -> None:
        primary = await self._get_primary_backend()
        await primary.store_sync_operation(operation)

    async def get_pending_sync_operations(self, device_id: str) -> List[SyncOperation]:
        primary = await self._get_primary_backend()
        return await primary.get_pending_sync_operations(device_id)

    async def mark_sync_operation_resolved(self, operation_id: str) -> None:
        primary = await self._get_primary_backend()
        await primary.mark_sync_operation_resolved(operation_id)

    async def store_conversation(self, session_id: str, conversation_data: Dict[str, Any]) -> None:
        primary = await self._get_primary_backend()
        await primary.store_conversation(session_id, conversation_data)

    async def load_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        primary = await self._get_primary_backend()
        return await primary.load_conversation(session_id)

    async def list_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        primary = await self._get_primary_backend()
        return await primary.list_conversations(limit)

    async def delete_conversation(self, session_id: str) -> bool:
        primary = await self._get_primary_backend()
        return await primary.delete_conversation(session_id)