# File: chatbot/chat_handler.py
# Role: Coordinates chat responses using memory and knowledge retrieval
# Generates contextually aware responses by combining relevant information

from typing import Dict, List
from .llm_client import LLMClient
from ..utils import get_logger
logger = get_logger(__name__)

class ChatHandler:
    """Handles chat interactions with communal brain integration"""

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

    async def generate_response(self, user_message: str, query_embedding: List[float] = None) -> tuple:
        """
        Generate response using memory and knowledge context from communal brain

        Args:
            user_message: User's input message
            query_embedding: Pre-computed embedding for the user message (optional)

        Returns:
            Tuple of (response, token_info)
        """
        # Generate embedding if not provided
        if query_embedding is None:
            import asyncio
            query_embedding = await asyncio.get_event_loop().run_in_executor(
                None, self.embeddings_mgr.embed_text, user_message
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

        # Generate response using context
        response, token_info = await self._generate_response(
            user_message,
            relevant_memories,
            knowledge_results
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
        knowledge: List
    ) -> tuple:
        """
        Build context and generate LLM response

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

        # Build messages using LLM client's prompt building method (loads system prompt from config)
        messages = self.llm_client.build_prompt_with_context(
            user_message,
            memory_dicts,
            knowledge_dicts
        )

        # Generate response via LLM using config values (non-streaming for now)
        response, token_info = self.llm_client.generate_response(
            messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=False
        )

        return response, token_info

