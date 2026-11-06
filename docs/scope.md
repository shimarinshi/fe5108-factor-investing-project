# Delivered scope and remaining integration limits

Reports and results are available for Parts 1–5. The [complete assignment](../inputs/class_project_in_full.pdf) was received on November 6, 2026; the earlier post-class-3 handout is retained. The [final report](../reports/final_report/FE5108_Final_Project_Report.pdf) includes eight pages of main text, References and the exhibits/code appendix.

| Part | Delivered scope | Execution |
|---|---|---|
| 1 | Factor-premium tests, MSCI methodology discussion, diversification, construction comparisons and volatility sensitivity | Standalone script; readable report, tables and figures |
| 2 | 2A data diagnostics, 2B market proxy, 2C value portfolios and 2D active-return analysis | Shared runner |
| 3 | 3A optimization, 3B in-sample risk, 3C out-of-sample risk, 3D reoptimization and 3E crisis comparisons | Shared runner |
| 4 | NVDA/NVDL daily risk, leverage regression, compounding and product discussion | Shared runner |
| 5 | Value replication, multi-factor active performance and risk decomposition | Shared runner |

Part 1 runs separately with `python src/part_1/build_part1.py`; its tables are directly available under `outputs/part_1/tables/`. `run_all.py --all` runs Parts 2–5. The final PDF is the submission copy; part-level pages retain the supporting detail.

Part 2 uses monthly P1/P99 winsorized returns. Its broad-market proxy retains Pb = 0.50 observations; value portfolios exclude them in the baseline and include them in a sensitivity comparison. The P/B concentration does not establish negative book equity. Source workbooks and CSVs remain unchanged.

Part 4 uses instructor-supplied daily total returns. The report distinguishes estimated leverage drag from the stated management fee and notes that the historical factsheet has not been independently checked. See each part's report for assumptions, sample windows and limitations.
