"""
Embeddings utility for generating vector embeddings
Supports sentence-transformers and OpenAI embeddings based on configuration
"""
import os
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


class EmbeddingsGenerator:
    """
    Generates embeddings for text using various embedding models.
    Supports sentence-transformers (local) and OpenAI (API-based) embeddings.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embeddings generator.
        
        Args:
            model_name: Name of the embedding model to use.
                       Can be:
                       - sentence-transformers model (e.g., "sentence-transformers/all-MiniLM-L6-v2")
                       - OpenAI model (e.g., "openai:text-embedding-3-small")
        """
        self.model_name = model_name
        self.model = None
        self.model_type = None
        
        # Determine model type and initialize
        if model_name.startswith("openai:"):
            self._init_openai_model()
        elif model_name.startswith("sentence-transformers/"):
            self._init_sentence_transformer()
        else:
            # Default to sentence-transformers
            self.model_name = f"sentence-transformers/{model_name}"
            self._init_sentence_transformer()
    
    def _init_openai_model(self):
        """Initialize OpenAI embeddings model"""
        try:
            from openai import OpenAI
            self.model_type = "openai"
            # Extract model name after "openai:" prefix
            openai_model = self.model_name.split(":", 1)[1]
            self.openai_model_name = openai_model
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not found, OpenAI embeddings will not work")
            self.model = OpenAI(api_key=api_key)
            logger.info(f"Initialized OpenAI embeddings with model: {openai_model}")
        except ImportError:
            logger.error("OpenAI package not installed. Please install with: pip install openai")
            raise
    
    def _init_sentence_transformer(self):
        """Initialize sentence-transformers model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model_type = "sentence-transformers"
            # Extract model name after "sentence-transformers/" prefix
            model_name = self.model_name.split("/", 1)[1] if "/" in self.model_name else self.model_name
            self.model = SentenceTransformer(model_name)
            logger.info(f"Initialized sentence-transformers with model: {model_name}")
        except ImportError:
            logger.error("sentence-transformers package not installed. Please install with: pip install sentence-transformers")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding generation")
            return []
        
        try:
            if self.model_type == "openai":
                response = self.model.embeddings.create(
                    input=text,
                    model=self.openai_model_name
                )
                return response.data[0].embedding
            
            elif self.model_type == "sentence-transformers":
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            
            else:
                logger.error(f"Unknown model type: {self.model_type}")
                return []
                
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            logger.warning("No valid texts provided for embedding generation")
            return []
        
        try:
            if self.model_type == "openai":
                # OpenAI supports batch embedding generation
                response = self.model.embeddings.create(
                    input=valid_texts,
                    model=self.openai_model_name
                )
                return [item.embedding for item in response.data]
            
            elif self.model_type == "sentence-transformers":
                embeddings = self.model.encode(valid_texts, convert_to_numpy=True)
                return embeddings.tolist()
            
            else:
                logger.error(f"Unknown model type: {self.model_type}")
                return []
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors produced by this model.
        
        Returns:
            Integer dimension of embeddings
        """
        if self.model_type == "openai":
            # OpenAI embedding dimensions by model
            dimensions = {
                "text-embedding-3-small": 1536,
                "text-embedding-3-large": 3072,
                "text-embedding-ada-002": 1536,
            }
            return dimensions.get(self.openai_model_name, 1536)
        
        elif self.model_type == "sentence-transformers":
            # Get dimension from the model
            return self.model.get_sentence_embedding_dimension()
        
        return 384  # Default fallback dimension


def create_embeddings_generator(config=None) -> EmbeddingsGenerator:
    """
    Create an embeddings generator from configuration.
    
    Args:
        config: Configuration object with EMBEDDING_MODEL attribute
        
    Returns:
        EmbeddingsGenerator instance
    """
    if config and hasattr(config, 'embedding_model'):
        model_name = config.embedding_model
    else:
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    return EmbeddingsGenerator(model_name)
