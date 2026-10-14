import sys,time,numpy as np
sys.path.insert(0,'.')
from ext_common import *
def optimal_portfolio(arcs,b,c,u,k,n,B,delta=5.0,tl=300):
    m=len(arcs);inc,eq,cap=matrices(n,arcs,k)
    nx=k*m;cost=np.r_[np.tile(c,k),np.zeros(m)]
    A_eq=sparse.hstack([eq,sparse.csr_matrix((eq.shape[0],m))])
    A_cap=sparse.hstack([cap,-delta*sparse.eye(m)])
    A_bud=sparse.csr_matrix(np.r_[np.zeros(nx),np.ones(m)][None,:])
    cons=[LinearConstraint(A_eq,b.ravel(),b.ravel()),LinearConstraint(A_cap,-np.inf,u),LinearConstraint(A_bud,B,B)]
    integ=np.r_[np.zeros(nx),np.ones(m)]
    t=time.perf_counter()
    r=milp(cost,constraints=cons,integrality=integ,bounds=Bounds(np.zeros(nx+m),np.r_[np.full(nx,np.inf),np.ones(m)]),options={'time_limit':tl,'mip_rel_gap':1e-6,'presolve':True,'disp':False})
    return r,time.perf_counter()-t
if __name__=='__main__':
    for n,s in [(70,0),(300,0)]:
        arcs,e,b,c,u,w=generate(n,s);m=len(arcs);k=4
        inc,eq,cap=matrices(n,arcs,k);r0,_=lp(np.tile(c,k),eq,b.ravel(),cap,u)
        for f in [.05,.10]:
            B=int(np.ceil(f*m));r,t=optimal_portfolio(arcs,b,c,u,k,n,B,tl=120)
            print(n,s,f,B,'status',r.status,r.message[:60],'t=%.1f'%t,'impr=%.3f%%'%(100*(r0.fun-r.fun)/r0.fun if r.x is not None else -1),'gap',getattr(r,'mip_gap',None),'bound',getattr(r,'mip_dual_bound',None))
