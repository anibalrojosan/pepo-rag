"""Filesystem paths for benchmarks and RAG eval artifacts (repo-root relative)."""

from pathlib import Path


def repo_root() -> Path:
    """Repository root (parent of ``backend/``)."""
    return Path(__file__).resolve().parents[2]


def golden_questions_path() -> Path:
    return repo_root() / "backend" / "tests" / "data" / "golden_questions.json"


def benchmark_results_path() -> Path:
    return repo_root() / "docs" / "benchmark_results.json"


def rag_eval_output_dir() -> Path:
    out = repo_root() / "docs" / "evaluations" / "rag"
    out.mkdir(parents=True, exist_ok=True)
    return out
