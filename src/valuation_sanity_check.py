"""Lightweight within-month rank-correlation checks of P/B = market cap / book equity."""
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def average_ranks(values):
    _, inverse, counts = np.unique(values, return_inverse=True, return_counts=True)
    ends = np.cumsum(counts)
    ranks = ends - (counts - 1) / 2
    return ranks[inverse]


def spearman(x, y):
    x, y = average_ranks(x), average_ranks(y)
    if len(x) < 10 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return float('nan')
    return float(np.corrcoef(x, y)[0, 1])


def run(root):
    root = Path(root)
    months = defaultdict(list)
    with (root/'data/raw/security_characteristics.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            month = datetime.strptime(row['date'], '%m/%d/%Y').strftime('%Y-%m')
            months[month].append([float(row[k]) for k in ['Pb', 'Bv', 'Mkt_Cap_3M_Usd']])
    # Column positions: Pb=0, Bv=1, market cap=2.
    checks = [('Similar Bv', 1, 2, 0, 1),
              ('Similar market cap', 2, 1, 0, -1),
              ('Similar Pb', 0, 2, 1, 1)]
    details, summary = [], []
    for label, fixed, x, y, sign in checks:
        for sample in ['Exclude Pb = 0.50', 'Include all']:
            correlations = []
            skipped = 0
            for month, records in sorted(months.items()):
                a = np.asarray(records)
                if sample == 'Exclude Pb = 0.50':
                    a = a[a[:, 0] != .5]
                # Supplied ranks in (0,.1], (.1,.2], ...; do not rerank filtered data.
                bins = np.minimum((np.ceil(np.round(a[:, fixed]*100, 8)/10)-1).astype(int),9)
                for band in range(10):
                    subset = a[bins == band]
                    rho = spearman(subset[:, x], subset[:, y])
                    if np.isfinite(rho):
                        correlations.append(rho)
                    else:
                        skipped += 1
                    details.append([label, sample, month, band+1, len(subset),
                                    rho if np.isfinite(rho) else ''])
            summary.append([label, '+' if sign > 0 else '-', sample, len(correlations),
                            skipped, float(np.median(correlations)),
                            float(np.mean(np.array(correlations)*sign > 0))])
    out = root/'outputs/valuation_sanity_check'
    out.mkdir(parents=True, exist_ok=True)
    for name, header, rows in [
        ('group_correlations.csv', ['check','sample','formation_month','rank_band','observations','spearman_rho'], details),
        ('summary.csv', ['check','expected_sign','sample','valid_groups','skipped_groups','median_rho','share_expected_sign'], summary)]:
        with (out/name).open('w',newline='') as stream:
            w=csv.writer(stream); w.writerow(header); w.writerows(rows)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'svg.fonttype': 'none'})
    fig, ax = plt.subplots(figsize=(13.4, 7.3))
    fig.subplots_adjust(left=.31, right=.955, top=.72, bottom=.30)
    positions = np.arange(3)
    main_values = [r[5] for r in summary[::2]]
    control_values = [r[5] for r in summary[1::2]]
    for offset, values, color, label in [
        (-.17, main_values, '#246B83', 'Exclude Pb = 0.50'),
        (.17, control_values, '#87949E', 'Include all observations')]:
        ax.barh(positions + offset, values, height=.27, color=color, label=label)
        for y, value in zip(positions + offset, values):
            # Labels sit inside bars to preserve the full -1 to +1 reference scale.
            ax.text(value - .035 if value > 0 else value + .035, y,
                    f'{value:+.3f}', ha='right' if value > 0 else 'left',
                    va='center', color='white', fontsize=11, weight='bold')
    ax.set_yticks(positions, [
        'Similar book equity (Bv)\nMarket cap vs. P/B  |  Expected: +',
        'Similar market cap\nBook equity vs. P/B  |  Expected: −',
        'Similar P/B\nMarket cap vs. book equity  |  Expected: +'])
    ax.invert_yaxis()
    ax.set_xlim(-1, 1)
    ax.set_xticks([-1, -.5, 0, .5, 1], ['−1.0', '−0.5', '0', '+0.5', '+1.0'])
    ax.set_xlabel('Median within-group Spearman correlation', labelpad=14, color='#213444')
    ax.axvline(0, color='#546471', linewidth=1)
    ax.grid(axis='x', color='#DFE5E9', linewidth=.7)
    ax.set_axisbelow(True)
    ax.tick_params(axis='both', length=0, pad=12, labelcolor='#546471')
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.text(.065, .93, 'Do the valuation fields move as expected?',
             fontsize=23, weight='bold', color='#213444')
    fig.text(.065, .872, 'P/B = market capitalization / book equity',
             fontsize=13, color='#546471')
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(.06, .825),
               ncol=2, frameon=False, fontsize=11)
    fig.text(.065, .15, 'Each month: hold one supplied score approximately constant in 10 rank bands; correlate the other two within each band.',
             fontsize=9.5, color='#65727C')
    fig.text(.065, .108, 'Bars show the median across valid month-band groups, equally weighted. Groups with fewer than 10 stocks or constant inputs are omitted.',
             fontsize=9.5, color='#65727C')
    fig.text(.065, .066, 'Source: security_characteristics.csv; Nov 1998–Mar 2019. Valid groups per sample: 2,446 / 2,445 / 2,450 (top to bottom).',
             fontsize=9.5, color='#65727C')
    fig.text(.065, .024, 'Expected directions assume positive book equity. Rank-based comparisons check consistency, not exact equality of raw ratios.',
             fontsize=9.5, color='#65727C')
    for extension in ('png', 'svg'):
        fig.savefig(out / f'valuation_sanity_check.{extension}', dpi=220, facecolor='white')
    plt.close(fig)
    table=['| Similar characteristic | Expected sign | Median rho, excluding 0.50 | Groups with expected sign | Median rho, including 0.50 |',
           '|---|---|---:|---:|---:|']
    for i in range(0,len(summary),2):
        main,control=summary[i:i+2]
        table.append(f'| {main[0]} | {main[1]} | {main[5]:.3f} | {main[6]:.1%} | {control[5]:.3f} |')
    text='''# Valuation sanity check

![Valuation sanity check](../outputs/valuation_sanity_check/valuation_sanity_check.png)

Starting from P/B = market capitalization / book equity, we compare stocks with similar ranks in one characteristic and check the relationship between the other two. With positive book equity, similar Bv implies a positive relationship between market cap and P/B; similar market cap implies a negative relationship between Bv and P/B; similar P/B implies a positive relationship between market cap and Bv.

Within each month, we place stocks in ten fixed bands of the supplied score for the characteristic held approximately constant: (0, 0.10], ..., (0.90, 1.00]. We calculate Spearman correlations within each band, using average ranks for ties, then report the median across month-band groups. The main check excludes Pb = 0.50; retaining these observations provides a comparison. Groups with fewer than ten observations or a constant compared variable are skipped and counted in the summary CSV. Each valid group receives equal weight; the percentages below refer to groups, not stocks.

'''+ '\n'.join(table)+'''

This is a directional consistency check, not verification of the accounting identity. Similar percentile ranks do not guarantee similar raw amounts, Bv ranks do not identify negative equity, and the supplied market-cap field is a three-month average that may differ from the denominator timing used for P/B. We do not divide percentile scores or interpret these correlations as causal effects.

Source: `data/raw/security_characteristics.csv`; all supplied formation months, November 1998–March 2019. The grouped horizontal bar chart uses a common −1 to +1 scale, teal for the exclusion sample and gray for the full sample. Labels show expected signs and observed medians. The PNG/SVG figure and detailed and summary tables are in `outputs/valuation_sanity_check/`. Run `python run_all.py --task valuation_sanity_check`. This diagnostic does not modify any observations.
'''
    (root/'reports/valuation_sanity_check.md').write_text(text)
    print('\n'.join(table))
    print('Valid/skipped groups:',[(r[0],r[2],r[3],r[4]) for r in summary])
