"""
Golden-set RAG quality evaluation against local Ollama models (PydanticAI agent).

Runs each model on ``backend/tests/data/golden_questions.json`` and writes timestamped JSON
under ``docs/evaluations/rag/``.

Modes:
  * ``full`` — Native JSON vs ``RagResponse``, normalized JSON, then **app contract**
    (normalized dict or plain-text adapter). Reports ``canonical_valid_rate``.
  * ``raw-qwen`` — JSON diagnostics only (native + normalized), **no** plain-text rescue.
    Same shape as the legacy ``eval_rag_quality_raw_qwen.py`` aggregate JSON.

Prerequisites: Ollama running; models pulled; execute from repo with backend on ``PYTHONPATH``
(see commands below — ``uv run`` from ``backend/`` adds the project root).

Examples::

    cd backend
    uv run python scripts/eval_rag_quality.py
    uv run python scripts/eval_rag_quality.py --mode full
    uv run python scripts/eval_rag_quality.py --mode raw-qwen
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from peporag_eval.rag_eval_runner import EvalMode, run_eval


def _parse_mode(value: str) -> EvalMode:
    normalized = value.strip().lower().replace("-", "_")
    if normalized == "full":
        return EvalMode.FULL
    if normalized in ("raw_qwen", "rawqwen"):
        return EvalMode.RAW_QWEN
    raise argparse.ArgumentTypeError(f"unknown mode {value!r}; use 'full' or 'raw-qwen'")


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG golden-set eval (full or raw-qwen JSON diagnostic).")
    parser.add_argument(
        "--mode",
        type=_parse_mode,
        default=EvalMode.FULL,
        help="full (default): app contract + canonical metrics; raw-qwen: JSON native+normalized only",
    )
    args = parser.parse_args()
    out = asyncio.run(run_eval(args.mode))
    if out is None:
        sys.exit(1)


if __name__ == "__main__":
    # Allow ``python scripts/eval_rag_quality.py`` when cwd is backend (optional dotenv, etc.)
    os.chdir(_BACKEND_ROOT)
    main()
