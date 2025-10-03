# Communal Brain Architecture

## Overview

The Communal Brain is the central intelligence system that enables collective learning and knowledge sharing across multiple chatbot instances running on different devices in your homelab. Instead of each device having its own isolated memory and knowledge base, all devices contribute to and draw from a shared intelligence pool.

## Core Philosophy

**"One Brain, Many Bodies"** - Your homelab devices act as different embodiments of the same intelligent system, each specialized for their hardware capabilities while sharing all learned knowledge and experiences.

## Key Principles

### 1. **Shared Intelligence**
- All conversation memories are stored in a communal pool
- Knowledge from any device becomes available to all devices
- Learning on one device benefits the entire system

### 2. **Device Attribution**
- Every memory and knowledge item tracks which device created it
- Enables specialization and expertise tracking
- Supports conflict resolution and provenance

### 3. **Hardware-Aware Distribution**
- Tasks are routed to devices with appropriate capabilities
- Low-power devices handle simple queries
- High-performance devices tackle complex reasoning
- Automatic capability detection and registration

### 4. **Resilient Architecture**
- Local caching for offline operation
- Synchronization when network is available
- Graceful degradation during network issues
- Conflict resolution for concurrent updates

## Architecture Components

### Storage Abstraction Layer

The storage system is designed to be backend-agnostic, allowing seamless migration from local development to distributed production systems.

```python
class StorageAbstraction:
    """Manages multiple storage backends with intelligent routing"""

    backends = {
        'local': SQLiteBackend(),      # Development/local storage
        'remote': PostgreSQLBackend(), # Production distributed storage
        'cache': RedisBackend()        # High-performance caching
    }

    async def store_memory(self, memory: MemoryItem):
        # Store in primary backend
        await self.backends['remote'].store_memory(memory)

        # Cache locally for fast access
        await self.backends['cache'].store_memory(memory)
```

#### Supported Backends

1. **SQLite** (Local Development)
   - Zero-configuration setup
   - Full vector search capabilities
   - WAL mode for concurrency
   - Compatible with existing mini implementation

2. **PostgreSQL** (Production Distributed)
   - Multi-device concurrent access
   - Advanced indexing and query optimization
   - Built-in replication and backup
   - pgvector extension for vector operations

3. **Redis/Memcached** (Caching Layer)
   - Sub-millisecond retrieval for hot data
   - Automatic cache invalidation
   - Distributed cache clustering support

### Data Models

#### DeviceContext
Represents a device in the communal brain network:

```python
@dataclass
class DeviceContext:
    device_id: str                    # Unique identifier
    hardware_tier: DeviceTier        # RASPBERRY_PI, LAPTOP, WORKSTATION, SERVER
    capabilities: List[str]          # ['gpu', 'high_memory', 'fast_network']
    specialization: Optional[str]    # 'research', 'coding', 'analysis'
    location: str                    # Physical location in homelab
    status: DeviceStatus             # ONLINE, OFFLINE, SYNCING
```

#### MemoryItem
A conversation memory with full attribution:

```python
@dataclass
class MemoryItem:
    id: str                          # Unique memory ID
    user_message: str               # User's input
    bot_response: str              # Bot's response
    embedding: List[float]         # Vector representation
    device_id: str                 # Which device created this
    context: str                   # Additional context
    timestamp: datetime            # When it was created
    tags: List[str]                # Categorization tags
```

#### KnowledgeItem
Structured knowledge with source tracking:

```python
@dataclass
class KnowledgeItem:
    id: str                        # Unique knowledge ID
    content: str                   # The knowledge content
    embedding: List[float]        # Vector representation
    source: str                    # File path, URL, or device
    device_id: str                 # Contributing device
    chunk_index: int              # For chunked content
    total_chunks: int             # Total chunks in document
```

### Communal Brain API

The main interface that all chatbots use:

```python
class CommunalBrain:
    """Central intelligence hub"""

    async def store_memory(self, user_msg: str, bot_response: str,
                          embedding: List[float]) -> str:
        """Store conversation memory in communal pool"""

    async def retrieve_memories(self, query_embedding: List[float],
                               top_k: int = 5) -> List[MemoryItem]:
        """Find similar memories across all devices"""

    async def store_knowledge(self, content: str, embedding: List[float],
                             source: str) -> str:
        """Add knowledge to communal pool"""

    async def retrieve_knowledge(self, query_embedding: List[float],
                                top_k: int = 5) -> List[KnowledgeItem]:
        """Find relevant knowledge from any device"""
```

## Synchronization & Conflict Resolution

### Sync Operations
Cross-device changes are tracked and synchronized:

```python
@dataclass
class SyncOperation:
    operation_type: str    # 'create', 'update', 'delete'
    item_type: str        # 'memory', 'knowledge', 'device'
    item_id: str          # ID of the item being synced
    device_id: str        # Source device
    data: Dict           # The actual data payload
    resolved: bool       # Whether this operation is complete
```

### Conflict Resolution Strategies

1. **Last Write Wins** (Simple)
   - Most recent update takes precedence
   - Fast and simple for most cases

2. **Device Priority** (Hierarchical)
   - Server > Workstation > Laptop > Raspberry Pi
   - Higher-tier devices override lower-tier

3. **Content Merge** (Intelligent)
   - AI-powered merging of conflicting content
   - Preserves important information from both versions

## Implementation Details

### Current Implementation Status

#### ✅ Completed Components (Phase 1 Enhanced)

1. **Storage Abstraction Layer** 🗂️
     - **Modularized:** Monolithic storage.py → 4 focused modules ✅
     - Abstract backend interface with protocols ✅
     - SQLite backend implementation (499 lines) ✅
     - PostgreSQL/Redis backend interfaces ready ✅
     - Intelligent caching and routing logic ✅

2. **Data Models**
     - Complete type definitions ✅
     - Serialization/deserialization ✅
     - Validation and constraints ✅

3. **Communal Brain API**
     - Core CRUD operations ✅
     - Device management ✅
     - Statistics and monitoring ✅
     - **Refactored:** Uses DI container and modular components ✅

4. **Universal Conversation Manager**
     - Centralized conversation tracking ✅
     - Session-based conversation continuity ✅
     - Cross-device conversation handoff ✅
     - Conversation persistence and retrieval ✅

5. **Device Management** 🧠
     - Auto-detection of hardware capabilities ✅
     - Dynamic registration and heartbeat ✅
     - Capability-based task routing ✅
     - **Modularized:** Extracted to components/device.py ✅

6. **Vector Search**
     - Cosine similarity implementation ✅
     - Multiple distance metrics ✅
     - Optimized ranking algorithms ✅

7. **Configuration System** ⚙️
     - Unified configuration management ✅
     - Environment variable integration ✅
     - Type-safe configuration models ✅
     - Hierarchical config loading ✅

8. **Dependency Injection** 🏗️
     - Lightweight DI container ✅
     - Service registration and resolution ✅
     - Automatic dependency injection ✅
     - Type-safe service management ✅

9. **Chatbot Integration**
     - Mini chatbot with universal conversations ✅
     - Nano chatbot with universal conversations ✅
     - Session management across chatbots ✅
     - Real-time brain sharing verified ✅
     - **Updated:** Both use data/ directory for storage ✅

10. **Data Organization** 💾
     - Centralized data directory structure ✅
     - Organized storage for logs, summaries, archives ✅
     - Proper separation of persistent data ✅

#### 🚧 In Progress / Planned

1. **Network Synchronization**
    - WebSocket-based real-time sync
    - Offline queue management
    - Conflict resolution engine

2. **Multi-Device Testing**
    - Test with multiple physical devices
    - Validate cross-device memory sharing
    - Performance benchmarking

3. **Agent Framework Foundation**
    - Base agent classes
    - Extension hook system
    - Streaming infrastructure

### File Structure (Phase 1 - Refactored)

```
core/                    # Shared intelligence framework
├── brain/              # Communal brain implementation
│   ├── __init__.py     # Brain package exports
│   ├── brain.py        # Main CommunalBrain API (refactored)
│   ├── storage/        # 🗂️ Modularized storage system
│   │   ├── __init__.py
│   │   ├── interfaces.py    # Storage backend interfaces
│   │   ├── config.py        # Storage configuration
│   │   ├── abstraction.py   # Storage abstraction layer
│   │   └── backends/
│   │       ├── __init__.py
│   │       └── sqlite.py    # SQLite backend implementation
│   ├── components/     # 🧠 Refactored brain components
│   │   ├── config.py        # Brain configuration
│   │   ├── device.py        # Device management utilities
│   │   └── sync.py          # Background synchronization
│   ├── models.py       # Data structures
│   ├── vector_search.py # Similarity algorithms
│   └── conversation_manager.py # Universal conversation tracking
├── data/               # 💾 Centralized data directory
│   ├── communal_brain.db    # Main database
│   ├── last_context.txt     # Raw chat logs
│   ├── conversations/       # Active conversation files
│   ├── summaries/           # Summarization outputs
│   └── archive/             # Archived conversations
├── config/             # ⚙️ Unified configuration system
│   ├── models.py       # Global configuration models
│   └── loader.py       # Configuration loading utilities
├── di/                 # 🏗️ Dependency injection container
│   ├── __init__.py
│   └── container.py    # DI container implementation
├── llm/                # LLM client abstraction
└── logging.py          # Centralized logging

mini/                  # Enhanced chatbot with communal brain
├── src/core/          # Chatbot implementation
├── config.toml        # Configuration
├── main.py            # Entry point
├── prompts/           # System prompts
├── knowledge_docs/    # Knowledge base input
└── docs/             # Documentation

nano/                  # Simple chatbot with communal brain
└── main.py           # Simple chatbot implementation

tests/                 # 🧪 Enhanced test suite
├── test_memory_sharing.py        # Memory sharing tests
├── test_phase1_validation.py     # Phase 1 validation tests
└── test_full_system_integration.py # Comprehensive integration tests

docs/                  # 📖 Centralized documentation
├── CENTRALBRAIN.md    # Communal brain architecture
├── FILE_GUIDE.md      # File organization guide
├── PROJECT_STATUS.md  # Current implementation status
└── QUICKSTART.md      # Getting started guide

run.py                 # 🎯 CLI entry point for selecting chatbots
```

### Dependencies Added

```txt
aiosqlite>=0.19.0      # Async SQLite operations
psutil>=5.9.0          # Hardware capability detection
```

## Usage Examples

### Basic Usage

```python
from core import CommunalBrain, BrainConfig

# Initialize communal brain
config = BrainConfig()
brain = CommunalBrain(config)
await brain.initialize()

# Store a conversation memory
memory_id = await brain.store_memory(
    user_message="How do I sort a list in Python?",
    bot_response="Use the sorted() function or list.sort() method",
    embedding=[0.1, 0.2, ...]  # Vector embedding
)

# Retrieve similar memories
similar = await brain.retrieve_memories(
    query_embedding=[0.1, 0.2, ...],
    top_k=3
)
```

### Device-Aware Operations

```python
# Get all registered devices
devices = await brain.list_devices()

# Find devices with GPU capabilities
gpu_devices = [d for d in devices if 'gpu' in d.capabilities]

# Update device context
await brain.update_device_context(
    specialization='coding_assistant',
    location='server_rack_3'
)
```

## Benefits & Use Cases

### For Your Homelab Setup

1. **Raspberry Pi Chatbot**
   - Handles simple queries locally
   - Contributes memories to communal pool
   - Benefits from knowledge learned on powerful devices

2. **Workstation Agent**
   - Tackles complex reasoning tasks
   - Trains on communal knowledge
   - Shares advanced insights with all devices

3. **Server-Based Knowledge Hub**
   - Maintains authoritative knowledge base
   - Handles synchronization across devices
   - Provides backup and archival storage

### Performance Optimizations

- **Local Caching**: Frequently accessed data cached locally
- **Lazy Loading**: Knowledge loaded on-demand
- **Background Sync**: Synchronization happens asynchronously
- **Compression**: Automatic compression for network transfer

## Future Extensions

### Tier 2: Agent Capabilities
- Multi-agent communication protocols
- Hierarchical agent relationships
- Prompt-driven behavior configuration

### Tier 3: Advanced Features
- Real-time streaming responses
- User intervention capabilities
- External API integrations (MCP)
- Distributed agent orchestration

## Migration Path

### From Current Mini
1. Replace local `MemoryStore` with `CommunalBrain`
2. Update `KnowledgeBase` to use communal storage
3. Add device context to all operations
4. Maintain existing API compatibility

### Scaling Strategy
1. Start with SQLite backend (development)
2. Migrate to PostgreSQL (production)
3. Add Redis caching (performance)
4. Implement distributed synchronization (scale)

## Monitoring & Debugging

### Built-in Statistics
```python
stats = await brain.get_memory_stats()
# Returns: memory_count, knowledge_count, device_count, etc.
```

### Health Checks
- Device connectivity monitoring
- Storage backend health
- Synchronization status
- Performance metrics

This communal brain architecture provides the foundation for true collective intelligence across your homelab, where each device specializes in its strengths while contributing to a shared, growing knowledge base.