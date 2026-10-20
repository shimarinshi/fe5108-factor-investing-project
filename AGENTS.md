# Repository instructions

Read README.md, CONTRIBUTING.md and docs/data_contract.md before edits. Follow the same integration requirements as human contributors. Work only in this repository; do not change earlier course projects. Keep documentation and identifiers in English. Do not invent results, future assignment requirements or contributor roles. Preserve raw sources and never insert credentials. An analysis is integrated only when it is reachable from run_all.py, documented and checked. Report missing inputs and unfinished work explicitly. Do not publish or change repository visibility without user authorization.

## Mandatory shared-data check before commits and pushes

Read `data/README.md` and `data/raw/source_manifest.json` before adding data, implementing a data consumer, or preparing a commit/push. The three course datasets are ALREADY UPLOADED at the canonical paths listed there. Reuse them; do not duplicate raw files in part-specific directories. Inspect staged changes for copies, including renamed copies. Future potentially shared sources must be added once and registered in both the manifest and data registry in the same change. If intermediate tables become shared inputs, register their canonical derived path, schema and producer too.

Part-specific intermediate/result tables may be committed with their generating code and documented provenance; selective force-add is allowed for intentional deliverables in ignored output directories. Do not confuse derived tables with duplicate raw sources. Review the PR checklist before push. These rules apply to all parts and all agents, not just Part 2.
