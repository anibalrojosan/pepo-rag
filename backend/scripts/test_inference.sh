#!/bin/bash

# This script performs a quick inference test to the Ollama API
# Useful to verify that the backend can communicate with the model.

MODEL="llama3.2:3b"
PROMPT="Respond briefly: What is the capital of Chile?"

echo "🚀 Sending test request to Ollama (Model: $MODEL)..."

curl -s http://localhost:11434/api/generate -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"$PROMPT\",
  \"stream\": false
}" | jq

if [ $? -eq 0 ]; then
    echo -e "\n✅ Inference test completed successfully."
else
    echo -e "\n❌ Error communicating with the Ollama API."
fi