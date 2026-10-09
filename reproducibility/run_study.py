"""New replacement experiments, not a reproduction of the original timing table."""
import os
for v in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']: os.environ[v]='1'
import csv,json,time,platform,warnings,hashlib,sys
from pathlib import Path
import numpy as np
import scipy
from scipy import sparse
from scipy.optimize import linprog,OptimizeWarning
from scipy.sparse.csgraph import dijkstra
from scipy.stats import spearmanr
warnings.filterwarnings('ignore',category=OptimizeWarning)
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
LOG=open(OUT/'solver_records.jsonl','w')
COUNTER=0

def savecsv(name,rows):
 if not rows:return
 with open(OUT/name,'w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def matrices(n,arcs,k):
 m=len(arcs);a=np.asarray(arcs);inc=sparse.coo_matrix((np.r_[np.ones(m),-np.ones(m)],(np.r_[a[:,0],a[:,1]],np.r_[np.arange(m),np.arange(m)])),shape=(n,m)).tocsr()
 return inc,sparse.kron(sparse.eye(k),inc,format='csr'),sparse.hstack([sparse.eye(m)]*k,format='csr')

def solve(c,eq,b,cap,u,method='highs-ds',label=''):
 global COUNTER
 t=time.perf_counter();r=linprog(c,A_ub=cap,b_ub=u,A_eq=eq,b_eq=b,bounds=(0,None),method=method,options={'presolve':True,'threads':1,'time_limit':60,'primal_feasibility_tolerance':1e-7,'dual_feasibility_tolerance':1e-7,'ipm_optimality_tolerance':1e-8});elapsed=time.perf_counter()-t
 COUNTER+=1
 rec={'id':COUNTER,'label':label,'method':method,'seconds':elapsed,'status':r.status,'message':r.message,'nit':r.nit,'crossover_nit':r.get('crossover_nit',0),'objective':r.fun}
 if r.success:rec.update(balance_max=float(np.max(np.abs(eq@r.x-b))),capacity_max=float(max(0,np.max(cap@r.x-u))))
 LOG.write(json.dumps(rec)+'\n');LOG.flush()
 return r,elapsed

def audit():
 base=ROOT/'original_data';rows=[]
 for p in sorted(base.rglob('nodes.csv')):
  folder=p.parent;read=lambda name:list(csv.DictReader(open(folder/name)))
  nodes=read('nodes.csv');aa=read('arcs.csv');dd=read('demands.csv');ids={int(r['node']):j for j,r in enumerate(nodes)};ss=sorted(set(r['service'] for r in dd));smap={s:j for j,s in enumerate(ss)}
  n=len(nodes);k=len(ss);b=np.zeros((k,n));e=np.array([float(r['Ec_i']) for r in nodes]);O={ids[int(r['node'])] for r in nodes if int(r['is_source'])};D={ids[int(r['node'])] for r in nodes if int(r['is_destination'])}
  for r in dd:b[smap[r['service']],ids[int(r['node'])]]=float(r['b_i_s'])
  for restricted in [True,False]:
   ars=[(ids[int(r['i'])],ids[int(r['j'])]) for r in aa if not restricted or (ids[int(r['j'])] not in O and ids[int(r['i'])] not in D)]
   u=np.array([float(r['u_ij']) for r in aa if not restricted or (ids[int(r['j'])] not in O and ids[int(r['i'])] not in D)])
   inc,eq,cap=matrices(n,ars,k);r,t=solve(np.tile([e[i]*e[j] for i,j in ars],k),eq,b.ravel(),cap,u,label=str(folder.relative_to(base)))
   deficits=[(int(nodes[j]['node']),float(-b[:,j].sum()),float(sum(u[a] for a,(_,v) in enumerate(ars) if v==j))) for j in D]
   worst=max(deficits,key=lambda v:v[1]-v[2])
   rows.append(dict(instance=str(folder.relative_to(base)),restricted=restricted,n=n,k=k,m=len(ars),status=r.status,message=r.message,destination=worst[0],required=worst[1],inbound=worst[2]))
 savecsv('original_feasibility_audit.csv',rows)

def route(n,arcs,c,b,dest):
 # Valid because this newly generated family has a single common destination.
 a=np.asarray(arcs);m=len(arcs);g=sparse.csr_matrix((c,(a[:,1],a[:,0])),shape=(n,n));_,pred=dijkstra(g,directed=True,indices=dest,return_predecessors=True);index={tuple(ij):q for q,ij in enumerate(arcs)};x=np.zeros(m)
 for src in np.flatnonzero(b>0):
  v=int(src)
  while v!=dest:
   w=int(pred[v]);assert w>=0,(src,v);x[index[v,w]]+=b[src];v=w
 return x

def generate(n,seed,k=4):
 rng=np.random.default_rng(seed+10000*n);ns=max(5,n//10);O=set(range(ns));dest=n-1;rel=list(range(ns,n-1));edges=set()
 def add(i,j):edges.add(tuple(sorted((int(i),int(j)))))
 for i,j in zip(rel,rel[1:]+rel[:1]):add(i,j)
 for i in range(ns):
  for j in rng.choice(rel,3,replace=False):add(i,j)
 for j in rng.choice(rel,4,replace=False):add(dest,j)
 while len(edges)<3*n:
  i,j=rng.choice(rel,2,replace=False);add(i,j)
 arcs=sorted((i,j) for a,b in edges for i,j in [(a,b),(b,a)] if j not in O and i!=dest)
 e=rng.integers(1,100,n).astype(float);e[dest]=1;b=np.zeros((k,n))
 for s in range(k):b[s,:ns]=rng.integers(1,6,ns);b[s,dest]=-sum(b[s,:ns])
 c=np.array([e[i]*e[j] for i,j in arcs]);witness=np.array([route(n,arcs,rng.uniform(1,3,len(arcs)),b[s],dest) for s in range(k)])
 u=witness.sum(0)+rng.uniform(1,4,len(arcs))
 return arcs,e,b,c,u,witness

def study():
 benchmarks=[];invest=[];prior=[];stress=[];prices=[];validation=[]
 for n in [70,150,300]:
  for seed in range(20):
   k=4;arcs,e,b,c,u,witness=generate(n,seed,k);m=len(arcs);start=time.perf_counter();inc,eq,cap=matrices(n,arcs,k);build=time.perf_counter()-start
   tag=f'n{n}_s{seed}';np.savez_compressed(ROOT/'data'/f'{tag}.npz',arcs=arcs,energy=e,b=b,c=c,u=u,witness=witness)
   assert np.max(abs(eq@witness.ravel()-b.ravel()))<1e-8 and np.max(cap@witness.ravel()-u)<0
   results={}
   for method in (['highs-ds','highs-ipm'] if seed%2==0 else ['highs-ipm','highs-ds']):
    r,t=solve(np.tile(c,k),eq,b.ravel(),cap,u,method,tag);assert r.success;rsol=r
    results[method]=(r,t)
    benchmarks.append(dict(n=n,seed=seed,k=k,m=m,variables=k*m,rows=k*n+m,sources=max(5,n//10),destinations=1,method=method,build_seconds=build,solve_seconds=t,nit=r.nit,crossover_nit=r.get('crossover_nit',0),objective=r.fun,balance_max=float(np.max(abs(eq@r.x-b.ravel()))),capacity_max=float(max(0,np.max(cap@r.x-u)))))
   r,t=results['highs-ds'];exact=np.maximum(0,-r.ineqlin.marginals);flow=r.x.reshape(k,m);util=np.round(flow.sum(0)/u,12)
   assert abs(r.fun-results['highs-ipm'][0].fun)<1e-6*max(1,r.fun)
   # Capacity-constrained minimum-hop comparator, all services treated equally.
   hop,ht=solve(np.ones(k*m),eq,b.ravel(),cap,u,label=tag+'_hops');assert hop.success
   validation.append(dict(n=n,seed=seed,objective=r.fun,hop_energy=float(np.tile(c,k)@hop.x),energy_hops=float(r.x.sum()),hop_hops=float(hop.x.sum())))
   # A pure shortest-path solve must agree with the per-service relaxed LP.
   if seed==0:
    for s in range(k):
     sp=route(n,arcs,c,b[s],n-1)
     lr=linprog(c,A_eq=inc,b_eq=b[s],bounds=(0,None),method='highs-ds',options={'threads':1})
     assert lr.success and abs(c@sp-lr.fun)<1e-6*max(1,lr.fun)
   # Diagnostic pricing: no claimed warm start, no use of the exact objective for step selection.
   lam=np.zeros(m);best=-np.inf;tic=time.perf_counter();snaps={}
   scale=float(np.median(c)/max(1,np.mean(u)))
   for it in range(1,51):
    xs=np.array([route(n,arcs,c+lam,b[s],n-1) for s in range(k)])
    dual=float(sum((c+lam)@x for x in xs)-lam@u);best=max(best,dual);g=xs.sum(0)-u
    if it in [5,10,20,50]:
     rho=float(spearmanr(lam,exact).statistic) if np.std(lam)>0 and np.std(exact)>0 else float('nan');kk=max(1,int(np.ceil(.05*m)))
     order=np.lexsort((np.arange(m),-lam));exactorder=np.lexsort((np.arange(m),-exact));overlap=len(set(order[:kk])&set(exactorder[:kk]))/kk
     prices.append(dict(n=n,seed=seed,iteration=it,best_lower_bound=best,exact_objective=r.fun,relative_gap=(r.fun-best)/max(1,abs(r.fun)),spearman=rho,top5_overlap=overlap,mae=float(np.mean(abs(lam-exact))),violation=float(max(0,g.max())),seconds=time.perf_counter()-tic))
     snaps[it]=lam.copy()
    lam=np.maximum(0,lam+scale/(it**.75)*g)
   assert best<=r.fun+1e-6*max(1,r.fun)
   # Degree-product is an explicitly defined structural baseline, not betweenness.
   deg=np.bincount(np.array(arcs).ravel(),minlength=n);central=np.array([deg[i]*deg[j] for i,j in arcs])
   policies={'exact_dual':exact,'utilization':util,'degree_product':central,'early_price_50':snaps[50]}
   for fraction in [.05,.10]:
    kk=int(np.ceil(fraction*m))
    for policy,score in list(policies.items())+[('random_'+str(j),None) for j in range(10)]:
     ix=np.random.default_rng(900000+n*1000+seed*10+int(policy.split('_')[-1])).choice(m,kk,replace=False) if score is None else np.lexsort((np.arange(m),-score))[:kk]
     uu=u.copy();uu[ix]+=5.;up,tt=solve(np.tile(c,k),eq,b.ravel(),cap,uu,label=tag+'_'+policy);assert up.success
     invest.append(dict(n=n,seed=seed,fraction=fraction,k_arcs=kk,policy=policy,before=r.fun,after=up.fun,improvement_pct=100*(r.fun-up.fun)/r.fun,benefit_per_unit=(r.fun-up.fun)/(5*kk),saturated_before=int(sum(util>=1-1e-7)),saturated_after=int(sum((cap@up.x)/uu>=1-1e-7))))
   for w in [1,2,5,10]:
    weights=np.array([w,1,1,1]);pr,tt=solve((weights[:,None]*c).ravel(),eq,b.ravel(),cap,u,label=tag+f'_w{w}');assert pr.success;cost=pr.x.reshape(k,m)@c
    prior.append(dict(n=n,seed=seed,weight=w,priority_cost=cost[0],nonpriority_cost=sum(cost[1:]),total_cost=sum(cost)))
   for beta in [1,.98,.95,.90,.75,.5,.25]:
    rr,tt=solve(np.tile(c,k),eq,b.ravel(),cap,u*beta,label=tag+f'_stress{beta}')
    stress.append(dict(n=n,seed=seed,beta=beta,status=rr.status,objective=rr.fun))
   # Small finite-difference sensitivity check at top positive-price arc.
   ix=int(np.argmax(exact));uu=u.copy();uu[ix]+=1e-4
   rr,tt=solve(np.tile(c,k),eq,b.ravel(),cap,uu,label=tag+'_sensitivity');assert rr.success
   validation[-1].update(max_price=float(exact[ix]),observed_slope=(r.fun-rr.fun)/1e-4)
   if seed%5==0:print(tag,'complete',COUNTER,flush=True)
 for name,rows in [('benchmark.csv',benchmarks),('investment.csv',invest),('priority.csv',prior),('stress.csv',stress),('prices.csv',prices),('validation.csv',validation)]:savecsv(name,rows)

if __name__=='__main__':
 import scipy.optimize._highspy._core as hc
 env={'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'highs':f'{hc.HIGHS_VERSION_MAJOR}.{hc.HIGHS_VERSION_MINOR}.{hc.HIGHS_VERSION_PATCH}','platform':platform.platform(),'cpu':next((l.split(':',1)[1].strip() for l in open('/proc/cpuinfo') if l.startswith('model name')),''),'memory':next((l.strip() for l in open('/proc/meminfo') if l.startswith('MemTotal')),''),'threads':1,'time_limit_seconds':60,'seeds':list(range(20)),'n':[70,150,300],'k':4}
 (OUT/'environment.json').write_text(json.dumps(env,indent=2));audit();study();LOG.close();print('DONE',COUNTER)
