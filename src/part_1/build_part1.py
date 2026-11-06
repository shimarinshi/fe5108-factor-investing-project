"""Offline Part 1 analysis. Numerical inputs: classroom workbook only.
Run from the repository root: python src/part_1/build_part1.py
Dependencies: numpy, pandas, openpyxl, matplotlib. Python >=3.10.
No downloaded factors, simulated data, or prior-project estimates are used.
"""
from pathlib import Path
import os, math, json, hashlib, platform, html, datetime, base64
import numpy as np
import pandas as pd
import openpyxl
os.environ.setdefault('MPLCONFIGDIR', '/tmp/fe5108_part1_mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO/'outputs/part_1'
T = ROOT/'tables'; F = ROOT/'figures'
for p in (T,F): p.mkdir(parents=True, exist_ok=True)
SRC = REPO/'data/raw/ff_msci_shared.xlsx'
W = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
AUDIT = []
FFURL = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html'
MOMURL = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_10_port_form_pr_12_2.html'
BETAURL = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_port_form_BETA.html'
MSCIURL = 'https://www.msci.com/eqb/methodology/meth_docs/MSCI_Momentum_Indices_Methodology.pdf'
LIBURL = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html'
ARCHURL = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors_archive.html'

def monthly_key(v):
    return isinstance(v,(int,float)) and float(v).is_integer() and 190001<=v<=210012 and 1<=int(v)%100<=12

def first_monthly_block(sheet, header_row):
    s=W[sheet]; rows=list(s.iter_rows(values_only=True)); data=[]; started=False; first=None; last=None
    for i,r in enumerate(rows[header_row:],header_row+1):
        if monthly_key(r[0]):
            if first is None: first=i
            last=i; started=True; data.append(r)
        elif started: break
    frame=pd.DataFrame(data)
    idx=pd.PeriodIndex([f'{int(v)//100:04d}-{int(v)%100:02d}' for v in frame.pop(0)],freq='M')
    frame.index=idx; frame.index.name='month'
    frame=frame.astype(float)
    assert frame.index.is_unique and frame.index.equals(pd.period_range(idx.min(),idx.max(),freq='M',name='month'))
    assert not frame.isin([-99.99,-999]).any().any() and np.isfinite(frame.to_numpy()).all()
    AUDIT.append(dict(sheet=sheet,excel_rows=f'{first}:{last}',start=str(idx.min()),end=str(idx.max()),months=len(frame),missing=0,duplicates=0,source_units='percent; divide by 100'))
    return frame/100

ff=first_monthly_block('FF - 3 factor returns',4); ff.columns=['Mkt-RF','SMB','HML','RF']
mom_all=first_monthly_block('FF - portfolios sorted on pmom',11)
beta_all=first_monthly_block('FF - portfolios sorted on beta',16)
# original Excel: momentum B=Lo PRIOR, K=Hi PRIOR; beta G=Lo10, P=Hi10.
mom=mom_all[10]-mom_all[1]; mom.name='MOM_decile'
lowbeta=beta_all[6]-beta_all[15]; lowbeta.name='LOWBETA_decile'

levels=[]; raw_dates=[]
for row in W['MSCI - factor totret index'].iter_rows(min_row=8,values_only=True):
    try: d=datetime.datetime.strptime(str(row[0]),'%b %d, %Y')
    except ValueError: continue
    levels.append([pd.Period(d,freq='M'),*[float(str(v).replace(',','')) for v in row[1:6]]]); raw_dates.append(d.date().isoformat())
names=['USA','Value','MinVol','EqualWeight','Momentum']
lev=pd.DataFrame(levels,columns=['month',*names]).set_index('month')
assert lev.index.is_unique and lev.index.equals(pd.period_range('1994-12','2023-07',freq='M',name='month'))
assert (lev>0).all().all() and np.isfinite(lev.to_numpy()).all()
AUDIT.append(dict(sheet='MSCI - factor totret index',excel_rows='8:351',start='1994-12',end='2023-07',months=len(lev),missing=0,duplicates=0,source_units='USD Gross total return index levels; numeric text'))
msci=lev.pct_change(fill_method=None).iloc[1:]
assert len(msci)==343 and msci.index[0]==pd.Period('1995-01')
factors=ff.join(mom).join(lowbeta)
common=ff.loc['1995-01':'2023-07'].join(mom).join(lowbeta).join(msci)
assert len(common)==343 and common.notna().all().all()

def save(df,filename,index=True):
    df.to_csv(T/filename,index=index,float_format='%.12g',encoding='utf-8-sig')

save(ff,'ff3_monthly_decimal.csv'); save(mom.to_frame(),'momentum_decile_spread_monthly_decimal.csv')
save(lowbeta.to_frame(),'lowbeta_decile_spread_monthly_decimal.csv'); save(lev,'msci_levels.csv')
save(pd.DataFrame({'month':lev.index.astype(str),'original_date':raw_dates}),'msci_date_mapping.csv',False)
save(msci,'msci_monthly_returns_decimal.csv'); save(common,'common_monthly_inputs_decimal.csv')
save(pd.DataFrame(AUDIT),'input_audit.csv',False)

# 1A: ordinary mean t statistics; no HAC adjustment, as explicitly allowed.
a_rows=[]
for period,start,end in [('1927-1992','1927-01','1992-12'),('1993-2023Jul','1993-01','2023-07')]:
    for name in ['Mkt-RF','SMB','HML']:
        x=ff.loc[start:end,name]; se=x.std(ddof=1)/np.sqrt(len(x))
        a_rows.append(dict(period=period,factor=name,n=len(x),mean_monthly=x.mean(),mean_annual_arithmetic=12*x.mean(),vol_monthly=x.std(ddof=1),se_mean_monthly=se,t_mean=x.mean()/se,ci95_low_monthly=x.mean()-1.96*se,ci95_high_monthly=x.mean()+1.96*se))
a=pd.DataFrame(a_rows); save(a,'1A_factor_mean_tests.csv',False)
# Additional explicit difference check: large-sample independent-window SE, not a causal publication effect.
diff=[]
for name in ['Mkt-RF','SMB','HML']:
    x=ff.loc['1927-01':'1992-12',name]; y=ff.loc['1993-01':'2023-07',name]
    se=np.sqrt(x.var(ddof=1)/len(x)+y.var(ddof=1)/len(y)); delta=y.mean()-x.mean()
    z=delta/se
    diff.append(dict(factor=name,post_minus_pre_mean_monthly=delta,se_monthly=se,z_large_sample=z,p_two_sided_normal=math.erfc(abs(z)/math.sqrt(2))))
diff=pd.DataFrame(diff); save(diff,'1A_mean_difference_supplement.csv',False)

# 1C: monthly equal-weight mix, rebalanced monthly; arithmetic annualized mean.
rets=msci.copy(); rets['MultiFactor']=rets[['Value','MinVol','EqualWeight','Momentum']].mean(axis=1)
rets['RF']=common['RF']
c=[]
for name,x in rets.items():
    annmean=12*x.mean(); annvol=x.std(ddof=1)*np.sqrt(12)
    sharpe=(annmean-12*rets.RF.mean())/annvol
    # Literal assignment definition gives 0 for RF because the numerator is zero.
    # Its time-series variation is changing bill rates, not risky-asset price volatility.
    c.append(dict(strategy=name,n=len(x),mean_annual_arithmetic=annmean,vol_annual=annvol,sharpe_assignment=sharpe,cagr=np.prod(1+x)**(12/len(x))-1))
c=pd.DataFrame(c).set_index('strategy'); save(c,'1C_performance.csv'); save(rets,'1C_strategy_monthly_returns_decimal.csv')
# Diversification evidence using the same 343 complete monthly observations.
style_names=['Value','MinVol','EqualWeight','Momentum']
style_corr=rets[style_names].corr()
style_cov_annual=12*rets[style_names].cov(ddof=1)
weights=np.full(4,.25)
variance_actual=float(weights@style_cov_annual.to_numpy()@weights)
variance_diagonal=float(np.sum(weights**2*np.diag(style_cov_annual)))
perfect_corr_vol=float(np.dot(weights,np.sqrt(np.diag(style_cov_annual))))
actual_vol=float(np.sqrt(variance_actual))
assert np.isclose(actual_vol,c.loc['MultiFactor','vol_annual'],rtol=1e-12)
div_metrics=pd.DataFrame([
 {'metric':'mean_constituent_vol_and_perfect_positive_correlation_reference','value':perfect_corr_vol},
 {'metric':'multifactor_vol_annual','value':actual_vol},
 {'metric':'vol_reduction_absolute','value':perfect_corr_vol-actual_vol},
 {'metric':'vol_reduction_relative','value':1-actual_vol/perfect_corr_vol},
 {'metric':'portfolio_variance_annual','value':variance_actual},
 {'metric':'diagonal_variance_component','value':variance_diagonal},
 {'metric':'off_diagonal_covariance_component','value':variance_actual-variance_diagonal},
 {'metric':'perfect_positive_correlation_variance_reference','value':perfect_corr_vol**2},
 {'metric':'variance_reduction_relative','value':1-variance_actual/perfect_corr_vol**2},
 {'metric':'minimum_pairwise_total_return_correlation','value':style_corr.to_numpy()[np.triu_indices(4,1)].min()},
 {'metric':'maximum_pairwise_total_return_correlation','value':style_corr.to_numpy()[np.triu_indices(4,1)].max()},
])
save(style_corr,'1C_factor_index_return_correlations.csv')
save(style_cov_annual,'1C_factor_index_covariance_annual.csv')
save(div_metrics,'1C_diversification_evidence.csv',False)
risk_variance_contribution=weights*(style_cov_annual.to_numpy()@weights)
save(pd.DataFrame({'strategy':style_names,'weight':weights,'annual_variance_contribution':risk_variance_contribution,'variance_contribution_fraction':risk_variance_contribution/variance_actual}),'1C_risk_contributions.csv',False)

wealth=(1+rets).cumprod(); wealth=pd.concat([pd.DataFrame(1.,index=pd.PeriodIndex(['1994-12'],freq='M',name='month'),columns=wealth.columns),wealth])
save(wealth,'1C_growth_of_1.csv')

# 1D: active return vs broad market, not vs RF.
active=msci[['Value','MinVol','EqualWeight','Momentum']].sub(msci.USA,axis=0)
academic=common[['HML','SMB','MOM_decile','LOWBETA_decile']]
corr=pd.DataFrame({x:active.apply(lambda y:y.corr(academic[x])) for x in academic})
save(active,'1D_msci_active_returns_decimal.csv'); save(corr,'1D_correlations_4x4.csv')

# 1E: contemporaneous descriptive relation + prior-month information robustness.
# Both specifications use exactly Dec1995-Jul2023; lagged Nov1995 window requires Dec1994.
vol=ff.loc['1995-01':'2023-07','Mkt-RF'].rolling(12,min_periods=12).std(ddof=1)*np.sqrt(12)
vol_lag_full=ff['Mkt-RF'].rolling(12,min_periods=12).std(ddof=1).shift(1)*np.sqrt(12)
e=pd.DataFrame({'momentum':mom,'vol_t':vol,'vol_t_minus_1':vol_lag_full}).loc['1995-12':'2023-07'].copy()
assert len(e)==332 and e.notna().all().all()

def ols_hac(y,x,lags=12,keep=None):
    # Optional exclusions retain the original monthly calendar for HAC lags.
    y_full=np.asarray(y,float);x_full=np.asarray(x,float)
    keep=np.ones(len(x_full),dtype=bool) if keep is None else np.asarray(keep,bool)
    X_full=np.column_stack([np.ones(len(x_full)),x_full])
    y=y_full[keep];x=x_full[keep];X=X_full[keep]
    b=np.linalg.lstsq(X,y,rcond=None)[0]; u=y-X@b; bread=np.linalg.inv(X.T@X)
    scores=np.zeros_like(X_full);scores[keep]=X*u[:,None];meat=scores.T@scores
    for lag in range(1,lags+1):
        gamma=scores[lag:].T@scores[:-lag]
        meat+=(1-lag/(lags+1))*(gamma+gamma.T)
    cov=bread@meat@bread*len(x)/(len(x)-X.shape[1])
    se=np.sqrt(np.diag(cov)); z=b/se
    return dict(n=len(x),intercept=b[0],slope=b[1],slope_se_hac=se[1],slope_z_hac=z[1],slope_p_hac_normal=math.erfc(abs(z[1])/math.sqrt(2)),ci95_low=b[1]-1.96*se[1],ci95_high=b[1]+1.96*se[1],r_squared=1-u@u/np.sum((y-y.mean())**2),correlation=np.corrcoef(x,y)[0,1],lags=lags),X_full@b

er=[]; regimes=[]
for col in ['vol_t','vol_t_minus_1']:
    for l in [3,12]:
        row,fit=ols_hac(e.momentum,e[col],l); er.append({'specification':col,**row})
        if l==12:e['fitted_'+col]=fit
    e['regime_'+col]=pd.qcut(e[col],3,labels=['Low','Middle','High'])
    for reg in ['Low','Middle','High']:
        z=e.loc[e['regime_'+col]==reg]
        regimes.append(dict(specification=col,regime=reg,n=len(z),vol_min=z[col].min(),vol_max=z[col].max(),vol_mean=z[col].mean(),momentum_mean_monthly=z.momentum.mean(),momentum_mean_annual_arithmetic=12*z.momentum.mean(),momentum_vol_annual=z.momentum.std(ddof=1)*np.sqrt(12),momentum_negative_fraction=(z.momentum<0).mean()))
er=pd.DataFrame(er); regimes=pd.DataFrame(regimes)
save(e,'1E_monthly_analysis.csv'); save(er,'1E_regressions_HAC.csv',False); save(regimes,'1E_volatility_terciles.csv',False)
# Post-hoc influence diagnostic; the full-sample primary analysis is unchanged.
excluded=e.momentum.nsmallest(2).index
influence=[]
for col in ['vol_t','vol_t_minus_1']:
    row,_=ols_hac(e.momentum,e[col],12,keep=~e.index.isin(excluded))
    influence.append({'specification':col,'excluded_months':';'.join(str(k) for k in sorted(excluded)),**row})
influence=pd.DataFrame(influence);save(influence,'1E_extreme_month_sensitivity.csv',False)

plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18,'figure.dpi':130,'savefig.dpi':200,'font.size':10,'axes.titleweight':'bold'})
palette=['#34495e','#b65c36','#168878','#9580ba','#2178ae','#d49b24','#8b9298']
def finish(fig,name,caption):
    fig.text(.02,.015,caption,fontsize=8,color='#4d5661',ha='left')
    fig.tight_layout(rect=(0,.065,1,1));fig.savefig(F/(name+'.png'),bbox_inches='tight');fig.savefig(F/(name+'.svg'),bbox_inches='tight');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(11,4.4))
for k,period in enumerate(a.period.unique()):
    z=a[a.period==period]; xpos=np.arange(3)+(k-.5)*.34
    axs[0].bar(xpos,z.mean_annual_arithmetic*100,.32,label=period,color=palette[k])
    axs[1].bar(xpos,z.t_mean,.32,label=period,color=palette[k])
for ax in axs:ax.set_xticks(range(3),['Mkt-RF','SMB','HML']);ax.axhline(0,color='black',lw=.7)
axs[0].set(ylabel='Arithmetic annualized mean (%)',title='1A | Average factor spreads')
axs[1].set(ylabel='Ordinary t statistic of mean',title='1A | Statistical evidence')
axs[1].axhline(1.96,color='#b65c36',ls='--',label='1.96 reference');axs[0].legend(fontsize=8);axs[1].legend(fontsize=8)
finish(fig,'1A_premia_and_tstats','Source: classroom FF3; US published factor spreads. 1927-1992 (792 months), 1993-Jul2023 (367). No HAC.')
fig,axs=plt.subplots(1,2,figsize=(12,4.8));ix=np.arange(len(c)); labels=['USA','Value','MinVol','Equal\nWeight','Momentum','Multi\nFactor','RF']
axs[0].bar(ix,c.mean_annual_arithmetic*100,color=palette);axs[1].bar(ix,c.sharpe_assignment,color=palette)
for ax in axs:ax.set_xticks(ix,labels,rotation=25,ha='right');ax.axhline(0,color='black',lw=.7)
axs[0].set(title='1C | Arithmetic average return',ylabel='Annualized mean (%)');axs[1].set(title='1C | Assignment Sharpe ratio',ylabel='Sharpe (strategy volatility denominator)')
finish(fig,'1C_returns_and_sharpe','Source: classroom MSCI USA large/mid-cap Gross USD indices + FF RF. Jan1995-Jul2023, 343 months. RF ratio=0 literally.')
# Print-sized chart with labels intended for insertion at 6.7 inches wide.
fig,ax=plt.subplots(figsize=(6.7,2.7))
bar_names=['Value','MinVol','EqualWeight','Momentum','MultiFactor','Corr = 1\nreference']
bar_values=[*c.loc[style_names,'vol_annual'],actual_vol,perfect_corr_vol]
bars=ax.bar(bar_names,np.array(bar_values)*100,color=[palette[1],palette[2],palette[3],palette[4],palette[5],'#c2c8ce'])
for bar,v in zip(bars,bar_values):ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+.3,f'{v:.2%}',ha='center',fontsize=9)
ax.set(ylabel='Annualized volatility (%)',ylim=(0,20),title='Diversification reduces risk despite high correlations')
fig.tight_layout();fig.savefig(F/'1C_diversification_risk.png',dpi=250,bbox_inches='tight');fig.savefig(F/'1C_diversification_risk.svg',bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(6.7,2.8))
ax.scatter(e.vol_t*100,e.momentum*100,s=15,alpha=.55,color='#2178ae')
order=np.argsort(e.vol_t.to_numpy());ax.plot(e.vol_t.iloc[order]*100,e.fitted_vol_t.iloc[order]*100,color='#b65c36',lw=1.8)
ax.axhline(0,color='black',lw=.6)
ax.set(xlabel='Trailing 12-month market volatility (annualized %)',ylabel='Monthly momentum spread (%)',title='Weak negative linear association in this sample')
chart_stats=pd.read_csv(T/'1E_regressions_HAC.csv');chart_stats=chart_stats[(chart_stats.specification=='vol_t')&(chart_stats.lags==12)].iloc[0]
ax.set_title('Weak negative linear association in this sample',pad=23)
ax.text(.98,1.02,f'n = {len(e)}; R² = {chart_stats.r_squared:.1%}; HAC(12) p = {chart_stats.slope_p_hac_normal:.3f}',transform=ax.transAxes,ha='right',va='bottom',fontsize=8)
fig.tight_layout();fig.savefig(F/'1E_primary_scatter_print.png',dpi=250,bbox_inches='tight');fig.savefig(F/'1E_primary_scatter_print.svg',bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(10,5))
for i,col in enumerate(wealth):ax.plot(wealth.index.to_timestamp(),wealth[col],label=col,color=palette[i],lw=2 if col=='MultiFactor' else 1.25)
ax.set(yscale='log',title='1C | Growth of USD 1 (supplement)',ylabel='Cumulative wealth (log scale)',xlabel='Month');ax.legend(ncol=4,fontsize=9)
finish(fig,'1C_cumulative_wealth','Source: classroom MSCI Gross USD + FF RF; Dec1994 base through Jul2023. Four-index mix reset to 25% monthly; no costs.')
fig,ax=plt.subplots(figsize=(8,4.6));im=ax.imshow(corr,vmin=-1,vmax=1,cmap='RdBu_r',aspect='auto')
ax.grid(False);ax.set_xticks(range(4),['HML','SMB','Momentum\ndecile spread','Low-beta\ndecile spread']);ax.set_yticks(range(4),corr.index)
for i in range(4):
    for j in range(4):ax.text(j,i,f'{corr.iloc[i,j]:.3f}',ha='center',va='center',color='white' if abs(corr.iloc[i,j])>.6 else '#202b36')
ax.set_title('1D | MSCI active returns vs academic spreads');fig.colorbar(im,ax=ax,label='Pearson correlation')
finish(fig,'1D_correlation_heatmap','Source: classroom MSCI/FF; Jan1995-Jul2023, n=343 each cell. MSCI returns less USA; all academic legs value-weighted.')
fig,axs=plt.subplots(1,2,figsize=(11,4.8))
for ax,col,label in zip(axs,['vol_t','vol_t_minus_1'],['Same-month descriptive','Prior-month information']):
    ax.scatter(e[col]*100,e.momentum*100,s=14,alpha=.5,color='#2178ae')
    order=np.argsort(e[col].to_numpy());ax.plot(e[col].iloc[order]*100,e['fitted_'+col].iloc[order]*100,color='#b65c36',lw=2)
    ax.axhline(0,color='black',lw=.6);ax.set(title=label,xlabel='Trailing 12-month market volatility (annualized %)',ylabel='Momentum spread, monthly (%)')
finish(fig,'1E_volatility_scatter','Source: classroom FF Mkt-RF + value-weighted momentum deciles. Dec1995-Jul2023, n=332. Lines: OLS, not causality.')
fig,axs=plt.subplots(1,2,figsize=(10,4.5))
for ax,col,label in zip(axs,['vol_t','vol_t_minus_1'],['Same-month volatility','Prior-month volatility']):
    z=regimes[regimes.specification==col];ax.bar(z.regime,z.momentum_mean_annual_arithmetic*100,color=[palette[2],palette[4],palette[1]])
    ax.axhline(0,color='black',lw=.7);ax.set(title=label,xlabel='Full-sample volatility tercile',ylabel='Momentum annualized arithmetic mean (%)')
finish(fig,'1E_volatility_regimes','Source: classroom FF; Dec1995-Jul2023. Terciles are descriptive full-sample bins, not implementable real-time thresholds.')

# Independent numerical and source-shape checks, rather than mirrored unit tests.
checks={}
checks['1A_expected_n']=a.n.tolist()==[792,792,792,367,367,367]
checks['1A_t_matches_intercept_OLS']=True
for row in a.itertuples():
    start,end=('1927-01','1992-12') if row.period=='1927-1992' else ('1993-01','2023-07')
    x=ff.loc[start:end,row.factor].to_numpy(); u=x-x.mean()
    assert np.isclose(row.t_mean, x.mean()/np.sqrt((u@u/(len(x)-1))/len(x)))
checks['MSCI_343_returns']=len(msci)==343
checks['MSCI_reconstruction_max_error']=float(np.max(np.abs(((1+msci).cumprod()*lev.iloc[0]/lev.iloc[1:])-1)))
assert checks['MSCI_reconstruction_max_error']<1e-12
checks['multifactor_weighted_sum_max_error']=float(abs(rets.MultiFactor-(msci.Value+msci.MinVol+msci.EqualWeight+msci.Momentum)/4).max())
checks['1D_independent_matrix_max_error']=float(abs(corr.to_numpy()-np.corrcoef(np.column_stack([active.to_numpy(),academic.to_numpy()]).T)[:4,4:]).max())
assert checks['1D_independent_matrix_max_error']<1e-12
checks['1E_expected_n']=len(e)==332
first=e.iloc[0]; assert np.isclose(first.vol_t,ff.loc['1995-01':'1995-12','Mkt-RF'].std(ddof=1)*np.sqrt(12))
assert np.isclose(first.vol_t_minus_1,ff.loc['1994-12':'1995-11','Mkt-RF'].std(ddof=1)*np.sqrt(12))
checks['1E_window_boundaries_verified']=True
# HAC L=0 is independently HC1; slope = corr(y,x)*sd(y)/sd(x).
for col in ['vol_t','vol_t_minus_1']:
    row,_=ols_hac(e.momentum,e[col],0)
    assert np.isclose(row['slope'],e.momentum.corr(e[col])*e.momentum.std()/e[col].std())
    # Independent scalar projection of HAC slope variance, without matrix sandwich.
    xx=e[col].to_numpy(); yy=e.momentum.to_numpy(); xc=xx-xx.mean()
    slope=xc@(yy-yy.mean())/(xc@xc); residual=yy-yy.mean()-slope*xc
    score=xc*residual; scalar_meat=score@score
    for lag in range(1,13):scalar_meat+=2*(1-lag/13)*(score[lag:]@score[:-lag])
    independent_se=np.sqrt(scalar_meat/(xc@xc)**2*len(xx)/(len(xx)-2))
    row,_=ols_hac(yy,xx,12)
    assert np.isclose(row['slope_se_hac'],independent_se,rtol=1e-12)
checks['1E_slope_crosscheck']=True
checks['1E_HAC_scalar_projection_crosscheck']=True
assert np.isfinite(a.select_dtypes('number')).all().all() and np.isfinite(c).all().all() and np.isfinite(corr).all().all()
checks['finite_all_summary_outputs']=True
checks['1C_covariance_portfolio_vol_verified']=bool(np.isclose(actual_vol,c.loc['MultiFactor','vol_annual']))
checks['1C_risk_contributions_sum_verified']=bool(np.isclose(risk_variance_contribution.sum(),variance_actual))
manifest={'numerical_source':'data/raw/ff_msci_shared.xlsx only','original_path':'data/raw/ff_msci_shared.xlsx','source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'assignment_sha256':hashlib.sha256((REPO/'inputs/class_project_in_full.pdf').read_bytes()).hexdigest(),'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'openpyxl':openpyxl.__version__,'matplotlib':matplotlib.__version__,'methods_access_date':'2026-10-19','msci_methodology_version':'December 2013, assignment URL; not asserted valid over entire return history','sources':[FFURL,MOMURL,BETAURL,MSCIURL,LIBURL,ARCHURL],'checks':checks}
(ROOT/'audit_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

print("Part 1: tables, figures and numerical checks written to outputs/part_1/.")
