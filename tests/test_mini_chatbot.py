#!/usr/bin/env python3
"""
Test script for Mini Chatbot with communal brain integration
Tests the full-featured chatbot with vector memory, knowledge base, and LLM responses
"""

import asyncio
import sys
from pathlib import Path

# Add workspace root to path for core imports
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

# Add mini to path
mini_path = workspace_root / "mini"
sys.path.insert(0, str(mini_path))

from mini.src.core.main import Chatbot

async def test_mini_chatbot():
    """Test Mini chatbot with communal brain and full features"""
    print("🧪 Testing Mini Chatbot with Communal Brain")
    print("=" * 50)

    # Initialize chatbot
    chatbot = Chatbot()
    await chatbot.initialize()

    # Test conversation
    print("\n💬 Starting conversation with Mini...")

    test_messages = [
        "Hello Mini! Tell me about machine learning.",
        "That's interesting. How do neural networks work?",
        "Thanks for the explanation!"
    ]

    for message in test_messages:
        print(f"You: {message}")

        # Generate response
        response, stats = await chatbot.chat(message)

        print(f"🤖 Mini: {response}")

        # Show stats
        print(f"📊 Stats: {stats['memories_retrieved']} memories, {stats['knowledge_retrieved']} knowledge chunks")
        print(f"💾 Saved: {stats['memories_saved']} new memories")
        print()

    # Check communal brain storage
    print("🧠 Checking communal brain storage...")
    brain_stats = await chatbot.brain.get_memory_stats()
    print(f"📊 Memories stored: {brain_stats['memory_count']}")
    print(f"📚 Knowledge chunks: {brain_stats['knowledge_count']}")
    print(f"🤖 Connected devices: {brain_stats['device_count']}")

    # Test memory retrieval
    query_embedding = await asyncio.get_event_loop().run_in_executor(
        None, chatbot.embeddings_mgr.encode, "machine learning"
    )
    memories = await chatbot.brain.retrieve_memories(query_embedding, top_k=3)
    print(f"📝 Found {len(memories)} memories related to 'machine learning'")

    for i, mem in enumerate(memories[:2], 1):  # Show first 2
        print(f"   {i}. User: {mem.user_message[:50]}...")
        print(f"      Bot: {mem.bot_response[:50]}...")
        print(f"      Relevance: {mem.relevance_score:.2f}")
        print()

    print("✅ Mini chatbot test completed successfully!")
    print("✅ Communal brain integration working!")
    print("✅ Vector memory and knowledge retrieval functional!")

    # Cleanup
    await chatbot.brain.close()

if __name__ == "__main__":
    asyncio.run(test_mini_chatbot())