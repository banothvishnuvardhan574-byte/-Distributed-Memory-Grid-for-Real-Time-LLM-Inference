
import io

import pytest
from fastapi import HTTPException
from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
)

from app.main import extract_pdf_text


def create_pdf_with_text(text: str) -> bytes:
    """Create a valid, single-page PDF containing extractable text."""
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


def test_extract_text_from_first_pdf():
    pdf_bytes = create_pdf_with_text("First sample PDF")

    assert "First sample PDF" in extract_pdf_text(pdf_bytes)


def test_extract_text_from_second_pdf():
    pdf_bytes = create_pdf_with_text("Second sample PDF")

    assert "Second sample PDF" in extract_pdf_text(pdf_bytes)


def test_corrupt_pdf_raises_http_exception():
    with pytest.raises(HTTPException) as exc_info:
        extract_pdf_text(b"This is not a valid PDF")

    assert exc_info.value.status_code == 400


def test_extract_text_from_valid_pdf_without_text_returns_empty_string():
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    output = io.BytesIO()
    writer.write(output)

    assert extract_pdf_text(output.getvalue()) == ""    
