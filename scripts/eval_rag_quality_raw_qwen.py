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
MODELS_TO_TEST = ["ollama:qwen2.5:3b"]
OUTPUT_FILE = Path("docs/rag_eval_results_qwen_raw.json")

def normalize_qwen_payload(parsed_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map variable Qwen JSON shapes into the canonical RagResponse-compatible dict.
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
        # Force text output to inspect what Qwen really returns
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

        # Validate parsed JSON in two passes:
        # 1) native schema compliance, 2) schema compliance after normalization.
        native_schema_ok = False
        native_schema_error = None
        native_response = None

        normalized_schema_ok = False
        normalized_schema_error = None
        normalized_response = None
        normalized_json = None

        if json_ok:
            try:
                native_response = RagResponse.model_validate(parsed_json)
                native_schema_ok = True
            except Exception as ve:
                native_schema_error = str(ve)

            try:
                normalized_json = normalize_qwen_payload(parsed_json)
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

    except Exception as e:
        duration = time.time() - start_time
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
            "error": str(e)
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
    normalized_schema_ok_count = 0
    native_total_duration = 0
    normalized_total_duration = 0
    
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
        if eval_result["normalized_schema_ok"]:
            normalized_schema_ok_count += 1
            normalized_total_duration += eval_result["duration"]
            
    avg_latency_native = native_total_duration / native_schema_ok_count if native_schema_ok_count > 0 else 0
    avg_latency_normalized = (
        normalized_total_duration / normalized_schema_ok_count if normalized_schema_ok_count > 0 else 0
    )
    json_parse_rate = (json_ok_count / len(questions)) * 100
    native_schema_valid_rate = (native_schema_ok_count / len(questions)) * 100
    normalized_schema_valid_rate = (normalized_schema_ok_count / len(questions)) * 100
    
    return {
        "model": model_name,
        "json_parse_rate": json_parse_rate,
        "native_schema_valid_rate": native_schema_valid_rate,
        "normalized_schema_valid_rate": normalized_schema_valid_rate,
        "avg_latency_native": avg_latency_native,
        "avg_latency_normalized": avg_latency_normalized,
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
        print(f"  Normalized Schema Valid Rate (RagResponse): {res['normalized_schema_valid_rate']}%")
        print(f"  Avg Latency (Native): {res['avg_latency_native']:.2f}s")
        print(f"  Avg Latency (Normalized): {res['avg_latency_normalized']:.2f}s")
        print("----------------")

if __name__ == "__main__":
    asyncio.run(main())
