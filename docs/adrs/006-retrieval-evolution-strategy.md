# ADR-006: Retrieval Evolution Strategy

## Status
Proposed

## Context
The goal of PepoRAG is to provide highly accurate technical answers from a library of 200+ books. While vector-based retrieval (Semantic Search) is excellent for capturing intent, it often fails at "exact match" scenarios common in technical documentation (e.g., error codes, specific function names, or version numbers). Furthermore, as the library grows, simple similarity may not be enough to reason about complex relationships between different technical concepts.

## Decision
We will implement a three-phased evolutionary strategy for the retrieval engine, leveraging the flexibility of PostgreSQL as our primary data store.

### Phase 1: Vector-Only RAG (MVP)
* **Implementation:** Use `pgvector` for HNSW/IVFFlat indexing and cosine similarity.
* **Rationale:** Fastest time-to-market and handles 70-80% of semantic queries effectively.

### Phase 2: Hybrid Search (Optimization)
* **Implementation:** Combine PostgreSQL Full-Text Search (FTS) with `pgvector` scores using Reciprocal Rank Fusion (RRF) or a simple weighted sum.
* **Rationale:** Fixes the "exact match" problem without changing the database infrastructure.

### Phase 3: Knowledge-Enhanced Retrieval (Advanced)
* **Implementation:** Explore GraphRAG techniques by extracting entities and relationships into a graph structure (potentially using a graph extension or a separate store if necessary, though PG can handle basic graph structures).
* **Rationale:** Enables multi-hop reasoning and better understanding of architectural relationships across multiple books.

## Consequences
* **Positive:** We avoid "over-engineering" at the start while ensuring the architecture (PostgreSQL) can support future phases.
* **Positive:** Improved accuracy for technical users who rely on precise terminology.
* **Negative:** Increased complexity in the retrieval logic as we move to Phase 2 and 3.
* **Negative:** Higher computational cost for Phase 3 (LLM-based graph extraction).

## Alternatives Considered
* **Vector-only forever:** Rejected due to known limitations with technical precision.
* **Starting with GraphRAG:** Rejected due to extreme complexity and high initial latency.
