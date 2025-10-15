"""
Qdrant Vector Store Utilities
This module provides basic Qdrant client initialization and collection management.
"""
import os
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


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
            from qdrant_client.models import Distance, VectorParams, PointStruct
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
        self._point_struct = PointStruct
        self._point_counter = 0
    
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
                logger.info(f"Collection '{self.collection_name}' already exists")
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
            logger.info(f"Collection '{self.collection_name}' created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
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
            logger.error(f"Error checking collection: {e}")
            return False
    
    def delete_collection(self) -> bool:
        """
        Delete the collection.
        
        Returns:
            bool: True if collection was deleted, False otherwise
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Collection '{self.collection_name}' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Add documents with embeddings to the collection.
        
        Args:
            texts: List of text content
            embeddings: List of embedding vectors
            metadata: Optional list of metadata dictionaries for each document
            
        Returns:
            bool: True if successful
        """
        if len(texts) != len(embeddings):
            logger.error("Number of texts and embeddings must match")
            return False
        
        if not texts:
            logger.warning("No documents to add")
            return True
        
        try:
            points = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                point_id = self._point_counter
                self._point_counter += 1
                
                payload = {"text": text}
                if metadata and i < len(metadata):
                    payload.update(metadata[i])
                
                point = self._point_struct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Added {len(points)} documents to collection")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using a query embedding.
        
        Args:
            query_embedding: Query vector
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (optional)
            
        Returns:
            List of search results with text, metadata, and scores
        """
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            results = []
            for hit in search_result:
                result = {
                    "text": hit.payload.get("text", ""),
                    "score": hit.score,
                    "metadata": {k: v for k, v in hit.payload.items() if k != "text"}
                }
                results.append(result)
            
            logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching collection: {e}")
            return []
    
    def get_collection_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the collection.
        
        Returns:
            Dictionary with collection information or None
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.name if hasattr(collection_info.config, 'name') else self.collection_name,
                "vector_size": collection_info.config.params.vectors.size,
                "points_count": collection_info.points_count if hasattr(collection_info, 'points_count') else 0
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None
