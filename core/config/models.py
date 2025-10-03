"""
Global configuration models for the gob ecosystem.
Centralized configuration that all chatbots and agents can use.
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older Python


def load_global_config() -> dict:
    """Load global configuration from gob/.env and config files"""
    config = {}

    # Load from .env file if it exists
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=env_path)
        except ImportError:
            pass  # dotenv not available, rely on environment variables

    # Load from config.toml if it exists (for future use)
    config_path = Path(__file__).parent.parent.parent / 'config.toml'
    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                toml_config = tomllib.load(f)
                config.update(toml_config)
        except Exception:
            pass  # TOML loading failed, continue with defaults

    return config


@dataclass
class LLMConfig:
    """Global LLM configuration for all chatbots and agents"""
    api_key: Optional[str] = None
    model: str = "openai/gpt-oss-120b"
    base_url: str = "https://openrouter.ai/api/v1"
    temperature: float = 1.0
    max_tokens: int = 10000
    timeout: int = 60

    def __post_init__(self):
        # Load from environment variables with fallbacks
        if self.api_key is None:
            self.api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

        # Override with environment variables if set
        if os.getenv("LLM_MODEL"):
            self.model = os.getenv("LLM_MODEL")
        if os.getenv("LLM_BASE_URL"):
            self.base_url = os.getenv("LLM_BASE_URL")
        if os.getenv("LLM_TEMPERATURE"):
            try:
                self.temperature = float(os.getenv("LLM_TEMPERATURE"))
            except ValueError:
                pass
        if os.getenv("LLM_MAX_TOKENS"):
            try:
                self.max_tokens = int(os.getenv("LLM_MAX_TOKENS"))
            except ValueError:
                pass
        if os.getenv("LLM_TIMEOUT"):
            try:
                self.timeout = int(os.getenv("LLM_TIMEOUT"))
            except ValueError:
                pass


@dataclass
class EmbeddingsConfig:
    """Global embeddings configuration for all chatbots and agents"""
    api_key: Optional[str] = None
    model_name: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    timeout: int = 30

    def __post_init__(self):
        # Load from environment variables
        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")

        # Override with environment variables if set
        if os.getenv("EMBEDDINGS_MODEL"):
            self.model_name = os.getenv("EMBEDDINGS_MODEL")
        if os.getenv("EMBEDDINGS_DIM"):
            try:
                self.embedding_dim = int(os.getenv("EMBEDDINGS_DIM"))
            except ValueError:
                pass
        if os.getenv("EMBEDDINGS_TIMEOUT"):
            try:
                self.timeout = int(os.getenv("EMBEDDINGS_TIMEOUT"))
            except ValueError:
                pass

        # Auto-set dimensions based on model if not explicitly set
        if "3-small" in self.model_name:
            self.embedding_dim = 1536
        elif "3-large" in self.model_name:
            self.embedding_dim = 3072
        elif "ada-002" in self.model_name:
            self.embedding_dim = 1536


@dataclass
class StorageConfig:
    """Storage configuration for the communal brain"""
    primary_backend: str = "local"
    local_db_path: str = "data/communal_brain.db"
    remote_host: Optional[str] = None
    remote_port: int = 5432
    remote_database: Optional[str] = None
    remote_user: Optional[str] = None
    remote_password: Optional[str] = None
    cache_host: Optional[str] = None
    cache_port: Optional[int] = None
    cache_type: str = "redis"
    enable_wal: bool = True
    cache_size: int = -64000
    connection_pool_size: int = 10

    def __post_init__(self):
        # Load from environment variables
        if os.getenv("STORAGE_BACKEND"):
            self.primary_backend = os.getenv("STORAGE_BACKEND")
        if os.getenv("DB_PATH"):
            self.local_db_path = os.getenv("DB_PATH")

        # Remote config
        if os.getenv("DB_HOST"):
            self.remote_host = os.getenv("DB_HOST")
        if os.getenv("DB_PORT"):
            try:
                self.remote_port = int(os.getenv("DB_PORT"))
            except ValueError:
                pass
        if os.getenv("DB_NAME"):
            self.remote_database = os.getenv("DB_NAME")
        if os.getenv("DB_USER"):
            self.remote_user = os.getenv("DB_USER")
        if os.getenv("DB_PASSWORD"):
            self.remote_password = os.getenv("DB_PASSWORD")

        # Cache config
        if os.getenv("CACHE_HOST"):
            self.cache_host = os.getenv("CACHE_HOST")
        if os.getenv("CACHE_PORT"):
            try:
                self.cache_port = int(os.getenv("CACHE_PORT"))
            except ValueError:
                pass
        if os.getenv("CACHE_TYPE"):
            self.cache_type = os.getenv("CACHE_TYPE")

        # Validation
        if self.primary_backend not in ['local', 'remote', 'cache']:
            raise ValueError(f"Invalid primary_backend: {self.primary_backend}")
        if self.cache_type not in ['redis', 'memcached']:
            raise ValueError(f"Invalid cache_type: {self.cache_type}")


@dataclass
class GlobalConfig:
    """Main global configuration aggregator for the gob ecosystem"""
    llm: LLMConfig = None
    embeddings: EmbeddingsConfig = None
    storage: StorageConfig = None

    def __post_init__(self):
        if self.llm is None:
            self.llm = LLMConfig()
        if self.embeddings is None:
            self.embeddings = EmbeddingsConfig()
        if self.storage is None:
            self.storage = StorageConfig()


# Global configuration instance
global_config = GlobalConfig()