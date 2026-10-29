"""FE5108 Part 4: analyze instructor-provided NVDA and NVDL daily total returns."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import hashlib

def run(input_path, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    raw = pd.read_excel(input_path, sheet_name="NVDL", header=4, usecols="A:C")
    raw.columns = ["date", "NVDA", "NVDL"]
    raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
    df = raw.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    df = df.loc[df.date.between("2024-02-01", "2024-08-31")].copy()
    for name in ["NVDA", "NVDL"]:
        df[name] = pd.to_numeric(df[name], errors="raise")
    if len(df) != 147 or df.date.duplicated().any() or df[["NVDA","NVDL"]].isna().any().any():
        raise ValueError("Unexpected missing, duplicate, or incomplete observations")
    if not np.isfinite(df[["NVDA","NVDL"]].to_numpy()).all() or (df[["NVDA","NVDL"]] <= -1).any().any():
        raise ValueError("Invalid daily return")
    df.to_csv(out/"daily_returns.csv", index=False, date_format="%Y-%m-%d", float_format="%.12g")
    risks=[]
    for name in ["NVDA","NVDL"]:
        x=df[name].to_numpy()
        q=np.quantile(x,0.05,method="linear")
        risks.append({"asset":name,"observations":len(x),"daily_volatility":np.std(x,ddof=1),
                      "return_5th_percentile":q,"var_95_loss":-q,
                      "cvar_95_loss":-np.mean(x[x<=q]),"tail_observations":int(sum(x<=q))})
    risk=pd.DataFrame(risks)
    risk.to_csv(out/"daily_risk.csv",index=False,float_format="%.12g")
    x=df.NVDA.to_numpy(); y=df.NVDL.to_numpy()
    fit=stats.linregress(x,y)
    X=np.column_stack([np.ones(len(x)),x])
    coef=np.array([fit.intercept,fit.slope])
    resid=y-X@coef
    se=np.sqrt(np.diag(np.linalg.inv(X.T@X)*np.dot(resid,resid)/(len(x)-2)))
    critical=stats.t.ppf(.975,len(x)-2)
    reg=pd.DataFrame({"coefficient":["intercept","NVDA_slope"],"estimate":coef,"standard_error":se,
                      "ci_95_lower":coef-critical*se,"ci_95_upper":coef+critical*se,
                      "t_stat":coef/se})
    reg.to_csv(out/"regression.csv",index=False,float_format="%.12g")
    sums=[]
    for label,g in list(df.groupby(df.date.dt.strftime("%Y-%m"),sort=True))+[("2024-02_to_2024-08",df)]:
        a=np.prod(1+g.NVDA.to_numpy())-1
        b=np.prod(1+g.NVDL.to_numpy())-1
        sums.append({"period":label,"days":len(g),"NVDA":a,"NVDL":b,"twice_NVDA":2*a,"difference_from_twice":b-2*a})
    pd.DataFrame(sums).to_csv(out/"cumulative_returns.csv",index=False,float_format="%.12g")
    examples=pd.DataFrame([{"asset":"NVDA","day_1":.10,"day_2":-.09,"two_day_return":1.1*.91-1},
                           {"asset":"NVDL_ideal_2x","day_1":.20,"day_2":-.18,"two_day_return":1.2*.82-1}])
    examples.to_csv(out/"two_day_example.csv",index=False,float_format="%.12g")
    fig,ax=plt.subplots(figsize=(9,4.5))
    for name,color in [("NVDA","#246B83"),("NVDL","#BD503B")]:
        wealth=np.r_[1,(1+df[name]).cumprod().to_numpy()]
        dates=pd.concat([pd.Series([df.date.min()-pd.Timedelta(days=1)]),df.date],ignore_index=True)
        ax.plot(dates,wealth,label=name,color=color,lw=1.8)
    ax.set(title="NVDA and NVDL: cumulative growth of $1",ylabel="Value of $1",xlabel="Date")
    ax.grid(alpha=.25); ax.legend(); fig.text(.12,.01,"Source: instructor-provided daily total returns; Feb–Aug 2024.",fontsize=9)
    fig.tight_layout(rect=(0,.04,1,1)); fig.savefig(out/"cumulative_growth.png",dpi=180); plt.close(fig)
    print("risk\n",risk.to_string(index=False))
    print("regression\n",reg.to_string(index=False))
    print("r2",fit.rvalue**2,"annualized intercept",fit.intercept*252)
    print("returns\n",pd.DataFrame(sums).to_string(index=False))
    print("input_sha256",hashlib.sha256(Path(input_path).read_bytes()).hexdigest())

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    run(args.input,args.output)

