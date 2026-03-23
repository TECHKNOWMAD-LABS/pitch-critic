"""Property-based tests using Hypothesis for core invariants."""

import json

from hypothesis import given, settings
from hypothesis import strategies as st

from pitchcritic.critic import (
    DIMENSIONS,
    DimensionCritique,
    PitchCritique,
    _parse_json_response,
    critique_pitch,
)
from pitchcritic.scorer import PitchScore, calculate_score


# --- Strategies ---

score_strategy = st.integers(min_value=0, max_value=10)
dimension_strategy = st.sampled_from(DIMENSIONS)


def make_dimension_critique(dim: str, score: int, flaw: str | None = None) -> dict:
    return {
        "dimension": dim,
        "score": score,
        "critique": f"Critique for {dim}.",
        "fatal_flaw": flaw,
    }


@st.composite
def valid_llm_response(draw: st.DrawFn) -> str:
    """Generate a valid LLM JSON response with random scores."""
    scores = [draw(score_strategy) for _ in DIMENSIONS]
    has_flaw = draw(st.booleans())
    payload = {
        "dimensions": [
            make_dimension_critique(
                dim, score, "A flaw" if (has_flaw and i == 0) else None
            )
            for i, (dim, score) in enumerate(zip(DIMENSIONS, scores))
        ],
        "overall_verdict": draw(st.text(min_size=1, max_size=200)),
    }
    return json.dumps(payload)


@st.composite
def pitch_critique_strategy(draw: st.DrawFn) -> PitchCritique:
    """Generate a random PitchCritique with valid scores."""
    scores = [draw(score_strategy) for _ in DIMENSIONS]
    flaws = [draw(st.booleans()) for _ in DIMENSIONS]
    return PitchCritique(
        dimensions=[
            DimensionCritique(
                dimension=dim,
                score=score,
                critique=f"Critique for {dim}.",
                fatal_flaw=f"Flaw in {dim}" if has_flaw else None,
            )
            for dim, score, has_flaw in zip(DIMENSIONS, scores, flaws)
        ],
        overall_verdict="Test verdict.",
    )


# --- Property tests: scorer invariants ---


class TestScorerProperties:
    """Property-based tests for scoring invariants."""

    @given(critique=pitch_critique_strategy())
    @settings(max_examples=200)
    def test_total_score_always_0_to_100(self, critique: PitchCritique) -> None:
        score = calculate_score(critique)
        assert 0 <= score.total <= 100

    @given(critique=pitch_critique_strategy())
    @settings(max_examples=200)
    def test_grade_always_valid(self, critique: PitchCritique) -> None:
        score = calculate_score(critique)
        assert score.grade in ("A", "B", "C", "D", "F")

    @given(critique=pitch_critique_strategy())
    @settings(max_examples=200)
    def test_verdict_always_valid(self, critique: PitchCritique) -> None:
        score = calculate_score(critique)
        assert score.verdict in ("Fundable", "Needs Work", "Major Gaps", "Weak", "Pass")

    @given(critique=pitch_critique_strategy())
    @settings(max_examples=200)
    def test_dimension_scores_dict_complete(self, critique: PitchCritique) -> None:
        score = calculate_score(critique)
        assert set(score.dimension_scores.keys()) == set(DIMENSIONS)

    @given(critique=pitch_critique_strategy())
    @settings(max_examples=200)
    def test_fatal_flaws_count_matches_non_none(self, critique: PitchCritique) -> None:
        score = calculate_score(critique)
        expected = sum(1 for d in critique.dimensions if d.fatal_flaw)
        assert len(score.fatal_flaws) == expected

    @given(critique=pitch_critique_strategy())
    @settings(max_examples=100)
    def test_score_is_sum_of_dimensions(self, critique: PitchCritique) -> None:
        score = calculate_score(critique)
        raw_sum = sum(d.score for d in critique.dimensions)
        assert score.total == max(0, min(100, raw_sum))

    @given(critique=pitch_critique_strategy())
    @settings(max_examples=100)
    def test_grade_monotonic_with_score(self, critique: PitchCritique) -> None:
        """Higher scores should never produce lower grades."""
        score = calculate_score(critique)
        grade_order = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
        grade_val = grade_order[score.grade]
        if score.total >= 85:
            assert grade_val == 4
        elif score.total >= 70:
            assert grade_val == 3
        elif score.total >= 55:
            assert grade_val == 2
        elif score.total >= 40:
            assert grade_val == 1
        else:
            assert grade_val == 0


# --- Property tests: critic parse invariants ---


class TestParseProperties:
    """Property-based tests for JSON parsing."""

    @given(response=valid_llm_response())
    @settings(max_examples=100)
    def test_parse_roundtrip_preserves_data(self, response: str) -> None:
        """Parsing valid JSON should never crash."""
        data = _parse_json_response(response)
        assert "dimensions" in data
        assert "overall_verdict" in data
        assert len(data["dimensions"]) == 10

    @given(response=valid_llm_response())
    @settings(max_examples=50)
    def test_parse_with_code_fence_roundtrip(self, response: str) -> None:
        """Wrapping in code fences should produce identical parsed output."""
        plain = _parse_json_response(response)
        fenced = _parse_json_response(f"```json\n{response}\n```")
        assert plain == fenced


# --- Property tests: critique with mock LLM ---


class TestCritiqueProperties:
    """Property-based tests for full critique pipeline."""

    @given(response=valid_llm_response())
    @settings(max_examples=100)
    def test_critique_never_crashes_on_valid_response(self, response: str) -> None:
        from unittest.mock import MagicMock

        mock = MagicMock(return_value=response)
        result = critique_pitch("Test content", llm_caller=mock)
        assert isinstance(result, PitchCritique)
        assert len(result.dimensions) == 10

    @given(response=valid_llm_response())
    @settings(max_examples=100)
    def test_all_scores_clamped_0_to_10(self, response: str) -> None:
        from unittest.mock import MagicMock

        mock = MagicMock(return_value=response)
        result = critique_pitch("Test content", llm_caller=mock)
        for d in result.dimensions:
            assert 0 <= d.score <= 10

    @given(
        content=st.text(min_size=1, max_size=5000, alphabet=st.characters(codec="utf-8"))
    )
    @settings(max_examples=50)
    def test_no_crash_on_random_unicode_content(self, content: str) -> None:
        """Critique should handle any unicode content without crashing."""
        from unittest.mock import MagicMock

        payload = {
            "dimensions": [
                make_dimension_critique(dim, 5) for dim in DIMENSIONS
            ],
            "overall_verdict": "Test.",
        }
        mock = MagicMock(return_value=json.dumps(payload))
        result = critique_pitch(content, llm_caller=mock)
        assert isinstance(result, PitchCritique)
