
import asyncio
import io

from pypdf import PdfWriter

import app.main as main


def create_sample_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def test_pdf_text_is_normalized_and_stored_in_grid(monkeypatch):
    monkeypatch.setattr(
        main,
        "extract_pdf_text",
        lambda _file_bytes: "  Project   review\n\n11/oct   status update.  ",
    )

    class FakeUpload:
        filename = "sample.pdf"

        async def read(self):
            return create_sample_pdf()

    response = asyncio.run(
        main.extract_today_pdf_matches(
            file=FakeUpload(),
            day=11,
            month="oct",
        )
    )

    assert response["matches_found"] == 1

    normalized_text = "Project review 11/oct status update."
    cache_key = next(
        key
        for node in main.grid.nodes
        for key in node.store
        if key.startswith("pdf:sample.pdf:")
    )

    assert main.grid.get(cache_key) == normalized_text
