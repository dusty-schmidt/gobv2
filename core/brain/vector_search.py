"""
Vector search utilities for the communal brain
"""

import math
from typing import List


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors

    Args:
        a: First vector
        b: Second vector

    Returns:
        Cosine similarity score between 0 and 1
    """
    if len(a) != len(b):
        raise ValueError(f"Vector dimensions don't match: {len(a)} vs {len(b)}")

    # Calculate dot product
    dot_product = sum(x * y for x, y in zip(a, b))

    # Calculate magnitudes
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))

    # Avoid division by zero
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    # Calculate cosine similarity
    similarity = dot_product / (magnitude_a * magnitude_b)

    # Normalize to 0-1 range (cosine similarity is -1 to 1)
    return (similarity + 1) / 2


def euclidean_distance(a: List[float], b: List[float]) -> float:
    """
    Calculate Euclidean distance between two vectors

    Args:
        a: First vector
        b: Second vector

    Returns:
        Euclidean distance
    """
    if len(a) != len(b):
        raise ValueError(f"Vector dimensions don't match: {len(a)} vs {len(b)}")

    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def manhattan_distance(a: List[float], b: List[float]) -> float:
    """
    Calculate Manhattan distance between two vectors

    Args:
        a: First vector
        b: Second vector

    Returns:
        Manhattan distance
    """
    if len(a) != len(b):
        raise ValueError(f"Vector dimensions don't match: {len(a)} vs {len(b)}")

    return sum(abs(x - y) for x, y in zip(a, b))


def find_similar_vectors(query: List[float], vectors: List[List[float]],
                        top_k: int = 5, similarity_func = cosine_similarity) -> List[tuple]:
    """
    Find the most similar vectors to a query vector

    Args:
        query: Query vector
        vectors: List of vectors to search
        top_k: Number of most similar vectors to return
        similarity_func: Function to calculate similarity

    Returns:
        List of (index, similarity_score) tuples, sorted by similarity (descending)
    """
    similarities = []

    for i, vector in enumerate(vectors):
        similarity = similarity_func(query, vector)
        similarities.append((i, similarity))

    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:top_k]


def normalize_vector(vector: List[float]) -> List[float]:
    """
    Normalize a vector to unit length

    Args:
        vector: Input vector

    Returns:
        Normalized vector
    """
    magnitude = math.sqrt(sum(x * x for x in vector))

    if magnitude == 0:
        return vector  # Avoid division by zero

    return [x / magnitude for x in vector]


def vector_magnitude(vector: List[float]) -> float:
    """
    Calculate the magnitude (length) of a vector

    Args:
        vector: Input vector

    Returns:
        Vector magnitude
    """
    return math.sqrt(sum(x * x for x in vector))


def dot_product(a: List[float], b: List[float]) -> float:
    """
    Calculate dot product of two vectors

    Args:
        a: First vector
        b: Second vector

    Returns:
        Dot product
    """
    if len(a) != len(b):
        raise ValueError(f"Vector dimensions don't match: {len(a)} vs {len(b)}")

    return sum(x * y for x, y in zip(a, b))