#!/usr/bin/env python3
"""
Test script to verify memory sharing between Mini and Nano chatbots
"""

import asyncio
import sys
from pathlib import Path

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from core import CommunalBrain, BrainConfig
from mini.src.core.embeddings_manager import EmbeddingsManager
from mini.src.core.config import ChatbotConfig

async def test_memory_sharing():
    """Test that memories are shared between different chatbot instances"""
    print("🧠 Testing Communal Memory Sharing")
    print("=" * 50)

    # Initialize communal brain
    config = BrainConfig()
    communal_db_path = workspace_root / "core" / "communal_brain.db"
    config.storage.local_db_path = str(communal_db_path)
    config.device_name = "Test Script"
    config.device_location = "local"

    brain = CommunalBrain(config)
    await brain.initialize()

    # Initialize embeddings
    mini_config = ChatbotConfig()
    embeddings_mgr = EmbeddingsManager(
        api_key=mini_config.embeddings.api_key,
        model_name=mini_config.embeddings.model_name,
        embedding_dim=mini_config.embeddings.embedding_dim
    )

    # Check current memory count
    stats = await brain.get_memory_stats()
    print(f"📊 Current memories: {stats['memory_count']}")

    # Simulate Mini chatbot storing a memory
    print("\n🤖 Simulating Mini chatbot storing memory...")
    mini_user_msg = "tell me a short story about a clockmaker"
    mini_response = "Once upon a time, there was a clockmaker named Elena who fixed time itself..."

    mini_embedding = await asyncio.get_event_loop().run_in_executor(
        None, embeddings_mgr.encode, mini_user_msg
    )
    await brain.store_memory(mini_user_msg, mini_response, mini_embedding, context="Mini Chatbot")
    print("✅ Mini stored memory")

    # Simulate Nano chatbot retrieving the memory
    print("\n🤖 Simulating Nano chatbot retrieving memory...")
    nano_query = "what was that story about the clockmaker"
    nano_embedding = await asyncio.get_event_loop().run_in_executor(
        None, embeddings_mgr.encode, nano_query
    )

    memories = await brain.retrieve_memories(nano_embedding, top_k=3)
    print(f"📝 Nano found {len(memories)} relevant memories")

    if memories:
        print("✅ Memory sharing works! Nano can access Mini's memories")
        for i, mem in enumerate(memories, 1):
            print(f"   {i}. User: {mem.user_message[:50]}...")
            print(f"      Bot: {mem.bot_response[:50]}...")
            print(f"      Device: {mem.device_id}")
    else:
        print("❌ Memory sharing failed! Nano cannot access Mini's memories")

    # Check final stats
    final_stats = await brain.get_memory_stats()
    print(f"\n📊 Final memories: {final_stats['memory_count']}")

    await brain.close()

    return len(memories) > 0

if __name__ == "__main__":
    success = asyncio.run(test_memory_sharing())
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Memory sharing test")
    sys.exit(0 if success else 1)