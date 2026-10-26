#!/usr/bin/env bash
set -e

uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

(cd frontend && npm run dev) &
FRONTEND_PID=$!

cleanup() {
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Backend docs: http://localhost:8000/docs"
echo "Frontend:     http://localhost:5173"

wait
