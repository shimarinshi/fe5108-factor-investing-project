# Shared analytical interfaces

These are target contracts for future modules, not claims that datasets already exist.

- Security panel: one row per `stock_id, formation_month`; retain `return_month`, raw and cleaned forward returns, standardized features and eligibility/quality flags. Months use YYYY-MM.
- Benchmark panel: one row per return `month`; descriptive decimal-return columns (e.g. `msci_usa_gross_return`, `hml_return`, `rf_return`). Keep price/index levels separate from returns.
- Portfolio weights: `strategy, formation_month, stock_id, weight`; unique keys, finite weights, documented rounding tolerance. Part 2 weights must be nonnegative and sum to one. Part 3 shorting restrictions depend on the strategy.
- Strategy returns: `strategy, month, return`; a month is always the realized RETURN month. Save coverage and treatment of missing outcomes.
- Estimation outputs: record training dates, decision dates, evaluation dates and constraints. Part 3 seed covariance ends December 2004; future observations must not leak into it.

Coordinate schema changes through a PR and update all consumers together. Give every task named inputs/outputs and deterministic parameters; seeds, solver settings and package versions belong in the run metadata when applicable. A task must fail with a useful message on missing required inputs, never silently skip to produce an apparently complete report.

## Implemented Part 3 interfaces

Every section exposes `run(root)` and is registered in dependency order in `run_all.py`. `--part 3` includes raw-source validation. Individual tasks require their documented upstream result files; no notebook memory is used.

- Industry inputs: a 343-by-49 DataFrame, monthly PeriodIndex named `month`, stripped industry abbreviations as columns, decimal returns. These are contemporaneous returns, not Part 2 forward-return fields. The 2004 estimate only uses January 1995–December 2004; the updated estimate only uses January 2006–December 2015.
- `portfolio_optimization/industry_weights_2004.csv`: `industry` plus `min_var_short`, `min_var_long_only`, `inverse_volatility`. The wide form preserves the existing notebook/report interface. There is no `Total` row in the reusable CSV. Formation date is `2004-12-31` in metadata. Industry labels are not anonymized `stock_id` values.
- Strategy-return CSVs: `month` plus one decimal-return column per named strategy. In-sample months are 1995-01–2004-12; out-of-sample months are 2005-01–2023-07. These part-specific wide tables are not new shared datasets.
- `reoptimization/long_only_weights_2004_vs_2015.csv`: `industry`, `original_2004`, `updated_2015`. The corresponding 91-row return table uses `month` and the same two strategy columns for 2016-01–2023-07.
- `performance_expectations/strategy_and_benchmark_returns.csv`: `month`, `min_var_2004`, `msci_usa`. Both are total returns, not factor spreads. The 224-row wealth table starts at 1 in 2004-12 and compounds 223 returns. It is not a return table.
- Columns ending in `_percentage_points` contain 100 times a difference between decimal measures. All other returns, weights and volatility remain decimals. Crisis ranking tables contain `crisis`, `rank`, `industry`, `cumulative_return`.

See [the Part 3 guide](../src/part_3/README.md) for the full file inventory and assumptions. These outputs remain part-specific; if promoted to shared inputs later, register a canonical derived path and producer in `data/README.md`.
