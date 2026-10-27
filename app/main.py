import io
import re
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.config import settings
from app.grid.memory_node import MemoryNode
from app.grid.router import GridRouter
from worker.worker import process_prompt

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

app = FastAPI(
    title=settings.app_name,
    description="Backend API for real-time LLM inference",
    version=settings.version,
)


class PromptRequest(BaseModel):
    prompt: str


router = GridRouter(node_count=settings.node_count)
nodes = [MemoryNode(node_id=node_id) for node_id in range(settings.node_count)]


def stub_inference(prompt: str) -> str:
    return f"[stub] echo: {prompt[:200]}"


def run_prompt(prompt: str, request_id: str) -> dict[str, str]:
    node = nodes[router.route(prompt)]
    cached = node.get(prompt)
    if cached is not None:
        return {
            "request_id": request_id,
            "status": "completed",
            "response": cached,
            "cache": "hit",
        }

    result = process_prompt(request_id, prompt, stub_inference)
    if result["status"] == "completed":
        node.set(prompt, result["response"])
        result["cache"] = "miss"
    return result


def find_today_date_matches(text: str, day: int = 11, month: str = "oct") -> list[str]:
    if not text:
        return []

    month_pattern = re.escape(month)
    patterns = [
        re.compile(rf"(?i)\b{day}\s*(?:/|-)\s*{month_pattern}\b"),
        re.compile(rf"(?i)\b{day}\s+{month_pattern}\b"),
        re.compile(rf"(?i)\b{month_pattern}\s+{day}\b"),
    ]

    sentences = [
        sentence.strip()
        for sentence in re.split(r"\n+|(?<=[.!?])\s+", text)
        if sentence.strip()
    ]

    matches: list[str] = []
    for sentence in sentences:
        if any(pattern.search(sentence) for pattern in patterns):
            matches.append(sentence)

    return matches


def extract_pdf_text(file_bytes: bytes) -> str:
    if PdfReader is None:
        raise HTTPException(
            status_code=500,
            detail="PDF support is not installed. Please install pypdf.",
        )

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return "\n".join(pages)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read PDF content: {exc}",
        ) from exc


@app.get("/")
def home():
    return {
        "message": "LLM MemoryGrid API is running",
        "status": "ready",
    }


def health_check():
    return {"status": "ok"}


@app.get("/health")
def health_check_route():
    return {"status": "healthy"}


def submit_prompt(request: PromptRequest):
    prompt = request.prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty",
        )

    request_id = str(uuid4())
    result = run_prompt(prompt, request_id)
    return result


@app.post("/api/prompt")
def submit_prompt_route(request: PromptRequest):
    prompt = request.prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty",
        )

    request_id = str(uuid4())
    result = run_prompt(prompt, request_id)

    return {
        "request_id": result["request_id"],
        "status": "accepted",
        "prompt": prompt,
        "response": result["response"],
        "cache": result.get("cache", "miss"),
    }


@app.get("/api/grid/stats")
def grid_stats():
    return {"nodes": [node.stats() for node in nodes]}


@app.post("/api/pdf/today")
async def extract_today_pdf_matches(
    file: UploadFile = File(...),
    day: int = Form(11),
    month: str = Form("oct"),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    file_bytes = await file.read()
    text = extract_pdf_text(file_bytes)
    matches = find_today_date_matches(text, day=day, month=month.lower())

    return {
        "file_name": file.filename,
        "target_date": f"{day}/{month.lower()}",
        "matches_found": len(matches),
        "matches": matches[:10],
        "message": (
            "Small PDF check complete. "
            "Only the requested date has been extracted."
        ),
    }
