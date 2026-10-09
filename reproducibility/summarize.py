from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;O=R/'results';F=R/'figures'
def stats(a):
 a=np.array(a,float);a=a[np.isfinite(a)];n=len(a);s=a.std(ddof=1) if n>1 else 0;h=t.ppf(.975,n-1)*s/np.sqrt(n) if n>1 else 0
 return dict(n=n,mean=float(a.mean()),sd=float(s),median=float(np.median(a)),lo=float(a.mean()-h),hi=float(a.mean()+h),min=float(a.min()),max=float(a.max()))
b=pd.read_csv(O/'benchmark.csv');iv=pd.read_csv(O/'investment.csv');pr=pd.read_csv(O/'prices.csv');pt=pd.read_csv(O/'priority.csv');v=pd.read_csv(O/'validation.csv');st=pd.read_csv(O/'stress.csv')
iv['policy']=iv.policy.str.replace(r'random_\d+','random',regex=True)
iv=iv.groupby(['n','seed','fraction','policy'],as_index=False).mean(numeric_only=True)
S={'environment':json.loads((O/'environment.json').read_text()),'benchmark':[],'investment':[],'paired':[],'prices':[],'priority':[],'stress':[],'validation':{}}
for (n,m),g in b.groupby(['n','method']):S['benchmark'].append(dict(n=int(n),method=m,solve=stats(g.solve_seconds),build=stats(g.build_seconds),iterations=stats(g.nit),arcs=int(g.m.iloc[0]),variables=int(g.variables.iloc[0]),rows=int(g.rows.iloc[0])))
for (frac,p),g in iv.groupby(['fraction','policy']):S['investment'].append(dict(fraction=float(frac),policy=p,improvement=stats(g.improvement_pct)))
for frac,g in iv.groupby('fraction'):
 z=g.pivot(index=['n','seed'],columns='policy',values='improvement_pct')
 for p in ['utilization','random','degree_product','early_price_50']:S['paired'].append(dict(fraction=float(frac),comparator=p,difference=stats(z.exact_dual-z[p]),wins=int(sum(z.exact_dual>z[p]+1e-8)),ties=int(sum(abs(z.exact_dual-z[p])<=1e-8))))
for it,g in pr.groupby('iteration'):S['prices'].append(dict(iteration=int(it),gap=stats(g.relative_gap*100),spearman=stats(g.spearman),overlap=stats(g.top5_overlap*100),mae=stats(g.mae),violation=stats(g.violation),seconds=stats(g.seconds)))
base=pt[pt.weight==1].set_index(['n','seed'])
for w,g in pt.groupby('weight'):
 g=g.set_index(['n','seed']);S['priority'].append(dict(weight=int(w),priority_reduction=stats(100*(1-g.priority_cost/base.priority_cost)),other_increase=stats(100*(g.nonpriority_cost/base.nonpriority_cost-1)),total_increase=stats(100*(g.total_cost/base.total_cost-1))))
for (n,beta),g in st.groupby(['n','beta']):S['stress'].append(dict(n=int(n),beta=float(beta),optimal=int(sum(g.status==0)),infeasible=int(sum(g.status==2)),other=int(sum(~g.status.isin([0,2])))))
S['validation']={'max_balance':float(b.balance_max.max()),'max_capacity':float(b.capacity_max.max()),'hop_cost_reduction':stats(100*(1-v.objective/v.hop_energy)),'hop_increase':stats(100*(v.energy_hops/v.hop_hops-1)),'sensitivity_max_relative_error':float(np.max(abs(v.observed_slope-v.max_price)/np.maximum(1,v.max_price)))}
(O/'summary.json').write_text(json.dumps(S,indent=2));iv.to_csv(O/'investment_seed_means.csv',index=False)
# stratified summaries keep topology-size heterogeneity visible.
rows=[]
for (n,frac,p),g in iv.groupby(['n','fraction','policy']):rows.append(dict(nodes=n,fraction=frac,policy=p,**stats(g.improvement_pct)))
pd.DataFrame(rows).to_csv(O/'investment_by_size.csv',index=False)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(7,3.5));pol=['random','degree_product','utilization','early_price_50','exact_dual'];labels=['Random','Degree product','Utilization','Pricing (50)','Exact dual'];x=np.arange(5)
for j,frac in enumerate([.05,.1]):
 vals=[next(a['improvement'] for a in S['investment'] if a['fraction']==frac and a['policy']==p) for p in pol]
 ax.bar(x+(j-.5)*.36,[z['mean'] for z in vals],.36,yerr=[z['hi']-z['mean'] for z in vals],capsize=3,label=f'{int(frac*100)}% of arcs')
ax.set_xticks(x,labels);ax.set_ylabel('Routing-cost reduction (%)');ax.legend(frameon=False);fig.tight_layout();fig.savefig(F/'investment.png',dpi=210);fig.savefig(F/'investment.pdf');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(7,3));it=[z['iteration'] for z in S['prices']]
axs[0].plot(it,[z['gap']['mean'] for z in S['prices']],marker='o');axs[0].set_ylabel('Mean dual-bound gap (%)');axs[1].plot(it,[z['overlap']['mean'] for z in S['prices']],marker='o');axs[1].set_ylabel('Mean top-5% overlap (%)')
for a in axs:a.set_xlabel('Pricing iteration');a.grid(alpha=.2)
fig.tight_layout();fig.savefig(F/'pricing.png',dpi=210);fig.savefig(F/'pricing.pdf');plt.close(fig)
fig,ax=plt.subplots(figsize=(7,3));weights=[z['weight'] for z in S['priority']]
for metric,label in [('priority_reduction','Priority cost reduction'),('other_increase','Other-service cost increase'),('total_increase','Total unweighted cost increase')]:ax.plot(weights,[z[metric]['mean'] for z in S['priority']],marker='o',label=label)
ax.set_xlabel('Weight of service 1');ax.set_ylabel('Change relative to weight 1 (%)');ax.legend(frameon=False);fig.tight_layout();fig.savefig(F/'priority.png',dpi=210);fig.savefig(F/'priority.pdf')
print(json.dumps(S,indent=2))
