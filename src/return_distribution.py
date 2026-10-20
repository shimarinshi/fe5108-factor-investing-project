"""Describe raw forward returns and winsorize separately by formation month."""
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, StrMethodFormatter
import numpy as np


def winsorize_month(values):
    """Linear-interpolated P1/P99; preserve missing values and observations."""
    a = np.asarray(values, dtype=float)
    valid = a[np.isfinite(a)]
    if not len(valid):
        return a.copy(), float('nan'), float('nan')
    lo, hi = np.quantile(valid, [.01, .99], method='linear')
    return np.clip(a, lo, hi), float(lo), float(hi)


def write_csv(path, columns, rows):
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(rows)


def run(root):
    root = Path(root)
    output = root / 'outputs/return_distribution'
    processed = root / 'data/processed/security_returns'
    output.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)
    groups = defaultdict(list)
    with (root / 'data/raw/security_characteristics.csv').open(newline='') as stream:
        for r in csv.DictReader(stream):
            day = datetime.strptime(r['date'], '%m/%d/%Y')
            value = float(r['R1M_Usd']) if r['R1M_Usd'].strip() else float('nan')
            if np.isinf(value):
                raise ValueError('Infinite return requires source review.')
            groups[day.strftime('%Y-%m')].append((r['stock_id'], value))
    raw = np.array([v for month in sorted(groups) for _, v in groups[month]])
    valid = raw[np.isfinite(raw)]
    lo, hi = np.quantile(valid, [.01, .99], method='linear')
    below, above = int((valid < lo).sum()), int((valid > hi).sum())
    clean_rows, audit = [], []
    for month, records in sorted(groups.items()):
        values = np.array([v for _, v in records])
        clean, lower, upper = winsorize_month(values)
        y, m = map(int, month.split('-'))
        return_month = f'{y + m // 12:04d}-{m % 12 + 1:02d}'
        for (sid, value), cleaned in zip(records, clean):
            clean_rows.append((sid, month, return_month,
                               value if np.isfinite(value) else '',
                               cleaned if np.isfinite(cleaned) else '',
                               bool(np.isfinite(value) and value != cleaned)))
        audit.append((month, len(values), int(np.isfinite(values).sum()), lower, upper,
                      int((values < lower).sum()), int((values > upper).sum())))
    write_csv(processed / 'winsorized_returns.csv',
              ['stock_id', 'formation_month', 'return_month', 'raw_return',
               'winsorized_return', 'was_winsorized'], clean_rows)
    write_csv(output / 'monthly_winsorization.csv',
              ['formation_month', 'observations', 'valid_returns', 'p01', 'p99',
               'lower_values_changed', 'upper_values_changed'], audit)

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'svg.fonttype': 'none', 'axes.spines.top': False,
                         'axes.spines.right': False})
    blue, red, ink, gray = '#246B83', '#BD503B', '#213444', '#546471'
    fig, axes = plt.subplots(1, 2, figsize=(14, 7.4))
    fig.subplots_adjust(left=.075, right=.975, bottom=.29, top=.73, wspace=.25)
    # Central bins are approximately one percentage point wide.
    central_edges = np.linspace(lo, hi, int(np.ceil((hi-lo)/.01))+1)
    full_edges = np.arange(np.floor(valid.min()/.1)*.1,
                           np.ceil(valid.max()/.1)*.1+.100001, .1)
    histograms = []
    for panel, ax, edges in zip(['central', 'full'], axes, [central_edges, full_edges]):
        counts, edges, patches = ax.hist(valid, bins=edges, color=blue,
                                         edgecolor='white', linewidth=.25)
        histograms.extend((panel, float(a), float(b), int(n))
                          for a,b,n in zip(edges[:-1],edges[1:],counts))
        ax.set_axisbelow(True)
        ax.grid(axis='y', color='#DFE5E9', linewidth=.6)
        ax.tick_params(length=0, labelcolor=gray)
        ax.set_xlabel('One-month forward return', color=ink, labelpad=12)
        ax.spines['left'].set_color('#DFE5E9')
        ax.spines['bottom'].set_color('#DFE5E9')
        ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    axes[0].set_title('A. Main distribution', loc='left', fontsize=14, weight='bold', color=ink, pad=38)
    axes[0].text(0,1.045, f'P1–P99 view: {lo:.1%} to {hi:.1%}', transform=axes[0].transAxes, color=gray)
    axes[0].set_xlim(lo, hi)
    axes[0].set_ylabel('Number of stock-month observations', color=ink, labelpad=10)
    axes[0].yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    axes[1].set_title('B. Full distribution', loc='left', fontsize=14, weight='bold', color=ink, pad=38)
    axes[1].text(0,1.045,'All observations; logarithmic frequency axis', transform=axes[1].transAxes, color=gray)
    axes[1].set_yscale('log')
    axes[1].set_ylim(.7, 1e6)
    axes[1].set_xlim(-1.5, 32)
    axes[1].set_xticks([0,5,10,15,20,25,30])
    axes[1].set_ylabel('Number of observations (log scale)', color=ink, labelpad=10)
    for value, pos, label in [(valid.min(),(.12,.83),'Minimum'),
                               (valid.max(),(.52,.48),'Maximum')]:
        axes[1].axvline(value, color=red, linestyle='--', linewidth=.9, alpha=.8)
        axes[1].annotate(f'{label}: {value:+,.1%}', xy=(value,2),
                         xytext=pos, textcoords='axes fraction', color=red,
                         arrowprops={'arrowstyle':'-', 'color':red, 'lw':.8},
                         bbox={'facecolor':'white','edgecolor':'none','pad':3})
    fig.text(.075,.93,'Distribution of raw stock returns', fontsize=23, weight='bold', color=ink)
    fig.text(.075,.875, f'{len(valid):,} stock-month observations | Nov 1998–Mar 2019 formation months', fontsize=12, color=gray)
    fig.text(.075,.185, f'Panel A omits {below:,} observations below P1 and {above:,} above P99 for display only. Panel B includes all observations.', fontsize=10, color=gray)
    fig.text(.075,.145,'Bins: approximately 1 percentage point in A; 10 percentage points in B. Bar heights are counts, not densities.', fontsize=10, color=gray)
    fig.text(.075,.105,'The log frequency axis makes sparse tail observations visible; returns remain on a linear horizontal axis.', fontsize=10, color=gray)
    fig.text(.075,.065,'Source: Instructor-provided security_characteristics.csv. All finite raw forward returns pooled across stocks and months.', fontsize=9, color='#65727C')
    fig.text(.075,.028,'Both panels show uncleaned data. Display percentiles are pooled; winsorization thresholds are computed separately within each month.', fontsize=9, color='#65727C')
    for ext in ['png','svg']:
        fig.savefig(output/f'raw_return_distribution.{ext}',dpi=220,facecolor='white')
    plt.close(fig)
    write_csv(output/'histogram_counts.csv',['panel','bin_left','bin_right','count'],histograms)
    changed_low=sum(r[5] for r in audit)
    changed_high=sum(r[6] for r in audit)
    summary={'observations':len(raw),'finite_returns':len(valid),'months':len(groups),
             'minimum':float(valid.min()),'maximum':float(valid.max()),
             'pooled_p01':float(lo),'pooled_p99':float(hi),
             'display_below':below,'display_above':above,
             'winsorized_lower':changed_low,'winsorized_upper':changed_high,
             'quantile_method':'linear','monthly_limits':[.01,.99]}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    text = f'''# Return distribution and winsorization

Raw monthly stock returns range from {valid.min():.1%} to {valid.max():,.1%}. Both tails contain extreme observations, with a much more pronounced upside tail. For comparison, the pooled 1st and 99th percentiles are {lo:.1%} and {hi:.1%}. Extreme values alone do not establish data errors.

The left histogram zooms in on the pooled 1st–99th percentile range so the main distribution remains visible. It leaves out {below:,} lower-tail and {above:,} upper-tail observations for display only. The right histogram includes all observations and uses a logarithmic frequency axis to show sparse tails. Returns remain on a linear horizontal axis. Bin widths are approximately 1 percentage point on the left and 10 percentage points on the right; heights are counts, so they should not be compared directly across panels. Both panels show raw returns, pooled across stocks and months, before cleaning.

We winsorize stock returns at the 1st and 99th percentiles within each month (an alternative interpretation is the 0.5th and 99.5th percentiles). This adjusts {changed_low + changed_high:,} returns ({(changed_low + changed_high) / len(valid):.2%} of the sample), with {changed_low:,} in the lower tail and {changed_high:,} in the upper tail. Subsequent portfolio calculations will use the winsorized returns. Thresholds use linear interpolation; values strictly outside the thresholds are capped, while ties at the thresholds stay unchanged. Missing returns, if present, are excluded from threshold estimation and remain missing. The raw return column is retained.

Source: `data/raw/security_characteristics.csv`; all {len(groups)} formation months from November 1998 through March 2019. Returns are one month forward, covering December 1998 through April 2019. The figure uses pooled percentiles only for display; these are not the monthly cleaning thresholds.

Figure: `outputs/return_distribution/raw_return_distribution.png` (also SVG). Monthly thresholds and changed counts: `outputs/return_distribution/monthly_winsorization.csv`. Histogram bins: `outputs/return_distribution/histogram_counts.csv`. Cleaned returns: `data/processed/security_returns/winsorized_returns.csv`. Producer: `src/return_distribution.py`, registered as `return_distribution` in `run_all.py`.
'''
    (root/'reports/return_distribution.md').write_text(text)
    print(json.dumps(summary))
