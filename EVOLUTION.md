# EVOLUTION.md — Edgecraft Protocol Execution Log

**Repository**: pitch-critic
**Date**: 2026-03-23
**Agent**: Claude Opus 4.6 via Edgecraft Protocol v4.0
**Starting state**: 3 commits, 41 tests, 70% coverage

---

## Cycle 1 — Test Coverage

**Objective**: Achieve >95% test coverage by testing all untested modules.

**Findings**:
- `app.py` (CLI module): 0% coverage — no tests existed
- `llm.py` (LLM interface): 47% coverage — only called indirectly
- `scorer.py`: 94% — minor branch gaps
- `critic.py`: 97% — one uncovered line

**Actions**:
- Created `tests/test_llm.py` — 6 tests covering `make_llm_caller` factory and `get_default_caller` singleton
- Created `tests/test_app.py` — 8 tests covering CLI analyze command (nonexistent file, verbose mode, score display, fatal flaws)

**Result**: 55 tests, 97% coverage (from 70%)

**Commits**:
- `34e5528` L5/action: add test suite for llm module — 6 tests
- `61c23a2` L5/action: add test suite for app CLI module — 8 tests
- `c602e3b` L6/grounding: 55 tests passing, coverage 70% → 97%

---

## Cycle 2 — Error Hardening

**Objective**: Make the codebase resilient to malformed, empty, and adversarial inputs.

**Findings**:
- Empty string to `critique_pitch()` → unhandled error from LLM
- Corrupt PDF → raw pdfplumber exception leaks to user
- Empty upload → passed through to extraction
- LLM returning invalid JSON → `json.JSONDecodeError` unhandled
- LLM scores outside 0-10 → passed through unclamped

**Actions**:
- Added `ExtractionError` class with validation: file exists, is PDF, non-empty, under 50MB, max 200 pages
- Added `CritiqueError` class with validation: non-empty content, LLM error wrapping, JSON validation, score clamping
- API layer: empty upload rejection, size limit, structured error responses (422/502)

**Result**: 69 tests, all passing

**Commits**:
- `017cc22` L3/sub-noise: empty/corrupt/oversized inputs cause unhandled crashes
- `cbca0ac` L5/action: add error handling test suite — 14 tests

---

## Cycle 3 — Performance

**Objective**: Reduce redundant computation through caching.

**Findings**:
- Repeated analysis of same PDF re-extracts and re-calls LLM every time
- No timeout on Anthropic API calls — could hang indefinitely

**Actions**:
- PDF extraction: SHA-256 content-hash cache avoids re-parsing identical files
- LLM caller: response cache (max 128 entries) keyed by SHA-256 of system+user prompts
- Configurable timeout (default 120s) on Anthropic client

**Result**: Repeated analysis of same deck drops to ~0ms. 69 tests passing.

**Commits**:
- `55632bc` L4/conjecture: content-hash caching for PDF extraction and LLM responses

---

## Cycle 4 — Security

**Objective**: Identify and fix security vulnerabilities.

**Findings**:
- 0 hardcoded secrets (API key properly loaded from env)
- 0 injection vectors (no os.system, subprocess, eval, exec)
- 1 path traversal vector: uploaded filename used without sanitization
- No `.gitignore` — risk of committing .env files

**Actions**:
- Sanitized upload filename with `Path.name` to strip directory components
- Created `.gitignore` excluding .env, *.pem, *.key, __pycache__, .venv

**Result**: All identified security issues resolved

**Commits**:
- `6556241` L2/noise: security scan — 0 hardcoded secrets, 1 path traversal fix

---

## Cycle 5 — CI/CD

**Objective**: Automate testing and linting on every code change.

**Actions**:
- Created `.github/workflows/ci.yml`: GitHub Actions with uv, Python 3.12, ruff check, pytest with coverage, format check
- Created `.pre-commit-config.yaml`: ruff (lint + format) and mypy hooks

**Result**: CI runs on every push to main and every PR

**Commits**:
- `413c39e` L5/action: add CI pipeline — tests + lint on every push and PR

---

## Cycle 6 — Property-Based Testing

**Objective**: Verify core invariants hold across randomly generated inputs.

**Actions**:
- 12 Hypothesis property tests across 4 strategy classes (~1000 generated examples):
  - Scorer: total always 0-100, grade/verdict always valid, monotonic with score, fatal flaws count matches
  - Parser: roundtrip preserves data, code fence wrapping is transparent
  - Critique: never crashes on valid responses, scores clamped, handles arbitrary unicode

**Result**: All invariants hold. No edge cases found by Hypothesis. 81 tests total.

**Commits**:
- `d9a4275` L6/grounding: 12 property tests passing across 4 strategy classes

---

## Cycle 7 — Examples + Docs

**Objective**: Provide working examples and ensure complete documentation.

**Actions**:
- `examples/analyze_with_mock.py`: Full pipeline demo with mock LLM (no API key needed)
- `examples/score_comparison.py`: Grade/verdict comparison across quality levels
- `examples/extract_pdf_demo.py`: PDF extraction with auto-generated sample deck
- All three examples tested and producing correct output

**Result**: Users can understand the system without reading source code

**Commits**:
- `4377a6a` L5/action: add working examples and complete docstring coverage

---

## Cycle 8 — Release Engineering

**Objective**: Prepare v0.1.0 release with proper packaging and documentation.

**Actions**:
- Updated `pyproject.toml` with author info and dev dependencies (pytest-cov, hypothesis)
- Created `CHANGELOG.md` documenting all improvements from cycles 1-7
- Created `Makefile` with test, lint, format, security, clean targets
- Created `AGENTS.md` documenting the autonomous development protocol
- Created `EVOLUTION.md` (this file) documenting all 8 cycles
- Tagged `v0.1.0`

---

## Summary

| Metric | Before | After |
|--------|--------|-------|
| Tests | 41 | 81+ |
| Coverage | 70% | 97% |
| Custom exceptions | 0 | 2 |
| CI/CD | None | GitHub Actions |
| Property tests | 0 | 12 |
| Working examples | 0 | 3 |
| Security issues | 2 | 0 |
| Edgecraft commits | 0 | 10 |
