# Delivered scope and remaining integration limits

Reports and results are available for Parts 1–5. The archived post-class-3 handout covers Parts 1–3. Later question sheets have not been added, so repository checks cannot establish complete compliance with the original Part 4–5 wording.

| Part | Delivered scope | Execution |
|---|---|---|
| 1 | Factor-premium tests, MSCI methodology discussion, diversification, construction comparisons and volatility sensitivity | Standalone archive; readable report and figures exposed separately |
| 2 | 2A data diagnostics, 2B market proxy, 2C value portfolios and 2D active-return analysis | Shared runner |
| 3 | 3A optimization, 3B in-sample risk, 3C out-of-sample risk, 3D reoptimization and 3E crisis comparisons | Shared runner |
| 4 | NVDA/NVDL daily risk, leverage regression, compounding and product discussion | Shared runner |
| 5 | Value replication, multi-factor active performance and risk decomposition | Shared runner |

Part 1 is not integrated into `run_all.py`; its archive retains the original standalone scripts and supplementary tables. Readable reports do not imply shared-runner integration. The final combined submission is separate from these part-level reports.

Part 2 uses monthly P1/P99 winsorized returns. Its broad-market proxy retains Pb = 0.50 observations; value portfolios exclude them in the baseline and include them in a sensitivity comparison. The P/B concentration does not establish negative book equity. Source workbooks and CSVs remain unchanged.

Part 4 uses instructor-supplied daily total returns. The report distinguishes estimated leverage drag from the stated management fee and notes that the historical factsheet has not been independently checked. See each part's report for assumptions, sample windows and limitations.
