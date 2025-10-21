"""
OpenAI-compatible embeddings client for the embedding microservice
Drop-in replacement for OpenAI/LlamaCpp embeddings
"""
import os
import requests
from typing import List, Optional
import logging
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)


class EmbeddingServiceClient:
    """
    Client for the embedding microservice
    Compatible with OpenAI Embeddings API
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 3000  # 50 minutes - increased 10x for large document batches
    ):
        """
        Initialize client

        Args:
            base_url: Service URL (default: http://localhost:8001)
            timeout: Request timeout in seconds (default: 3000 = 50 minutes)
        """
        self.base_url = base_url or os.environ.get(
            "EMBEDDING_SERVICE_URL",
            "http://localhost:8001"
        )
        self.timeout = timeout

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings (synchronous)
        Uses OpenAI-compatible /v1/embeddings endpoint

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = requests.post(
                f"{self.base_url}/v1/embeddings",
                json={"input": texts, "model": "snowflake-arctic-embed"},
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            # Extract embeddings from OpenAI-format response
            return [item["embedding"] for item in result["data"]]
        except Exception as e:
            logger.error(f"Embedding service error: {e}")
            raise

    def create_embeddings(
        self,
        input: str | List[str],
        model: str = "snowflake-arctic-embed"
    ) -> dict:
        """
        OpenAI-compatible embeddings endpoint

        Args:
            input: Text or list of texts
            model: Model name (ignored)

        Returns:
            OpenAI-formatted response
        """
        try:
            response = requests.post(
                f"{self.base_url}/v1/embeddings",
                json={"input": input, "model": model},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Embedding service error: {e}")
            raise

    def health_check(self) -> dict:
        """Check service health"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as e:
            logger.error(f"Health check timeout: {e}")
            return {"status": "timeout", "error": str(e)}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Health check connection failed: {e}")
            return {"status": "unavailable", "error": str(e)}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}


class OpenAICompatibleEmbeddings(Embeddings):
    """
    OpenAI Embeddings API compatible wrapper
    Can be used as drop-in replacement for OpenAI embeddings
    Inherits from LangChain's Embeddings base class for full compatibility
    """

    def __init__(self, base_url: Optional[str] = None):
        """Initialize with service URL"""
        super().__init__()
        self.client = EmbeddingServiceClient(base_url=base_url)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """LangChain-compatible: embed multiple documents"""
        return self.client.embed(texts)

    def embed_query(self, text: str) -> List[float]:
        """LangChain-compatible: embed single query"""
        return self.client.embed([text])[0]


# For backward compatibility
def create_embeddings_client(base_url: Optional[str] = None) -> EmbeddingServiceClient:
    """Factory function to create client"""
    return EmbeddingServiceClient(base_url=base_url)
