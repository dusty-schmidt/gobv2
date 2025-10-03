# Homelab Intelligence Framework

A multi-tier chatbot framework that evolves from simple conversational AI to advanced Agent Zero-style autonomous agents, with shared intelligence across all your homelab devices.

## Project Structure

```
gob/                        # Workspace root
├── core/                  # 🧠 Shared intelligence framework
│   ├── brain/            # Communal brain implementation
│   ├── communal_brain.db # Live communal database
│   ├── config/           # Global configuration system
│   ├── llm/              # LLM client abstraction
│   └── logging.py        # Centralized logging
├── mini/                 # 🤖 Enhanced chatbot with communal brain (Tier 1)
│   ├── src/             # Chatbot implementation
│   ├── config.toml      # Configuration
│   ├── prompts/         # System prompts
│   ├── knowledge_docs/  # Knowledge base input
│   └── docs/            # Documentation
├── nano/                 # 🔬 Simple chatbot with communal brain (Tier 1)
│   └── main.py          # Simple chatbot implementation
├── tests/               # 🧪 Test suite
│   ├── test_memory_sharing.py    # Communal brain tests
│   ├── test_mini_chatbot.py      # Mini chatbot tests
│   ├── test_nano_llm.py          # Nano LLM tests
│   ├── test_nano_stats.py        # Nano stats display tests
│   └── test_run.py               # Entry point tests
├── docs/                 # 📖 Centralized documentation
│   ├── CENTRALBRAIN.md  # Communal brain architecture
│   ├── PROJECT_STATUS.md # Development status
│   └── QUICKSTART.md    # Getting started
└── run.py                # 🎯 CLI entry point for chatbots
```

## Core Concept: Communal Brain

**"One Brain, Many Bodies"** - All chatbots share the same intelligence pool, learning from each other while specializing based on their hardware capabilities.

### Key Features
- **Shared Memory**: Conversation memories accessible across all devices
- **Device Attribution**: Track which device contributed which knowledge
- **Hardware Awareness**: Automatic capability detection and task routing
- **Scalable Storage**: From local SQLite to distributed PostgreSQL
- **Conflict Resolution**: Intelligent merging of concurrent updates

## Development Tiers

### Tier 1: Foundation (Current - 100% Complete) ✅
**Status**: Communal brain fully operational with two working chatbots
- ✅ Communal brain architecture and API
- ✅ Storage abstraction layer (SQLite + extensible)
- ✅ Device management and auto-detection
- ✅ Mini chatbot integration with communal brain
- ✅ Nano chatbot integration with communal brain
- ✅ Cross-device memory and knowledge sharing
- ✅ Centralized database in gob/core/
- ✅ Global configuration and logging systems
- ✅ Memory usage statistics and transparency
- ✅ CLI entry point for chatbot selection
- ✅ Comprehensive test suite
- ⏳ Agent framework groundwork (extension hooks, streaming)

### Tier 2: Agent Capabilities (Planned)
- Multi-agent communication
- Prompt-driven behavior
- Tool framework
- Hierarchical relationships

### Tier 3: Advanced Agent Framework (Vision)
- Full Agent Zero features
- Real-time streaming UI
- MCP protocol support
- Distributed orchestration

## Quick Start

### Using the Communal Brain

```python
from core import CommunalBrain, BrainConfig

# Initialize shared intelligence
config = BrainConfig()
brain = CommunalBrain(config)
await brain.initialize()

# Store conversation memory
await brain.store_memory(
    "How do I sort a list in Python?",
    "Use sorted() or list.sort()",
    embedding=[0.1, 0.2, ...]
)

# Retrieve similar memories
memories = await brain.retrieve_memories(
    query_embedding=[0.1, 0.2, ...],
    top_k=3
)
```

### Running Mini Chatbot

```bash
cd mini
pip install -r requirements.txt
python main.py
```

## Device Examples

### Raspberry Pi Chatbot
- Handles simple queries locally
- Contributes to communal knowledge
- Benefits from powerful device learning

### Workstation Agent
- Tackles complex reasoning
- Shares insights with all devices
- Trains on collective knowledge

### Server Hub
- Maintains authoritative knowledge base
- Handles cross-device synchronization
- Provides backup and archival

## Dependencies

### Core Framework
```txt
aiosqlite>=0.19.0    # Async database operations
psutil>=5.9.0        # Hardware capability detection
```

### Mini Chatbot
```txt
openai>=1.12.0       # OpenAI API client
numpy>=1.24.0        # Vector operations
requests>=2.31.0     # HTTP client
python-dotenv>=1.0.0 # Environment variables
tomli>=2.0.0         # TOML configuration
```

## Development Status

### ✅ Completed (Tier 1: Foundation)
- Communal brain architecture and API
- Storage abstraction (SQLite + extensible backends)
- Device management and auto-detection
- Data models and vector search
- Mini chatbot integration with communal brain
- Nano chatbot integration with communal brain
- Cross-device memory sharing and statistics
- Centralized database in gob/core/
- Global configuration and logging systems
- Project reorganization and documentation
- CLI entry point (run.py) for chatbot selection
- Comprehensive test suite in tests/
- Memory usage transparency and stats display

### 🔄 Ready for Tier 2: Agent Capabilities
- Agent framework groundwork (extension hooks, streaming)
- Multi-agent communication protocols
- Prompt-driven behavior system
- Tool framework foundation

### 📋 Planned for Tier 3: Advanced Agent Framework
- Full Agent Zero features (hierarchical agents, instruments)
- Real-time streaming UI with intervention
- MCP protocol support for external tools
- Distributed agent orchestration
- Advanced synchronization and conflict resolution

## Documentation

- **[Communal Brain Architecture](./docs/CENTRALBRAIN.md)** - Technical deep-dive into the shared intelligence system
- **[Project Status](./docs/PROJECT_STATUS.md)** - Current development status and roadmap
- **[Quick Start](./docs/QUICKSTART.md)** - Getting started guide
- **[Core Framework](./core/README.md)** - API documentation for the shared components
- **[Mini Chatbot](./mini/README.md)** - Enhanced chatbot with vector memory and knowledge base
- **[Nano Chatbot](./nano/README.md)** - Simple chatbot for testing and lightweight devices
- **[Test Suite](./tests/)** - Automated tests for all components

## Philosophy

This framework embodies the principle that **intelligence should be collective, not isolated**. Just as human knowledge builds upon the discoveries of others, AI systems should share their learning experiences. The communal brain ensures that every device, regardless of its computational power, contributes to and benefits from the collective intelligence of your homelab.

## Contributing

1. **Fork Development**: Each tier can be developed independently
2. **Shared Core**: All implementations use the same communal brain
3. **Device Specialization**: Different hardware serves different purposes
4. **Collective Benefit**: Improvements to any component help all implementations

## License

This project is part of a personal homelab intelligence framework. See individual component licenses for details.

---

*"The whole is greater than the sum of its parts"* - Aristotle

This framework demonstrates that distributed AI systems can achieve more together than any single agent could alone.