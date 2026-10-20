"""Inspect standardized P/B concentration and its association with low Bv ranks."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, StrMethodFormatter


def run(root):
    root=Path(root)
    with (root/'data/raw/security_characteristics.csv').open(newline='') as stream:
        rows=list(csv.DictReader(stream))
    pb=np.array([float(r['Pb']) for r in rows])
    bv=np.array([float(r['Bv']) for r in rows])
    assert np.isfinite(pb).all() and np.isfinite(bv).all()
    mask=pb==.5
    output=root/'outputs/price_to_book_distribution'
    output.mkdir(parents=True,exist_ok=True)
    values,counts=np.unique(pb,return_counts=True)
    with (output/'pb_frequency.csv').open('w',newline='') as stream:
        w=csv.writer(stream); w.writerow(['standardized_pb','stock_month_count']); w.writerows(zip(values,counts))
    thresholds=[.01,.05,.10]
    stats=[]
    for t in thresholds:
        for label,selection in [('Pb = 0.50',mask),('Other Pb values',~mask)]:
            n=int(selection.sum()); low=int((bv[selection]<=t).sum())
            stats.append((t,label,n,low,low/n))
    with (output/'low_book_value_comparison.csv').open('w',newline='') as stream:
        w=csv.writer(stream); w.writerow(['bv_threshold','group','observations','at_or_below_threshold','share']); w.writerows(stats)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'})
    fig,axes=plt.subplots(1,2,figsize=(14,7))
    fig.subplots_adjust(left=.075,right=.975,top=.73,bottom=.27,wspace=.26)
    blue,red,ink,gray='#246B83','#BD503B','#213444','#546471'
    axes[0].bar(values,counts,width=.008,color=[red if v==.5 else blue for v in values])
    axes[0].set_xlim(0,1.01); axes[0].set_ylim(0,12000)
    axes[0].set_xlabel('Standardized price-to-book score',labelpad=12,color=ink)
    axes[0].set_ylabel('Stock-month observations',labelpad=10,color=ink)
    axes[0].yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    axes[0].set_title('A. Distribution of standardized P/B',loc='left',pad=24,color=ink,weight='bold',fontsize=13)
    axes[0].annotate(f'Pb = 0.50\n{mask.sum():,} observations ({mask.mean():.2%})',xy=(.5,int(mask.sum())),xytext=(.66,10300),color=red,fontsize=10,arrowprops={'arrowstyle':'-','color':red},va='center')
    x=np.arange(3)
    a=[r[4] for r in stats if r[1]=='Pb = 0.50']
    b=[r[4] for r in stats if r[1]=='Other Pb values']
    bars1=axes[1].bar(x-.18,a,.34,color=red,label='Pb = 0.50')
    bars2=axes[1].bar(x+.18,b,.34,color=blue,label='Other Pb values')
    for bars in [bars1,bars2]:
        axes[1].bar_label(bars,labels=[f'{v.get_height():.1%}' if v.get_height()>=.001 else f'{v.get_height():.3%}' for v in bars],padding=5,fontsize=10,color=ink)
    axes[1].set_ylim(0,.78)
    axes[1].set_xticks(x,['Bv ≤ 0.01','Bv ≤ 0.05','Bv ≤ 0.10'])
    axes[1].yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
    axes[1].set_ylabel('Share within each P/B group',labelpad=10,color=ink)
    axes[1].set_xlabel('Low book-equity rank thresholds (nested)',labelpad=12,color=ink)
    axes[1].set_title('B. Are the 0.50 scores linked to low Bv?',loc='left',pad=24,color=ink,weight='bold',fontsize=13)
    axes[1].legend(frameon=False,loc='upper left',ncol=2,fontsize=10)
    for ax in axes:
        ax.grid(axis='y',color='#DFE5E9',lw=.7); ax.set_axisbelow(True)
        ax.tick_params(length=0,labelcolor=gray)
        for s in ax.spines.values(): s.set_visible(False)
    fig.text(.075,.93,'P/B concentration and low book equity',fontsize=23,weight='bold',color=ink)
    fig.text(.075,.865,f'{len(rows):,} stock-month observations | Nov 1998–Mar 2019 formation months',fontsize=12,color=gray)
    fig.text(.075,.17,'Panel A shows counts at each recorded score (0.01 increments). Panel B compares cumulative shares within each group.',fontsize=10,color=gray)
    fig.text(.075,.12,'Very low Bv is defined as a score ≤ 0.05; 0.01 and 0.10 provide sensitivity checks. Thresholds use the supplied ranks.',fontsize=10,color=gray)
    fig.text(.075,.075,'Source: Instructor-provided security_characteristics.csv. All stock-month records are pooled; repeated stocks count in each month.',fontsize=9,color='#65727C')
    fig.text(.075,.035,'Pb and Bv are standardized scores, not raw ratios or amounts. A low Bv rank does not establish negative book equity.',fontsize=9,color='#65727C')
    for ext in ['png','svg']: fig.savefig(output/f'price_to_book_distribution.{ext}',dpi=220,facecolor='white')
    plt.close(fig)
    report=f'''# Standardized price-to-book distribution

![P/B distribution and low book equity](../outputs/price_to_book_distribution/price_to_book_distribution.png)

The standardized P/B distribution has a clear spike at 0.50, with {mask.sum():,} stock-month observations ({mask.mean():.2%} of the sample). The adjacent scores, 0.49 and 0.51, contain {int((pb==.49).sum()):,} and {int((pb==.51).sum()):,} observations, respectively.

We define very low book equity as a supplied Bv score of 0.05 or below and also check thresholds of 0.01 and 0.10. Among observations with Pb = 0.50, 5,976 (58.6%) meet the 0.05 threshold, compared with 3.0% of other observations. At thresholds of 0.01 and 0.10, the corresponding shares are 28.5% versus 0.004%, and 61.8% versus 8.2%. Thus, the 0.50 concentration is strongly associated with low book-equity ranks, but not every observation in this group has low Bv: 41.4% lie above 0.05.

Fama–French HML portfolios require positive book equity. This motivates checking whether the 0.50 spike reflects special treatment of stocks with nonpositive or otherwise unusable book equity. The association supports investigating this explanation, but does not confirm it: Bv is a percentile score, so its sign does not reveal the sign of raw book equity. Ordinary mid-ranked observations may also share the rounded score of 0.50. For subsequent value portfolios, our baseline will exclude stock-month observations with Pb = 0.50, with their inclusion as a robustness check. This is a conservative treatment of an ambiguous valuation signal, not a claim that these stocks have negative book equity. It may exclude valid mid-ranked observations. The rule applies to the affected month, not the entire stock history; portfolio performance comparisons remain to be implemented in Parts 2B–2D.

The figure pools all observations from November 1998 to March 2019. Panel A uses one bar per recorded P/B score rather than a smoothed density, preserving the spike. Panel B uses grouped bars with a common percentage axis; each percentage uses its own P/B group's observations as denominator. Thresholds are nested, not mutually exclusive, and use the supplied rounded scores rather than newly calculated full-sample quantiles. The unit is a stock-month, not a unique company.

Source: `data/raw/security_characteristics.csv`. HML methodology: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html

Producer: `src/price_to_book_distribution.py`; run `python run_all.py --task price_to_book_distribution`. Figure (PNG/SVG) and both underlying tables are in `outputs/price_to_book_distribution/`. No observations or features are changed by this diagnostic.
'''
    (root/'reports/price_to_book_distribution.md').write_text(report)
    print(stats)
