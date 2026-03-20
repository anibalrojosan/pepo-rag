"""
Compatibility shim for the JSON-only RAG eval (legacy entrypoint).

Prefer::

    cd backend && uv run python scripts/eval_rag_quality.py --mode raw-qwen

This file delegates to the same runner as ``eval_rag_quality.py`` with ``EvalMode.RAW_QWEN``.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from peporag_eval.rag_eval_runner import EvalMode, run_eval


def main() -> None:
    out = asyncio.run(run_eval(EvalMode.RAW_QWEN))
    if out is None:
        sys.exit(1)


if __name__ == "__main__":
    os.chdir(_BACKEND_ROOT)
    main()
