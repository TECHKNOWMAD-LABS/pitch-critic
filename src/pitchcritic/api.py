"""FastAPI application exposing the PitchCritic analysis endpoint."""

import logging
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from .critic import CritiqueError, critique_pitch
from .extractor import ExtractionError, extract_pdf
from .scorer import calculate_score

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB

app = FastAPI(
    title="PitchCritic",
    description="Upload your pitch deck, get it destroyed.",
    version="0.1.0",
)


class DimensionResult(BaseModel):
    dimension: str
    score: int
    critique: str
    fatal_flaw: str | None


class AnalysisResult(BaseModel):
    total_score: int
    grade: str
    verdict: str
    overall_verdict: str
    dimensions: list[DimensionResult]
    fatal_flaws: list[str]
    slide_count: int


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_pitch(file: UploadFile = File(...)) -> AnalysisResult:
    """Accept a pitch deck PDF and return a 0-100 adversarial score."""
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({len(content) / 1024 / 1024:.1f} MB). Max is 50 MB.",
        )

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        pitch_content = extract_pdf(tmp_path)
        critique = critique_pitch(pitch_content.text)
        score = calculate_score(critique)
    except ExtractionError as exc:
        logger.warning("PDF extraction failed: %s", exc)
        raise HTTPException(status_code=422, detail=f"PDF extraction failed: {exc}")
    except CritiqueError as exc:
        logger.error("Critique generation failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Analysis failed: {exc}")
    finally:
        tmp_path.unlink(missing_ok=True)

    return AnalysisResult(
        total_score=score.total,
        grade=score.grade,
        verdict=score.verdict,
        overall_verdict=critique.overall_verdict,
        dimensions=[
            DimensionResult(
                dimension=d.dimension,
                score=d.score,
                critique=d.critique,
                fatal_flaw=d.fatal_flaw,
            )
            for d in critique.dimensions
        ],
        fatal_flaws=score.fatal_flaws,
        slide_count=pitch_content.slide_count,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
