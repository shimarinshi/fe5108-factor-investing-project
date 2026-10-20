# Shared analytical interfaces

These are target contracts for future modules, not claims that datasets already exist.

- Security panel: one row per `stock_id, formation_month`; retain `return_month`, raw and cleaned forward returns, standardized features and eligibility/quality flags. Months use YYYY-MM.
- Benchmark panel: one row per return `month`; descriptive decimal-return columns (e.g. `msci_usa_gross_return`, `hml_return`, `rf_return`). Keep price/index levels separate from returns.
- Portfolio weights: `strategy, formation_month, stock_id, weight`; unique keys, finite weights, documented rounding tolerance. Part 2 weights must be nonnegative and sum to one. Part 3 shorting restrictions depend on the strategy.
- Strategy returns: `strategy, month, return`; a month is always the realized RETURN month. Save coverage and treatment of missing outcomes.
- Estimation outputs: record training dates, decision dates, evaluation dates and constraints. Part 3 seed covariance ends December 2004; future observations must not leak into it.

Coordinate schema changes through a PR and update all consumers together. Give every task named inputs/outputs and deterministic parameters; seeds, solver settings and package versions belong in the run metadata when applicable. A task must fail with a useful message on missing required inputs, never silently skip to produce an apparently complete report.
