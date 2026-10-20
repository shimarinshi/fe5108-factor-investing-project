"""Monthly long-only market proxy weighted by standardized market-cap scores."""
import csv
import calendar
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import PercentFormatter


def portfolio(scores, returns):
    scores, returns = np.asarray(scores, float), np.asarray(returns, float)
    if scores.shape != returns.shape or not len(scores) or not np.isfinite(scores).all() or not np.isfinite(returns).all():
        raise ValueError('All holdings require valid scores and returns; no silent exclusions.')
    if (scores < 0).any() or scores.sum() <= 0:
        raise ValueError('Market-cap scores must be nonnegative with a positive sum.')
    weights = scores / scores.sum()
    return weights, float(weights @ returns)


def save_csv(path, header, rows):
    with path.open('w', newline='') as stream:
        w=csv.writer(stream,lineterminator='\n'); w.writerow(header)
        w.writerows([f'{v:.12f}' if isinstance(v, (float, np.floating)) else v for v in row] for row in rows)


def style(ax):
    ax.grid(axis='y', color='#DFE5E9', lw=.7); ax.set_axisbelow(True)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0, labelcolor='#546471')


def run(root):
    root=Path(root)
    source=root/'data/processed/security_returns/winsorized_returns.csv'
    if not source.exists():
        raise ValueError('Run return_distribution first to create shared cleaned returns.')
    clean={}
    for r in csv.DictReader(source.open()):
        key=(r['stock_id'],r['formation_month'])
        if key in clean: raise ValueError('Duplicate cleaned return key')
        clean[key]=r
    groups=defaultdict(list)
    for r in csv.DictReader((root/'data/raw/security_characteristics.csv').open()):
        month=datetime.strptime(r['date'],'%m/%d/%Y').strftime('%Y-%m')
        if '1998-12'<=month<='2018-11': groups[month].append(r)
    expected=[f'{1998+(11+i)//12:04d}-{(11+i)%12+1:02d}' for i in range(240)]
    if sorted(groups)!=expected: raise ValueError('Incomplete formation-month window')
    out=root/'outputs/part_2/broad_market'; out.mkdir(parents=True,exist_ok=True)
    results=[]; holdings=[]; bands=[]
    for month,rows in sorted(groups.items()):
        scores=[float(r['Mkt_Cap_3M_Usd']) for r in rows]
        matched=[clean[(r['stock_id'],month)] for r in rows]
        y,m=map(int,month.split('-')); rm=f'{y+m//12:04d}-{m%12+1:02d}'
        if any(r['return_month']!=rm for r in matched): raise ValueError('Return-month mismatch')
        if any(float(c['raw_return'])!=float(r['R1M_Usd']) for c,r in zip(matched,rows)):
            raise ValueError('Cleaned input does not match raw returns')
        w,ret=portfolio(scores,[r['winsorized_return'] for r in matched])
        pb_weight=sum(weight for weight,r in zip(w,rows) if float(r['Pb'])==.5)
        results.append([rm,month,ret,len(rows),float(w.sum()),float(w.min()),float(w.max()),pb_weight])
        for r,weight in zip(rows,w): holdings.append(['market_score_weighted',month,r['stock_id'],weight])
        scores=np.asarray(scores)
        b=np.minimum(np.ceil(np.round(scores*100,8)/10).astype(int)-1,9)
        for k in range(10):
            select=b==k
            bands.append([month,k+1,int(select.sum()),float(w[select].sum()),float(select.mean())])
    save_csv(out/'market_returns.csv',['month','formation_month','return','stocks','weight_sum','minimum_weight','maximum_weight','pb_half_weight'],results)
    save_csv(out/'portfolio_weights.csv',['strategy','formation_month','stock_id','weight'],holdings)
    save_csv(out/'monthly_size_band_weights.csv',['formation_month','size_band','stocks','portfolio_weight','equal_weight_share'],bands)
    band_array=np.array([[r[3],r[4]] for r in bands]).reshape(240,10,2)
    means=band_array.mean(axis=0)
    save_csv(out/'average_size_band_weights.csv',['size_band','portfolio_weight','equal_weight_share'],[[i+1,*r] for i,r in enumerate(means)])
    dates=[datetime.strptime(r[0],'%Y-%m') for r in results]
    dates=[d.replace(day=calendar.monthrange(d.year,d.month)[1]) for d in dates]
    returns=np.array([r[2] for r in results]); wealth=np.cumprod(1+returns)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none'})
    blue,gray,ink='#246B83','#87949E','#213444'
    fig,ax=plt.subplots(figsize=(12.8,6.4)); fig.subplots_adjust(left=.08,right=.97,top=.73,bottom=.25)
    x=np.arange(10)
    bars=ax.bar(x-.19,means[:,0],.36,color=blue,label='Market-cap score weights')
    ax.bar(x+.19,means[:,1],.36,color=gray,label='Equal-weight allocation to the same bands')
    ax.bar_label(bars,labels=[f'{v:.1%}' for v in means[:,0]],padding=4,fontsize=10,color=ink)
    ax.set_xticks(x,['1\nSmallest','2','3','4','5','6','7','8','9','10\nLargest'])
    ax.yaxis.set_major_formatter(PercentFormatter(1)); ax.set_ylim(0,.235)
    ax.set_ylabel('Average share of portfolio capital'); ax.set_xlabel('Supplied market-cap score band',labelpad=10)
    ax.legend(frameon=False,loc='upper left',fontsize=10); style(ax)
    fig.text(.08,.92,'How market-cap scores allocate capital',fontsize=23,weight='bold',color=ink)
    fig.text(.08,.85,'Monthly portfolio weights, averaged over 240 formation months',color='#546471')
    fig.text(.08,.12,'Bands: (0, 0.10], …, (0.90, 1.00] of the supplied score; no reranking. Equal-weight bars use the same monthly stocks.',fontsize=9,color='#65727C')
    fig.text(.08,.065,'Source: security_characteristics.csv; Dec 1998–Nov 2018. All stocks retained, including Pb = 0.50. Scores are not actual market caps.',fontsize=9,color='#65727C')
    for ext in ['png','svg']: fig.savefig(out/f'market_weight_allocation.{ext}',dpi=220,facecolor='white')
    plt.close(fig)
    fig,axes=plt.subplots(2,1,figsize=(12.8,8),sharex=True,gridspec_kw={'height_ratios':[1.4,1]})
    fig.subplots_adjust(left=.09,right=.96,top=.80,bottom=.19,hspace=.23)
    axes[0].plot([datetime(1998,12,31)]+dates,[1]+list(wealth),color=blue,lw=2)
    axes[0].set_ylabel('Value of $1'); axes[0].set_ylim(bottom=0)
    axes[0].annotate(f'${wealth[-1]:.2f}',(dates[-1],wealth[-1]),xytext=(10,0),textcoords='offset points',ha='left',va='center',color=blue,weight='bold')
    axes[1].bar(dates,returns,width=22,color=[blue if v>=0 else '#BD503B' for v in returns])
    axes[1].axhline(0,color='#546471',lw=.7); axes[1].yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
    axes[1].set_ylabel('Monthly return'); axes[1].set_xlabel('Return month',labelpad=10)
    axes[1].xaxis.set_major_locator(mdates.YearLocator(2)); axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    for ax in axes: style(ax)
    fig.text(.09,.93,'Performance of the market proxy',fontsize=23,weight='bold',color=ink)
    fig.text(.09,.87,'Jan 1999–Dec 2018 | Rebalanced monthly using standardized market-cap scores',color='#546471')
    fig.text(.09,.105,'Source: supplied security panel and Part 2A monthly P1/P99 winsorized returns. All eligible-month stock records are included.',fontsize=9,color='#65727C')
    fig.text(.09,.065,'Formation scores set next-month weights. No leverage or cash; no transaction costs. Growth compounds monthly portfolio returns.',fontsize=9,color='#65727C')
    fig.text(.09,.025,'This is a score-weighted market approximation, not MSCI USA or an index weighted by actual market capitalization.',fontsize=9,color='#65727C')
    for ext in ['png','svg']: fig.savefig(out/f'market_return_history.{ext}',dpi=220,facecolor='white')
    plt.close(fig)
    report=root/'reports/part_2/broad_market/README.md'; report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(f'''# Part 2B: broad-market portfolio

## 1. Market-cap score weighting

For each formation month from December 1998 to November 2018, we divide each stock's standardized market-cap score by the sum of scores across that month's stocks. The next-month portfolio return is the weighted sum of the Part 2A winsorized stock returns. We rebalance monthly, retain Pb = 0.50 observations, and assume no transaction costs. The resulting 240 returns cover January 1999–December 2018. All weights are nonnegative and sum to one in each month; unavailable scores or outcomes trigger an error rather than silent stock deletion.

![Capital allocation by market-cap score](../../../outputs/part_2/broad_market/market_weight_allocation.png)

The highest market-cap score band receives an average {means[9,0]:.1%} of capital, versus {means[0,0]:.1%} for the lowest band. Equal weighting of the same stocks allocates {means[9,1]:.1%} and {means[0,1]:.1%}, respectively. The score-based rule therefore tilts capital toward larger-ranked stocks. It does not reproduce true capitalization weights: a score twice as large does not imply twice the actual market cap.

The chart groups stocks by fixed supplied score bands, (0, 0.10], ..., (0.90, 1.00], and averages each band's capital share equally across months. The gray comparison is the fraction of stocks in each band, not a separate equal-weight performance backtest.

![Monthly return history and cumulative growth](../../../outputs/part_2/broad_market/market_return_history.png)

A $1 investment grows to ${wealth[-1]:.2f} over the 240 months under these assumptions. The lower panel displays the monthly returns; the upper panel compounds them from December 1998. The portfolio is an approximate market benchmark, not an exact MSCI replication.

Run `python run_all.py --task return_distribution` first if the shared cleaned panel is absent, then `python run_all.py --task market_portfolio`; `--all` runs both in dependency order. Code: `src/part_2/broad_market/market_portfolio.py`. Results: `outputs/part_2/broad_market/` (returns, security weights, monthly/average band allocations and PNG/SVG figures). Stock weights are keyed by strategy, formation_month and stock_id; returns use realized month. The shared raw CSV remains unchanged.

## 2. MSCI USA comparison

See [MSCI USA comparison](benchmark_comparison.md) for the aligned cumulative-growth chart, monthly-return scatter and interpretation. Run `benchmark_comparison` after this task.

[Back to Part 2](../README.md)
''')
    print(f'240 months; {len(holdings):,} weights; end wealth {wealth[-1]:.6f}; low/high band {means[0,0]:.6f}/{means[9,0]:.6f}')
