FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for llama-cpp-python
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy service files
COPY embedding_service/ ./embedding_service/
COPY requirements.txt ./requirements_main.txt

# Install Python dependencies
# First install llama-cpp-python from main requirements (with GPU support if needed)
RUN pip install --no-cache-dir llama-cpp-python

# Then install service-specific dependencies
RUN pip install --no-cache-dir -r embedding_service/requirements.txt

# Create cache directory for models
RUN mkdir -p /root/.cache/research-agent-local/models

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Environment variables (can be overridden)
ENV EMBEDDING_HOST=0.0.0.0
ENV EMBEDDING_PORT=8001
ENV LLAMACPP_N_CTX=8000
ENV LLAMACPP_N_BATCH=512
ENV LLAMACPP_N_UBATCH=512
ENV LLAMACPP_N_GPU_LAYERS=25

# Run service
CMD ["python", "-m", "uvicorn", "embedding_service.server:app", "--host", "0.0.0.0", "--port", "8001"]
