# Hardware and Runtime Feasibility: Inference Options & Recommendation

**Author:** Suraj Kotrange (Model & Inference Integration Lead)  
**Branch:** `suraj-inference`  
**Date:** 3 November 2026  
**Document Status:** Pending Vishnu approval  

---

## 1. Machine Constraints & Hardware Audit

Before selecting a model or downloading weights, the deployment host was benchmarked to establish empirical constraints:

| Metric | Measured Value | Constraint Implication |
| :--- | :--- | :--- |
| **Processor (CPU)** | Intel(R) Xeon(R) 6985P-C @ 2 vCPUs | Compute-constrained; full multi-threading / AVX-512 available |
| **System Memory (RAM)** | 7.8 GiB total (~6.7 GiB available) | Strict upper boundary of < 4.0 GB memory footprint for model weights |
| **Accelerators (GPU / VRAM)** | None (0 MB VRAM) | CUDA/Triton unavailable; inference must run entirely on CPU |
| **Disk Space** | 18 GiB free on `/working_dir` | Sufficient for quantized weights (< 2.5 GB) and caches |
| **Python Environment** | Python 3.11.2 (Linux x86_64) | Full compatibility with modern C/C++ runtimes and PyTorch / GGUF |

---

## 2. Evaluation of Model & Runtime Candidates

Given 2 vCPUs and ~6.7 GB available RAM, heavy LLMs (7B+ parameters) are strictly infeasible and will trigger Out-Of-Memory (OOM) failures or excessive latency (> 45s/query). Three small, genuine open-weight candidates were evaluated:

### Candidate 1: Qwen2.5-0.5B-Instruct (Recommended Primary)
* **Architecture:** 490M parameter decoder-only transformer.
* **License:** Apache 2.0 (fully open for development and commercial prototyping).
* **Quantization & Size:**
  * GGUF Q4_K_M: ~380 MB download size.
  * Runtime RAM footprint: ~650 MB working memory.
* **CPU Latency Estimate (2 vCPUs):** ~1.5s – 3.2s per 50-token response (15–20 tokens/sec).
* **Pros:** Highly competent instruction following despite tiny size; minimal memory overhead; extremely stable on low-tier hardware.
* **Cons:** Limited complex reasoning capabilities.

### Candidate 2: SmolLM2-360M-Instruct (Lightweight Fallback)
* **Architecture:** 360M parameter compact transformer (Hugging Face).
* **License:** Apache 2.0.
* **Quantization & Size:**
  * GGUF Q4_K_M: ~270 MB download size.
  * Runtime RAM footprint: ~480 MB working memory.
* **CPU Latency Estimate (2 vCPUs):** ~1.0s – 2.0s per response (25+ tokens/sec).
* **Pros:** Lowest latency and resource footprint; virtually zero OOM risk.
* **Cons:** Output style is concise; less resilient to complex prompts.

### Candidate 3: TinyLlama-1.1B-Chat-v1.0 (Alternative Baseline)
* **Architecture:** 1.1B parameter compact LLaMA architecture.
* **License:** Apache 2.0.
* **Quantization & Size:**
  * GGUF Q4_K_M: ~670 MB download size.
  * Runtime RAM footprint: ~1.2 GB working memory.
* **CPU Latency Estimate (2 vCPUs):** ~4.5s – 8.0s per response (6–10 tokens/sec).
* **Pros:** Well-established community benchmark.
* **Cons:** Higher CPU overhead and slower generation on 2 cores.

---

## 3. Runtime Engine Selection

1. **llama-cpp-python (GGUF Quantization) — Recommended:**
   * Uses native C++ SIMD vectorization (AVX-512 / AVX2).
   * Extremely low memory overhead and predictable memory-mapped (`mmap`) paging.
   * Native support for thread limiting (`n_threads=2`).
2. **PyTorch CPU (safetensors):**
   * Higher memory footprint (requires unquantized or INT8 PyTorch weights, ~1.5x to 2x memory).
3. **Hosted API / Cloud Inference:**
   * Strictly disallowed unless team lead approves cost, network dependency, and privacy guidelines. For the self-contained demonstrator, local GGUF inference is preferred.

---

## 4. Recommendation & Next Steps

1. **Approved Architecture:** Deploy **Qwen2.5-0.5B-Instruct (GGUF Q4_K_M)** using `llama-cpp-python` / CPU engine.
2. **Failover Policy:** If model binary is unavailable or download is pending, adapter raises clean `ModelNotReadyError` with clear diagnostic logs rather than returning a mock/echo.
3. **Interface Sign-off:** Sign-off requested from **Vishnu** (FastAPI backend) and **Nikhila** (worker integration) for the public contract:
   ```python
   def generate_response(prompt: str, max_tokens: int = 128, timeout_sec: float = 15.0) -> str:
       ...
   ```
