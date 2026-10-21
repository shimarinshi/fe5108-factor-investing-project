# Part 2: security-level portfolios

Parts 2A–2D are complete for the post-class-3 assignment. Read the sections in order: data validation establishes the cleaning rules, the market portfolio supplies the benchmark, and the value portfolios are compared both on their own and relative to that benchmark.

## Report navigation

| Section | Assignment questions and results | Status |
|---|---|---|
| [2A: data cleaning and validation](data_validation/README.md) | Monthly stock counts; return distribution and winsorization; return coverage; P/B anomalies; valuation sanity check | Complete |
| [2B: broad-market portfolio](broad_market/README.md) | Market-cap score weights and monthly returns; [comparison with MSCI USA](broad_market/benchmark_comparison.md) | Complete |
| [2C: value portfolios](value_portfolios/README.md) | Three construction methods; annualized returns and volatility; final-period holdings and maximum weights | Complete |
| [2D: active returns](active_returns/README.md) | Tracking error; [strategy and HML correlations](active_returns/factor_correlations.md) | Complete |

## Common analysis conventions

- Performance covers January 1999–December 2018 (240 months), using formation scores from December 1998–November 2018 and the corresponding next-month returns. Portfolios rebalance monthly, are long-only and fully invested, and exclude transaction costs.
- Stock returns use the Part 2A monthly 1st/99th percentile winsorization. The market proxy retains all supplied stocks; baseline value portfolios exclude Pb = 0.50 stock-months. Part 2C also reports the inclusion sensitivity check.
- Supplied characteristics are percentile scores on a 0.01–1.00 scale. B/P scores are constructed as 1.01 − Pb without reranking; market-cap scores approximate size weights and are not actual capitalization. Top-20% selection includes boundary ties.
- Annualized returns use geometric compounding. Volatility and tracking error use monthly sample standard deviations times sqrt(12). Part 2D active returns subtract the Part 2B market proxy; HML is already a return spread.
- MSCI USA gross total-return levels and HML come from the shared instructor workbook. Both benchmarks are aligned on realized return month and retain their supplied values.

## Reproduce and locate results

From the repository root, use the documented Python environment and run:

```bash
python run_all.py --all
python -m unittest discover -s tests -v
```

`--all` runs input validation, the five 2A diagnostics, `market_portfolio`, `benchmark_comparison`, `value_returns`, `tracking_error`, and `factor_correlations` in dependency order. Individual `--task` commands require their upstream files to exist; each section documents its commands.

Reports, code and outputs use the same four section names: `data_validation`, `broad_market`, `value_portfolios`, and `active_returns`, under `reports/part_2/`, `src/part_2/`, and `outputs/part_2/`. Figures appear inline in the relevant reports; numerical tables are saved alongside their figures. Selected figures and tables are versioned for review. Large security-weight panels and SVG exports are generated locally.

Reuse the [shared input registry](../../data/README.md). Raw sources stay in `data/raw/`; the shared cleaned stock-return panel is generated at `data/processed/security_returns/winsorized_returns.csv`. No section carries its own raw-data copy.

[All project reports](../README.md) · [Project overview](../../README.md)
