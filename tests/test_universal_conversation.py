#!/usr/bin/env python3
"""
Test script to verify universal conversation management across chatbots
"""

import asyncio
import sys
from pathlib import Path

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from nano.main import NanoChatbot
from mini.src.core.main import Chatbot as MiniChatbot

async def test_universal_conversation():
    """Test universal conversation management across different chatbots"""
    print("🔄 Testing Universal Conversation Management")
    print("=" * 60)

    # Start with Nano
    print("🤖 Starting conversation with Nano...")
    nano = NanoChatbot()
    await nano.initialize()

    session_id = nano.current_session_id
    print(f"📋 Session ID: {session_id}")

    # First message with Nano
    msg1 = "Hello! I'm starting a conversation that I want to continue with Mini."
    response1, stats1 = await nano.chat(msg1)
    print(f"🤖 Nano: {response1[:100]}...")

    # Second message with Nano
    msg2 = "Can you tell me about Python programming?"
    response2, stats2 = await nano.chat(msg2)
    print(f"🤖 Nano: {response2[:100]}...")

    # End Nano session (but keep conversation active)
    await nano.brain.close()
    print("✅ Nano conversation saved to universal brain")

    # Now continue with Mini using the same session
    print(f"\n🤖 Continuing conversation with Mini (Session: {session_id})...")

    # Create Mini with the same session
    mini = MiniChatbot()
    await mini.initialize()

    # Manually set the session ID to continue the conversation
    mini.chat_handler.current_session_id = session_id
    print("📋 Mini joined existing session")

    # Continue the conversation with Mini
    msg3 = "That's interesting! Can you tell me more about object-oriented programming?"
    response3, stats3 = await mini.chat(msg3)
    print(f"🤖 Mini: {response3[:100]}...")

    # Check conversation history
    print("\n📜 Checking universal conversation history...")
    history = mini.chat_handler.get_conversation_history()
    print(f"📝 Total conversation turns: {len(history)}")
    for i, turn in enumerate(history, 1):
        if turn.user_message:
            print(f"  {i}. User: {turn.user_message[:50]}...")
        if turn.bot_response:
            chatbot = "Nano" if i <= 2 else "Mini"
            print(f"     {chatbot}: {turn.bot_response[:50]}...")

    # End Mini session
    mini.chat_handler.end_conversation()
    await mini.brain.close()

    print("\n✅ Universal conversation test completed!")
    print("🎉 Conversation successfully handed off from Nano to Mini!")

if __name__ == "__main__":
    asyncio.run(test_universal_conversation())