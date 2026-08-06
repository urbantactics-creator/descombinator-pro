# ADR-006: Benchmark Regression Gate

- **Status:** Accepted
- **Date:** 2026-08-02
- **Deciders:** Performance Engineer, DevOps Engineer

## Context

As the application evolves, performance regressions can be introduced silently. We need an automated way to detect and prevent performance regressions in CI.

## Decision

We implement a **benchmark regression gate** using `pytest-benchmark` and a custom regression checker:

- `benchmarks/` package with 16 non-slow gates + slow real-separation benchmarks
- `benchmarks/baselines.json` — committed baseline medians from CI
- `scripts/bench/check_regressions.py` — fails on > 20% median regression or missed absolute target
- CI `benchmark` job runs after `lint-and-test` job

### Rationale

- **Reproducible:** Benchmarks use synthetic data and mock pipelines
- **Automated:** Runs in CI on every PR
- **Configurable:** 20% threshold and absolute targets are configurable
- **Visible:** Results uploaded as CI artifacts

## Consequences

### Positive

- Catches performance regressions before merge
- Provides performance baselines for future optimization
- Documents performance targets in code

### Negative

- Adds CI time (benchmarks run on every PR)
- Requires baseline maintenance when intentional optimizations are made

## Alternatives Considered

- **Manual benchmarking:** Rejected — not automated, easy to forget
- **External tools (e.g., asv):** Rejected — adds external dependency, more complex setup
- **No regression gate:** Rejected — performance would degrade over time
