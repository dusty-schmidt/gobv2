#!/usr/bin/env python3
"""
Test script to verify Nano memory stats display
"""

import asyncio
import sys
from pathlib import Path

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from nano.main import NanoChatbot

async def test_nano_stats():
    """Test Nano with memory stats display"""
    print("🧪 Testing Nano Memory Stats Display")
    print("=" * 50)

    # Initialize Nano
    nano = NanoChatbot()
    await nano.initialize()

    # Test a conversation
    print("💬 Testing conversation with memory stats...")

    test_message = "Hello Nano! Tell me about AI."
    print(f"You: {test_message}")

    response, stats = await nano.chat(test_message)
    print(f"🤖 Nano: {response}")

    # Display stats
    print()
    nano._display_exchange_stats(stats)
    print()

    # Test memory retrieval
    print("💬 Testing memory retrieval...")
    follow_up = "What did I just ask you about?"
    print(f"You: {follow_up}")

    response2, stats2 = await nano.chat(follow_up)
    print(f"🤖 Nano: {response2}")

    print()
    nano._display_exchange_stats(stats2)
    print()

    print("✅ Nano memory stats display working!")
    print(f"📊 Memories in brain: {stats2['total_memories']}")

    await nano.brain.close()

if __name__ == "__main__":
    asyncio.run(test_nano_stats())