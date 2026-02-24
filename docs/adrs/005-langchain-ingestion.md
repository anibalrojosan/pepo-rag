# ADR 005: Use of LangChain exclusively for Ingestion

## Status
Accepted

## Context
The project needs to process a variety of technical book formats (PDF, EPub, Markdown, etc.), chunk the text appropriately, and generate embeddings. While we've chosen PydanticAI for orchestration, we need a robust set of tools for the initial document processing phase.

## Decision
We will use **LangChain** (specifically its document loaders and text splitters) **exclusively for the ingestion pipeline**.

## Rationale
- **Rich Ecosystem:** LangChain has the most comprehensive collection of document loaders (PDF, EPub, HTML, etc.) in the Python ecosystem.
- **Proven Utilities:** Its text splitters (e.g., `RecursiveCharacterTextSplitter`) are well-tested and handle various edge cases in technical text.
- **Separation of Concerns:** By limiting LangChain to ingestion, we avoid the complexity and "magic" of its orchestration layer for our core RAG logic, which will be handled by PydanticAI.
- **Efficiency:** Allows us to leverage existing, high-quality code for the "heavy lifting" of document parsing without committing to the entire LangChain framework.

## Consequences
- **Dependency Management:** LangChain and its sub-packages (like `langchain-community`) will be included in the project's dependencies.
- **Architecture:** A clear boundary must be maintained between the ingestion code (using LangChain) and the retrieval/generation code (using PydanticAI).
- **Maintenance:** We need to keep LangChain updated to benefit from new loaders and bug fixes in document processing.
