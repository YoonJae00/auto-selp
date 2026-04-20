#!/bin/bash

echo "=== Auto-Selp Backend Verification ==="

# 1. Install Dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# 2. Start Server in Background
echo "Starting FastAPI Server..."
python -m uvicorn src.api.main:app --port 8000 > server.log 2>&1 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"

# Wait for server to start
sleep 5

# 3. Run Integration Test
echo "Running Integration Test..."
python tests/test_backend.py

# 4. Cleanup
echo "Stopping Server..."
kill $SERVER_PID
echo "Done."
