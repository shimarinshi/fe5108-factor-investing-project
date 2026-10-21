"""Part 2D: monthly active returns and annualized tracking error."""
import csv
import math
import statistics
from pathlib import Path
from src.part_2.broad_market.market_portfolio import save_csv
from src.part_2.value_portfolios.value_returns import STRATEGIES, LABELS

MONTHS = [f'{1999+i//12:04d}-{i%12+1:02d}' for i in range(240)]


def aligned_differences(strategy, market, months):
    if set(strategy) != set(months) or set(market) != set(months):
        raise ValueError('Both series must cover the same complete return-month window.')
    if not all(math.isfinite(v) for v in [*strategy.values(), *market.values()]):
        raise ValueError('Missing or nonfinite returns are not allowed.')
    return [strategy[m] - market[m] for m in months]


def run(root):
    root = Path(root)
    market_path = root/'outputs/part_2/broad_market/market_returns.csv'
    value_path = root/'outputs/part_2/value_portfolios/value_returns.csv'
    if not market_path.exists() or not value_path.exists():
        raise ValueError('Run market_portfolio and value_returns first.')
    market = {}
    with market_path.open() as f:
        for row in csv.DictReader(f):
            if row['month'] in market: raise ValueError('Duplicate market month.')
            market[row['month']] = float(row['return'])
    values = {s: {} for s in STRATEGIES}
    with value_path.open() as f:
        for row in csv.DictReader(f):
            s, m = row['strategy'], row['month']
            if s not in values: raise ValueError('Unexpected value strategy.')
            if m in values[s]: raise ValueError('Duplicate strategy month.')
            values[s][m] = float(row['return'])
    active, summary = [], []
    for s in STRATEGIES:
        differences = aligned_differences(values[s], market, MONTHS)
        monthly_sd = statistics.stdev(differences)
        summary.append([s, len(differences), monthly_sd, monthly_sd * math.sqrt(12)])
        active.extend([s, m, values[s][m], market[m], d] for m,d in zip(MONTHS,differences))
    out = root/'outputs/part_2/active_returns'; out.mkdir(parents=True,exist_ok=True)
    save_csv(out/'monthly_active_returns.csv', ['strategy','month','strategy_return','market_return','active_return'], active)
    save_csv(out/'tracking_error.csv', ['strategy','months','monthly_active_sample_sd','annualized_tracking_error'], summary)
    table = '\n'.join(f'| {label} | {r[3]:.2%} |' for label,r in zip(LABELS,summary))
    lowest = min(range(3), key=lambda i: summary[i][3])
    report = root/'reports/part_2/active_returns/README.md'; report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(f'''# Part 2D: active returns

## 1. Annualized tracking error

For each of the 240 return months from January 1999 to December 2018, we subtract the Part 2B market-proxy return from each Part 2C value-strategy return. Tracking error is the sample standard deviation of these monthly differences (ddof = 1, centered on their arithmetic mean), multiplied by sqrt(12). Both inputs retain the previously agreed monthly winsorization and universe rules; Pb = 0.50 is excluded from the value strategies and retained in the market proxy. We align on return month and require complete, unique observations.

| Value portfolio | Annualized tracking error |
|---|---:|
{table}

**{LABELS[lowest]} has the lowest tracking error ({summary[lowest][3]:.2%}).** It retains the market proxy's size-score weighting and adds a value tilt, so its allocation is structurally closer to the benchmark. The top-20% equal-weighted portfolio has the highest tracking error ({summary[0][3]:.2%}): it holds a narrower set of value stocks and does not retain the benchmark's size weighting. These differences plausibly explain the ranking. Tracking error measures fluctuations in returns relative to the market, rather than the strategy's standalone volatility or average outperformance.

This ranking is consistent with the overall visual impression of the cumulative-growth chart: the B/P × size-weighted portfolio follows the market proxy more closely, while B/P weighting and especially the top-20% equal-weighted portfolio show greater departures from its path. The tracking-error calculation, rather than cumulative distance alone, establishes the ranking.

Run `python run_all.py --task tracking_error` after `market_portfolio` and `value_returns`, or run `--all`. Code: `src/part_2/active_returns/tracking_error.py`. Tables: `outputs/part_2/active_returns/monthly_active_returns.csv` and `tracking_error.csv`. All returns and standard deviations are stored as decimals. No additional chart is used for this question.

## 2. Correlations with each other and HML

See [Active-return correlations and HML](factor_correlations.md) for the aligned four-series correlation matrix and interpretation.

[Back to Part 2](../README.md)
''')
    print(table)
