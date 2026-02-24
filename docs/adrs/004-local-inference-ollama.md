# ADR 004: Local Inference with Ollama

## Status
Accepted

## Context
A core requirement of the project is to ensure 100% local compute and data privacy. We need a reliable way to run and serve Large Language Models (LLMs) on the user's local hardware.

## Decision
We will use **Ollama** as the local inference engine.

## Rationale
- **Ease of Use:** Simplifies the process of downloading, running, and managing local LLMs.
- **API Compatibility:** Provides an OpenAI-compatible API, making it easy to integrate with various tools and frameworks.
- **Performance:** Optimized for running models on consumer hardware (macOS, Linux, Windows) using various backends (Metal, CUDA, ROCm).
- **Model Variety:** Supports a wide range of popular open-source models (Llama 3, Mistral, Phi-3, etc.).
- **Local Control:** Fits perfectly with our "strictly local" constraint.

## Consequences
- **Hardware Requirements:** Users must have sufficient RAM and/or GPU VRAM to run the chosen models effectively.
- **Installation:** Ollama must be installed and running as a service on the host machine.
- **Model Management:** We need to provide guidance or automation for downloading the required models via Ollama.
