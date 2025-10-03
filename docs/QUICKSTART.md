# Quick Start Guide

## ⚡ Get Started in 3 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set API Keys
```bash
# Get your keys:
# - OpenAI: https://platform.openai.com/api-keys
# - OpenRouter: https://openrouter.ai/keys

export OPENAI_API_KEY='sk-...'
export OPENROUTER_API_KEY='sk-or-v1-...'
```

### Step 3: Configure (Optional)
Edit `config.toml` to customize models, prompts, and settings.

### Step 4: Run the Chatbot!
```bash
./run.sh
```

**Alternative:** `python3 main.py`

---

## 🎯 What to Try

### Ask about the knowledge base:
- "What is Python?"
- "Tell me about machine learning"
- "What are the types of ML?"

### Test memory:
- "My name is John"
- (later) "What's my name?"

### Test universal conversations:
- Start with Nano: "Let's talk about Python programming"
- Switch to Mini and continue: "Tell me more about classes"
- Both chatbots share the same conversation history!

### Special commands:
- Type `stats` to see database statistics
- Type `clear` to reset conversation (start new session)
- Type `sessions` to list all conversation sessions (Mini only)
- Type `history` to view current conversation history
- Type `exit` to quit

---

## 📊 Add Your Own Knowledge

```bash
# Add .txt files to knowledge_docs/
echo "Your knowledge here..." > knowledge_docs/my_topic.txt

# Delete database to reload knowledge
rm chatbot.db*

# Run chatbot (will reload all knowledge)
./run.sh
```

---

## 🔧 Customize Settings

Edit `src/core/config.py`:

```python
# Use better embeddings (costs more)
model_name = "text-embedding-3-large"  # 3072 dimensions

# Use different LLM
model = "anthropic/claude-3.5-sonnet"  # or any OpenRouter model

# Retrieve more memories
top_k = 5

# Lower threshold for more results
similarity_threshold = 0.2
```

---

## 🧪 Testing

```bash
# Run comprehensive smoke test
python3 tests/smoke_test.py --no-save

# Debug prompts being sent to model
python3 debug_prompt.py

# Enable debug logging to see prompts in chat
LOG_LEVEL=DEBUG ./run.sh
```

---

## 💡 Tips

- The communal brain database `core/communal_brain.db` stores all memories, knowledge, and conversations
- Conversations are now universal - start with one chatbot, continue with another using session IDs
- Backup the communal brain database to preserve all your collective intelligence
- Use `./run.sh` for easy execution from any directory
- Both Nano and Mini share the same brain, so learning on one benefits both

