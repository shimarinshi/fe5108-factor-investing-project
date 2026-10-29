"""Additional Part 5 exhibits using the saved numerical outputs."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from scipy.stats import t

def run(out):
    out=Path(out)
    plt.rcParams.update({"font.family":"DejaVu Sans","axes.titlecolor":"#213444","axes.labelcolor":"#213444"})
    r=pd.read_csv(out/"regression.csv").set_index("term").loc[["RF","Mkt_RF","HML","SMB"]]
    vals=r.coefficient.to_numpy(); delta=t.ppf(.975,338)*r.standard_error.to_numpy()
    fig,ax=plt.subplots(figsize=(8,4.8))
    labels=["Risk-free rate","Market excess","Value (HML)","Size (SMB)"]
    ax.errorbar(vals,np.arange(4),xerr=delta,fmt="o",color="#246B83",ecolor="#BD503B",capsize=4,label="OLS estimate and 95% confidence interval")
    ax.axvline(0,color="#65727C",lw=1,ls="--")
    ax.set_yticks(np.arange(4),labels);ax.invert_yaxis()
    ax.set(title="MSCI USA Value: estimated factor exposures",xlabel="Regression coefficient",ylabel="Factor")
    ax.grid(axis="x",alpha=.2);ax.legend(fontsize=8,loc="lower right")
    fig.text(.12,.01,"Source: instructor MSCI gross USD returns and French factors; Jan 1995–Jul 2023; conventional OLS.",fontsize=8)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(out/"factor_exposures.png",dpi=180);plt.close(fig)

    d=pd.read_csv(out/"monthly_panel.csv")
    records=[]
    for label,col in [("Value","Value_active"),("Minimum volatility","Minimum_volatility_active"),("Equal weight","Equal_weight_active"),("Momentum","Momentum_active"),("Multifactor","Multi_active")]:
        a=d[col]
        records.append({"strategy":label,"annualized_active_return":12*a.mean(),"annualized_tracking_error":a.std(ddof=1)*np.sqrt(12),"information_ratio":12*a.mean()/(a.std(ddof=1)*np.sqrt(12))})
    tbl=pd.DataFrame(records);tbl.to_csv(out/"component_active_metrics.csv",index=False,float_format="%.12g",lineterminator="\n")
    fig,ax=plt.subplots(figsize=(9,5))
    colors=["#246B83"]*4+["#BD503B"]
    ax.scatter(tbl.annualized_tracking_error,tbl.annualized_active_return,s=75,c=colors,zorder=3)
    offsets=[(8,5),(8,5),(8,5),(8,-14),(8,5)]
    for row,offset in zip(tbl.itertuples(),offsets):
        ax.annotate(row.strategy,(row.annualized_tracking_error,row.annualized_active_return),xytext=offset,textcoords="offset points",fontsize=9)
    ax.axhline(0,color="#65727C",lw=1);ax.grid(alpha=.2)
    ax.xaxis.set_major_formatter(PercentFormatter(1));ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set(title="Active return versus tracking error",xlabel="Annualized tracking error versus MSCI USA",ylabel="Annualized arithmetic active return")
    ax.margins(x=.25,y=.22)
    fig.text(.1,.01,"Source: instructor MSCI gross USD index returns; Jan 1995–Jul 2023; no implementation costs.",fontsize=8)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(out/"active_return_vs_tracking_error.png",dpi=180);plt.close(fig)

    m=pd.read_csv(out/"replication_metrics.csv").set_index("portfolio")
    fig,axes=plt.subplots(1,3,figsize=(10,4.3))
    for ax,(column,title) in zip(axes,[("annualized_arithmetic_return","Annualized return"),("annualized_volatility","Annualized volatility"),("sharpe","Sharpe ratio")]):
        v=m.loc[["Value","Replication"],column].to_numpy()
        bars=ax.bar(["Value","Replication"],v,color=["#246B83","#BD503B"])
        ax.set_title(title);ax.grid(axis="y",alpha=.2);ax.set_axisbelow(True);ax.set_ylim(0,max(v)*1.28)
        if column!="sharpe": ax.yaxis.set_major_formatter(PercentFormatter(1))
        ax.bar_label(bars,labels=[f"{x:.2%}" if column!="sharpe" else f"{x:.3f}" for x in v],padding=3,fontsize=9)
    fig.suptitle("Value index and factor replication: in-sample comparison",color="#213444")
    fig.text(.07,.01,"Source: instructor MSCI gross USD levels and French factors; Jan 1995–Jul 2023; no costs.",fontsize=8)
    fig.tight_layout(rect=(0,.05,1,.94));fig.savefig(out/"replication_metrics_comparison.png",dpi=180);plt.close(fig)

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,required=True);run(parser.parse_args().output)
