#!/bin/bash

# Vercel-compatible build script for FreeCAD using dnf (Amazon Linux 2023)
echo "=== FREECAD BUILD SCRIPT STARTING FOR PYTHON BACKEND ==="
echo "Starting Vercel build with FreeCAD using dnf package manager..."
echo "Current working directory: $(pwd)"
echo "Available commands: $(which dnf)"
echo "Script location: $(pwd)/build-vercel.sh"
echo "Script exists: $(test -f build-vercel.sh && echo 'YES' || echo 'NO')"
echo "Building for: backend/main.py with @vercel/python"

# Check if we're in Vercel build environment
if [ -n "$VERCEL" ]; then
    echo "Running in Vercel build environment for Python backend"
else
    echo "Not in Vercel build environment"
fi

# Update package list
echo "Updating package lists..."
dnf update -y

# Install system dependencies using dnf (Amazon Linux 2023)
dnf install -y \
    gcc \
    gcc-c++ \
    make \
    cmake \
    git \
    wget \
    curl \
    python3-devel \
    python3-pip \
    libglvnd-glx \
    mesa-libGL \
    mesa-libGLU \
    libX11 \
    libXext \
    libXrender \
    libXcursor \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXcomposite \
    libXdamage \
    libXfixes \
    libXinerama \
    libXxf86vm \
    libdrm \
    libxcb \
    libxcb-keysyms \
    libxcb-icccm \
    libxcb-image \
    libxcb-shm \
    libxcb-util \
    libxcb-randr \
    libxcb-render-util \
    libxcb-render \
    libxcb-shape \
    libxcb-sync \
    libxcb-xfixes \
    libxcb-xinerama \
    libxkbcommon \
    libxkbcommon-x11 \
    pango \
    atk \
    gtk3 \
    gtk3-devel \
    at-spi2-atk \
    cups-libs \
    alsa-lib \
    expat-devel \
    libffi-devel \
    zlib-devel \
    bzip2-devel \
    libjpeg-devel \
    libpng-devel \
    libwebp-tools \
    zstd

# Install FreeCAD from EPEL repository
dnf install -y epel-release
dnf install -y freecad

# Alternative: Try to install FreeCAD from snap (if available)
# snap install freecad

# Set up FreeCAD environment
export FREECAD_USER_HOME=/tmp/freecad
mkdir -p $FREECAD_USER_HOME
export PYTHONPATH="/usr/lib/freecad-python3/lib:$PYTHONPATH"

# Create symlinks for FreeCAD Python modules
if [ -d "/usr/lib/freecad-python3/lib" ]; then
    echo "FreeCAD Python path found: /usr/lib/freecad-python3/lib"
elif [ -d "/usr/lib64/freecad/lib" ]; then
    echo "FreeCAD Python path found: /usr/lib64/freecad/lib"
    export PYTHONPATH="/usr/lib64/freecad/lib:$PYTHONPATH"
else
    echo "Searching for FreeCAD installation..."
    find /usr -name "*freecad*" -type d 2>/dev/null | head -10
fi

echo "FreeCAD installation completed for Vercel using dnf"
