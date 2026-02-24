# Experimentation Phase - Model Selection

This document records the tests performed to select the most suitable Large Language Model (LLM) and embedding model for the local environment.

## Test Hardware
- **CPU:** [To be completed]
- **GPU/VRAM:** [To be completed]
- **RAM:** [To be completed]

---

## 1. Large Language Models (LLMs)

### 1.1 Candidate Models (Ollama)

| Model | Size | Parameters | Quantization | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Llama 3.1 8B | ~4.7GB | 8B | Q4_K_M | Industry benchmark. |
| Qwen 2.5 7B | ~4.7GB | 7B | Q4_K_M | Excellent in code and technical logic. |
| Qwen 2.5 3B | ~3.0GB | 3B | Q4_K_M | Balanced model for RAG. |
| Mistral 7B | ~4.1GB | 7B | Q4_0 | Very robust for RAG. |
| Phi-3.5 Mini | ~2.3GB | 3.8B | Q4_K_M | Ultra-fast, ideal for CPUs. |

### 1.2 Evaluation Methodology

#### 1.2.1 Performance Benchmark (Latency)
Response time is measured using a standard technical prompt:
- **TTFT (Time To First Token):** Perceived latency.
- **TPS (Tokens Per Second):** Generation speed.

#### 1.2.2 Quality Evaluation (Evals)
A mini-dataset of "Golden Questions" based on a sample technical book will be used:
- **Faithfulness:** Does the answer come only from the context?
- **Instruction Following:** Can it return the answer in a specific JSON format for PydanticAI?
- **Technical Reasoning:** Does it correctly explain architectural concepts?

### 1.3 Test Results

| Model | TPS (Local) | RAG Quality (1-5) | JSON Follow | Recommended for |
| :--- | :--- | :--- | :--- | :--- |
| Llama 3.1 8B | | | | High-end Local |
| Qwen 2.5 7B | | | | Balanced (Recommended) |
| Qwen 2.5 3B | | | | Mid-range / Laptop |
| Phi-3.5 Mini | | | | Low-end / CPU only |

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

## Conclusions
*(To be completed after running evaluation scripts in Phase 2 of the Roadmap)*
