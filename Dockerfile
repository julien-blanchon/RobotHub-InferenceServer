# Use official UV base image with Python 3.12
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
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

# Copy dependency files
COPY --chown=appuser:appuser pyproject.toml ./

# Copy the external python client dependency
COPY --chown=appuser:appuser external/ ./external/

# Install Python dependencies (without --frozen to regenerate lock)
RUN --mount=type=cache,target=/tmp/uv-cache \
    uv sync --no-dev

# Copy the entire project
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose port 7860 (HuggingFace Spaces default)
EXPOSE 7860

# Health check using activated virtual environment (FastAPI health endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/api/health')" || exit 1

# Run the application with activated virtual environment
CMD ["python", "launch_simple.py", "--host", "0.0.0.0", "--port", "7860"] 