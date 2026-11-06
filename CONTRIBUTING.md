# Contribution rules

## Naming and layout

Use descriptive English `lower_snake_case` for Python modules, CSV files and analytical directories: `value_portfolio_returns.csv`, `industry_minimum_variance.py`. Use `kebab-case` branch names under `feature/`, `fix/` or `docs/`. Standard entry names such as `README.md`, `CONTRIBUTING.md`, `AGENTS.md` and `.github/` are deliberate exceptions.

Do not name analytical files `exhibit_2`, `question_3`, `final_final` or after a contributor. Map course question numbers to descriptive outputs in README/report text. Course handout snapshots include their release label, e.g. `class_project_post_class_3.pdf`; retain the original filename in the source manifest. Use ISO dates, UTF-8, repository-relative paths, and `pathlib` rather than workstation-specific paths. Preserve original raw CSV column names; normalize names only in derived datasets with an explicit mapping.

## Runtime and dependencies

Python 3.12.14 is the reproducibility baseline. Any version change updates `.python-version`, CI and README in the same PR. Pin all introduced runtime packages exactly in `requirements.txt`; for transitive dependencies add a reproducible lock when numerical dependencies arrive. Runtime dependencies are recorded in requirements.txt and requirements.lock. Test a clean virtual environment, not just a notebook kernel. Avoid unused dependencies.

## Integration and submission

1. Create a short-lived branch from current main; keep work scoped to the stated task.
2. Put reusable logic in `src/`. Notebooks may explain an analysis but cannot be its only executable implementation.
3. Register new tasks in `run_all.py` in dependency order. Shared inputs must be built before their consumers. Do not duplicate a second private pipeline per person.
4. Update root README status, commands and output locations for changed behavior. Review README and runner on every PR; documentation-only changes need not create meaningless code edits.
5. Record source, units, timing, sample filters, estimation windows, missing-data policy and formulas. Save tables underlying charts; label axes and provide source, period and universe in captions.
6. Run `python run_all.py --all`, relevant tests, and `git diff --check` before declaring code ready. A failed or missing task is reported explicitly. Pure documentation changes require link/content review and whitespace checks, not rerunning unrelated analysis.
7. Submit a PR describing what changed, the exact verification commands, and remaining limitations. Request teammate review before merging. Do not overwrite another contributor's work or force-push main.

Generated outputs are ignored by default. If an output is needed for review or submission, selectively version it and its generating code together; document why and how to reproduce it. Do not manually edit computed tables. Regenerate affected outputs after changes and remove stale outputs from the documented result set.

## Changes to the assignment

Add each new handout as a separate snapshot and register its provenance. Update scope and README for newly released work. Do not invent future requirements, split responsibilities, or mark unfinished sections complete. Document methodological choices before comparing performance; never choose cleaning thresholds solely for better backtest results.

## Shared data: mandatory pre-push review

Read [the shared data registry](data/README.md) and its source manifest before every data-related change and before preparing a push. All four instructor datasets are already uploaded. Reuse canonical paths; do not upload renamed copies or put source files in personal/part-specific folders. New potentially shared source data must be registered once in `data/raw/`, the manifest and registry together. Shared derived tables need a canonical `data/processed/` path, schema and producer registration. Part-specific intermediate tables can be committed with their generating code; selectively force-add intended artifacts where ignored, never entire temporary output trees. Check staged files for duplicate content before push.
