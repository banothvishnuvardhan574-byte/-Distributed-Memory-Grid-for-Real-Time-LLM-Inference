
import io
import logging
import re
import time
from calendar import month_abbr, month_name
from datetime import date
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
 member4-day13


class PromptRequest(BaseModel):
    prompt: str = Field(..., max_length=4000)


 main

from app.core.config import settings
from app.grid.memory_grid import MemoryGrid
from worker.worker import process_prompt

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


# --------------------------------------------------
# Logging and application setup
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memgrid")

app = FastAPI(
    title=settings.app_name,
    description="Backend API for real-time LLM inference",
    version=settings.version,
)


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    start = time.time()
    response = await call_next(request)
    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        (time.time() - start) * 1000,
    )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=list(
        set(settings.cors_origins + ["http://localhost:5173"])
    ),
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request and response models
# --------------------------------------------------

class PromptRequest(BaseModel):
    # Keep max_length, but do not use min_length.
    # Empty prompts must reach the endpoint and return HTTP 400.
    prompt: str = Field(..., max_length=4000)


# Response model
class PromptResponse(BaseModel):
    request_id: str
    status: str
    prompt: str
    response: str | None
    cache: str
    error: str | None = None


# --------------------------------------------------
# Memory grid and metrics
# --------------------------------------------------

grid = MemoryGrid(
    node_count=settings.node_count,
    capacity_per_node=settings.cache_size_per_node,
)

cache_metrics = {
    "hits": 0,
    "misses": 0,
}


@app.on_event("startup")
def startup():
    logger.info(
        "MemoryGrid started: nodes=%s, ttl=%ss, capacity_per_node=%s",
        settings.node_count,
        settings.default_ttl_seconds,
        settings.cache_size_per_node,
    )


# --------------------------------------------------
# Prompt processing
# --------------------------------------------------

def stub_inference(prompt: str) -> str:
    """Fallback inference function used by the worker."""
    return f"[stub] echo: {prompt[:200]}"


def run_prompt(prompt: str, request_id: str) -> dict:
    """Return a cached response or invoke the worker."""
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

    result = process_prompt(
        request_id,
        prompt,
        stub_inference,
    )

    # Count a miss only when inference succeeds.
    if result.get("status") == "completed":
        grid.set(prompt, result["response"])
        cache_metrics["misses"] += 1
        result["cache"] = "miss"

    return result


# --------------------------------------------------
# PDF date matching
# --------------------------------------------------

def find_today_date_matches(
    text: str,
    day: int | None = None,
    month: str | None = None,
) -> list[str]:
    """Find sentences containing the requested day and month."""
    today = date.today()

    if day is None:
        day = today.day

    if month is None:
        month = month_abbr[today.month]

    month = month.strip().lower()

    if not text or not month:
        return []

    month_index = next(
        (
            index
            for index in range(1, 13)
            if month in (
                month_abbr[index].lower(),
                month_name[index].lower(),
            )
        ),
        None,
    )

    month_names = {month}

    if month_index is not None:
        month_names.update(
            {
                month_abbr[month_index].lower(),
                month_name[month_index].lower(),
            }
        )

    month_pattern = "(?:" + "|".join(
        re.escape(name)
        for name in sorted(
            month_names,
            key=len,
            reverse=True,
        )
    ) + ")"

    day_pattern = rf"{day}(?:st|nd|rd|th)?"

    patterns = [
        re.compile(
            rf"(?i)\b{day_pattern}\s*(?:/|-|\.)\s*"
            rf"{month_pattern}\b"
        ),
        re.compile(
            rf"(?i)\b{day_pattern}\s+{month_pattern}\b"
        ),
        re.compile(
            rf"(?i)\b{month_pattern}\s+{day_pattern}\b"
        ),
    ]

    if month_index is not None:
        numeric_month = f"{month_index:02d}"

        patterns.extend(
            [
                re.compile(
                    rf"\b{day}\s*(?:/|-)\s*"
                    rf"{numeric_month}(?!\d)"
                ),
                re.compile(
                    rf"\b{numeric_month}\s*(?:/|-)\s*"
                    rf"{day_pattern}(?!\d)"
                ),
            ]
        )

    sentences = [
        sentence.strip()
        for sentence in re.split(
            r"\n+|(?<=[.!?])\s+",
            text,
        )
        if sentence.strip()
    ]

    return [
        sentence
        for sentence in sentences
        if any(
            pattern.search(sentence)
            for pattern in patterns
        )
    ]


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from uploaded PDF bytes."""
    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Unable to read PDF content: uploaded PDF is empty.",
        )

    if PdfReader is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "PDF support is not installed. "
                "Please install pypdf."
            ),
        )

    try:
        reader = PdfReader(io.BytesIO(file_bytes))

        if reader.is_encrypted:
            try:
                if not reader.decrypt(""):
                    raise HTTPException(
                        status_code=400,
                        detail="Encrypted PDFs are not supported.",
                    )
            except HTTPException:
                raise
            except Exception as exc:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to read encrypted PDF.",
                ) from exc

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read PDF content: {exc}",
        ) from exc


# Normalize extracted PDF text
def normalize_pdf_text(text: str) -> str:
    """Normalize whitespace in extracted PDF text."""
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------
# Home and health endpoints
# --------------------------------------------------

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


# --------------------------------------------------
# Prompt endpoint
# --------------------------------------------------


@app.post(
    "/api/prompt",
    response_model=PromptResponse,
)
def submit_prompt(request: PromptRequest):
    prompt = request.prompt.strip()

    # Return HTTP 400 for empty or whitespace-only prompts.
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

    try:
        result = run_prompt(
            prompt,
            request_id,
        )

    except Exception as exc:
        logger.exception("Prompt processing failed")

        raise HTTPException(
            status_code=500,
            detail="Prompt processing failed",
        ) from exc

    # Surface worker failures as HTTP 500.
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


# --------------------------------------------------
# Grid configuration and statistics
# --------------------------------------------------

@app.get("/api/grid/config")
def grid_config():
    return {
        "request_id": result["request_id"],
        "status": "accepted",
        "prompt": prompt,
        "response": result["response"],
        "cache": result.get("cache", "miss"),
        "node_count": settings.node_count,
        "cache_size_per_node": settings.cache_size_per_node,
        "default_ttl_seconds": settings.default_ttl_seconds,
    }


@app.get("/api/grid/health")
def grid_health():
    stats = grid.stats()
    return {
        "status": "healthy",
        "node_count": len(stats),
        "total_cached_entries": sum(node["entries"] for node in stats),
        "capacity_per_node": settings.cache_size_per_node,
    }


# Memory grid statistics endpoint
@app.get("/api/grid/stats")
def grid_stats():
    hits = cache_metrics["hits"]
    misses = cache_metrics["misses"]
    total_requests = hits + misses

    return {
        "nodes": grid.stats(),
        "cache_hits": hits,
        "cache_misses": misses,
        "hit_rate": (
            hits / total_requests
            if total_requests
            else 0.0
        ),
    }


# Clear memory grid and reset cache metrics
@app.post("/api/grid/clear", status_code=200)
def grid_clear():
    for node in grid.nodes:
        node.clear()

    cache_metrics["hits"] = 0
    cache_metrics["misses"] = 0

    return {
        "status": "cleared",
        "nodes": len(grid.nodes),
    }


# --------------------------------------------------
# PDF endpoint
# --------------------------------------------------

@app.post("/api/pdf/today")
async def extract_today_pdf_matches(
    file: UploadFile = File(...),
    day: int | None = Form(None),
    month: str | None = Form(None),
):
    if (
        not file.filename
        or not file.filename.lower().endswith(".pdf")
    ):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    file_bytes = await file.read()

    text = extract_pdf_text(file_bytes)
    normalized_text = normalize_pdf_text(text)

    today = date.today()

    target_day = day if day is not None else today.day
    target_month = (
        month if month is not None else month_abbr[today.month]
    ).strip().lower()

    matches = find_today_date_matches(
        normalized_text,
        day=target_day,
        month=target_month,
    )

    # Cache PDF text for 60 seconds.
    # This requires MemoryGrid.set(..., ttl=60) support.
    pdf_cache_key = f"pdf:{file.filename}:{uuid4()}"

    grid.set(
        pdf_cache_key,
        normalized_text,
        ttl=60,
    )

    return {
        "file_name": file.filename,
        "target_date": f"{target_day}/{target_month}",
        "matches_found": len(matches),
        "matches": matches[:10],
        "message": (
            "Small PDF check complete. "
            "Only the requested date has been extracted."
        ),
    }
