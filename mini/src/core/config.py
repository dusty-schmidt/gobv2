# File: chatbot_v2/config.py
# Role: Central configuration for chatbot settings
# Loads configuration from config.toml with fallback defaults

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older Python


def load_config() -> dict:
    """Load configuration from config.toml file"""
    config_path = Path(__file__).parent.parent.parent / "config.toml"

    if config_path.exists():
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    return {}


# Load configuration from TOML
_toml_config = load_config()

@dataclass
class EmbeddingsConfig:
    """Configuration for OpenAI embeddings"""
    api_key: Optional[str] = None
    model_name: str = None  # Will be set from TOML or default
    embedding_dim: int = None  # Will be auto-set based on model

    def __post_init__(self):
        # Load from TOML config or use defaults
        embeddings_config = _toml_config.get("embeddings", {})

        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")

        if self.model_name is None:
            self.model_name = embeddings_config.get("model_name", "text-embedding-3-small")

        if self.embedding_dim is None:
            self.embedding_dim = embeddings_config.get("embedding_dim", 1536)

        # Auto-set dimensions based on model if not explicitly set
        if "3-small" in self.model_name:
            self.embedding_dim = 1536
        elif "3-large" in self.model_name:
            self.embedding_dim = 3072
        elif "ada-002" in self.model_name:
            self.embedding_dim = 1536

@dataclass
class LLMConfig:
    """Configuration for LLM API calls"""
    api_key: Optional[str] = None
    model: str = None  # Will be set from TOML
    base_url: str = None  # Will be set from TOML
    temperature: float = None  # Will be set from TOML
    max_tokens: int = None  # Will be set from TOML

    def __post_init__(self):
        # Load from TOML config or use defaults
        llm_config = _toml_config.get("llm", {})

        if self.api_key is None:
            self.api_key = os.getenv("OPENROUTER_API_KEY")

        if self.model is None:
            self.model = llm_config.get("model", "openai/gpt-oss-120b")

        if self.base_url is None:
            self.base_url = llm_config.get("base_url", "https://openrouter.ai/api/v1")

        if self.temperature is None:
            self.temperature = llm_config.get("temperature", 1.0)

        if self.max_tokens is None:
            self.max_tokens = llm_config.get("max_tokens", 10000)

@dataclass
class DatabaseConfig:
    """Configuration for SQLite database with vector support"""
    db_path: str = None  # Will be set from TOML
    enable_wal: bool = None  # Will be set from TOML
    cache_size: int = None  # Will be set from TOML

    def __post_init__(self):
        # Load from TOML config or use defaults
        db_config = _toml_config.get("database", {})

        if self.db_path is None:
            self.db_path = db_config.get("db_path", "chatbot.db")

        if self.enable_wal is None:
            self.enable_wal = db_config.get("enable_wal", True)

        if self.cache_size is None:
            self.cache_size = db_config.get("cache_size", -64000)

@dataclass
class MemoryConfig:
    """Configuration for memory retrieval"""
    top_k: int = None  # Will be set from TOML
    similarity_threshold: float = None  # Will be set from TOML
    max_conversation_history: int = None  # Will be set from TOML

    def __post_init__(self):
        # Load from TOML config or use defaults
        memory_config = _toml_config.get("memory", {})

        if self.top_k is None:
            self.top_k = memory_config.get("top_k", 3)

        if self.similarity_threshold is None:
            self.similarity_threshold = memory_config.get("similarity_threshold", 0.3)

        if self.max_conversation_history is None:
            self.max_conversation_history = memory_config.get("max_conversation_history", 1000)

@dataclass
class KnowledgeConfig:
    """Configuration for knowledge base"""
    chunk_size: int = None  # Will be set from TOML
    top_k: int = None  # Will be set from TOML
    similarity_threshold: float = None  # Will be set from TOML
    docs_directory: str = None  # Will be set from TOML

    def __post_init__(self):
        # Load from TOML config or use defaults
        knowledge_config = _toml_config.get("knowledge", {})

        if self.chunk_size is None:
            self.chunk_size = knowledge_config.get("chunk_size", 500)

        if self.top_k is None:
            self.top_k = knowledge_config.get("top_k", 2)

        if self.similarity_threshold is None:
            self.similarity_threshold = knowledge_config.get("similarity_threshold", 0.4)

        if self.docs_directory is None:
            self.docs_directory = knowledge_config.get("docs_directory", "knowledge_docs/")

@dataclass
class ChatbotConfig:
    """Main configuration aggregator"""
    embeddings: EmbeddingsConfig = None
    llm: LLMConfig = None
    database: DatabaseConfig = None
    memory: MemoryConfig = None
    knowledge: KnowledgeConfig = None

    def __post_init__(self):
        if self.embeddings is None:
            self.embeddings = EmbeddingsConfig()
        if self.llm is None:
            self.llm = LLMConfig()
        if self.database is None:
            self.database = DatabaseConfig()
        if self.memory is None:
            self.memory = MemoryConfig()
        if self.knowledge is None:
            self.knowledge = KnowledgeConfig()

# Default configuration instance
default_config = ChatbotConfig()
