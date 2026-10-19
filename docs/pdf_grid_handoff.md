# PDF-to-Grid Handoff

## Purpose

This document describes how extracted PDF text is normalized and handed off to the memory grid.

## Workflow

1. The `/api/pdf/today` endpoint receives a PDF upload.
2. `extract_pdf_text()` extracts text from the PDF using `pypdf`.
3. `normalize_pdf_text()` trims the text and collapses consecutive whitespace into single spaces.
4. A unique storage key is created using the uploaded filename and a request ID.
5. `GridRouter.route()` selects the memory node for that key.
6. `MemoryNode.set()` stores the normalized text.
7. The endpoint searches the normalized text for the requested date and returns its existing response fields.

## Verification

The test `tests/test_pdf_grid_handoff.py` verifies that normalized PDF text is stored in the memory node selected by the router.

Run the test with:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_pdf_grid_handoff.py -v
```

## Error handling

Invalid PDF content is handled by the existing extraction function, which raises an HTTP 400 error when the PDF cannot be read.
