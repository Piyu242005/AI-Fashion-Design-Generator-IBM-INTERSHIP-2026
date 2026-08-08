# ============================================================
#  Piyu AI Clothing Fashion Design Generator
#  Docker Image — CUDA 11.8 · Python 3.11 · Streamlit
# ============================================================
#
#  Build:
#    docker build -t piyu-fashion:latest .
#
#  Run (GPU):
#    docker run --gpus all -p 8501:8501 --env-file .env piyu-fashion:latest
#
#  Run (CPU-only):
#    docker run -p 8501:8501 --env-file .env piyu-fashion:latest
# ============================================================

# ── Stage 1: Base ─────────────────────────────────────────────────────────
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04 AS base

LABEL maintainer="Piyush Ramteke <piyushramteke2420@gmail.com>" \
      description="Piyu AI Clothing Fashion Design Generator — RealVisXL · SAM · IDM-VTON" \
      version="1.0.0" \
      python.version="3.11" \
      cuda.version="11.8"

# Prevent interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC

# ── System packages ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python 3.11
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    # Build tools
    build-essential \
    cmake \
    ninja-build \
    gcc \
    g++ \
    # OpenCV / image processing
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-glx \
    libglib2.0-dev \
    # Git (for git+https:// installs)
    git \
    # Utilities
    wget \
    curl \
    ca-certificates \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    # ONNX runtime dependencies
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Make python3.11 the default python/pip
RUN update-alternatives --install /usr/bin/python  python  /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    python -m pip install --upgrade pip setuptools wheel

# ── Environment variables ─────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Hugging Face cache inside the container (mount as volume for persistence)
    HF_HOME=/app/hf_cache \
    TRANSFORMERS_CACHE=/app/hf_cache \
    # Model weight cache (can be overridden via docker run -e MODEL_DIR=...)
    MODEL_DIR=/app/weights \
    # Streamlit
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none \
    # Torch
    TORCH_HOME=/app/torch_cache \
    # CUDA
    CUDA_VISIBLE_DEVICES=0 \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

# ── Working directory ─────────────────────────────────────────────────────
WORKDIR /app


# ── Stage 2: Python dependencies ──────────────────────────────────────────
FROM base AS deps

# Install PyTorch 2.1.0 with CUDA 11.8 first (large wheel, separate layer for caching)
RUN pip install --no-cache-dir \
    torch==2.1.0 \
    torchvision==0.16.0 \
    --index-url https://download.pytorch.org/whl/cu118

# Install the rest of the Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install Segment Anything from source
RUN pip install --no-cache-dir \
    "git+https://github.com/facebookresearch/segment-anything.git"

# Install CLIP from source (official OpenAI implementation)
RUN pip install --no-cache-dir \
    "git+https://github.com/openai/CLIP.git"

# Install python-dotenv (reads .env at startup)
RUN pip install --no-cache-dir python-dotenv>=1.0.0


# ── Stage 3: Application ──────────────────────────────────────────────────
FROM deps AS app

# Create required runtime directories
RUN mkdir -p \
    /app/weights \
    /app/hf_cache \
    /app/torch_cache \
    /app/results \
    /app/reference_images \
    /app/samples \
    /app/assets \
    /app/.streamlit

# Copy application source
COPY app.py               /app/app.py
COPY generate_model.py    /app/generate_model.py
COPY model_manager.py     /app/model_manager.py
COPY segment.py           /app/segment.py
COPY try_on.py            /app/try_on.py
COPY src/                 /app/src/
COPY .streamlit/          /app/.streamlit/
COPY assets/              /app/assets/

# Copy optional sample data (non-critical)
COPY samples/             /app/samples/

# Healthcheck — ensure Streamlit is responding
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose Streamlit port
EXPOSE 8501

# Non-root user for security
RUN groupadd -r fashion && useradd -r -g fashion -d /app fashion && \
    chown -R fashion:fashion /app
USER fashion

# Default entrypoint
ENTRYPOINT ["python", "-m", "streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.headless=true", \
            "--server.fileWatcherType=none", \
            "--browser.gatherUsageStats=false"]
