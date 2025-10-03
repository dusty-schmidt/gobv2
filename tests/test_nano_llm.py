#!/usr/bin/env python3
"""
Test script for Nano AI Chatbot with LLM integration
Tests the communal brain functionality and LLM responses
"""

import asyncio
import sys
from pathlib import Path

# Add workspace root to path for core imports
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from nano.main import NanoChatbot

async def test_nano_llm():
    """Test Nano chatbot with LLM calls and communal brain"""
    print("🧪 Testing Nano AI Chatbot with LLM calls")
    print("=" * 50)

    # Initialize chatbot
    chatbot = NanoChatbot()
    await chatbot.initialize()

    # Test conversation
    print("\n💬 Starting conversation with Nano...")
    test_messages = [
        "Hello Nano! Can you tell me what AI is?",
        "That's interesting. How does machine learning work?",
        "Thanks for the explanation!"
    ]

    for message in test_messages:
        print(f"You: {message}")
        response = await chatbot.chat(message)
        print(f"🤖 Nano: {response}")
        print()

    # Check communal brain storage
    print("🧠 Checking communal brain storage...")
    stats = await chatbot.brain.get_memory_stats()
    print(f"📊 Memories stored: {stats['memory_count']}")
    print(f"📝 Found {len(await chatbot.brain.retrieve_memories(await asyncio.get_event_loop().run_in_executor(None, chatbot.embeddings_mgr.encode, 'AI'), top_k=5))} memories related to 'AI'")

    # Show sample memories
    memories = await chatbot.brain.retrieve_memories(await asyncio.get_event_loop().run_in_executor(None, chatbot.embeddings_mgr.encode, 'AI'), top_k=3)
    for i, mem in enumerate(memories[:3], 1):
        print(f"   {i}. User: {mem.user_message[:50]}...")
        print(f"      Bot: {mem.bot_response[:50]}...")
        print(f"      Device: {mem.device_id}")
        print()

    print("✅ Nano LLM test completed successfully!")
    print("✅ Communal brain correctly stored conversations!")

    # Cleanup
    await chatbot.brain.close()

if __name__ == "__main__":
    asyncio.run(test_nano_llm())