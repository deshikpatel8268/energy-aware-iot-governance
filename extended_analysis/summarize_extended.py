import pandas as pd,numpy as np,glob,sys
from scipy import stats
def ci(x):
    x=np.asarray(x,float);x=x[~np.isnan(x)];m=x.mean();h=stats.t.ppf(.975,len(x)-1)*x.std(ddof=1)/np.sqrt(len(x));return m,m-h,m+h,len(x)
inv=pd.concat([pd.read_csv(f) for f in glob.glob('results_extended/investment_n*.csv')])
pol=[c for c in ['exact_dual','utilization','polyak50','seq_util_T2','seq_util_T4','seq_dual_T2','seq_dual_T4','seq_dual_T8','seq_dual_T1each','optimal'] if c in inv]
for c in pol+['uncapacitated']: inv[c+'_pct']=100*(inv.z0-inv[c])/inv.z0
for c in pol:
    if c!='optimal' and 'optimal' in inv: inv[c+'_share']=100*(inv.z0-inv[c])/(inv.z0-inv.optimal)
print("n per (n,fraction):",inv.groupby(['n','fraction']).size().to_dict())
print("\nMEAN % reduction pooled, by fraction")
for f,g in inv.groupby('fraction'):
    print(f'-- {f}')
    for c in pol: print(f'{c:18s}',"%.2f [%.2f, %.2f] n=%d"%ci(g[c+'_pct']), ('share of opt %.1f [%.1f,%.1f]'%ci(g[c+'_share'])[:3] if c+'_share' in g else ''))
print("\nBy size means")
print(inv.groupby(['n','fraction'])[[c+'_pct' for c in pol]].mean().round(2).to_string())
if 'milp_seconds' in inv: print("\nMILP seconds by n,f:",inv.groupby(['n','fraction']).milp_seconds.agg(['mean','max']).round(2).to_string(), "\nstatus:",inv.milp_status.value_counts().to_dict())
if 'seq_dual_T1each_seconds' in inv: print("T1each seconds:",inv.groupby(['n','fraction']).seq_dual_T1each_seconds.mean().round(2).to_dict())
# paired: seq_dual_T4 vs exact_dual and utilization; T1each vs optimal
for a,b in [('seq_dual_T4','exact_dual'),('seq_dual_T4','utilization'),('seq_dual_T1each','seq_dual_T4'),('optimal','seq_dual_T1each'),('polyak50','exact_dual')]:
    if a in inv and b in inv:
        for f,g in inv.groupby('fraction'):
            d=g[a+'_pct']-g[b+'_pct'];print(f'paired {a}-{b} f={f}: %.2f [%.2f, %.2f]'%ci(d)[:3],'wins',(d>1e-9).sum(),'ties',(abs(d)<=1e-9).sum(),'of',len(d))
pr=pd.concat([pd.read_csv(f) for f in glob.glob('results_extended/pricing_polyak_n*.csv')])
print("\nPOLYAK pooled by iteration")
for it,g in pr.groupby('iteration'):
    print(it,len(g),'gap %.2f [%.2f,%.2f]'%tuple(100*np.array(ci(g.relative_gap)[:3])),'sp %.3f [%.3f,%.3f]'%ci(g.spearman)[:3],'top5 %.2f [%.2f,%.2f]'%tuple(100*np.array(ci(g.top5_overlap)[:3])),'viol %.2f [%.2f,%.2f]'%ci(g.violation)[:3],'t %.4f'%g.seconds.mean())
print(pr.groupby(['n','iteration']).relative_gap.mean().unstack().mul(100).round(2).to_string())
bd=pd.concat([pd.read_csv(f) for f in glob.glob('results_extended/bounds_n*.csv')])
print("\nmax possible (uncapacitated) %:",bd.groupby('n').max_possible_pct.mean().round(2).to_dict(), "witness gap %:",(100*(bd.witness_cost-bd.z0)/bd.z0).groupby(bd.n).mean().round(2).to_dict())
bm=pd.concat([pd.read_csv(f) for f in glob.glob('results_extended/benchmark_n*.csv')])
print("\nbench:",bm.groupby('n')[['m','variables','rows','ds_seconds','ipm_seconds']].agg(['mean','std']).round(4).to_string())
