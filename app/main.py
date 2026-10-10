from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="LLM MemoryGrid",
    description="Backend API for real-time LLM inference",
    version="0.2.0",
)


class PromptRequest(BaseModel):
    prompt: str


@app.get("/")
def home():
    return {
        "message": "LLM MemoryGrid API is running",
        "status": "ready",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/prompt")
def submit_prompt(request: PromptRequest):
    prompt = request.prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty",
        )

    request_id = str(uuid4())

    return {
        "request_id": request_id,
        "status": "accepted",
        "prompt": prompt,
        "message": (
            "Prompt received successfully. "
            "LLM inference is not connected yet."
        ),
    }