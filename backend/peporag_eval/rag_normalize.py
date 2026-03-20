"""Map heterogeneous LLM JSON (or plain text) into ``RagResponse``-shaped dicts."""

import json
from typing import Any


def normalize_payload(parsed_json: dict[str, Any]) -> dict[str, Any]:
    """
    Map heterogeneous model JSON shapes into the canonical RagResponse schema.
    """
    normalized: dict[str, Any] = {}

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
                if isinstance(item, dict) and isinstance(item.get("text"), str) and item.get("text").strip()
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


def normalize_text_output(raw_text: str) -> dict[str, Any]:
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
