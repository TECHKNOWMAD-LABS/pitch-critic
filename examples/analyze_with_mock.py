#!/usr/bin/env python3
"""Example: Analyze a pitch deck using a mock LLM caller.

This demonstrates the full pipeline without requiring an API key.
Useful for testing, CI, and understanding the data flow.
"""

import json

from pitchcritic.critic import DIMENSIONS, critique_pitch
from pitchcritic.scorer import calculate_score


def mock_llm_caller(system: str, user: str) -> str:
    """Simulate an LLM response with realistic scores."""
    payload = {
        "dimensions": [
            {
                "dimension": "problem_clarity",
                "score": 8,
                "critique": "Clear problem statement with quantified pain point.",
                "fatal_flaw": None,
            },
            {
                "dimension": "solution_fit",
                "score": 7,
                "critique": "Solution addresses the problem but differentiation is weak.",
                "fatal_flaw": None,
            },
            {
                "dimension": "market_size",
                "score": 6,
                "critique": "TAM is reasonable but SAM/SOM lacks geographic specificity.",
                "fatal_flaw": None,
            },
            {
                "dimension": "business_model",
                "score": 5,
                "critique": "SaaS model is standard but margins seem optimistic.",
                "fatal_flaw": "40% gross margin is below SaaS benchmarks",
            },
            {
                "dimension": "traction",
                "score": 7,
                "critique": "500 beta users and $50K MRR is decent for pre-seed.",
                "fatal_flaw": None,
            },
            {
                "dimension": "team_strength",
                "score": 8,
                "critique": "Strong technical founders with relevant experience.",
                "fatal_flaw": None,
            },
            {
                "dimension": "competitive_moat",
                "score": 4,
                "critique": "AI automation is not a moat — it's a feature.",
                "fatal_flaw": "No defensible moat articulated",
            },
            {
                "dimension": "financial_projections",
                "score": 3,
                "critique": "Hockey stick from $1.2M to $15M ARR with no basis shown.",
                "fatal_flaw": "Projections are fantasy without supporting assumptions",
            },
            {
                "dimension": "go_to_market",
                "score": 6,
                "critique": "SMB communities is a channel, not a strategy.",
                "fatal_flaw": None,
            },
            {
                "dimension": "investment_thesis",
                "score": 5,
                "critique": "$15M cap for a pre-seed with $50K MRR needs justification.",
                "fatal_flaw": None,
            },
        ],
        "overall_verdict": (
            "A competent but uninspiring pitch. Strong team, weak moat, "
            "and financial projections that belong in a fairy tale."
        ),
    }
    return json.dumps(payload)


def main() -> None:
    # Simulate pitch deck text
    pitch_text = """
    Problem: Small businesses lose $50B annually to manual invoicing errors.
    Solution: AI-powered invoicing that reduces errors by 95%.
    Market: TAM $200B, SAM $40B, SOM $2B.
    Business Model: SaaS, $99/mo per seat, 40% gross margin.
    Traction: 500 beta users, $50K MRR, 15% MoM growth.
    Team: CEO ex-Stripe, CTO ex-Google.
    Competition: QuickBooks, FreshBooks. We win on AI automation.
    Financials: Year 1 $1.2M ARR, Year 3 $15M ARR.
    GTM: Bottom-up via SMB communities, $180 CAC.
    Ask: Raising $3M Seed at $15M cap.
    """

    # Run the critique pipeline
    critique = critique_pitch(pitch_text, llm_caller=mock_llm_caller)
    score = calculate_score(critique)

    # Display results
    print(f"Total Score: {score.total}/100")
    print(f"Grade: {score.grade}")
    print(f"Verdict: {score.verdict}")
    print(f"\nOverall: {critique.overall_verdict}")
    print(f"\nFatal Flaws ({len(score.fatal_flaws)}):")
    for flaw in score.fatal_flaws:
        print(f"  - {flaw}")
    print("\nDimension Breakdown:")
    for d in critique.dimensions:
        flaw_marker = " [FATAL]" if d.fatal_flaw else ""
        print(f"  {d.dimension}: {d.score}/10{flaw_marker}")


if __name__ == "__main__":
    main()
