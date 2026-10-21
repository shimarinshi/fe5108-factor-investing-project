# Generated outputs

Outputs follow the assignment hierarchy. Use the report links for methods, interpretation and inline figures.

| Output directory | Contents | Report |
|---|---|---|
| `input_validation/` | Shared source-integrity and schema checks | [Data registry](../data/README.md) |
| `part_2/data_validation/` | Five 2A diagnostics, organized by analysis | [Part 2A](../reports/part_2/data_validation/README.md) |
| `part_2/broad_market/` | Market returns, allocation tables and MSCI comparison | [Part 2B](../reports/part_2/broad_market/README.md) |
| `part_2/value_portfolios/` | Value returns, cumulative growth, risk and final holdings | [Part 2C](../reports/part_2/value_portfolios/README.md) |
| `part_2/active_returns/` | Monthly active returns, tracking error and aligned HML correlations | [Part 2D](../reports/part_2/active_returns/README.md) |

Run `python run_all.py --all` to regenerate implemented outputs. Selected PNGs and numerical tables are versioned with their producers; large stock-weight tables, SVGs and temporary files remain ignored. Raw sources belong in `data/raw/`, shared cleaned data in its registered `data/processed/` location, and reusable code in `src/`.
