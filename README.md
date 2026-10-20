# FE5108 Factor Investing Project

Shared workspace for the Fall 2026 practitioner-segment class project. This is independent of the earlier portfolio-theory project. Repository documentation and code use English.

The assignment is released incrementally. The supplied post-class-3 handout describes Parts 1–3; future work is not invented or assigned here. No team responsibilities are prescribed.

## Quick start

Use **Python 3.12.14**, recorded in `.python-version` and used by CI. A version file does not install Python automatically.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
python run_all.py --all
python -m unittest discover -s tests -v
```

On Windows, activate with `.venv\Scripts\Activate.ps1`. Run commands from the repository root; the runner also resolves files independently of the working directory. After dependency installation, the integrated analysis runs offline without API keys.

## Shared course data — already uploaded

**Before adding data or preparing a push, read [data/README.md](data/README.md).** The shared FF/MSCI workbook, security-level CSV and 49-industry workbook are already in `data/raw/`. Reuse them across parts; do not upload separate copies. New common data must follow the same registry process. Part-specific intermediate tables may be committed with their generating code.

## What runs today

`python run_all.py` and `python run_all.py --all` validate supplied source files, write a descriptive input inventory to `outputs/input_validation/`, and generate the five Part 2A diagnostics and monthly winsorized returns. `--list` reports implemented tasks. Explicit requests for unimplemented tasks fail rather than silently succeeding.

| Course area | Implementation status | Required inputs |
|---|---|---|
| Part 1: factor investing | Not implemented | Shared FF/MSCI workbook uploaded; extraction and semantic checks pending |
| Part 2: security-level portfolios | Part 2A implemented; Parts 2B–2D pending | Supplied anonymized security CSV; shared Part 1 benchmarks |
| Part 3: industry portfolio optimization | Not implemented | Industry workbook and shared FF/MSCI workbook uploaded; extraction pending |

Add each new executable task to the ordered `TASKS` registry in `run_all.py`, update this table and document inputs, outputs and dependencies. `--all` must cover every integrated analysis. Never present an isolated uploaded folder as completed integration.

## Part 2A: data cleaning and validation

Use the existing `data/raw/security_characteristics.csv`; all checks cover the full supplied history (November 1998–March 2019 formation months). Run `python run_all.py --all` for all integrated tasks, or `python run_all.py --task <task>` for one row below.

| Assignment bullet | Method | Task / results directory under `outputs/` | Report |
|---|---|---|---|
| 1. Monthly stock counts | Count distinct stock IDs each month; highlight the two largest declines. | `monthly_stock_coverage` | [Stock coverage](reports/monthly_stock_coverage.md) |
| 2. Return distribution and winsorization | Plot raw returns with a central-range view and a full-range log-frequency view; cap returns at each month's P1/P99 using linear-interpolated quantiles. | `return_distribution` | [Returns](reports/return_distribution.md) |
| 3. Return coverage | Divide nonmissing raw returns by recorded stocks in each month; zero returns are valid. | `return_coverage` | [Return coverage](reports/return_coverage.md) |
| 4. Standardized P/B distribution | Plot score frequencies; compare low Bv shares for Pb = 0.50 versus other records. Baseline value portfolios will exclude the affected stock-months, with inclusion as a robustness check. | `price_to_book_distribution` | [P/B diagnostic](reports/price_to_book_distribution.md) |
| 5. P/B ratio sanity check | Within each month, hold one score approximately constant in ten rank bands; compute Spearman correlations between the other two and summarize the group medians. Compare excluding Pb = 0.50 with including it. | `valuation_sanity_check` | [Sanity check](reports/valuation_sanity_check.md) |

Each results directory contains a PNG figure and its underlying CSV tables. PNGs and small tables are versioned for teammate review; SVGs are regenerated locally. Shared cleaned returns are generated at `data/processed/security_returns/winsorized_returns.csv`, with raw returns, winsorized returns, both month labels and an adjustment flag. They are not duplicated in Git; regenerate them with `return_distribution`. Subsequent portfolio calculations will use the winsorized returns. Portfolio construction and its robustness comparison remain Part 2B–2D work.

Dependencies are pinned in `requirements.lock`. Regenerate the lock with `uv pip compile requirements.txt --python-version 3.12 --output-file requirements.lock`.

## Layout


- `inputs/`: unchanged course handout snapshots; retain earlier releases.
- `data/raw/`: unchanged supplied observations and source manifest.
- `data/processed/`: generated shared datasets, with documented schemas.
- `src/`: reusable validation and analysis modules.
- `tests/`: targeted tests for data contracts and numerical behavior.
- `outputs/`: reproducible generated tables, figures and validation summaries.
- `reports/`: authored narrative and final report.
- `docs/`: scope, data semantics and shared interface contracts.
- `run_all.py`: single integrated execution entry point.

## Collaboration

Read [CONTRIBUTING.md](CONTRIBUTING.md), [data contract](docs/data_contract.md), [shared interfaces](docs/interfaces.md), and [scope](docs/scope.md) before contributing. PRs run CI on Python 3.12.14; CI configuration alone is not a claim that branch protection is enabled.

Use a short-lived branch and a pull request. Keep raw inputs unchanged, preserve source attribution, and update code, runner, documentation, checks and affected results together. Do not commit credentials, local absolute paths, virtual environments or generated temporary files. This private teaching repository does not grant redistribution rights over course/provider materials.
