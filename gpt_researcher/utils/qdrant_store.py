"""
Qdrant Vector Store Utilities
This module provides basic Qdrant client initialization and collection management.
"""
import os
from typing import Optional


class QdrantStore:
    """
    Basic Qdrant client wrapper for vector storage operations.
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        api_key: Optional[str] = None,
        collection_name: str = "research_documents"
    ):
        """
        Initialize Qdrant client.
        
        Args:
            host: Qdrant server host (defaults to QDRANT_HOST env var or localhost)
            port: Qdrant server port (defaults to QDRANT_PORT env var or 6333)
            api_key: Qdrant API key (defaults to QDRANT_API_KEY env var)
            collection_name: Name of the collection to use
        """
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
        except ImportError:
            raise ImportError(
                "qdrant-client is not installed. "
                "Please install it with: pip install -U qdrant-client"
            )
        
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = port or int(os.getenv("QDRANT_PORT", "6333"))
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name
        
        # Initialize Qdrant client
        if self.api_key:
            self.client = QdrantClient(
                host=self.host,
                port=self.port,
                api_key=self.api_key
            )
        else:
            self.client = QdrantClient(
                host=self.host,
                port=self.port
            )
        
        self._distance = Distance
        self._vector_params = VectorParams
    
    def create_collection(
        self,
        vector_size: int = 1536,
        distance: str = "COSINE"
    ) -> bool:
        """
        Create a new collection if it doesn't exist.
        
        Args:
            vector_size: Dimension of the vectors (default 1536 for OpenAI embeddings)
            distance: Distance metric to use (COSINE, EUCLID, or DOT)
            
        Returns:
            bool: True if collection was created, False if it already exists
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            if any(col.name == self.collection_name for col in collections):
                print(f"Collection '{self.collection_name}' already exists")
                return False
            
            # Create collection
            distance_metric = getattr(self._distance, distance)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=self._vector_params(
                    size=vector_size,
                    distance=distance_metric
                )
            )
            print(f"Collection '{self.collection_name}' created successfully")
            return True
        except Exception as e:
            print(f"Error creating collection: {e}")
            raise
    
    def collection_exists(self) -> bool:
        """
        Check if the collection exists.
        
        Returns:
            bool: True if collection exists, False otherwise
        """
        try:
            collections = self.client.get_collections().collections
            return any(col.name == self.collection_name for col in collections)
        except Exception as e:
            print(f"Error checking collection: {e}")
            return False
    
    def delete_collection(self) -> bool:
        """
        Delete the collection.
        
        Returns:
            bool: True if collection was deleted, False otherwise
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            print(f"Collection '{self.collection_name}' deleted successfully")
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False
