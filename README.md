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

**Before adding data or preparing a push, read [data/README.md](data/README.md).** The shared FF/MSCI workbook, security-level CSV, 49-industry workbook and Part 4 product-innovation workbook are in `data/raw/`. Reuse them across parts; do not upload separate copies. New common data must follow the same registry process. Part-specific intermediate tables may be committed with their generating code.

## What runs today

`python run_all.py --all` verifies shared source files and reproduces all implemented analyses in dependency order. Part 2A–2D, Part 3A–3E and Parts 4 and 5 computations are integrated. Use `python run_all.py --part 5` to reproduce Part 5 tables and figures. Use `python run_all.py --part 4` to reproduce the Part 4 tables and figures. Use `python run_all.py --part 3` for Part 3 only, or `--list` to see every registered task. The [Part 3 guide](src/part_3/README.md) documents methods, task dependencies and all 18 result files; its final group-report narrative remains pending.

| Course area | Implementation status | Required inputs |
|---|---|---|
| Part 1: factor investing | Standalone handoff archive present; runner integration pending | Shared FF/MSCI workbook |
| Part 2: security-level portfolios | Parts 2A–2D implemented | Shared security CSV and FF/MSCI workbook |
| Part 3: industry portfolio optimization | 3A–3E computations integrated; final narrative pending | Existing industry workbook and shared FF/MSCI workbook |
| Part 4: product innovation | Analysis and figures integrated; [report](reports/part4/README.md) | Instructor-provided NVDA/NVDL daily total returns, February–August 2024 |
| Part 5: portfolio analytics | Numerical analysis and figures integrated; final report pending | Shared FF/MSCI workbook |

Add each new executable task to the ordered `TASKS` registry in `run_all.py`, update this table and document inputs, outputs and dependencies. `--all` must cover every integrated analysis. Never present an isolated uploaded folder as completed integration.

## Project navigation

- [Shared input data](data/README.md)
- [Reports by assignment part](reports/README.md)
- [Part 2: security-level analysis](reports/part_2/README.md)
- [Part 3: execution and methods](src/part_3/README.md)
- [Part 3: result navigation](reports/part_3/README.md)
- [Part 4: product innovation](reports/part4/README.md)

Each part owns its report, code and output subdirectories. Section-specific methods and results belong inside that part, rather than on this team-wide page. Part 2 uses matching section folders under `reports/part_2/`, `src/part_2/` and `outputs/part_2/`. All implemented analyses remain accessible through the shared `run_all.py` entry point.

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
