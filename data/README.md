# Shared data registry — read before adding or uploading data

**All four supplied course datasets are already committed. Every part should reuse these canonical files; do not upload another copy under a part, notebook, contributor or output folder.** The original filenames and exact-byte SHA-256 hashes are recorded in [the source manifest](raw/source_manifest.json). File labels identify their source, not exclusive ownership by a part.

| Canonical path (from repository root) | Contents | Availability |
|---|---|---|
| `data/raw/ff_msci_shared.xlsx` | FF beta-sorted portfolios, momentum-sorted portfolios, three-factor returns, and MSCI factor total-return index sheets; source labeled parts 1 and 5 | Uploaded; shared by all analyses that need these series |
| `data/raw/security_characteristics.csv` | Anonymized security-level characteristics and forward monthly returns; source labeled part 2 | Uploaded previously; reused without a second copy |
| `data/raw/product_innovation.xlsx` | NVDA and NVDL daily total returns; source labeled part 4 (product innovation) | Uploaded; shared original workbook |
| `data/raw/industry_portfolios.xlsx` | `49_Industry_Portfolios` worksheet; source labeled part 3 | Uploaded; shared by all analyses that need industry returns |

Workbook bytes and sheet names are unchanged. These are source files, not standardized analysis tables. Check headers, units, missing sentinels, dates and value/equal weighting before extracting a sheet; a matching file hash is not economic validation. Parts 1 and 5 both use the shared FF/MSCI workbook; their analysis windows and methods are documented in their reports.

## Part 4 workbook inventory

`product_innovation.xlsx` preserves the instructor file byte-for-byte, including sheet `NVDL`. Row 3 labels the series "daily total returns"; row 5 identifies columns B/C as NVDA/NVDL, with dates in column A. There are 147 dated observations from February 1 to August 30, 2024, in descending date order. Returns are stored as decimal fractions (0.01 = 1%). Trailing blank/formatted rows are not observations. Reuse the supplied total returns directly; do not calculate percentage changes of these return fields. The [Part 4 report](../reports/part4/README.md) documents the implemented analysis. The provider's underlying return construction has not been independently verified.

## Before every data-related commit or push

1. Read this registry and `data/raw/source_manifest.json`; inspect the staged changes for duplicate source data.
2. Reuse an existing canonical path if the requested data are already present. Do not copy raw workbooks or CSVs into your own part's directory.
3. For new potentially shared source data, put one copy in `data/raw/`, add its source/original name/date/hash to the manifest and describe its canonical path, contents, units/timing where known, and intended uses here. Update consumers and root README as needed.
4. A revised source is a new explicitly named version with a documented reason; do not silently overwrite an existing source. Compare content hashes to detect renamed duplicates.
5. Run `python run_all.py --all` to check registered source integrity before pushing.

## Intermediate and result tables

Part-specific intermediate tables and results may be committed under descriptive analysis directories such as `outputs/part_2/value_portfolios/`, together with the generating code and documented input/output paths. These directories are ignored by default: selectively add intended deliverables with `git add -f <specific-file>`, not an entire output tree. Raw-data copies are not intermediate products.

If a derived table becomes useful to multiple parts, promote it to a documented shared path under `data/processed/`, specify its schema and generating task, and register it here under shared derived datasets. Reuse that path instead of maintaining separate competing versions.

## Shared derived datasets

- `data/processed/security_returns/winsorized_returns.csv`: produced by `return_distribution` in `run_all.py` from the canonical security CSV. One row per `stock_id, formation_month`; columns: `stock_id`, `formation_month`, `return_month` (YYYY-MM), `raw_return`, `winsorized_return` (decimal returns), `was_winsorized` (boolean). No rows dropped. Raw returns are retained; monthly P1/P99 caps use linear interpolation. Available for subsequent Part 2 portfolio tasks. Missing returns remain blank.
