"""PDF extraction using pdfplumber."""

from dataclasses import dataclass
from pathlib import Path

import pdfplumber

MAX_PDF_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_PAGES = 200


class ExtractionError(Exception):
    """Raised when PDF extraction fails."""


@dataclass
class PitchContent:
    text: str
    pages: list[str]
    slide_count: int


def extract_pdf(path: Path | str) -> PitchContent:
    """Extract text content from a pitch deck PDF."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if not path.suffix.lower() == ".pdf":
        raise ExtractionError(f"Not a PDF file: {path.suffix}")

    file_size = path.stat().st_size
    if file_size == 0:
        raise ExtractionError("PDF file is empty (0 bytes)")
    if file_size > MAX_PDF_SIZE_BYTES:
        raise ExtractionError(
            f"PDF too large: {file_size / 1024 / 1024:.1f} MB (max {MAX_PDF_SIZE_BYTES // 1024 // 1024} MB)"
        )

    pages: list[str] = []

    try:
        with pdfplumber.open(path) as pdf:
            if len(pdf.pages) > MAX_PAGES:
                raise ExtractionError(
                    f"PDF has {len(pdf.pages)} pages (max {MAX_PAGES})"
                )
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages.append(text)
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(f"Failed to read PDF: {exc}") from exc

    return PitchContent(
        text="\n\n".join(pages),
        pages=pages,
        slide_count=len(pages),
    )
