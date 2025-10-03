# Core Intelligence Framework

The `core/` directory contains the shared communal brain and foundational components that power all chatbot implementations in the homelab.

## Overview

This package provides:

- **Communal Brain**: Shared intelligence system across all devices
- **Storage Abstraction**: Backend-agnostic data persistence
- **Device Management**: Hardware-aware device coordination
- **Vector Search**: Semantic similarity algorithms
- **Synchronization**: Cross-device data consistency

## Architecture

```
core/
├── brain/              # Communal brain implementation
│   ├── brain.py        # Main CommunalBrain API
│   ├── storage.py      # Storage abstraction layer
│   ├── models.py       # Data structures
│   ├── vector_search.py # Similarity algorithms
│   └── __init__.py     # Package exports
├── __init__.py         # Core package exports
└── README.md           # This file
```

## Quick Start

```python
from core import CommunalBrain, BrainConfig

# Configure for local development
config = BrainConfig()
config.storage.primary_backend = "local"  # Use SQLite

# Initialize communal brain
brain = CommunalBrain(config)
await brain.initialize()

# Store a memory
memory_id = await brain.store_memory(
    user_message="How do I sort a list in Python?",
    bot_response="Use sorted() or list.sort()",
    embedding=[0.1, 0.2, ...]  # Vector embedding
)

# Retrieve similar memories
memories = await brain.retrieve_memories(
    query_embedding=[0.1, 0.2, ...],
    top_k=3
)
```

## Usage in Chatbots

All chatbots should import and use the communal brain:

```python
# In your chatbot implementation
import sys
sys.path.append('..')  # Add parent directory to path
from core import CommunalBrain, BrainConfig

class MyChatbot:
    def __init__(self):
        self.brain = CommunalBrain(BrainConfig())
        # ... rest of initialization
```

## Configuration

### Storage Backends

```python
config = BrainConfig()

# Local SQLite (development)
config.storage.primary_backend = "local"
config.storage.local_db_path = "shared_brain.db"

# Remote PostgreSQL (production)
config.storage.primary_backend = "remote"
config.storage.remote_host = "brain-server.local"
config.storage.remote_database = "communal_brain"

# Redis caching
config.storage.cache_host = "redis.local"
config.storage.cache_port = 6379
```

### Device Configuration

```python
config = BrainConfig()
config.device_name = "Raspberry Pi Assistant"
config.device_location = "server_rack_1"
config.hardware_tier = DeviceTier.RASPBERRY_PI
```

## Dependencies

```txt
aiosqlite>=0.19.0    # Async SQLite operations
psutil>=5.9.0        # Hardware capability detection
```

## Development

### Running Tests

```bash
cd ../mini  # Tests are in mini directory for now
python test_brain.py
```

### Adding New Features

1. **New Storage Backend**: Implement `StorageBackend` interface
2. **New Data Model**: Add to `models.py` with serialization methods
3. **New Brain Feature**: Add to `CommunalBrain` class
4. **Update Exports**: Add to `__init__.py` `__all__` list

## Integration with Chatbots

The core framework is designed to be imported by multiple chatbot implementations:

- `mini/` - Basic chatbot with communal brain
- `agent/` - Advanced agent with multi-tier capabilities (future)
- `specialist/` - Domain-specific chatbots (future)

Each chatbot remains independent but shares the same intelligence pool through the communal brain.

## Version History

- **1.0.0**: Initial release with SQLite backend and basic communal brain functionality