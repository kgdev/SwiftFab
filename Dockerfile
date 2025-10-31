# Use Python slim image for CADQuery
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for CADQuery (OpenCASCADE)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglu1-mesa \
    libxrender1 \
    libxext6 \
    libsm6 \
    libxrandr2 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install UV for faster dependency management
RUN pip install --no-cache-dir uv

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copy data directory with CSV parameters
COPY data /app/data

# Copy backend application code
COPY backend /app/backend

# Set default PORT if not provided
ENV PORT=8000

# Expose port (Railway will override this with PORT env var)
EXPOSE $PORT

# Run with uvicorn using PORT environment variable
CMD python3 -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
