# Development Log: PepoRAG

This document describes the development process of the **PepoRAG** project. It serves as a record of decisions made, lessons learned, problems encountered and resolved, and overall progress.

📑 Table of contents
* [[2026-02-24] - Phase 1: Foundation and Local Inference](#2026-02-24---phase-1-foundation-and-local-inference)
* [[2026-02-23] - Strategic Definition and Initial Architecture](#2026-02-23---strategic-definition-and-initial-architecture)


---

## [2026-02-24] - Phase 1: Foundation and Local Inference
**Context:** Implementation of base infrastructure and validation of the inference engine on real hardware.

### Task 1: Development Environment Setup
*   **Dependency Management:** Implemented `uv` for ultra-fast and reproducible package management.
*   **Docker Infrastructure:** Created `docker-compose.yml` for PostgreSQL with the `pgvector` extension.
*   **Project Scaffolding:** Initial folder structure established (`scripts/`, `docs/`, `data/`).

### Task 2: Model Experimentation and Benchmarking
Conducted an exhaustive performance analysis on local hardware (GTX 1050 3GB VRAM / 24GB RAM):
*   **Critical Finding:** 7B/8B models (Llama 3.1, Qwen 2.5) are unfeasible for this hardware due to the VRAM limit, dropping to <4 TPS.
*   **Model Selection:** Validated **Llama 3.2 3B** (Quality) and **Qwen 2.5 3B** (Speed) as the project standards, achieving latencies (TTFT) under 1 second.
*   **Documentation:** Updated `docs/EXPERIMENTATION.md` with comparative TPS and TTFT tables.

### Task 3: Verification Tooling
*   **Utility Scripts:** Created `scripts/check_ollama.sh` and `scripts/test_inference.sh` to ensure a reproducible and healthy inference environment.
*   **User Guide:** Drafted `docs/SETUP_LOCAL.md` to facilitate technical onboarding.

**Current Status:** Phase 1 is officially closed. The system has a vector-ready database and a validated, documented inference engine. Ready to start **Phase 2: Document Ingestion**.

---

## [2026-02-23] - Strategic Definition and Initial Architecture
**Context:** Project kickoff for PepoRAG. Established the vision for a 100% local RAG system for technical libraries, prioritizing privacy and performance on modest hardware.

### Task 1: Building the Documentation Ecosystem
Key project pillars were drafted in the `docs/` directory to ensure a "single source of truth":
*   **PRD.md:** Problem definition, User Stories for technical readers, and a 4-phase Roadmap.
*   **ARCHITECTURE.md:** System-level data flow design (Streamlit -> FastAPI -> PostgreSQL/pgvector -> PydanticAI -> Ollama).
*   **ROADMAP.md:** Detailed planning from foundation to chat interface.
* **EXPERIMENTATION.md**: Experiment desing for model selection.

### Task 2: Architectural Decision Records (ADRs)
Implemented 5 foundational ADRs:
*   **ADR-001 (PostgreSQL/pgvector):** Chose Postgres over pure vector databases for its maturity and SQL support.
*   **ADR-002 (PydanticAI):** Adopted this framework for LLM orchestration with strict typing.
*   **ADR-003 (FastAPI):** Selected for the backend due to its speed and automatic validation.
*   **ADR-004 (Local Inference):** Decision to use Ollama to guarantee total privacy.
*   **ADR-005 (LangChain for Ingestion):** Limited use exclusively for document processing (PDF/EPub).
