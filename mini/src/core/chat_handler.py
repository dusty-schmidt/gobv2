# File: chatbot/chat_handler.py
# Role: Coordinates chat responses using memory and knowledge retrieval
# Generates contextually aware responses by combining relevant information

from typing import Dict, List
from .llm_client import LLMClient
from ..utils import get_logger
from datetime import datetime
logger = get_logger(__name__)


class ContextManager:
    """Manages conversation context for Mini chatbot"""

    def __init__(self, max_history=20):
        self.conversation_history = []
        self.max_history = max_history
        self.debug_mode = False

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        message = {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        self.conversation_history.append(message)

        # Keep only recent messages
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def get_recent_context(self, max_messages=8):
        """Get recent conversation context for LLM"""
        return self.conversation_history[-max_messages:] if len(self.conversation_history) > max_messages else self.conversation_history

    def clear(self):
        """Clear conversation history"""
        self.conversation_history = []

    def toggle_debug(self):
        """Toggle debug mode"""
        self.debug_mode = not self.debug_mode
        return self.debug_mode


class ChatHandler:
    """Handles chat interactions with communal brain integration and conversation context"""

    def __init__(self, brain, embeddings_mgr, llm_client: LLMClient,
                 memory_config=None, knowledge_config=None, llm_config=None):
        """
        Initialize chat handler

        Args:
            brain: CommunalBrain instance
            embeddings_mgr: EmbeddingsManager for generating embeddings
            llm_client: LLMClient instance for LLM API calls
            memory_config: Memory configuration (optional)
            knowledge_config: Knowledge configuration (optional)
            llm_config: LLM configuration for temperature/max_tokens (optional)
        """
        self.brain = brain
        self.embeddings_mgr = embeddings_mgr
        self.llm_client = llm_client

        # Store configs
        self.memory_config = memory_config
        self.knowledge_config = knowledge_config
        self.llm_config = llm_config

        # Extract LLM parameters with defaults
        self.temperature = llm_config.temperature if llm_config else 0.7
        self.max_tokens = llm_config.max_tokens if llm_config else 1000

        # Initialize context manager for conversation history
        self.context_manager = ContextManager(max_history=20)

    async def generate_response(self, user_message: str, query_embedding: List[float] = None) -> tuple:
        """
        Generate response using memory, knowledge, and conversation context from communal brain

        Args:
            user_message: User's input message
            query_embedding: Pre-computed embedding for the user message (optional)

        Returns:
            Tuple of (response, token_info)
        """
        # Add user message to conversation context
        self.context_manager.add_message("user", user_message)

        # Generate embedding if not provided
        if query_embedding is None:
            import asyncio
            query_embedding = await asyncio.get_event_loop().run_in_executor(
                None, self.embeddings_mgr.encode, user_message
            )

        # Retrieve relevant memories from communal brain
        relevant_memories = await self.brain.retrieve_memories(
            query_embedding,
            top_k=self.memory_config.top_k if self.memory_config else 3,
            min_similarity=self.memory_config.similarity_threshold if self.memory_config else 0.3
        )

        # Search knowledge base from communal brain
        knowledge_results = await self.brain.retrieve_knowledge(
            query_embedding,
            top_k=self.knowledge_config.top_k if self.knowledge_config else 2,
            min_similarity=self.knowledge_config.similarity_threshold if self.knowledge_config else 0.4
        )

        # Generate response using comprehensive context
        response, token_info = await self._generate_response(
            user_message,
            relevant_memories,
            knowledge_results
        )

        # Add AI response to conversation context
        self.context_manager.add_message("assistant", response)

        # Store this interaction in communal brain
        try:
            await self.brain.store_memory(
                user_message=user_message,
                bot_response=response,
                embedding=query_embedding,
                context="chat_interaction"
            )
        except Exception:
            logger.exception('Failed to save memory for message: %s', user_message)

        return response, token_info

    async def _generate_response(
        self,
        user_message: str,
        memories: List,
        knowledge: List
    ) -> tuple:
        """
        Build comprehensive context and generate LLM response

        Args:
            user_message: Current user message
            memories: Relevant MemoryItem objects
            knowledge: Relevant KnowledgeItem objects

        Returns:
            Tuple of (response, token_info)
        """
        # Convert to format expected by LLM client
        memory_dicts = []
        for mem in memories:
            memory_dicts.append({
                'user_message': mem.user_message,
                'bot_response': mem.bot_response,
                'similarity_score': mem.relevance_score,
                'device_id': mem.device_id,
                'timestamp': mem.timestamp
            })

        knowledge_dicts = []
        for kb in knowledge:
            knowledge_dicts.append({
                'text': kb.content,
                'similarity_score': kb.relevance_score,
                'metadata': {
                    'source': kb.source,
                    'device_id': kb.device_id,
                    'chunk_index': kb.chunk_index
                }
            })

        # Build comprehensive context like Nano does
        full_context = self._build_comprehensive_context(user_message, memory_dicts, knowledge_dicts)

        # Save context for debugging (like Nano does)
        self._save_context_snapshot(full_context, user_message, memory_dicts, knowledge_dicts)

        # For LLM API, send as separate messages for better control
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": full_context}
        ]

        # Generate response via LLM using config values (non-streaming for now)
        response, token_info = self.llm_client.generate_response(
            messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=False
        )

        return response, token_info

    def _build_comprehensive_context(self, user_message: str, memories: List[Dict], knowledge: List[Dict]) -> str:
        """Build comprehensive context including conversation history, memories, and knowledge"""
        context_parts = []

        # Add recent conversation context
        recent_context = self.context_manager.get_recent_context(max_messages=8)
        if recent_context:
            context_parts.append("=== RECENT CONVERSATION HISTORY ===")
            for msg in recent_context[:-1]:  # Exclude current user message
                role_display = "USER" if msg["role"] == "user" else "ASSISTANT"
                context_parts.append(f"**{role_display}**: {msg['content']}")
            context_parts.append("")

        # Add relevant long-term memories
        if memories:
            context_parts.append("=== RELEVANT LONG-TERM MEMORIES ===")
            for i, mem in enumerate(memories[:3], 1):  # Limit to 3 for conciseness
                context_parts.append(
                    f"**Memory {i}** (relevance: {mem['similarity_score']:.2f}):"
                    f"\n  User asked: {mem['user_message']}"
                    f"\n  Assistant replied: {mem['bot_response']}"
                )
            context_parts.append("")

        # Add knowledge if available
        if knowledge:
            context_parts.append("=== RELEVANT KNOWLEDGE ===")
            for i, kb in enumerate(knowledge[:2], 1):  # Limit to 2 knowledge items
                source = kb['metadata'].get('source', 'Unknown')
                context_parts.append(
                    f"**Knowledge {i}** (relevance: {kb['similarity_score']:.2f}, source: {source}):"
                    f"\n  {kb['text'][:500]}{'...' if len(kb['text']) > 500 else ''}"
                )
            context_parts.append("")

        # Add current user message
        context_parts.append(f"=== CURRENT USER MESSAGE ===\n{user_message}")

        return "\n".join(context_parts)

    def _get_system_prompt(self) -> str:
        """Get system prompt for Mini chatbot"""
        return (
            "You are GOB (Grid Overwatch Bridge), a helpful AI assistant in the The-Net homelab. "
            "You are fiercely dedicated to open source software and digital privacy. "
            "Keep responses helpful and contextual. Use the provided conversation history and memories "
            "to maintain continuity and provide relevant responses. Reference previous parts of the "
            "conversation when appropriate."
        )

    def _save_context_snapshot(self, full_context: str, user_message: str,
                              memories: List[Dict], knowledge: List[Dict]):
        """Save context snapshot for debugging (like Nano does)"""
        try:
            import os
            from pathlib import Path

            # Save to core/data/last_context.txt (same location as Nano)
            # From mini/src/core/chat_handler.py, go up to gob/, then to core/data/
            context_file = Path(__file__).parent.parent.parent.parent / "core" / "data" / "last_context.txt"

            logger.info(f"Saving Mini context snapshot to: {context_file}")
            logger.info(f"Context length: {len(full_context)} characters")
            logger.info(f"Conversation turns: {len(self.context_manager.conversation_history)}")

            with open(context_file, 'w', encoding='utf-8') as f:
                f.write("=== MINI CHATBOT CONTEXT ===\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
                f.write(full_context)
                f.write("\n\n=== DEBUG INFO ===\n")
                f.write(f"Conversation turns: {len(self.context_manager.conversation_history)}\n")
                f.write(f"Memories retrieved: {len(memories)}\n")
                f.write(f"Knowledge retrieved: {len(knowledge)}\n")
                f.write(f"Debug mode: {self.context_manager.debug_mode}\n")
                f.write(f"Current user message: {user_message[:100]}{'...' if len(user_message) > 100 else ''}\n")

            logger.info("Mini context snapshot saved successfully")

        except Exception as e:
            logger.error(f"Could not save context snapshot: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def clear_conversation(self):
        """Clear conversation history"""
        self.context_manager.clear()

    def toggle_debug(self):
        """Toggle debug mode for context inspection"""
        return self.context_manager.toggle_debug()

