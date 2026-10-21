# Part 2D: correlations with the value factor

## 2. Active-return correlations and HML

We calculate Pearson correlations using the same 240 return months, January 1999–December 2018. Each strategy series is its monthly return minus the Part 2B market-proxy return. HML comes from the instructor's shared workbook, `FF - 3 factor returns`, column D, with percentage returns divided by 100. We use the supplied historical vintage (worksheet header: July 2023 CRSP database), without updating, winsorizing or subtracting the market from HML. All four series have complete observations; months are matched explicitly.

| Series | Top 20% equal | B/P score | B/P × size | HML |
|---|---:|---:|---:|---:|
| Top 20% · equal weight | 1.000 | 0.957 | 0.740 | 0.555 |
| B/P score weighted | 0.957 | 1.000 | 0.764 | 0.598 |
| B/P × size score weighted | 0.740 | 0.764 | 1.000 | 0.855 |
| Fama–French HML | 0.555 | 0.598 | 0.855 | 1.000 |

The three strategies' active returns are strongly positively correlated (0.740–0.957). Their positive correlations with HML (0.555–0.855) support a common value-style exposure, although they are not identical implementations. The near-perfect correlation between top-20% equal weighting and B/P weighting (0.957) is particularly strong. Shared holdings and the common subtracted market benchmark can also contribute to the correlations.

**B/P × size score weighted is most similar to HML**, with a correlation of 0.855, compared with 0.555 for top-20% equal weighting and 0.598 for B/P weighting. This is consistent with its use of size-based weighting: HML is formed from capitalization-weighted portfolios within small and big stock groups, averaging their value-minus-growth spreads. Our size-weighted value strategy is closer to that within-group weighting principle than the other two methods. This is a plausible explanation, not proof of the contribution of size weighting. [Source: Kenneth French factor construction](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html).

The match is imperfect: our strategy uses percentile size scores rather than actual capitalization, does not separately balance small and big groups, and subtracts the broad market rather than a growth portfolio. Its stock universe, signal timing and return cleaning also differ. A stronger value tilt alone therefore need not produce the highest HML correlation.

Run `python run_all.py --task factor_correlations` after `tracking_error`, or use `--all`. Code: `src/part_2/active_returns/factor_correlations.py`. The aligned decimal-return panel and correlation matrix are saved as `outputs/part_2/active_returns/aligned_active_hml_returns.csv` and `factor_correlations.csv`. The matrix is reported directly as a table.

[Back to Part 2D](README.md)
