#!/usr/bin/env python3
"""
Test script to verify persistent conversation context across sessions
"""

import asyncio
import sys
from pathlib import Path
import json

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from nano.main import NanoChatbot

async def test_persistent_context():
    """Test persistent conversation context across sessions"""
    print("🔄 Testing Persistent Conversation Context")
    print("=" * 50)

    data_dir = workspace_root / "core" / "data"
    conversations_dir = data_dir / "conversations"

    # Clean up any existing test conversations
    if conversations_dir.exists():
        for file in conversations_dir.glob("nano_*test*.json"):
            file.unlink()

    print("Creating first Nano instance (Session 1)...")
    nano1 = NanoChatbot()
    await nano1.initialize()

    # First conversation
    print("💬 Session 1 - First message...")
    msg1 = "Hello Nano! My name is PersistentTester and I love testing."
    response1, stats1 = await nano1.chat(msg1)
    print(f"🤖 Nano: {response1[:100]}...")

    print("💬 Session 1 - Second message...")
    msg2 = "Can you remember my name?"
    response2, stats2 = await nano1.chat(msg2)
    print(f"🤖 Nano: {response2[:100]}...")

    await nano1.brain.close()

    # Check if conversation was saved
    conversation_files = list(conversations_dir.glob("nano_*.json"))
    if conversation_files:
        print(f"✅ Conversation saved: {len(conversation_files)} file(s)")

        # Read the most recent conversation file
        latest_file = max(conversation_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        print(f"   Session ID: {saved_data.get('session_id', 'unknown')}")
        print(f"   Messages saved: {len(saved_data.get('messages', []))}")
        print(f"   Device: {saved_data.get('device', 'unknown')}")

    else:
        print("❌ No conversation files found!")
        return

    print("\nCreating second Nano instance (Session 2)...")
    nano2 = NanoChatbot()
    await nano2.initialize()

    # Check if persistent context was loaded
    initial_history_length = len(nano2.conversation.conversation_history)
    print(f"📚 Initial conversation history loaded: {initial_history_length} messages")

    if initial_history_length > 0:
        print("✅ Persistent context loaded successfully!")
        print("   Sample loaded messages:")
        for i, msg in enumerate(nano2.conversation.conversation_history[:3]):
            role = "You" if msg["role"] == "user" else "Nano"
            content_preview = msg["content"][:60] + "..." if len(msg["content"]) > 60 else msg["content"]
            print(f"   {i+1}. {role}: {content_preview}")
    else:
        print("⚠️  No persistent context loaded (this may be expected for first run)")

    # Test conversation continuity
    print("\n💬 Session 2 - Testing context continuity...")
    msg3 = "What was my name again?"
    response3, stats3 = await nano2.chat(msg3)
    print(f"🤖 Nano: {response3[:100]}...")

    # Check if context includes previous session
    context_includes_previous = any("[Previous Session]" in msg["content"]
                                   for msg in nano2.conversation.conversation_history)
    if context_includes_previous:
        print("✅ Previous session context included in current conversation!")
    else:
        print("ℹ️  Previous session context not yet included (may appear in context building)")

    await nano2.brain.close()

    # Verify conversation files
    final_conversation_files = list(conversations_dir.glob("nano_*.json"))
    print(f"\n📁 Total conversation files: {len(final_conversation_files)}")

    # Clean up test files
    for file in conversations_dir.glob("nano_*test*.json"):
        file.unlink()

    print("\n✅ Persistent context testing completed!")

if __name__ == "__main__":
    asyncio.run(test_persistent_context())