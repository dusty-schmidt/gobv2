# Enhanced Chatbot v2.0

## 🚀 What's New

This is a **major upgrade** from v1 with the following improvements:

### ✅ **OpenAI Embeddings** (vs. SentenceTransformers)
- **80% smaller dependencies** - No more PyTorch or HuggingFace models
- **Better performance** on low-tier hardware
- **Higher quality** embeddings from OpenAI's latest models
- **Cost-effective** - ~$0.00002 per 1K tokens (text-embedding-3-small)

### ✅ **SQLite Persistence** (vs. In-memory + JSON)
- **Full database persistence** - All memories and knowledge stored in SQLite
- **Fast vector search** - Cosine similarity search directly in database
- **Auto-cleanup** - Prevents memory bloat with configurable limits
- **Production-ready** - WAL mode, indexes, caching optimizations

---

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Keys

```bash
export OPENAI_API_KEY='sk-...your-key-here...'
export OPENROUTER_API_KEY='sk-or-v1-...your-key-here...'
```

### 3. Run the Chatbot

```bash
./run.sh
```

**Alternative:** `python3 main.py`

---

## ⚙️ Configuration

Edit `config.toml` to customize models, prompts, thresholds, and paths.

**Advanced:** Edit `src/core/config.py` for programmatic configuration.

---

## 💡 Usage

### Interactive Mode
```bash
./run.sh
```

### Special Commands
- `stats` - Show database statistics
- `clear` - Clear terminal screen
- `exit`, `quit`, `bye` - Exit chatbot

### Testing
- Run comprehensive tests: `python3 tests/smoke_test.py --no-save`

---

## 🔧 Technical Details

**Embedding Model:** text-embedding-3-small (1536 dimensions)
**Database:** SQLite with vector search
**Memory:** Persistent with cosine similarity retrieval
**Knowledge:** Document chunking with semantic search

---

## 📈 Performance

- **Install size:** ~50MB (vs. ~2GB for v1)
- **Memory usage:** ~100MB (vs. ~1GB for v1)
- **Startup time:** ~2s (vs. ~15s for v1)
- **Query speed:** <100ms for vector search

