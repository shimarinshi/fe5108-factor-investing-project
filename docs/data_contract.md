# Data contract

## Source and boundaries

The supplied security CSV is an anonymized course extract attributed by the handout to Coqueret and Guida's Machine Learning for Factor Investing data. It is not the previous project's Massive dataset. `data/raw/source_manifest.json` records original filenames, destinations and SHA-256 hashes; original bytes are retained. Raw observations are immutable: cleaning writes derived files and records affected counts and rules.

## Security fields

| Raw field | Interpretation |
|---|---|
| stock_id | Anonymized identifier; preserve as a string, never map to a guessed ticker |
| date | Signal/formation date, month end; raw format M/D/YYYY |
| R1M_Usd | Following month's return, in decimals; 0.01 means 1% |
| Pb | Standardized price-to-book field, not raw P/B |
| Bv | Standardized book-equity field, not dollars |
| Mkt_Cap_3M_Usd | Standardized market-cap field, not dollars or true company capitalization |
| Vol3Y_Usd | Standardized volatility field, not a directly usable annual volatility estimate |

The actual supplied standardized fields range from 0.01 to 1.00; the handout describes percentile ranks with 100 highest. Record this scale difference explicitly; do not blindly multiply or reinterpret it. Do not divide percentile market cap by percentile book equity to claim recovery of actual P/B. Subsequent value portfolios will exclude Pb = 0.50 stock-months in the baseline and retain them in a robustness comparison; this is not proof of negative equity. Part 2C reverses the supplied score as B/P score = 1.01 − Pb, without reranking after exclusion. This is a percentile transformation, not recovery of the raw ratio.

For Part 2 performance, formation months December 1998–November 2018 correspond to return months January 1999–December 2018. Store both dates; join benchmarks on RETURN month. Future returns are outcomes, never selection features. Availability in the teaching file does not independently prove point-in-time provenance.

## Return cleaning and remaining decisions

The agreed interpretation is monthly 1st/99th percentile winsorization (an alternative is 0.5th/99.5th). The return_distribution task uses NumPy linear-interpolated quantiles and caps values strictly outside the thresholds; ties remain unchanged. Missing returns are excluded from quantiles and preserved. Raw and cleaned return columns are stored separately. Pooled percentiles are only display limits. Do not silently fill missing returns, discard outliers, change the universe using future outcomes, or renormalize only over winners/survivors. Record the chosen missing-return/weight treatment and its implications.

The bootstrap records ranges and missingness without changing observations. Its passed checks prove file integrity/schema and unique stock-date keys, not economic correctness or completed Part 2A cleaning.

## Shared benchmarks and metrics

Part 1/2/3 use the specified MSCI USA **gross total-return** benchmark, not the earlier project's MSCI World net-return series or a price index. Convert month-end index levels to monthly returns and retain the preceding level needed for the first month. French percentage returns must be converted to decimals once; recognized missing sentinels must become missing before computations. HML is a spread, not a long-only portfolio return.

Document arithmetic versus geometric annualization, volatility ddof, Sharpe definition, RF subtraction, rebalancing/drift and cost assumptions. Follow each question's specification and use consistent definitions across comparisons. Do not compare mismatched return months or silently use pairwise deletion across different samples.
