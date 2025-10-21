#!/usr/bin/env bash
# Embedding Microservice Startup Script

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="${VENV_PATH:-$HOME/work}"
HOST="${EMBEDDING_HOST:-0.0.0.0}"
PORT="${EMBEDDING_PORT:-8001}"

echo "🚀 Starting Embedding Microservice"
echo "================================================"

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    echo "✓ Activating virtual environment: $VENV_PATH"
    source "$VENV_PATH/bin/activate"
else
    echo "❌ Virtual environment not found: $VENV_PATH"
    echo "   Please create it: python -m venv $VENV_PATH"
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT"
echo "✓ Working directory: $PROJECT_ROOT"

# Check dependencies
echo ""
echo "Checking dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI not installed. Installing dependencies..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    echo "✓ FastAPI installed"
fi

if ! python -c "import uvicorn" 2>/dev/null; then
    echo "⚠️  Uvicorn not installed. Installing..."
    pip install uvicorn[standard]
else
    echo "✓ Uvicorn installed"
fi

# Check model path
if [ -z "$EMBEDDING_MODEL_PATH" ]; then
    echo "⚠️  EMBEDDING_MODEL_PATH not set, using default"
    export EMBEDDING_MODEL_PATH="$HOME/.cache/research-agent-local/models/snowflake-arctic-embed-l-v2.0.F16.gguf"
fi

if [ ! -f "$EMBEDDING_MODEL_PATH" ]; then
    echo "❌ Model file not found: $EMBEDDING_MODEL_PATH"
    echo "   Please set EMBEDDING_MODEL_PATH environment variable"
    exit 1
fi
echo "✓ Model found: $EMBEDDING_MODEL_PATH"

# Display configuration
echo ""
echo "Configuration:"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Model: $(basename "$EMBEDDING_MODEL_PATH")"
echo "  N_CTX: ${LLAMACPP_N_CTX:-8000}"
echo "  N_BATCH: ${LLAMACPP_N_BATCH:-512}"
echo "  N_UBATCH: ${LLAMACPP_N_UBATCH:-512}"
echo "  N_GPU_LAYERS: ${LLAMACPP_N_GPU_LAYERS:-25}"
echo ""

# Start service
echo "================================================"
echo "Starting service on http://$HOST:$PORT"
echo "Press Ctrl+C to stop"
echo "================================================"
echo ""

exec python -m uvicorn embedding_service.server:app \
    --host "$HOST" \
    --port "$PORT" \
    --log-level info
