#!/usr/bin/env python3
"""
Embedding Microservice - OpenAI-compatible API
Handles LlamaCpp embeddings with proper queuing and single model instance
"""
import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from llama_cpp import Llama

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global model instance and queue
_model: Optional[Llama] = None
_request_queue: Optional[asyncio.Queue] = None
_model_lock = asyncio.Lock()


class EmbeddingRequest(BaseModel):
    """OpenAI-compatible embedding request"""
    input: str | List[str] = Field(..., description="Text(s) to embed")
    model: str = Field(default="snowflake-arctic-embed",
                       description="Model name (ignored, uses configured model)")
    encoding_format: str = Field(
        default="float", description="Encoding format")


class EmbeddingObject(BaseModel):
    """Single embedding result"""
    object: str = "embedding"
    embedding: List[float]
    index: int


class Usage(BaseModel):
    """Token usage information"""
    prompt_tokens: int
    total_tokens: int


class EmbeddingResponse(BaseModel):
    """OpenAI-compatible embedding response"""
    object: str = "list"
    data: List[EmbeddingObject]
    model: str
    usage: Usage


async def load_model():
    """Load the LlamaCpp model on startup"""
    global _model

    model_path = os.environ.get(
        "EMBEDDING_MODEL_PATH",
        "/home/yy/.cache/research-agent-local/models/snowflake-arctic-embed-l-v2.0.F16.gguf"
    )

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    logger.info("🚀 Loading embedding model...")
    logger.info(f"   Model: {os.path.basename(model_path)}")

    n_ctx = int(os.environ.get("LLAMACPP_N_CTX", "8000"))
    n_batch = int(os.environ.get("LLAMACPP_N_BATCH", "512"))
    n_ubatch = int(os.environ.get("LLAMACPP_N_UBATCH", "512"))
    n_gpu_layers = int(os.environ.get("LLAMACPP_N_GPU_LAYERS", "25"))

    _model = Llama(
        model_path=model_path,
        embedding=True,
        verbose=False,
        n_ctx=n_ctx,
        n_batch=n_batch,
        n_ubatch=n_ubatch,
        n_gpu_layers=n_gpu_layers,
        n_threads=None,
    )

    logger.info("✅ Model loaded successfully!")
    logger.info(f"   Context: {n_ctx}, Batch: {n_batch}, UBatch: {n_ubatch}")
    logger.info(f"   GPU Layers: {n_gpu_layers}")


async def unload_model():
    """Unload the model on shutdown"""
    global _model
    if _model:
        logger.info("Unloading model...")
        _model.close()
        _model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    await load_model()
    global _request_queue
    # Queue for managing concurrent requests
    _request_queue = asyncio.Queue(maxsize=100)

    # Start request processor
    processor_task = asyncio.create_task(process_requests())

    yield

    # Shutdown
    await _request_queue.put(None)  # Signal shutdown
    await processor_task
    await unload_model()


app = FastAPI(
    title="Embedding Microservice",
    description="OpenAI-compatible embedding API with LlamaCpp backend",
    version="1.0.0",
    lifespan=lifespan
)


async def process_requests():
    """Background task to process embedding requests sequentially"""
    global _model, _request_queue

    logger.info("🔄 Request processor started")

    while True:
        item = await _request_queue.get()

        # Shutdown signal
        if item is None:
            logger.info("Request processor shutting down")
            break

        future, texts = item

        try:
            # Process embeddings sequentially (thread-safe)
            async with _model_lock:
                embeddings = []
                for text in texts:
                    if _model is None:
                        raise RuntimeError("Model not loaded")

                    # Generate embedding
                    embedding = _model.embed(text)

                    # Handle different return formats
                    if isinstance(embedding, list) and isinstance(embedding[0], list):
                        embeddings.append(list(map(float, embedding[0])))
                    else:
                        embeddings.append(list(map(float, embedding)))

                future.set_result(embeddings)

        except Exception as e:
            logger.error(f"Error processing embedding: {e}")
            future.set_exception(e)
        finally:
            _request_queue.task_done()


async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Queue an embedding request and wait for result

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    future = asyncio.Future()
    await _request_queue.put((future, texts))
    return await future


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "embedding-microservice",
        "model_loaded": _model is not None,
        "queue_size": _request_queue.qsize() if _request_queue else 0
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "status": "healthy",
        "model_loaded": True,
        "queue_size": _request_queue.qsize(),
        "queue_max_size": _request_queue.maxsize
    }


@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest) -> EmbeddingResponse:
    """
    OpenAI-compatible embeddings endpoint

    Compatible with:
    - OpenAI Python SDK
    - LangChain OpenAIEmbeddings
    - Any OpenAI-compatible client
    """
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Convert input to list
    texts = [request.input] if isinstance(
        request.input, str) else request.input

    if not texts:
        raise HTTPException(status_code=400, detail="No input provided")

    try:
        # Generate embeddings via queue
        embeddings = await generate_embeddings(texts)

        # Build response
        data = [
            EmbeddingObject(
                embedding=emb,
                index=idx
            )
            for idx, emb in enumerate(embeddings)
        ]

        # Calculate token usage (rough estimate)
        total_tokens = sum(len(text.split()) for text in texts)

        return EmbeddingResponse(
            data=data,
            model=request.model,
            usage=Usage(
                prompt_tokens=total_tokens,
                total_tokens=total_tokens
            )
        )

    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embed", response_model=Dict[str, Any])
async def embed_legacy(texts: List[str]) -> Dict[str, Any]:
    """
    Legacy embedding endpoint (simplified format)

    Args:
        texts: List of texts to embed

    Returns:
        {"embeddings": [[float, ...], ...]}
    """
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Validate input
    if not texts or len(texts) == 0:
        raise HTTPException(status_code=400, detail="texts cannot be empty")

    try:
        embeddings = await generate_embeddings(texts)
        return {"embeddings": embeddings}
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Start the embedding service"""
    host = os.environ.get("EMBEDDING_HOST", "0.0.0.0")
    port = int(os.environ.get("EMBEDDING_PORT", "8001"))

    logger.info(f"🚀 Starting Embedding Service on {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
