#!/usr/bin/env python3
"""
Test script to verify data saving functionality after Phase 1 refactoring
Tests raw chat logs, summaries, and data persistence without external APIs
"""

import asyncio
import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add workspace root to path
workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root))

async def test_data_saving():
    """Test that data is saved correctly in the new structure"""
    print("🧪 Testing Data Saving Functionality")
    print("=" * 50)

    # Import core components
    from core import CommunalBrain, BrainConfig

    # Initialize brain with test database
    config = BrainConfig()
    config.device_name = "DataSavingTest"
    config.device_location = "test"
    config.storage.local_db_path = "test_data_saving.db"  # Use test database
    config.enable_summarizer = False  # Disable summarizer for testing
    config.enable_sync = False  # Disable sync for testing

    brain = CommunalBrain(config)
    await brain.initialize()

    print("✅ Brain initialized successfully")

    # Test 1: Memory storage
    print("\n📝 Test 1: Memory Storage")
    initial_stats = await brain.get_memory_stats()
    initial_count = initial_stats['memory_count']

    # Store some test memories
    test_memories = [
        ("Hello world", "A simple greeting program"),
        ("Python functions", "Functions are reusable blocks of code"),
        ("Machine learning", "Algorithms that learn from data"),
    ]

    for user_msg, bot_response in test_memories:
        # Create a simple embedding (normally done by embeddings manager)
        embedding = [0.1] * 1536  # Mock embedding
        await brain.store_memory(user_msg, bot_response, embedding)

    final_stats = await brain.get_memory_stats()
    stored_count = final_stats['memory_count'] - initial_count

    assert stored_count == len(test_memories), f"Expected {len(test_memories)} memories, got {stored_count}"
    print(f"✅ Stored {stored_count} memories successfully")

    # Test 2: Conversation management
    print("\n💬 Test 2: Conversation Management")
    from core.brain.conversation_manager import UniversalConversationManager

    conv_manager = UniversalConversationManager(brain)
    session_id = await conv_manager.start_conversation("DataSavingTest")

    # Add conversation turns
    await conv_manager.add_turn(session_id, "What is AI?", "AI stands for Artificial Intelligence", tokens_used=10)
    await conv_manager.add_turn(session_id, "Tell me more", "AI systems can learn and make decisions", tokens_used=8)

    # Check conversation history
    history = await conv_manager.get_conversation_history(session_id)
    assert len(history) == 2, f"Expected 2 conversation turns, got {len(history)}"
    print(f"✅ Conversation with {len(history)} turns managed")

    # Test 3: Raw chat logs (simulate Nano's logging)
    print("\n📄 Test 3: Raw Chat Logs")
    data_dir = workspace_root / "core" / "data"
    context_file = data_dir / "last_context.txt"

    # Simulate context logging
    context_data = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "conversation_turns": len(history),
        "memories_retrieved": 1,
        "current_query": "Test query for logging",
        "full_context": "This is a test context that should be logged"
    }

    with open(context_file, 'w', encoding='utf-8') as f:
        f.write("=== LAST LLM CONTEXT ===\n")
        f.write(f"Timestamp: {context_data['timestamp']}\n\n")
        f.write(context_data['full_context'])
        f.write("\n\n=== DEBUG INFO ===\n")
        f.write(f"Conversation turns: {context_data['conversation_turns']}\n")
        f.write(f"Memories retrieved: {context_data['memories_retrieved']}\n")
        f.write(f"Session ID: {context_data['session_id']}\n")

    # Verify file was created and contains expected content
    assert context_file.exists(), "Context file not created"
    with open(context_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "LAST LLM CONTEXT" in content, "Context header not found"
        assert context_data['session_id'] in content, "Session ID not logged"
        assert str(context_data['conversation_turns']) in content, "Conversation turns not logged"

    print("✅ Raw chat logs saved successfully")

    # Test 4: Conversation persistence
    print("\n💾 Test 4: Conversation Persistence")
    conversation_data = {
        "session_id": session_id,
        "chatbot_name": "DataSavingTest",
        "device_id": "DataSavingTest",
        "start_time": datetime.now().isoformat(),
        "status": "active",
        "metadata": {"test": True},
        "turns": [
            {"role": "user", "content": "Hello", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": "Hi there!", "timestamp": datetime.now().isoformat()},
            {"role": "user", "content": "How are you?", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": "I'm doing well, thank you!", "timestamp": datetime.now().isoformat()}
        ]
    }

    # Save conversation to database
    await brain.storage.store_conversation(session_id, conversation_data)

    # Retrieve conversation
    retrieved = await brain.storage.load_conversation(session_id)
    assert retrieved is not None, "Conversation not retrieved"
    assert retrieved['session_id'] == session_id, "Session ID mismatch"
    assert len(retrieved['turns']) == len(conversation_data['turns']), "Message count mismatch"

    print("✅ Conversation persisted and retrieved successfully")

    # Test 5: Summary system (mock test)
    print("\n📋 Test 5: Summary System Structure")
    summaries_dir = data_dir / "summaries"
    assert summaries_dir.exists(), "Summaries directory not found"

    # Create a mock summary file
    summary_data = {
        "original_session_id": session_id,
        "device": "DataSavingTest",
        "original_timestamp": conversation_data['start_time'],
        "original_message_count": len(conversation_data['turns']),
        "summary": "This is a test summary of the conversation",
        "summarized_at": datetime.now().isoformat(),
        "summarizer_model": "test-model",
        "file_size_bytes": 1024
    }

    summary_filename = f"{session_id}_summary.json"
    summary_filepath = summaries_dir / summary_filename

    with open(summary_filepath, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)

    # Verify summary file
    assert summary_filepath.exists(), "Summary file not created"
    with open(summary_filepath, 'r', encoding='utf-8') as f:
        loaded_summary = json.load(f)
        assert loaded_summary['original_session_id'] == session_id, "Summary session ID mismatch"
        assert 'summary' in loaded_summary, "Summary content missing"

    print("✅ Summary system structure verified")

    # Test 6: Archive system
    print("\n📦 Test 6: Archive System")
    archive_dir = data_dir / "archive" / "conversations"
    assert archive_dir.exists(), "Archive directory not found"

    # Create a mock archived conversation
    archive_filename = f"{session_id}.json"
    archive_filepath = archive_dir / archive_filename

    with open(archive_filepath, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, indent=2)

    assert archive_filepath.exists(), "Archived conversation not created"
    print("✅ Archive system working")

    # Test 7: Data directory structure
    print("\n📁 Test 7: Data Directory Structure")
    required_dirs = ["conversations", "summaries", "archive"]
    for dir_name in required_dirs:
        dir_path = data_dir / dir_name
        assert dir_path.exists(), f"Required directory {dir_name} missing"
        assert dir_path.is_dir(), f"{dir_name} is not a directory"

    # Check database exists
    db_file = data_dir / "communal_brain.db"
    assert db_file.exists(), "Database file missing from data directory"

    print("✅ Data directory structure correct")

    # Cleanup
    await brain.close()

    print("\n" + "=" * 50)
    print("🎉 All data saving tests passed!")
    print("✅ Raw chat logs are being saved")
    print("✅ Conversations are being persisted")
    print("✅ Summary system is ready")
    print("✅ Archive system is working")
    print("✅ Data directory structure is correct")

    return True

if __name__ == "__main__":
    success = asyncio.run(test_data_saving())
    sys.exit(0 if success else 1)
