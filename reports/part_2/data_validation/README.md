# Part 2A: data cleaning and validation

Use the existing `data/raw/security_characteristics.csv`; all checks cover the full supplied history (November 1998–March 2019 formation months). Run `python run_all.py --all` for all integrated tasks, or `python run_all.py --task <task>` for one row below.

| Assignment bullet | Method | Task / results directory under `outputs/part_2/data_validation/` | Report |
|---|---|---|---|
| 1. Monthly stock counts | Count distinct stock IDs each month; highlight the two largest declines. | `monthly_stock_coverage` | [Stock coverage](monthly_stock_coverage.md) |
| 2. Return distribution and winsorization | Plot raw returns with a central-range view and a full-range log-frequency view; cap returns at each month's P1/P99 using linear-interpolated quantiles. | `return_distribution` | [Returns](return_distribution.md) |
| 3. Return coverage | Divide nonmissing raw returns by recorded stocks in each month; zero returns are valid. | `return_coverage` | [Return coverage](return_coverage.md) |
| 4. Standardized P/B distribution | Plot score frequencies; compare low Bv shares for Pb = 0.50 versus other records. Baseline value portfolios will exclude the affected stock-months, with inclusion as a robustness check. | `price_to_book_distribution` | [P/B diagnostic](price_to_book_distribution.md) |
| 5. P/B ratio sanity check | Within each month, hold one score approximately constant in ten rank bands; compute Spearman correlations between the other two and summarize the group medians. Compare excluding Pb = 0.50 with including it. | `valuation_sanity_check` | [Sanity check](valuation_sanity_check.md) |

Each results directory contains a PNG figure and its underlying CSV tables. PNGs and small tables are versioned for teammate review; SVGs are regenerated locally. Shared cleaned returns are generated at `data/processed/security_returns/winsorized_returns.csv`, with raw returns, winsorized returns, both month labels and an adjustment flag. They are not duplicated in Git; regenerate them with `return_distribution`. Subsequent portfolio calculations will use the winsorized returns. Portfolio construction and its robustness comparison remain Part 2B–2D work.

Dependencies are pinned in `requirements.lock`. Regenerate the lock with `uv pip compile requirements.txt --python-version 3.12 --output-file requirements.lock`.


[Back to Part 2](../README.md)
