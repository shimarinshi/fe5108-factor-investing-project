# Part 5: portfolio analytics

Part 5 uses the instructor-provided FF/MSCI workbook at `data/raw/ff_msci_shared.xlsx`. The sample is January 1995–July 2023 (343 months), with December 1994 index levels retained to calculate the first return. MSCI levels are gross USD; French factor percentages are divided by 100. The multifactor return is the monthly average of the four MSCI factor index returns.

From the repository root, use `python run_all.py --part 5`; `--all` also runs both tasks after the earlier parts. The runner validates shared inputs, runs `part5_analysis`, then `part5_figures`. For an individual plotting task, the analysis CSVs must already exist.

Results under `outputs/part5/` include the aligned monthly panel, factor regression, replication metrics, active-performance and risk-decomposition tables, per-component active metrics, diagnostics and five figures. Annualized arithmetic returns are 12 times monthly mean; volatility and tracking error are sample monthly standard deviation times sqrt(12). The replication is fitted and evaluated on the same sample and excludes costs. See the script for the exact input checks and formulas.

`tests/test_part5_integration.py` regenerates the outputs in a temporary directory, compares numerical CSVs with committed references using tolerance, checks images and verifies task isolation. Part 5's final narrative report is not yet in the repository.
