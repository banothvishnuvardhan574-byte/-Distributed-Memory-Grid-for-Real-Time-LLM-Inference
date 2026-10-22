import asyncio
from datetime import date as date_type
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from fastapi.openapi.utils import get_openapi


import app.main as main


def test_prompt_response_model_is_published_in_openapi():
    schema = get_openapi(
        title=main.app.title,
        version=main.app.version,
        routes=main.app.routes,
    )

    assert schema["paths"]["/api/prompt"]["post"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"]["$ref"] == "#/components/schemas/PromptResponse"


def test_empty_prompt_returns_bad_request():
    with pytest.raises(HTTPException) as exc_info:
        main.submit_prompt(main.PromptRequest(prompt=""))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Prompt cannot be empty"


def test_worker_failure_returns_http_500_with_detail(monkeypatch):
    monkeypatch.setattr(
        main,
        "run_prompt",
        lambda prompt, request_id: {
            "request_id": request_id,
            "status": "failed",
            "response": "Inference timed out",
            "error": "Inference timed out",
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        main.submit_prompt(main.PromptRequest(prompt="day9"))

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Inference timed out"


def test_worker_failure_returns_http_500_without_counting_a_cache_miss(monkeypatch):
    main.grid_clear()
    monkeypatch.setattr(
        main,
        "process_prompt",
        lambda request_id, prompt, inference_fn: {
            "request_id": request_id,
            "status": "failed",
            "response": None,
            "error": "Worker unavailable",
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        main.submit_prompt(main.PromptRequest(prompt="worker failure over HTTP"))

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Worker unavailable"
    stats = main.grid_stats()
    assert stats["cache_hits"] == 0
    assert stats["cache_misses"] == 0
    assert stats["hit_rate"] == 0.0
    main.grid_clear()


def test_pdf_endpoint_defaults_to_current_date(monkeypatch):
    class FixedDate(date_type):
        @classmethod
        def today(cls):
            return cls(2026, 10, 22)

    monkeypatch.setattr(main, "date", FixedDate)
    monkeypatch.setattr(
        main,
        "extract_pdf_text",
        lambda file_bytes: "Meeting on 22 October.\nPrevious meeting on 21 October.",
    )

    upload = UploadFile(
        filename="today.pdf",
        file=BytesIO(b"valid PDF placeholder"),
    )
    response = asyncio.run(
        main.extract_today_pdf_matches(
            file=upload,
            day=None,
            month=None,
        )
    )

    assert response["target_date"] == "22/oct"
    assert response["matches"] == ["Meeting on 22 October."]


def _submit_pdf(filename: str, contents: bytes):
    upload = UploadFile(filename=filename, file=BytesIO(contents))
    return asyncio.run(
        main.extract_today_pdf_matches(file=upload, day=11, month="oct")
    )


def test_empty_pdf_is_rejected_safely():
    with pytest.raises(HTTPException) as exc_info:
        _submit_pdf("empty.pdf", b"")

    assert exc_info.value.status_code == 400
    assert "Unable to read PDF content" in exc_info.value.detail


def test_invalid_pdf_is_rejected_safely():
    with pytest.raises(HTTPException) as exc_info:
        _submit_pdf("invalid.pdf", b"not a PDF")

    assert exc_info.value.status_code == 400
    assert "Unable to read PDF content" in exc_info.value.detail
