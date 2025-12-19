#!/bin/bash
# ============================================================================
# Download AI Models Inside Docker Container
# Run this if models weren't downloaded during build
# ============================================================================

echo "📥 Downloading AI Models for L&T Audio Translator"
echo "=================================================="
echo ""

# Check if we're inside a Docker container
if [ -f /.dockerenv ]; then
    echo "✅ Running inside Docker container"
else
    echo "⚠️  Not inside Docker container"
    echo "🐳 Starting download in backend container..."
    docker exec -it lt-translator-backend bash -c "python download_models.py"
    exit 0
fi

# Download models
echo "🔽 Starting model download (~3-4GB)..."
echo "This may take 10-15 minutes..."
echo ""

python download_models.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All models downloaded successfully!"
    echo ""
    echo "📦 Downloaded:"
    echo "  - Whisper STT model"
    echo "  - M2M100 Translation model"
    echo "  - Piper TTS binary"
    echo "  - 5 language voice models"
    echo ""
    echo "🎯 Ready to translate!"
else
    echo ""
    echo "❌ Model download failed!"
    echo "Check internet connection and try again"
    exit 1
fi
