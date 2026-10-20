"""Monthly availability of raw one-month-forward stock returns."""
import csv
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import PercentFormatter


def run(root):
    root = Path(root)
    groups = defaultdict(lambda: [0, 0])
    seen = set()
    with (root/'data/raw/security_characteristics.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            month = datetime.strptime(row['date'], '%m/%d/%Y').replace(day=1)
            key = (month, row['stock_id'])
            if key in seen:
                raise ValueError('Duplicate stock-month record')
            seen.add(key)
            groups[month][0] += 1
            text = row['R1M_Usd'].strip()
            if text.lower() in {'', 'na', 'nan', 'null'}:
                continue
            value = float(text)
            if math.isfinite(value):
                groups[month][1] += 1
    dates = sorted(groups)
    if not dates:
        raise ValueError('No observations')
    ratios = [groups[d][1]/groups[d][0] for d in dates]
    output = root/'outputs/part_2/data_validation/return_coverage'
    output.mkdir(parents=True, exist_ok=True)
    with (output/'monthly_return_coverage.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['formation_month','stocks','nonmissing_returns','missing_returns','coverage'])
        writer.writerows((d.strftime('%Y-%m'),groups[d][0],groups[d][1],groups[d][0]-groups[d][1],r) for d,r in zip(dates,ratios))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none'})
    fig, ax = plt.subplots(figsize=(12.8,4.6))
    fig.subplots_adjust(left=.08,right=.97,top=.70,bottom=.30)
    ax.plot(dates,ratios,color='#246B83',lw=2.4)
    ax.set_ylim(0,1.08)
    ax.set_yticks([0,.5,1])
    ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlabel('Formation month',labelpad=10,color='#213444')
    ax.set_ylabel('Return coverage',labelpad=10,color='#213444')
    ax.grid(axis='y',color='#DFE5E9',lw=.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=0,labelcolor='#546471')
    for spine in ax.spines.values(): spine.set_visible(False)
    if all(r==1 for r in ratios):
        label=f'100% coverage in all {len(dates)} months'
    else:
        label=f'Monthly coverage: {min(ratios):.1%}–{max(ratios):.1%}'
    ax.text(.5,.66,label,transform=ax.transAxes,ha='center',color='#246B83',fontsize=15,weight='bold')
    fig.text(.08,.91,'Availability of monthly stock returns',fontsize=22,weight='bold',color='#213444')
    total=sum(v[0] for v in groups.values())
    missing=sum(v[0]-v[1] for v in groups.values())
    fig.text(.08,.81,f'{dates[0]:%b %Y}–{dates[-1]:%b %Y} | {total:,} stock-month observations | {missing:,} missing returns',color='#546471')
    fig.text(.08,.13,'Coverage = stocks with nonmissing returns / stocks recorded in that month. Zero returns count as observed.',fontsize=9,color='#65727C')
    fig.text(.08,.07,'Source: Instructor-provided security_characteristics.csv, raw R1M_Usd. Coverage is conditional on inclusion in the file.',fontsize=9,color='#65727C')
    for ext in ['png','svg']:
        fig.savefig(output/f'monthly_return_coverage.{ext}',dpi=220,facecolor='white')
    plt.close(fig)
    print(f'Return coverage: {len(dates)} months; {total:,} observations; {missing} missing; min={min(ratios):.2%}.')
