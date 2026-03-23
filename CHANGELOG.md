# Changelog

## [0.1.0] — 2026-03-23

### Added
- **Test Coverage (Cycle 1)**: Comprehensive test suites for `llm.py` and `app.py` CLI module, bringing coverage from 70% to 97% (55 → 81 tests).
- **Error Hardening (Cycle 2)**: Input validation across all modules — `ExtractionError` and `CritiqueError` custom exceptions, file size/type/emptiness checks, LLM response validation, score clamping, and structured API error responses (400/422/502).
- **Performance (Cycle 3)**: Content-hash caching for PDF extraction and LLM responses (SHA-256 keyed), configurable timeout on API calls (default 120s).
- **Security (Cycle 4)**: Filename path traversal sanitization, `.gitignore` for secret protection (.env, .pem, .key files excluded).
- **CI/CD (Cycle 5)**: GitHub Actions workflow (uv sync, ruff check, pytest with coverage, format check), pre-commit hooks (ruff + mypy).
- **Property-Based Testing (Cycle 6)**: 12 Hypothesis property tests covering scorer invariants, JSON parse roundtrips, and critique pipeline with random unicode input (~1000 generated examples).
- **Examples (Cycle 7)**: Three executable example scripts — mock analysis, score comparison, and PDF extraction demo.
- **Release Engineering (Cycle 8)**: Makefile with standard targets, AGENTS.md, EVOLUTION.md, CHANGELOG.md.

### Fixed
- Empty/corrupt/oversized PDF inputs now raise clear errors instead of crashing
- LLM API failures wrapped in `CritiqueError` with descriptive messages
- Scores from LLM responses clamped to valid 0-10 range
- Upload filename stripped of path components to prevent directory traversal
