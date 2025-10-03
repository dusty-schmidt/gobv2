#!/usr/bin/env python3
# Debug script to show what prompts are being sent to the LLM

import os
from pathlib import Path
from typing import List, Dict

# Import TOML loader directly
try:
    import tomllib
except ImportError:
    import tomli as tomllib

def load_config():
    """Load configuration from config.toml file"""
    config_path = Path(__file__).parent / "config.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    return {}

def build_prompt_with_context(
    user_message: str,
    memories: List[Dict],
    knowledge: List[Dict],
    system_prompt: str = None
) -> List[Dict[str, str]]:
    """
    Build messages array with context from memories and knowledge
    (Copied from llm_client.py for debugging)
    """
    # Load system prompt from config or use default
    if system_prompt is None:
        _toml_config = load_config()
        prompts_config = _toml_config.get("prompts", {})
        system_prompt = prompts_config.get("system_prompt", "").strip()
        if not system_prompt:
            # Fallback default if TOML doesn't have it
            system_prompt = (
                "You are a helpful AI assistant with access to conversation history "
                "and a knowledge base. Use the provided context to give accurate, "
                "contextual responses. If the context is relevant, reference it naturally. "
                "If you're not sure about something, say so."
            )

    # Build context section
    context_parts = []

    if memories:
        context_parts.append("=== RELEVANT PAST CONVERSATIONS ===")
        for i, mem in enumerate(memories, 1):
            context_parts.append(
                f"\nConversation {i} (similarity: {mem['similarity_score']:.2f}):\n"
                f"User: {mem['user_message']}\n"
                f"Assistant: {mem['bot_response']}"
            )

    if knowledge:
        context_parts.append("\n=== RELEVANT KNOWLEDGE BASE ===")
        for i, kb in enumerate(knowledge, 1):
            source = kb['metadata'].get('source', 'Unknown')
            context_parts.append(
                f"\nKnowledge {i} (similarity: {kb['similarity_score']:.2f}, "
                f"source: {source}):\n{kb['text']}"
            )

    # Construct messages
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Add context as a system message if available
    if context_parts:
        context_content = "\n".join(context_parts)
        messages.append({
            "role": "system",
            "content": f"Here is relevant context:\n\n{context_content}"
        })

    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message
    })

    return messages

def test_prompt_building():
    """Test the prompt building functionality"""

    # Test data
    user_message = "Hello, who are you?"
    memories = [
        {
            'user_message': 'What is your name?',
            'bot_response': 'I am GOB, your AI assistant.',
            'similarity_score': 0.85
        }
    ]
    knowledge = [
        {
            'text': 'GOB stands for General Operations Bot in the homelab called The-Net.',
            'source': 'system_info.txt',
            'metadata': {'source': 'system_info.txt'},
            'similarity_score': 0.72
        }
    ]

    # Build the prompt
    messages = build_prompt_with_context(user_message, memories, knowledge)

    print("=== FULL PROMPT BEING SENT TO MODEL ===")
    print()

    for i, msg in enumerate(messages, 1):
        print(f"## Message {i}: {msg['role'].upper()}")
        print(msg['content'])
        print()

    print("=" * 50)
    print(f"Total messages: {len(messages)}")
    print()

    # Show what system prompt was loaded
    config = load_config()
    prompts_config = config.get("prompts", {})
    system_prompt = prompts_config.get("system_prompt", "").strip()
    if system_prompt:
        print("✅ System prompt loaded from config.toml")
    else:
        print("⚠️  Using fallback system prompt (config.toml not found or empty)")

if __name__ == "__main__":
    test_prompt_building()