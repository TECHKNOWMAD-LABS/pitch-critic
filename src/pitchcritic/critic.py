"""10-dimension adversarial pitch analysis."""

import json
from dataclasses import dataclass

from .llm import LLMCaller, get_default_caller

DIMENSIONS = [
    "problem_clarity",
    "solution_fit",
    "market_size",
    "business_model",
    "traction",
    "team_strength",
    "competitive_moat",
    "financial_projections",
    "go_to_market",
    "investment_thesis",
]

DIMENSION_DESCRIPTIONS: dict[str, str] = {
    "problem_clarity": "Is the problem real, painful, and clearly articulated?",
    "solution_fit": (
        "Does the solution directly address the problem with defensible differentiation?"
    ),
    "market_size": "Is the TAM/SAM/SOM credible and large enough to matter?",
    "business_model": "Is the revenue model clear, scalable, and believable?",
    "traction": "Is there evidence of real customer demand—paid users, LOIs, or meaningful pilots?",
    "team_strength": (
        "Does the founding team have relevant domain expertise and execution history?"
    ),
    "competitive_moat": "Are the moats real and durable, or just marketing fluff?",
    "financial_projections": (
        "Are the financial projections grounded in reality with sound assumptions?"
    ),
    "go_to_market": "Is the customer acquisition strategy specific and executable?",
    "investment_thesis": (
        "Is the investment ask clear, the valuation justified, and the exit path credible?"
    ),
}

_SYSTEM_PROMPT = """\
You are a hyper-critical venture capitalist who has seen thousands of pitch decks.
You are brutally honest, contrarian, and highly skeptical. You assume every founder is
delusional until proven otherwise. You look for fatal flaws, not strengths. You have zero
tolerance for vague claims, hockey-stick projections without basis, and buzzword-heavy
slides without substance.

You must evaluate the pitch deck on exactly 10 dimensions and return ONLY valid JSON.

Score each dimension 0-10 where:
- 0-2: Catastrophically bad or completely missing
- 3-4: Weak, vague, or unconvincing
- 5-6: Adequate but nothing special
- 7-8: Strong with minor gaps
- 9-10: Exceptional (rare)

Be adversarial. If something is missing, score it 0. If a claim is unsubstantiated, call it out.
The overall_verdict should be 1-2 sentences of brutal honesty.\
"""


@dataclass
class DimensionCritique:
    dimension: str
    score: int
    critique: str
    fatal_flaw: str | None = None


@dataclass
class PitchCritique:
    dimensions: list[DimensionCritique]
    overall_verdict: str


def critique_pitch(
    content: str,
    llm_caller: LLMCaller | None = None,
) -> PitchCritique:
    """Run adversarial 10-dimension critique against pitch deck content."""
    if llm_caller is None:
        llm_caller = get_default_caller()

    dimension_list = "\n".join(
        f'  "{dim}": "{desc}"' for dim, desc in DIMENSION_DESCRIPTIONS.items()
    )

    user_prompt = f"""\
Evaluate this pitch deck content on the following 10 dimensions:
{dimension_list}

Return ONLY valid JSON in this exact format:
{{
  "dimensions": [
    {{
      "dimension": "<dimension_name>",
      "score": <0-10>,
      "critique": "<brutal 2-3 sentence critique>",
      "fatal_flaw": "<the single biggest problem, or null if none>"
    }}
  ],
  "overall_verdict": "<1-2 sentence brutal summary>"
}}

PITCH DECK CONTENT:
---
{content[:8000]}
---\
"""

    raw = llm_caller(_SYSTEM_PROMPT, user_prompt)
    data = _parse_json_response(raw)

    dimensions = [
        DimensionCritique(
            dimension=d["dimension"],
            score=int(d["score"]),
            critique=d["critique"],
            fatal_flaw=d.get("fatal_flaw"),
        )
        for d in data["dimensions"]
    ]

    return PitchCritique(dimensions=dimensions, overall_verdict=data["overall_verdict"])


def _parse_json_response(raw: str) -> dict:
    """Extract JSON from LLM response, stripping markdown code fences if present."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop opening fence (```json or ```) and closing fence (```)
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        text = "\n".join(inner)
    return json.loads(text)
