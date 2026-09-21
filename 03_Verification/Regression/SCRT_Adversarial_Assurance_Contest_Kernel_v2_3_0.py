#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Adversarial-Assurance Contest Kernel and Budget Duality Theorem
Version 2.3.0

Exact integration of role-polarized assurance obstructions, coupled attacker
impacts, and target-saturated defender recovery effects.  The canonical contest
kernel supports exact attacker-cost / defender-recovery frontiers, dual budget
queries, constructive witnesses, and future attacker/recovery extension.

Dependency-free and deterministic.
"""
from __future__ import annotations

import argparse
import itertools
from dataclasses import dataclass
from typing import Iterable

VERSION = "2.3.0"
Mask = int
Typed = tuple[Mask, Mask]
Pair = tuple[int, Mask]
Effect = tuple[int, ...]
INF = 10**9


def subsets(mask: Mask) -> tuple[Mask, ...]:
    out=[]; s=mask
    while True:
        out.append(s)
        if s==0: break
        s=(s-1)&mask
    return tuple(out)


def minimal_antichain(items: Iterable[Mask]) -> tuple[Mask,...]:
    vals=sorted(set(items), key=lambda x:(x.bit_count(),x)); out=[]
    for x in vals:
        if any((y&x)==y for y in out): continue
        out.append(x)
    return tuple(out)


def pareto_pairs(items: Iterable[Pair]) -> tuple[Pair,...]:
    vals=sorted(set(items), key=lambda x:(x[0],x[1].bit_count(),x[1])); out=[]
    for c,r in vals:
        if any(c0<=c and (r0&r)==r0 for c0,r0 in out): continue
        out=[(c0,r0) for c0,r0 in out if not (c<=c0 and (r&r0)==r)]
        out.append((c,r))
    return tuple(sorted(out))


def valid_typed(t:Typed)->bool:
    d,e=t; return (d!=0 or e!=0) and (d&e)==0


def typed_universe(m:int)->tuple[Typed,...]:
    full=(1<<m)-1
    return tuple((d,e) for d in range(full+1) for e in range(full+1) if valid_typed((d,e)))


def typed_support(t:Typed)->Mask: return t[0]|t[1]

def role_mask(d:Mask,e:Mask,m:int)->Mask: return d|(e<<m)

def split_role_mask(c:Mask,m:int)->tuple[Mask,Mask]:
    full=(1<<m)-1; return c&full,(c>>m)&full


def pairwise_disjoint_masks(ms:tuple[Mask,...])->bool:
    seen=0
    for s in ms:
        if seen&s: return False
        seen|=s
    return True


def pairwise_physically_disjoint(ts:tuple[Typed,...])->bool:
    seen=0
    for t in ts:
        s=typed_support(t)
        if seen&s: return False
        seen|=s
    return True


def operational_packing_unions(routes:tuple[Mask,...],k:int)->tuple[Mask,...]:
    if k<=0:return (0,)
    out=set()
    for idxs in itertools.combinations(range(len(routes)),k):
        chosen=tuple(routes[i] for i in idxs)
        if pairwise_disjoint_masks(chosen):
            u=0
            for s in chosen:u|=s
            out.add(u)
    return tuple(sorted(out))


def certified_packing_exposures(routes:tuple[Typed,...],k:int,m:int)->tuple[Mask,...]:
    if k<=0:return (0,)
    out=set()
    for idxs in itertools.combinations(range(len(routes)),k):
        chosen=tuple(routes[i] for i in idxs)
        if pairwise_physically_disjoint(chosen):
            d=e=0
            for td,te in chosen:d|=td;e|=te
            out.add(role_mask(d,e,m))
    return tuple(sorted(out))


def op_capacity(routes:tuple[Mask,...],fd:Mask,k:int)->int:
    surv=tuple(s for s in routes if not(s&fd))
    for q in range(k,0,-1):
        if operational_packing_unions(surv,q): return q
    return 0


def cert_capacity(routes:tuple[Typed,...],impact:Mask,k:int,m:int)->int:
    fd,fe=split_role_mask(impact,m)
    surv=tuple(t for t in routes if not(t[0]&fd) and not(t[1]&fe))
    for q in range(k,0,-1):
        if certified_packing_exposures(surv,q,m): return q
    return 0


def minimal_blockers(universe:Mask,packings:tuple[Mask,...])->tuple[Mask,...]:
    if not packings:return (0,)
    return minimal_antichain(f for f in subsets(universe) if all(f&u for u in packings))


def operational_blockers(m:int,op:tuple[Mask,...],k:int)->tuple[Mask,...]:
    return minimal_blockers((1<<m)-1,operational_packing_unions(op,k))


def silent_obstructions(m:int,op:tuple[Mask,...],cert:tuple[Typed,...],k:int)->tuple[Mask,...]:
    op_p=operational_packing_unions(op,k)
    if not op_p:return ()
    cert_p=certified_packing_exposures(cert,k,m)
    out=[]
    for b in minimal_blockers((1<<(2*m))-1,cert_p):
        fd,_=split_role_mask(b,m)
        if any(not(fd&u) for u in op_p):out.append(b)
    return tuple(sorted(out,key=lambda x:(x.bit_count(),x)))


def contains_blocker(x:Mask,bs:tuple[Mask,...])->bool:
    return any((b&x)==b for b in bs)


def op_safe(impact:Mask,op_b:tuple[Mask,...],m:int)->bool:
    fd,_=split_role_mask(impact,m)
    return not contains_blocker(fd,op_b)


@dataclass(frozen=True)
class AttackAction:
    impact: Mask
    cost: int
    resources: Mask=0

@dataclass(frozen=True)
class RecoveryAction:
    route: Typed
    cost: int
    resources: Mask=0


def feasible_actions(resources:tuple[Mask,...],pmask:Mask)->bool:
    used=0
    for i,r in enumerate(resources):
        if pmask&(1<<i):
            if used&r:return False
            used|=r
    return True


def attack_summary(actions:tuple[AttackAction,...],pmask:Mask)->tuple[Mask,int,Mask]:
    imp=cost=res=0
    for i,a in enumerate(actions):
        if pmask&(1<<i):imp|=a.impact;cost+=a.cost;res|=a.resources
    return imp,cost,res


def recovery_effect(actions:tuple[RecoveryAction,...],pmask:Mask,types:tuple[Typed,...],k:int)->tuple[Effect,int,Mask]:
    index={t:i for i,t in enumerate(types)}
    counts=[0]*len(types);cost=res=0
    for i,a in enumerate(actions):
        if pmask&(1<<i):
            j=index[a.route];counts[j]=min(k,counts[j]+1);cost+=a.cost;res|=a.resources
    return tuple(counts),cost,res


@dataclass(frozen=True)
class AttackImpactKernel:
    entries: tuple[tuple[Mask,tuple[Pair,...]],...]
    def as_dict(self):return dict(self.entries)

@dataclass(frozen=True)
class RecoveryEffectKernel:
    entries: tuple[tuple[Effect,tuple[Pair,...]],...]
    def as_dict(self):return dict(self.entries)


def make_attack_kernel(actions:tuple[AttackAction,...])->AttackImpactKernel:
    by={}
    res_tuple=tuple(a.resources for a in actions)
    for p in range(1<<len(actions)):
        if not feasible_actions(res_tuple,p):continue
        imp,c,r=attack_summary(actions,p);by.setdefault(imp,[]).append((c,r))
    return AttackImpactKernel(tuple(sorted((imp,pareto_pairs(v)) for imp,v in by.items())))


def make_recovery_kernel(actions:tuple[RecoveryAction,...],types:tuple[Typed,...],k:int)->RecoveryEffectKernel:
    by={}
    res_tuple=tuple(a.resources for a in actions)
    for p in range(1<<len(actions)):
        if not feasible_actions(res_tuple,p):continue
        eff,c,r=recovery_effect(actions,p,types,k);by.setdefault(eff,[]).append((c,r))
    return RecoveryEffectKernel(tuple(sorted((eff,pareto_pairs(v)) for eff,v in by.items())))


def compose_attack_kernels(a:AttackImpactKernel,b:AttackImpactKernel)->AttackImpactKernel:
    by={}
    for ia,va in a.entries:
        for ib,vb in b.entries:
            for ca,ra in va:
                for cb,rb in vb:
                    if ra&rb:continue
                    by.setdefault(ia|ib,[]).append((ca+cb,ra|rb))
    return AttackImpactKernel(tuple(sorted((i,pareto_pairs(v)) for i,v in by.items())))


def compose_recovery_kernels(a:RecoveryEffectKernel,b:RecoveryEffectKernel,k:int)->RecoveryEffectKernel:
    by={}
    for ea,va in a.entries:
        for eb,vb in b.entries:
            ec=tuple(min(k,x+y) for x,y in zip(ea,eb))
            for ca,ra in va:
                for cb,rb in vb:
                    if ra&rb:continue
                    by.setdefault(ec,[]).append((ca+cb,ra|rb))
    return RecoveryEffectKernel(tuple(sorted((e,pareto_pairs(v)) for e,v in by.items())))


def min_pair_cost(pairs:tuple[Pair,...],allowed:Mask)->int:
    vals=[c for c,r in pairs if (r&allowed)==r]
    return min(vals) if vals else INF


def add_effect(cert:tuple[Typed,...],eff:Effect,types:tuple[Typed,...])->tuple[Typed,...]:
    out=list(cert)
    for t,n in zip(types,eff):out.extend([t]*n)
    return tuple(out)


def recovery_requirement(cert:tuple[Typed,...],rk:RecoveryEffectKernel,impact:Mask,k:int,m:int,types:tuple[Typed,...],allowed:Mask)->int:
    best=INF
    for eff,pairs in rk.entries:
        c=min_pair_cost(pairs,allowed)
        if c>=best:continue
        if cert_capacity(add_effect(cert,eff,types),impact,k,m)>=k:best=c
    return best


def attack_requirement(ak:AttackImpactKernel,impact:Mask,allowed:Mask)->int:
    return min_pair_cost(ak.as_dict().get(impact,()),allowed)


def contest_points(m:int,op:tuple[Mask,...],cert:tuple[Typed,...],ak:AttackImpactKernel,rk:RecoveryEffectKernel,k:int,types:tuple[Typed,...],allowed_a:Mask,allowed_d:Mask)->tuple[tuple[int,int,Mask],...]:
    op_b=operational_blockers(m,op,k);out=[]
    for imp,pairs in ak.entries:
        if not op_safe(imp,op_b,m):continue
        a=min_pair_cost(pairs,allowed_a)
        if a>=INF:continue
        d=recovery_requirement(cert,rk,imp,k,m,types,allowed_d)
        out.append((a,d,imp))
    return tuple(sorted(out))


def contest_frontier(points:tuple[tuple[int,int,Mask],...])->tuple[tuple[int,int,Mask],...]:
    out=[]
    for p in sorted(points,key=lambda x:(x[0],-x[1],x[2])):
        a,d,_=p
        if any(a0<=a and d0>=d for a0,d0,_ in out):continue
        out=[q for q in out if not(a<=q[0] and d>=q[1])]
        out.append(p)
    return tuple(sorted(out))


def alpha(points:tuple[tuple[int,int,Mask],...],bd:int)->int:
    vals=[a for a,d,_ in points if d>bd]
    return min(vals) if vals else INF


def delta(points:tuple[tuple[int,int,Mask],...],ba:int)->int:
    vals=[d for a,d,_ in points if a<=ba]
    return max(vals) if vals else 0


def attacker_wins_kernel(points:tuple[tuple[int,int,Mask],...],ba:int,bd:int)->bool:
    return any(a<=ba and d>bd for a,d,_ in points)


def attacker_wins_direct(m:int,op:tuple[Mask,...],cert:tuple[Typed,...],attacks:tuple[AttackAction,...],recoveries:tuple[RecoveryAction,...],k:int,ba:int,bd:int,allowed_a:Mask,allowed_d:Mask)->bool:
    ares=tuple(a.resources for a in attacks);dres=tuple(a.resources for a in recoveries)
    for p in range(1<<len(attacks)):
        if not feasible_actions(ares,p):continue
        imp,ac,ar=attack_summary(attacks,p)
        if ac>ba or (ar&allowed_a)!=ar:continue
        fd,_=split_role_mask(imp,m)
        if op_capacity(op,fd,k)<k:continue
        restored=False
        for h in range(1<<len(recoveries)):
            if not feasible_actions(dres,h):continue
            eff,dc,dr=recovery_effect(recoveries,h,typed_universe(m),k)
            if dc>bd or (dr&allowed_d)!=dr:continue
            if cert_capacity(add_effect(cert,eff,typed_universe(m)),imp,k,m)>=k:
                restored=True;break
        if not restored:return True
    return False


def min_attack_witness(attacks:tuple[AttackAction,...],impact:Mask,cost:int,allowed:Mask)->Mask|None:
    res=tuple(a.resources for a in attacks);best=None
    for p in range(1<<len(attacks)):
        if not feasible_actions(res,p):continue
        imp,c,r=attack_summary(attacks,p)
        if imp==impact and c==cost and (r&allowed)==r:
            best=p;break
    return best


def min_recovery_witness(cert:tuple[Typed,...],recoveries:tuple[RecoveryAction,...],impact:Mask,k:int,m:int,cost:int,allowed:Mask)->Mask|None:
    res=tuple(a.resources for a in recoveries);types=typed_universe(m)
    for p in range(1<<len(recoveries)):
        if not feasible_actions(res,p):continue
        eff,c,r=recovery_effect(recoveries,p,types,k)
        if c==cost and (r&allowed)==r and cert_capacity(add_effect(cert,eff,types),impact,k,m)>=k:return p
    return None


def permute_mask(mask:Mask,perm:tuple[int,...])->Mask:
    out=0
    for i,j in enumerate(perm):
        if mask&(1<<i):out|=1<<j
    return out


def permute_role_mask(c:Mask,m:int,perm:tuple[int,...])->Mask:
    d,e=split_role_mask(c,m);return role_mask(permute_mask(d,perm),permute_mask(e,perm),m)


def permute_typed(t:Typed,perm:tuple[int,...])->Typed:return permute_mask(t[0],perm),permute_mask(t[1],perm)


def make_models():
    # m=2, target k=1. Operational route is kept compact; certified route geometries vary.
    ops=((1,),(2,),(3,),(1,2))
    ts=typed_universe(2)
    models=[]
    for op in ops:
        for n in (1,2,3):
            for cert in itertools.combinations(ts,n):
                if op_capacity(op,0,1)>=1 and cert_capacity(cert,0,1,2)>=1:models.append((op,cert))
    return tuple(models)


def make_attack_catalogs():
    imps=(1,2,4,8,5,10,12,15)
    prim=tuple(AttackAction(imp,1+(i%3),1<<(i%4)) for i,imp in enumerate(imps))
    out=[()]
    for r in (1,2,3):
        for idxs in itertools.combinations(range(len(prim)),r):out.append(tuple(prim[i] for i in idxs))
    return tuple(out)


def make_recovery_catalogs():
    ts=typed_universe(2)
    prim=tuple(RecoveryAction(t,1+(i%2),1<<(i%4)) for i,t in enumerate(ts))
    out=[()]
    for r in (1,2,3):
        for idxs in itertools.combinations(range(len(prim)),r):out.append(tuple(prim[i] for i in idxs))
    return tuple(out)


def verify_contest_kernel_exactness()->tuple[int,int]:
    models=make_models();acs=make_attack_catalogs();rcs=make_recovery_catalogs();types=typed_universe(2)
    checks=0;wins=0
    for i,(op,cert) in enumerate(models[:90]):
        ac=acs[(7*i+3)%len(acs)];rc=rcs[(11*i+5)%len(rcs)]
        ak=make_attack_kernel(ac);rk=make_recovery_kernel(rc,types,1)
        pts=contest_points(2,op,cert,ak,rk,1,types,15,15)
        for ba in range(5):
            for bd in range(5):
                lhs=attacker_wins_direct(2,op,cert,ac,rc,1,ba,bd,15,15)
                rhs=attacker_wins_kernel(pts,ba,bd)
                assert lhs==rhs
                wins+=int(lhs);checks+=1
    return checks,wins


def verify_budget_duality()->int:
    models=make_models();acs=make_attack_catalogs();rcs=make_recovery_catalogs();types=typed_universe(2);checks=0
    for i,(op,cert) in enumerate(models[:100]):
        pts=contest_points(2,op,cert,make_attack_kernel(acs[i%len(acs)]),make_recovery_kernel(rcs[(3*i+1)%len(rcs)],types,1),1,types,15,15)
        for ba in range(6):
            for bd in range(6):
                assert (alpha(pts,bd)>ba)==(delta(pts,ba)<=bd)
                checks+=1
    return checks


def verify_frontier_reconstruction()->int:
    models=make_models();acs=make_attack_catalogs();rcs=make_recovery_catalogs();types=typed_universe(2);checks=0
    for i,(op,cert) in enumerate(models[:110]):
        pts=contest_points(2,op,cert,make_attack_kernel(acs[(5*i)%len(acs)]),make_recovery_kernel(rcs[(7*i+2)%len(rcs)],types,1),1,types,15,15)
        fr=contest_frontier(pts)
        for b in range(7):
            assert alpha(pts,b)==alpha(fr,b)
            assert delta(pts,b)==delta(fr,b)
            checks+=2
    return checks


def verify_constructive_witnesses()->tuple[int,int]:
    models=make_models();acs=make_attack_catalogs();rcs=make_recovery_catalogs();types=typed_universe(2);aw=dw=0
    for i,(op,cert) in enumerate(models[:90]):
        ac=acs[(9*i+1)%len(acs)];rc=rcs[(5*i+4)%len(rcs)]
        pts=contest_points(2,op,cert,make_attack_kernel(ac),make_recovery_kernel(rc,types,1),1,types,15,15)
        for bd in range(4):
            a=alpha(pts,bd)
            if a>=INF:continue
            p=next(p for p in pts if p[0]==a and p[1]>bd)
            assert min_attack_witness(ac,p[2],a,15) is not None;aw+=1
            d=p[1]
            if d<INF:
                assert min_recovery_witness(cert,rc,p[2],1,2,d,15) is not None;dw+=1
    return aw,dw


def verify_future_extension()->tuple[int,int]:
    acs=make_attack_catalogs();rcs=make_recovery_catalogs();types=typed_universe(2)
    # dominated alternates must canonicalize away and remain invisible after future extension
    abase=(AttackAction(4,1,1),);aalt=abase+(AttackAction(4,4,1|8),)
    rbase=(RecoveryAction(types[0],1,1),);ralt=rbase+(RecoveryAction(types[0],4,1|8),)
    assert make_attack_kernel(abase)==make_attack_kernel(aalt)
    assert make_recovery_kernel(rbase,types,1)==make_recovery_kernel(ralt,types,1)
    ac=rc=0
    for f in acs[:24]:
        assert compose_attack_kernels(make_attack_kernel(abase),make_attack_kernel(f))==make_attack_kernel(abase+f)
        assert make_attack_kernel(abase+f)==make_attack_kernel(aalt+f);ac+=1
    for f in rcs[:24]:
        assert compose_recovery_kernels(make_recovery_kernel(rbase,types,1),make_recovery_kernel(f,types,1),1)==make_recovery_kernel(rbase+f,types,1)
        assert make_recovery_kernel(rbase+f,types,1)==make_recovery_kernel(ralt+f,types,1);rc+=1
    return ac,rc


def verify_scalar_frontier_not_continuation_complete()->tuple[int,int]:
    # Same current budget frontier, different hidden attack resources; future extension exposes difference.
    # Both attacks have identical impact/cost, but occupy different resources.
    a=(AttackAction(12,1,1),)
    b=(AttackAction(12,1,2),)
    op=(1,);cert=((1,2),(1,1));types=typed_universe(2);rk=make_recovery_kernel((),types,1)
    pa=contest_frontier(contest_points(2,op,cert,make_attack_kernel(a),rk,1,types,15,15))
    pb=contest_frontier(contest_points(2,op,cert,make_attack_kernel(b),rk,1,types,15,15))
    assert tuple((x,y) for x,y,_ in pa)==tuple((x,y) for x,y,_ in pb)
    future=(AttackAction(3,1,1),)
    ka=make_attack_kernel(a+future);kb=make_attack_kernel(b+future)
    assert ka!=kb
    return len(pa),1


def verify_name_transport()->int:
    perm=(1,0);types=typed_universe(2);models=make_models();acs=make_attack_catalogs();rcs=make_recovery_catalogs();checks=0
    for i,(op,cert) in enumerate(models[:60]):
        ac=acs[(2*i+1)%len(acs)];rc=rcs[(3*i+2)%len(rcs)]
        pop=tuple(sorted(permute_mask(x,perm) for x in op));pcert=tuple(sorted(permute_typed(x,perm) for x in cert))
        pac=tuple(AttackAction(permute_role_mask(a.impact,2,perm),a.cost,a.resources) for a in ac)
        prc=tuple(RecoveryAction(permute_typed(a.route,perm),a.cost,a.resources) for a in rc)
        p1=contest_points(2,op,cert,make_attack_kernel(ac),make_recovery_kernel(rc,types,1),1,types,15,15)
        p2=contest_points(2,pop,pcert,make_attack_kernel(pac),make_recovery_kernel(prc,types,1),1,types,15,15)
        canon1=sorted((a,d,imp.bit_count()) for a,d,imp in p1)
        canon2=sorted((a,d,imp.bit_count()) for a,d,imp in p2)
        assert canon1==canon2;checks+=1
    return checks


def verify_target_saturation()->int:
    # k=1: duplicating exact base/recovery route tokens above one does not alter contest answers.
    types=typed_universe(2);op=(1,);base=((1,2),);ac=(AttackAction(role_mask(0,2,2),1,1),);rc=(RecoveryAction((1,2),1,1),)
    checks=0
    for n in range(1,9):
        cert=base*n
        pts=contest_points(2,op,cert,make_attack_kernel(ac),make_recovery_kernel(rc,types,1),1,types,15,15)
        ref=contest_points(2,op,base,make_attack_kernel(ac),make_recovery_kernel(rc,types,1),1,types,15,15)
        for ba in range(3):
            for bd in range(3):
                assert attacker_wins_kernel(pts,ba,bd)==attacker_wins_kernel(ref,ba,bd);checks+=1
    return checks


def run_verify()->None:
    c,w=verify_contest_kernel_exactness();print(f"assurance_contest_kernel_exactness:PASS:checks={c}:attacker_wins={w}")
    c=verify_budget_duality();print(f"attack_recovery_budget_duality:PASS:checks={c}:law=Alpha(bD)>bA iff Delta(bA)<=bD")
    c=verify_frontier_reconstruction();print(f"contest_frontier_reconstruction:PASS:checks={c}:representation=PARETO_ATTACK_COST_RECOVERY_REQUIREMENT")
    a,d=verify_constructive_witnesses();print(f"constructive_contest_witnesses:PASS:attack_witnesses={a}:recovery_certificates={d}")
    a,r=verify_future_extension();print(f"future_attack_recovery_extension_congruence:PASS:attack_extensions={a}:recovery_extensions={r}")
    n,x=verify_scalar_frontier_not_continuation_complete();print(f"scalar_contest_frontier_not_continuation_complete:PASS:frontier_points={n}:future_resource_separator={x}")
    c=verify_name_transport();print(f"name_invariant_contest_transport:PASS:checks={c}")
    c=verify_target_saturation();print(f"target_saturation_binding:PASS:checks={c}")
    print("status:PASS")


def run_self_test()->None:
    assert verify_budget_duality()>0
    assert verify_frontier_reconstruction()>0
    assert verify_scalar_frontier_not_continuation_complete()[1]==1
    print("SCRT Adversarial-Assurance Contest Kernel v2.3.0 self-test")
    print("TOTAL 3/3 PASS")


def main():
    p=argparse.ArgumentParser();p.add_argument("--verify",action="store_true");p.add_argument("--self-test",action="store_true");a=p.parse_args()
    if a.verify:print("SCRT Adversarial-Assurance Contest Kernel v2.3.0 verification");run_verify()
    else:run_self_test()

if __name__=="__main__":main()
