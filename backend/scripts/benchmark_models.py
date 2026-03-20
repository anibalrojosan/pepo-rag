import json
import statistics
import threading
import time
from datetime import datetime
from pathlib import Path

import requests

# Config
OLLAMA_API_URL = "http://localhost:11434/api/generate"
_REPO_ROOT = Path(__file__).resolve().parents[2]
MODELS_TO_TEST = [
    "qwen2.5:3b",
    "qwen3.5:2b",
    "qwen3:4b",
    "qwen3:1.7b",
    "granite3-dense:2b",
]
TEST_PROMPT = "Briefly explain what a decorator is in Python and give an example of code."
ITERATIONS = 5
# First request after pull can load multi-GB weights into VRAM (minutes on 3GB GPUs).
REQUEST_TIMEOUT_SEC = (30, 600)
# Console feedback while blocked on Ollama (so it does not look “frozen”).
HEARTBEAT_INTERVAL_SEC = 10.0


class _OllamaWaitHeartbeat:
    """Prints periodic timestamps until stop() — use while waiting on stream/read."""

    def __init__(self, detail: str) -> None:
        self._detail = detail
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._started_perf: float = 0.0

    def start(self) -> None:
        self._stop.clear()
        self._started_perf = time.perf_counter()
        self._thread = threading.Thread(target=self._run, name="ollama-heartbeat", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None

    def _run(self) -> None:
        while not self._stop.wait(HEARTBEAT_INTERVAL_SEC):
            elapsed = time.perf_counter() - self._started_perf
            ts = datetime.now().strftime("%H:%M:%S")
            print(
                f"  [{ts}] ⏳ {elapsed:.0f}s waiting — {self._detail}",
                flush=True,
            )
            print(
                "      → Ollama is still busy (often GPU model load). Keep waiting unless "
                "this repeats past your request timeout.",
                flush=True,
            )


def benchmark_model(model_name):
    print(f"\n--- Testing model: {model_name} ---")
    metrics = []

    for i in range(ITERATIONS):
        payload = {
            "model": model_name,
            "prompt": TEST_PROMPT,
            "stream": True,
        }

        start_time = time.perf_counter()
        ttft = None
        total_duration = None
        eval_count = None

        heartbeat = _OllamaWaitHeartbeat(f"model `{model_name}` — no stream data yet (loading weights or queued).")
        try:
            print(
                f"  Iteration {i + 1}/{ITERATIONS}: sending request to Ollama…",
                flush=True,
            )
            print(
                "      If the next line is silent for a while, a heartbeat will print every "
                f"{HEARTBEAT_INTERVAL_SEC:.0f}s — that means the script is still waiting, not stuck.",
                flush=True,
            )
            heartbeat.start()
            response = requests.post(
                OLLAMA_API_URL,
                json=payload,
                stream=True,
                timeout=REQUEST_TIMEOUT_SEC,
            )
            response.raise_for_status()
            print("      HTTP OK — waiting for first stream line from Ollama…", flush=True)

            first_line_seen = False
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if not first_line_seen:
                    first_line_seen = True
                    heartbeat.stop()
                    print(
                        "      ✓ First stream line received — Ollama is generating (or finishing load).",
                        flush=True,
                    )
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if ttft is None and chunk.get("response"):
                    ttft = time.perf_counter() - start_time
                    print(
                        "      ✓ First token chunk in JSON — measuring TTFT from here.",
                        flush=True,
                    )

                if chunk.get("done"):
                    td_ns = chunk.get("total_duration")
                    total_duration = (td_ns / 1e9) if td_ns is not None else None
                    eval_count = chunk.get("eval_count")
                    break

            heartbeat.stop()

            if total_duration is None or eval_count is None:
                raise RuntimeError(
                    "Stream ended without a final `done` chunk (or missing timing fields). "
                    "Try again after the model finishes loading, or check Ollama logs."
                )

            if ttft is None:
                ttft = total_duration

            tps = eval_count / total_duration if total_duration and total_duration > 0 else 0.0

            metrics.append(
                {
                    "iteration": i + 1,
                    "ttft": ttft,
                    "tps": tps,
                    "total_duration": total_duration,
                    "tokens": eval_count,
                }
            )
            print(
                f"  Iteration {i + 1}: {tps:.2f} tokens/s | TTFT: {ttft:.2f}s",
                flush=True,
            )

        except requests.exceptions.Timeout as e:
            heartbeat.stop()
            print(f"  Error testing {model_name} (timeout): {e}", flush=True)
            continue
        except Exception as e:
            heartbeat.stop()
            print(f"  Error testing {model_name}: {e}", flush=True)
            continue

    if not metrics:
        return None

    # Calculate averages
    return {
        "model": model_name,
        "avg_tps": statistics.mean([m["tps"] for m in metrics]),
        "avg_ttft": statistics.mean([m["ttft"] for m in metrics]),
        "avg_duration": statistics.mean([m["total_duration"] for m in metrics]),
        "timestamp": datetime.now().isoformat(),
    }


def main():
    results = []
    for model in MODELS_TO_TEST:
        res = benchmark_model(model)
        if res:
            results.append(res)

    # Save results
    output_file = _REPO_ROOT / "docs" / "benchmark_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    print(f"\nBenchmarking completed. Results saved in {output_file}")


if __name__ == "__main__":
    main()
