# Product Requirements Document (PRD) - PepoRAG

## 1. Problem Definition
Developers and tech enthusiasts often have large collections of technical books (PDFs, EPubs, etc.) that are difficult to search through effectively. Traditional keyword search fails to capture semantic meaning, making it hard to find specific technical solutions or concepts across hundreds of volumes. Existing RAG solutions often rely on cloud providers, raising privacy concerns and incurring ongoing costs.

## 2. Target Users
- **Software Engineers:** Looking for specific implementation details or architectural patterns.
- **System Architects:** Researching best practices and historical context of technologies.
- **Students/Researchers:** Navigating vast amounts of technical literature.

## 3. MVP User Stories
- **As a user**, I want to upload or point to a directory of technical books so they can be indexed.
- **As a user**, I want to ask questions in natural language and receive answers based on my book library.
- **As a user**, I want to see citations and references to the specific books and pages used to generate the answer.
- **As a user**, I want all processing and storage to happen locally on my machine to ensure privacy.

## 4. Success Metrics
- **Accuracy:** The system provides relevant answers with correct citations for at least 80% of technical queries.
- **Performance:** Response time for queries (including retrieval and generation) is under 10 seconds on recommended local hardware.
- **Privacy:** 100% of data remains local; zero external API calls for data processing.

## 5. Development Roadmap

### Phase 1: Foundation & Environment (Setup)
- Setup project structure with `uv`.
- Configure `docker-compose` for PostgreSQL + `pgvector`.
- LLM Environment: Setup Ollama and download base models.

### Phase 2: Model Experimentation & Selection
- Performance Benchmarking: Measure tokens/sec on local hardware.
- Quality Evaluation (Evals): Implement faithfulness and instruction-following tests.
- Final Selection: Document recommended models based on speed/accuracy trade-offs.

### Phase 3: Data Layer & Ingestion
- Database Schema: Define tables for documents, chunks, and embeddings.
- Document Processing: Implement LangChain loaders for PDF and EPub.
- Chunking Strategy: Optimize fragmentation for technical content.
- Vectorization: Generate and store embeddings in `pgvector`.

### Phase 4: RAG Orchestration (Core Logic)
- PydanticAI Agents: Design the technical assistant agent.
- Retrieval Tools: Implement semantic search as an agent tool.
- Citation System: Logic to reference exact books and pages in responses.

### Phase 5: Backend API (FastAPI)
- Query Endpoints: Create `/ask` with streaming support.
- Management Endpoints: APIs for book uploads and ingestion monitoring.

### Phase 6: Frontend (Streamlit)
- Chat Interface: Create a fluid and modern UI with Streamlit.
- Document Viewer: Display retrieved chunks and book metadata.
- Ingestion Dashboard: Interface for users to manage their local library.

### Phase 7: Optimization & MVP
- Retrieval Refinement: Implement Hybrid Search and Re-ranking.
- User Testing: Validate with real-world technical book use cases.
- Final Documentation: "One-click" deployment guide for local users.
