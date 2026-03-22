"""PDF extraction using pdfplumber."""

from dataclasses import dataclass
from pathlib import Path

import pdfplumber


@dataclass
class PitchContent:
    text: str
    pages: list[str]
    slide_count: int


def extract_pdf(path: Path | str) -> PitchContent:
    """Extract text content from a pitch deck PDF."""
    path = Path(path)
    pages: list[str] = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)

    return PitchContent(
        text="\n\n".join(pages),
        pages=pages,
        slide_count=len(pages),
    )
