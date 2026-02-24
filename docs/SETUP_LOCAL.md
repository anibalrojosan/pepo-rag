# Local Inference Setup Guide (Ollama)

This guide explains how to prepare your machine to run the PepoRAG inference engine.

## 1. Prerequisites
Ensure you have the following tools installed in your WSL2/Linux environment:
- **Ollama:** [Installation Guide](https://ollama.com/download/linux)
- **System Utilities:** `sudo apt install jq curl`
- **Python Manager:** `uv` (for backend execution)

## 2. Model Requirements
Based on our benchmarks (see `EXPERIMENTATION.md`), the following models are required for optimal performance on mid-range hardware (3GB+ VRAM):

```bash
# LLMs for generation
ollama pull llama3.2:3b
ollama pull qwen2.5:3b

# Embedding model for RAG
ollama pull nomic-embed-text
```

## 3. Verification Scripts
We have provided utility scripts in the `scripts/` folder to manage the environment:

### Check Service Status
Verifies if the Ollama service is running and lists available models.
```bash
./scripts/check_ollama.sh
```

### Test API Inference
Performs a real inference test via curl to ensure the API is accessible.
```bash
./scripts/test_inference.sh
```

## 4. Troubleshooting
- **Slow Inference:** Ensure no other GPU-heavy applications (browsers, videos) are running.
- **Connection Refused:** Run `ollama serve` in a separate terminal if the service isn't starting automatically.
