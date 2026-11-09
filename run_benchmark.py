import time
from llama_cpp import Llama

model_path = "models/qwen2.5-0.5b-instruct-q4_k_m.gguf"

print("=== 1. Loading Model Weights ===")
t0 = time.time()
llm = Llama(model_path=model_path, n_threads=2, n_ctx=1024, verbose=False)
print(f"Model loaded in {time.time() - t0:.2f} seconds\n")

prompts = [
    "Explain distributed inference in one simple sentence.",
    "What is an in-memory cache and why is it used?",
    "List three key benefits of microservices architecture."
]

print("=== 2. Running Prompts ===")
for i, p in enumerate(prompts, 1):
    print(f"\nPrompt {i}: {p}")
    t_start = time.time()
    out = llm(p, max_tokens=64, temperature=0.7, stop=["</s>", "<|im_end|>"])
    latency_ms = int((time.time() - t_start) * 1000)
    response = out["choices"][0]["text"].strip()
    print(f"Response: {response}")
    print(f"Latency: {latency_ms} ms")
    print("-" * 50)
