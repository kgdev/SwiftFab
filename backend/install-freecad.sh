#!/bin/bash

# Install FreeCAD dependencies for Vercel build
echo "Installing FreeCAD dependencies..."

# Update package list
apt-get update

# Install system dependencies
apt-get install -y \
    software-properties-common \
    wget \
    curl \
    gnupg2

# Add FreeCAD PPA
wget -qO - https://www.freecad.org/keys/FreeCAD.asc | apt-key add -
echo "deb https://www.freecad.org/debian/ jammy main" > /etc/apt/sources.list.d/freecad.list

# Install FreeCAD
apt-get update && apt-get install -y \
    freecad \
    libgl1-mesa-glx \
    libglu1-mesa \
    libxrender1 \
    libxext6 \
    libxcb1 \
    libx11-6

echo "FreeCAD installation completed"
