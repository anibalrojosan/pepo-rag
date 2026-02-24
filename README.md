# 😎 PepoRAG: Tech RAG Assistant

> This project is in development. Currently in [Phase 2: Model Experimentation & Selection](docs/ROADMAP.md#phase-2-model-experimentation--selection-model-benchmarking).

A 100% local Retrieval-Augmented Generation (RAG) system designed to help you chat with your technical book library without ever leaving your machine.

## 🎯 Objective
The goal of this project is to provide a private, high-performance assistant that can answer technical questions using your own collection of PDFs and EPubs, ensuring zero data exposure to the cloud.

## 🚀 Key Features
- **Strictly Local:** Powered by Ollama and PostgreSQL/pgvector.
- **Technical Focus:** Optimized for technical literature and documentation.
- **Type-Safe Orchestration:** Built with PydanticAI and FastAPI.
- **Clean UI:** Simple and intuitive interface using Streamlit.
- **Verified Performance:** Benchmarked on entry-level hardware to ensure a fluid experience.

## 📚 Documentation

To understand the vision and architecture of the project, please refer to the following documentation:

- [PRD](docs/PRD.md): Project objectives, features, user stories, and MVP scope.
- [ARCHITECTURE](docs/ARCHITECTURE.md): System architecture and data flow.
- [ROADMAP](docs/ROADMAP.md): Project phases and features.

## 🛠️ Tech Stack
- **LLM Engine:** [Ollama](https://ollama.com/)
  - *Recommended:* `Llama 3.2 3B` (Quality) or `Qwen 2.5 3B` (Speed).
- **Embeddings:** `nomic-embed-text` (768 dimensions).
- **Orchestration:** PydanticAI.
- **Database:** PostgreSQL + pgvector (via Docker).
- **Backend:** FastAPI + Python 3.12 (managed by `uv`).

## 🛠️ Quick Start (Local Inference)

If you have Ollama installed, you can verify the environment immediately:

### 1. Pull the recommended models
```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### 2. Run the verification script
```bash
./scripts/check_ollama.sh
```

For more details, see the [Local Setup Guide](docs/SETUP_LOCAL.md).

---

> Done with ❤️ by [Anibal Rojo](https://github.com/anibalrojosan)