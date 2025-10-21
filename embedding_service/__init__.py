"""
Embedding Microservice

OpenAI-compatible embedding API service using LlamaCpp.
Provides a single-instance embedding service to prevent GPU OOM.

Usage:
    # Start service
    $ python embedding_service/server.py

    # Or use startup script
    $ ./embedding_service/start.sh

    # Use client
    from embedding_service.client import EmbeddingServiceClient
    client = EmbeddingServiceClient()
    embeddings = client.embed(["text1", "text2"])
"""

__version__ = "1.0.0"
__all__ = ["EmbeddingServiceClient", "OpenAICompatibleEmbeddings"]

from .client import EmbeddingServiceClient, OpenAICompatibleEmbeddings

__all__ = ["EmbeddingServiceClient", "OpenAICompatibleEmbeddings"]
