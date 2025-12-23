# ============================================================================
# Audio Translator - Backend Dockerfile
# Full Offline Translation Pipeline: Speech → STT → Translation → TTS → Speech
# ============================================================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker caching)
COPY requirements.txt .

# Install Python dependencies
# Use PyTorch CPU-only builds from official wheel repository to keep image lean
RUN pip install --no-cache-dir -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p piper/voices piper/piper resources tools

# Download models on build (optional - can also be done at runtime)
# Uncomment the next line to download models during build (increases image size by ~3-4GB)
# RUN python download_models.py

# Expose backend port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
