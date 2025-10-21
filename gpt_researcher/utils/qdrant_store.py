"""
Qdrant Vector Store Utilities
This module provides basic Qdrant client initialization and collection management.
"""
import os
import hashlib
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

        logger.debug(
            f"🔵 [QDRANT_INIT] QdrantStore initialized: host={self.host}, port={self.port}, collection={self.collection_name}")

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
                logger.info(
                    f"Collection '{self.collection_name}' already exists")
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
            logger.info(
                f"Collection '{self.collection_name}' created successfully")
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
            logger.info(
                f"Collection '{self.collection_name}' deleted successfully")
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
        Uses content-based integer IDs to prevent duplicates and ensure idempotency.

        Args:
            texts: List of text content
            embeddings: List of embedding vectors
            metadata: Optional list of metadata dictionaries for each document

        Returns:
            bool: True if successful
        """
        if len(texts) != len(embeddings):
            logger.error(
                f"Mismatch: {len(texts)} texts but {len(embeddings)} embeddings")
            return False

        if not texts:
            logger.warning("No documents to add to Qdrant")
            return True

        try:
            logger.info(
                f"📥 Adding {len(texts)} documents to Qdrant collection '{self.collection_name}'")

            # Get current collection size for logging
            collection_info = self.get_collection_info()
            points_before = collection_info.get(
                'points_count', 0) if collection_info else 0
            logger.info(f"📊 Collection size BEFORE: {points_before} points")

            points = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                # Generate deterministic integer ID based on content hash + URL (if available)
                # This ensures same content always gets same ID, preventing duplicates
                content_hash_input = text
                if metadata and i < len(metadata) and 'url' in metadata[i]:
                    content_hash_input = f"{metadata[i]['url']}:{text}"

                # Use SHA256 and take first 8 bytes as integer ID
                # This gives us 2^64 possible IDs with very low collision probability
                content_hash = hashlib.sha256(
                    content_hash_input.encode('utf-8')).digest()
                point_id = int.from_bytes(content_hash[:8], byteorder='big')

                payload = {"text": text}
                if metadata and i < len(metadata):
                    payload.update(metadata[i])

                # Log point details
                url_preview = ""
                if metadata and i < len(metadata) and 'url' in metadata[i]:
                    url_preview = metadata[i].get('url', '')[:60]
                    logger.debug(
                        f"  Point {i}: ID={point_id}, URL={url_preview}")
                else:
                    logger.debug(
                        f"  Point {i}: ID={point_id}, text_len={len(text)}")

                point = self._point_struct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
                points.append(point)

            logger.info(f"📤 Upserting {len(points)} points to Qdrant...")
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            # Get collection size after upsert
            collection_info_after = self.get_collection_info()
            points_after = collection_info_after.get(
                'points_count', 0) if collection_info_after else 0
            points_added = points_after - points_before

            logger.info(
                f"📊 Collection size AFTER: {points_after} points (added {points_added} new)")
            logger.info(
                f"✅ Successfully upserted {len(points)} documents to Qdrant collection")
            return True

        except Exception as e:
            logger.error(
                f"❌ Error adding documents to Qdrant: {type(e).__name__}: {e}")
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

    def search_by_metadata(
        self,
        filter_dict: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for documents by metadata filter (e.g., URL, timestamp).

        Args:
            filter_dict: Dictionary of metadata key-value pairs to filter by
            limit: Maximum number of results to return

        Returns:
            List of matching documents with content and metadata
        """
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            # Build Qdrant filter conditions
            conditions = []
            for key, value in filter_dict.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )

            # Search with metadata filter (no vector search, just filter)
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(must=conditions),
                limit=limit,
                with_payload=True,
                with_vectors=False
            )

            results = []
            # scroll returns (points, next_offset)
            for point in search_result[0]:
                result = {
                    "content": point.payload.get("text", ""),
                    "metadata": {k: v for k, v in point.payload.items() if k != "text"},
                    "id": point.id
                }
                results.append(result)

            logger.info(
                f"Metadata search returned {len(results)} results for filter {filter_dict}")
            return results

        except Exception as e:
            logger.error(f"Error searching by metadata: {e}")
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
