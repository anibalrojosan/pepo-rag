# ADR 002: Use of PydanticAI for LLM Orchestration

## Status
Accepted

## Context
We need a robust framework to orchestrate the RAG flow, including managing prompts, handling LLM responses, and ensuring type safety throughout the application logic.

## Decision
We will use **PydanticAI** as our primary framework for LLM orchestration.

## Rationale
- **Type Safety:** Built on top of Pydantic, it provides strict type checking for LLM inputs and outputs, reducing runtime errors.
- **Structured Outputs:** Simplifies the process of getting structured data from LLMs, which is essential for complex RAG tasks.
- **Developer Experience:** Offers a clean, Pythonic API that integrates well with modern Python practices (FastAPI, Pydantic).
- **Control:** Provides more granular control over the agentic flow compared to more "magical" frameworks like LangChain, which we prefer for the core logic.
- **Modern Design:** Designed specifically for the current generation of LLMs and tool-calling capabilities.

## Consequences
- **Learning Curve:** Team members need to familiarize themselves with PydanticAI's specific patterns (Agents, Tools, Dependencies).
- **Ecosystem:** While growing, the PydanticAI ecosystem is smaller than LangChain's, meaning fewer pre-built integrations.
- **Integration:** Requires manual implementation of some RAG patterns that might be "out-of-the-box" in other frameworks.
