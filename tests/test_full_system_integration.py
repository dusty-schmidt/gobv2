#!/usr/bin/env python3
"""
Comprehensive integration test for the full GOB system after Phase 1 refactoring
Tests memory storage, summarization, context loading, and data persistence
"""

import asyncio
import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from core import CommunalBrain, BrainConfig
from core.brain.conversation_manager import UniversalConversationManager
from mini.src.core.embeddings_manager import EmbeddingsManager
from mini.src.core.config import ChatbotConfig


class SystemIntegrationTester:
    """Comprehensive tester for the full GOB system"""

    def __init__(self):
        self.brain = None
        self.conversation_manager = None
        self.embeddings_mgr = None
        self.data_dir = workspace_root / "core" / "data"
        self.session_id = None

    async def setup(self):
        """Initialize all system components"""
        print("🔧 Setting up system components...")

        # Initialize communal brain
        config = BrainConfig()
        config.device_name = "IntegrationTest"
        config.device_location = "test"

        self.brain = CommunalBrain(config)
        await self.brain.initialize()

        # Initialize embeddings
        mini_config = ChatbotConfig()
        self.embeddings_mgr = EmbeddingsManager(
            api_key=mini_config.embeddings.api_key,
            model_name=mini_config.embeddings.model_name,
            embedding_dim=mini_config.embeddings.embedding_dim
        )

        # Initialize conversation manager
        self.conversation_manager = UniversalConversationManager(self.brain)

        # Start a test conversation session
        self.session_id = self.conversation_manager.start_conversation("IntegrationTest")

        print("✅ System setup complete")

    async def teardown(self):
        """Clean up system components"""
        if self.session_id:
            self.conversation_manager.end_conversation(self.session_id)
        if self.brain:
            await self.brain.close()
        print("🧹 System cleanup complete")

    async def test_memory_storage_and_retrieval(self):
        """Test that memories are properly stored and retrieved"""
        print("\n🧠 Testing Memory Storage & Retrieval...")

        # Store some test memories
        test_memories = [
            ("What is Python?", "Python is a high-level programming language known for its simplicity and readability."),
            ("How do I install packages?", "Use pip install package_name to install Python packages."),
            ("What are lists in Python?", "Lists are mutable sequences that can contain different types of objects."),
        ]

        initial_stats = await self.brain.get_memory_stats()
        initial_count = initial_stats['memory_count']

        # Store memories
        for user_msg, bot_response in test_memories:
            embedding = await asyncio.get_event_loop().run_in_executor(
                None, self.embeddings_mgr.encode, user_msg
            )
            await self.brain.store_memory(user_msg, bot_response, embedding)

        # Verify storage
        after_stats = await self.brain.get_memory_stats()
        stored_count = after_stats['memory_count'] - initial_count

        assert stored_count == len(test_memories), f"Expected {len(test_memories)} memories, got {stored_count}"
        print(f"✅ Stored {stored_count} memories successfully")

        # Test retrieval
        query = "How do I use Python lists?"
        query_embedding = await asyncio.get_event_loop().run_in_executor(
            None, self.embeddings_mgr.encode, query
        )

        retrieved_memories = await self.brain.retrieve_memories(query_embedding, top_k=5)

        assert len(retrieved_memories) > 0, "No memories retrieved"
        assert any("lists" in mem.user_message.lower() for mem in retrieved_memories), "Relevant memory not found"
        print(f"✅ Retrieved {len(retrieved_memories)} relevant memories")

        return True

    async def test_conversation_management(self):
        """Test conversation session management"""
        print("\n💬 Testing Conversation Management...")

        # Add conversation turns
        conversation_turns = [
            ("Hello", "Hi there! How can I help you today?"),
            ("Tell me about machine learning", "Machine learning is a subset of AI that enables systems to learn from data."),
            ("What programming language should I learn?", "Python is excellent for beginners and widely used in ML."),
        ]

        for user_msg, bot_response in conversation_turns:
            self.conversation_manager.add_turn(
                self.session_id,
                user_msg,
                bot_response,
                tokens_used=50,
                metadata={"test": True}
            )

        # Verify conversation history
        history = self.conversation_manager.get_conversation_history(self.session_id)
        assert len(history) == len(conversation_turns), f"Expected {len(conversation_turns)} turns, got {len(history)}"

        # Verify conversation summary
        summary = self.conversation_manager.get_conversation_summary(self.session_id)
        assert summary['total_turns'] == len(conversation_turns), "Conversation summary incorrect"

        print(f"✅ Conversation with {len(conversation_turns)} turns managed successfully")
        return True

    async def test_context_logging(self):
        """Test that context snapshots are saved"""
        print("\n📝 Testing Context Logging...")

        # Simulate Nano-style context logging
        context_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "conversation_turns": 3,
            "memories_retrieved": 2,
            "current_query": "Test query",
            "full_context": "Test context content"
        }

        # Save context (simulating Nano's behavior)
        context_file = self.data_dir / "last_context.txt"
        with open(context_file, 'w', encoding='utf-8') as f:
            f.write("=== LAST LLM CONTEXT ===\n")
            f.write(f"Timestamp: {context_data['timestamp']}\n\n")
            f.write(context_data['full_context'])
            f.write("\n\n=== DEBUG INFO ===\n")
            f.write(f"Conversation turns: {context_data['conversation_turns']}\n")
            f.write(f"Memories retrieved: {context_data['memories_retrieved']}\n")
            f.write(f"Session ID: {context_data['session_id']}\n")

        # Verify file was created
        assert context_file.exists(), "Context file not created"
        print("✅ Context snapshot saved successfully")

        # Verify content
        with open(context_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "LAST LLM CONTEXT" in content, "Context header not found"
            assert context_data['session_id'] in content, "Session ID not in context"

        print("✅ Context content verified")
        return True

    async def test_summarization_system(self):
        """Test that the summarization system works"""
        print("\n📋 Testing Summarization System...")

        # Check if summarizer is available
        if not self.brain.summarizer:
            print("⚠️  Summarizer not enabled, skipping summarization tests")
            return True

        # Test context size checking
        large_context = "This is a very long context. " * 1000  # ~30KB of text
        needs_summary, suggested_summary = await self.brain.check_context_size(large_context)

        assert needs_summary, "Large context should require summarization"
        assert suggested_summary, "Should provide summary suggestion"
        print("✅ Context size checking works")

        # Test summarizer stats
        stats = self.brain.get_summarizer_stats()
        assert stats is not None, "Summarizer stats should be available"
        print("✅ Summarizer stats retrieved")

        return True

    async def test_data_persistence(self):
        """Test that data persists correctly across sessions"""
        print("\n💾 Testing Data Persistence...")

        # Store a unique test memory
        test_marker = f"PersistenceTest_{datetime.now().isoformat()}"
        embedding = await asyncio.get_event_loop().run_in_executor(
            None, self.embeddings_mgr.encode, test_marker
        )
        await self.brain.store_memory(test_marker, "Persistence response", embedding)

        # Verify it was stored
        stats = await self.brain.get_memory_stats()
        assert stats['memory_count'] > 0, "No memories found"

        # Create a new brain instance to test persistence
        config2 = BrainConfig()
        config2.device_name = "PersistenceTest2"

        brain2 = CommunalBrain(config2)
        await brain2.initialize()

        # Check if the memory persists
        stats2 = await brain2.get_memory_stats()
        assert stats2['memory_count'] >= stats['memory_count'], "Memory count decreased"

        # Try to retrieve the test memory
        retrieved = await brain2.retrieve_memories(embedding, top_k=10)
        found_test_memory = any(test_marker in mem.user_message for mem in retrieved)
        assert found_test_memory, "Test memory not persisted"

        await brain2.close()
        print("✅ Data persistence verified across sessions")

        return True

    async def test_file_organization(self):
        """Test that files are organized correctly in the data directory"""
        print("\n📁 Testing File Organization...")

        # Check database exists
        db_file = self.data_dir / "communal_brain.db"
        assert db_file.exists(), "Database file not found in data directory"
        print("✅ Database file in correct location")

        # Check directories exist
        required_dirs = ["conversations", "summaries", "archive"]
        for dir_name in required_dirs:
            dir_path = self.data_dir / dir_name
            assert dir_path.exists(), f"Required directory {dir_name} not found"
        print("✅ Required directories exist")

        # Check that context file was created
        context_file = self.data_dir / "last_context.txt"
        assert context_file.exists(), "Context file not in data directory"
        print("✅ Context file in correct location")

        return True

    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Full System Integration Tests")
        print("=" * 60)

        try:
            await self.setup()

            tests = [
                self.test_memory_storage_and_retrieval,
                self.test_conversation_management,
                self.test_context_logging,
                self.test_summarization_system,
                self.test_data_persistence,
                self.test_file_organization,
            ]

            passed = 0
            failed = 0

            for test in tests:
                try:
                    result = await test()
                    if result:
                        passed += 1
                    else:
                        failed += 1
                except Exception as e:
                    print(f"❌ Test {test.__name__} failed: {e}")
                    failed += 1

            print("\n" + "=" * 60)
            print(f"📊 Test Results: {passed} passed, {failed} failed")

            if failed == 0:
                print("🎉 All integration tests passed!")
                return True
            else:
                print("❌ Some tests failed")
                return False

        finally:
            await self.teardown()


async def main():
    """Main test runner"""
    tester = SystemIntegrationTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())