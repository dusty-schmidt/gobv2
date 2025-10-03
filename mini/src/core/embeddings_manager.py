# File: core/embeddings_manager.py
# Role: Handles text-to-vector conversion using OpenAI API
# Simplified version for communal brain integration

import numpy as np
from typing import List
from openai import OpenAI
import time
from ..utils import get_logger
logger = get_logger(__name__)

class EmbeddingsManager:
    """Manages embeddings generation using OpenAI API"""

    def __init__(self, api_key: str, model_name: str = 'text-embedding-3-small', embedding_dim: int = 1536):
        """
        Initialize embeddings manager with OpenAI client

        Args:
            api_key: OpenAI API key
            model_name: OpenAI embedding model (default: text-embedding-3-small)
            embedding_dim: Dimension of embeddings (1536 for small, 3072 for large)
        """
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.embedding_dim = embedding_dim

    def encode(self, text: str, retry_count: int = 3) -> np.ndarray:
        """
        Convert text to embedding vector using OpenAI API

        Args:
            text: Input text string
            retry_count: Number of retries on failure

        Returns:
            Numpy array representing the embedding
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.embedding_dim)

        for attempt in range(retry_count):
            try:
                response = self.client.embeddings.create(
                    input=text,
                    model=self.model_name
                )
                embedding = np.array(response.data[0].embedding, dtype=np.float32)
                return embedding

            except Exception as e:
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning("Embedding API error (attempt %d/%d): %s", attempt + 1, retry_count, e)
                    logger.info("Retrying in %ds...", wait_time)
                    time.sleep(wait_time)
                else:
                    logger.error("Failed to generate embedding after %d attempts: %s", retry_count, e)
                    raise