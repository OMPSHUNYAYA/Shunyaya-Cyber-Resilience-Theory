#!/usr/bin/env python3
"""SCRT v2.18.0 assumption-sharpness and countermodel audit.

These small countermodels test boundaries of the written theorem hypotheses.
They are not universal proofs.
"""
import argparse
VERSION='2.18.0'

def operational_survives(routes, fd, k=1):
    surv=[set(r) for r in routes if set(r).isdisjoint(fd)]
    if k==1: return bool(surv)
    from itertools import combinations
    return any(all(a.isdisjoint(b) for i,a in enumerate(c) for b in c[i+1:]) for c in combinations(surv,k))

def certified_survives(routes, fd, fe, k=1):
    surv=[]
    for d,e in routes:
        if set(d).isdisjoint(fd) and set(e).isdisjoint(fe): surv.append(set(d)|set(e))
    if k==1: return bool(surv)
    from itertools import combinations
    return any(all(a.isdisjoint(b) for i,a in enumerate(c) for b in c[i+1:]) for c in combinations(surv,k))

def silent(O,C,fd,fe,k=1): return operational_survives(O,fd,k) and not certified_survives(C,fd,fe,k)

def evidence_only_baseline_assumption_needed():
    # Baseline does not meet k=1. Hardening creates operation while evidence is bad.
    O=[]; Op=[{'a'}]; C=[(set(),{'e'})]
    fd=set(); fe={'e'}
    return (not silent(O,C,fd,fe)) and silent(Op,C,fd,fe)

def additive_operational_hardening_needed():
    # Replacement rather than addition can destroy an old surviving route.
    O=[{'a'}]; O_nonadd=[{'b'}]; C=[]
    fd={'b'}; fe=set()
    return silent(O,C,fd,fe) and not silent(O_nonadd,C,fd,fe)

def additive_certified_hardening_needed():
    # Removing the sole certificate can create a silent state.
    O=[{'a'}]; C=[(set(),{'e'})]; C_nonadd=[]
    fd=set(); fe=set()
    return (not silent(O,C,fd,fe)) and silent(O,C_nonadd,fd,fe)

def hereditary_resource_feasibility_needed():
    # k=1. Action q1 alone supplies the needed route, but a deliberately
    # non-hereditary feasibility rule admits only the pair {q1,q2}.
    successful=lambda q: 'q1' in q
    feasible=lambda q: set(q)=={'q1','q2'}
    candidates=[set(),{'q1'},{'q2'},{'q1','q2'}]
    admissible=[q for q in candidates if feasible(q) and successful(q)]
    minimal=[q for q in admissible if not any(r<q and feasible(r) and successful(r) for r in candidates)]
    return minimal==[{'q1','q2'}] and len(minimal[0])>1

def conflict_free_global_lift_not_valid_with_exclusive_resources():
    # k=1, two scenarios. Each has a singleton response, but both responses
    # require the same exclusive resource.
    local1=[('q1','r')]; local2=[('q2','r')]
    each=bool(local1) and bool(local2)
    joint=any(r1!=r2 for _,r1 in local1 for _,r2 in local2)
    return each and not joint

def zero_cost_does_not_mean_empty_portfolio():
    # Baseline certificate absent; one zero-cost action restores it.
    costs={'q':0}
    good=[{'q'}]
    optimum=min(sum(costs[x] for x in q) for q in good)
    return optimum==0 and all(q for q in good)

def scalar_gain_size_not_frontier_complete():
    # Equal number of newly survivable scenarios but different identities.
    # A future requirement can name one scenario and distinguish them.
    gain_x={'F1'}; gain_y={'F2'}
    same_scalar=len(gain_x)==len(gain_y)
    query=lambda g: 'F1' in g
    return same_scalar and query(gain_x)!=query(gain_y)

def run():
    tests=[
      ('baseline_target_operational_needed_for_evidence_only_invariance',evidence_only_baseline_assumption_needed),
      ('additive_operational_hardening_needed_for_silent_set_inclusion',additive_operational_hardening_needed),
      ('additive_certified_hardening_needed_for_contraction',additive_certified_hardening_needed),
      ('hereditary_resource_feasibility_needed_for_local_rank_bound',hereditary_resource_feasibility_needed),
      ('conflict_free_composition_needed_for_order_k_global_lift',conflict_free_global_lift_not_valid_with_exclusive_resources),
      ('zero_cost_compensation_does_not_imply_empty_portfolio',zero_cost_does_not_mean_empty_portfolio),
      ('scalar_gain_cardinality_not_semantically_complete',scalar_gain_size_not_frontier_complete),
    ]
    print(f'SCRT Assumption Sharpness and Countermodel Audit v{VERSION}')
    for name,fn in tests:
        ok=bool(fn()); print(f'{name}:{"PASS" if ok else "FAIL"}')
        if not ok: raise SystemExit(1)
    print(f'countermodels:PASS:{len(tests)}/{len(tests)}')
    print('status:PASS')

def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True); g.add_argument('--self-test',action='store_true'); g.add_argument('--verify',action='store_true'); a=ap.parse_args(); run()
if __name__=='__main__': main()
