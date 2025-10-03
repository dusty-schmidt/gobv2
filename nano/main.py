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
from core.brain.conversation_manager import UniversalConversationManager
from core.llm import LLMClient
from mini.src.core.embeddings_manager import EmbeddingsManager
from mini.src.core.config import ChatbotConfig



class NanoChatbot:
    """Ultra-simple chatbot using communal brain with universal conversation management"""

    def __init__(self):
        self.brain = None
        self.llm_client = None
        self.embeddings_mgr = None
        self.conversation_manager = None
        self.device_name = "Nano Chatbot"
        self.current_session_id = None

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

        # Initialize universal conversation manager
        self.conversation_manager = UniversalConversationManager(self.brain)

        # Initialize LLM client (using global config)
        llm_config = LLMConfig()
        self.llm_client = LLMClient(
            api_key=llm_config.api_key,
            model=llm_config.model,
            base_url=llm_config.base_url
        )

        # Start a new conversation session
        self.current_session_id = self.conversation_manager.start_conversation(self.device_name)

        # Show current brain stats
        stats = await self.brain.get_memory_stats()
        print(f"🧠 Connected to communal brain:")
        print(f"   📝 Memories: {stats['memory_count']}")
        print(f"   📚 Knowledge: {stats['knowledge_count']}")
        print(f"   🤖 Devices: {stats['device_count']}")
        print(f"🤖 LLM Model: {llm_config.model}")
        print(f"💬 Session ID: {self.current_session_id}")
        print("\n💬 Nano AI ready!")
        print("Commands: 'exit' to quit | 'stats' for brain info | 'clear' to reset conversation | 'history' to view chat log | 'sessions' to list all conversations\n")

    async def chat(self, user_message: str):
        """AI chat with communal memory context and universal conversation management"""
        # Get memory count before
        stats_before = await self.brain.get_memory_stats()
        memories_before = stats_before['memory_count']

        # Generate embedding for the user message
        import asyncio
        query_embedding = await asyncio.get_event_loop().run_in_executor(
            None, self.embeddings_mgr.encode, user_message
        )

        # Retrieve relevant memories from communal brain (long-term context)
        memories = await self.brain.retrieve_memories(query_embedding, top_k=3)

        # Get recent conversation history from universal manager
        conversation_history = self.conversation_manager.get_conversation_history(
            self.current_session_id, max_turns=8
        )

        # Create system prompt
        system_prompt = (
            "You are Nano, a helpful AI assistant with access to conversation history and past experiences. "
            "Keep responses concise and friendly. Use the provided context when relevant, "
            "but don't force it if it doesn't apply. Be conversational and maintain context from our ongoing discussion. "
            "Reference previous parts of our conversation when appropriate."
        )

        # Build LLM context manually (since we don't have the old ContextManager)
        context_parts = [f"=== SYSTEM PROMPT ===\n{system_prompt}\n"]

        # Add recent conversation context
        if conversation_history:
            context_parts.append("=== RECENT CONVERSATION HISTORY ===")
            for turn in conversation_history[:-1]:  # Exclude current user message if it's already in history
                role_display = "USER" if turn.user_message else "ASSISTANT"
                if turn.user_message:
                    context_parts.append(f"**USER**: {turn.user_message}")
                if turn.bot_response:
                    context_parts.append(f"**ASSISTANT**: {turn.bot_response}")
            context_parts.append("")

        # Add relevant long-term memories
        if memories:
            context_parts.append("=== RELEVANT LONG-TERM MEMORIES ===")
            for i, mem in enumerate(memories[:3], 1):
                context_parts.append(
                    f"**Memory {i}** (relevance: {mem.relevance_score:.2f}):"
                    f"\n  User asked: {mem.user_message}"
                    f"\n  Assistant replied: {mem.bot_response}"
                )
            context_parts.append("")

        # Add current user message
        context_parts.append(f"=== CURRENT USER MESSAGE ===\n{user_message}")

        full_context = "\n".join(context_parts)

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

        # Add the conversation turn to universal manager
        self.conversation_manager.add_turn(
            self.current_session_id,
            user_message,
            response,
            tokens_used=token_info.get('total_tokens', 0),
            metadata={"model": self.llm_client.model}
        )

        # Store the conversation in communal brain (use user message embedding for consistency)
        await self.brain.store_memory(user_message, response, query_embedding)

        # Get memory count after
        stats_after = await self.brain.get_memory_stats()
        memories_after = stats_after['memory_count']

        # Get conversation context info for stats
        conversation_summary = self.conversation_manager.get_conversation_summary(self.current_session_id)
        conversation_turns = conversation_summary.get('total_turns', 0)
        conversation_context_used = conversation_turns > 1  # True if we have conversation history

        # Save context snapshot for verification (legacy support)
        metadata = {
            "conversation_turns": conversation_turns,
            "memories_retrieved": len(memories),
            "session_id": self.current_session_id
        }

        # Save to legacy location for backward compatibility
        legacy_context_file = workspace_root / "core" / "last_context.txt"
        with open(legacy_context_file, 'w', encoding='utf-8') as f:
            f.write("=== LAST LLM CONTEXT ===\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
            f.write(full_context)
            f.write("\n\n=== DEBUG INFO ===\n")
            f.write(f"Conversation turns: {conversation_turns}\n")
            f.write(f"Memories retrieved: {len(memories)}\n")
            f.write(f"Session ID: {self.current_session_id}\n")

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
                    # End current conversation and start a new one
                    if self.current_session_id:
                        self.conversation_manager.end_conversation(self.current_session_id)
                    self.current_session_id = self.conversation_manager.start_conversation(self.device_name)
                    print(f"🧹 Conversation history cleared. New session: {self.current_session_id}")
                    continue

                if user_input.lower() == 'history':
                    history = self.conversation_manager.get_conversation_history(self.current_session_id)
                    if history:
                        print(f"\n📜 Conversation History (Session: {self.current_session_id}):")
                        for i, turn in enumerate(history, 1):
                            print(f"{i}. You: {turn.user_message}")
                            if turn.bot_response:
                                print(f"   Nano: {turn.bot_response}")
                        print()
                    else:
                        print("📜 No conversation history yet.\n")
                    continue

                if user_input.lower() == 'sessions':
                    conversations = self.conversation_manager.list_all_conversations(limit=10)
                    if conversations:
                        print("\n📋 Recent Conversations:")
                        for conv in conversations:
                            status = "Active" if conv.get('status') == 'active' else "Completed"
                            turns = conv.get('total_turns', 0)
                            print(f"  {conv['session_id']} - {conv['chatbot_name']} ({turns} turns, {status})")
                        print()
                    else:
                        print("📋 No conversations found.\n")
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
        if self.current_session_id:
            self.conversation_manager.end_conversation(self.current_session_id)
        if self.brain:
            await self.brain.close()

async def main():
    """Entry point"""
    chatbot = NanoChatbot()
    await chatbot.run()

if __name__ == "__main__":
    asyncio.run(main())