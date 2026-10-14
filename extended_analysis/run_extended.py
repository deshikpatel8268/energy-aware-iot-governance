"""Extended experiments for the journal version (does not modify results/ of run_study.py).
E1 optimal budgeted portfolio (MILP), E2 sequential dual re-pricing heuristics,
E3 Polyak-type pricing with a feasible (witness) target, E4 larger instances."""
import sys,json,time,csv
import numpy as np
sys.path.insert(0,'.')
from ext_common import *
from ext_milp import optimal_portfolio
from scipy.stats import spearmanr
OUT='results_extended/'
def save(name,rows):
    if rows:
        with open(OUT+name,'w') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def duals(r): return np.maximum(0,-r.ineqlin.marginals)
def sequential(c,eq,b,cap,u,k,m,B,T,score='dual',delta=5.0):
    uu=u.copy();chosen=np.zeros(m,bool);sizes=[B//T+(1 if t<B%T else 0) for t in range(T)];nlp=0;t0=time.perf_counter()
    for sz in sizes:
        r,_=lp(np.tile(c,k),eq,b,cap,uu);nlp+=1;assert r.success
        sc=duals(r) if score=='dual' else np.round(r.x.reshape(k,m).sum(0)/uu,12)
        sc=np.where(chosen,-np.inf,sc);ix=np.lexsort((np.arange(m),-sc))[:sz]
        chosen[ix]=True;uu[ix]+=delta
    r,_=lp(np.tile(c,k),eq,b,cap,uu);nlp+=1
    return r.fun,nlp,time.perf_counter()-t0
def static(c,eq,b,cap,u,k,m,B,score,delta=5.0):
    ix=np.lexsort((np.arange(m),-score))[:B];uu=u.copy();uu[ix]+=delta;r,_=lp(np.tile(c,k),eq,b,cap,uu);return r.fun
def polyak(n,arcs,b,c,u,k,UBt,iters,exact,obj):
    m=len(arcs);lam=np.zeros(m);best=-np.inf;theta=2.0;stall=0;snaps={};out=[];t0=time.perf_counter()
    for it in range(1,iters+1):
        xs=np.array([route(n,arcs,c+lam,b[s],n-1) for s in range(k)])
        phi=float(sum((c+lam)@x for x in xs)-lam@u);g=xs.sum(0)-u
        if phi>best+1e-9: best=phi;stall=0
        else:
            stall+=1
            if stall>=5: theta/=2;stall=0
        if it in (5,10,20,50,100,200):
            kk=max(1,int(np.ceil(.05*m)));o=np.lexsort((np.arange(m),-lam));eo=np.lexsort((np.arange(m),-exact))
            rho=float(spearmanr(lam,exact).statistic) if np.std(lam)>0 else float('nan')
            out.append(dict(iteration=it,relative_gap=(obj-best)/max(1,abs(obj)),spearman=rho,top5_overlap=len(set(o[:kk])&set(eo[:kk]))/kk,violation=float(max(0,g.max())),seconds=time.perf_counter()-t0));snaps[it]=lam.copy()
        nn=float(g@g)
        if nn<=0: break
        lam=np.maximum(0,lam+theta*(UBt-phi)/nn*g)
    return out,snaps
def run(n,seeds,milp_on=True,tl=300,Ts=(2,4),t1=True):
    inv=[];pri=[];bench=[];bounds=[]
    seeds=list(seeds)
    for seed in seeds:
        k=4;arcs,e,b,c,u,w=generate(n,seed,k);m=len(arcs);inc,eq,cap=matrices(n,arcs,k);bb=b.ravel()
        rd,td=lp(np.tile(c,k),eq,bb,cap,u,'highs-ds');ri,ti=lp(np.tile(c,k),eq,bb,cap,u,'highs-ipm');assert rd.success and ri.success
        bench.append(dict(n=n,seed=seed,m=m,variables=k*m,rows=k*n+m,ds_seconds=td,ipm_seconds=ti,ds_nit=rd.nit,ipm_nit=ri.nit,objective=rd.fun))
        z0=rd.fun;exact=duals(rd);util=np.round(rd.x.reshape(k,m).sum(0)/u,12)
        # uncapacitated (shortest-path) objective = lower bound on any upgrade outcome
        unc=sum(c@route(n,arcs,c,b[s],n-1) for s in range(k));UBw=float(np.tile(c,k)@w.ravel())
        bounds.append(dict(n=n,seed=seed,z0=z0,uncapacitated=unc,max_possible_pct=100*(z0-unc)/z0,witness_cost=UBw))
        # E3 Polyak pricing with witness-cost target (feasible UB, no exact objective used)
        out,snaps=polyak(n,arcs,b,c,u,k,UBw,200,exact,z0)
        for o in out: pri.append(dict(n=n,seed=seed,**o))
        for f in (.05,.10):
            B=int(np.ceil(f*m));row=dict(n=n,seed=seed,fraction=f,B=B,z0=z0,uncapacitated=unc)
            row['exact_dual']=static(c,eq,bb,cap,u,k,m,B,exact);row['utilization']=static(c,eq,bb,cap,u,k,m,B,util)
            row['polyak50']=static(c,eq,bb,cap,u,k,m,B,snaps[50])
            for T in Ts:
                row[f'seq_dual_T{T}'],_,_=sequential(c,eq,bb,cap,u,k,m,B,T,'dual')
                row[f'seq_util_T{T}'],_,_=sequential(c,eq,bb,cap,u,k,m,B,T,'util')
            if t1:
                v,nlp,ts=sequential(c,eq,bb,cap,u,k,m,B,B,'dual');row['seq_dual_T1each']=v;row['seq_dual_T1each_seconds']=ts;row['seq_dual_T1each_lps']=nlp
            for T in Ts:
                t0=time.perf_counter();sequential(c,eq,bb,cap,u,k,m,B,T,'dual');row[f'seq_dual_T{T}_seconds']=time.perf_counter()-t0
            if milp_on:
                r,t=optimal_portfolio(arcs,b,c,u,k,n,B,tl=tl)
                row['optimal']=r.fun if r.x is not None else float('nan');row['milp_status']=r.status;row['milp_seconds']=t
                row['milp_gap']=getattr(r,'mip_gap',float('nan'));row['milp_bound']=getattr(r,'mip_dual_bound',float('nan'))
            inv.append(row)
        print(n,seed,'done',flush=True)
    tag=f'n{n}'+(f'_s{seeds[0]}-{seeds[-1]}' if len(seeds)<20 else '')
    save(f'investment_{tag}.csv',inv);save(f'pricing_polyak_{tag}.csv',pri);save(f'benchmark_{tag}.csv',bench);save(f'bounds_{tag}.csv',bounds)
if __name__=='__main__':
    n=int(sys.argv[1]);a,bnd=(sys.argv[2].split('-')+[None])[:2];seeds=list(range(int(a),int(bnd))) if bnd else list(range(int(a)));milp_on=sys.argv[3]=='1' if len(sys.argv)>3 else True
    if n>=1000: run(n,seeds,milp_on,tl=600,Ts=(2,4,8),t1=False)
    else: run(n,seeds,milp_on)
