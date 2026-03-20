"""Async RAG golden-set evaluation: FULL (app contract) vs RAW_QWEN (JSON-only diagnostics)."""

import datetime
import json
import time
from enum import StrEnum
from pathlib import Path
from typing import Any

from app.core.agent_factory import get_rag_agent
from app.schemas.rag_response import RagResponse
from peporag_eval.paths import golden_questions_path, rag_eval_output_dir
from peporag_eval.rag_normalize import normalize_payload, normalize_text_output


class EvalMode(StrEnum):
    FULL = "full"
    RAW_QWEN = "raw_qwen"


DEFAULT_MODELS = [
    "ollama:qwen2.5:3b",
    "ollama:qwen3.5:2b",
    "ollama:qwen3:4b",
    "ollama:qwen3:1.7b",
    "ollama:granite3-dense:2b",
]


def new_eval_output_path(mode: EvalMode) -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "eval_results_phase2-04_" if mode == EvalMode.FULL else "qwen_raw_phase2-04_"
    return rag_eval_output_dir() / f"{prefix}{ts}.json"


async def run_single_eval(
    agent,
    question_data: dict[str, Any],
    mode: EvalMode,
) -> dict[str, Any]:
    question = question_data["question"]
    context = question_data["context"]

    prompt = f"""
    Context:
    {context}

    Question:
    {question}
    """

    start_time = time.time()
    try:
        result = await agent.run(prompt, output_type=str)
        duration = time.time() - start_time

        raw_text: str = result.output

        parsed_json = None
        json_ok = False
        json_error = None
        try:
            parsed_json = json.loads(raw_text)
            json_ok = True
        except Exception as je:
            json_error = str(je)

        if mode is EvalMode.RAW_QWEN:
            return _run_single_eval_raw_qwen_body(
                duration=duration,
                raw_text=raw_text,
                parsed_json=parsed_json,
                json_ok=json_ok,
                json_error=json_error,
            )

        return _run_single_eval_full_body(
            duration=duration,
            raw_text=raw_text,
            parsed_json=parsed_json,
            json_ok=json_ok,
            json_error=json_error,
        )
    except Exception as e:
        duration = time.time() - start_time
        if mode is EvalMode.RAW_QWEN:
            return {
                "success": False,
                "duration": duration,
                "json_ok": False,
                "native_schema_ok": False,
                "native_response": None,
                "native_schema_error": None,
                "normalized_schema_ok": False,
                "response": None,
                "normalized_schema_error": None,
                "parsed_json": None,
                "normalized_json": None,
                "raw_output": "",
                "error": str(e),
                "json_error": None,
            }
        return {
            "success": False,
            "duration": duration,
            "json_ok": False,
            "native_schema_ok": False,
            "native_response": None,
            "native_schema_error": None,
            "normalized_json_schema_ok": False,
            "normalized_json_schema_error": None,
            "canonical_ok": False,
            "canonical_response": None,
            "canonical_error": None,
            "response": None,
            "parsed_json": None,
            "normalized_json": None,
            "canonical_payload": None,
            "raw_output": "",
            "error": str(e),
            "json_error": None,
        }


def _run_single_eval_full_body(
    *,
    duration: float,
    raw_text: str,
    parsed_json: dict[str, Any] | None,
    json_ok: bool,
    json_error: str | None,
) -> dict[str, Any]:
    native_schema_ok = False
    native_schema_error = None
    native_response = None

    normalized_json_schema_ok = False
    normalized_json_schema_error = None

    canonical_ok = False
    canonical_error = None
    canonical_response = None
    normalized_json: dict[str, Any] | None = None
    canonical_payload = None

    if json_ok and parsed_json is not None:
        try:
            native_response = RagResponse.model_validate(parsed_json)
            native_schema_ok = True
        except Exception as ve:
            native_schema_error = str(ve)

        try:
            normalized_json = normalize_payload(parsed_json)
            RagResponse.model_validate(normalized_json)
            normalized_json_schema_ok = True
        except Exception as ve:
            normalized_json_schema_error = str(ve)

    try:
        canonical_payload = normalized_json if normalized_json is not None else normalize_text_output(raw_text)
        canonical_response = RagResponse.model_validate(canonical_payload)
        canonical_ok = True
    except Exception as ve:
        canonical_error = str(ve)

    return {
        "success": canonical_ok,
        "duration": duration,
        "json_ok": json_ok,
        "native_schema_ok": native_schema_ok,
        "native_response": native_response.model_dump() if native_response else None,
        "native_schema_error": native_schema_error,
        "normalized_json_schema_ok": normalized_json_schema_ok,
        "normalized_json_schema_error": normalized_json_schema_error,
        "canonical_ok": canonical_ok,
        "canonical_response": canonical_response.model_dump() if canonical_response else None,
        "canonical_error": canonical_error,
        "response": canonical_response.model_dump() if canonical_response else None,
        "parsed_json": parsed_json,
        "normalized_json": normalized_json,
        "canonical_payload": canonical_payload,
        "raw_output": raw_text,
        "error": canonical_error or normalized_json_schema_error or native_schema_error or json_error,
        "json_error": json_error,
    }


def _run_single_eval_raw_qwen_body(
    *,
    duration: float,
    raw_text: str,
    parsed_json: dict[str, Any] | None,
    json_ok: bool,
    json_error: str | None,
) -> dict[str, Any]:
    native_schema_ok = False
    native_schema_error = None
    native_response = None

    normalized_schema_ok = False
    normalized_schema_error = None
    normalized_response = None
    normalized_json = None

    if json_ok and parsed_json is not None:
        try:
            native_response = RagResponse.model_validate(parsed_json)
            native_schema_ok = True
        except Exception as ve:
            native_schema_error = str(ve)

        try:
            normalized_json = normalize_payload(parsed_json)
            normalized_response = RagResponse.model_validate(normalized_json)
            normalized_schema_ok = True
        except Exception as ve:
            normalized_schema_error = str(ve)

    return {
        "success": normalized_schema_ok,
        "duration": duration,
        "json_ok": json_ok,
        "native_schema_ok": native_schema_ok,
        "native_response": native_response.model_dump() if native_response else None,
        "native_schema_error": native_schema_error,
        "normalized_schema_ok": normalized_schema_ok,
        "response": normalized_response.model_dump() if normalized_response else None,
        "normalized_schema_error": normalized_schema_error,
        "parsed_json": parsed_json,
        "normalized_json": normalized_json,
        "raw_output": raw_text,
        "error": normalized_schema_error or native_schema_error or json_error,
        "json_error": json_error,
    }


async def evaluate_model(model_name: str, questions: list[dict[str, Any]], mode: EvalMode) -> dict[str, Any]:
    print(f"Starting evaluation for model: {model_name}")
    agent = get_rag_agent(model_name=model_name)

    results = []
    json_ok_count = 0
    native_schema_ok_count = 0
    normalized_json_schema_ok_count = 0
    normalized_schema_ok_count = 0
    canonical_ok_count = 0
    native_total_duration = 0
    normalized_json_total_duration = 0
    normalized_total_duration = 0
    canonical_total_duration = 0

    for q in questions:
        print(f"  - Testing question: {q['id']}...")
        eval_result = await run_single_eval(agent, q, mode)

        eval_result["question_id"] = q["id"]
        results.append(eval_result)

        if eval_result["json_ok"]:
            json_ok_count += 1
        if eval_result["native_schema_ok"]:
            native_schema_ok_count += 1
            native_total_duration += eval_result["duration"]

        if mode is EvalMode.FULL:
            if eval_result.get("normalized_json_schema_ok"):
                normalized_json_schema_ok_count += 1
                normalized_json_total_duration += eval_result["duration"]
            if eval_result.get("canonical_ok"):
                canonical_ok_count += 1
                canonical_total_duration += eval_result["duration"]
        else:
            if eval_result.get("normalized_schema_ok"):
                normalized_schema_ok_count += 1
                normalized_total_duration += eval_result["duration"]

    n = len(questions)
    json_parse_rate = (json_ok_count / n) * 100
    native_schema_valid_rate = (native_schema_ok_count / n) * 100
    avg_latency_native = native_total_duration / native_schema_ok_count if native_schema_ok_count > 0 else 0

    if mode is EvalMode.FULL:
        avg_latency_normalized_json = (
            normalized_json_total_duration / normalized_json_schema_ok_count
            if normalized_json_schema_ok_count > 0
            else 0
        )
        avg_latency_canonical = canonical_total_duration / canonical_ok_count if canonical_ok_count > 0 else 0
        normalized_json_schema_valid_rate = (normalized_json_schema_ok_count / n) * 100
        canonical_valid_rate = (canonical_ok_count / n) * 100
        return {
            "model": model_name,
            "json_parse_rate": json_parse_rate,
            "native_schema_valid_rate": native_schema_valid_rate,
            "normalized_json_schema_valid_rate": normalized_json_schema_valid_rate,
            "canonical_valid_rate": canonical_valid_rate,
            "avg_latency_native": avg_latency_native,
            "avg_latency_normalized_json": avg_latency_normalized_json,
            "avg_latency_canonical": avg_latency_canonical,
            "details": results,
        }

    avg_latency_normalized = (
        normalized_total_duration / normalized_schema_ok_count if normalized_schema_ok_count > 0 else 0
    )
    normalized_schema_valid_rate = (normalized_schema_ok_count / n) * 100
    return {
        "model": model_name,
        "json_parse_rate": json_parse_rate,
        "native_schema_valid_rate": native_schema_valid_rate,
        "normalized_schema_valid_rate": normalized_schema_valid_rate,
        "avg_latency_native": avg_latency_native,
        "avg_latency_normalized": avg_latency_normalized,
        "details": results,
    }


def _print_summary(all_results: list[dict[str, Any]], mode: EvalMode) -> None:
    print("\n--- SUMMARY ---")
    for res in all_results:
        print(f"Model: {res['model']}")
        print(f"  JSON Parse Rate: {res['json_parse_rate']}%")
        print(f"  Native Schema Valid Rate (RagResponse): {res['native_schema_valid_rate']}%")
        if mode is EvalMode.FULL:
            print(f"  Normalized JSON Schema Valid Rate (RagResponse): {res['normalized_json_schema_valid_rate']}%")
            print(f"  Canonical Valid Rate (App Contract): {res['canonical_valid_rate']}%")
            print(f"  Avg Latency (Native): {res['avg_latency_native']:.2f}s")
            print(f"  Avg Latency (Normalized JSON): {res['avg_latency_normalized_json']:.2f}s")
            print(f"  Avg Latency (Canonical): {res['avg_latency_canonical']:.2f}s")
        else:
            print(f"  Normalized Schema Valid Rate (RagResponse): {res['normalized_schema_valid_rate']}%")
            print(f"  Avg Latency (Native): {res['avg_latency_native']:.2f}s")
            print(f"  Avg Latency (Normalized): {res['avg_latency_normalized']:.2f}s")
        print("----------------")


async def run_eval(mode: EvalMode, models: list[str] | None = None) -> Path | None:
    golden = golden_questions_path()
    if not golden.exists():
        print(f"Error: Dataset not found at {golden}")
        return None

    with open(golden) as f:
        questions = json.load(f)

    model_list = models if models is not None else DEFAULT_MODELS
    all_results = []
    for model in model_list:
        model_results = await evaluate_model(model, questions, mode)
        all_results.append(model_results)

    output_file = new_eval_output_path(mode)
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nEvaluation complete. Results saved to {output_file}")
    _print_summary(all_results, mode)
    return output_file
