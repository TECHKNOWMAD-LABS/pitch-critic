# PitchCritic

**Upload your pitch deck, get it destroyed.**

A brutally honest AI-powered pitch deck analyzer that scores your startup pitch across 10 adversarial dimensions, producing a 0-100 Pitch Score with specific callouts of every weakness, inconsistency, and fatal flaw.

## What it does

PitchCritic extracts text from your PDF, sends it to Claude Opus, and gets back a hyper-critical VC perspective across 10 dimensions:

| Dimension | Question |
|---|---|
| Problem Clarity | Is the problem real, painful, and clearly articulated? |
| Solution Fit | Does the solution directly address the problem? |
| Market Size | Is the TAM/SAM/SOM credible and large enough? |
| Business Model | Is the revenue model clear and scalable? |
| Traction | Evidence of real customer demand? |
| Team Strength | Relevant domain expertise and execution history? |
| Competitive Moat | Are the moats real or marketing fluff? |
| Financial Projections | Grounded in reality? |
| Go-to-Market | Specific and executable? |
| Investment Thesis | Ask clear, valuation justified? |

Each dimension is scored 0–10. Total = Pitch Score (0–100).

| Score | Grade | Verdict |
|---|---|---|
| 85–100 | A | Fundable |
| 70–84 | B | Needs Work |
| 55–69 | C | Major Gaps |
| 40–54 | D | Weak |
| 0–39 | F | Pass |

## Install

```bash
pip install -e ".[dev]"
```

Set your API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## CLI

```bash
pitchcritic analyze deck.pdf
pitchcritic analyze deck.pdf --verbose
```

## API

```bash
uvicorn pitchcritic.api:app --reload
```

```
POST /analyze   multipart/form-data  file=<your_deck.pdf>
GET  /health
```

Example with curl:

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@deck.pdf" | jq .
```

## Test

```bash
pytest -v
```

## License

MIT
