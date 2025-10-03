#!/usr/bin/env python3
"""
Test SummarizerAgent functionality
Tests conversation summarization using meta-llama/llama-3.3-8b-instruct:free
"""

import asyncio
import json
import os
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

# Add the gob directory to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.summarizer_agent import SummarizerAgent, SummarizerConfig
from core.logging import get_logger

logger = get_logger(__name__)

async def test_summarizer_agent():
    """Test the SummarizerAgent with sample conversation data"""

    print("🧠 Testing SummarizerAgent")
    print("=" * 50)

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir) / "data"
        data_dir.mkdir()

        # Create subdirectories
        conversations_dir = data_dir / "conversations"
        summaries_dir = data_dir / "summaries"
        conversations_dir.mkdir()
        summaries_dir.mkdir()

        # Create sample conversation data
        sample_conversation = {
            "session_id": "test_session_001",
            "device": "test_device",
            "timestamp": datetime.now().isoformat(),
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! I'm testing this chatbot system. My name is TestUser and I love exploring new AI technologies.",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "assistant",
                    "content": "Hi TestUser! Welcome to our AI chatbot system. It's great to meet someone passionate about AI technologies. I'm here to help you explore and understand our system. What would you like to know about our capabilities?",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "user",
                    "content": "Can you tell me about the memory system? How does it work and what makes it special?",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "assistant",
                    "content": "Absolutely! Our memory system is quite sophisticated. We use vector embeddings to store and retrieve conversation memories, allowing the AI to remember past interactions across sessions. The key features include: semantic search using cosine similarity, persistent storage in SQLite, knowledge base integration, and device-aware memory sharing. This means all your devices can share the same learned knowledge!",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "user",
                    "content": "That sounds amazing! How do you handle context management when conversations get long?",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "assistant",
                    "content": "Great question! We have a multi-layered approach to context management: 1) Recent conversation history is always included, 2) Relevant memories are retrieved based on semantic similarity, 3) We use summarization agents to compress old conversations when they become too long, and 4) We maintain persistent conversation logs that survive across sessions. This ensures continuity while keeping context sizes manageable for the AI models.",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }

        # Save sample conversation
        conv_file = conversations_dir / "test_conversation.json"
        with open(conv_file, 'w') as f:
            json.dump(sample_conversation, f, indent=2)

        print(f"📝 Created sample conversation file: {conv_file.name}")
        print(f"   Messages: {len(sample_conversation['messages'])}")
        print(f"   File size: {conv_file.stat().st_size} bytes")

        # Initialize SummarizerAgent
        config = SummarizerConfig()
        # Reduce file size threshold for testing
        config.max_file_size_bytes = 1000  # 1KB to trigger summarization

        summarizer = SummarizerAgent(data_dir, config)

        print("🤖 Initialized SummarizerAgent")
        print(f"   Model: {config.model}")
        print(f"   Max file size: {config.max_file_size_bytes} bytes")

        # Test file size check
        should_summarize = await summarizer._should_summarize_file(conv_file)
        print(f"📏 Should summarize file: {should_summarize}")

        if should_summarize:
            print("🔄 Summarizing conversation...")

            # Test summarization
            success = await summarizer._summarize_conversation_file(conv_file)

            if success:
                print("✅ Summarization completed!")

                # Check if summary was created
                summary_files = list(summaries_dir.glob("*.json"))
                if summary_files:
                    summary_file = summary_files[0]
                    print(f"📄 Summary file created: {summary_file.name}")

                    # Read and display summary
                    with open(summary_file, 'r') as f:
                        summary_data = json.load(f)

                    print("📋 Summary content:")
                    print(f"   Original messages: {summary_data['original_message_count']}")
                    print(f"   Summarized at: {summary_data['summarized_at']}")
                    print(f"   Model used: {summary_data['summarizer_model']}")
                    print("   Summary text:"
                    print(f"   {summary_data['summary'][:200]}...")

                # Check if original was archived
                archive_dir = data_dir / "archive" / "conversations"
                archived_files = list(archive_dir.glob("*.json")) if archive_dir.exists() else []
                if archived_files:
                    print(f"📦 Original archived: {archived_files[0].name}")
                else:
                    print("⚠️  Original file still exists (not archived)")
            else:
                print("❌ Summarization failed")
        else:
            print("ℹ️  File does not need summarization yet")

        # Test context size checking
        print("\n🧠 Testing context size checking...")

        # Create a long context string
        long_context = "This is a test context. " * 200  # ~4000 characters
        context_tokens = len(long_context) // 4  # Rough token estimate

        print(f"📏 Test context length: {len(long_context)} chars (~{context_tokens} tokens)")

        is_too_large, suggested_summary = await summarizer.check_context_size(long_context)

        if is_too_large:
            print("⚠️  Context flagged as too large")
            if suggested_summary:
                print("💡 Suggested summary:")
                print(f"   {suggested_summary[:150]}...")
        else:
            print("✅ Context size is acceptable")

        # Get summarizer stats
        stats = summarizer.get_stats()
        print("
📊 Summarizer Stats:"        for key, value in stats.items():
            print(f"   {key}: {value}")

    print("\n🎉 SummarizerAgent testing completed!")

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ OPENROUTER_API_KEY environment variable not set")
        print("   Please set it to test the summarizer")
        sys.exit(1)

    asyncio.run(test_summarizer_agent())