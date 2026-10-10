from fastapi import FastAPI

app = FastAPI(title="LLM MemoryGrid")


@app.get("/")
def home():
    return {"message": "LLM MemoryGrid API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"} 