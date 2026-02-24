#!/bin/bash

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