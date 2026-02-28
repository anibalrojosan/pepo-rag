# ADR: Single Canonical Response Schema with Model-Specific Adapters

- **Status:** Accepted
- **Date:** 2026-02-28
- **Related Issues:** `phase2-02: rag-quality-evals-and-json-compliance`, `phase2-03: runtime-model-routing-policy` (planned)

## Context

The RAG assistant integrates multiple local LLMs (e.g., Qwen 3B, Granite 2B) that produce heterogeneous output formats:

- strict JSON-like objects,
- partially structured JSON with non-canonical keys,
- plain text responses.

At the same time, the backend and frontend require a stable and typed contract for downstream processing, rendering, and validation.

The canonical response contract is defined by `RagResponse` and includes mandatory fields such as:

- `answer`
- `confidence_score`
- `sources_used`

Raw model behavior showed strong variability in native schema compliance, especially for smaller local models. However, many non-canonical outputs are still semantically useful and can be safely transformed.

## Decision

We adopt a **single canonical response schema** (`RagResponse`) across the application and implement **model-specific adapters** to map heterogeneous model outputs into that schema.

### Core rules

1. The API contract exposed to the app remains **one schema only** (`RagResponse`).
2. Each model may have a dedicated adapter/normalizer layer before final validation.
3. Final acceptance for production behavior is measured with **canonical contract compliance** (`canonical_valid_rate`), not only raw JSON formatting.
4. Diagnostic metrics (raw JSON parse and native schema compliance) are still collected for transparency and model analysis.

## Rationale

- Preserves a stable interface for frontend and backend integration.
- Decouples product contract from model-specific formatting quirks.
- Enables fair comparison of model usefulness in real app conditions.
- Reduces fragility when switching models or model versions.

## Consequences

### Positive

- Consistent response shape for all consumers.
- Easier long-term maintenance of the API contract.
- Better production robustness with local models that do not consistently emit strict JSON.
- Clear separation between:
  - model behavior diagnostics, and
  - product-level contract validity.

### Trade-offs

- Additional adapter logic per model must be maintained.
- Risk of over-normalization masking native model weaknesses if diagnostics are ignored.
- Requires disciplined observability to detect adapter regressions.

## Validation and Metrics

The evaluation pipeline should report at least:

- `json_parse_rate` (raw JSON parse success),
- `native_schema_valid_rate` (raw payload directly valid),
- `normalized_json_schema_valid_rate` (JSON after normalization),
- `canonical_valid_rate` (final app-contract validity; primary selection metric).

Model selection for production should prioritize:

1. `canonical_valid_rate`,
2. latency under canonical flow,
3. quality/faithfulness checks.

## Alternatives Considered

1. **Single strict raw JSON path only**
  Rejected: penalizes useful models that answer well but do not emit strict schema-compliant JSON.
2. **Different schema per model**
  Rejected: would increase API complexity and leaks model-specific behavior into product boundaries.
3. **Canonical schema with adapters (selected)**
  Accepted: balances stability, flexibility, and practical local-model constraints. The model-specific adapters ensures that the api contract is still respected even when the model does not emit strict JSON.

## Follow-up

- Keep adapter logic observable and testable.
- Reassess adapter complexity when introducing runtime routing.
- Update this ADR if canonical schema fields evolve.

