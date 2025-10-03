"""
Communal Brain Module

This module implements the shared intelligence system for the chatbot framework.
All devices contribute to and draw from the same knowledge and memory pool.
"""

from .storage import StorageAbstraction, StorageConfig
from .models import DeviceContext, MemoryItem, KnowledgeItem, DeviceTier, DeviceStatus
from .brain import CommunalBrain, BrainConfig
from .vector_search import cosine_similarity, euclidean_distance

__all__ = [
    'CommunalBrain',
    'BrainConfig',
    'StorageAbstraction',
    'StorageConfig',
    'DeviceContext',
    'MemoryItem',
    'KnowledgeItem',
    'DeviceTier',
    'DeviceStatus',
    'cosine_similarity',
    'euclidean_distance'
]