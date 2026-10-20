# FE5108 Factor Investing Project

Shared workspace for the Fall 2026 practitioner-segment class project. This is independent of the earlier portfolio-theory project. Repository documentation and code use English.

The assignment is released incrementally. The supplied post-class-3 handout describes Parts 1–3; future work is not invented or assigned here. No team responsibilities are prescribed.

## Quick start

Use **Python 3.12.14**, recorded in `.python-version` and used by CI. A version file does not install Python automatically.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_all.py --all
python -m unittest discover -s tests -v
```

On Windows, activate with `.venv\Scripts\Activate.ps1`. Run commands from the repository root; the runner also resolves files independently of the working directory. No API keys or network downloads are needed for the current bootstrap.

## Shared course data — already uploaded

**Before adding data or preparing a push, read [data/README.md](data/README.md).** The shared FF/MSCI workbook, security-level CSV and 49-industry workbook are already in `data/raw/`. Reuse them across parts; do not upload separate copies. New common data must follow the same registry process. Part-specific intermediate tables may be committed with their generating code.

## What runs today

`python run_all.py` and `python run_all.py --all` both validate supplied source files and write a descriptive input inventory to `outputs/input_validation/`. This is a working **bootstrap**, not completed factor analysis. `--list` reports implemented tasks. Explicit requests for unimplemented parts fail rather than silently succeeding.

| Course area | Implementation status | Required inputs |
|---|---|---|
| Part 1: factor investing | Not implemented | Shared FF/MSCI workbook uploaded; extraction and semantic checks pending |
| Part 2: security-level portfolios | Raw input registered; analysis not implemented | Supplied anonymized security CSV; shared Part 1 benchmarks |
| Part 3: industry portfolio optimization | Not implemented | Industry workbook and shared FF/MSCI workbook uploaded; extraction pending |

Add each new executable task to the ordered `TASKS` registry in `run_all.py`, update this table and document inputs, outputs and dependencies. `--all` must cover every integrated analysis. Never present an isolated uploaded folder as completed integration.

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
