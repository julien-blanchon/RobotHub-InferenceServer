# Base image with uv + Python 3.12
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# ---------- build-time args ----------
ARG PORT=8001
ARG TRANSPORT_SERVER_URL=https://blanchon-robothub-transportserver.hf.space/api

# ---------- system packages ----------
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc g++ \
        libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
        ffmpeg git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ---------- non-root user ----------
RUN groupadd -r appuser && useradd -m -r -g appuser -s /bin/bash appuser

# ---------- working dir ----------
WORKDIR /app

# ---------- copy manifests (as root, but owned by appuser) ----------
COPY --chown=appuser:appuser pyproject.toml uv.lock* ./
COPY --chown=appuser:appuser external/ ./external/

# ---------- switch to non-root BEFORE anything that downloads ----------
USER appuser

# ---------- cache locations (all writable) ----------
ENV \
    # generic caches
    XDG_CACHE_HOME=/home/appuser/.cache \
    # huggingface-hub + datasets
    HF_HOME=/home/appuser/.cache \
    HF_HUB_CACHE=/home/appuser/.cache/hub \
    HUGGINGFACE_HUB_CACHE=/home/appuser/.cache/hub \
    # transformers
    TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface/hub \
    # uv & app settings
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_CACHE_DIR=/tmp/uv-cache \
    PORT=${PORT} \
    TRANSPORT_SERVER_URL=${TRANSPORT_SERVER_URL}

# make sure cache dirs exist
RUN mkdir -p $HF_HUB_CACHE $TRANSFORMERS_CACHE

# ---------- install dependencies ----------
RUN --mount=type=cache,target=/tmp/uv-cache \
    uv sync --locked --no-install-project --no-dev

# ---------- copy application code ----------
COPY --chown=appuser:appuser . .

# ---------- install project itself ----------
RUN --mount=type=cache,target=/tmp/uv-cache \
    uv sync --locked --no-editable --no-dev

# ---------- virtual-env path ----------
ENV PATH="/app/.venv/bin:$PATH"

# ---------- network / health ----------
EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request, os; urllib.request.urlopen(f'http://localhost:{os.getenv(\"PORT\")}/api/health')" || exit 1

# ---------- run ----------
CMD ["sh", "-c", "python launch_simple.py --host 0.0.0.0 --port ${PORT} --transport-server-url ${TRANSPORT_SERVER_URL}"]
