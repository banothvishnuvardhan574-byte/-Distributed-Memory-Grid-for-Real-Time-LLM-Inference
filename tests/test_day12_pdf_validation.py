import asyncio
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

import app.main as main


def submit_pdf_upload(filename: str):
    upload = UploadFile(
        filename=filename,
        file=BytesIO(b"test file content"),
    )
    return asyncio.run(main.extract_today_pdf_matches(file=upload))


def test_upload_rejects_unsupported_file_extension():
    with pytest.raises(HTTPException) as exc_info:
        submit_pdf_upload("report.txt")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Please upload a PDF file."


def test_upload_rejects_empty_filename():
    with pytest.raises(HTTPException) as exc_info:
        submit_pdf_upload("")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Please upload a PDF file."