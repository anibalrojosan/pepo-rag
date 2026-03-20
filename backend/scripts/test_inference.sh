#!/bin/bash
#
# One-shot non-streaming generation against Ollama (/api/generate) for smoke testing.
#
# Prerequisites: bash, curl, jq; Ollama running; model pulled (default MODEL below).
# Edit MODEL/PROMPT as needed, then run: ./scripts/test_inference.sh
#

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