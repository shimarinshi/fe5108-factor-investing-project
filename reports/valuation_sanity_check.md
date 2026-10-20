# Valuation sanity check

Starting from P/B = market capitalization / book equity, we compare stocks with similar ranks in one characteristic and check the relationship between the other two. With positive book equity, similar Bv implies a positive relationship between market cap and P/B; similar market cap implies a negative relationship between Bv and P/B; similar P/B implies a positive relationship between market cap and Bv.

Within each month, we place stocks in ten fixed bands of the supplied score for the characteristic held approximately constant: (0, 0.10], ..., (0.90, 1.00]. We calculate Spearman correlations within each band, using average ranks for ties, then report the median across month-band groups. The main check excludes Pb = 0.50; retaining these observations provides a comparison. Groups with fewer than ten observations or a constant compared variable are skipped and counted in the summary CSV. Each valid group receives equal weight; the percentages below refer to groups, not stocks.

| Similar characteristic | Expected sign | Median rho, excluding 0.50 | Groups with expected sign | Median rho, including 0.50 |
|---|---|---:|---:|---:|
| Similar Bv | + | 0.898 | 100.0% | 0.893 |
| Similar market cap | - | -0.897 | 100.0% | -0.859 |
| Similar Pb | + | 0.977 | 100.0% | 0.974 |

This is a directional consistency check, not verification of the accounting identity. Similar percentile ranks do not guarantee similar raw amounts, Bv ranks do not identify negative equity, and the supplied market-cap field is a three-month average that may differ from the denominator timing used for P/B. We do not divide percentile scores or interpret these correlations as causal effects.

Source: `data/raw/security_characteristics.csv`; all supplied formation months, November 1998–March 2019. The grouped horizontal bar chart uses a common −1 to +1 scale, teal for the exclusion sample and gray for the full sample. Labels show expected signs and observed medians. The PNG/SVG figure and detailed and summary tables are in `outputs/valuation_sanity_check/`. Run `python run_all.py --task valuation_sanity_check`. This diagnostic does not modify any observations.
