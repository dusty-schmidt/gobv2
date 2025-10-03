#!/usr/bin/env python3
"""
Test script to verify Nano conversation context management
"""

import asyncio
import sys
from pathlib import Path

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from nano.main import NanoChatbot

async def test_nano_context():
    """Test Nano conversation context across multiple turns"""
    print("🧪 Testing Nano Conversation Context")
    print("=" * 50)

    # Initialize Nano
    nano = NanoChatbot()
    await nano.initialize()

    # Test conversation flow
    print("💬 Testing multi-turn conversation...")

    # Turn 1: Introduce myself
    msg1 = "Hi Nano! My name is Alex and I love programming."
    print(f"You: {msg1}")
    response1, stats1 = await nano.chat(msg1)
    print(f"🤖 Nano: {response1}")
    print()
    nano._display_exchange_stats(stats1)
    print()

    # Turn 2: Ask about my interests
    msg2 = "What do you think about programming?"
    print(f"You: {msg2}")
    response2, stats2 = await nano.chat(msg2)
    print(f"🤖 Nano: {response2}")
    print()
    nano._display_exchange_stats(stats2)
    print()

    # Turn 3: Reference previous context
    msg3 = "Do you remember my name?"
    print(f"You: {msg3}")
    response3, stats3 = await nano.chat(msg3)
    print(f"🤖 Nano: {response3}")
    print()
    nano._display_exchange_stats(stats3)
    print()

    # Check conversation history
    print("📜 Conversation History:")
    history = nano.conversation.get_full_history()
    for i, msg in enumerate(history, 1):
        role = "You" if msg["role"] == "user" else "Nano"
        print(f"{i}. {role}: {msg['content']}")
    print()

    # Verify context is working
    context_used = stats3.get('conversation_context_used', False)
    turns = stats3.get('conversation_turns', 0)

    print("✅ Context Test Results:")
    print(f"   Conversation context used: {context_used}")
    print(f"   Total conversation turns: {turns}")
    print(f"   History length: {len(history)}")

    if context_used and turns >= 6:  # 3 user + 3 assistant messages
        print("✅ SUCCESS: Nano maintains conversation context!")
    else:
        print("❌ FAILED: Context management not working properly")

    await nano.brain.close()

if __name__ == "__main__":
    asyncio.run(test_nano_context())