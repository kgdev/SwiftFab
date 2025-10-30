# Use Ubuntu as base image for better FreeCAD support
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies for FreeCAD
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    curl \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Install FreeCAD and Python dependencies from Ubuntu repositories
RUN apt-get update && apt-get install -y \
    freecad \
    freecad-python3 \
    python3-pip \
    python3-dev \
    python3-setuptools \
    build-essential \
    libgl1-mesa-glx \
    libglu1-mesa \
    libxrender1 \
    libxext6 \
    libxcb1 \
    libx11-6 \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    libxcb-xkb1 \
    libxcb-keysyms1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-shm0 \
    libxcb-util1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-render0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy data directory with CSV parameters
COPY data /app/data

# Copy backend application code
COPY backend /app/backend

# Create a startup script that sets up FreeCAD environment
RUN echo '#!/bin/bash\n\
export FREECAD_USER_HOME=/tmp/freecad\n\
mkdir -p $FREECAD_USER_HOME\n\
export PYTHONPATH="/usr/lib/freecad-python3/lib:/usr/lib/freecad/lib:$PYTHONPATH"\n\
export QT_QPA_PLATFORM=offscreen\n\
exec "$@"' > /usr/local/bin/freecad-wrapper.sh \
    && chmod +x /usr/local/bin/freecad-wrapper.sh

# Set default PORT if not provided
ENV PORT=8000

# Expose port (Railway will override this with PORT env var)
EXPOSE $PORT

# Use the wrapper script
ENTRYPOINT ["/usr/local/bin/freecad-wrapper.sh"]
CMD ["python3", "backend/main.py"]

