from pathlib import Path

import pdfplumber
from pydantic import BaseModel, Field


class PdfText(BaseModel):
    pages: list[str] = Field(..., description="Cleaned layout text, one string per page")
    needs_ocr: bool = Field(..., description="True if any page has no extractable text")


def clean_layout_text(text: str) -> str:
    """Drop empty lines and trailing spaces; keep leading spaces (they encode columns)."""
    lines = []
    for line in text.splitlines():
        if line.strip():
            lines.append(line.rstrip())
    return "\n".join(lines)


def read_pdf(path: Path) -> PdfText:
    """Extract cleaned layout text from every page of a PDF."""
    pages = []
    needs_ocr = False

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(layout=True) or ""
            cleaned = clean_layout_text(text)

            if not cleaned:
                needs_ocr = True

            pages.append(cleaned)

    return PdfText(pages=pages, needs_ocr=needs_ocr)