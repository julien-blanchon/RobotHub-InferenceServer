FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# ---------- build args ----------
ARG PORT=8001
ARG TRANSPORT_SERVER_URL=https://blanchon-robothub-transportserver.hf.space/api

# ---------- system packages ----------
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc g++ \
        libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
        ffmpeg git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ---------- app user ----------
RUN groupadd -r appuser && useradd -m -r -g appuser -s /bin/bash appuser

# ---------- cache directories & environment ----------
ENV HOME=/home/appuser
ENV \
    HF_HOME=$HOME/.cache \
    HF_HUB_CACHE=$HOME/.cache/hub \
    HUGGINGFACE_HUB_CACHE=$HOME/.cache/hub \
    TRANSFORMERS_CACHE=$HOME/.cache/huggingface/hub \
    UV_CACHE_DIR=$HOME/.cache/uv \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    PORT=${PORT} \
    TRANSPORT_SERVER_URL=${TRANSPORT_SERVER_URL}

# create the caches while still root, then chown to appuser
RUN mkdir -p "$HF_HUB_CACHE" "$TRANSFORMERS_CACHE" "$UV_CACHE_DIR" \
    && chown -R appuser:appuser "$HOME/.cache"

# switch to non-root user (no inline comment!)
USER appuser

# ---------- workdir ----------
WORKDIR /app

# ---------- copy manifests first ----------
COPY --chown=appuser:appuser pyproject.toml uv.lock* ./
COPY --chown=appuser:appuser external/ ./external/

# ---------- install deps ----------
RUN --mount=type=cache,target=$UV_CACHE_DIR,uid=1000,gid=1000 \
    uv sync --locked --no-install-project --no-dev

# ---------- copy source ----------
COPY --chown=appuser:appuser . .

# ---------- install the project itself ----------
RUN --mount=type=cache,target=$UV_CACHE_DIR,uid=1000,gid=1000 \
    uv sync --locked --no-editable --no-dev

# ---------- virtual-env path ----------
ENV PATH="/app/.venv/bin:$PATH"

# ---------- runtime ----------
EXPOSE ${PORT}
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request, os; urllib.request.urlopen(f'http://localhost:{os.getenv(\"PORT\")}/api/health')" || exit 1

CMD ["sh", "-c", "python launch_simple.py --host 0.0.0.0 --port ${PORT} --transport-server-url ${TRANSPORT_SERVER_URL}"]
