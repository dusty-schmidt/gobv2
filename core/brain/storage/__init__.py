"""
Storage module for the communal brain
"""

from .interfaces import StorageBackend, StorageBackendProtocol
from .config import StorageConfig
from .abstraction import StorageAbstraction
from .backends.sqlite import SQLiteBackend

__all__ = [
    'StorageBackend',
    'StorageBackendProtocol',
    'StorageConfig',
    'StorageAbstraction',
    'SQLiteBackend'
]