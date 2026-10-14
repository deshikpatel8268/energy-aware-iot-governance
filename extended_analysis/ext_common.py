"""Shared helpers for the extended experiments. Instance generation is copied verbatim
from run_study.py (importing run_study would overwrite its solver log)."""
import os
for v in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']: os.environ[v]='1'
import time, warnings
import numpy as np
from scipy import sparse
from scipy.optimize import linprog, milp, LinearConstraint, Bounds, OptimizeWarning
from scipy.sparse.csgraph import dijkstra
warnings.filterwarnings('ignore', category=OptimizeWarning)
OPTS={'presolve':True,'threads':1,'time_limit':600,'primal_feasibility_tolerance':1e-7,'dual_feasibility_tolerance':1e-7,'ipm_optimality_tolerance':1e-8}

def matrices(n,arcs,k):
    m=len(arcs);a=np.asarray(arcs)
    inc=sparse.coo_matrix((np.r_[np.ones(m),-np.ones(m)],(np.r_[a[:,0],a[:,1]],np.r_[np.arange(m),np.arange(m)])),shape=(n,m)).tocsr()
    return inc,sparse.kron(sparse.eye(k),inc,format='csr'),sparse.hstack([sparse.eye(m)]*k,format='csr')

def route(n,arcs,c,b,dest):
    a=np.asarray(arcs);m=len(arcs);g=sparse.csr_matrix((c,(a[:,1],a[:,0])),shape=(n,n))
    _,pred=dijkstra(g,directed=True,indices=dest,return_predecessors=True)
    index={tuple(ij):q for q,ij in enumerate(arcs)};x=np.zeros(m)
    for src in np.flatnonzero(b>0):
        v=int(src)
        while v!=dest:
            w=int(pred[v]);assert w>=0;x[index[v,w]]+=b[src];v=w
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

def lp(c,eq,b,cap,u,method='highs-ds'):
    t=time.perf_counter();r=linprog(c,A_ub=cap,b_ub=u,A_eq=eq,b_eq=b,bounds=(0,None),method=method,options=OPTS)
    return r,time.perf_counter()-t
