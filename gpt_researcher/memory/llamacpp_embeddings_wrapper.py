"""
Thread-safe wrapper for LlamaCpp embeddings to prevent CUDA errors during concurrent access.

This module provides a wrapper around LangChain's LlamaCppEmbeddings that adds global lock
protection to prevent concurrent GPU operations that cause "llama_decode returned -1" errors.
"""

import threading
import logging
from typing import List
from langchain_community.embeddings import LlamaCppEmbeddings

logger = logging.getLogger(__name__)

# Global lock to prevent concurrent LlamaCpp operations
# This lock is shared across ALL instances of ThreadSafeLlamaCppEmbeddings
_LLAMACPP_GLOBAL_LOCK = threading.Lock()


class ThreadSafeLlamaCppEmbeddings(LlamaCppEmbeddings):
    """
    Thread-safe wrapper for LlamaCppEmbeddings that prevents concurrent GPU access.

    The LlamaCpp library has issues with concurrent GPU operations, causing errors like:
    "llama_decode returned -1". This wrapper ensures only one embedding operation
    runs at a time across ALL instances.

    Features:
    - Global lock prevents ANY concurrent LlamaCpp operations system-wide
    - Inherits all functionality from LangChain's LlamaCppEmbeddings
    - Transparent drop-in replacement - same API as LlamaCppEmbeddings
    - Debug logging to track lock acquisition and GPU operations

    Usage:
        embeddings = ThreadSafeLlamaCppEmbeddings(
            model_path="/path/to/model.gguf",
            n_ctx=512,
            n_threads=None
        )
        vectors = embeddings.embed_documents(["text1", "text2"])
    """

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents with global lock protection.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (one per text)

        Note:
            Uses global lock to prevent concurrent GPU access across all instances.
            Embeds documents ONE AT A TIME to avoid llama.cpp batch processing bugs.
        """
        logger.debug(
            f"🔒 Acquiring global GPU lock for embedding {len(texts)} documents...")

        with _LLAMACPP_GLOBAL_LOCK:
            logger.debug("✅ GPU lock acquired, generating embeddings...")
            try:
                # Process documents ONE AT A TIME to avoid llama.cpp batching issues
                # that cause "llama_decode returned -1" errors
                results = []
                for i, text in enumerate(texts):
                    logger.debug(
                        f"   Embedding document {i+1}/{len(texts)}...")
                    # Call parent's embed_query for single document
                    embedding = super().embed_query(text)
                    results.append(embedding)

                logger.debug(
                    f"✅ Successfully generated {len(results)} embeddings")
                return results
            except Exception as e:
                logger.error(f"❌ Error generating embeddings: {e}")
                raise
            finally:
                logger.debug("🔓 Releasing GPU lock")

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text with global lock protection.

        Args:
            text: Query text to embed

        Returns:
            Single embedding vector

        Note:
            Uses global lock to prevent concurrent GPU access across all instances
        """
        logger.debug("🔒 Acquiring global GPU lock for query embedding...")

        with _LLAMACPP_GLOBAL_LOCK:
            logger.debug("✅ GPU lock acquired, generating query embedding...")
            try:
                result = super().embed_query(text)
                logger.debug("✅ Successfully generated query embedding")
                return result
            except Exception as e:
                logger.error(f"❌ Error generating query embedding: {e}")
                raise
            finally:
                logger.debug("🔓 Releasing GPU lock")
