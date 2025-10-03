# src/__init__.py
# Bootstrap all main chatbot components for easy importing
# Updated for communal brain architecture - memory/knowledge now handled by gob/core/

from .core import Chatbot, ChatbotConfig, ChatHandler, LLMClient, EmbeddingsManager
from .utils import get_logger

__all__ = [
    'Chatbot',
    'ChatbotConfig',
    'ChatHandler',
    'LLMClient',
    'EmbeddingsManager',
    'get_logger'
]