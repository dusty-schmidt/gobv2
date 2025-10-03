#!/usr/bin/env python3
"""
Nano v1.0 - Simple Communal Brain Chatbot
A minimal chatbot that demonstrates communal intelligence sharing
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add workspace root to path for core imports
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

# Load environment variables from gob/.env
try:
    from dotenv import load_dotenv
    env_path = workspace_root / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"✅ Loaded environment from {env_path}")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

from core import CommunalBrain, BrainConfig, LLMConfig, EmbeddingsConfig
from core.llm import LLMClient
from mini.src.core.embeddings_manager import EmbeddingsManager
from mini.src.core.config import ChatbotConfig

class ConversationStorage:
    """Persistent storage for conversation logs across sessions"""

    def __init__(self, data_dir: Path, device_name: str = "nano"):
        self.data_dir = data_dir
        self.conversations_dir = data_dir / "conversations"
        self.contexts_dir = data_dir / "contexts"
        self.device_name = device_name
        self.current_session_id = None

        # Ensure directories exist
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        self.contexts_dir.mkdir(parents=True, exist_ok=True)

    def start_new_session(self):
        """Start a new conversation session"""
        import uuid
        self.current_session_id = f"{self.device_name}_{uuid.uuid4().hex[:8]}"
        return self.current_session_id

    def save_conversation_log(self, conversation_history: list):
        """Save complete conversation log to persistent storage"""
        if not self.current_session_id:
            self.start_new_session()

        filename = f"{self.current_session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.conversations_dir / filename

        conversation_data = {
            "session_id": self.current_session_id,
            "device": self.device_name,
            "timestamp": datetime.now().isoformat(),
            "messages": conversation_history
        }

        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)

        return filepath

    def load_recent_conversations(self, limit: int = 5):
        """Load recent conversation logs for context building"""
        if not self.conversations_dir.exists():
            return []

        # Get all conversation files, sorted by modification time (newest first)
        conversation_files = sorted(
            self.conversations_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        conversations = []
        for filepath in conversation_files[:limit]:
            try:
                import json
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    conversations.append(data)
            except Exception as e:
                print(f"Warning: Could not load conversation file {filepath}: {e}")

        return conversations

    def save_context_snapshot(self, context_content: str, metadata: dict = None):
        """Save current context snapshot"""
        if not self.current_session_id:
            self.start_new_session()

        filename = f"context_{self.current_session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self.contexts_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=== CONTEXT SNAPSHOT ===\n")
            f.write(f"Session: {self.current_session_id}\n")
            f.write(f"Device: {self.device_name}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            if metadata:
                f.write(f"Metadata: {metadata}\n")
            f.write("\n")
            f.write(context_content)

        return filepath


class ContextManager:
    """Dedicated context manager for Nano chatbot with debug capabilities and persistent storage"""

    def __init__(self, max_history=20, data_dir: Path = None, device_name: str = "nano"):
        self.conversation_history = []
        self.max_history = max_history
        self.debug_mode = False

        # Initialize persistent storage
        if data_dir is None:
            workspace_root = Path(__file__).parent.parent
            data_dir = workspace_root / "core" / "data"

        self.storage = ConversationStorage(data_dir, device_name)
        self.storage.start_new_session()

        # Load recent conversation context from persistent storage
        self._load_persistent_context()

    def _load_persistent_context(self):
        """Load recent conversation context from persistent storage"""
        try:
            recent_conversations = self.storage.load_recent_conversations(limit=3)

            # Extract messages from recent conversations and add to current history
            loaded_messages = []
            for conv in recent_conversations:
                if 'messages' in conv:
                    # Add messages but mark them as from previous sessions
                    for msg in conv['messages'][-5:]:  # Limit messages per conversation
                        loaded_messages.append({
                            "role": msg["role"],
                            "content": f"[Previous Session] {msg['content']}",
                            "from_session": conv.get('session_id', 'unknown')
                        })

            # Add loaded messages to current history (but don't exceed max_history)
            for msg in loaded_messages[-10:]:  # Limit total loaded messages
                if len(self.conversation_history) < self.max_history:
                    self.conversation_history.append(msg)

        except Exception as e:
            print(f"Warning: Could not load persistent context: {e}")
            # Continue without persistent context

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        message = {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        self.conversation_history.append(message)

        # Keep only recent messages
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

        # Save conversation log periodically (every 3 messages)
        if len(self.conversation_history) % 3 == 0:
            try:
                self.storage.save_conversation_log(self.conversation_history)
            except Exception as e:
                print(f"Warning: Could not save conversation log: {e}")

    def get_recent_context(self, max_messages=8):
        """Get recent conversation context for LLM"""
        return self.conversation_history[-max_messages:] if len(self.conversation_history) > max_messages else self.conversation_history

    def get_full_history(self):
        """Get complete conversation history"""
        return self.conversation_history.copy()

    def clear(self):
        """Clear conversation history"""
        self.conversation_history = []

    def build_llm_context(self, user_message: str, memories: list, system_prompt: str):
        """Build complete context for LLM including system prompt, conversation, and memories"""

        context_parts = []

        # Add system prompt
        context_parts.append(f"=== SYSTEM PROMPT ===\n{system_prompt}\n")

        # Add recent conversation context (including persistent history)
        recent_context = self.get_recent_context(max_messages=8)  # Get more context
        if recent_context:
            context_parts.append("=== RECENT CONVERSATION HISTORY ===")
            for msg in recent_context[:-1]:  # Exclude current user message
                role_display = "USER" if msg["role"] == "user" else "ASSISTANT"
                content = msg['content']

                # Handle persistent context markers
                if content.startswith("[Previous Session]"):
                    content = content.replace("[Previous Session] ", "")
                    role_display = f"{role_display} (previous session)"

                context_parts.append(f"**{role_display}**: {content}")
            context_parts.append("")  # Add spacing

        # Add relevant long-term memories
        if memories:
            context_parts.append("=== RELEVANT LONG-TERM MEMORIES ===")
            for i, mem in enumerate(memories[:3], 1):  # Limit to 3 for conciseness
                context_parts.append(
                    f"**Memory {i}** (relevance: {mem.relevance_score:.2f}):"
                    f"\n  User asked: {mem.user_message}"
                    f"\n  Assistant replied: {mem.bot_response}"
                )
            context_parts.append("")  # Add spacing

        # Add current user message
        context_parts.append(f"=== CURRENT USER MESSAGE ===\n{user_message}")

        # Combine all context
        full_context = "\n".join(context_parts)

        if self.debug_mode:
            print("\n" + "="*80)
            print("🔍 DEBUG: FULL CONTEXT BEING SENT TO LLM")
            print("="*80)
            print(full_context)
            print("="*80 + "\n")

        return full_context

    def toggle_debug(self):
        """Toggle debug mode for context inspection"""
        self.debug_mode = not self.debug_mode
        return self.debug_mode


# Backward compatibility alias
ConversationContext = ContextManager


class NanoChatbot:
    """Ultra-simple chatbot using communal brain with conversation context"""

    def __init__(self):
        self.brain = None
        self.llm_client = None
        self.embeddings_mgr = None
        self.device_name = "Nano Chatbot"
        self.conversation = ConversationContext(max_history=20)  # Keep more history for context

    async def initialize(self):
        """Initialize communal brain and LLM client"""
        print("🤖 Initializing Nano AI Chatbot...")

        # Initialize communal brain
        config = BrainConfig()
        communal_db_path = workspace_root / "core" / "communal_brain.db"
        config.storage.local_db_path = str(communal_db_path)
        config.device_name = self.device_name
        config.device_location = "local"

        self.brain = CommunalBrain(config)
        await self.brain.initialize()

        # Initialize embeddings manager (shared with mini)
        mini_config = ChatbotConfig()
        self.embeddings_mgr = EmbeddingsManager(
            api_key=mini_config.embeddings.api_key,
            model_name=mini_config.embeddings.model_name,
            embedding_dim=mini_config.embeddings.embedding_dim
        )

        # Initialize LLM client (using global config)
        llm_config = LLMConfig()
        self.llm_client = LLMClient(
            api_key=llm_config.api_key,
            model=llm_config.model,
            base_url=llm_config.base_url
        )

        # Show current brain stats
        stats = await self.brain.get_memory_stats()
        print(f"🧠 Connected to communal brain:")
        print(f"   📝 Memories: {stats['memory_count']}")
        print(f"   📚 Knowledge: {stats['knowledge_count']}")
        print(f"   🤖 Devices: {stats['device_count']}")
        print(f"🤖 LLM Model: {llm_config.model}")
        print("\n💬 Nano AI ready!")
        print("Commands: 'exit' to quit | 'stats' for brain info | 'clear' to reset conversation | 'history' to view chat log | 'debug' to toggle LLM prompt inspection\n")

    async def chat(self, user_message: str):
        """AI chat with communal memory context and conversation history"""
        # Get memory count before
        stats_before = await self.brain.get_memory_stats()
        memories_before = stats_before['memory_count']

        # Add user message to conversation history
        self.conversation.add_message("user", user_message)

        # Generate embedding for the user message
        import asyncio
        query_embedding = await asyncio.get_event_loop().run_in_executor(
            None, self.embeddings_mgr.encode, user_message
        )

        # Retrieve relevant memories from communal brain (long-term context)
        memories = await self.brain.retrieve_memories(query_embedding, top_k=3)

        # Create system prompt
        system_prompt = (
            "You are Nano, a helpful AI assistant with access to conversation history and past experiences. "
            "Keep responses concise and friendly. Use the provided context when relevant, "
            "but don't force it if it doesn't apply. Be conversational and maintain context from our ongoing discussion. "
            "Reference previous parts of our conversation when appropriate."
        )

        # Build complete LLM context using ContextManager
        full_context = self.conversation.build_llm_context(user_message, memories, system_prompt)

        # For LLM API, we need to send as separate messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_context}  # Include all context in user message for simplicity
        ]

        # Generate AI response
        try:
            response, token_info = self.llm_client.generate_response(
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                stream=False
            )
        except Exception as e:
            # Fallback if LLM fails
            response = f"I understand you said: '{user_message}'. (LLM temporarily unavailable)"
            token_info = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}

        # Add AI response to conversation history
        self.conversation.add_message("assistant", response)

        # Store the conversation in communal brain (use user message embedding for consistency)
        await self.brain.store_memory(user_message, response, query_embedding)

        # Get memory count after
        stats_after = await self.brain.get_memory_stats()
        memories_after = stats_after['memory_count']

        # Get conversation context info for stats
        conversation_turns = len(self.conversation.conversation_history)
        conversation_context_used = conversation_turns > 1  # True if we have conversation history

        # Save context snapshot for verification
        metadata = {
            "conversation_turns": conversation_turns,
            "memories_retrieved": len(memories),
            "debug_mode": self.conversation.debug_mode,
            "session_id": self.conversation.storage.current_session_id
        }
        context_file = self.conversation.storage.save_context_snapshot(full_context, metadata)

        # Also save to the old location for backward compatibility
        legacy_context_file = workspace_root / "core" / "last_context.txt"
        with open(legacy_context_file, 'w', encoding='utf-8') as f:
            f.write("=== LAST LLM CONTEXT ===\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
            f.write(full_context)
            f.write("\n\n=== DEBUG INFO ===\n")
            f.write(f"Conversation turns: {conversation_turns}\n")
            f.write(f"Memories retrieved: {len(memories)}\n")
            f.write(f"Debug mode: {self.conversation.debug_mode}\n")
            f.write(f"Session ID: {self.conversation.storage.current_session_id}\n")
            f.write(f"Context file: {context_file}\n")

        # Build statistics
        stats = {
            'memories_retrieved': len(memories),
            'conversation_context_used': conversation_context_used,
            'knowledge_retrieved': 0,  # Nano doesn't use knowledge base yet
            'memories_saved': memories_after - memories_before,
            'total_memories': memories_after,
            'retrieved_memory_scores': [m.relevance_score for m in memories],
            'conversation_turns': conversation_turns,
            'input_tokens': token_info.get('input_tokens', 0),
            'output_tokens': token_info.get('output_tokens', 0),
            'total_tokens': token_info.get('total_tokens', 0),
            'model': self.llm_client.model
        }

        return response, stats

    def _display_exchange_stats(self, stats):
        """Display memory statistics for the current exchange"""
        # Build stats line
        parts = []

        # Conversation context used
        if stats.get('conversation_context_used', False):
            parts.append(f"💬 Conversation context active ({stats.get('conversation_turns', 0)} turns)")
        else:
            parts.append("💬 New conversation started")

        # Memories used
        if stats['memories_retrieved'] > 0:
            avg_score = sum(stats['retrieved_memory_scores']) / len(stats['retrieved_memory_scores'])
            parts.append(f"📝 {stats['memories_retrieved']} memories used (avg similarity: {avg_score:.2f})")
        else:
            parts.append("📝 No memories used")

        # Knowledge used (Nano doesn't use knowledge yet)
        parts.append("📚 No knowledge used")

        # Memories saved
        if stats['memories_saved'] > 0:
            parts.append(f"💾 {stats['memories_saved']} new memory saved")

        # Total memories
        parts.append(f"Total: {stats['total_memories']} memories")

        # Model used
        if 'model' in stats:
            # Extract just the model name for display (remove provider prefix if present)
            model_name = stats['model'].split('/')[-1] if '/' in stats['model'] else stats['model']
            parts.append(f"🤖 Model: {model_name}")

        # Token usage
        if stats.get('total_tokens', 0) > 0:
            parts.append(f"🎫 Tokens: {stats['input_tokens']}in + {stats['output_tokens']}out = {stats['total_tokens']} total")

        # Display with color (simple version without ANSI codes for Nano)
        stats_line = " | ".join(parts)
        print("─" * 80)
        print(stats_line)
        print("─" * 80)

    async def show_stats(self):
        """Show communal brain statistics"""
        stats = await self.brain.get_memory_stats()
        print("\n📊 Communal Brain Stats:")
        print(f"   Total memories: {stats['memory_count']}")
        print(f"   Knowledge chunks: {stats['knowledge_count']}")
        print(f"   Connected devices: {stats['device_count']}")
        print()

    async def run(self):
        """Main chat loop"""
        await self.initialize()

        print("🎯 Nano Chatbot - Testing Communal Intelligence")
        print("=" * 50)

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Nano signing off!")
                    break

                if user_input.lower() == 'stats':
                    await self.show_stats()
                    continue

                if user_input.lower() == 'clear':
                    self.conversation.clear()
                    print("🧹 Conversation history cleared. Starting fresh!")
                    continue

                if user_input.lower() == 'history':
                    history = self.conversation.get_full_history()
                    if history:
                        print("\n📜 Conversation History:")
                        for i, msg in enumerate(history, 1):
                            role = "You" if msg["role"] == "user" else "Nano"
                            print(f"{i}. {role}: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
                        print()
                    else:
                        print("📜 No conversation history yet.\n")
                    continue

                if user_input.lower() == 'debug':
                    debug_state = self.conversation.toggle_debug()
                    status = "ENABLED" if debug_state else "DISABLED"
                    print(f"🔍 Debug mode {status}. Full LLM prompts will be displayed.\n")
                    continue

                # Generate response
                response, stats = await self.chat(user_input)

                print(f"🤖 Nano: {response}")

                # Display memory statistics
                print()
                self._display_exchange_stats(stats)
                print()

            except KeyboardInterrupt:
                print("\n👋 Nano interrupted!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        # Cleanup
        if self.brain:
            await self.brain.close()

async def main():
    """Entry point"""
    chatbot = NanoChatbot()
    await chatbot.run()

if __name__ == "__main__":
    asyncio.run(main())