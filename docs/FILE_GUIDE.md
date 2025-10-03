# File Guide - Chatbot v2

## 🏗️ Project Structure
# File Guide - Homelab Intelligence Framework

## 🏗️ Project Structure

```
gob/                        # Workspace root
├── core/                  # 🧠 Shared intelligence framework
│   ├── brain/            # Communal brain implementation
│   │   ├── brain.py      # Main CommunalBrain API
│   │   ├── storage.py    # Storage abstraction layer
│   │   ├── models.py     # Data structures
│   │   ├── vector_search.py # Similarity algorithms
│   │   └── conversation_manager.py # Universal conversation tracking
│   ├── communal_brain.db # Live communal database
│   ├── config/           # Global configuration system
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
├── tests/                # 🧪 Test suite
├── docs/                 # 📖 Centralized documentation
└── run.py                # 🎯 CLI entry point for chatbots
```

## 📋 Core Framework (`core/`)

### `core/brain/` - Communal Brain Implementation

#### `brain.py` (18K)
**Role:** Main CommunalBrain API
- Central intelligence hub for all devices
- Memory and knowledge storage/retrieval
- Device management and registration
- Statistics and monitoring
- **Core of the shared intelligence system**

#### `storage.py` (25K)
**Role:** Storage abstraction layer
- Backend-agnostic storage interface
- SQLite implementation with vector search
- PostgreSQL/Redis backend support
- Conversation persistence
- **Handles all data persistence**

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

### `core/config/` - Global Configuration

#### `loader.py` (2.1K)
**Role:** Configuration management
- TOML configuration loading
- Environment variable integration
- Validation and defaults
- **Centralized configuration system**

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

### `smoke_test.py` (8.5K)
**Role:** Comprehensive smoke test
- Tests all components without external APIs
- Validates imports and basic functionality
- Uses mock LLM client for testing
- **Run to verify everything works**

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

### `knowledge_docs/`
**Role:** Knowledge base documents
- Contains .txt files with information
- Auto-loaded on first run
- Add your own documents here
- **Included examples:**
  - `python.txt` - Python programming info
  - `machine_learning.txt` - ML basics

### `prompts/`
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

### `core/communal_brain.db`
**Role:** Communal SQLite database
- Stores all memories, knowledge, and conversations
- Device registrations and capabilities
- Conversation sessions and history
- Vector embeddings for semantic search
- **Central intelligence repository for all chatbots**

### `core/communal_brain.db-wal` and `core/communal_brain.db-shm`
**Role:** SQLite Write-Ahead Log files
- Temporary files for WAL mode
- Better concurrency and crash resistance
- **Created automatically by SQLite**

### `core/data/last_context.txt`
**Role:** Debug context snapshots
- Shows LLM prompts being sent
- Memory retrieval results
- Conversation context building
- **Updated after each interaction**

### `core/data/conversations/`
**Role:** Conversation session storage
- JSON files for conversation persistence
- Organized by session ID and timestamp
- **Legacy storage, now superseded by database**

---

## 📊 Architecture Benefits

**Universal Intelligence:**
- One brain shared across all chatbots
- Conversation continuity between different chatbots
- Collective learning benefits all implementations
- Session-based conversation handoff

**Modular Design:**
- Clear separation of concerns
- Easy to extend and maintain
- Stable import paths via `__init__.py`
- Backend-agnostic storage abstraction

**Scalability:**
- From single device to distributed homelab
- PostgreSQL backend ready for scale
- Redis caching for performance
- Device capability-aware task routing

**Developer Experience:**
- `./run.sh` for easy execution
- Clear documentation structure
- Comprehensive test suite
- Real-time brain sharing verified

**Performance:**
- SQLite with WAL mode for speed
- Efficient vector operations
- Optimized memory usage
- Semantic search with relevance scoring

