"""Tests for the FastAPI endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from pitchcritic.api import app
from pitchcritic.critic import DIMENSIONS, DimensionCritique, PitchCritique


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _mock_critique(score: int = 5) -> PitchCritique:
    return PitchCritique(
        dimensions=[
            DimensionCritique(
                dimension=dim,
                score=score,
                critique=f"Test {dim}.",
                fatal_flaw=None,
            )
            for dim in DIMENSIONS
        ],
        overall_verdict="Mediocre at best. Try again.",
    )


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_returns_200_for_pdf(client: TestClient, sample_pdf_bytes: bytes) -> None:
    with patch("pitchcritic.api.critique_pitch", return_value=_mock_critique()):
        response = client.post(
            "/analyze",
            files={"file": ("pitch.pdf", sample_pdf_bytes, "application/pdf")},
        )
    assert response.status_code == 200


def test_analyze_returns_score_in_range(client: TestClient, sample_pdf_bytes: bytes) -> None:
    with patch("pitchcritic.api.critique_pitch", return_value=_mock_critique(5)):
        response = client.post(
            "/analyze",
            files={"file": ("pitch.pdf", sample_pdf_bytes, "application/pdf")},
        )
    data = response.json()
    assert "total_score" in data
    assert 0 <= data["total_score"] <= 100


def test_analyze_returns_ten_dimensions(client: TestClient, sample_pdf_bytes: bytes) -> None:
    with patch("pitchcritic.api.critique_pitch", return_value=_mock_critique()):
        response = client.post(
            "/analyze",
            files={"file": ("pitch.pdf", sample_pdf_bytes, "application/pdf")},
        )
    assert len(response.json()["dimensions"]) == 10


def test_analyze_returns_grade(client: TestClient, sample_pdf_bytes: bytes) -> None:
    with patch("pitchcritic.api.critique_pitch", return_value=_mock_critique()):
        response = client.post(
            "/analyze",
            files={"file": ("pitch.pdf", sample_pdf_bytes, "application/pdf")},
        )
    data = response.json()
    assert "grade" in data
    assert data["grade"] in ("A", "B", "C", "D", "F")


def test_analyze_returns_slide_count(client: TestClient, sample_pdf_bytes: bytes) -> None:
    with patch("pitchcritic.api.critique_pitch", return_value=_mock_critique()):
        response = client.post(
            "/analyze",
            files={"file": ("pitch.pdf", sample_pdf_bytes, "application/pdf")},
        )
    assert response.json()["slide_count"] == 10


def test_analyze_rejects_non_pdf(client: TestClient) -> None:
    response = client.post(
        "/analyze",
        files={"file": ("deck.txt", b"not a pdf", "text/plain")},
    )
    assert response.status_code == 400


def test_analyze_returns_overall_verdict(client: TestClient, sample_pdf_bytes: bytes) -> None:
    with patch("pitchcritic.api.critique_pitch", return_value=_mock_critique()):
        response = client.post(
            "/analyze",
            files={"file": ("pitch.pdf", sample_pdf_bytes, "application/pdf")},
        )
    data = response.json()
    assert "overall_verdict" in data
    assert isinstance(data["overall_verdict"], str)
