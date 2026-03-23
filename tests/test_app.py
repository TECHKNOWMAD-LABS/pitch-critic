"""Tests for the CLI entry point module."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from pitchcritic.app import cli
from pitchcritic.critic import DIMENSIONS, DimensionCritique, PitchCritique

runner = CliRunner()


def _mock_critique(score: int = 5, with_flaws: bool = False) -> PitchCritique:
    return PitchCritique(
        dimensions=[
            DimensionCritique(
                dimension=dim,
                score=score,
                critique=f"Test critique for {dim}.",
                fatal_flaw=f"Fatal: {dim}" if with_flaws else None,
            )
            for dim in DIMENSIONS
        ],
        overall_verdict="This pitch is mediocre at best.",
    )


def _mock_llm_json(score: int = 5, with_flaws: bool = False) -> MagicMock:
    payload = {
        "dimensions": [
            {
                "dimension": dim,
                "score": score,
                "critique": f"Test critique for {dim}.",
                "fatal_flaw": f"Fatal: {dim}" if with_flaws else None,
            }
            for dim in DIMENSIONS
        ],
        "overall_verdict": "This pitch is mediocre at best.",
    }
    return MagicMock(return_value=json.dumps(payload))


class TestAnalyzeCommand:
    """Tests for the CLI analyze command."""

    def test_nonexistent_file_exits_with_error(self) -> None:
        result = runner.invoke(cli, ["/tmp/does_not_exist_xyz.pdf"])
        assert result.exit_code == 1

    @patch("pitchcritic.app.critique_pitch", return_value=_mock_critique())
    def test_successful_analysis(
        self, mock_critique: MagicMock, sample_pdf_path: Path
    ) -> None:
        result = runner.invoke(cli, [str(sample_pdf_path)])
        assert result.exit_code == 0
        assert "50" in result.output or "Pitch Score" in result.output

    @patch("pitchcritic.app.critique_pitch", return_value=_mock_critique())
    def test_verbose_mode_shows_critiques(
        self, mock_critique: MagicMock, sample_pdf_path: Path
    ) -> None:
        result = runner.invoke(cli, [str(sample_pdf_path), "--verbose"])
        assert result.exit_code == 0
        assert "Critique" in result.output or "Test critique" in result.output

    @patch("pitchcritic.app.critique_pitch", return_value=_mock_critique(9))
    def test_high_score_shows_green_grade(
        self, mock_critique: MagicMock, sample_pdf_path: Path
    ) -> None:
        result = runner.invoke(cli, [str(sample_pdf_path)])
        assert result.exit_code == 0
        assert "90" in result.output

    @patch("pitchcritic.app.critique_pitch", return_value=_mock_critique(2))
    def test_low_score_output(
        self, mock_critique: MagicMock, sample_pdf_path: Path
    ) -> None:
        result = runner.invoke(cli, [str(sample_pdf_path)])
        assert result.exit_code == 0
        assert "20" in result.output

    @patch(
        "pitchcritic.app.critique_pitch",
        return_value=_mock_critique(3, with_flaws=True),
    )
    def test_fatal_flaws_displayed(
        self, mock_critique: MagicMock, sample_pdf_path: Path
    ) -> None:
        result = runner.invoke(cli, [str(sample_pdf_path)])
        assert result.exit_code == 0
        assert "Fatal Flaws" in result.output

    @patch("pitchcritic.app.critique_pitch", return_value=_mock_critique())
    def test_shows_slide_count(
        self, mock_critique: MagicMock, sample_pdf_path: Path
    ) -> None:
        result = runner.invoke(cli, [str(sample_pdf_path)])
        assert result.exit_code == 0
        assert "10" in result.output

    @patch("pitchcritic.app.critique_pitch", return_value=_mock_critique())
    def test_shows_overall_verdict(
        self, mock_critique: MagicMock, sample_pdf_path: Path
    ) -> None:
        result = runner.invoke(cli, [str(sample_pdf_path)])
        assert result.exit_code == 0
        assert "Overall Verdict" in result.output
