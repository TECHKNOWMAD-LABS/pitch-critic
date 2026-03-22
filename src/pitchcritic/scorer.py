"""Pitch scoring: aggregate 10 dimension scores into a 0-100 total."""

from dataclasses import dataclass

from .critic import PitchCritique


@dataclass
class PitchScore:
    total: int
    dimension_scores: dict[str, int]
    grade: str
    verdict: str
    fatal_flaws: list[str]


def calculate_score(critique: PitchCritique) -> PitchScore:
    """Aggregate dimension scores (each 0-10) into a 0-100 Pitch Score."""
    dimension_scores = {d.dimension: d.score for d in critique.dimensions}
    total = max(0, min(100, sum(dimension_scores.values())))

    fatal_flaws = [
        f"{d.dimension}: {d.fatal_flaw}"
        for d in critique.dimensions
        if d.fatal_flaw
    ]

    return PitchScore(
        total=total,
        dimension_scores=dimension_scores,
        grade=_grade(total),
        verdict=_verdict(total),
        fatal_flaws=fatal_flaws,
    )


def _grade(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _verdict(score: int) -> str:
    if score >= 85:
        return "Fundable"
    if score >= 70:
        return "Needs Work"
    if score >= 55:
        return "Major Gaps"
    if score >= 40:
        return "Weak"
    return "Pass"
