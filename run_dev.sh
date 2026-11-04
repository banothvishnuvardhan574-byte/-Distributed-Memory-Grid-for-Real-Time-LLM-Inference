#!/usr/bin/env bash
set -e

uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

(
    cd frontend
    exec npm run dev
) &
FRONTEND_PID=$!

cleanup() {
    trap - EXIT INT TERM
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Backend: http://localhost:8000/docs  |  Frontend: http://localhost:5173"

wait
