"""Independent checks on saved Part 5 results."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
p=Path(__file__).resolve().parents[2] / "outputs" / "part5"
d=pd.read_csv(p/"monthly_panel.csv")
reg=pd.read_csv(p/"regression.csv").set_index("term")
m=pd.read_csv(p/"replication_metrics.csv").set_index("portfolio")
risk=pd.read_csv(p/"risk_decomposition.csv")
a=pd.read_csv(p/"active_performance.csv").iloc[0]
assert len(d)==343 and d.month.is_unique and d.month.iloc[0]=="1995-01" and d.month.iloc[-1]=="2023-07"
assert d.notna().all().all()
x=np.column_stack([np.ones(len(d)),d[["RF","Mkt_RF","HML","SMB"]]])
y=d.Value.to_numpy()
coefs=np.linalg.solve(x.T@x,x.T@y)
np.testing.assert_allclose(coefs,reg.coefficient,rtol=1e-8,atol=1e-10)
res=y-x@coefs
assert np.max(np.abs(x.T@res))<1e-10
np.testing.assert_allclose(d.Replication,x[:,1:]@coefs[1:],rtol=1e-8,atol=1e-10)
for name in ["Value","Replication"]:
 series=d[name]
 np.testing.assert_allclose(series.mean()*12,m.loc[name,"annualized_arithmetic_return"],rtol=1e-9)
 np.testing.assert_allclose(series.std(ddof=1)*np.sqrt(12),m.loc[name,"annualized_volatility"],rtol=1e-9)
active=d[["Value_active","Minimum_volatility_active","Equal_weight_active","Momentum_active"]].to_numpy()
np.testing.assert_allclose(active.mean(axis=1),d.Multi_active,rtol=1e-8,atol=1e-10)
cov=np.cov(active.T,ddof=1)
np.testing.assert_allclose(cov.sum()/16,d.Multi_active.var(ddof=1),rtol=1e-9)
np.testing.assert_allclose(risk.variance_share.sum(),1,rtol=1e-9)
np.testing.assert_allclose(a.annualized_tracking_error,d.Multi_active.std(ddof=1)*np.sqrt(12),rtol=1e-9)
print("PASS: sample alignment, independent normal-equation regression, replication, metrics, active-return and covariance identities.")
