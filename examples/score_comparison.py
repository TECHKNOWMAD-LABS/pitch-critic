#!/usr/bin/env python3
"""Example: Compare scoring across different pitch quality levels.

Demonstrates how the scorer module maps dimension scores to grades,
verdicts, and fatal flaw detection.
"""

from pitchcritic.critic import DIMENSIONS, DimensionCritique, PitchCritique
from pitchcritic.scorer import calculate_score


def make_pitch(
    label: str,
    base_score: int,
    fatal_dimensions: list[str] | None = None,
) -> tuple[str, PitchCritique]:
    """Create a PitchCritique with uniform scores and optional fatal flaws."""
    fatal_dims = set(fatal_dimensions or [])
    return label, PitchCritique(
        dimensions=[
            DimensionCritique(
                dimension=dim,
                score=base_score,
                critique=f"Score of {base_score} for {dim}.",
                fatal_flaw=f"Critical issue in {dim}" if dim in fatal_dims else None,
            )
            for dim in DIMENSIONS
        ],
        overall_verdict=f"Pitch with base score {base_score}.",
    )


def main() -> None:
    scenarios = [
        make_pitch("Exceptional Pitch", 9),
        make_pitch("Strong Pitch", 7),
        make_pitch("Average Pitch", 5),
        make_pitch("Weak Pitch", 3),
        make_pitch("Terrible Pitch", 1),
        make_pitch(
            "Mixed — Strong but Fatal Flaws",
            7,
            fatal_dimensions=["competitive_moat", "financial_projections"],
        ),
    ]

    print(f"{'Scenario':<35} {'Score':>5} {'Grade':>5} {'Verdict':<12} {'Flaws':>5}")
    print("-" * 70)

    for label, critique in scenarios:
        score = calculate_score(critique)
        print(
            f"{label:<35} {score.total:>5} {score.grade:>5} "
            f"{score.verdict:<12} {len(score.fatal_flaws):>5}"
        )


if __name__ == "__main__":
    main()
