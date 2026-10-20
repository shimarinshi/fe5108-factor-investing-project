# Repository instructions

Read README.md, CONTRIBUTING.md and docs/data_contract.md before edits. Follow the same integration requirements as human contributors. Work only in this repository; do not change earlier course projects. Keep documentation and identifiers in English. Do not invent results, future assignment requirements or contributor roles. Preserve raw sources and never insert credentials. An analysis is integrated only when it is reachable from run_all.py, documented and checked. Report missing inputs and unfinished work explicitly. Do not publish or change repository visibility without user authorization.

## Mandatory shared-data check before commits and pushes

Read `data/README.md` and `data/raw/source_manifest.json` before adding data, implementing a data consumer, or preparing a commit/push. The three course datasets are ALREADY UPLOADED at the canonical paths listed there. Reuse them; do not duplicate raw files in part-specific directories. Inspect staged changes for copies, including renamed copies. Future potentially shared sources must be added once and registered in both the manifest and data registry in the same change. If intermediate tables become shared inputs, register their canonical derived path, schema and producer too.

Part-specific intermediate/result tables may be committed with their generating code and documented provenance; selective force-add is allowed for intentional deliverables in ignored output directories. Do not confuse derived tables with duplicate raw sources. Review the PR checklist before push. These rules apply to all parts and all agents, not just Part 2.

## Chart style defaults

Use these shared defaults for new charts so figures remain visually consistent across contributors and agents. These are presentation recommendations, not additional course requirements. Adapt where needed for clear multi-series comparisons or accessibility; keep color meanings consistent within a figure and across related figures.

- Use English chart titles, axis labels, legends and annotations.
- Use **DejaVu Sans** for chart text. There is no fixed font-size requirement; choose sizes that remain readable in the final report.
- Use a white background (`#FFFFFF`).
- Use teal-blue (`#246B83`) for the primary data series.
- Use muted red (`#BD503B`) for selected highlights or unusual observations; do not imply an observation is erroneous solely by coloring it red.
- Use dark blue-gray (`#213444`) for titles and axis labels, slate-gray (`#546471`) for secondary text and tick labels, and gray (`#65727C`) for source notes.
- Use light gray (`#DFE5E9`) for subtle gridlines. Optional area shading may use the primary series color at about 7% opacity.
- Avoid decorative borders and unnecessary visual clutter. For additional series, use clearly distinguishable colors and line styles rather than reusing the highlight color indiscriminately.

For Matplotlib, set `font.family` to `DejaVu Sans` and pass the hex colors above explicitly. No particular plotting library or fixed figure dimensions are required.

## Assignment hierarchy

Keep the team-wide README concise: shared setup, part-level status and navigation only. Organize each contribution by assignment part, then section, using descriptive section names. Part 2A lives under `reports/part_2/data_validation/`, `src/part_2/data_validation/` and `outputs/part_2/data_validation/`. The part and report-section directories have README entry pages. Do not flatten individual analyses into shared top-level directories or create contributor-named silos. Later sections belong alongside data_validation; do not scaffold unimplemented sections just to fill the tree. Shared raw data and genuinely shared derived datasets keep their registered canonical paths. Keep all tasks integrated through run_all.py and render figures inline in section reports.
