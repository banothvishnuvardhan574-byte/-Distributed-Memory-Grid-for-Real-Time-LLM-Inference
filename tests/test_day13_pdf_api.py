import io

from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import (
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
)

import app.main as main


def create_pdf_with_text(text: str) -> bytes:
    """Create a real PDF containing extractable text."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)

    font = DictionaryObject()
    font.update(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_ref = writer._add_object(font)

    resources = DictionaryObject()
    fonts = DictionaryObject()
    fonts[NameObject("/F1")] = font_ref
    resources[NameObject("/Font")] = fonts
    page[NameObject("/Resources")] = resources

    content = DecodedStreamObject()
    content.set_data(
        f"BT /F1 12 Tf 20 200 Td ({text}) Tj ET".encode("ascii")
    )
    page[NameObject("/Contents")] = writer._add_object(content)

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def test_post_pdf_today_upload_returns_expected_date_matches():
    pdf_bytes = create_pdf_with_text("Meeting on 11 October 2026.")

    main.grid_clear()

    try:
        with TestClient(main.app) as client:
            response = client.post(
                "/api/pdf/today",
                files={
                    "file": (
                        "schedule.pdf",
                        pdf_bytes,
                        "application/pdf",
                    )
                },
                data={"day": "11", "month": "OCT"},
            )

        assert response.status_code == 200

        payload = response.json()

        assert payload["file_name"] == "schedule.pdf"
        assert payload["target_date"] == "11/oct"
        assert payload["matches_found"] == 1
        assert payload["matches"] == [
            "Meeting on 11 October 2026."
        ]
        assert "Small PDF check complete." in payload["message"]
    finally:
        main.grid_clear()