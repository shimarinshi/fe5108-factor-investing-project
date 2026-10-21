# Part 2D: active returns

## 1. Annualized tracking error

For each of the 240 return months from January 1999 to December 2018, we subtract the Part 2B market-proxy return from each Part 2C value-strategy return. Tracking error is the sample standard deviation of these monthly differences (ddof = 1, centered on their arithmetic mean), multiplied by sqrt(12). Both inputs retain the previously agreed monthly winsorization and universe rules; Pb = 0.50 is excluded from the value strategies and retained in the market proxy. We align on return month and require complete, unique observations.

| Value portfolio | Annualized tracking error |
|---|---:|
| Top 20% · equal weight | 9.51% |
| B/P score weighted | 4.94% |
| B/P × size score weighted | 2.86% |

**B/P × size score weighted has the lowest tracking error (2.86%).** It retains the market proxy's size-score weighting and adds a value tilt, so its allocation is structurally closer to the benchmark. The top-20% equal-weighted portfolio has the highest tracking error (9.51%): it holds a narrower set of value stocks and does not retain the benchmark's size weighting. These differences plausibly explain the ranking. Tracking error measures fluctuations in returns relative to the market, rather than the strategy's standalone volatility or average outperformance.

This ranking is consistent with the overall visual impression of the cumulative-growth chart: the B/P × size-weighted portfolio follows the market proxy more closely, while B/P weighting and especially the top-20% equal-weighted portfolio show greater departures from its path. The tracking-error calculation, rather than cumulative distance alone, establishes the ranking.

Run `python run_all.py --task tracking_error` after `market_portfolio` and `value_returns`, or run `--all`. Code: `src/part_2/active_returns/tracking_error.py`. Tables: `outputs/part_2/active_returns/monthly_active_returns.csv` and `tracking_error.csv`. All returns and standard deviations are stored as decimals. No additional chart is used for this question.

## 2. Correlations with each other and HML

See [Active-return correlations and HML](factor_correlations.md) for the aligned four-series correlation matrix and interpretation.

[Back to Part 2](../README.md)
