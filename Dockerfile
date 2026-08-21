FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with timeout and no cache for smaller image
RUN pip install --no-cache-dir --timeout 600 -r requirements.txt

# Pre-download the embedding model to avoid download issues at runtime
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY . .

# Create necessary directories with write permissions for HF Spaces
RUN mkdir -p data/vectors data/indexes logs temp cache && \
    chmod -R 777 data logs temp cache

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Expose port (HF Spaces expects 7860)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:7860/api/v1/health || exit 1

# Run the application
CMD ["python", "-m", "app.main"]