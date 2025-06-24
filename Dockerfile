# Use official UV base image with Python 3.12
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set environment variables for Python and UV
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_CACHE_DIR=/tmp/uv-cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build tools for compiling Python packages
    build-essential \
    gcc \
    g++ \
    # Essential system libraries
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # FFmpeg for video processing
    ffmpeg \
    # Git for potential model downloads
    git \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser -m -s /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy dependency files for better layer caching
COPY --chown=appuser:appuser pyproject.toml uv.lock* ./

# Copy external dependencies (submodules) needed for dependency resolution
COPY --chown=appuser:appuser external/ ./external/

# Install dependencies first (better caching)
RUN --mount=type=cache,target=/tmp/uv-cache \
    uv sync --locked --no-install-project --no-dev

# Copy the rest of the application
COPY --chown=appuser:appuser . .

# Install the project in non-editable mode for production
RUN --mount=type=cache,target=/tmp/uv-cache \
    uv sync --locked --no-editable --no-dev

# Switch to non-root user
USER appuser

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose port 7860 (HuggingFace Spaces default)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/api/health')" || exit 1

# Run the application
CMD ["python", "launch_simple.py", "--host", "0.0.0.0", "--port", "7860"] 