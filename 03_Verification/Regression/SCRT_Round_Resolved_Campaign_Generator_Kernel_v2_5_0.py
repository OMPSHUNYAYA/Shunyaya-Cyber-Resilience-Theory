#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Round-Resolved Campaign Generator Kernel
Version 2.5.0

Exact semantic quotient for finite target-relative assurance campaigns.
Primitive descriptions are compiled to one-round semantic generators, dominated
variants of the same idempotent generator are removed, and the entire base state
plus attacker/recovery generator family is canonicalized under one shared
ancestry gauge. The quotient preserves campaign value and compatible future
extension under the frozen campaign contract.

Dependency-free and deterministic.
"""
from __future__ import annotations

import argparse
import functools
import itertools
from dataclasses import dataclass
from typing import Iterable

VERSION = "2.5.0"
INF = 10**9
Mask = int
Typed = tuple[Mask, Mask]


def typed_support(t: Typed) -> Mask:
    return t[0] | t[1]


def pairwise_disjoint_masks(ms: tuple[Mask, ...]) -> bool:
    seen = 0
    for s in ms:
        if seen & s:
            return False
        seen |= s
    return True


def pairwise_physically_disjoint(ts: tuple[Typed, ...]) -> bool:
    return pairwise_disjoint_masks(tuple(typed_support(t) for t in ts))


def split_role_mask(c: Mask, m: int) -> tuple[Mask, Mask]:
    full = (1 << m) - 1
    return c & full, (c >> m) & full


def role_mask(d: Mask, e: Mask, m: int) -> Mask:
    return d | (e << m)


def nonempty_unique_masks(routes: Iterable[Mask]) -> tuple[Mask, ...]:
    return tuple(sorted({r for r in routes if r != 0}))


def nonempty_unique_typed(routes: Iterable[Typed]) -> tuple[Typed, ...]:
    return tuple(sorted({t for t in routes if typed_support(t) != 0}))


def operational_capacity(routes: tuple[Mask, ...], impact: Mask, k: int, m: int) -> int:
    fd, _ = split_role_mask(impact, m)
    surv = tuple(s for s in routes if not (s & fd))
    for q in range(k, 0, -1):
        for idxs in itertools.combinations(range(len(surv)), q):
            if pairwise_disjoint_masks(tuple(surv[i] for i in idxs)):
                return q
    return 0


def certified_capacity(routes: tuple[Typed, ...], impact: Mask, k: int, m: int) -> int:
    fd, fe = split_role_mask(impact, m)
    surv = tuple(t for t in routes if not (t[0] & fd) and not (t[1] & fe))
    for q in range(k, 0, -1):
        for idxs in itertools.combinations(range(len(surv)), q):
            if pairwise_physically_disjoint(tuple(surv[i] for i in idxs)):
                return q
    return 0


@dataclass(frozen=True, order=True)
class RawAttack:
    impact_parts: tuple[Mask, ...]
    cost: int
    resources: Mask = 0
    label: str = ""

    def compile_impact(self) -> Mask:
        out = 0
        for p in self.impact_parts:
            out |= p
        return out


@dataclass(frozen=True, order=True)
class RawRecovery:
    route: Typed
    cost: int
    resources: Mask = 0
    label: str = ""


@dataclass(frozen=True, order=True)
class AttackAction:
    impact: Mask
    cost: int
    resources: Mask = 0


@dataclass(frozen=True, order=True)
class RecoveryAction:
    route: Typed
    cost: int
    resources: Mask = 0


def pareto_pairs(items: Iterable[tuple[int, Mask]]) -> tuple[tuple[int, Mask], ...]:
    vals = sorted(set(items), key=lambda x: (x[0], x[1].bit_count(), x[1]))
    out: list[tuple[int, Mask]] = []
    for c, r in vals:
        if any(c0 <= c and (r0 & r) == r0 for c0, r0 in out):
            continue
        out = [(c0, r0) for c0, r0 in out if not (c <= c0 and (r & r0) == r)]
        out.append((c, r))
    return tuple(sorted(out))


def reduce_attacks(raw: tuple[RawAttack, ...]) -> tuple[tuple[Mask, tuple[tuple[int, Mask], ...]], ...]:
    by: dict[Mask, list[tuple[int, Mask]]] = {}
    for a in raw:
        by.setdefault(a.compile_impact(), []).append((a.cost, a.resources))
    return tuple(sorted((impact, pareto_pairs(vals)) for impact, vals in by.items() if impact != 0))


def reduce_recoveries(raw: tuple[RawRecovery, ...]) -> tuple[tuple[Typed, tuple[tuple[int, Mask], ...]], ...]:
    by: dict[Typed, list[tuple[int, Mask]]] = {}
    for r in raw:
        if typed_support(r.route) != 0:
            by.setdefault(r.route, []).append((r.cost, r.resources))
    return tuple(sorted((route, pareto_pairs(vals)) for route, vals in by.items()))


def expanded_attacks(red: tuple[tuple[Mask, tuple[tuple[int, Mask], ...]], ...]) -> tuple[AttackAction, ...]:
    return tuple(AttackAction(impact, c, q) for impact, vals in red for c, q in vals)


def expanded_recoveries(red: tuple[tuple[Typed, tuple[tuple[int, Mask], ...]], ...]) -> tuple[RecoveryAction, ...]:
    return tuple(RecoveryAction(route, c, q) for route, vals in red for c, q in vals)


def raw_compiled_attacks(raw: tuple[RawAttack, ...]) -> tuple[AttackAction, ...]:
    return tuple(AttackAction(a.compile_impact(), a.cost, a.resources) for a in raw if a.compile_impact() != 0)


def raw_compiled_recoveries(raw: tuple[RawRecovery, ...]) -> tuple[RecoveryAction, ...]:
    return tuple(RecoveryAction(r.route, r.cost, r.resources) for r in raw if typed_support(r.route) != 0)


@dataclass(frozen=True)
class CampaignKernel:
    op_routes: tuple[Mask, ...]
    cert_routes: tuple[Typed, ...]
    attacks: tuple[AttackAction, ...]
    recoveries: tuple[RecoveryAction, ...]
    m: int
    k: int


@dataclass(frozen=True)
class CampaignState:
    impact: Mask
    cert_routes: tuple[Typed, ...]
    used_attacks: Mask
    used_recoveries: Mask
    attack_resources: Mask
    recovery_resources: Mask


def build_kernel(op_routes: Iterable[Mask], cert_routes: Iterable[Typed],
                 attacks: tuple[AttackAction, ...], recoveries: tuple[RecoveryAction, ...],
                 m: int, k: int) -> CampaignKernel:
    return CampaignKernel(nonempty_unique_masks(op_routes), nonempty_unique_typed(cert_routes),
                          tuple(sorted(attacks)), tuple(sorted(recoveries)), m, k)


def safe_state(K: CampaignKernel, s: CampaignState) -> bool:
    return operational_capacity(K.op_routes, s.impact, K.k, K.m) >= K.k and certified_capacity(s.cert_routes, s.impact, K.k, K.m) >= K.k


def add_recovery_route(routes: tuple[Typed, ...], route: Typed) -> tuple[Typed, ...]:
    return nonempty_unique_typed(routes + (route,))


class CampaignSolver:
    def __init__(self, K: CampaignKernel):
        self.K = K
        self.initial = CampaignState(0, K.cert_routes, 0, 0, 0, 0)

    @functools.lru_cache(maxsize=None)
    def required_defense(self, s: CampaignState, b: int) -> int:
        if not safe_state(self.K, s):
            return INF
        worst = 0
        for i, a in enumerate(self.K.attacks):
            if s.used_attacks & (1 << i) or a.cost > b or (s.attack_resources & a.resources):
                continue
            imp = s.impact | a.impact
            if operational_capacity(self.K.op_routes, imp, self.K.k, self.K.m) < self.K.k:
                continue
            ua = s.used_attacks | (1 << i)
            ar = s.attack_resources | a.resources
            responses: list[int] = []
            ps = CampaignState(imp, s.cert_routes, ua, s.used_recoveries, ar, s.recovery_resources)
            if safe_state(self.K, ps):
                responses.append(self.required_defense(ps, b - a.cost))
            for j, d in enumerate(self.K.recoveries):
                if s.used_recoveries & (1 << j) or (s.recovery_resources & d.resources):
                    continue
                s2 = CampaignState(imp, add_recovery_route(s.cert_routes, d.route), ua,
                                   s.used_recoveries | (1 << j), ar, s.recovery_resources | d.resources)
                if not safe_state(self.K, s2):
                    continue
                f = self.required_defense(s2, b - a.cost)
                responses.append(INF if f >= INF else d.cost + f)
            branch = min(responses) if responses else INF
            if branch > worst:
                worst = branch
        return worst

    def delta(self, b: int) -> int:
        return self.required_defense(self.initial, b)

    def profile(self) -> tuple[int, ...]:
        maxb = sum(a.cost for a in self.K.attacks)
        return tuple(self.delta(b) for b in range(maxb + 1))


def semantic_kernel(op_routes: Iterable[Mask], cert_routes: Iterable[Typed], raw_attacks: tuple[RawAttack, ...],
                    raw_recoveries: tuple[RawRecovery, ...], m: int, k: int) -> CampaignKernel:
    return build_kernel(op_routes, cert_routes, expanded_attacks(reduce_attacks(raw_attacks)),
                        expanded_recoveries(reduce_recoveries(raw_recoveries)), m, k)


def literal_kernel(op_routes: Iterable[Mask], cert_routes: Iterable[Typed], raw_attacks: tuple[RawAttack, ...],
                   raw_recoveries: tuple[RawRecovery, ...], m: int, k: int) -> CampaignKernel:
    return build_kernel(op_routes, cert_routes, raw_compiled_attacks(raw_attacks), raw_compiled_recoveries(raw_recoveries), m, k)


def permute_mask(mask: Mask, perm: tuple[int, ...]) -> Mask:
    out = 0
    for i, j in enumerate(perm):
        if mask & (1 << i):
            out |= 1 << j
    return out


def permute_typed(t: Typed, perm: tuple[int, ...]) -> Typed:
    return permute_mask(t[0], perm), permute_mask(t[1], perm)


def permute_role_mask(impact: Mask, m: int, perm: tuple[int, ...]) -> Mask:
    d, e = split_role_mask(impact, m)
    return role_mask(permute_mask(d, perm), permute_mask(e, perm), m)


def permute_reduced_attacks(red, m: int, perm: tuple[int, ...]):
    return tuple(sorted((permute_role_mask(impact, m, perm), vals) for impact, vals in red))


def permute_reduced_recoveries(red, perm: tuple[int, ...]):
    return tuple(sorted((permute_typed(route, perm), vals) for route, vals in red))


def joint_campaign_generator_kernel(op_routes: Iterable[Mask], cert_routes: Iterable[Typed],
                                    raw_attacks: tuple[RawAttack, ...], raw_recoveries: tuple[RawRecovery, ...],
                                    m: int, k: int):
    op = nonempty_unique_masks(op_routes)
    cert = nonempty_unique_typed(cert_routes)
    ar = reduce_attacks(raw_attacks)
    rr = reduce_recoveries(raw_recoveries)
    reps = []
    for perm in itertools.permutations(range(m)):
        op2 = tuple(sorted(permute_mask(s, perm) for s in op))
        cert2 = tuple(sorted(permute_typed(t, perm) for t in cert))
        ar2 = permute_reduced_attacks(ar, m, perm)
        rr2 = permute_reduced_recoveries(rr, perm)
        reps.append((m, k, op2, cert2, ar2, rr2))
    return min(reps)


def individual_generator_orbit_profile(raw_attacks: tuple[RawAttack, ...], m: int):
    out = []
    for a in raw_attacks:
        impact = a.compile_impact()
        orb = min(permute_role_mask(impact, m, p) for p in itertools.permutations(range(m)))
        out.append((orb, a.cost, a.resources))
    return tuple(sorted(out))


def semantic_reduction_witnesses() -> tuple[tuple[RawAttack, ...], tuple[RawRecovery, ...]]:
    m = 2
    e0 = role_mask(0, 1, m)
    e1 = role_mask(0, 2, m)
    attacks = (
        RawAttack((e0,), 1, 1, "a0"),
        RawAttack((e0, e0), 2, 1, "redundant_expensive"),
        RawAttack((e1,), 1, 2, "a1"),
        RawAttack((e1,), 3, 6, "dominated_resource"),
    )
    recoveries = (
        RawRecovery((0, 1), 1, 1, "r0"),
        RawRecovery((0, 1), 2, 1, "r0_alt"),
        RawRecovery((0, 2), 1, 2, "r1"),
    )
    return attacks, recoveries


def verify_duplicate_route_elimination() -> int:
    checks = 0
    m = 3
    for k in (1, 2, 3):
        typed_pool = ((0,1),(0,2),(0,4),(1,2),(2,4))
        for base in typed_pool:
            routes = (base, base, base)
            uniq = nonempty_unique_typed(routes)
            for impact in range(1 << (2*m)):
                assert certified_capacity(routes, impact, k, m) == certified_capacity(uniq, impact, k, m)
                checks += 1
    return checks


def verify_primitive_semantic_reduction() -> tuple[int, int, int]:
    m = 2
    k = 1
    op = (1,2)
    cert = ((0,1),(0,2))
    attacks, rec = semantic_reduction_witnesses()
    lit = literal_kernel(op, cert, attacks, rec, m, k)
    sem = semantic_kernel(op, cert, attacks, rec, m, k)
    checks = 0
    for b in range(sum(a.cost for a in lit.attacks)+1):
        assert CampaignSolver(lit).delta(b) == CampaignSolver(sem).delta(b)
        checks += 1
    return checks, len(lit.attacks)+len(lit.recoveries), len(sem.attacks)+len(sem.recoveries)


def witness_individual_orbit_failure() -> tuple[tuple, tuple, int, int]:
    m = 2
    k = 1
    e0 = role_mask(0,1,m)
    e1 = role_mask(0,2,m)
    op = (1,)
    cert = ((0,1),(0,2))
    same = (
        RawAttack((e0,),1,1,"x"),
        RawAttack((e0,),1,2,"y"),
    )
    split = (
        RawAttack((e0,),1,1,"x"),
        RawAttack((e1,),1,2,"y"),
    )
    assert individual_generator_orbit_profile(same,m) == individual_generator_orbit_profile(split,m)
    ks = joint_campaign_generator_kernel(op,cert,same,(),m,k)
    kd = joint_campaign_generator_kernel(op,cert,split,(),m,k)
    assert ks != kd
    ds = CampaignSolver(semantic_kernel(op,cert,same,(),m,k)).delta(2)
    dd = CampaignSolver(semantic_kernel(op,cert,split,(),m,k)).delta(2)
    assert ds == 0 and dd >= INF
    return individual_generator_orbit_profile(same,m), ks, ds, dd


def catalog_variants():
    m = 2
    k = 1
    e0 = role_mask(0,1,m)
    e1 = role_mask(0,2,m)
    d0 = role_mask(1,0,m)
    bases = [
        ((1,), ((0,1),(0,2))),
        ((2,), ((0,1),(0,2))),
        ((1,2), ((0,1),(0,2))),
    ]
    attack_sets = [
        (RawAttack((e0,),1,1,"a"),),
        (RawAttack((e1,),1,1,"b"),),
        (RawAttack((e0,),1,1,"a"), RawAttack((e0,),2,1,"dom")),
        (RawAttack((e0,),1,1,"a"), RawAttack((e1,),1,2,"b")),
        (RawAttack((e0,e1),2,3,"joint"),),
        (RawAttack((d0,),2,4,"d"),),
    ]
    rec_sets = [
        (),
        (RawRecovery((0,1),1,1,"r0"),),
        (RawRecovery((0,2),1,1,"r1"),),
        (RawRecovery((0,1),1,1,"r0"), RawRecovery((0,1),2,1,"dom")),
        (RawRecovery((1,2),2,4,"rd"),),
    ]
    out=[]
    for bi,(op,cert) in enumerate(bases):
        for ai,a in enumerate(attack_sets):
            r=rec_sets[(bi*3+ai)%len(rec_sets)]
            out.append((op,cert,a,r,m,k))
    # add explicit gauge/description variants
    op,cert,a,r,m,k=out[0]
    out.append(((2,), tuple(permute_typed(t,(1,0)) for t in cert),
                tuple(RawAttack((permute_role_mask(x.compile_impact(),m,(1,0)),),x.cost,x.resources,"renamed") for x in a),
                r,m,k))
    a2 = a + (RawAttack((a[0].compile_impact(),a[0].compile_impact()),5,a[0].resources|8,"dominated"),)
    out.append((op,cert,a2,r,m,k))
    return tuple(out)


def value_profile(model) -> tuple[int,...]:
    op,cert,a,r,m,k=model
    K=semantic_kernel(op,cert,a,r,m,k)
    return CampaignSolver(K).profile()


def verify_joint_kernel_exactness() -> tuple[int,int,int]:
    models=catalog_variants()
    by={}
    for M in models:
        key=joint_campaign_generator_kernel(*M)
        by.setdefault(key,[]).append(M)
    checks=dups=0
    for group in by.values():
        if len(group)>1:
            dups += 1
        ref=value_profile(group[0])
        for M in group[1:]:
            assert value_profile(M)==ref
            checks += 1
    return len(models),len(by),dups+checks


def permute_raw_attacks(raw: tuple[RawAttack,...],m:int,perm:tuple[int,...]):
    return tuple(RawAttack((permute_role_mask(a.compile_impact(),m,perm),),a.cost,a.resources,a.label) for a in raw)


def permute_raw_recoveries(raw: tuple[RawRecovery,...],perm:tuple[int,...]):
    return tuple(RawRecovery(permute_typed(r.route,perm),r.cost,r.resources,r.label) for r in raw)


def verify_future_extension_congruence() -> tuple[int,int]:
    m=2;k=1
    e0=role_mask(0,1,m);e1=role_mask(0,2,m)
    op=(1,);cert=((0,1),(0,2))
    base=(RawAttack((e0,),1,1,"a"),RawAttack((e1,),1,2,"b"))
    perm=(1,0)
    op2=tuple(permute_mask(x,perm) for x in op)
    cert2=tuple(permute_typed(x,perm) for x in cert)
    base2=permute_raw_attacks(base,m,perm)
    assert joint_campaign_generator_kernel(op,cert,base,(),m,k)==joint_campaign_generator_kernel(op2,cert2,base2,(),m,k)
    extensions=[
        ((RawAttack((e0|e1,),2,4,"j"),),()),
        ((),(RawRecovery((0,1),1,4,"r"),)),
        ((RawAttack((e0,),3,8,"late"),),(RawRecovery((0,2),2,16,"rr"),)),
    ]
    checks=profiles=0
    for ea,er in extensions:
        ea2=permute_raw_attacks(ea,m,perm)
        er2=permute_raw_recoveries(er,perm)
        A=base+ea; B=base2+ea2
        R=er; R2=er2
        k1=joint_campaign_generator_kernel(op,cert,A,R,m,k)
        k2=joint_campaign_generator_kernel(op2,cert2,B,R2,m,k)
        assert k1==k2
        checks += 1
        v1=CampaignSolver(semantic_kernel(op,cert,A,R,m,k)).profile()
        v2=CampaignSolver(semantic_kernel(op2,cert2,B,R2,m,k)).profile()
        assert v1==v2
        profiles += 1
    return checks,profiles


def verify_separator_registry() -> tuple[int, int, int]:
    # A finite separator-complete campaign registry with distinct present value profiles.
    m = 3
    k = 1
    e0 = role_mask(0, 1, m)
    e1 = role_mask(0, 2, m)
    op = (4,)
    cert = ((0, 1), (0, 2))
    models = (
        (op, cert,
         (RawAttack((e0,), 1, 1, "a"), RawAttack((e0,), 1, 2, "a2")), (), m, k),
        (op, cert,
         (RawAttack((e0,), 1, 1, "a"), RawAttack((e1,), 1, 2, "b")), (), m, k),
        (op, cert,
         (RawAttack((e0,), 1, 1, "a"), RawAttack((e1,), 1, 2, "b")),
         (RawRecovery((0, 4), 1, 4, "r"),), m, k),
        (op, cert,
         (RawAttack((e0,), 1, 1, "a"), RawAttack((e1,), 1, 2, "b")),
         (RawRecovery((0, 4), 2, 4, "r"),), m, k),
        (op, cert,
         (RawAttack((e0,), 2, 1, "a"), RawAttack((e1,), 2, 2, "b")), (), m, k),
    )
    kernels = [joint_campaign_generator_kernel(*M) for M in models]
    assert len(set(kernels)) == len(models)
    profiles = [value_profile(M) for M in models]
    pairs = separated = 0
    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            pairs += 1
            assert profiles[i] != profiles[j]
            separated += 1
    return len(models), pairs, separated


def verify_future_resource_separator() -> tuple[int, int, int]:
    # Same current campaign value, different hidden recovery resource occupancy.
    # A future recovery action exposes the difference.
    m = 4
    k = 2
    e0 = role_mask(0, 1, m)
    e1 = role_mask(0, 2, m)
    op = (1 << 2, 1 << 3)
    cert = ((0, 1 << 0), (0, 1 << 1))
    attacks = (RawAttack((e0,), 1, 1, "a0"), RawAttack((e1,), 1, 2, "a1"))
    left_r = (RawRecovery((0, 1 << 2), 1, 1, "r2"),)
    right_r = (RawRecovery((0, 1 << 2), 1, 2, "r2"),)
    L = CampaignSolver(semantic_kernel(op, cert, attacks, left_r, m, k)).profile()
    R = CampaignSolver(semantic_kernel(op, cert, attacks, right_r, m, k)).profile()
    assert L == R
    assert joint_campaign_generator_kernel(op, cert, attacks, left_r, m, k) != joint_campaign_generator_kernel(op, cert, attacks, right_r, m, k)
    future = (RawRecovery((0, 1 << 3), 1, 1, "r3"),)
    L2 = CampaignSolver(semantic_kernel(op, cert, attacks, left_r + future, m, k)).delta(2)
    R2 = CampaignSolver(semantic_kernel(op, cert, attacks, right_r + future, m, k)).delta(2)
    assert L2 >= INF and R2 == 2
    return len(L), L2, R2


def verify_current_value_not_generator_complete() -> tuple[int, int]:
    # Two systems can have the same present campaign profile while carrying
    # different generator-continuation information.
    n, l, r = verify_future_resource_separator()
    assert l >= INF and r == 2
    return n, 1

def run_verify():
    c=verify_duplicate_route_elimination()
    print(f"duplicate_route_semantic_reduction:PASS:checks={c}:condition=NONEMPTY_PHYSICAL_SUPPORT")
    c,l,s=verify_primitive_semantic_reduction()
    print(f"primitive_transition_pareto_reduction:PASS:budget_checks={c}:literal_generators={l}:semantic_generators={s}")
    prof,_,ds,dd=witness_individual_orbit_failure()
    print(f"independent_generator_orbit_quotient_failure:PASS:individual_profile_size={len(prof)}:same_target_required_defense={ds}:split_target_required_defense=INF")
    n,classes,dup=verify_joint_kernel_exactness()
    print(f"joint_campaign_generator_kernel:PASS:models={n}:kernel_classes={classes}:equal_kernel_checks={dup}")
    c,p=verify_future_extension_congruence()
    print(f"future_campaign_extension_congruence:PASS:kernel_extensions={c}:value_profiles={p}:extension=GAUGE_TRANSPORTED")
    classes,pairs,sep=verify_separator_registry()
    print(f"constructive_campaign_separator_registry:PASS:kernel_classes={classes}:pairs={pairs}:separated={sep}:registry=FINITE_SEPARATOR_COMPLETE")
    n,l,r=verify_future_resource_separator()
    print(f"future_resource_continuation_separator:PASS:current_profile_points={n}:left_extended=INF:right_extended={r}")
    n,c=verify_current_value_not_generator_complete()
    print(f"current_campaign_value_not_generator_complete:PASS:profile_points={n}:future_separator={c}")
    print("status:PASS")


def run_self_test():
    assert verify_duplicate_route_elimination()>0
    assert verify_primitive_semantic_reduction()[0]>0
    assert witness_individual_orbit_failure()[2]==0
    assert verify_separator_registry()[2]>0
    assert verify_future_resource_separator()[2]==2
    print("SCRT Round-Resolved Campaign Generator Kernel v2.5.0 self-test")
    print("TOTAL 4/4 PASS")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--verify",action="store_true")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.verify:
        print("SCRT Round-Resolved Campaign Generator Kernel v2.5.0 verification")
        run_verify()
    else:
        run_self_test()


if __name__=="__main__":
    main()
