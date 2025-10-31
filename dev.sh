#!/bin/bash
# Quick development startup script

# Check if PostgreSQL is running
if ! docker ps | grep -q swiftfab-postgres; then
    echo "Starting PostgreSQL..."
    docker start swiftfab-postgres || ./start-postgres.sh
fi

# Start backend in background
echo "Starting backend..."
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm start

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT

