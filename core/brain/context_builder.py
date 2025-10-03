"""Utilities for assembling conversation context for LLM prompts."""

from __future__ import annotations

from typing import Iterable, Dict, List, Any


def build_context_block(
    user_message: str,
    conversation_history: Iterable[Any],
    memories: List[Dict[str, Any]],
    knowledge: List[Dict[str, Any]],
    *,
    max_memory_items: int = 3,
    max_knowledge_items: int = 2,
) -> str:
    """Construct a formatted prompt context from conversation artifacts.

    Args:
        user_message: The latest user utterance.
        conversation_history: Recent conversation turns (objects with user_message/bot_response).
        memories: Retrieved long-term memories from the communal brain.
        knowledge: Retrieved knowledge chunks.
        max_memory_items: Upper bound on the number of memory snippets to include.
        max_knowledge_items: Upper bound on the number of knowledge snippets to include.

    Returns:
        A string containing the assembled context sections.
    """
    context_parts: List[str] = []

    history_list = list(conversation_history)
    if history_list:
        context_parts.append("=== RECENT CONVERSATION HISTORY ===")
        for turn in history_list:
            user_text = getattr(turn, "user_message", "") or ""
            if user_text:
                context_parts.append(f"**USER**: {user_text}")
            assistant_text = getattr(turn, "bot_response", "") or ""
            if assistant_text:
                context_parts.append(f"**ASSISTANT**: {assistant_text}")
        context_parts.append("")

    if memories:
        context_parts.append("=== RELEVANT LONG-TERM MEMORIES ===")
        for idx, mem in enumerate(memories[:max_memory_items], 1):
            similarity = mem.get('similarity_score')
            relevance = f" (relevance: {similarity:.2f})" if isinstance(similarity, float) else ""
            user_text = mem.get('user_message', '')
            assistant_text = mem.get('bot_response', '')
            context_parts.append(
                f"**Memory {idx}**{relevance}:\n  User asked: {user_text}\n  Assistant replied: {assistant_text}"
            )
        context_parts.append("")

    if knowledge:
        context_parts.append("=== RELEVANT KNOWLEDGE ===")
        for idx, chunk in enumerate(knowledge[:max_knowledge_items], 1):
            similarity = chunk.get('similarity_score')
            relevance = f" (relevance: {similarity:.2f})" if isinstance(similarity, float) else ""
            source = chunk.get('metadata', {}).get('source', 'Unknown')
            text = chunk.get('text', '')
            preview = text[:500] + ('...' if len(text) > 500 else '')
            context_parts.append(
                f"**Knowledge {idx}**{relevance}, source: {source}:\n  {preview}"
            )
        context_parts.append("")

    context_parts.append(f"=== CURRENT USER MESSAGE ===\n{user_message}")

    return "\n".join(context_parts)
