# ─────────────────────────── base image ───────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ARG PORT=8001
ARG TRANSPORT_SERVER_URL=https://blanchon-robothub-transportserver.hf.space/api

# ──────────────────────── core environment ────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    PORT=${PORT} \
    TRANSPORT_SERVER_URL=${TRANSPORT_SERVER_URL}

# ────────────────────────── OS packages ───────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc g++ \
        libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
        ffmpeg git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ────────────────────────── app user ──────────────────────────────
RUN groupadd -r appuser && useradd -m -r -g appuser -s /bin/bash appuser
ENV HOME=/home/appuser
ENV USER=appuser

# All caches live in the user’s home → no writes to system paths
ENV HF_HOME=$HOME/.cache/huggingface \
    HF_HUB_CACHE=$HOME/.cache/huggingface/hub \
    TRANSFORMERS_CACHE=$HOME/.cache/huggingface/transformers \
    XDG_CACHE_HOME=$HOME/.cache \
    UV_CACHE_DIR=$HOME/.cache/uv

RUN mkdir -p $HF_HUB_CACHE $TRANSFORMERS_CACHE $UV_CACHE_DIR && \
    chown -R $USER:$USER $HOME/.cache

# ───────────────────────── project code ───────────────────────────
WORKDIR /app

# 1️⃣ copy lockfiles first for layer-caching
COPY pyproject.toml uv.lock* /app/
COPY external/ /app/external/

RUN --mount=type=cache,target=/tmp/uv-cache \
    uv sync --locked --no-install-project --no-dev

# 2️⃣ copy the rest & install the project
COPY . /app/
RUN chown -R $USER:$USER /app

RUN --mount=type=cache,target=/tmp/uv-cache \
    uv sync --locked --no-editable --no-dev

# ───────────────────────── runtime user ───────────────────────────
USER appuser

# Expose port (parameterized)
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/api/health')" || exit 1

# Run the application
CMD ["sh", "-c", "python launch_simple.py --host 0.0.0.0 --port ${PORT} --transport-server-url ${TRANSPORT_SERVER_URL}"] 
