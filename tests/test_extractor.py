"""Tests for the PDF extractor module."""

from pathlib import Path

import pytest

from pitchcritic.extractor import PitchContent, extract_pdf


def test_extract_returns_pitch_content(sample_pdf_path: Path) -> None:
    result = extract_pdf(sample_pdf_path)
    assert isinstance(result, PitchContent)


def test_extract_slide_count(sample_pdf_path: Path) -> None:
    result = extract_pdf(sample_pdf_path)
    assert result.slide_count == 10


def test_extract_pages_list_length(sample_pdf_path: Path) -> None:
    result = extract_pdf(sample_pdf_path)
    assert len(result.pages) == 10


def test_extract_text_contains_slide_titles(sample_pdf_path: Path) -> None:
    result = extract_pdf(sample_pdf_path)
    assert "Problem" in result.text
    assert "Solution" in result.text
    assert "Market" in result.text


def test_extract_text_is_string(sample_pdf_path: Path) -> None:
    result = extract_pdf(sample_pdf_path)
    assert isinstance(result.text, str)
    assert len(result.text) > 0


def test_extract_accepts_string_path(tmp_path: Path, sample_pdf_bytes: bytes) -> None:
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(sample_pdf_bytes)
    result = extract_pdf(str(pdf_path))
    assert result.slide_count == 10


def test_extract_single_page(tmp_path: Path, single_page_pdf_bytes: bytes) -> None:
    pdf_path = tmp_path / "single.pdf"
    pdf_path.write_bytes(single_page_pdf_bytes)
    result = extract_pdf(pdf_path)
    assert result.slide_count == 1


def test_extract_nonexistent_file_raises(tmp_path: Path) -> None:
    with pytest.raises(Exception):
        extract_pdf(tmp_path / "does_not_exist.pdf")
