#!/bin/bash
#
# Quick health check: Ollama HTTP API is reachable and lists local models.
#
# Prerequisites: bash, curl, jq; Ollama running (e.g. ollama serve).
# Usage: from repo root or backend — ./scripts/check_ollama.sh (ensure executable).
#

OLLAMA_URL="http://localhost:11434/api/tags"

echo "🔍 Checking Ollama service..."

if curl -s -f "$OLLAMA_URL" > /dev/null; then
    echo "✅ Ollama is responding correctly."
    echo "------------------------------------------"
    echo "Available models locally:"
    curl -s "$OLLAMA_URL" | jq -r '.models[].name'
else
    echo "❌ Error: Ollama is not responding at $OLLAMA_URL"
    echo "Make sure the service is running (ollama serve)"
    exit 1
fi