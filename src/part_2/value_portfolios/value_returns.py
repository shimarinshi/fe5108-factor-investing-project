"""Part 2C: value weighting, geometric annualized returns and volatility."""
import calendar
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from src.part_2.broad_market.market_portfolio import portfolio, save_csv, style

STRATEGIES = ('value_top20_equal', 'value_score', 'value_score_times_size')
LABELS = ('Top 20% · equal weight', 'B/P score weighted', 'B/P × size score weighted', 'Broad-market proxy')
COLORS = ('#246B83', '#BD503B', '#8A733B', '#87949E')


def value_weights(pb, size):
    pb, size = np.asarray(pb, float), np.asarray(size, float)
    if pb.shape != size.shape or not len(pb) or not np.isfinite(pb).all() or not np.isfinite(size).all():
        raise ValueError('Value portfolios require finite matching score arrays.')
    if ((pb < .01) | (pb > 1) | (size < .01) | (size > 1)).any():
        raise ValueError('Scores must be in [0.01, 1.00].')
    if not np.allclose(pb * 100, np.round(pb * 100), atol=1e-8, rtol=0):
        raise ValueError('Reverse-score convention requires the supplied 0.01 grid.')
    bp = 1.01 - pb
    # Include the entire boundary tie group, rather than choose stocks by ID.
    cutoff = np.sort(pb)[int(np.ceil(.2 * len(pb))) - 1]
    selected = (pb <= cutoff).astype(float)
    weights = [portfolio(s, np.zeros(len(pb)))[0] for s in (selected, bp, bp * size)]
    return weights, bp


def annualized_return(returns):
    returns = np.asarray(returns, float)
    if not len(returns) or not np.isfinite(returns).all() or (returns <= -1).any():
        raise ValueError('Compounding requires finite returns greater than -100%.')
    return float(np.expm1(np.log1p(returns).sum() * 12 / len(returns)))


def annualized_volatility(returns):
    returns = np.asarray(returns, float)
    if returns.ndim != 1 or len(returns) < 2 or not np.isfinite(returns).all():
        raise ValueError('Volatility requires at least two finite monthly returns.')
    return float(np.std(returns, ddof=1) * np.sqrt(12))


def run(root):
    root = Path(root)
    clean_path = root/'data/processed/security_returns/winsorized_returns.csv'
    market_path = root/'outputs/part_2/broad_market/market_returns.csv'
    if not clean_path.exists() or not market_path.exists():
        raise ValueError('Run return_distribution and market_portfolio first.')
    with clean_path.open() as f:
        clean_rows = list(csv.DictReader(f))
    clean = {(r['stock_id'], r['formation_month']): r for r in clean_rows}
    if len(clean) != len(clean_rows): raise ValueError('Duplicate cleaned return keys.')
    with market_path.open() as f:
        market_rows = list(csv.DictReader(f))
    expected = [f'{1999+i//12:04d}-{i%12+1:02d}' for i in range(240)]
    if [r['month'] for r in market_rows] != expected: raise ValueError('Market window mismatch.')
    groups = defaultdict(list)
    with (root/'data/raw/security_characteristics.csv').open() as f:
        for r in csv.DictReader(f):
            month = datetime.strptime(r['date'], '%m/%d/%Y').strftime('%Y-%m')
            if '1998-12' <= month <= '2018-11': groups[month].append(r)
    if sorted(groups) != [r['formation_month'] for r in market_rows]:
        raise ValueError('Formation window mismatch.')
    out = root/'outputs/part_2/value_portfolios'; out.mkdir(parents=True, exist_ok=True)
    returns, holdings, diagnostics, robustness = [], [], [], []
    for benchmark in market_rows:
        month, rm = benchmark['formation_month'], benchmark['month']
        y, m = map(int, month.split('-'))
        if rm != f'{y+m//12:04d}-{m%12+1:02d}': raise ValueError('Forward timing mismatch.')
        for include_half in (False, True):
            rows = [r for r in groups[month] if include_half or float(r['Pb']) != .5]
            matched = [clean[(r['stock_id'], month)] for r in rows]
            if any(c['return_month'] != rm or float(c['raw_return']) != float(r['R1M_Usd']) for r,c in zip(rows, matched)):
                raise ValueError('Raw/clean input or return timing mismatch.')
            outcomes = np.array([float(c['winsorized_return']) for c in matched])
            if not np.isfinite(outcomes).all(): raise ValueError('Missing forward outcomes.')
            size = np.array([float(r['Mkt_Cap_3M_Usd']) for r in rows])
            weights, bp = value_weights([float(r['Pb']) for r in rows], size)
            for strategy, w in zip(STRATEGIES, weights):
                if (w < 0).any() or not np.isclose(w.sum(), 1): raise ValueError('Invalid weights.')
                result = [strategy, rm, float(w @ outcomes)]
                if include_half:
                    robustness.append(result)
                    continue
                returns.append(result)
                holdings.extend([strategy, month, r['stock_id'], weight] for r,weight in zip(rows,w) if weight > 0)
                diagnostics.append([strategy, month, len(rows), int((w>0).sum()), float(w.sum()), float(w@bp), float(w@size)])
    save_csv(out/'value_returns.csv', ['strategy','month','return'], returns)
    save_csv(out/'portfolio_weights.csv', ['strategy','formation_month','stock_id','weight'], holdings)
    final_month = market_rows[-1]['formation_month']
    final_holdings = []
    for strategy in STRATEGIES:
        selected = [r for r in holdings if r[0] == strategy and r[1] == final_month and r[3] > 0]
        if len({r[2] for r in selected}) != len(selected):
            raise ValueError('Duplicate final-period holdings.')
        if not np.isclose(sum(r[3] for r in selected), 1):
            raise ValueError('Final-period weights do not sum to one.')
        final_holdings.append([strategy, final_month, market_rows[-1]['month'], len(selected), max(r[3] for r in selected)])
    save_csv(out/'final_period_holdings.csv',
             ['strategy','formation_month','return_month','stocks_held','maximum_single_stock_weight'], final_holdings)
    holdings_table = '\n'.join(f'| {label} | {r[3]:,} | {r[4]:.4%} |' for label,r in zip(LABELS,final_holdings))

    save_csv(out/'monthly_diagnostics.csv', ['strategy','formation_month','eligible_stocks','held_stocks','weight_sum','weighted_bp_score','weighted_size_score'], diagnostics)
    save_csv(out/'robustness_including_pb_half.csv', ['strategy','month','return'], robustness)
    series = [np.array([r[2] for r in returns if r[0]==s]) for s in STRATEGIES]
    series.append(np.array([float(r['return']) for r in market_rows]))
    # Match the persisted monthly-return precision before compounding on any platform.
    series = [np.round(r, 12) for r in series]
    volatility = [annualized_volatility(r) for r in series]
    save_csv(out/'annualized_volatility.csv',
             ['strategy','months','monthly_sample_standard_deviation','annualized_standard_deviation'],
             [[name,len(r),v/np.sqrt(12),v] for name,r,v in zip((*STRATEGIES,'market_score_weighted'),series,volatility)])
    volatility_table = '\n'.join(f'| {label} | {v:.2%} |' for label,v in zip(LABELS,volatility))
    volatility_winner = LABELS[int(np.argmax(volatility))]
    paths = [np.r_[1, np.cumprod(1+r)] for r in series]
    metrics = [[s, 240, annualized_return(r), float(p[-1])] for s,r,p in zip((*STRATEGIES,'market_score_weighted'),series,paths)]
    save_csv(out/'annualized_returns.csv', ['strategy','months','geometric_annualized_return','ending_wealth'], metrics)
    save_csv(out/'cumulative_growth.csv', ['month',*STRATEGIES,'market_score_weighted'], [[m,*v] for m,v in zip(['1998-12',*expected],zip(*paths))])
    robustness_metrics = [[s, annualized_return([r[2] for r in robustness if r[0]==s])] for s in STRATEGIES]
    save_csv(out/'robustness_annualized_returns.csv', ['strategy','geometric_annualized_return'], robustness_metrics)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none'})
    dates = [datetime.strptime(m,'%Y-%m') for m in ['1998-12',*expected]]
    dates = [d.replace(day=calendar.monthrange(d.year,d.month)[1]) for d in dates]
    fig, ax = plt.subplots(figsize=(13.8,8.2))
    fig.subplots_adjust(left=.08,right=.97,top=.69,bottom=.19)
    for i,(label,color,path) in enumerate(zip(LABELS,COLORS,paths)):
        ax.plot(dates,path,color=color,lw=2 if i<3 else 1.8,ls='-' if i<3 else '--')
    ax.set_ylim(bottom=0); ax.set_ylabel('Value of an initial $1',color='#213444')
    ax.set_xlabel('Return month',labelpad=10,color='#213444')
    ax.xaxis.set_major_locator(mdates.YearLocator(2)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    style(ax)
    fig.text(.08,.94,'Value portfolios: growth of $1',fontsize=24,weight='bold',color='#213444')
    fig.text(.08,.89,'Jan 1999–Dec 2018 | Monthly rebalancing | Geometric annualized returns (CAGR)',color='#546471')
    for i,(label,color,metric) in enumerate(zip(LABELS,COLORS,metrics)):
        x=.08+i*.232
        fig.text(x,.825,label,fontsize=10.5,color=color,weight='bold')
        fig.text(x,.775,f'{metric[2]:.2%} per year',fontsize=17,color=color,weight='bold')
        fig.text(x,.735,f'Ending value: ${metric[3]:.2f}',fontsize=10.5,color='#546471')
    fig.text(.08,.11,'Value portfolios exclude Pb = 0.50; the broad-market proxy retains all stocks. Returns use monthly P1/P99 winsorization.',fontsize=9,color='#65727C')
    fig.text(.08,.07,'B/P score = 1.01 − supplied P/B score; top-20% cutoff includes ties. All portfolios are long-only, fully invested, before costs.',fontsize=9,color='#65727C')
    fig.text(.08,.03,'Source: instructor-provided security panel; formation months Dec 1998–Nov 2018. Initial investment: Dec 31, 1998.',fontsize=9,color='#65727C')
    for ext in ('png','svg'): fig.savefig(out/f'value_growth_comparison.{ext}',dpi=220,facecolor='white')
    plt.close(fig)
    table='\n'.join(f'| {label} | {r[2]:.2%} | ${r[3]:.2f} |' for label,r in zip(LABELS,metrics))
    winner=int(np.argmax([m[2] for m in metrics]))
    report=root/'reports/part_2/value_portfolios/README.md'; report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(f'''# Part 2C: value portfolios

## 1. Annualized returns

Each month, we exclude Pb = 0.50 and reverse the supplied 0.01–1.00 P/B score as B/P score = 1.01 − Pb, without reranking the remaining stocks. This reverses the percentile scale; it does not recover raw B/P. We construct (1) an equal-weight portfolio of the highest B/P 20%, (2) weights proportional to B/P scores, and (3) weights proportional to B/P scores times market-cap scores. The first rule selects ceil(20% × eligible stocks), including all ties at its boundary. Each rule is normalized to sum to one.

Formation months December 1998–November 2018 produce 240 monthly returns for January 1999–December 2018. We use the Part 2A winsorized forward returns, rebalance monthly and assume no transaction costs. The Part 2B market proxy is unchanged, including its retention of Pb = 0.50.

![Growth of one dollar across four portfolios](../../../outputs/part_2/value_portfolios/value_growth_comparison.png)

| Portfolio | Annualized return (CAGR) | Ending value of $1 |
|---|---:|---:|
{table}

Annualized return is geometric: [product of (1 + monthly return)]^(12/240) − 1. The chart starts at $1 on December 31, 1998 and compounds the same monthly returns.

**{LABELS[winner]} has the highest annualized return.** One possible explanation is that it concentrates entirely on the cheapest stocks, whereas the other methods still allocate capital to relatively more expensive stocks, potentially diluting the value tilt. Equal weighting also avoids giving larger stocks additional weight within the selected group. This comparison does not isolate the effect of equal weighting from that of stock selection. Comparisons with the market also reflect the different treatment of Pb = 0.50.

As a sensitivity check, retaining Pb = 0.50 gives annualized returns of {robustness_metrics[0][1]:.2%}, {robustness_metrics[1][1]:.2%} and {robustness_metrics[2][1]:.2%}, respectively. These observations remain of uncertain interpretation; this check does not validate their P/B values.

Run `python run_all.py --task value_returns` after `return_distribution` and `market_portfolio`, or use `--all`. Code: `src/part_2/value_portfolios/value_returns.py`. Tables and PNG/SVG figure: `outputs/part_2/value_portfolios/`. Security weights are generated locally; monthly diagnostics record holdings, weight sums and weighted characteristic scores.

## 2. Annualized standard deviation

| Portfolio | Annualized standard deviation |
|---|---:|
{volatility_table}

We use the same 240 monthly returns (January 1999–December 2018). Annualized standard deviation equals the monthly sample standard deviation (ddof = 1), calculated around the arithmetic mean, times sqrt(12). This is the conventional square-root-of-time annualization; the return comparison above uses geometric compounding.

**{volatility_winner} has the highest volatility**, at {max(volatility):.2%}, versus {volatility[3]:.2%} for the broad-market proxy. The top-20% rule holds a narrower set of value stocks and has greater exposure to smaller-ranked stocks. These features plausibly contribute to its higher volatility; fewer holdings alone do not determine portfolio risk, which also depends on individual stock volatility and co-movement. Its higher realized return therefore comes with greater fluctuations in this sample. The available comparison does not isolate each source of risk.

Underlying table: `outputs/part_2/value_portfolios/annualized_volatility.csv`; regenerated by the same `value_returns` task. No additional figure is used for this question.

## 3. Final-period holdings

Formation month: November 2018; corresponding return month: December 2018. Counts include strictly positive weights after the baseline Pb = 0.50 exclusion. These are formation weights, before subsequent return-driven drift.

| Value portfolio | Stocks held | Maximum single-stock weight |
|---|---:|---:|
{holdings_table}

Source: the generated security-level weights. Reproducible summary: `outputs/part_2/value_portfolios/final_period_holdings.csv`. The top-20% boundary includes ties, as specified above. The top-20% equal-weighted portfolio holds the fewest stocks ({final_holdings[0][3]:,}) and has the highest single-stock weight ({final_holdings[0][4]:.4%}). This is consistent with allocating capital equally across a much smaller set of stocks than the other two portfolios, which each hold {final_holdings[1][3]:,} stocks.

Multiplying B/P scores by market-cap scores increases the maximum single-stock weight from {final_holdings[1][4]:.4%} to {final_holdings[2][4]:.4%}. Stocks with high scores on both characteristics receive larger weights, making the largest position more concentrated than under B/P weighting alone. However, its maximum weight remains below that of the top-20% portfolio.


[Back to Part 2](../README.md)
''')
    print(table)
    print(volatility_table)
    print(holdings_table)
    print('Including Pb = 0.50:', robustness_metrics)

if __name__ == '__main__':
    run(Path(__file__).resolve().parents[3])
