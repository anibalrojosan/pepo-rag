# Development Log: PepoRAG

This document describes the development process of the **PepoRAG** project. It serves as a record of decisions made, lessons learned, problems encountered and resolved, and overall progress.

📑 Table of contents
* [[2026-03-13] - Phase 2.3: Runtime Model Routing and Reliability Fallback](#2026-03-13---phase-23-runtime-model-routing-and-reliability-fallback)
* [[2026-03-11] - Refactor: Project Restructuring and Multi-Service Orchestration](#2026-03-11---refactor-project-restructuring-and-multi-service-orchestration)
* [[2026-02-28] - Phase 2.2: RAG Quality Evals and JSON Compliance](#2026-02-28---phase-22-rag-quality-evals-and-json-compliance)
* [[2026-02-27] - Phase 2.1: Automated Performance Benchmarking](#2026-02-27---phase-21-automated-performance-benchmarking)
* [[2026-02-24] - Phase 1: Foundation and Local Inference](#2026-02-24---phase-1-foundation-and-local-inference)
* [[2026-02-23] - Strategic Definition and Initial Architecture](#2026-02-23---strategic-definition-and-initial-architecture)

---

## [2026-03-13] - Phase 2.3: Runtime Model Routing and Reliability Fallback
**Context & Goals:**
Implemented a dynamic model routing policy (Sprint `phase2-03`) to optimize the balance between inference speed and reasoning quality on limited local hardware (GTX 1050 3GB). The goal is to use the fastest model for simple tasks while reserving more capable models for complex technical reasoning.

### Technical Implementation
*   **Model Router:** Created `backend/app/core/model_router.py` with a simple heuristic-based routing (query length > 150 chars or presence of complex keywords like "compare", "architect", "why").
*   **Agent Factory Integration:** Updated `backend/app/core/agent_factory.py` to dynamically select models (`granite3-dense:2b` vs `qwen2.5:3b`) based on the user query.
*   **Reliability Layer:** Implemented `backend/app/core/rag_service.py` with an automated fallback mechanism. If the primary model fails (e.g., JSON validation error), the system retries with the alternate model.
*   **Observability:** Added structured logging to track routing decisions and fallback events in the backend logs.
*   **Verification Tooling:** Added `make test-routing` to the root `Makefile` for automated validation of the routing heuristics.

### 💡 Deep Dive: Performance and Resource Efficiency of Heuristic Routing
During implementation, the efficiency of the heuristic-based router was validated using the `time` utility. The results shown that a code-based it's fast enough for this task. LLM-based router would be slower and more resource-intensive, but will be evaluated in the future:
1.  **Latency Overhead:** The router logic adds only **~0.33s** of total elapsed time (including Docker overhead), with only **~70ms** of actual CPU processing.
2.  **Memory Footprint:** The routing process has a peak resident memory (RSS) of only **~28MB**, ensuring it doesn't compete for VRAM or system RAM with the inference engine.
3.  **Deterministic Reliability:** Unlike using a "router LLM", the heuristic approach is 100% deterministic and adds zero inference cost, preserving all available VRAM for the actual RAG task. It may be enough for the MVP.
4.  **Fallback Logic:** The ternary fallback condition (`fallback_model = REASONING_MODEL if primary_model == FAST_MODEL else FAST_MODEL`) ensures that even if the lightweight model fails the `RagResponse` contract, the system has a second chance with a more robust model.

### Next Steps
*   Begin Phase 3: Data Layer & Ingestion.
*   Implement the document chunking strategy for technical literature.

---

## [2026-03-11] - Refactor: Project Restructuring and Multi-Service Orchestration
**Context & Goals:**
The project was restructured to decouple the Backend and Frontend into independent services. This move improves scalability, simplifies dependency management with `uv` workspaces, and prepares the infrastructure for a multi-container production-like environment.

### Technical Implementation
*   **Decoupled Architecture:** Created `backend/` and `frontend/` directories, moving existing FastAPI logic and Streamlit code respectively.
*   **Docker Orchestration:** Updated `docker-compose.yml` to manage three distinct services: `peporag-db` (PostgreSQL/pgvector), `peporag-backend` (FastAPI), and `peporag-frontend` (Streamlit).
*   **Environment Centralization:** Consolidated configuration into a single root `.env` file, using symbolic links and Docker `env_file` directives to ensure consistency across services.
*   **Automation:** Introduced a root `Makefile` to simplify common tasks like `make up`, `make down`, and `make health`.
*   **Dependency Management:** Migrated to a multi-project structure where each service maintains its own `pyproject.toml` and `uv.lock`.
*   **Retrieval Strategy:** Defined the evolutionary roadmap for the retrieval engine (Vector -> Hybrid -> GraphRAG) and documented it in `ADR-006` and `docs/ROADMAP.md`.

### 💡 Deep Dive: Docker Multi-Service Configuration
To successfully lift the three services, we implemented several key Docker patterns:
1.  **Build Contexts:** Used specific `context` paths for `backend/` and `frontend/` to keep images lean, copying only relevant source code.
2.  **Internal Networking:** Leveraged Docker's default bridge network, allowing the frontend to communicate with the backend using the service name (`http://backend:8000`) instead of hardcoded IPs.
3.  **Variable Interpolation:** Solved the `.env` visibility issue by ensuring Docker Compose reads the root `.env` for YAML variable substitution (e.g., `${POSTGRES_PORT}`), while passing the same file to containers for runtime environment variables.
4.  **Healthcheck Strategy:** Integrated a native PostgreSQL healthcheck for the database and established a pattern for manual/automated health verification of the API and UI services.

### Next Steps
*   Complete the migration of `scripts/` and `tests/` into the `backend/` directory.
*   Implement the evolutionary retrieval roadmap (Hybrid Search) as defined in `ADR-006`.
*   Begin Phase 2.3: Document Ingestion Pipeline.

---

## [2026-02-28] - Phase 2.2: RAG Quality Evals and JSON Compliance
**Context:** Implementation of structured quality evaluation for RAG responses, focused on strict JSON contract compliance under real local-model variability.

### Task 1: Golden Dataset and Evaluation Workflow
*   **Golden Questions:** Finalized a 5-question dataset covering synthesis, extraction, faithfulness, multi-hop reasoning, and instruction-following.
*   **Evaluation Script:** Built `scripts/eval_rag_quality.py` and `scripts/eval_rag_quality_raw_qwen.py` to run repeatable model evals using local Ollama models.
*   **Results Artifacts:** Persisted outputs in `docs/rag_eval_results.json` and `docs/rag_eval_results_qwen_raw.json`.

### Task 2: JSON Compliance Diagnostics
*   **Breaking API Adaptation:** Updated evaluation logic for current `pydantic-ai` behavior (`output_type`, `result.output`) to prevent false negatives.
*   **Dual Compliance Metrics:** Introduced layered metrics:
    *   `json_parse_rate`
    *   `native_schema_valid_rate`
    *   `normalized_schema_valid_rate`
*   **Root Cause Finding:** Confirmed Qwen outputs are usually parseable JSON but frequently non-canonical for strict `RagResponse` validation.

### Task 3: Normalization Strategy for Qwen
*   **Deterministic Adapter:** Implemented `normalize_qwen_payload(...)` to map heterogeneous Qwen output shapes into canonical `RagResponse`.
*   **Coverage of Real Shapes:** Added mapping rules for `answer`, `output`, nested `response`, escaped JSON strings, and model-choice rationale payloads.
*   **Outcome:** Achieved stable, schema-compliant responses post-normalization while preserving native compliance visibility.

### Task 4: Documentation and Explainability
*   **Experiment Criteria:** Added explicit acceptance criteria and metric semantics to `docs/EXPERIMENTATION.md`.
*   **Technical Explainability Notebook:** Created `notebooks/qwen_normalization_explainer.ipynb` to show:
    *   real raw outputs,
    *   native validation failures,
    *   normalization logic,
    *   final canonical outputs.

### Phase 2.2 Update (Production Evaluation Criteria)

During the final stage of `phase2-02`, the RAG quality evaluation was updated to prioritize **application-level contract reliability** over raw JSON strictness. The benchmark now treats `canonical_valid_rate` as the primary decision metric for production readiness.

Key updates:
- Added **`canonical_valid_rate`** as the main success metric for model selection in the app.
- Introduced **plain-text adaptation** for models that return useful answers without strict JSON structure (notably Granite), so outputs can still be validated against the canonical `RagResponse` schema.
- Kept diagnostic layers (`json_parse_rate`, `native_schema_valid_rate`, `normalized_json_schema_valid_rate`) for transparency, but shifted decision logic to canonical contract compliance.
- Updated interpretation of model results: selection now reflects real backend behavior (final canonical payload), not only native JSON formatting behavior.

---

## [2026-02-27] - Phase 2.1: Automated Performance Benchmarking
**Context:** Transition from manual model checks to a repeatable benchmark workflow aligned with constrained local hardware (GTX 1050, 3GB VRAM).

### Task 1: Benchmark Automation
*   **Benchmark Script:** Implemented automated model benchmarking in `scripts/benchmark_models.py`.
*   **Metrics Tracked:** Standardized collection for TTFT, TPS, and average response duration across multiple runs.
*   **Structured Output:** Persisted benchmark data in JSON (`docs/benchmark_results.json`) for reproducibility and post-analysis.

### Task 2: Candidate Model Execution
*   **Models Evaluated:** Benchmarked practical local candidates including `qwen2.5:3b`, `granite3-dense:2b`, and Llama variants.
*   **Hardware-Aware Findings:** Confirmed larger models (>3B effective footprint on this setup) incur high latency and low throughput due to VRAM constraints.
*   **Performance Baseline:** Established Granite 2B as latency leader and Qwen 3B as a quality/speed balance candidate.

### Task 3: Documentation of Results
*   **Experiment Report Update:** Incorporated benchmark comparison tables into `docs/EXPERIMENTATION.md`.
*   **Selection Readiness:** Produced quantitative evidence to support moving to quality/compliance validation in Phase 2.2.

**Current Status:** Phase 2.1 is complete. The project now has reproducible, objective performance baselines that feed directly into final model-selection decisions.

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
