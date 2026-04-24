#!/usr/bin/env bash
set -e

ollama serve &
OLLAMA_PID=$!

echo "Waiting for Ollama..."
until curl -s http://127.0.0.1:11434/api/tags >/dev/null; do
  sleep 2
done

echo "Pulling model qwen2.5:0.5b..."
ollama pull qwen2.5:0.5b

echo "Starting FastAPI..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000