#!/usr/bin/env python3
# File: tools/example_usage.py
# Role: Demonstrates programmatic usage of the chatbot (moved from project root)

import sys
import os
# Ensure project root is on sys.path when running scripts from tools/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from main import Chatbot
from config import ChatbotConfig
import time

def example_basic_chat():
    """Basic chatbot usage example"""
    print("="*60)
    print("Example 1: Basic Chat")
    print("="*60 + "\n")

    # Initialize chatbot
    bot = Chatbot()

    # Have a conversation
    questions = [
        "What is Python?",
        "Tell me about machine learning",
        "What are the main types of ML?"
    ]

    for question in questions:
        print(f"User: {question}")
        response = bot.chat(question)
        print(f"Bot: {response}\n")
        time.sleep(1)

    # Show stats
    bot.show_stats()

    # Cleanup
    bot.cleanup()

def example_custom_config():
    """Example with custom configuration"""
    print("\n" + "="*60)
    print("Example 2: Custom Configuration")
    print("="*60 + "\n")

    # Create custom config
    config = ChatbotConfig()
    config.memory.top_k = 5  # Retrieve more memories
    config.memory.similarity_threshold = 0.2  # Lower threshold
    config.embeddings.model_name = "text-embedding-3-large"  # Better embeddings

    # Initialize with custom config
    bot = Chatbot(config)

    response = bot.chat("What is supervised learning?")
    print(f"Bot: {response}\n")

    bot.cleanup()

def example_memory_retrieval():
    """Example showing memory retrieval"""
    print("\n" + "="*60)
    print("Example 3: Memory Retrieval")
    print("="*60 + "\n")

    bot = Chatbot()

    # First conversation
    print("User: My favorite color is blue")
    response = bot.chat("My favorite color is blue")
    print(f"Bot: {response}\n")

    time.sleep(1)

    # Ask about it later
    print("User: What's my favorite color?")
    response = bot.chat("What's my favorite color?")
    print(f"Bot: {response}\n")

    bot.cleanup()

if __name__ == "__main__":
    print("\n\ud83e\udd16 Chatbot Usage Examples\n")

    try:
        example_basic_chat()
        example_custom_config()
        example_memory_retrieval()

        print("\n\u2705 All examples completed successfully!\n")

    except Exception as e:
        print(f"\n\u274c Error: {e}\n")
        import traceback
        traceback.print_exc()
