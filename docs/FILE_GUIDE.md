# File Guide - Chatbot v2

## 🏗️ Project Structure
# File Guide - Chatbot v2

## 🏗️ Project Structure

```
chatbot_v2.2/
├── src/                    # Core application code
│   ├── core/              # Main chatbot components
│   ├── memory/            # Memory management system
│   ├── knowledge/         # Knowledge base & embeddings
│   └── utils/             # Shared utilities
├── tests/                 # Testing utilities
├── docs/                  # Documentation
├── knowledge_docs/        # Knowledge base documents
├── prompts/               # System prompts
├── main.py                # Entry point
├── run.sh                 # Simple bash runner
└── [config files...]
```

## 📋 Core Application (`src/`)

### `src/core/` - Main Chatbot Components

#### `main.py` (7.3K)
**Role:** Main entry point and orchestration
- Initializes all components
- Manages interactive chat loop
- Handles database lifecycle
- Shows statistics and status
- **Imported by root main.py**

#### `config.py` (2.7K)
**Role:** Configuration management
- OpenAI embeddings settings
- LLM model configuration
- Database paths and settings
- Memory and knowledge retrieval parameters
- **Edit this to customize behavior**

#### `chat_handler.py` (2.6K)
**Role:** Response generation orchestration
- Retrieves relevant memories
- Searches knowledge base
- Builds context for LLM
- Generates responses
- Saves new conversations
- **Ties everything together**

#### `llm_client.py` (6.8K)
**Role:** LLM API interface
- Connects to OpenRouter
- Formats prompts
- Handles API calls
- Error handling and retries
- **Unchanged from v1**

### `src/memory/` - Memory Management System

#### `database.py` (12K)
**Role:** SQLite persistence layer
- Creates and manages database schema
- Vector search for memories and knowledge
- CRUD operations for all data
- Performance optimizations (WAL, indexes)
- **Core of the persistence system**

#### `memory_store.py` (5.8K)
**Role:** Conversation memory management
- Stores chat history in database
- Retrieves relevant past conversations
- Semantic search via embeddings
- Memory cleanup utilities
- **Your chatbot's memory system**

### `src/knowledge/` - Knowledge Base System

#### `embeddings_manager.py` (5.5K)
**Role:** OpenAI embeddings interface
- Converts text to vectors via OpenAI API
- Batch processing for efficiency
- Cosine similarity calculations
- Retry logic with exponential backoff
  - **Standardized on OpenAI embeddings**

#### `knowledge_base.py` (5.7K)
**Role:** Document knowledge management
- Loads .txt files from knowledge_docs/
- Chunks documents intelligently
- Stores chunks in database
- Semantic search for relevant info
- **Your chatbot's knowledge system**

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

### `chatbot.db`
**Role:** SQLite database
- Stores all memories
- Stores all knowledge chunks
- Stores embeddings as binary
- **Created automatically on first run**

### `chatbot.db-wal` and `chatbot.db-shm`
**Role:** SQLite Write-Ahead Log files
- Temporary files for WAL mode
- Better concurrency and crash resistance
- **Created automatically by SQLite**

### `chatbot.log`
**Role:** Application log file
- All logging output in reverse chronological order
- Auto-deletes logs older than 7 days
- Keeps most recent 1000 entries
- Newest logs appear at top of file
- **Check here for debugging info**

---

## 📊 Architecture Benefits

**Modular Design:**
- Clear separation of concerns
- Easy to extend and maintain
- Stable import paths via `__init__.py`

**Testing:**
- Comprehensive smoke tests
- Isolated testing environment
- No external API dependencies for basic tests

**Developer Experience:**
- `./run.sh` for easy execution
- Clear documentation structure
- Minimal dependencies (3 packages)

**Performance:**
- SQLite with WAL mode for speed
- Efficient vector operations
- Optimized memory usage

