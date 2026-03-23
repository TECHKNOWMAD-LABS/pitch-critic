"""PDF extraction using pdfplumber."""

import hashlib
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


_extraction_cache: dict[str, PitchContent] = {}


def _file_hash(path: Path) -> str:
    """Compute SHA-256 of file for cache key."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


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

    content_hash = _file_hash(path)
    if content_hash in _extraction_cache:
        return _extraction_cache[content_hash]

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

    result = PitchContent(
        text="\n\n".join(pages),
        pages=pages,
        slide_count=len(pages),
    )
    _extraction_cache[content_hash] = result
    return result
