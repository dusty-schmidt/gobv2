#!/usr/bin/env python3
"""
Test script to verify Nano debug functionality shows full LLM context
"""

import asyncio
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from nano.main import NanoChatbot

async def test_nano_debug():
    """Test Nano debug functionality"""
    print("🔍 Testing Nano Debug Functionality")
    print("=" * 50)

    # Initialize Nano
    nano = NanoChatbot()
    await nano.initialize()

    # Enable debug mode
    print("Enabling debug mode...")
    debug_state = nano.conversation.toggle_debug()
    print(f"Debug mode: {debug_state}")

    # Capture stdout to check debug output
    captured_output = StringIO()

    with patch('sys.stdout', captured_output):
        # Test a simple message
        user_msg = "Hello Nano, this is a test message."
        print(f"You: {user_msg}")

        # Generate embedding (mock for testing)
        import asyncio
        query_embedding = await asyncio.get_event_loop().run_in_executor(
            None, nano.embeddings_mgr.encode, user_msg
        )

        # Retrieve memories (will be empty for new conversation)
        memories = await nano.brain.retrieve_memories(query_embedding, top_k=3)

        # Build context using debug-enabled context manager
        system_prompt = "You are Nano, a helpful AI assistant."
        full_context = nano.conversation.build_llm_context(user_msg, memories, system_prompt)

    # Check if debug output was captured
    debug_output = captured_output.getvalue()

    print("✅ Debug output captured!")
    print(f"Debug output length: {len(debug_output)} characters")

    # Check for expected debug markers
    if "🔍 DEBUG: FULL CONTEXT BEING SENT TO LLM" in debug_output:
        print("✅ Debug header found in output")
    else:
        print("❌ Debug header NOT found in output")

    if "=== SYSTEM PROMPT ===" in debug_output:
        print("✅ System prompt section found")
    else:
        print("❌ System prompt section NOT found")

    if "=== CURRENT USER MESSAGE ===" in debug_output:
        print("✅ User message section found")
    else:
        print("❌ User message section NOT found")

    print("\n📋 Sample debug output:")
    # Show first 500 characters of debug output
    print(debug_output[:500] + "..." if len(debug_output) > 500 else debug_output)

    await nano.brain.close()

    print("\n✅ Debug functionality test completed!")

if __name__ == "__main__":
    asyncio.run(test_nano_debug())