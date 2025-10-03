# File Guide - Homelab Intelligence Framework (Phase 1 - Refactored)

## 🏗️ Project Structure

```
gob/                        # Workspace root
├── core/                  # 🧠 Shared intelligence framework
│   ├── brain/            # Communal brain implementation
│   │   ├── brain.py      # Main CommunalBrain API (refactored)
│   │   ├── storage/      # 🗂️ Modularized storage system
│   │   │   ├── __init__.py
│   │   │   ├── interfaces.py    # Storage backend interfaces
│   │   │   ├── config.py        # Storage configuration
│   │   │   ├── abstraction.py   # Storage abstraction layer
│   │   │   └── backends/
│   │   │       ├── __init__.py
│   │   │       └── sqlite.py    # SQLite backend implementation
│   │   ├── components/  # 🧠 Refactored brain components
│   │   │   ├── config.py        # Brain configuration
│   │   │   ├── device.py        # Device management utilities
│   │   │   └── sync.py          # Background synchronization
│   │   ├── models.py     # Data structures
│   │   ├── vector_search.py # Similarity algorithms
│   │   └── conversation_manager.py # Universal conversation tracking
│   ├── data/             # 💾 Centralized data directory
│   │   ├── communal_brain.db    # Main database
│   │   ├── last_context.txt     # Raw chat logs
│   │   ├── conversations/       # Active conversation files
│   │   ├── summaries/           # Summarization outputs
│   │   └── archive/             # Archived conversations
│   ├── config/           # ⚙️ Unified configuration system
│   │   ├── models.py     # Global configuration models
│   │   └── loader.py     # Configuration loading utilities
│   ├── di/               # 🏗️ Dependency injection container
│   │   ├── __init__.py
│   │   └── container.py  # DI container implementation
│   ├── llm/              # LLM client abstraction
│   └── logging.py        # Centralized logging
├── mini/                 # 🤖 Enhanced chatbot with communal brain
│   ├── src/core/         # Chatbot implementation
│   ├── config.toml       # Configuration
│   ├── prompts/          # System prompts
│   ├── knowledge_docs/   # Knowledge base input
│   └── docs/             # Documentation
├── nano/                 # 🔬 Simple chatbot with communal brain
│   └── main.py           # Simple chatbot implementation
├── tests/                # 🧪 Enhanced test suite
│   ├── test_memory_sharing.py   # Memory sharing tests
│   ├── test_phase1_validation.py # Phase 1 validation tests
│   └── test_full_system_integration.py # Comprehensive integration tests
├── docs/                 # 📖 Centralized documentation
└── run.py                # 🎯 CLI entry point for chatbots
```

## 📋 Core Framework (`core/`)

### `core/brain/` - Communal Brain Implementation

#### `brain.py` (12K - refactored)
**Role:** Main CommunalBrain API
- Central intelligence hub for all devices
- Memory and knowledge storage/retrieval
- Device management and registration
- Statistics and monitoring
- **Core of the shared intelligence system**
- **Refactored:** Uses DI container and modular components

#### `storage/` - Modularized Storage System 🗂️

##### `interfaces.py` (2.1K)
**Role:** Storage backend interfaces and protocols
- Abstract base classes for storage backends
- Type-safe interfaces for all storage operations
- Protocol definitions for dependency injection
- **Enables pluggable storage backends**

##### `config.py` (1.2K)
**Role:** Storage configuration management
- StorageConfig dataclass with validation
- Environment variable integration
- Path resolution and validation
- **Centralized storage configuration**

##### `abstraction.py` (2.8K)
**Role:** Storage abstraction layer
- Backend-agnostic storage interface
- Intelligent routing between backends
- Caching and performance optimization
- **Handles all data persistence operations**

##### `backends/sqlite.py` (7.2K)
**Role:** SQLite backend implementation
- Complete SQLite storage implementation
- Vector search with cosine similarity
- WAL mode for concurrency
- Comprehensive error handling
- **Production-ready local storage**

#### `components/` - Brain Component Modules 🧠

##### `config.py` (1.1K)
**Role:** Brain configuration
- BrainConfig dataclass
- Device and sync settings
- Summarizer configuration
- **Type-safe brain configuration**

##### `device.py` (2.1K)
**Role:** Device management utilities
- Hardware capability detection
- Device ID generation
- Network information gathering
- **Automated device profiling**

##### `sync.py` (1.3K)
**Role:** Background synchronization
- Cross-device sync management
- Background task coordination
- Conflict resolution framework
- **Enables distributed intelligence**

#### `conversation_manager.py` (2.5K)
**Role:** Universal conversation tracking
- Session-based conversation management
- Cross-device conversation continuity
- Conversation history retrieval
- **Enables conversation handoff between chatbots**

#### `models.py` (3.2K)
**Role:** Data structures and types
- DeviceContext, MemoryItem, KnowledgeItem
- Conversation data models
- Type definitions and validation
- **Foundation data structures**

#### `vector_search.py` (1.8K)
**Role:** Similarity algorithms
- Cosine similarity implementation
- Multiple distance metrics
- Optimized ranking algorithms
- **Powers semantic search**

### `core/llm/` - LLM Abstraction

#### `llm_client.py` (6.8K)
**Role:** LLM API interface
- Connects to OpenRouter/OpenAI
- Formats prompts and handles responses
- Error handling and retries
- **Standardized LLM interface**

### `core/config/` - Unified Configuration System ⚙️

#### `models.py` (4.8K)
**Role:** Global configuration models
- LLMConfig, EmbeddingsConfig, StorageConfig
- GlobalConfig aggregator class
- Environment variable integration
- Type validation and defaults
- **Centralized, type-safe configuration**
- **Phase 1:** Unified all configuration into single system

#### `loader.py` (2.1K)
**Role:** Configuration loading utilities
- TOML configuration loading
- Environment variable integration
- Validation and defaults
- **Configuration loading helpers**

### `core/di/` - Dependency Injection Container 🏗️

#### `container.py` (2.5K)
**Role:** Lightweight DI container
- Service registration and resolution
- Singleton and transient scopes
- Automatic dependency injection
- Type-safe service management
- **Phase 1:** Enables loose coupling and testability**

### `src/utils/` - Shared Utilities

#### `logging_config.py` (2.1K)
**Role:** Advanced logging configuration
- Console and reverse-chronological file logging
- Auto-deletes logs older than 7 days
- Keeps most recent 1000 log entries
- Newest logs appear at top of file
- Suppresses noisy third-party logs
- **Used throughout the application**

---

## 🧪 Testing (`tests/`)

### `test_phase1_validation.py` (4.2K) - **NEW**
**Role:** Phase 1 validation tests
- Validates all Phase 1 architectural changes
- Tests modular imports and DI container
- Verifies configuration and storage systems
- **Run after Phase 1 changes: `python3 tests/test_phase1_validation.py`**

### `test_full_system_integration.py` (5.6K) - **NEW**
**Role:** Comprehensive integration tests
- Tests memory storage and retrieval
- Validates conversation management
- Checks context logging and summarization
- Verifies data persistence across sessions
- **End-to-end system validation**

### `test_memory_sharing.py` (2.1K)
**Role:** Memory sharing validation
- Tests cross-device memory sharing
- Validates communal brain functionality
- **Core functionality verification**

---

## ⚙️ Configuration (`config.toml`)

### `config.toml` (1.2K)
**Role:** Centralized configuration
- LLM model and parameters
- Embedding settings
- Database configuration
- Memory and knowledge parameters
- System prompts
- **Edit this to customize behavior**

## 📚 Documentation (`docs/`)

### `QUICKSTART.md` (1.7K)
**Role:** Quick start guide
- 3-minute setup
- Basic usage examples
- Customization tips
- **Start here to get running fast**

### `FILE_GUIDE.md` (This file)
**Role:** Detailed file guide
- Complete project structure
- File roles and descriptions
- Architecture overview
- **Reference for understanding the codebase**

### `README.md` (1.8K)
**Role:** Main documentation
- Feature overview
- Installation instructions
- Architecture diagram
- Performance metrics
- **Start here for overview**

---

## 📂 Data Directories

### `core/data/` - Centralized Data Storage 💾 **UPDATED**

#### `communal_brain.db`
**Role:** Main communal database
- All memories, knowledge, and conversations
- Device registrations and capabilities
- Vector embeddings for semantic search
- **Central intelligence repository**
- **Phase 1:** Moved from `core/` to `core/data/`

#### `last_context.txt`
**Role:** Raw chat logs and context snapshots
- Shows LLM prompts being sent
- Memory retrieval results
- Conversation context building
- **Updated after each interaction**
- **Phase 1:** Moved from `core/` to `core/data/`

#### `conversations/`
**Role:** Active conversation session storage
- JSON files for conversation persistence
- Organized by session ID and timestamp
- **Real-time conversation data**

#### `summaries/`
**Role:** Summarization outputs
- Summarized conversation files
- Generated by background summarizer
- **Token-bloat management**

#### `archive/conversations/`
**Role:** Archived conversation data
- Original conversations after summarization
- Historical conversation storage
- **Long-term conversation history**

### `mini/knowledge_docs/`
**Role:** Knowledge base documents
- Contains .txt files with information
- Auto-loaded on first run
- Add your own documents here
- **Included examples:**
  - `python.txt` - Python programming info
  - `machine_learning.txt` - ML basics

### `mini/prompts/`
**Role:** System prompts
- `system.main.md` - Main system prompt
- `system.role.md` - Role definition prompt
- **Customize chatbot personality here**

---

## 🚀 Entry Points

### `main.py` (7 bytes)
**Role:** Root entry point
- Imports and runs `src.core.main()`
- **Use `python3 main.py` or `./run.sh`**

### `run.sh` (7 bytes)
**Role:** Simple bash runner
- Executes `python3 main.py` with proper path handling
- **Use `./run.sh` for easy execution**

---

## 🗄️ Generated Files (Created at Runtime)

### `core/data/communal_brain.db`
**Role:** Main communal database
- Stores all memories, knowledge, and conversations
- Device registrations and capabilities
- Conversation sessions and history
- Vector embeddings for semantic search
- **Central intelligence repository**
- **Phase 1:** Relocated to `core/data/` directory

### `core/data/communal_brain.db-wal` and `core/data/communal_brain.db-shm`
**Role:** SQLite Write-Ahead Log files
- Temporary files for WAL mode
- Better concurrency and crash resistance
- **Created automatically by SQLite**
- **Phase 1:** Now in `core/data/` directory

### `core/data/last_context.txt`
**Role:** Raw chat logs and context snapshots
- Shows LLM prompts being sent
- Memory retrieval results
- Conversation context building
- **Updated after each interaction**
- **Phase 1:** Relocated to `core/data/` directory

### `core/data/conversations/`
**Role:** Active conversation session storage
- JSON files for conversation persistence
- Organized by session ID and timestamp
- **Real-time conversation data**

### `core/data/summaries/`
**Role:** Summarization outputs
- JSON files with summarized conversations
- Generated by background summarizer agent
- **Token-bloat management**

### `core/data/archive/conversations/`
**Role:** Archived conversation data
- Original conversations after summarization
- Historical conversation storage
- **Long-term conversation history**

---

## 📊 Architecture Benefits

**Universal Intelligence:**
- One brain shared across all chatbots
- Conversation continuity between different chatbots
- Collective learning benefits all implementations
- Session-based conversation handoff

**Phase 1: Enhanced Modularity 🗂️**
- **Storage Modularization:** Monolithic storage.py (947 lines) → 4 focused modules (<300 lines each)
- **Dependency Injection:** Loose coupling with type-safe service management
- **Unified Configuration:** Single source of truth with environment variable support
- **Component Refactoring:** Brain logic split into focused, testable components

**Scalability:**
- From single device to distributed homelab
- PostgreSQL/Redis backends ready for scale
- Device capability-aware task routing
- **Phase 1:** Cleaner backend abstraction for easy scaling

**Developer Experience:**
- `./run.sh` for easy execution
- Clear documentation structure
- **Phase 1:** Enhanced test suite with validation tests
- Real-time brain sharing verified
- **Phase 1:** Improved IDE support with better imports

**Performance:**
- SQLite with WAL mode for speed
- Efficient vector operations
- Optimized memory usage
- Semantic search with relevance scoring
- **Phase 1:** Better error handling and resource management

**Maintainability:**
- **Phase 1:** Single responsibility principle across all modules
- **Phase 1:** Type-safe configuration and dependency injection
- **Phase 1:** Comprehensive validation and testing
- **Phase 1:** Clear separation of data storage in `core/data/`

