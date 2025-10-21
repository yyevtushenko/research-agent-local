import os
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

OPENAI_EMBEDDING_MODEL = os.environ.get(
    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
)

SUPPORTED_EMBEDDING_PROVIDERS = {
    "openai",
    "azure_openai",
    "custom",
    "cohere",
    "google_vertexai",
    "google_genai",
    "fireworks",
    "gigachat",
    "ollama",
    "together",
    "mistralai",
    "huggingface",
    "nomic",
    "voyageai",
    "dashscope",
    "bedrock",
    "aimlapi",
    "netmind",
    "llamacpp",
}

# Backwards compatibility alias
_SUPPORTED_PROVIDERS = SUPPORTED_EMBEDDING_PROVIDERS


def _try_embedding_service(model: str, **embedding_kwargs) -> Optional[Any]:
    """
    Try to use embedding microservice if enabled.

    Returns:
        Embedding client if service is available, None otherwise
    """
    import socket
    import requests
    from requests.exceptions import ReadTimeout, ConnectionError, Timeout

    # Check if service is enabled
    service_enabled = os.environ.get(
        "EMBEDDING_SERVICE_ENABLED", "false").lower() == "true"

    if not service_enabled:
        logger.warning("⚠️ Embedding service is DISABLED in environment")
        return None

    service_url = os.environ.get(
        "EMBEDDING_SERVICE_URL", "http://localhost:8001")

    try:
        from embedding_service.client import EmbeddingServiceClient, OpenAICompatibleEmbeddings

        # Test connection with health check first (with timeout)
        test_client = EmbeddingServiceClient(base_url=service_url)
        health = test_client.health_check()

        if health.get("status") != "healthy":
            logger.warning(f"Embedding service unhealthy: {health}")
            return None

        logger.info(f"✓ Using embedding microservice: {service_url}")
        logger.info(f"  Model: {health.get('model', 'unknown')}")
        logger.info(
            f"  Queue: {health.get('queue_size', 0)}/{health.get('max_queue_size', 'N/A')}")

        # Return LangChain-compatible wrapper
        result = OpenAICompatibleEmbeddings(base_url=service_url)
        return result

    except ImportError as e:
        logger.warning(f"Embedding service imports not available: {e}")
        logger.info("Falling back to local embeddings")
        return None
    except (ReadTimeout, Timeout, ConnectionError, socket.timeout) as e:
        logger.warning(
            f"Embedding service timeout/connection error ({service_url}): {type(e).__name__}")
        logger.info("Falling back to local embeddings")
        return None
    except Exception as e:
        logger.warning(
            f"Embedding service unavailable ({service_url}): {type(e).__name__}: {e}")
        logger.info("Falling back to local embeddings")
        return None


class Memory:
    def __init__(self, embedding_provider: str, model: str, **embedding_kwargs: Any):
        _embeddings = None
        match embedding_provider:
            case "custom":
                # Try embedding service first (recommended for GPU OOM prevention)
                service_embeddings = _try_embedding_service(
                    model, **embedding_kwargs)
                if service_embeddings is not None:
                    _embeddings = service_embeddings
                else:
                    # Fallback to custom OpenAI-compatible endpoint
                    from langchain_openai import OpenAIEmbeddings

                    _embeddings = OpenAIEmbeddings(
                        model=model,
                        openai_api_key=os.getenv("OPENAI_API_KEY", "custom"),
                        openai_api_base=os.getenv(
                            "OPENAI_BASE_URL", "http://localhost:1234/v1"
                        ),  # default for lmstudio
                        check_embedding_ctx_length=False,
                        **embedding_kwargs,
                    )  # quick fix for lmstudio
            case "openai":
                from langchain_openai import OpenAIEmbeddings

                # Support custom OpenAI-compatible APIs via OPENAI_BASE_URL
                if "openai_api_base" not in embedding_kwargs and os.environ.get("OPENAI_BASE_URL"):
                    embedding_kwargs["openai_api_base"] = os.environ["OPENAI_BASE_URL"]

                _embeddings = OpenAIEmbeddings(model=model, **embedding_kwargs)
            case "azure_openai":
                from langchain_openai import AzureOpenAIEmbeddings

                _embeddings = AzureOpenAIEmbeddings(
                    model=model,
                    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                    openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
                    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                    **embedding_kwargs,
                )
            case "cohere":
                from langchain_cohere import CohereEmbeddings

                _embeddings = CohereEmbeddings(model=model, **embedding_kwargs)
            case "google_vertexai":
                from langchain_google_vertexai import VertexAIEmbeddings

                _embeddings = VertexAIEmbeddings(
                    model=model, **embedding_kwargs)
            case "google_genai":
                from langchain_google_genai import GoogleGenerativeAIEmbeddings

                _embeddings = GoogleGenerativeAIEmbeddings(
                    model=model, **embedding_kwargs
                )
            case "fireworks":
                from langchain_fireworks import FireworksEmbeddings

                _embeddings = FireworksEmbeddings(
                    model=model, **embedding_kwargs)
            case "gigachat":
                from langchain_gigachat import GigaChatEmbeddings

                _embeddings = GigaChatEmbeddings(
                    model=model, **embedding_kwargs)
            case "ollama":
                from langchain_ollama import OllamaEmbeddings

                _embeddings = OllamaEmbeddings(
                    model=model,
                    base_url=os.environ["OLLAMA_BASE_URL"],
                    **embedding_kwargs,
                )
            case "together":
                from langchain_together import TogetherEmbeddings

                _embeddings = TogetherEmbeddings(
                    model=model, **embedding_kwargs)
            case "netmind":
                from langchain_netmind import NetmindEmbeddings

                _embeddings = NetmindEmbeddings(
                    model=model, **embedding_kwargs)
            case "mistralai":
                from langchain_mistralai import MistralAIEmbeddings

                _embeddings = MistralAIEmbeddings(
                    model=model, **embedding_kwargs)
            case "huggingface":
                from langchain_huggingface import HuggingFaceEmbeddings

                _embeddings = HuggingFaceEmbeddings(
                    model_name=model, **embedding_kwargs)
            case "nomic":
                from langchain_nomic import NomicEmbeddings

                _embeddings = NomicEmbeddings(model=model, **embedding_kwargs)
            case "voyageai":
                from langchain_voyageai import VoyageAIEmbeddings

                _embeddings = VoyageAIEmbeddings(
                    voyage_api_key=os.environ["VOYAGE_API_KEY"],
                    model=model,
                    **embedding_kwargs,
                )
            case "dashscope":
                from langchain_community.embeddings import DashScopeEmbeddings

                _embeddings = DashScopeEmbeddings(
                    model=model, **embedding_kwargs)
            case "bedrock":
                from langchain_aws.embeddings import BedrockEmbeddings

                _embeddings = BedrockEmbeddings(
                    model_id=model, **embedding_kwargs)
            case "aimlapi":
                from langchain_openai import OpenAIEmbeddings

                _embeddings = OpenAIEmbeddings(
                    model=model,
                    openai_api_key=os.getenv("AIMLAPI_API_KEY"),
                    openai_api_base=os.getenv(
                        "AIMLAPI_BASE_URL", "https://api.aimlapi.com/v1"),
                    **embedding_kwargs,
                )
            case "llamacpp":
                # Try embedding service first (recommended for GPU OOM prevention)
                service_embeddings = _try_embedding_service(
                    model, **embedding_kwargs)
                if service_embeddings is not None:
                    _embeddings = service_embeddings
                else:
                    # Fallback to local LlamaCpp embeddings
                    logger.info(
                        "Using local LlamaCpp embeddings (fallback mode)")

                    from langchain_community.embeddings import LlamaCppEmbeddings
                    from .llamacpp_embeddings_wrapper import ThreadSafeLlamaCppEmbeddings

                    # Extract model path from the model string
                    # Expected format: "llamacpp:/path/to/model.gguf" or just "/path/to/model.gguf"
                    model_path = model
                    if model.startswith("llamacpp:"):
                        model_path = model.split(":", 1)[1]

                    # Get configuration from environment or use defaults
                    n_ctx = int(os.environ.get("LLAMACPP_N_CTX", "8000"))
                    n_gpu_layers = int(os.environ.get(
                        "LLAMACPP_N_GPU_LAYERS", "25"))
                    n_batch = int(os.environ.get("LLAMACPP_N_BATCH", "512"))

                    # Use thread-safe wrapper to prevent CUDA errors with concurrent access
                    # NOTE: LangChain's LlamaCppEmbeddings doesn't support n_ubatch parameter
                    # The underlying Llama model will use default n_ubatch based on n_batch
                    _embeddings = ThreadSafeLlamaCppEmbeddings(
                        model_path=model_path,
                        n_ctx=n_ctx,
                        # Batch size (LangChain uses this for both prompt and embeddings)
                        n_batch=n_batch,
                        n_gpu_layers=n_gpu_layers,
                        n_threads=None,  # Use all available threads
                        **embedding_kwargs,
                    )
            case _:
                raise Exception("Embedding not found.")

        self._embeddings = _embeddings

    def get_embeddings(self):
        return self._embeddings
