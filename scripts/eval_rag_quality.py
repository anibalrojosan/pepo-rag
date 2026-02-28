import asyncio
import json
import time
from typing import List, Dict, Any
from pathlib import Path
import sys
import os

# Add the project root to sys.path to allow imports from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.agent_factory import get_rag_agent
from app.schemas.rag_response import RagResponse

# Configuration
GOLDEN_DATASET_PATH = Path("tests/data/golden_questions.json")
MODELS_TO_TEST = ["ollama:qwen2.5:3b", "ollama:granite3-dense:2b"]
OUTPUT_FILE = Path("docs/rag_eval_results.json")

def normalize_payload(parsed_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map heterogeneous model JSON shapes into the canonical RagResponse schema.
    """
    normalized: Dict[str, Any] = {}

    answer = None

    # 1) answer direct
    answer_value = parsed_json.get("answer")
    if isinstance(answer_value, str) and answer_value.strip():
        answer = answer_value.strip()

    # 2) output string
    if answer is None:
        output_value = parsed_json.get("output")
        if isinstance(output_value, str) and output_value.strip():
            answer = output_value.strip()

    # 3) output.value
    if answer is None:
        output_value = parsed_json.get("output")
        if isinstance(output_value, dict):
            nested_value = output_value.get("value")
            if isinstance(nested_value, str) and nested_value.strip():
                answer = nested_value.strip()

    # 4-8) response-based variants
    response_value = parsed_json.get("response")

    # 4) response.explanation list of strings
    if answer is None and isinstance(response_value, dict):
        explanation = response_value.get("explanation")
        if isinstance(explanation, list):
            parts = [x.strip() for x in explanation if isinstance(x, str) and x.strip()]
            if parts:
                answer = " ".join(parts)

    # 5) response.utterance
    if answer is None and isinstance(response_value, dict):
        utterance = response_value.get("utterance")
        if isinstance(utterance, str) and utterance.strip():
            answer = utterance.strip()

    # 6) response as string (try nested JSON first)
    if answer is None and isinstance(response_value, str) and response_value.strip():
        response_text = response_value.strip()
        if response_text.startswith("{"):
            try:
                nested = json.loads(response_text)
                if isinstance(nested, dict):
                    nested_text = nested.get("text") or nested.get("answer") or nested.get("value")
                    if isinstance(nested_text, str) and nested_text.strip():
                        answer = nested_text.strip()
            except Exception:
                pass
        if answer is None:
            answer = response_text

    # 7) output.model_chosen + output.rationale
    if answer is None:
        output_value = parsed_json.get("output")
        if isinstance(output_value, dict):
            model_chosen = output_value.get("model_chosen")
            rationale = output_value.get("rationale")
            chunks = []
            if isinstance(model_chosen, str) and model_chosen.strip():
                chunks.append(f"Model chosen: {model_chosen.strip()}.")
            if isinstance(rationale, str) and rationale.strip():
                chunks.append(rationale.strip())
            if chunks:
                answer = " ".join(chunks)

    # 8) response.answers[].text
    if answer is None and isinstance(response_value, dict):
        answers = response_value.get("answers")
        if isinstance(answers, list):
            texts = [
                item.get("text").strip()
                for item in answers
                if isinstance(item, dict)
                and isinstance(item.get("text"), str)
                and item.get("text").strip()
            ]
            if texts:
                answer = ", ".join(texts)

    # 9) output list (e.g. ["Atomicity", "Consistency", "Durability"])
    if answer is None:
        output_value = parsed_json.get("output")
        if isinstance(output_value, list):
            parts = []
            for item in output_value:
                if isinstance(item, str):
                    cleaned = item.strip().strip('"')
                    if cleaned:
                        parts.append(cleaned)
            if parts:
                answer = ", ".join(parts)

    # 10) output with alternative keys used by some models
    if answer is None:
        output_value = parsed_json.get("output")
        if isinstance(output_value, dict):
            selection = output_value.get("selection")
            justification = output_value.get("justification")
            chunks = []
            if isinstance(selection, str) and selection.strip():
                chunks.append(f"Model chosen: {selection.strip()}.")
            if isinstance(justification, str) and justification.strip():
                chunks.append(justification.strip())
            if chunks:
                answer = " ".join(chunks)

    normalized["answer"] = answer if isinstance(answer, str) and answer.strip() else "No answer provided."

    confidence = parsed_json.get(
        "confidence_score",
        parsed_json.get("confidence", parsed_json.get("score", 0.5)),
    )
    try:
        confidence = float(confidence)
    except Exception:
        confidence = 0.5
    normalized["confidence_score"] = max(0.0, min(1.0, confidence))

    key_terms = parsed_json.get("key_terms")
    if not isinstance(key_terms, list) or not all(isinstance(x, str) for x in key_terms):
        key_terms = []
    normalized["key_terms"] = key_terms

    if "sources_used" in parsed_json:
        sources_used = bool(parsed_json["sources_used"])
    elif "source" in parsed_json:
        sources_used = parsed_json["source"] is not None
    else:
        sources_used = True
    normalized["sources_used"] = sources_used

    reasoning = parsed_json.get("reasoning")
    normalized["reasoning"] = reasoning if isinstance(reasoning, str) and reasoning.strip() else None

    return normalized

def normalize_text_output(raw_text: str) -> Dict[str, Any]:
    """
    Build a canonical payload from plain-text responses.
    This is used when a model returns useful text but not JSON.
    """
    text = raw_text.strip()
    return {
        "answer": text if text else "No answer provided.",
        "confidence_score": 0.5,
        "key_terms": [],
        "sources_used": True,
        "reasoning": None,
    }

async def run_single_eval(agent, question_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs a single evaluation for a specific question.
    """
    question = question_data["question"]
    context = question_data["context"]
    
    # Construct the prompt with context
    prompt = f"""
    Context:
    {context}
    
    Question:
    {question}
    """
    
    start_time = time.time()
    try:
        # Use raw text output to evaluate native vs normalized schema compliance.
        result = await agent.run(prompt, output_type=str)
        duration = time.time() - start_time

        raw_text: str = result.output

        # Parse raw output as JSON first.
        parsed_json = None
        json_ok = False
        json_error = None
        try:
            parsed_json = json.loads(raw_text)
            json_ok = True
        except Exception as je:
            json_error = str(je)

        # Validation layers:
        # 1) native schema on parsed JSON
        # 2) normalized JSON schema on parsed JSON
        # 3) canonical schema for production contract (JSON if available, else text adapter)
        native_schema_ok = False
        native_schema_error = None
        native_response = None

        normalized_json_schema_ok = False
        normalized_json_schema_error = None
        normalized_json_response = None

        canonical_ok = False
        canonical_error = None
        canonical_response = None
        normalized_json = None
        canonical_payload = None

        if json_ok:
            try:
                native_response = RagResponse.model_validate(parsed_json)
                native_schema_ok = True
            except Exception as ve:
                native_schema_error = str(ve)

            try:
                normalized_json = normalize_payload(parsed_json)
                normalized_json_response = RagResponse.model_validate(normalized_json)
                normalized_json_schema_ok = True
            except Exception as ve:
                normalized_json_schema_error = str(ve)

        # Canonical (production) contract:
        # - use normalized JSON when available
        # - otherwise adapt raw plain text into canonical payload
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
    except Exception as e:
        duration = time.time() - start_time
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

async def evaluate_model(model_name: str, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates a single model against the full dataset.
    """
    print(f"Starting evaluation for model: {model_name}")
    agent = get_rag_agent(model_name)
    
    results = []
    json_ok_count = 0
    native_schema_ok_count = 0
    normalized_json_schema_ok_count = 0
    canonical_ok_count = 0
    native_total_duration = 0
    normalized_json_total_duration = 0
    canonical_total_duration = 0
    
    for q in questions:
        print(f"  - Testing question: {q['id']}...")
        eval_result = await run_single_eval(agent, q)
        
        eval_result["question_id"] = q["id"]
        results.append(eval_result)
        
        if eval_result["json_ok"]:
            json_ok_count += 1
        if eval_result["native_schema_ok"]:
            native_schema_ok_count += 1
            native_total_duration += eval_result["duration"]
        if eval_result["normalized_json_schema_ok"]:
            normalized_json_schema_ok_count += 1
            normalized_json_total_duration += eval_result["duration"]
        if eval_result["canonical_ok"]:
            canonical_ok_count += 1
            canonical_total_duration += eval_result["duration"]

    avg_latency_native = native_total_duration / native_schema_ok_count if native_schema_ok_count > 0 else 0
    avg_latency_normalized_json = (
        normalized_json_total_duration / normalized_json_schema_ok_count if normalized_json_schema_ok_count > 0 else 0
    )
    avg_latency_canonical = canonical_total_duration / canonical_ok_count if canonical_ok_count > 0 else 0
    json_parse_rate = (json_ok_count / len(questions)) * 100
    native_schema_valid_rate = (native_schema_ok_count / len(questions)) * 100
    normalized_json_schema_valid_rate = (normalized_json_schema_ok_count / len(questions)) * 100
    canonical_valid_rate = (canonical_ok_count / len(questions)) * 100
    
    return {
        "model": model_name,
        "json_parse_rate": json_parse_rate,
        "native_schema_valid_rate": native_schema_valid_rate,
        "normalized_json_schema_valid_rate": normalized_json_schema_valid_rate,
        "canonical_valid_rate": canonical_valid_rate,
        "avg_latency_native": avg_latency_native,
        "avg_latency_normalized_json": avg_latency_normalized_json,
        "avg_latency_canonical": avg_latency_canonical,
        "details": results
    }

async def main():
    if not GOLDEN_DATASET_PATH.exists():
        print(f"Error: Dataset not found at {GOLDEN_DATASET_PATH}")
        return

    with open(GOLDEN_DATASET_PATH, "r") as f:
        questions = json.load(f)
        
    all_results = []
    
    for model in MODELS_TO_TEST:
        model_results = await evaluate_model(model, questions)
        all_results.append(model_results)
        
    # Save results
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_results, f, indent=2)
        
    print(f"\nEvaluation complete. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    print("\n--- SUMMARY ---")
    for res in all_results:
        print(f"Model: {res['model']}")
        print(f"  JSON Parse Rate: {res['json_parse_rate']}%")
        print(f"  Native Schema Valid Rate (RagResponse): {res['native_schema_valid_rate']}%")
        print(f"  Normalized JSON Schema Valid Rate (RagResponse): {res['normalized_json_schema_valid_rate']}%")
        print(f"  Canonical Valid Rate (App Contract): {res['canonical_valid_rate']}%")
        print(f"  Avg Latency (Native): {res['avg_latency_native']:.2f}s")
        print(f"  Avg Latency (Normalized JSON): {res['avg_latency_normalized_json']:.2f}s")
        print(f"  Avg Latency (Canonical): {res['avg_latency_canonical']:.2f}s")
        print("----------------")

if __name__ == "__main__":
    asyncio.run(main())
