"""
Local Ollama throughput/latency benchmark (TPS, TTFT).

Calls ``POST /api/generate`` with streaming, several iterations per model, and writes
aggregates to ``docs/benchmark_results.json`` at the **repository** root.

Prerequisites: ``ollama serve`` and models listed in ``peporag_eval.ollama_benchmark``.

Example::

    cd backend
    uv run python scripts/benchmark_models.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from peporag_eval.ollama_benchmark import main

if __name__ == "__main__":
    os.chdir(_BACKEND_ROOT)
    main()
