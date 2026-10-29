"""Create Part 4 exhibits from the analysis output CSVs."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def run(out):
    out=Path(out)
    colors=["#246B83","#BD503B"]
    plt.rcParams.update({"font.family":"DejaVu Sans","axes.titlecolor":"#213444","axes.labelcolor":"#213444"})
    risk=pd.read_csv(out/"daily_risk.csv").set_index("asset")
    fig,ax=plt.subplots(figsize=(8,4.7))
    x=np.arange(3); width=.34
    labels=["Daily volatility","95% VaR","95% CVaR"]
    columns=["daily_volatility","var_95_loss","cvar_95_loss"]
    for i,asset in enumerate(["NVDA","NVDL"]):
        vals=risk.loc[asset,columns].astype(float).to_numpy()
        bars=ax.bar(x+(i-.5)*width,vals,width,label=asset,color=colors[i])
        ax.bar_label(bars,labels=[f"{v:.2%}" for v in vals],padding=3,fontsize=9)
    ax.set_xticks(x,labels); ax.set_ylabel("Daily risk measure")
    ax.set_title("NVDL had higher daily risk than NVDA")
    ax.yaxis.set_major_formatter(PercentFormatter(1)); ax.set_ylim(0,.18)
    ax.grid(axis="y",alpha=.2); ax.set_axisbelow(True); ax.legend(loc="upper left")
    fig.text(.12,.01,"Source: instructor-provided daily total returns, Feb–Aug 2024; 147 observations. Historical VaR and tail-average CVaR.",fontsize=8)
    fig.tight_layout(rect=(0,.05,1,1)); fig.savefig(out/"daily_risk_comparison.png",dpi=180); plt.close(fig)
    d=pd.read_csv(out/"daily_returns.csv")
    reg=pd.read_csv(out/"regression.csv").set_index("coefficient")["estimate"]
    fig,ax=plt.subplots(figsize=(7,5.5))
    ax.scatter(d.NVDA,d.NVDL,s=16,color=colors[0],alpha=.6,label="Daily observations")
    x=np.linspace(d.NVDA.min(),d.NVDA.max(),100)
    ax.plot(x,reg["intercept"]+reg["NVDA_slope"]*x,color=colors[1],lw=2,label=f"OLS: intercept {reg['intercept']:.4f}, slope {reg['NVDA_slope']:.4f}")
    ax.plot(x,2*x,color="#65727C",lw=1.3,ls="--",label="Ideal daily 2× return")
    ax.xaxis.set_major_formatter(PercentFormatter(1)); ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set(xlabel="NVDA daily total return",ylabel="NVDL daily total return",title="Daily returns follow approximately a 2× relationship")
    ax.grid(alpha=.2); ax.legend(fontsize=8)
    fig.text(.12,.01,"Source: instructor-provided daily total returns, Feb–Aug 2024; 147 paired observations.",fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1)); fig.savefig(out/"daily_return_regression.png",dpi=180); plt.close(fig)
    c=pd.read_csv(out/"cumulative_returns.csv").iloc[:7]
    fig,ax=plt.subplots(figsize=(9,4.8)); x=np.arange(len(c)); width=.26
    for i,(col,label,color) in enumerate([("NVDA","NVDA",colors[0]),("NVDL","NVDL",colors[1]),("twice_NVDA","2 × NVDA cumulative","#65727C")]):
        ax.bar(x+(i-1)*width,c[col],width,label=label,color=color)
    ax.axhline(0,color="#213444",lw=.8); ax.set_xticks(x,["Feb","Mar","Apr","May","Jun","Jul","Aug"])
    ax.yaxis.set_major_formatter(PercentFormatter(1)); ax.set(ylabel="Compounded monthly return",xlabel="2024",title="Monthly NVDL returns differ from twice NVDA returns")
    ax.grid(axis="y",alpha=.2); ax.set_axisbelow(True); ax.legend(fontsize=8,ncol=3)
    fig.text(.12,.01,"Source: instructor-provided daily total returns; monthly returns compounded over trading days.",fontsize=8)
    fig.tight_layout(rect=(0,.05,1,1)); fig.savefig(out/"monthly_return_comparison.png",dpi=180); plt.close(fig)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    run(parser.parse_args().output)


