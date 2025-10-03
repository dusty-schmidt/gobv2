#!/usr/bin/env python3
"""
Nano v1.0 - Simple Communal Brain Chatbot
A minimal chatbot that demonstrates communal intelligence sharing
"""

import asyncio
import sys
from pathlib import Path

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

class NanoChatbot:
    """Ultra-simple chatbot using communal brain"""

    def __init__(self):
        self.brain = None
        self.llm_client = None
        self.embeddings_mgr = None
        self.device_name = "Nano Chatbot"

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
        print("\n💬 Nano AI ready! Type 'exit' to quit, 'stats' for info.\n")

    async def chat(self, user_message: str):
        """AI chat with communal memory context"""
        # Get memory count before
        stats_before = await self.brain.get_memory_stats()
        memories_before = stats_before['memory_count']

        # Generate embedding for the user message
        import asyncio
        query_embedding = await asyncio.get_event_loop().run_in_executor(
            None, self.embeddings_mgr.encode, user_message
        )

        # Retrieve relevant memories from communal brain
        memories = await self.brain.retrieve_memories(query_embedding, top_k=3)

        # Build context from memories
        context_parts = []
        if memories:
            context_parts.append("=== RELEVANT PAST CONVERSATIONS ===")
            for i, mem in enumerate(memories[:2], 1):  # Limit to 2 for conciseness
                context_parts.append(
                    f"\nConversation {i} (relevance: {mem.relevance_score:.2f}):"
                    f"\nUser: {mem.user_message}"
                    f"\nAssistant: {mem.bot_response}"
                )

        # Create simple prompt for LLM
        system_prompt = (
            "You are Nano, a helpful AI assistant with access to conversation history. "
            "Keep responses concise and friendly. Use the provided context when relevant, "
            "but don't force it if it doesn't apply. Be conversational and helpful."
        )

        context_text = "\n".join(context_parts) if context_parts else "No relevant past conversations."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"Context from communal brain:\n{context_text}"},
            {"role": "user", "content": user_message}
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

        # Store the conversation in communal brain (use user message embedding for consistency)
        await self.brain.store_memory(user_message, response, query_embedding)

        # Get memory count after
        stats_after = await self.brain.get_memory_stats()
        memories_after = stats_after['memory_count']

        # Build statistics
        stats = {
            'memories_retrieved': len(memories),
            'knowledge_retrieved': 0,  # Nano doesn't use knowledge base yet
            'memories_saved': memories_after - memories_before,
            'total_memories': memories_after,
            'retrieved_memory_scores': [m.relevance_score for m in memories],
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
        print("─" * 60)
        print(stats_line)
        print("─" * 60)

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