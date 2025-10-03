# File: chatbot/chat_handler.py
# Role: Coordinates chat responses using memory and knowledge retrieval
# Generates contextually aware responses by combining relevant information

from typing import Dict, List
from .llm_client import LLMClient
from ..utils import get_logger
from datetime import datetime
from core.brain.conversation_manager import UniversalConversationManager
from core.brain.context_builder import build_context_block
logger = get_logger(__name__)




class ChatHandler:
    """Handles chat interactions with communal brain integration and conversation context"""

    def __init__(self, brain, embeddings_mgr, llm_client: LLMClient,
                 conversation_manager: UniversalConversationManager,
                 memory_config=None, knowledge_config=None, llm_config=None):
        """
        Initialize chat handler

        Args:
            brain: CommunalBrain instance
            embeddings_mgr: EmbeddingsManager for generating embeddings
            llm_client: LLMClient instance for LLM API calls
            conversation_manager: UniversalConversationManager for session handling
            memory_config: Memory configuration (optional)
            knowledge_config: Knowledge configuration (optional)
            llm_config: LLM configuration for temperature/max_tokens (optional)
        """
        self.brain = brain
        self.embeddings_mgr = embeddings_mgr
        self.llm_client = llm_client
        self.conversation_manager = conversation_manager

        # Store configs
        self.memory_config = memory_config
        self.knowledge_config = knowledge_config
        self.llm_config = llm_config

        # Extract LLM parameters with defaults
        self.temperature = llm_config.temperature if llm_config else 0.7
        self.max_tokens = llm_config.max_tokens if llm_config else 1000

        # Session management
        self.current_session_id = None

    async def start_conversation(self, session_id: str = None) -> str:
        """Start a new conversation session"""
        self.current_session_id = await self.conversation_manager.start_conversation("mini", session_id)
        return self.current_session_id

    async def end_conversation(self):
        """End the current conversation session"""
        if self.current_session_id:
            await self.conversation_manager.end_conversation(self.current_session_id)
            self.current_session_id = None

    async def generate_response(self, user_message: str, query_embedding: List[float] = None) -> tuple:
        """
        Generate response using memory, knowledge, and conversation context from communal brain

        Args:
            user_message: User's input message
            query_embedding: Pre-computed embedding for the user message (optional)

        Returns:
            Tuple of (response, token_info)
        """
        # Ensure we have a session
        if not self.current_session_id:
            await self.start_conversation()

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

        conversation_history = await self.conversation_manager.get_conversation_history(
            self.current_session_id,
            max_turns=self.memory_config.max_conversation_history if self.memory_config else 8
        )

        # Generate response using comprehensive context
        response, token_info = await self._generate_response(
            user_message,
            relevant_memories,
            knowledge_results,
            conversation_history
        )

        # Add conversation turn to universal manager
        await self.conversation_manager.add_turn(
            self.current_session_id,
            user_message,
            response,
            tokens_used=token_info.get('total_tokens', 0),
            metadata={"model": self.llm_client.model}
        )

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
        knowledge: List,
        conversation_history
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
        full_context = build_context_block(
            user_message=user_message,
            conversation_history=conversation_history,
            memories=memory_dicts,
            knowledge=knowledge_dicts,
            max_memory_items=self.memory_config.top_k if self.memory_config else 3,
            max_knowledge_items=self.knowledge_config.top_k if self.knowledge_config else 2,
        )

        # Save context for debugging (like Nano does)
        await self._save_context_snapshot(full_context, user_message, memory_dicts, knowledge_dicts)

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

    def _get_system_prompt(self) -> str:
        """Get system prompt for Mini chatbot"""
        return (
            "You are GOB (Grid Overwatch Bridge), a helpful AI assistant in the The-Net homelab. "
            "You are fiercely dedicated to open source software and digital privacy. "
            "Keep responses helpful and contextual. Use the provided conversation history and memories "
            "to maintain continuity and provide relevant responses. Reference previous parts of the "
            "conversation when appropriate."
        )

    async def _save_context_snapshot(self, full_context: str, user_message: str,
                              memories: List[Dict], knowledge: List[Dict]):
        """Save context snapshot for debugging (like Nano does)"""
        try:
            import os
            from pathlib import Path

            # Save to core/data/last_context.txt (same location as Nano)
            # From mini/src/core/chat_handler.py, go up to gob/, then to core/data/
            context_file = Path(__file__).parent.parent.parent.parent / "core" / "data" / "last_context.txt"

            # Get conversation summary for stats
            conversation_turns = 0
            if self.current_session_id:
                summary = await self.conversation_manager.get_conversation_summary(self.current_session_id)
                conversation_turns = summary.get('total_turns', 0)

            logger.info(f"Saving Mini context snapshot to: {context_file}")
            logger.info(f"Context length: {len(full_context)} characters")
            logger.info(f"Conversation turns: {conversation_turns}")

            with open(context_file, 'w', encoding='utf-8') as f:
                f.write("=== MINI CHATBOT CONTEXT ===\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Session ID: {self.current_session_id}\n\n")
                f.write(full_context)
                f.write("\n\n=== DEBUG INFO ===\n")
                f.write(f"Conversation turns: {conversation_turns}\n")
                f.write(f"Memories retrieved: {len(memories)}\n")
                f.write(f"Knowledge retrieved: {len(knowledge)}\n")
                f.write(f"Session ID: {self.current_session_id}\n")
                f.write(f"Current user message: {user_message[:100]}{'...' if len(user_message) > 100 else ''}\n")

            logger.info("Mini context snapshot saved successfully")

        except Exception as e:
            logger.error(f"Could not save context snapshot: {e}")
            import traceback
            logger.error(traceback.format_exc())

    async def clear_conversation(self):
        """Clear conversation history by ending current session and starting new one"""
        if self.current_session_id:
            await self.conversation_manager.end_conversation(self.current_session_id)
        await self.start_conversation()
        return self.current_session_id

    async def get_conversation_history(self, max_turns=10):
        """Get conversation history for current session"""
        if self.current_session_id:
            return await self.conversation_manager.get_conversation_history(self.current_session_id, max_turns)
        return []

    async def list_all_conversations(self, limit=10):
        """List all conversations across all chatbots"""
        return await self.conversation_manager.list_all_conversations(limit)
