# FE5108 Factor Investing Project

Shared workspace for the Fall 2026 practitioner-segment class project. This is independent of the earlier portfolio-theory project. Repository documentation and code use English.

Reports and results for Parts 1–5 are available below. The retained assignment handout covers Parts 1–3; later question sheets are not yet archived in this repository.

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

**Before adding data or preparing a push, read [data/README.md](data/README.md).** The shared FF/MSCI workbook, security-level CSV, 49-industry workbook and Part 4 product-innovation workbook are in `data/raw/`. Reuse them across parts; do not upload separate copies. New common data must follow the same registry process. Part-specific intermediate tables may be committed with their generating code.

## Reports and reproduction

| Part | Report | Reproduction |
|---|---|---|
| 1: factor investing | [Part 1](reports/part_1/README.md) | Standalone delivery archive; not in the shared runner |
| 2: security-level portfolios | [Part 2A–2D](reports/part_2/README.md) | `python run_all.py --part 2` |
| 3: industry portfolio optimization | [Part 3A–3E](reports/part_3/README.md) | `python run_all.py --part 3` |
| 4: product innovation | [Part 4](reports/part4/README.md) | `python run_all.py --part 4` |
| 5: portfolio analytics | [Part 5](reports/part5/README.md) | `python run_all.py --part 5` |

`python run_all.py --all` verifies the shared sources and reproduces integrated Parts 2–5 in dependency order. Use `--list` to see registered tasks. Part 1's original scripts and supplementary tables remain in its delivery archive; `--all` does not rerun them.

Each part owns its report, code and output directories. Existing names (`part_2`, `part_3`, `part4`, `part5`) are retained so teammates' scripts and links continue to work. See the [report index](reports/README.md), [output index](outputs/README.md) and [Part 3 execution guide](src/part_3/README.md).

## Reading results across parts

| Analysis | Return sample | Main reporting convention |
|---|---|---|
| Part 1 MSCI comparisons and Part 5 | January 1995–July 2023 | Arithmetic annualized mean; Part 1 also gives CAGR |
| Part 2 portfolio performance | January 1999–December 2018 | Geometric annualized return (CAGR) |
| Part 3 | Estimation and evaluation windows vary by question | Monthly sample volatility × √12 |
| Part 4 | February 1–August 30, 2024 | Daily total returns, daily risk and compounded holding-period returns |

Part 1's historical factor tests use longer samples specified in its report. Different windows and return averages are intentional: compare strategies within the same question before comparing headline results across parts.

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
