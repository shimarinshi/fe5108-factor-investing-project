"""Compare the market proxy with instructor-provided MSCI USA gross USD returns."""
import csv
import calendar
from datetime import datetime
from pathlib import Path
import numpy as np
import openpyxl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import PercentFormatter
from src.part_2.broad_market.market_portfolio import save_csv, style


def read_levels(path):
    workbook=openpyxl.load_workbook(path,read_only=True,data_only=True)
    rows=list(workbook['MSCI - factor totret index'].values)
    if rows[2][1]!='Gross' or rows[3][1]!='USD' or rows[6][1]!='USA Standard (Large+Mid Cap)':
        raise ValueError('Unexpected MSCI units or index column')
    levels={}
    for row in rows[7:]:
        try: date=datetime.strptime(str(row[0]).strip(),'%b %d, %Y')
        except ValueError: continue
        month=date.strftime('%Y-%m')
        if month in levels: raise ValueError('Duplicate MSCI month')
        value=float(str(row[1]).replace(',',''))
        if not np.isfinite(value) or value<=0: raise ValueError('Invalid index level')
        levels[month]=value
    workbook.close()
    return levels


def run(root):
    root=Path(root); out=root/'outputs/part_2/broad_market'
    path=out/'market_returns.csv'
    if not path.exists(): raise ValueError('Run market_portfolio first')
    portfolio=list(csv.DictReader(path.open()))
    expected=[f'{1999+i//12:04d}-{i%12+1:02d}' for i in range(240)]
    if [r['month'] for r in portfolio]!=expected: raise ValueError('Expected Jan 1999–Dec 2018 returns')
    levels=read_levels(root/'data/raw/ff_msci_shared.xlsx')
    months=['1998-12']+expected
    if any(m not in levels for m in months): raise ValueError('Missing MSCI monthly levels')
    market=np.array([levels[b]/levels[a]-1 for a,b in zip(months[:-1],months[1:])])
    proxy=np.array([float(r['return']) for r in portfolio])
    if not np.isfinite(proxy).all(): raise ValueError('Missing proxy return')
    corr=float(np.corrcoef(market,proxy)[0,1]); spread=proxy-market
    tracking=float(np.std(spread,ddof=1)*np.sqrt(12))
    agree=float(np.mean(np.sign(proxy)==np.sign(market)))
    wealth_proxy=np.r_[1,np.cumprod(1+proxy)]; wealth_market=np.r_[1,np.cumprod(1+market)]
    save_csv(out/'benchmark_comparison.csv',['month','market_proxy_return','msci_usa_gross_return','return_difference','market_proxy_wealth','msci_usa_wealth'],[[m,a,b,a-b,wa,wb] for m,a,b,wa,wb in zip(expected,proxy,market,wealth_proxy[1:],wealth_market[1:])])
    save_csv(out/'benchmark_metrics.csv',['metric','value'],[['months',240],['monthly_pearson_correlation',corr],['same_return_sign_share',agree],['mean_monthly_difference',spread.mean()],['annualized_tracking_error',tracking],['proxy_terminal_wealth',wealth_proxy[-1]],['msci_terminal_wealth',wealth_market[-1]]])
    dates=[datetime.strptime(m,'%Y-%m') for m in months]; dates=[d.replace(day=calendar.monthrange(d.year,d.month)[1]) for d in dates]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none'})
    blue,gray,ink='#246B83','#87949E','#213444'
    fig,ax=plt.subplots(figsize=(12.8,6.7));fig.subplots_adjust(left=.08,right=.91,top=.75,bottom=.22)
    ax.plot(dates,wealth_proxy,color=blue,lw=2.3,label='Market proxy (score-weighted)')
    ax.plot(dates,wealth_market,color=gray,lw=2.3,label='MSCI USA (gross total return, USD)')
    for values,color in [(wealth_proxy,blue),(wealth_market,gray)]:
        ax.annotate(f'${values[-1]:.2f}',(dates[-1],values[-1]),xytext=(9,0),textcoords='offset points',va='center',color=color,weight='bold')
    ax.set_ylim(bottom=0);ax.set_ylabel('Value of $1');ax.set_xlabel('Return month',labelpad=12)
    ax.xaxis.set_major_locator(mdates.YearLocator(2));ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'));style(ax)
    ax.legend(frameon=False,loc='upper left',fontsize=10)
    fig.text(.08,.92,'Growth of $1: market proxy vs. MSCI USA',fontsize=22,weight='bold',color=ink)
    fig.text(.08,.85,'Same starting capital on Dec 31, 1998 | Monthly returns: Jan 1999–Dec 2018',color='#546471')
    fig.text(.08,.115,'Proxy: monthly score weights × winsorized next-month stock returns; Pb = 0.50 retained. MSCI: gross total-return index in USD.',fontsize=9,color='#65727C')
    fig.text(.08,.075,'Source: shared security_characteristics.csv and ff_msci_shared.xlsx. Values compound monthly returns; no transaction costs.',fontsize=9,color='#65727C')
    fig.text(.08,.035,'Different universes, weighting rules and return cleaning can produce lasting performance differences.',fontsize=9,color='#65727C')
    for ext in ['png','svg']:fig.savefig(out/f'msci_growth_comparison.{ext}',dpi=220,facecolor='white')
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,8));fig.subplots_adjust(left=.13,right=.95,top=.75,bottom=.23)
    ax.scatter(market,proxy,s=24,color=blue,alpha=.6,edgecolors='none')
    limit=max(abs(np.r_[market,proxy]))+.025
    ax.plot([-limit,limit],[-limit,limit],color=gray,ls='--',lw=1,label='Equal monthly returns')
    ax.axhline(0,color='#DFE5E9',lw=.7);ax.axvline(0,color='#DFE5E9',lw=.7)
    ax.set_xlim(-limit,limit);ax.set_ylim(-limit,limit);ax.set_aspect('equal',adjustable='box')
    ax.xaxis.set_major_formatter(PercentFormatter(1,0));ax.yaxis.set_major_formatter(PercentFormatter(1,0))
    ax.set_xlabel('MSCI USA monthly return',labelpad=10);ax.set_ylabel('Market proxy monthly return',labelpad=10);style(ax)
    ax.legend(frameon=False,loc='lower right',fontsize=10)
    fig.text(.10,.93,'Do monthly returns move together?',fontsize=21,weight='bold',color=ink)
    fig.text(.10,.865,f'Pearson correlation: {corr:.3f} | Same sign in {agree:.1%} of months',color=blue,fontsize=12)
    fig.text(.10,.815,'240 paired months | Jan 1999–Dec 2018',color='#546471')
    fig.text(.10,.12,'One dot per realized return month; both axes use the same scale.',fontsize=9,color='#65727C')
    fig.text(.10,.08,'Source: supplied stock panel (winsorized returns) and MSCI USA gross USD index.',fontsize=9,color='#65727C')
    fig.text(.10,.04,'The dashed line indicates equal returns, not an estimated regression.',fontsize=9,color='#65727C')
    for ext in ['png','svg']:fig.savefig(out/f'msci_monthly_scatter.{ext}',dpi=220,facecolor='white')
    plt.close(fig)
    report=root/'reports/part_2/broad_market/benchmark_comparison.md'
    report.write_text(f'''# Part 2B: comparison with MSCI USA

![Growth of one dollar](../../../outputs/part_2/broad_market/msci_growth_comparison.png)

Both series start at $1 on December 31, 1998. By December 2018, the market proxy reaches ${wealth_proxy[-1]:.2f}, compared with ${wealth_market[-1]:.2f} for MSCI USA. The cumulative chart shows common market movements as well as a substantial long-run performance difference.

![Monthly return comparison](../../../outputs/part_2/broad_market/msci_monthly_scatter.png)

Monthly returns show a clear positive relationship, with the scatter broadly following the y = x line. Their correlation is {corr:.3f}, and they move in the same direction in {agree:.1%} of months. The cumulative paths also show similar rises and falls, despite different terminal values. This strengthens our confidence that the supplied data capture broad US equity-market movements and that the returns are broadly reasonable. It does not verify every stock return. Differences in stock coverage, score-based weighting and winsorization may contribute to the performance gap; the comparison does not isolate these effects.

## Method

The shared workbook's `MSCI - factor totret index` sheet provides `USA Standard (Large+Mid Cap)` index levels, explicitly labeled Gross and USD. We convert consecutive monthly levels into returns using L(t)/L(t−1)−1, retaining December 1998 to calculate January 1999. Month-end trading dates are aligned by calendar month. The proxy is joined on realized return month, not formation month. All 240 months are present; no dates are dropped. Proxy returns retain the previously agreed monthly P1/P99 cleaning; MSCI returns are not winsorized.

The main figure compounds both return series with the same initial value. The supplementary scatter uses equal horizontal and vertical scales and an equality line, not a fitted regression. Pearson correlation measures monthly co-movement; tracking error uses sample standard deviation (ddof=1) multiplied by sqrt(12). All figures and their paired-return/metric tables are in `outputs/part_2/broad_market/`.

Run `python run_all.py --task benchmark_comparison` after `market_portfolio`, or run `--all` in dependency order. Sources: shared `data/raw/ff_msci_shared.xlsx` and the registered security panel. This analysis does not modify either source.

[Back to Part 2B](README.md)
''')
    print(f'correlation={corr:.6f}; same sign={agree:.4%}; tracking error={tracking:.4%}; terminal wealth proxy/MSCI={wealth_proxy[-1]:.6f}/{wealth_market[-1]:.6f}')
