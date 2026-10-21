import io
import logging
import re
from calendar import month_abbr, month_name
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.config import settings
from app.grid.memory_grid import MemoryGrid
from worker.worker import process_prompt



try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memgrid")


# FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Backend API for real-time LLM inference",
    version=settings.version,
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(
        set(settings.cors_origins + ["http://localhost:5173"])
    ),
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model
class PromptRequest(BaseModel):
    prompt: str


# Response model - Day 9
class PromptResponse(BaseModel):
    request_id: str
    status: str
    prompt: str
    response: str | None
    cache: str
    error: str | None = None


# Initialize memory grid
grid = MemoryGrid(node_count=settings.node_count)
cache_metrics = {"hits": 0, "misses": 0}


@app.on_event("startup")
def startup():
    logger.info(
        "MemoryGrid started: nodes=%s, ttl=%ss, capacity_per_node=%s",
        settings.node_count,
        settings.default_ttl_seconds,
        settings.cache_size_per_node,
    )


# Stub inference function
def stub_inference(prompt: str) -> str:
    return f"[stub] echo: {prompt[:200]}"


# Process prompt using memory grid and worker
def run_prompt(prompt: str, request_id: str) -> dict:
    cached = grid.get(prompt)

    if cached is not None:
        cache_metrics["hits"] += 1
        return {
            "request_id": request_id,
            "status": "completed",
            "response": cached,
            "cache": "hit",
            "error": None,
        }

    cache_metrics["misses"] += 1
    result = process_prompt(request_id, prompt, stub_inference)

    if result.get("status") == "completed":
        grid.set(prompt, result["response"])
        result["cache"] = "miss"

    return result


# Find sentences containing a requested date
def find_today_date_matches(
    text: str,
    day: int = 11,
    month: str = "oct",
) -> list[str]:
    month = month.strip().lower()
    if not text or not month:
        return []

    month_index = next(
        (
            index
            for index in range(1, 13)
            if month in (month_abbr[index].lower(), month_name[index].lower())
        ),
        None,
    )
    month_names = {month}
    if month_index is not None:
        month_names.update(
            {month_abbr[month_index].lower(), month_name[month_index].lower()}
        )
    month_pattern = "(?:" + "|".join(
        re.escape(name) for name in sorted(month_names, key=len, reverse=True)
    ) + ")"
    day_pattern = rf"{day}(?:st|nd|rd|th)?"

    patterns = [
        re.compile(rf"(?i)\b{day_pattern}\s*(?:/|-|\.)\s*{month_pattern}\b"),
        re.compile(rf"(?i)\b{day_pattern}\s+{month_pattern}\b"),
        re.compile(rf"(?i)\b{month_pattern}\s+{day_pattern}\b"),
    ]
    if month_index is not None:
        numeric_month = f"{month_index:02d}"
        patterns.extend(
            [
                re.compile(rf"\b{day}\s*(?:/|-)\s*{numeric_month}(?!\d)"),
                re.compile(rf"\b{numeric_month}\s*(?:/|-)\s*{day_pattern}(?!\d)"),
            ]
        )

    sentences = [
        sentence.strip()
        for sentence in re.split(r"\n+|(?<=[.!?])\s+", text)
        if sentence.strip()
    ]

    return [
        sentence
        for sentence in sentences
        if any(pattern.search(sentence) for pattern in patterns)
    ]


# Extract text from PDF
def extract_pdf_text(file_bytes: bytes) -> str:
    if PdfReader is None:
        raise HTTPException(
            status_code=500,
            detail="PDF support is not installed. Please install pypdf.",
        )

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read PDF content: {exc}",
        ) from exc


def normalize_pdf_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "LLM MemoryGrid API is running",
        "status": "ready",
    }


# Health endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}


# Prompt endpoint - updated for Day 9
@app.post(
    "/api/prompt",
    response_model=PromptResponse,
)
def submit_prompt(request: PromptRequest):
    prompt = request.prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty",
        )

    request_id = str(uuid4())

    try:
        result = run_prompt(prompt, request_id)

    except Exception as exc:
        logger.exception("Prompt processing failed")

        raise HTTPException(
            status_code=500,
            detail="Prompt processing failed",
        ) from exc

    # Surface worker failures as HTTP 500
    if result.get("status") != "completed":
        raise HTTPException(
            status_code=500,
            detail=result.get("error") or "Worker failed",
        )

    return PromptResponse(
        request_id=result.get("request_id", request_id),
        status=result["status"],
        prompt=prompt,
        response=result.get("response"),
        cache=result.get("cache", "miss"),
        error=result.get("error"),
    )


# Memory grid statistics
@app.get("/api/grid/stats")
def grid_stats():
    return {
        "nodes": grid.stats(),
        "cache_hits": cache_metrics["hits"],
        "cache_misses": cache_metrics["misses"],
    }


@app.post("/api/grid/clear", status_code=200)
def grid_clear():
    for node in grid.nodes:
        node.clear()

    cache_metrics["hits"] = 0
    cache_metrics["misses"] = 0
    return {"status": "cleared", "nodes": len(grid.nodes)}


# PDF date extraction endpoint
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
    normalized_text = normalize_pdf_text(text)
    request_id = str(uuid4())
    grid.set(f"pdf:{file.filename}:{request_id}", normalized_text)

    matches = find_today_date_matches(
        normalized_text,
        day=day,
        month=month.lower(),
    )

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
