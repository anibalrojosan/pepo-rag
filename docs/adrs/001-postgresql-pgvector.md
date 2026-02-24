# ADR 001: Use of PostgreSQL with pgvector for Vector Storage

## Status
Accepted

## Context
The project requires a storage solution for both relational metadata (book details, user sessions) and high-dimensional vector embeddings generated from technical book chunks. We need a system that is reliable, local, and supports efficient similarity searches.

## Decision
We will use **PostgreSQL** with the **pgvector** extension as our primary database and vector store.

## Rationale
- **Unified Storage:** Allows storing both structured metadata and vector embeddings in the same database, simplifying data management and consistency.
- **Performance:** `pgvector` provides efficient indexing (IVFFlat, HNSW) for vector similarity search, which is critical for RAG performance.
- **Reliability:** PostgreSQL is a mature, production-grade relational database with excellent tooling and community support.
- **Local Deployment:** Easily containerized using `docker-compose`, fitting our requirement for 100% local compute.
- **SQL Power:** Enables complex queries that combine relational filters (e.g., "search only in books by author X") with semantic similarity.

## Consequences
- **Infrastructure:** Requires a PostgreSQL instance with the `pgvector` extension installed (available in official Docker images).
- **Complexity:** Developers need to be familiar with SQL and the specific syntax for vector operations in `pgvector`.
- **Resource Usage:** Storing large numbers of embeddings can increase disk and memory usage, requiring careful indexing strategies.
