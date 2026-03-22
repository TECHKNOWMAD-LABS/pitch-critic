# PitchCritic

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Tests](https://img.shields.io/badge/tests-28%20passing-brightgreen.svg)](#test)

**Upload your pitch deck, get it destroyed.**

A brutally honest AI-powered pitch deck analyzer. Scores your startup pitch across 10 adversarial dimensions and produces a 0–100 Pitch Score with specific callouts of every weakness, inconsistency, and fatal flaw.

---

## Features

- **10-dimension VC critique** — Problem, Solution, Market, Business Model, Traction, Team, Moat, Financials, GTM, and Investment Thesis scored 0–10 each
- **Fatal flaw detection** — Surfaces deal-breakers that would cause a VC to pass, not polish
- **Graded verdicts** — A (Fundable) through F (Pass), mapped from the aggregate 0–100 score
- **CLI and REST API** — Run locally with `pitchcritic analyze deck.pdf` or deploy as a FastAPI service
- **Structured JSON output** — Every critique is machine-readable; pipe into dashboards or bulk-analysis pipelines
- **Clean pipeline architecture** — Extract → Critique → Score stages are independently testable and replaceable

---

## Quick Start

**Prerequisites:** Python 3.12+, an [Anthropic API key](https://console.anthropic.com/)

```bash
# Install
pip install -e ".[dev]"

# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Analyze a deck
pitchcritic analyze deck.pdf

# Full per-dimension breakdown
pitchcritic analyze deck.pdf --verbose
```

**Expected output (non-verbose):**

```
Pitch Score: 61 / 100   Grade: C   Verdict: Major Gaps

Fatal Flaws
  • No evidence of customer discovery — problem assumptions are unvalidated
  • TAM figure ($40B) is not cited and appears inflated
  • No moat articulated beyond "first mover advantage"
```

---

## REST API

```bash
uvicorn pitchcritic.api:app --reload
```

| Method | Endpoint  | Body                              | Description        |
|--------|-----------|-----------------------------------|--------------------|
| POST   | /analyze  | `multipart/form-data` `file=*.pdf`| Analyze a deck     |
| GET    | /health   | —                                 | Liveness check     |

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@deck.pdf" | jq .
```

Response schema:

```json
{
  "score": 61,
  "grade": "C",
  "verdict": "Major Gaps",
  "dimensions": [
    { "name": "Problem Clarity", "score": 7, "critique": "..." }
  ],
  "fatal_flaws": ["..."]
}
```

---

## Scoring Reference

| Dimension            | Question                                         |
|----------------------|--------------------------------------------------|
| Problem Clarity      | Is the problem real, painful, and specific?      |
| Solution Fit         | Does the solution directly address the problem?  |
| Market Size          | Is the TAM/SAM/SOM credible and large enough?    |
| Business Model       | Is the revenue model clear and scalable?         |
| Traction             | Evidence of real customer demand?                |
| Team Strength        | Relevant domain expertise and execution history? |
| Competitive Moat     | Are the moats real or marketing fluff?           |
| Financial Projections| Grounded in reality?                             |
| Go-to-Market         | Specific and executable?                         |
| Investment Thesis    | Ask clear, valuation justified?                  |

| Score  | Grade | Verdict     |
|--------|-------|-------------|
| 85–100 | A     | Fundable    |
| 70–84  | B     | Needs Work  |
| 55–69  | C     | Major Gaps  |
| 40–54  | D     | Weak        |
| 0–39   | F     | Pass        |

---

## Architecture

```
PDF input
    │
    ▼
extractor.py   ← pdfplumber: extracts text per slide → PitchContent
    │
    ▼
critic.py      ← Claude Opus via Anthropic API: scores 10 dimensions → DimensionResult[]
    │
    ▼
scorer.py      ← aggregates scores, assigns grade/verdict, collects fatal flaws → AnalysisResult
    │
    ├─▶ app.py    (Typer CLI — rich-formatted tables and panels)
    └─▶ api.py    (FastAPI — POST /analyze, GET /health)
```

**Module responsibilities:**

- `extractor.py` — PDF → `PitchContent(text, slide_count)`
- `llm.py` — Thin `LLMCaller` wrapper around `anthropic.Anthropic`; injectable for tests
- `critic.py` — System prompt encodes hyper-critical VC persona; parses JSON from Claude response (strips markdown fences)
- `scorer.py` — Pure aggregation; no I/O; fully unit-tested
- `app.py` / `api.py` — Thin delivery layers; no business logic

---

## Test

```bash
pytest -v
```

28 tests across `test_extractor`, `test_critic`, `test_scorer`, and `test_api`. Test fixtures generate real PDFs via `reportlab`.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

[MIT](LICENSE)

---

Built by [TechKnowMad Labs](https://techknowmad.ai)
