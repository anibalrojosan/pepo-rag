# Experimentation Phase - Model Selection

This document records the tests performed to select the most suitable Large Language Model (LLM) and embedding model for the local environment.

All models were tested using the `ollama run` command with the `--verbose` flag with the following hardware:

## Test Hardware

The benchmark was performed on an entry-level environment with the following detected specifications:

- **GPU:** NVIDIA GeForce GTX 1050 with Max-Q Design
  - **VRAM:** 3GB GDDR5
  - **CUDA:** 13.0 (Driver 581.83)
- **CPU:** Intel(R) Core(TM) i5-8265U @ 1.60GHz
  - **Cores:** 8 (4 physical / 8 threads)
  - **SIMD:** AVX2 Supported
- **RAM:** 24.0 GB DDR4 @ 2400 MHz
  - **Composition:** 2 SODIMM slots (24.0 GB Total)
  - **Available:** ~5.0 GB during high-load tests (based on system snapshots)
- **Performance Tier:** ULTRA LOW (according to `llm-checker`)
- **OS**: WSL Ubuntu 22.04 LTS (Windows 11)

### Detected Technical Constraints:
1. **VRAM Limit (3GB):** Models exceeding this size (such as Llama 3.1 8B or Qwen 2.5 7B, which are ~4.7GB) suffer massive performance degradation as they require *offloading* to system RAM.
2. **Ideal Model Size:** To maintain 100% GPU execution and achieve low latencies (TTFT < 1s), the model size must be under **2.5GB**. This validates the selection of **2B and 3B parameter models** for this specific hardware.

---

## 1. Large Language Models (LLMs)

### 1.1 Candidate Models (Ollama)

| Model | Size | Parameters | Quantization | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Llama 3.1 8B | ~4.7GB | 8B | Q4_K_M | Industry benchmark. |
| Llama 3.2 3B | ~1.5GB | 3.21B | Q4_K_M | Optimized for mobile devices and limited resources hardware. |
| Qwen 2.5 7B | ~4.7GB | 7B | Q4_K_M | Excellent in code and technical logic. |
| Qwen 2.5 3B | ~3.0GB | 3B | Q4_K_M | Balanced model for RAG. |
| Phi-3.5 Mini | ~2.3GB | 3.8B | Q4_K_M | Ultra-fast, ideal for CPUs. |
| Granite3 Dense 2B | ~2.0GB | 2B | Q4_K_M | High-ranking model on MTEB leaderboard for its size. |

### 1.2 Evaluation Methodology

#### 1.2.1 Performance Benchmark (Latency)
Response time is measured using a standard technical prompt:
- **TTFT (Time To First Token):** Perceived latency (`load duration` + `prompt evaluation duration`).
- **TPS (Tokens Per Second):** Generation speed.

All tests were performed with only the IDE open (all other applications closed) and the following prompt: 

> Explain in detail what a Vector Database is and why it is fundamental for a RAG (Retrieval-Augmented Generation) system. Respond in Spanish.

#### 1.2.2 Quality Evaluation (Evals)
A mini-dataset of "Golden Questions" based on a sample technical book will be used:
- **Faithfulness:** Does the answer come only from the context?
- **Instruction Following:** Can it return the answer in a specific JSON format for PydanticAI?
- **Technical Reasoning:** Does it correctly explain architectural concepts?

### 1.3 Test Results

| Model | TPS (Local) | TTFT (s) | RAG Quality (1-5) | JSON Follow | Recommended for |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Llama 3.2 3B** | ~9.20 | ~0.81 | 4.5 | Yes | **Very good quality and fast enough for this task** |
| **Qwen 2.5 3B** | ~11.70 | ~0.55 | 4 | Yes | **Balanced, short and concise answers / Best tradeoff between speed and quality** |
| **Granite 2B** | ~21.50 | ~0.26 | 3 | Yes | **Ultra-fast but very short answers / Could be useful for task that requires short answers** |
| Llama 3.1 8B | ~3.26 | ~1.84 | 5 | Yes | High-end but very slow on this hardware |
| Qwen 2.5 7B | ~3.80 | ~1.92 | 4 | Yes | Balanced (Slow on this hardware) |
| Phi-3.5 Mini | ~6.39 | ~0.71 | 2 | No | Low quality responses, hallucinations, not recommended for this task |

### 1.4 Selected models comparison (2026-02-27)

| Model | TPS (Tokens/s) | TTFT (s) | Avg Duration (s) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **granite3-dense:2b** | **19.42** | **1.13** | **11.72** | **Best Performance.** Ultra-fast generation and lowest latency. Ideal for responsive chat. |
| **qwen2.5:3b** | 13.58 | 1.43 | 25.81 | **Best Balance.** Good speed and likely better reasoning than 2B models. Strong contender. |
| llama3.2:3b | 8.17 | 2.91 | 33.92 | Acceptable speed, but significantly slower than Granite and Qwen. |
| llama3.1:latest | 3.75 | 6.08 | 82.07 | **Not Recommended.** Too heavy for current hardware (high latency, low TPS). |

---

## 2. Embedding Models (Vectorization)

### 2.1 Candidate Models

| Model | Dimensions | Provider | Notes |
| :--- | :--- | :--- | :--- |
| `nomic-embed-text` | 768 | Ollama | High quality, large context window, runs on GPU. |
| `all-minilm` | 384 | Sentence-Transformers | Very fast, lightweight, runs efficiently on CPU. |
| `bge-small-en-v1.5` | 384 | Sentence-Transformers | High ranking on MTEB leaderboard for its size. |

### 2.2 Evaluation Methodology

#### 2.2.1 Retrieval Accuracy
The embedding model is the "eyes" of the RAG system. We evaluate how well it finds relevant technical content:
- **Hit Rate @K:** Does the correct chunk appear in the top K results?
- **MRR (Mean Reciprocal Rank):** How high up in the results is the relevant chunk?

#### 2.2.2 Technical Domain Understanding
- **Semantic Similarity:** Ability to distinguish between similar technical terms (e.g., "Thread" in Java vs. "Thread" in a forum).
- **Context Window Alignment:** Ensuring the model's token limit matches our chunking strategy.

#### 2.2.3 Performance
- **Vectorization Speed:** Chunks processed per second during ingestion.
- **Query Latency:** Time to vectorize a user question in real-time.

### 2.3 Test Results

| Model | Hit Rate @3 | MRR | Ingestion Speed | Recommended for |
| :--- | :--- | :--- | :--- | :--- |
| `nomic-embed-text` | | | | High Accuracy |
| `all-minilm` | | | | High Speed / CPU |
| `bge-small-en-v1.5` | | | | Balanced |

---

## 3. Qualitative Evaluation (RAG Quality)

### 3.1 Methodology
To validate the "intelligence" and reliability of the models, a "Golden Dataset" of 5 technical questions was designed, covering:
- **Synthesis:** Ability to summarize complex concepts.
- **Extraction:** Ability to list items in JSON format.
- **Faithfulness:** Ability to admit lack of information (avoiding hallucinations).
- **Reasoning:** Ability to connect multiple concepts.
- **Instruction Following:** Ability to follow language and format constraints.

### 3.2 Results (Automated via PydanticAI)

| Model | Success Rate (JSON) | Avg Latency (s) | Faithfulness | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **qwen2.5:3b** | *Pending* | *Pending* | *Pending* | *To be populated* |
| **granite3-dense:2b** | *Pending* | *Pending* | *Pending* | *To be populated* |

### 3.3 Acceptance Criteria (Phase 2.2)

To compare models fairly while preserving a single canonical API contract (`RagResponse`), the evaluator tracks multiple compliance layers:

- **JSON Parse Rate:** `%` of runs where the raw model output is valid JSON (`json.loads` succeeds).
- **Native Schema Valid Rate:** `%` of runs where raw parsed JSON already matches `RagResponse` without adaptation.
- **Normalized JSON Schema Valid Rate:** `%` of runs where parsed JSON becomes valid `RagResponse` after deterministic normalization.
- **Canonical Valid Rate (App Contract):** `%` of runs where the final adapted payload (JSON-normalized or plain-text adapted) validates as `RagResponse`.

#### Why both schema metrics are required

- **Native** captures strict instruction-following and direct contract compliance.
- **Normalized JSON** captures how far structured outputs can be recovered from heterogeneous JSON.
- **Canonical** captures practical production viability for the app contract even when a model returns plain text.
- Reporting only one of them can be misleading:
  - Native only may undervalue useful but non-canonical model outputs.
  - Canonical only may hide poor native schema-following behavior.

#### Production selection rule for the RAG assistant

For model selection in the app, the primary metric is:

- **Canonical Valid Rate (App Contract)**

This reflects real product behavior: the backend must always end with a valid `RagResponse` object for downstream consumers, regardless of whether the model returned strict JSON or plain text.

---

## Conclusions

Based on the automated benchmark performed on 2026-02-27/28:

1.  **Primary Model Selection:** **`qwen2.5:3b`** is kept as the primary model for the RAG system.
    *   **Reasoning:** With ~13.6 TPS, it is still very usable and offers a larger parameter count (3B vs 2B) which may provide better reasoning capabilities for complex queries if Granite proves too simple.

2.  **Alternative/Fallback:** **`granite3-dense:2b`** is selected as the fallback model for the RAG system.
    *   **Reasoning:** It achieves ~19.4 TPS, which is nearly double the speed of Llama 3.2, and has a very low Time To First Token (1.13s), ensuring a snappy user experience on the GTX 1050 (3GB VRAM). 

3.  **Hardware Limitations Confirmed:**
    *   Models larger than 3B parameters (like `llama3.1:latest`) struggle significantly, dropping to < 4 TPS with high latency (> 6s TTFT), confirming the initial hypothesis that 8B models are not viable for this specific hardware configuration without heavy quantization or offloading.
