# Nano v1.0 - Simple AI Communal Brain Chatbot

A minimal AI chatbot that uses communal intelligence with LLM-generated responses, demonstrating collective learning across multiple chatbots.

## Features

- 🤖 **Ultra-Simple Interface**: Basic echo chatbot with memory awareness
- 🧠 **Communal Brain**: Shares intelligence with other chatbots (like Mini v3.0)
- 📝 **Memory Persistence**: Conversations persist across sessions and chatbots
- 📊 **Statistics**: View communal brain statistics with `stats` command

## Usage

### Via CLI Launcher
```bash
cd /path/to/gob
python3 run.py
# Select option 2 (Nano v1.0)
```

### Direct Run
```bash
cd nano-v1.0
python3 main.py
```

## Commands

- `stats` - Show communal brain statistics
- `exit`, `quit`, `bye` - Exit the chatbot

## Communal Testing

1. Start Nano chatbot and have a conversation
2. Exit Nano and start Mini v3.0 chatbot
3. Ask Mini about the previous conversation
4. Both chatbots share the same memory!

## Architecture

Nano uses the same `gob/core/communal_brain.db` database as all other chatbots, demonstrating true communal intelligence where:

- **Memory Sharing**: All conversations are stored in shared pool
- **Cross-Chatbot Recall**: Any chatbot can access memories from any other
- **Device Attribution**: Each memory tracks which chatbot/device created it
- **Unified Intelligence**: Collective learning across all implementations

## Comparison to Mini v3.0

| Feature | Nano v1.0 | Mini v3.0 |
|---------|-----------|-----------|
| Complexity | Simple AI | Full-featured |
| AI Responses | LLM-powered with context | OpenAI-powered with RAG |
| Memory | Communal access | Communal with embeddings |
| Knowledge Base | Basic access | Full semantic search |
| Interface | Text-only | Rich statistics |
| Use Case | Lightweight AI chat | Production chatbot |

Both use the same communal brain infrastructure, proving the shared intelligence concept works!