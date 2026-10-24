# Released scope and open decisions

The retained post-class-3 handout releases Parts 1–3. No later requirements or team roles are inferred.

Part 2A now covers all five bullets: monthly stock counts, raw-return distributions and monthly P1/P99 winsorization, return coverage, standardized P/B concentration, and rank-based valuation sanity checks. Raw shared sources are unchanged. Code is registered in run_all.py; figures, tables and English report sections document the methods and findings.

For subsequent value portfolios, exclude Pb = 0.50 stock-months in the baseline and include them in a robustness comparison. This does not establish negative book equity. Part 2B is implemented: monthly market-cap-score weights, winsorized forward returns, and an aligned MSCI USA gross USD comparison for 1999–2018. Pb = 0.50 stocks remain in this broad-market proxy. Part 2C annualized returns, volatility and final-period holdings comparisons are implemented, including a Pb = 0.50 inclusion sensitivity check. Part 2D tracking error and active-return/HML correlations are implemented.

Part 1 has a standalone handoff archive but is not registered in the shared runner. Part 3 computations for 3A–3E are integrated via five `run(root)` tasks and `--part 3`. The original notebook is retained; the module-backed notebook is the reproducible front end. Part 3's final report narrative is intentionally deferred. The implementation preserves the original notebook's 13 numerical result tables and adds deterministic presentation output, dependency declarations, task documentation and regression checks. No later assignment parts are inferred.
