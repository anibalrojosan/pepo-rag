import json
import statistics
import time
from datetime import datetime

import requests

# Config
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODELS_TO_TEST = [
    "qwen2.5:3b", 
    "granite3-dense:2b", 
    "llama3.2:3b", 
    "llama3.1:latest"
    ]
TEST_PROMPT = "Briefly explain what a decorator is in Python and give an example of code."
ITERATIONS = 5

def benchmark_model(model_name):
    print(f"\n--- Testing model: {model_name} ---")
    metrics = []

    for i in range(ITERATIONS):
        # Data to send to Ollama API
        payload = {
            "model": model_name,
            "prompt": TEST_PROMPT,
            "stream": True  # Necessary to measure TTFT
        }
        
        # Capture global start time of the request
        start_time = time.perf_counter()

        # Initialize TTFT measurement
        ttft = None
        
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    
                    # Measure TTFT in the first chunk that contains text
                    if ttft is None and chunk.get("response"):
                        ttft = time.perf_counter() - start_time
                    
                    # 'done' indicates the end of the Ollama API response
                    if chunk.get("done"):
                        total_duration = chunk.get("total_duration") / 1e9  # Convert ns to seconds
                        eval_count = chunk.get("eval_count") # Number of tokens generated
                        break
            
            # Calculate TPS (Tokens Per Second)
            tps = eval_count / total_duration if total_duration > 0 else 0
            
            metrics.append({
                "iteration": i + 1,
                "ttft": ttft,
                "tps": tps,
                "total_duration": total_duration,
                "tokens": eval_count
            })
            print(f"  Iteration {i+1}: {tps:.2f} tokens/s | TTFT: {ttft:.2f}s")
            
        except Exception as e:
            print(f"  Error testing {model_name}: {e}")
            continue

    if not metrics:
        return None

    # Calculate averages
    return {
        "model": model_name,
        "avg_tps": statistics.mean([m["tps"] for m in metrics]),
        "avg_ttft": statistics.mean([m["ttft"] for m in metrics]),
        "avg_duration": statistics.mean([m["total_duration"] for m in metrics]),
        "timestamp": datetime.now().isoformat()
    }

def main():
    results = []
    for model in MODELS_TO_TEST:
        res = benchmark_model(model)
        if res:
            results.append(res)
    
    # Save results
    output_file = "docs/benchmark_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"\nBenchmarking completed. Results saved in {output_file}")

if __name__ == "__main__":
    main()