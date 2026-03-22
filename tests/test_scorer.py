"""Tests for the scoring module."""


from pitchcritic.critic import DIMENSIONS, DimensionCritique, PitchCritique
from pitchcritic.scorer import PitchScore, calculate_score


def _make_critique(score_per_dim: int = 5, with_flaws: bool = False) -> PitchCritique:
    dimensions = [
        DimensionCritique(
            dimension=dim,
            score=score_per_dim,
            critique=f"Test {dim}.",
            fatal_flaw=f"Flaw in {dim}" if with_flaws else None,
        )
        for dim in DIMENSIONS
    ]
    return PitchCritique(dimensions=dimensions, overall_verdict="Test verdict.")


def test_calculate_score_returns_pitch_score() -> None:
    result = calculate_score(_make_critique())
    assert isinstance(result, PitchScore)


def test_perfect_score_is_100() -> None:
    result = calculate_score(_make_critique(score_per_dim=10))
    assert result.total == 100


def test_zero_score_is_0() -> None:
    result = calculate_score(_make_critique(score_per_dim=0))
    assert result.total == 0


def test_mid_score_is_50() -> None:
    result = calculate_score(_make_critique(score_per_dim=5))
    assert result.total == 50


def test_grade_a_for_high_score() -> None:
    result = calculate_score(_make_critique(score_per_dim=9))
    assert result.grade == "A"


def test_grade_b_for_mid_high_score() -> None:
    # 7 * 10 = 70 → B
    result = calculate_score(_make_critique(score_per_dim=7))
    assert result.grade == "B"


def test_grade_f_for_low_score() -> None:
    result = calculate_score(_make_critique(score_per_dim=2))
    assert result.grade == "F"


def test_total_never_exceeds_100() -> None:
    result = calculate_score(_make_critique(score_per_dim=10))
    assert result.total <= 100


def test_total_never_below_0() -> None:
    result = calculate_score(_make_critique(score_per_dim=0))
    assert result.total >= 0


def test_fatal_flaws_collected_when_present() -> None:
    result = calculate_score(_make_critique(with_flaws=True))
    assert len(result.fatal_flaws) == 10


def test_no_fatal_flaws_when_all_none() -> None:
    result = calculate_score(_make_critique(with_flaws=False))
    assert result.fatal_flaws == []


def test_dimension_scores_dict_has_all_dimensions() -> None:
    result = calculate_score(_make_critique(score_per_dim=7))
    assert set(result.dimension_scores.keys()) == set(DIMENSIONS)


def test_verdict_fundable_for_top_scores() -> None:
    result = calculate_score(_make_critique(score_per_dim=9))
    assert result.verdict == "Fundable"


def test_verdict_pass_for_bottom_scores() -> None:
    result = calculate_score(_make_critique(score_per_dim=1))
    assert result.verdict == "Pass"
