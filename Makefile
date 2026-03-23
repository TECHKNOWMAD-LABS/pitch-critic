.PHONY: test lint format security clean

test:
	uv run pytest -v --tb=short --cov=pitchcritic --cov-report=term-missing

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

security:
	@echo "Scanning for hardcoded secrets..."
	@grep -rn "api_key\s*=\s*[\"'][^\"']*[\"']" src/ tests/ && echo "FOUND HARDCODED KEYS" && exit 1 || echo "No hardcoded secrets found."
	@echo "Scanning for dangerous functions..."
	@grep -rn "os\.system\|subprocess\.call\|eval(\|exec(" src/ && echo "FOUND DANGEROUS CALLS" && exit 1 || echo "No dangerous function calls found."
	@echo "Security scan passed."

clean:
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
