# Generated outputs

Outputs follow the assignment hierarchy. Use the report links for methods, interpretation and inline figures.

| Output directory | Contents | Report |
|---|---|---|
| `part_1/figures/` | Part 1 report figures | [Part 1](../reports/part_1/README.md) |
| `input_validation/` | Shared source-integrity and schema checks | [Data registry](../data/README.md) |
| `part_2/data_validation/` | Five 2A diagnostics, organized by analysis | [Part 2A](../reports/part_2/data_validation/README.md) |
| `part_2/broad_market/` | Market returns, allocation tables and MSCI comparison | [Part 2B](../reports/part_2/broad_market/README.md) |
| `part_2/value_portfolios/` | Value returns, cumulative growth, risk and final holdings | [Part 2C](../reports/part_2/value_portfolios/README.md) |
| `part_2/active_returns/` | Monthly active returns, tracking error and aligned HML correlations | [Part 2D](../reports/part_2/active_returns/README.md) |
| `part_3/` | Industry allocations, in/out-of-sample risk, reoptimization and crisis comparisons | [Part 3](../reports/part_3/README.md) |
| `part4/` | NVDA/NVDL daily risk, leverage regression and compounded returns | [Part 4](../reports/part4/README.md) |
| `part5/` | Factor replication, active performance and risk decomposition | [Part 5](../reports/part5/README.md) |

Run `python run_all.py --all` to regenerate integrated Part 2–5 outputs. Selected PNGs and numerical tables are versioned with their producers; large stock-weight tables, SVGs and temporary files remain ignored. Raw sources belong in `data/raw/`, shared cleaned data in its registered `data/processed/` location, and reusable code in `src/`.

Part 1 tables are directly available in [part_1/tables/](part_1/tables/). Regenerate Part 1 separately with `python src/part_1/build_part1.py`. The [final report](../reports/final_report/FE5108_Final_Project_Report.pdf) is maintained as an authored submission under `reports/`.
