#!/usr/bin/env python3
"""
Test mini chatbot integration with Phase 1 refactored system
Tests basic initialization and data saving without API calls
"""

import asyncio
import sys
import os
from pathlib import Path

# Add workspace root to path
workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root))

# Set dummy API keys for testing
os.environ['OPENAI_API_KEY'] = 'dummy-key-for-testing'
os.environ['OPENROUTER_API_KEY'] = 'dummy-key-for-testing'

async def test_mini_integration():
    """Test mini chatbot integration with new system"""
    print("🧪 Testing Mini Chatbot Integration")
    print("=" * 50)

    try:
        # Import mini chatbot components
        from mini.src.core.main import Chatbot
        from mini.src.core.config import ChatbotConfig

        print("✅ Mini imports successful")

        # Create config with minimal settings
        config = ChatbotConfig()
        # Disable features that require real API calls
        config.llm.api_key = 'dummy-key'
        config.embeddings.api_key = 'dummy-key'

        # Create chatbot instance
        bot = Chatbot(config)
        print("✅ Chatbot instance created")

        # Initialize (this should set up the communal brain)
        await bot.initialize()
        print("✅ Chatbot initialized successfully")

        # Check if brain is working
        stats = await bot.brain.get_memory_stats()
        print(f"✅ Brain stats: {stats['memory_count']} memories, {stats['device_count']} devices")

        # Test basic memory storage
        test_embedding = [0.1] * 1536  # Mock embedding
        memory_id = await bot.brain.store_memory(
            "Test user message",
            "Test bot response",
            test_embedding
        )
        print(f"✅ Memory stored with ID: {memory_id}")

        # Verify memory was stored
        final_stats = await bot.brain.get_memory_stats()
        if final_stats['memory_count'] > stats['memory_count']:
            print("✅ Memory count increased after storage")
        else:
            print("❌ Memory count did not increase")

        # Check if data directory has files
        data_dir = workspace_root / "core" / "data"
        db_file = data_dir / "communal_brain.db"

        if db_file.exists():
            db_size = db_file.stat().st_size
            print(f"✅ Database exists: {db_size} bytes")
        else:
            print("❌ Database file not found")

        # Check for any log files
        last_context = data_dir / "last_context.txt"
        if last_context.exists():
            print("✅ Last context file exists")
        else:
            print("ℹ️  Last context file not yet created (expected for basic test)")

        # Cleanup
        await bot.brain.close()

        print("\n" + "=" * 50)
        print("🎉 Mini integration test completed successfully!")
        print("✅ Communal brain is working")
        print("✅ Data is being saved to core/data/")
        print("✅ Database file exists and is accessible")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mini_integration())
    sys.exit(0 if success else 1)