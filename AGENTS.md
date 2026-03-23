# AGENTS.md — Autonomous Development Protocol

## Overview

This repository was developed using the **Edgecraft Protocol**, an autonomous iterative development system by TechKnowMad Labs. The protocol executes 8 structured cycles (L0-L7 layers) to systematically harden a codebase from initial scaffold to production-ready release.

## Protocol Layers

| Layer | Name | Purpose |
|-------|------|---------|
| L0 | Attention | Identify what needs focus |
| L1 | Detection | Discover untested, unprotected, or underperforming code |
| L2 | Noise | Security scan — separate real findings from false positives |
| L3 | Sub-noise | Find hidden failure modes (edge cases, malformed inputs) |
| L4 | Conjecture | Form hypotheses about performance improvements |
| L5 | Action | Implement fixes, tests, and improvements |
| L6 | Grounding | Measure and verify with concrete numbers |
| L7 | Flywheel | Identify patterns applicable to other repositories |

## Cycle Structure

Each cycle is a complete L0-L7 pass focused on one quality dimension:

1. **Test Coverage** — Identify untested modules, write comprehensive tests
2. **Error Hardening** — Break the code with adversarial inputs, add validation
3. **Performance** — Find bottlenecks, add caching, measure improvements
4. **Security** — Scan for secrets, injection vectors, path traversal
5. **CI/CD** — Automated testing and linting on every push
6. **Property-Based Testing** — Verify invariants with generated inputs
7. **Examples + Docs** — Working examples and complete docstrings
8. **Release Engineering** — Versioning, changelog, build tooling

## Commit Convention

Every commit message starts with an Edgecraft layer prefix:

```
L1/detection: identify untested modules at 0% coverage
L3/sub-noise: empty input causes crash in extractor
L5/action: add input validation and error handling
L6/grounding: 81 tests passing, coverage at 97%
```

## Execution Model

- **Fully autonomous** — no human intervention during cycles
- **Test-driven** — all changes verified by running test suite
- **Continuous integration** — push after each cycle
- **Fail-forward** — if a command fails, log and continue
- **Meaningful commits only** — no empty or whitespace-only commits

## Agent Configuration

- **Model**: Claude Opus 4.6
- **Organization**: TECHKNOWMAD-LABS
- **Git Identity**: TechKnowMad Labs <admin@techknowmad.ai>
- **Language**: Python 3.12
- **Test Framework**: pytest + hypothesis
- **Linter**: ruff
