# ADR 003: Use of FastAPI for REST API

## Status
Accepted

## Context
The application needs a backend API to serve the frontend and handle requests for document management and RAG queries.

## Decision
We will use **FastAPI** as the web framework for our REST API.

## Rationale
- **Performance:** One of the fastest Python frameworks available, built on Starlette and Pydantic.
- **Auto-Documentation:** Automatically generates OpenAPI (Swagger) and Redoc documentation, facilitating frontend-backend integration.
- **Type Safety:** Deep integration with Pydantic ensures data validation and type safety at the API boundaries.
- **Asynchronous Support:** Native support for `async/await`, which is crucial for handling long-running LLM requests without blocking.
- **Ecosystem:** Extremely popular with a vast ecosystem of plugins and middleware.

## Consequences
- **Async Programming:** Requires developers to be comfortable with asynchronous Python programming.
- **Pydantic V2:** We will use Pydantic V2 for better performance and modern features, which is the default in recent FastAPI versions.
