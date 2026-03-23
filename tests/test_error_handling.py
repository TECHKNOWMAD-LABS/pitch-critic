"""Tests for input validation and error handling across modules."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from pitchcritic.api import app
from pitchcritic.critic import CritiqueError, critique_pitch
from pitchcritic.extractor import ExtractionError, extract_pdf


class TestExtractorValidation:
    """Tests for PDF extractor input validation."""

    def test_nonexistent_file_raises_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="PDF not found"):
            extract_pdf(tmp_path / "missing.pdf")

    def test_non_pdf_extension_raises(self, tmp_path: Path) -> None:
        txt_file = tmp_path / "deck.txt"
        txt_file.write_text("not a pdf")
        with pytest.raises(ExtractionError, match="Not a PDF file"):
            extract_pdf(txt_file)

    def test_empty_file_raises(self, tmp_path: Path) -> None:
        empty_pdf = tmp_path / "empty.pdf"
        empty_pdf.write_bytes(b"")
        with pytest.raises(ExtractionError, match="empty"):
            extract_pdf(empty_pdf)

    def test_corrupt_pdf_raises_extraction_error(self, tmp_path: Path) -> None:
        bad_pdf = tmp_path / "corrupt.pdf"
        bad_pdf.write_bytes(b"this is not a real pdf file content")
        with pytest.raises(ExtractionError, match="Failed to read PDF"):
            extract_pdf(bad_pdf)


class TestCritiqueValidation:
    """Tests for critique input validation."""

    def test_empty_content_raises(self) -> None:
        with pytest.raises(CritiqueError, match="empty"):
            critique_pitch("")

    def test_whitespace_only_content_raises(self) -> None:
        with pytest.raises(CritiqueError, match="empty"):
            critique_pitch("   \n\t  ")

    def test_none_content_raises(self) -> None:
        with pytest.raises((CritiqueError, TypeError)):
            critique_pitch(None)  # type: ignore[arg-type]

    def test_llm_failure_raises_critique_error(self) -> None:
        mock = MagicMock(side_effect=ConnectionError("API down"))
        with pytest.raises(CritiqueError, match="LLM call failed"):
            critique_pitch("Valid content", llm_caller=mock)

    def test_invalid_json_response_raises(self) -> None:
        mock = MagicMock(return_value="This is not JSON at all")
        with pytest.raises(CritiqueError, match="Failed to parse"):
            critique_pitch("Valid content", llm_caller=mock)

    def test_missing_fields_raises(self) -> None:
        mock = MagicMock(return_value='{"foo": "bar"}')
        with pytest.raises(CritiqueError, match="missing required fields"):
            critique_pitch("Valid content", llm_caller=mock)

    def test_score_clamped_to_valid_range(self) -> None:
        from pitchcritic.critic import DIMENSIONS

        payload = {
            "dimensions": [
                {
                    "dimension": dim,
                    "score": 99 if i == 0 else -5 if i == 1 else 5,
                    "critique": "Test.",
                    "fatal_flaw": None,
                }
                for i, dim in enumerate(DIMENSIONS)
            ],
            "overall_verdict": "Test.",
        }
        mock = MagicMock(return_value=json.dumps(payload))
        result = critique_pitch("Content", llm_caller=mock)
        assert result.dimensions[0].score == 10  # clamped from 99
        assert result.dimensions[1].score == 0  # clamped from -5


class TestAPIValidation:
    """Tests for API endpoint error handling."""

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_empty_upload_rejected(self, client: TestClient) -> None:
        response = client.post(
            "/analyze",
            files={"file": ("pitch.pdf", b"", "application/pdf")},
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_extraction_error_returns_422(
        self, client: TestClient, sample_pdf_bytes: bytes
    ) -> None:
        with patch(
            "pitchcritic.api.extract_pdf",
            side_effect=ExtractionError("corrupt PDF"),
        ):
            response = client.post(
                "/analyze",
                files={"file": ("pitch.pdf", sample_pdf_bytes, "application/pdf")},
            )
        assert response.status_code == 422

    def test_critique_error_returns_502(
        self, client: TestClient, sample_pdf_bytes: bytes
    ) -> None:
        with patch("pitchcritic.api.extract_pdf"), patch(
            "pitchcritic.api.critique_pitch",
            side_effect=CritiqueError("LLM down"),
        ):
            response = client.post(
                "/analyze",
                files={"file": ("pitch.pdf", sample_pdf_bytes, "application/pdf")},
            )
        assert response.status_code == 502
