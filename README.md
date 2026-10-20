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

## Project navigation

- [Shared input data](data/README.md)
- [Reports by assignment part](reports/README.md)
- [Part 2: security-level analysis](reports/part_2/README.md)

Each part owns its report, code and output subdirectories. Section-specific methods and results belong inside that part, rather than on this team-wide page. Part 2A uses `reports/part_2/data_validation/`, `src/part_2/data_validation/` and `outputs/part_2/data_validation/`. All implemented analyses remain accessible through the shared `run_all.py` entry point.

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
