"""Tests for the adversarial critic module."""

import json
from unittest.mock import MagicMock

from pitchcritic.critic import (
    DIMENSIONS,
    PitchCritique,
    _parse_json_response,
    critique_pitch,
)


def _make_mock_llm(score: int = 5, add_flaw_to_first: bool = True) -> MagicMock:
    payload = {
        "dimensions": [
            {
                "dimension": dim,
                "score": score,
                "critique": f"Test critique for {dim}.",
                "fatal_flaw": "Missing proof" if (i == 0 and add_flaw_to_first) else None,
            }
            for i, dim in enumerate(DIMENSIONS)
        ],
        "overall_verdict": "This pitch is forgettable.",
    }
    return MagicMock(return_value=json.dumps(payload))


def test_critique_returns_pitch_critique() -> None:
    result = critique_pitch("Test pitch content", llm_caller=_make_mock_llm())
    assert isinstance(result, PitchCritique)


def test_critique_has_ten_dimensions() -> None:
    result = critique_pitch("Test pitch content", llm_caller=_make_mock_llm())
    assert len(result.dimensions) == 10


def test_all_dimension_names_present() -> None:
    result = critique_pitch("Test pitch content", llm_caller=_make_mock_llm())
    names = {d.dimension for d in result.dimensions}
    assert names == set(DIMENSIONS)


def test_dimension_scores_in_range() -> None:
    result = critique_pitch("Test pitch content", llm_caller=_make_mock_llm(7))
    for d in result.dimensions:
        assert 0 <= d.score <= 10


def test_dimension_critique_is_non_empty_string() -> None:
    result = critique_pitch("Test pitch content", llm_caller=_make_mock_llm())
    for d in result.dimensions:
        assert isinstance(d.critique, str)
        assert len(d.critique) > 0


def test_overall_verdict_is_string() -> None:
    result = critique_pitch("Test pitch content", llm_caller=_make_mock_llm())
    assert isinstance(result.overall_verdict, str)
    assert len(result.overall_verdict) > 0


def test_critique_strips_markdown_code_fence() -> None:
    payload = {
        "dimensions": [
            {"dimension": dim, "score": 5, "critique": "Test.", "fatal_flaw": None}
            for dim in DIMENSIONS
        ],
        "overall_verdict": "Test verdict.",
    }
    json_in_markdown = f"```json\n{json.dumps(payload)}\n```"
    mock = MagicMock(return_value=json_in_markdown)
    result = critique_pitch("Test pitch", llm_caller=mock)
    assert len(result.dimensions) == 10


def test_fatal_flaw_can_be_none() -> None:
    result = critique_pitch("Test pitch content", llm_caller=_make_mock_llm())
    none_flaws = [d for d in result.dimensions if d.fatal_flaw is None]
    assert len(none_flaws) == 9


def test_fatal_flaw_populated_when_present() -> None:
    result = critique_pitch("Test pitch content", llm_caller=_make_mock_llm())
    first = result.dimensions[0]
    assert first.fatal_flaw == "Missing proof"


def test_parse_json_response_plain() -> None:
    data = {"dimensions": [], "overall_verdict": "test"}
    assert _parse_json_response(json.dumps(data)) == data


def test_parse_json_response_with_fence() -> None:
    data = {"dimensions": [], "overall_verdict": "test"}
    fenced = f"```json\n{json.dumps(data)}\n```"
    assert _parse_json_response(fenced) == data
