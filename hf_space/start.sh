#!/bin/bash
set -e

echo "=================================================="
echo " Starting SAGE Live Evaluation Dashboard Container"
echo " Port 7860 (Hugging Face Spaces)"
echo "=================================================="

# 1. Start FastAPI backend on internal port 8000
echo "[1/2] Launching FastAPI backend on 127.0.0.1:8000..."
python -m uvicorn sage.dashboard_backend.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait for backend health check
echo "Waiting for backend service to become ready..."
for i in {1..30}; do
  if python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" >/dev/null 2>&1; then
    echo "[PASS] FastAPI backend is ready and listening on port 8000!"
    break
  fi
  sleep 1
done

# 2. Start Next.js frontend on port 7860
echo "[2/2] Launching Next.js frontend on 0.0.0.0:7860..."
cd /app/sage/dashboard_frontend
export PORT=7860
export HOSTNAME="0.0.0.0"
export NEXT_PUBLIC_API_URL="http://127.0.0.1:8000"

exec npm start -- -p 7860 -H 0.0.0.0
