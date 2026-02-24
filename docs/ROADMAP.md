# Development Roadmap - PepoRAG

This roadmap details the development phases for building the local RAG assistant, prioritizing retrieval quality and response speed on local hardware.

## Phase 1: Foundation & Environment (Setup)
- [ ] **Project Configuration:** Initialize with `uv` and create `pyproject.toml`.
- [ ] **Infrastructure:** Configure `docker-compose` for PostgreSQL + `pgvector`.
- [ ] **LLM Environment:** Setup Ollama and download base models (Qwen2.5, Llama 3.1, Phi-3.5).

## Phase 2: Model Experimentation & Selection (Model Benchmarking)
- [ ] **Speed Benchmark:** Measure tokens/second on local hardware for different models.
- [ ] **Quality Evaluation (Evals):** Implement faithfulness and instruction-following (JSON) tests.
- [ ] **Final Selection:** Document recommended models based on speed/accuracy trade-offs.

## Phase 3: Data Layer & Ingestion (Ingestion Pipeline)
- [ ] **DB Schema:** Define PostgreSQL tables for documents, chunks, and embeddings.
- [ ] **Document Processing:** Implement LangChain loaders for PDF and EPub.
- [ ] **Chunking Strategy:** Optimize fragmentation for technical content.
- [ ] **Vectorization:** Generate and store embeddings in `pgvector`.

## Phase 4: RAG Orchestration (Core Logic)
- [ ] **PydanticAI Agents:** Design the technical assistant agent.
- [ ] **Retrieval Tools:** Implement semantic search as an agent tool.
- [ ] **Citation System:** Logic to reference exact books and pages in responses.

## Phase 5: Backend API (FastAPI)
- [ ] **Query Endpoints:** Create `/ask` with streaming support.
- [ ] **Management Endpoints:** APIs for book uploads and ingestion monitoring.
- [ ] **Local Security:** Implement basic data integrity validations.

## Phase 6: Frontend (Streamlit)
- [ ] **Chat Interface:** Create a fluid and modern UI with Streamlit.
- [ ] **Document Viewer:** Display retrieved chunks and book metadata.
- [ ] **Ingestion Dashboard:** Interface for users to manage their local library.

## Phase 7: Optimization & MVP
- [ ] **Retrieval Refinement:** Implement Hybrid Search (BM25 + Vector) and Re-ranking.
- [ ] **User Testing:** Validate with real-world technical book use cases.
- [ ] **Final Documentation:** "One-click" deployment guide for local users.
