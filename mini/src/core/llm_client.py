# File: chatbot/llm_client.py
# Role: Handles API calls to OpenRouter for LLM responses
# Manages prompt construction and streaming/non-streaming completions

import os
import requests
from typing import List, Dict, Optional, Generator, Tuple
import json
from ..utils import get_logger
logger = get_logger(__name__)

class LLMClient:
    """Client for making LLM API calls via OpenRouter"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = None,
        base_url: str = None
    ):
        """
        Initialize LLM client
        
        Args:
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            model: Model identifier on OpenRouter
            base_url: OpenRouter API base URL
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter"
            )
        
        self.model = model
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Tuple[str, Dict]:
        """
        Generate LLM response from messages
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
            
        Returns:
            Generated text response
        """
        endpoint = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        logger.debug("LLM generate_response called (model=%s, stream=%s)", self.model, stream)
        logger.debug("Request payload: %s", {k: v for k, v in payload.items() if k != 'messages' or len(payload['messages'])})

        if stream:
            # Streaming endpoint yields parts; consume and join so callers
            # always receive a (content, token_info) tuple for consistency.
            parts = []
            for part in self._stream_response(endpoint, payload):
                # If the stream yields error messages as strings, include them
                parts.append(str(part))

            content = "".join(parts)
            token_info = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
            logger.debug("Streamed content length=%d", len(content))
            return content, token_info
        else:
            return self._standard_response(endpoint, payload)
    
    def _standard_response(self, endpoint: str, payload: Dict) -> Tuple[str, Dict]:
        """Make non-streaming API call and return (content, token_info)"""
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            # Try to extract content and usage info if available
            content = data['choices'][0]['message']['content']
            usage = data.get('usage', {}) if isinstance(data, dict) else {}

            token_info = {
                'input_tokens': usage.get('prompt_tokens', 0),
                'output_tokens': usage.get('completion_tokens', 0),
                'total_tokens': usage.get('total_tokens', 0)
            }

            logger.debug("LLM response received (tokens=%s)", token_info)
            return content, token_info

        except requests.exceptions.RequestException as e:
            logger.exception("RequestException when calling LLM API")
            return f"Error calling LLM API: {str(e)}", {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
        except (KeyError, IndexError, TypeError) as e:
            logger.exception("Error parsing LLM response")
            return f"Error parsing LLM response: {str(e)}", {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
    
    def _stream_response(self, endpoint: str, payload: Dict) -> Generator[str, None, None]:
        """Make streaming API call (yields tokens as they arrive)"""
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        
                        if data_str == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            yield f"Error streaming from LLM API: {str(e)}"
    
    def build_prompt_with_context(
        self,
        user_message: str,
        memories: List[Dict],
        knowledge: List[Dict],
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build messages array with context from memories and knowledge

        Args:
            user_message: Current user message
            memories: Relevant past conversations
            knowledge: Relevant knowledge base entries
            system_prompt: Optional custom system prompt

        Returns:
            List of message dictionaries for API call
        """
        # Load system prompt from config or use default
        if system_prompt is None:
            try:
                from .config import _toml_config
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
            except ImportError:
                # Fallback if config loading fails
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

        # Debug logging to show what's being sent to the model
        logger.debug("=== PROMPT BEING SENT TO MODEL ===")
        for i, msg in enumerate(messages):
            logger.debug(f"Message {i+1} ({msg['role']}): {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}")
        logger.debug("=== END PROMPT ===")

        return messages
