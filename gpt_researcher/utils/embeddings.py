"""
Embeddings utility for generating vector embeddings
Supports sentence-transformers and OpenAI embeddings based on configuration
"""
import os
from typing import List, Union
import logging
import threading

logger = logging.getLogger(__name__)

# Global lock for all LlamaCpp embedding operations across all instances
# This prevents concurrent GPU access that causes CUDA errors
_LLAMACPP_GLOBAL_LOCK = threading.Lock()

# Singleton cache for LlamaCpp model instances (prevents multiple models in GPU memory)
# Key: model_path, Value: model_instance
# This ensures only ONE model instance exists system-wide, preventing GPU OOM
_LLAMACPP_MODEL_CACHE = {}
_MODEL_CACHE_LOCK = threading.Lock()


class EmbeddingsGenerator:
    """
    Generates embeddings for text using various embedding models.
    Supports sentence-transformers (local), OpenAI (API-based), and LlamaCpp (local) embeddings.

    For LlamaCpp models, embeddings are processed sequentially using a GLOBAL lock to prevent
    GPU memory issues and CUDA errors during concurrent processing across all instances.
    This ensures that only ONE embedding operation occurs at a time, regardless of how many
    EmbeddingsGenerator instances exist or how many parallel requests are being processed.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embeddings generator.

        Args:
            model_name: Name of the embedding model to use.
                       Can be:
                       - sentence-transformers model (e.g., "sentence-transformers/all-MiniLM-L6-v2")
                       - OpenAI model (e.g., "openai:text-embedding-3-small")
                       - LlamaCpp model (e.g., "llamacpp:/path/to/model.gguf")
                       - Absolute path to GGUF file (auto-detected as LlamaCpp)
        """
        self.model_name = model_name
        self.model = None
        self.model_type = None

        # Determine model type and initialize
        if model_name.startswith("openai:"):
            self._init_openai_model()
        elif model_name.startswith("llamacpp:"):
            self._init_llamacpp_model()
        elif model_name.endswith(".gguf") or (os.path.isabs(model_name) and os.path.exists(model_name)):
            # Auto-detect GGUF files or absolute paths as LlamaCpp
            self.model_name = f"llamacpp:{model_name}"
            self._init_llamacpp_model()
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

            # Check if embedding microservice is enabled
            service_enabled = os.getenv(
                "EMBEDDING_SERVICE_ENABLED", "false").lower() == "true"
            service_url = os.getenv(
                "EMBEDDING_SERVICE_URL", "http://localhost:8001")

            if service_enabled:
                # Use embedding microservice (OpenAI-compatible)
                logger.info(f"Using embedding microservice at {service_url}")
                self.model = OpenAI(
                    api_key="not-needed",  # Microservice doesn't need API key
                    base_url=f"{service_url}/v1"
                )
            else:
                # Use real OpenAI API
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    logger.warning(
                        "OPENAI_API_KEY not found, OpenAI embeddings will not work")
                self.model = OpenAI(api_key=api_key)
                logger.info(
                    f"Initialized OpenAI embeddings with model: {openai_model}")
        except ImportError:
            logger.error(
                "OpenAI package not installed. Please install with: pip install openai")
            raise

    def _init_sentence_transformer(self):
        """Initialize sentence-transformers model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model_type = "sentence-transformers"
            # Extract model name after "sentence-transformers/" prefix
            model_name = self.model_name.split(
                "/", 1)[1] if "/" in self.model_name else self.model_name
            self.model = SentenceTransformer(model_name)
            logger.info(
                f"Initialized sentence-transformers with model: {model_name}")
        except ImportError:
            logger.error(
                "sentence-transformers package not installed. Please install with: pip install sentence-transformers")
            raise

    def _init_llamacpp_model(self):
        """Initialize LlamaCpp embeddings model with GPU support (singleton pattern)"""
        try:
            from llama_cpp import Llama
            self.model_type = "llamacpp"
            # Extract model path after "llamacpp:" prefix
            model_path = self.model_name.split(":", 1)[1]

            # Check if model file exists
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"Model path does not exist: {model_path}")

            # Use singleton cache to ensure only ONE model instance exists
            # This prevents multiple models from loading into GPU memory during deep research
            with _MODEL_CACHE_LOCK:
                if model_path not in _LLAMACPP_MODEL_CACHE:
                    logger.info(
                        f"🚀 Initializing LlamaCpp with GPU acceleration...")
                    logger.info(f"   Model: {os.path.basename(model_path)}")
                    logger.info(f"   GPU Layers: 25, Context: 8000 tokens")
                    logger.info(
                        f"   Creating SINGLETON instance (will be reused)")

                    # Get batch sizes from environment or use safe defaults
                    n_batch = int(os.environ.get("LLAMACPP_N_BATCH", "512"))
                    n_ubatch = int(os.environ.get("LLAMACPP_N_UBATCH", "512"))

                    # Initialize LlamaCpp model for embeddings with GPU support
                    # Snowflake Arctic: 25 GPU layers for stable performance
                    # 8000 context: Reliable context window size
                    model_instance = Llama(
                        model_path=model_path,
                        embedding=True,  # Enable embedding mode
                        verbose=False,
                        n_ctx=8000,  # 8K context window (stable configuration)
                        n_batch=n_batch,  # Batch size for prompt processing
                        # Batch size for embeddings (CRITICAL: must handle large texts)
                        n_ubatch=n_ubatch,
                        n_threads=None,  # Use all available threads
                        # 25 GPU layers (proven stable for Snowflake Arctic)
                        n_gpu_layers=25,
                    )
                    _LLAMACPP_MODEL_CACHE[model_path] = model_instance
                    logger.info(
                        f"✅ LlamaCpp initialized and cached successfully")
                else:
                    logger.info(f"♻️ Reusing cached LlamaCpp model instance")

                # Use the cached singleton instance
                self.model = _LLAMACPP_MODEL_CACHE[model_path]

        except ImportError:
            logger.error(
                "llama-cpp-python package not installed. Please install with: pip install llama-cpp-python")
            raise
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize LlamaCpp model: {e}")
            raise

    def _chunk_text(self, text: str, max_tokens: int = 6000) -> List[str]:
        """
        Chunk text into smaller pieces to avoid context window overflow.

        Args:
            text: Text to chunk
            max_tokens: Maximum tokens per chunk (conservative estimate: ~4 chars = 1 token)
                       Default 6000 for stable 8K context window (with safety margin)

        Returns:
            List of text chunks
        """
        if not text:
            return []

        # Conservative estimate: 4 characters ≈ 1 token
        max_chars = max_tokens * 4

        if len(text) <= max_chars:
            return [text]

        # Split into chunks at sentence boundaries when possible
        chunks = []
        current_chunk = ""

        # Split by sentences (rough approximation)
        sentences = text.replace('. ', '.|').replace(
            '? ', '?|').replace('! ', '!|').split('|')

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chars:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # If single sentence is too long, split by words
                if len(sentence) > max_chars:
                    words = sentence.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 <= max_chars:
                            temp_chunk += word + " "
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            temp_chunk = word + " "
                    if temp_chunk:
                        current_chunk = temp_chunk
                else:
                    current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        logger.info(
            f"Chunked text into {len(chunks)} pieces (original: {len(text)} chars)")
        return chunks

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

            elif self.model_type == "llamacpp":
                # Use queue-based sequential processing for LlamaCpp
                return self._generate_llamacpp_embedding_queued(text)

            else:
                logger.error(f"Unknown model type: {self.model_type}")
                return []

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    def _generate_llamacpp_embedding_queued(self, text: str) -> List[float]:
        """
        Generate LlamaCpp embedding using global lock for sequential processing.
        This prevents concurrent GPU access across ALL instances that can cause CUDA errors.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        # Use global lock to prevent ANY concurrent LlamaCpp operations
        logger.debug(
            f"🔒 Acquiring global GPU lock for embedding ({len(text)} chars)")
        with _LLAMACPP_GLOBAL_LOCK:
            logger.debug(f"✅ GPU lock acquired, processing embedding")
            try:
                # Chunk text if too long to avoid llama_decode errors
                chunks = self._chunk_text(text, max_tokens=6000)

                if len(chunks) == 1:
                    # Single chunk - process directly
                    embedding = self.model.embed(text)
                    if isinstance(embedding, list) and len(embedding) > 0:
                        if isinstance(embedding[0], list):
                            return embedding[0]
                        else:
                            return embedding
                    else:
                        logger.error(
                            f"Unexpected embedding structure from LlamaCpp: {type(embedding)}")
                        return []
                else:
                    # Multiple chunks - process sequentially and average
                    import numpy as np
                    chunk_embeddings = []
                    for i, chunk in enumerate(chunks):
                        logger.debug(f"Processing chunk {i+1}/{len(chunks)}")
                        embedding = self.model.embed(chunk)
                        if isinstance(embedding, list) and len(embedding) > 0:
                            if isinstance(embedding[0], list):
                                chunk_embeddings.append(embedding[0])
                            else:
                                chunk_embeddings.append(embedding)

                    if chunk_embeddings:
                        # Average all chunk embeddings
                        avg_embedding = np.mean(chunk_embeddings, axis=0)
                        return avg_embedding.tolist()
                    else:
                        logger.error(
                            "Failed to generate embeddings for any chunk")
                        return []

            except Exception as e:
                logger.error(f"LlamaCpp embedding error: {e}")
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
                embeddings = self.model.encode(
                    valid_texts, convert_to_numpy=True)
                return embeddings.tolist()

            elif self.model_type == "llamacpp":
                # LlamaCpp: process texts sequentially (not concurrently)
                # Each text is processed through the queue to prevent GPU conflicts
                logger.info(
                    f"Processing {len(valid_texts)} texts sequentially through queue")
                embeddings = []
                for i, text in enumerate(valid_texts, 1):
                    logger.debug(
                        f"Processing text {i}/{len(valid_texts)} ({len(text)} chars)")
                    # generate_embedding uses queue lock internally
                    embedding = self.generate_embedding(text)
                    if embedding:
                        embeddings.append(embedding)
                    else:
                        logger.warning(
                            f"Failed to generate embedding for text {i} (length: {len(text)})")
                        embeddings.append([])
                logger.info(
                    f"Completed batch processing: {len(embeddings)} embeddings generated")
                return embeddings

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
            # Check if using embedding microservice (which may use non-OpenAI models)
            service_enabled = os.getenv(
                "EMBEDDING_SERVICE_ENABLED", "false").lower() == "true"

            if service_enabled:
                # Detect dimension dynamically from microservice by generating a test embedding
                try:
                    logger.info(
                        "🔍 Detecting embedding dimension from microservice...")
                    test_embedding = self.generate_embedding("test")
                    if test_embedding and len(test_embedding) > 0:
                        dim = len(test_embedding)
                        logger.info(
                            f"✅ Microservice embedding dimension: {dim}")
                        return dim
                    else:
                        logger.warning(
                            "Empty test embedding from microservice, using fallback 1536")
                        return 1536
                except Exception as e:
                    logger.warning(
                        f"Failed to detect microservice dimension: {e}, using fallback 1536")
                    return 1536
            else:
                # Using real OpenAI API - use model-specific dimensions
                dimensions = {
                    "text-embedding-3-small": 1536,
                    "text-embedding-3-large": 3072,
                    "text-embedding-ada-002": 1536,
                }
                return dimensions.get(self.openai_model_name, 1536)

        elif self.model_type == "sentence-transformers":
            # Get dimension from the model
            return self.model.get_sentence_embedding_dimension()

        elif self.model_type == "llamacpp":
            # For LlamaCpp embedding models
            # Snowflake Arctic Embed: 1024 dimensions (default)
            # Use embed() method which returns vectors (flat or nested list)
            try:
                # Generate a test embedding to get the dimension
                test_embedding = self.model.embed("test")
                # Handle both flat and nested list structures
                if isinstance(test_embedding, list) and len(test_embedding) > 0:
                    if isinstance(test_embedding[0], list):
                        dim = len(test_embedding[0])  # Nested structure
                    else:
                        dim = len(test_embedding)  # Flat structure
                    logger.info(f"✅ LlamaCpp embedding dimension: {dim}")
                    return dim
                else:
                    logger.warning(
                        f"Unexpected embedding structure. Using fallback 1024.")
                    return 1024
            except Exception as e:
                # Fallback to Snowflake Arctic default dimension
                logger.warning(
                    f"Could not determine embedding dimension dynamically: {e}. Using fallback 1024.")
                return 1024

        return 384  # Default fallback dimension


def create_embeddings_generator(config=None) -> EmbeddingsGenerator:
    """
    Create an embeddings generator from configuration.

    Args:
        config: Configuration object with EMBEDDING_MODEL and EMBEDDING_PROVIDER attributes

    Returns:
        EmbeddingsGenerator instance
    """
    if config and hasattr(config, 'embedding_provider') and hasattr(config, 'embedding_model'):
        # Reconstruct full embedding specification with provider prefix
        provider = config.embedding_provider
        model = config.embedding_model

        if provider == "llamacpp":
            # For LlamaCpp, reconstruct the full format: llamacpp:/path/to/model.gguf
            model_name = f"llamacpp:{model}"
        elif provider == "openai":
            # For OpenAI, reconstruct: openai:model-name
            model_name = f"openai:{model}"
        elif provider == "custom":
            # For custom/microservice, use openai format (microservice is OpenAI-compatible)
            model_name = f"openai:{model}"
        else:
            # For sentence-transformers and others, use as-is
            model_name = model
    else:
        # Load from EMBEDDING environment variable (format: provider:model)
        # Example: llamacpp:/path/to/model.gguf or openai:text-embedding-3-small
        embedding_spec = os.getenv(
            "EMBEDDING", "sentence-transformers/all-MiniLM-L6-v2")

        # If using custom provider with microservice, convert to openai format
        # The microservice is OpenAI-compatible
        if embedding_spec.startswith("custom:"):
            model_part = embedding_spec.split(":", 1)[1]
            model_name = f"openai:{model_part}"
        else:
            model_name = embedding_spec

    return EmbeddingsGenerator(model_name)
