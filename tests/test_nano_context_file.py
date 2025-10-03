#!/usr/bin/env python3
"""
Test script to verify Nano context file creation and content
"""

import asyncio
import sys
from pathlib import Path

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from nano.main import NanoChatbot

async def test_nano_context_file():
    """Test Nano context file creation and content verification"""
    print("📄 Testing Nano Context File Creation")
    print("=" * 50)

    # Initialize Nano
    nano = NanoChatbot()
    await nano.initialize()

    # Test a conversation
    print("💬 Testing conversation with context file creation...")

    msg1 = "Hello Nano! My name is TestUser and I like coding."
    print(f"You: {msg1}")
    response1, stats1 = await nano.chat(msg1)
    print(f"🤖 Nano: {response1}")
    print()

    # Check if context file was created
    context_file = workspace_root / "core" / "last_context.txt"
    if context_file.exists():
        print("✅ Context file created successfully!")

        # Read and display context file content
        with open(context_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"📄 Context file size: {len(content)} characters")
        print("\n📋 Context file content preview:")
        print("=" * 50)

        # Show first 1000 characters
        preview = content[:1000] + "..." if len(content) > 1000 else content
        print(preview)
        print("=" * 50)

        # Verify key sections are present
        checks = [
            ("System prompt section", "=== SYSTEM PROMPT ===" in content),
            ("Conversation history", "=== RECENT CONVERSATION HISTORY ===" in content),
            ("Long-term memories", "=== RELEVANT LONG-TERM MEMORIES ===" in content),
            ("Current user message", "=== CURRENT USER MESSAGE ===" in content),
            ("Debug info section", "=== DEBUG INFO ===" in content),
            ("Timestamp", "Timestamp:" in content),
            ("Conversation turns", "Conversation turns:" in content),
            ("Memories retrieved", "Memories retrieved:" in content),
        ]

        print("\n🔍 Content verification:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False

        if all_passed:
            print("\n✅ ALL CONTEXT FILE CHECKS PASSED!")
        else:
            print("\n❌ Some context file checks failed")

    else:
        print("❌ Context file was not created!")
        return

    # Test second message to see context accumulation
    print("\n💬 Testing second message...")
    msg2 = "What's my name?"
    print(f"You: {msg2}")
    response2, stats2 = await nano.chat(msg2)
    print(f"🤖 Nano: {response2}")
    print()

    # Check updated context file
    if context_file.exists():
        with open(context_file, 'r', encoding='utf-8') as f:
            updated_content = f.read()

        print("📄 Updated context file after second message:")
        print(f"   Size: {len(updated_content)} characters")

        # Check if conversation history grew
        if len(updated_content) > len(content):
            print("✅ Context file grew with conversation history")
        else:
            print("⚠️  Context file size didn't change significantly")

    await nano.brain.close()

    print("\n✅ Context file testing completed!")

if __name__ == "__main__":
    asyncio.run(test_nano_context_file())