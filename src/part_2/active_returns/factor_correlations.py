"""Correlate monthly active value returns with the supplied historical HML series."""
import csv
import math
import numpy as np
import openpyxl
from pathlib import Path
from src.part_2.active_returns.tracking_error import MONTHS
from src.part_2.value_portfolios.value_returns import STRATEGIES, LABELS
from src.part_2.broad_market.market_portfolio import save_csv


def read_hml(path):
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook['FF - 3 factor returns']
        if sheet.cell(4,4).value != 'HML': raise ValueError('Unexpected HML column.')
        result = {}
        for row in sheet.iter_rows(min_row=5, values_only=True):
            date = row[0]
            if not isinstance(date, (int,float)) or not 199901 <= date <= 201812: continue
            if int(date) != date: raise ValueError('Invalid monthly date.')
            key = str(int(date)); month = key[:4]+'-'+key[4:]
            if month not in MONTHS or month in result: raise ValueError('Invalid or duplicate HML month.')
            value = row[3]
            if not isinstance(value,(int,float)) or not math.isfinite(value) or value in (-99.99,-999):
                raise ValueError('Missing HML return.')
            result[month] = value / 100  # French worksheet returns are percentage units.
        if set(result) != set(MONTHS): raise ValueError('Incomplete HML window.')
        return result
    finally:
        workbook.close()


def run(root):
    root=Path(root)
    hml=read_hml(root/'data/raw/ff_msci_shared.xlsx')
    values={s:{} for s in STRATEGIES}
    with (root/'outputs/part_2/active_returns/monthly_active_returns.csv').open() as stream:
        for r in csv.DictReader(stream):
            s,m=r['strategy'],r['month']
            if s not in values or m in values[s]: raise ValueError('Unknown strategy or duplicate month.')
            values[s][m]=float(r['active_return'])
    if any(set(v)!=set(MONTHS) for v in values.values()): raise ValueError('Incomplete active-return window.')
    panel=np.array([[values[s][m] for s in STRATEGIES]+[hml[m]] for m in MONTHS])
    if not np.isfinite(panel).all() or (panel.std(axis=0)==0).any(): raise ValueError('Invalid correlation inputs.')
    corr=np.corrcoef(panel,rowvar=False)
    names=(*STRATEGIES,'hml'); labels=(*LABELS[:3],'Fama–French HML')
    out=root/'outputs/part_2/active_returns'
    save_csv(out/'aligned_active_hml_returns.csv',['month',*names],[[m,*row] for m,row in zip(MONTHS,panel)])
    save_csv(out/'factor_correlations.csv',['series',*names],[[n,*r] for n,r in zip(names,corr)])
    table='| Series | Top 20% equal | B/P score | B/P × size | HML |\n|---|---:|---:|---:|---:|\n'
    table+='\n'.join('| '+label+' | '+' | '.join(f'{v:.3f}' for v in row)+' |' for label,row in zip(labels,corr))
    winner=int(np.argmax(corr[:3,3]))
    report=root/'reports/part_2/active_returns/factor_correlations.md'
    report.write_text(f'''# Part 2D: correlations with the value factor

## 2. Active-return correlations and HML

We calculate Pearson correlations using the same 240 return months, January 1999–December 2018. Each strategy series is its monthly return minus the Part 2B market-proxy return. HML comes from the instructor's shared workbook, `FF - 3 factor returns`, column D, with percentage returns divided by 100. We use the supplied historical vintage (worksheet header: July 2023 CRSP database), without updating, winsorizing or subtracting the market from HML. All four series have complete observations; months are matched explicitly.

{table}

The three strategies' active returns are strongly positively correlated ({min(corr[0,1],corr[0,2],corr[1,2]):.3f}–{max(corr[0,1],corr[0,2],corr[1,2]):.3f}). Their positive correlations with HML ({min(corr[:3,3]):.3f}–{max(corr[:3,3]):.3f}) support a common value-style exposure, although they are not identical implementations. The near-perfect correlation between top-20% equal weighting and B/P weighting ({corr[0,1]:.3f}) is particularly strong. Shared holdings and the common subtracted market benchmark can also contribute to the correlations.

**{labels[winner]} is most similar to HML**, with a correlation of {corr[winner,3]:.3f}, compared with {corr[0,3]:.3f} for top-20% equal weighting and {corr[1,3]:.3f} for B/P weighting. This is consistent with its use of size-based weighting: HML is formed from capitalization-weighted portfolios within small and big stock groups, averaging their value-minus-growth spreads. Our size-weighted value strategy is closer to that within-group weighting principle than the other two methods. This is a plausible explanation, not proof of the contribution of size weighting. [Source: Kenneth French factor construction](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html).

The match is imperfect: our strategy uses percentile size scores rather than actual capitalization, does not separately balance small and big groups, and subtracts the broad market rather than a growth portfolio. Its stock universe, signal timing and return cleaning also differ. A stronger value tilt alone therefore need not produce the highest HML correlation.

Run `python run_all.py --task factor_correlations` after `tracking_error`, or use `--all`. Code: `src/part_2/active_returns/factor_correlations.py`. The aligned decimal-return panel and correlation matrix are saved as `outputs/part_2/active_returns/aligned_active_hml_returns.csv` and `factor_correlations.csv`. The matrix is reported directly as a table.

[Back to Part 2D](README.md)
''')
    print(table)
