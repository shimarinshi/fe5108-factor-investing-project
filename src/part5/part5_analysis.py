"""FE5108 Part 5: factor attribution, replication and active-risk analysis."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from scipy import stats

START, END = "1995-01", "2023-07"
COMPONENTS = ["Value", "Minimum_volatility", "Equal_weight", "Momentum"]
COLORS = ["#246B83", "#598fa0", "#a2b7bf", "#BD503B"]

def load_data(path):
    xls = pd.ExcelFile(path)
    raw = pd.read_excel(xls, sheet_name="MSCI - factor totret index", header=6, usecols="A:F")
    raw.columns = ["date", "Market"] + COMPONENTS
    raw["date"] = pd.to_datetime(raw["date"], format="%b %d, %Y", errors="coerce")
    raw = raw.dropna(subset=["date"]).copy()
    raw["month"] = raw["date"].dt.to_period("M")
    raw = raw.loc[raw["month"].between(pd.Period("1994-12"), pd.Period(END))].sort_values("month")
    if raw.month.duplicated().any(): raise ValueError("Duplicate MSCI months")
    for col in ["Market"] + COMPONENTS:
        raw[col] = pd.to_numeric(raw[col].astype(str).str.replace(",", "", regex=False), errors="raise")
    expected = pd.period_range("1994-12", END, freq="M")
    if not raw.month.reset_index(drop=True).equals(pd.Series(expected, name="month")): raise ValueError("Missing MSCI level month")
    if not np.isfinite(raw[["Market"] + COMPONENTS].to_numpy()).all() or (raw[["Market"] + COMPONENTS] <= 0).any().any():
        raise ValueError("Invalid MSCI index level")
    levels = raw.set_index("month")[["Market"] + COMPONENTS]
    returns = levels.pct_change(fill_method=None).iloc[1:]
    ff = pd.read_excel(xls, sheet_name="FF - 3 factor returns", header=3, usecols="A:E")
    ff.columns = ["date", "Mkt_RF", "SMB", "HML", "RF"]
    date_num = pd.to_numeric(ff["date"], errors="coerce")
    ff = ff.loc[date_num.between(199501,202307)].copy()
    ff["month"] = pd.PeriodIndex(pd.to_datetime(ff["date"].astype(int).astype(str), format="%Y%m"), freq="M")
    if ff.month.duplicated().any(): raise ValueError("Duplicate FF months")
    factors = ff.set_index("month")[["RF", "Mkt_RF", "HML", "SMB"]].apply(pd.to_numeric, errors="raise") / 100
    data = returns.join(factors, how="left")
    if len(data) != 343 or data.isna().any().any() or not np.isfinite(data.to_numpy()).all():
        raise ValueError("Incomplete aligned sample")
    if (factors <= -0.999).any().any(): raise ValueError("Possible French missing-value sentinel")
    data["Multi_factor"] = data[COMPONENTS].mean(axis=1)
    return data

def run(workbook, output):
    out=Path(output); out.mkdir(parents=True,exist_ok=True)
    df=load_data(workbook)
    X=np.column_stack([np.ones(len(df)),df[["RF","Mkt_RF","HML","SMB"]].to_numpy()])
    y=df.Value.to_numpy()
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    residual=y-X@coef; dof=len(y)-X.shape[1]
    variance=residual@residual/dof
    se=np.sqrt(np.diag(np.linalg.inv(X.T@X)*variance))
    t=coef/se; p=2*stats.t.sf(np.abs(t),dof)
    regression=pd.DataFrame({"term":["Intercept","RF","Mkt_RF","HML","SMB"],"coefficient":coef,"standard_error":se,"t_stat":t,"p_value":p})
    regression.to_csv(out/"regression.csv",index=False,float_format="%.12g",lineterminator="\n")
    df["Replication"]=X[:,1:]@coef[1:]
    fitted=X@coef
    r2=1-(residual@residual)/np.sum((y-y.mean())**2)
    def metrics(s):
        mean=s.mean()*12; vol=s.std(ddof=1)*np.sqrt(12)
        sharpe=(mean-df.RF.mean()*12)/vol
        return mean,vol,sharpe
    summ=[]
    for label in ["Value","Replication"]:
        a,v,s=metrics(df[label]); summ.append({"portfolio":label,"annualized_arithmetic_return":a,"annualized_volatility":v,"sharpe":s})
    pd.DataFrame(summ).to_csv(out/"replication_metrics.csv",index=False,float_format="%.12g",lineterminator="\n")
    corr=df[["Value","Replication"]].corr().iloc[0,1]
    active=df[COMPONENTS].subtract(df.Market,axis=0)
    df["Multi_active"]=df.Multi_factor-df.Market
    if not np.allclose(active.mean(axis=1),df.Multi_active,atol=1e-14): raise AssertionError("Active returns identity")
    mean_active=df.Multi_active.mean()*12; te=df.Multi_active.std(ddof=1)*np.sqrt(12); ir=mean_active/te
    pd.DataFrame([{"months":len(df),"annualized_arithmetic_active_return":mean_active,"annualized_tracking_error":te,"information_ratio":ir}]).to_csv(out/"active_performance.csv",index=False,float_format="%.12g",lineterminator="\n")
    variance_m=df.Multi_active.var(ddof=1)
    covs=active.apply(lambda col: col.cov(df.Multi_active))
    contrib=covs/4
    if not np.isclose(contrib.sum(),variance_m,rtol=1e-12,atol=1e-16): raise AssertionError("Variance decomposition")
    risks=pd.DataFrame({"component":COMPONENTS,"monthly_covariance":covs.to_numpy(),"monthly_variance_contribution":contrib.to_numpy(),"variance_share":contrib.to_numpy()/variance_m,"annualized_tracking_error_contribution":te*contrib.to_numpy()/variance_m})
    risks.to_csv(out/"risk_decomposition.csv",index=False,float_format="%.12g",lineterminator="\n")
    panel=df.copy()
    for col in COMPONENTS: panel[col+"_active"]=active[col]
    panel["Replication_residual"]=df.Value-df.Replication
    panel.index=panel.index.astype(str); panel.index.name="month"
    panel.to_csv(out/"monthly_panel.csv",float_format="%.12g",lineterminator="\n")
    (out/"diagnostics.json").write_text(json.dumps({"months":len(df),"start":START,"end":END,"regression_r2":r2,"replication_correlation":corr,"alpha_monthly":float(coef[0]),"alpha_annual_arithmetic":float(coef[0]*12),"monthly_active_variance":float(variance_m),"decomposition_sum":float(contrib.sum()),"workbook_sha256":hashlib.sha256(Path(workbook).read_bytes()).hexdigest()},indent=2)+"\n",encoding="utf-8")
    plt.rcParams.update({"font.family":"DejaVu Sans","axes.titlecolor":"#213444","axes.labelcolor":"#213444"})
    fig,ax=plt.subplots(figsize=(9,4.8))
    for col,label,color in [("Value","MSCI USA Value","#246B83"),("Replication","Factor replication","#BD503B")]:
        ax.plot(pd.DatetimeIndex([pd.Timestamp("1994-12-31")]).append(df.index.to_timestamp(how="end").normalize()),np.r_[1,(1+df[col]).cumprod()],label=label,color=color)
    ax.set(title="In-sample factor replication and MSCI Value",xlabel="Date",ylabel="Growth of $1")
    ax.grid(alpha=.2);ax.legend();fig.text(.12,.01,"Source: instructor MSCI gross USD levels and French monthly factors; Jan 1995–Jul 2023; no costs.",fontsize=8)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(out/"replication_growth.png",dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.8))
    bars=ax.bar(["Value","Minimum volatility","Equal weight","Momentum"],risks.variance_share,color=COLORS)
    ax.axhline(0,color="#213444",lw=.8);ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set(title="Contribution to multifactor active variance",ylabel="Share of active variance",xlabel="Factor index")
    ax.grid(axis="y",alpha=.2);ax.set_axisbelow(True)
    for b,v in zip(bars,risks.variance_share): ax.annotate(f"{v:.1%}",(b.get_x()+b.get_width()/2,v),xytext=(0,4 if v>=0 else -13),textcoords="offset points",ha="center",fontsize=9)
    fig.text(.12,.01,"Source: instructor MSCI gross USD index returns; Jan 1995–Jul 2023. Weights: 25% each.",fontsize=8)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(out/"active_risk_decomposition.png",dpi=180);plt.close(fig)
    print("REGRESSION\n",regression.to_string(index=False));print("R2",r2,"corr",corr)
    print("PERFORMANCE\n",pd.DataFrame(summ).to_string(index=False))
    print("ACTIVE",mean_active,te,ir)
    print("RISK\n",risks.to_string(index=False))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();run(a.input,a.output)
