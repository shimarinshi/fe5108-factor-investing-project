# Return distribution and winsorization

Raw monthly stock returns range from -92.2% to 3,017.6%. Both tails contain extreme observations, with a much more pronounced upside tail. For comparison, the pooled 1st and 99th percentiles are -32.3% and 35.3%. Extreme values alone do not establish data errors.

The left histogram zooms in on the pooled 1st–99th percentile range so the main distribution remains visible. It leaves out 2,816 lower-tail and 2,821 upper-tail observations for display only. The right histogram includes all observations and uses a logarithmic frequency axis to show sparse tails. Returns remain on a linear horizontal axis. Bin widths are approximately 1 percentage point on the left and 10 percentage points on the right; heights are counts, so they should not be compared directly across panels. Both panels show raw returns, pooled across stocks and months, before cleaning.

We winsorize stock returns at the 1st and 99th percentiles within each month (an alternative interpretation is the 0.5th and 99.5th percentiles). This adjusts 5,723 returns (2.02% of the sample), with 2,868 in the lower tail and 2,855 in the upper tail. Subsequent portfolio calculations will use the winsorized returns. Thresholds use linear interpolation; values strictly outside the thresholds are capped, while ties at the thresholds stay unchanged. Missing returns, if present, are excluded from threshold estimation and remain missing. The raw return column is retained.

Source: `data/raw/security_characteristics.csv`; all 245 formation months from November 1998 through March 2019. Returns are one month forward, covering December 1998 through April 2019. The figure uses pooled percentiles only for display; these are not the monthly cleaning thresholds.

Figure: `outputs/return_distribution/raw_return_distribution.png` (also SVG). Monthly thresholds and changed counts: `outputs/return_distribution/monthly_winsorization.csv`. Histogram bins: `outputs/return_distribution/histogram_counts.csv`. Cleaned returns: `data/processed/security_returns/winsorized_returns.csv`. Producer: `src/return_distribution.py`, registered as `return_distribution` in `run_all.py`.
