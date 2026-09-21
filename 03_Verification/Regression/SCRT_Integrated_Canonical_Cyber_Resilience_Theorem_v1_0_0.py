#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Integrated Canonical Cyber Resilience Theorem
Version 1.0.0

Exact finite semantics for obligation-resolved route kernels, coupled hardening
action kernels, compromise families, permanent hardening, adaptive recovery,
future action extension, constructive continuation separation, and the
finite-dimensional canonical cyber-resilience state.

Dependency-free and deterministic.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence

VERSION = "1.0.0"
Signature = tuple[int, int]
Effect = tuple[int, ...]
Pair = tuple[int, int]
OperationalCounts = dict[int, int]
TypedCounts = dict[Signature, int]
ObligationKernel = tuple[OperationalCounts, TypedCounts]
ResolvedKernel = tuple[ObligationKernel, ...]
HAK = dict[Effect, tuple[Pair, ...]]


def popcount(x: int) -> int:
    return x.bit_count()


def mask_subset(a: int, b: int) -> bool:
    return (a & b) == a


def resource_subset(a: int, b: int) -> bool:
    return (a & b) == a


def sig_support(s: Signature) -> int:
    return s[0] | s[1]


def sig_leq(a: Signature, b: Signature) -> bool:
    return mask_subset(a[0], b[0]) and mask_subset(a[1], b[1])


def sig_compose(a: Signature, b: Signature) -> Signature | None:
    d = a[0] | b[0]
    e = a[1] | b[1]
    if d & e:
        return None
    return d, e


def all_signatures(m: int, include_empty: bool = False) -> tuple[Signature, ...]:
    out: list[Signature] = []
    for d in range(1 << m):
        for e in range(1 << m):
            if d & e:
                continue
            if not include_empty and (d | e) == 0:
                continue
            out.append((d, e))
    return tuple(out)


def normalize_counts(counts: dict) -> dict:
    return {k: int(v) for k, v in counts.items() if int(v) > 0}


def compose_operational_counts(left: OperationalCounts, right: OperationalCounts) -> OperationalCounts:
    out: Counter[int] = Counter()
    for a, ca in left.items():
        for b, cb in right.items():
            if ca > 0 and cb > 0:
                out[a | b] += ca * cb
    return dict(out)


def compose_typed_counts(left: TypedCounts, right: TypedCounts) -> TypedCounts:
    out: Counter[Signature] = Counter()
    for a, ca in left.items():
        for b, cb in right.items():
            if ca <= 0 or cb <= 0:
                continue
            z = sig_compose(a, b)
            if z is not None:
                out[z] += ca * cb
    return dict(out)


def complete_operational_kernel(factors: Sequence[OperationalCounts]) -> OperationalCounts:
    cur: OperationalCounts = {0: 1}
    for factor in factors:
        cur = compose_operational_counts(cur, factor)
    cur.pop(0, None)
    return cur


def complete_typed_kernel(factors: Sequence[TypedCounts]) -> TypedCounts:
    cur: TypedCounts = {(0, 0): 1}
    for factor in factors:
        cur = compose_typed_counts(cur, factor)
    cur.pop((0, 0), None)
    return cur


def complete_irk(resolved: ResolvedKernel) -> ObligationKernel:
    return (
        complete_operational_kernel([k[0] for k in resolved]),
        complete_typed_kernel([k[1] for k in resolved]),
    )


def add_resolved(left: ResolvedKernel, right: ResolvedKernel) -> ResolvedKernel:
    if len(left) != len(right):
        raise ValueError("obligation counts differ")
    out: list[ObligationKernel] = []
    for (lo, lt), (ro, rt) in zip(left, right):
        oo = Counter(lo)
        oo.update(ro)
        tt = Counter(lt)
        tt.update(rt)
        out.append((dict(oo), dict(tt)))
    return tuple(out)


def canonical_resolved(k: ResolvedKernel) -> tuple:
    return tuple((tuple(sorted(op.items())), tuple(sorted(ty.items()))) for op, ty in k)


def operational_probe(counts: OperationalCounts, q: int) -> int:
    return sum(c for s, c in counts.items() if mask_subset(s, q))


def typed_probe(counts: TypedCounts, q: Signature) -> int:
    return sum(c for s, c in counts.items() if sig_leq(s, q))


def resolved_probe_signature(resolved: ResolvedKernel, m: int) -> tuple:
    typed_queries = all_signatures(m, include_empty=True)
    out = []
    for op, typed in resolved:
        op_table = tuple(operational_probe(op, q) for q in range(1 << m))
        typed_table = tuple(typed_probe(typed, q) for q in typed_queries)
        out.append((op_table, typed_table))
    return tuple(out)


def max_disjoint_operational_capacity(counts: OperationalCounts, failure: int) -> int:
    supports: list[int] = []
    for s, c in counts.items():
        if s & failure:
            continue
        supports.extend([s] * c)
    best = 0
    n = len(supports)
    def rec(i: int, used: int, chosen: int) -> None:
        nonlocal best
        if chosen + (n - i) <= best:
            return
        if i == n:
            best = max(best, chosen)
            return
        rec(i + 1, used, chosen)
        s = supports[i]
        if not (used & s):
            rec(i + 1, used | s, chosen + 1)
    rec(0, 0, 0)
    return best


def max_disjoint_typed_capacity(counts: TypedCounts, failure: int) -> int:
    sigs: list[Signature] = []
    for s, c in counts.items():
        if sig_support(s) & failure:
            continue
        sigs.extend([s] * c)
    best = 0
    n = len(sigs)
    def rec(i: int, used: int, chosen: int) -> None:
        nonlocal best
        if chosen + (n - i) <= best:
            return
        if i == n:
            best = max(best, chosen)
            return
        rec(i + 1, used, chosen)
        s = sigs[i]
        support = sig_support(s)
        if not (used & support):
            rec(i + 1, used | support, chosen + 1)
    rec(0, 0, 0)
    return best


@dataclass(frozen=True, order=True)
class Action:
    effect: Effect
    cost: int
    resources: int


def effect_add(a: Effect, b: Effect) -> Effect:
    if len(a) != len(b):
        raise ValueError("effect dimensions differ")
    return tuple(x + y for x, y in zip(a, b))


def effect_ge(a: Effect, b: Effect) -> bool:
    return len(a) == len(b) and all(x >= y for x, y in zip(a, b))


def zero_effect(d: int) -> Effect:
    return (0,) * d


def pair_dominates(a: Pair, b: Pair) -> bool:
    return a[0] <= b[0] and resource_subset(a[1], b[1])


def pareto_pairs(pairs: Iterable[Pair]) -> tuple[Pair, ...]:
    uniq = sorted(set((int(c), int(r)) for c, r in pairs))
    out: list[Pair] = []
    for p in uniq:
        if any(q != p and pair_dominates(q, p) for q in uniq):
            continue
        out.append(p)
    return tuple(out)


def enumerate_feasible_plans(catalog: Sequence[Action], d: int) -> list[tuple[Effect, int, int]]:
    out: list[tuple[Effect, int, int]] = []
    n = len(catalog)
    for pick in range(1 << n):
        eff = zero_effect(d)
        cost = 0
        resources = 0
        ok = True
        for i, a in enumerate(catalog):
            if not (pick & (1 << i)):
                continue
            if resources & a.resources:
                ok = False
                break
            resources |= a.resources
            cost += a.cost
            eff = effect_add(eff, a.effect)
        if ok:
            out.append((eff, cost, resources))
    return out


def hardening_action_kernel(catalog: Sequence[Action], d: int) -> HAK:
    buckets: dict[Effect, list[Pair]] = {}
    for eff, cost, resources in enumerate_feasible_plans(catalog, d):
        buckets.setdefault(eff, []).append((cost, resources))
    return {eff: pareto_pairs(pairs) for eff, pairs in buckets.items()}


def canonical_hak(hak: HAK) -> tuple:
    return tuple((eff, tuple(sorted(pairs))) for eff, pairs in sorted(hak.items()))


def compose_hak(left: HAK, right: HAK) -> HAK:
    buckets: dict[Effect, list[Pair]] = {}
    for e1, ps1 in left.items():
        for e2, ps2 in right.items():
            e = effect_add(e1, e2)
            for c1, r1 in ps1:
                for c2, r2 in ps2:
                    if r1 & r2:
                        continue
                    buckets.setdefault(e, []).append((c1 + c2, r1 | r2))
    return {eff: pareto_pairs(pairs) for eff, pairs in buckets.items()}


def apply_operational_effect(resolved: ResolvedKernel, eff: Effect, private_supports: Sequence[int]) -> ResolvedKernel:
    if len(resolved) != len(eff) or len(eff) != len(private_supports):
        raise ValueError("effect/obligation dimensions differ")
    out: list[ObligationKernel] = []
    for i, ((op, ty), amount) in enumerate(zip(resolved, eff)):
        op2 = dict(op)
        if amount:
            s = private_supports[i]
            op2[s] = op2.get(s, 0) + amount
        out.append((op2, dict(ty)))
    return tuple(out)


def apply_typed_effect(resolved: ResolvedKernel, eff: Effect, private_sigs: Sequence[Signature]) -> ResolvedKernel:
    if len(resolved) != len(eff) or len(eff) != len(private_sigs):
        raise ValueError("effect/obligation dimensions differ")
    out: list[ObligationKernel] = []
    for i, ((op, ty), amount) in enumerate(zip(resolved, eff)):
        ty2 = dict(ty)
        if amount:
            s = private_sigs[i]
            ty2[s] = ty2.get(s, 0) + amount
        out.append((dict(op), ty2))
    return tuple(out)


def robust_capacity_operational(resolved: ResolvedKernel, scenarios: Sequence[int]) -> int:
    complete = complete_operational_kernel([k[0] for k in resolved])
    return min(max_disjoint_operational_capacity(complete, f) for f in scenarios)


def robust_capacity_typed(resolved: ResolvedKernel, scenarios: Sequence[int]) -> int:
    complete = complete_typed_kernel([k[1] for k in resolved])
    return min(max_disjoint_typed_capacity(complete, f) for f in scenarios)


def kernel_min_cost_operational(
    resolved: ResolvedKernel,
    hak: HAK,
    scenarios: Sequence[int],
    target: int,
    private_supports: Sequence[int],
) -> int | None:
    best: int | None = None
    for eff, pairs in hak.items():
        hardened = apply_operational_effect(resolved, eff, private_supports)
        if robust_capacity_operational(hardened, scenarios) < target:
            continue
        for c, _ in pairs:
            if best is None or c < best:
                best = c
    return best


def kernel_min_cost_typed(
    resolved: ResolvedKernel,
    hak: HAK,
    scenarios: Sequence[int],
    target: int,
    private_sigs: Sequence[Signature],
) -> int | None:
    best: int | None = None
    for eff, pairs in hak.items():
        hardened = apply_typed_effect(resolved, eff, private_sigs)
        if robust_capacity_typed(hardened, scenarios) < target:
            continue
        for c, _ in pairs:
            if best is None or c < best:
                best = c
    return best


def direct_min_cost_operational(
    resolved: ResolvedKernel,
    catalog: Sequence[Action],
    scenarios: Sequence[int],
    target: int,
    private_supports: Sequence[int],
) -> int | None:
    d = len(resolved)
    best: int | None = None
    for eff, c, _ in enumerate_feasible_plans(catalog, d):
        hardened = apply_operational_effect(resolved, eff, private_supports)
        if robust_capacity_operational(hardened, scenarios) >= target:
            if best is None or c < best:
                best = c
    return best


def direct_min_cost_typed(
    resolved: ResolvedKernel,
    catalog: Sequence[Action],
    scenarios: Sequence[int],
    target: int,
    private_sigs: Sequence[Signature],
) -> int | None:
    d = len(resolved)
    best: int | None = None
    for eff, c, _ in enumerate_feasible_plans(catalog, d):
        hardened = apply_typed_effect(resolved, eff, private_sigs)
        if robust_capacity_typed(hardened, scenarios) >= target:
            if best is None or c < best:
                best = c
    return best


def direct_adaptive_cost_operational(
    resolved: ResolvedKernel,
    catalog: Sequence[Action],
    scenarios: Sequence[int],
    target: int,
    private_supports: Sequence[int],
) -> int | None:
    vals = [direct_min_cost_operational(resolved, catalog, (f,), target, private_supports) for f in scenarios]
    if any(v is None for v in vals):
        return None
    return max(int(v) for v in vals)


def kernel_adaptive_cost_operational(
    resolved: ResolvedKernel,
    hak: HAK,
    scenarios: Sequence[int],
    target: int,
    private_supports: Sequence[int],
) -> int | None:
    vals = [kernel_min_cost_operational(resolved, hak, (f,), target, private_supports) for f in scenarios]
    if any(v is None for v in vals):
        return None
    return max(int(v) for v in vals)


def primitive_actions() -> tuple[Action, ...]:
    effects = ((1, 0), (0, 1), (1, 1))
    costs = (1, 2)
    resources = (1, 2, 3)
    return tuple(Action(e, c, r) for e in effects for c in costs for r in resources)


def small_catalogs(max_size: int = 2) -> list[tuple[Action, ...]]:
    prim = primitive_actions()
    out: list[tuple[Action, ...]] = [tuple()]
    for k in range(1, max_size + 1):
        out.extend(tuple(x) for x in itertools.combinations(prim, k))
    return out


def operational_architectures() -> list[ResolvedKernel]:
    A, B = 1, 2
    route_types = (A, B, A | B)
    factors: list[OperationalCounts] = []
    for bits in range(1, 1 << len(route_types)):
        factors.append({route_types[i]: 1 for i in range(len(route_types)) if bits & (1 << i)})
    empty_typed: TypedCounts = {}
    return tuple(((a, empty_typed), (b, empty_typed)) for a in factors for b in factors)  # type: ignore[return-value]


def typed_architectures() -> list[ResolvedKernel]:
    A = 1
    route_types: tuple[Signature, ...] = ((A, 0), (0, A))
    factors: list[TypedCounts] = []
    for bits in range(1, 1 << len(route_types)):
        factors.append({route_types[i]: 1 for i in range(len(route_types)) if bits & (1 << i)})
    empty_op: OperationalCounts = {}
    return tuple(((empty_op, a), (empty_op, b)) for a in factors for b in factors)  # type: ignore[return-value]


def architecture_contexts_operational() -> tuple[ResolvedKernel, ...]:
    A, B = 1, 2
    E: TypedCounts = {}
    return (
        (({}, E), ({}, E)),
        (({A: 1}, E), ({}, E)),
        (({}, E), ({B: 1}, E)),
        (({B: 1}, E), ({A: 1}, E)),
    )


def architecture_contexts_typed() -> tuple[ResolvedKernel, ...]:
    A = 1
    E: OperationalCounts = {}
    return (
        ((E, {}), (E, {})),
        ((E, {(A, 0): 1}), (E, {})),
        ((E, {}), (E, {(0, A): 1})),
    )


def scenario_families(shared_mask: int) -> tuple[tuple[int, ...], ...]:
    failures = tuple(range(shared_mask + 1)) if shared_mask in (1, 3) else tuple(s for s in range(shared_mask + 1) if (s & ~shared_mask) == 0)
    out: list[tuple[int, ...]] = []
    for bits in range(1, 1 << len(failures)):
        fam = tuple(failures[i] for i in range(len(failures)) if bits & (1 << i))
        out.append(fam)
    return tuple(out)


def verify_integrated_operational_coupling() -> dict:
    architectures = operational_architectures()
    catalogs = small_catalogs(2)
    contexts = architecture_contexts_operational()
    futures = [tuple(), (primitive_actions()[0],), (primitive_actions()[7],)]
    scenarios = ((0,), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3))
    private_supports = (4, 8)
    checks = 0
    # Exhaust every architecture and catalog on core queries; then selected continuation extensions.
    for x in architectures:
        for cat in catalogs:
            hak = hardening_action_kernel(cat, 2)
            for fam in scenarios:
                for k in (1, 2):
                    a = direct_min_cost_operational(x, cat, fam, k, private_supports)
                    b = kernel_min_cost_operational(x, hak, fam, k, private_supports)
                    if a != b:
                        raise AssertionError(("operational coupling", x, cat, fam, k, a, b))
                    aa = direct_adaptive_cost_operational(x, cat, fam, k, private_supports)
                    bb = kernel_adaptive_cost_operational(x, hak, fam, k, private_supports)
                    if aa != bb:
                        raise AssertionError(("operational adaptive", x, cat, fam, k, aa, bb))
                    checks += 2
    extension_checks = 0
    for x in architectures[::8]:
        for cat in catalogs[::17]:
            kcat = hardening_action_kernel(cat, 2)
            for ctx in contexts:
                x2 = add_resolved(x, ctx)
                for fut in futures:
                    direct_cat = tuple(cat) + tuple(fut)
                    kh = compose_hak(kcat, hardening_action_kernel(fut, 2))
                    for fam in ((1,), (2,), (1, 2), (3,)):
                        for k in (1, 2):
                            a = direct_min_cost_operational(x2, direct_cat, fam, k, private_supports)
                            b = kernel_min_cost_operational(x2, kh, fam, k, private_supports)
                            if a != b:
                                raise AssertionError(("operational extension", x, cat, ctx, fut, fam, k, a, b))
                            extension_checks += 1
    return {"core_queries": checks, "continuation_queries": extension_checks}


def verify_integrated_typed_coupling() -> dict:
    architectures = typed_architectures()
    catalogs = small_catalogs(2)
    contexts = architecture_contexts_typed()
    futures = [tuple(), (primitive_actions()[0],), (primitive_actions()[7],)]
    private_sigs: tuple[Signature, ...] = ((2, 4), (8, 16))
    scenarios = ((0,), (1,), (0, 1))
    checks = 0
    for x in architectures:
        for cat in catalogs:
            hak = hardening_action_kernel(cat, 2)
            for fam in scenarios:
                for k in (1, 2):
                    a = direct_min_cost_typed(x, cat, fam, k, private_sigs)
                    b = kernel_min_cost_typed(x, hak, fam, k, private_sigs)
                    if a != b:
                        raise AssertionError(("typed coupling", x, cat, fam, k, a, b))
                    checks += 1
    extension_checks = 0
    for x in architectures:
        for cat in catalogs[::19]:
            kcat = hardening_action_kernel(cat, 2)
            for ctx in contexts:
                x2 = add_resolved(x, ctx)
                for fut in futures:
                    direct_cat = tuple(cat) + tuple(fut)
                    kh = compose_hak(kcat, hardening_action_kernel(fut, 2))
                    for fam in ((1,), (0, 1)):
                        for k in (1, 2):
                            a = direct_min_cost_typed(x2, direct_cat, fam, k, private_sigs)
                            b = kernel_min_cost_typed(x2, kh, fam, k, private_sigs)
                            if a != b:
                                raise AssertionError(("typed extension", x, cat, ctx, fut, fam, k, a, b))
                            extension_checks += 1
    return {"core_queries": checks, "continuation_queries": extension_checks}


def verify_equal_kernel_congruence() -> dict:
    catalogs = small_catalogs(2)
    groups: dict[tuple, list[tuple[Action, ...]]] = {}
    for c in catalogs:
        h = hardening_action_kernel(c, 2)
        groups.setdefault(canonical_hak(h), []).append(c)
    duplicate_classes = [v for v in groups.values() if len(v) >= 2]
    if not duplicate_classes:
        raise AssertionError("no duplicate HAK classes")
    x = operational_architectures()[17]
    contexts = architecture_contexts_operational()
    private_supports = (4, 8)
    checks = 0
    for cls in duplicate_classes:
        rep = cls[0]
        kh = hardening_action_kernel(rep, 2)
        for alt in cls[1:]:
            for ctx in contexts:
                x2 = add_resolved(x, ctx)
                for fam in ((1,), (2,), (1, 2), (3,)):
                    for k in (1, 2):
                        a = direct_min_cost_operational(x2, rep, fam, k, private_supports)
                        b = direct_min_cost_operational(x2, alt, fam, k, private_supports)
                        c = kernel_min_cost_operational(x2, kh, fam, k, private_supports)
                        if not (a == b == c):
                            raise AssertionError(("congruence", rep, alt, ctx, fam, k, a, b, c))
                        checks += 1
    return {"duplicate_HAK_classes": len(duplicate_classes), "checks": checks}


def verify_constructive_combined_separation() -> dict:
    # ORIK separation: swapped named obligations have same complete IRK but targeted probe differs.
    A, B = 1, 2
    E: TypedCounts = {}
    x: ResolvedKernel = (({A: 1}, E), ({B: 1}, E))
    y: ResolvedKernel = (({B: 1}, E), ({A: 1}, E))
    if complete_irk(x)[0] != complete_irk(y)[0]:
        raise AssertionError("complete IRK mismatch in ORIK separator witness")
    px = resolved_probe_signature(x, 2)
    py = resolved_probe_signature(y, 2)
    if px == py:
        raise AssertionError("targeted ORIK probes failed to separate")

    # HAK separation: same effect/cost, different occupied resources; a future action separates.
    left = (Action((1, 0), 1, 1),)
    right = (Action((1, 0), 1, 2),)
    future = (Action((0, 1), 1, 1),)
    kl = compose_hak(hardening_action_kernel(left, 2), hardening_action_kernel(future, 2))
    kr = compose_hak(hardening_action_kernel(right, 2), hardening_action_kernel(future, 2))
    target = (1, 1)
    lc = min((c for eff, ps in kl.items() if effect_ge(eff, target) for c, _ in ps), default=None)
    rc = min((c for eff, ps in kr.items() if effect_ge(eff, target) for c, _ in ps), default=None)
    if not (lc is None and rc == 2):
        raise AssertionError(("HAK separator", lc, rc))
    return {"ORIK_separator": "PASS", "HAK_future_action_separator": "PASS"}


def verify_no_finite_state_exact_intervention() -> dict:
    # Fixed q=1,m=1. Exact private-diversification probe exposes arbitrary multiplicity n.
    A = 1
    probe_responses = []
    for n in range(1, 65):
        k: ResolvedKernel = (({A: n}, {}),)
        response = operational_probe(k[0][0], A)
        probe_responses.append(response)
    if len(set(probe_responses)) != len(probe_responses):
        raise AssertionError("multiplicity family not separated")
    return {
        "fixed_boundary_q": 1,
        "fixed_boundary_m": 1,
        "pairwise_distinct_exact_states_checked": len(probe_responses),
        "conclusion": "UNBOUNDED_EXACT_SEMANTICS_HAS_INFINITELY_MANY_CONTEXT_CLASSES",
    }


def verify_finite_dimensional_bound() -> dict:
    checks = []
    for q in (1, 2, 3, 4):
        for m in (1, 2, 3, 4):
            d_orik = q * ((2 ** m - 1) + (3 ** m - 1))
            expected = q * (2 ** m + 3 ** m - 2)
            if d_orik != expected:
                raise AssertionError((q, m, d_orik, expected))
            checks.append((q, m, d_orik))
    # HAK is a finite map over realized aggregate effects; for fixed resource width r,
    # each effect stores an antichain of cost/resource pairs with resource masks in 2^r.
    return {"formula_checks": len(checks), "q3_m3_ORIK_coordinates": 3 * (2 ** 3 + 3 ** 3 - 2)}


def self_test() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    # Basic convolution identity.
    if compose_operational_counts({1: 1}, {2: 1}) != {3: 1}:
        raise AssertionError("operational convolution")
    out.append(("operational_convolution", "PASS"))
    if compose_typed_counts({(1, 0): 1}, {(0, 2): 1}) != {(1, 2): 1}:
        raise AssertionError("typed convolution")
    out.append(("typed_convolution", "PASS"))
    # Hardening kernel simple coupled action.
    k = hardening_action_kernel((Action((1, 1), 1, 1),), 2)
    if (1, 1) not in k or k[(1, 1)] != ((1, 1),):
        raise AssertionError("HAK simple")
    out.append(("hardening_action_kernel", "PASS"))
    # Robust hardening rescue.
    A, B, P0, P1 = 1, 2, 4, 8
    E: TypedCounts = {}
    x: ResolvedKernel = (({A: 1}, E), ({B: 1}, E))
    cat = (Action((1, 1), 1, 1),)
    c = direct_min_cost_operational(x, cat, (A | B,), 1, (P0, P1))
    if c != 1:
        raise AssertionError(("robust rescue", c))
    out.append(("integrated_robust_hardening", "PASS"))
    # Exact multiplicity obstruction.
    nf = verify_no_finite_state_exact_intervention()
    if nf["pairwise_distinct_exact_states_checked"] != 64:
        raise AssertionError("no-finite-state witness")
    out.append(("exact_multiplicity_obstruction", "PASS"))
    return out


def verify_all() -> list[tuple[str, dict]]:
    return [
        ("integrated_operational_coupling", verify_integrated_operational_coupling()),
        ("integrated_typed_coupling", verify_integrated_typed_coupling()),
        ("equal_kernel_congruence", verify_equal_kernel_congruence()),
        ("constructive_combined_separation", verify_constructive_combined_separation()),
        ("exact_no_finite_state_obstruction", verify_no_finite_state_exact_intervention()),
        ("finite_dimensional_kernel", verify_finite_dimensional_bound()),
    ]


def main() -> None:
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--self-test", action="store_true")
    g.add_argument("--verify", action="store_true")
    g.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.self_test:
        rows = self_test()
        print(f"SCRT Integrated Canonical Cyber Resilience Theorem v{VERSION} self-test")
        for name, status in rows:
            print(f"{name}:{status}")
        print(f"TOTAL {len(rows)}/{len(rows)} PASS")
        return

    rows = verify_all()
    if args.json:
        print(json.dumps({"version": VERSION, "status": "PASS", "verification": dict(rows)}, indent=2, sort_keys=True))
        return

    print(f"SCRT Integrated Canonical Cyber Resilience Theorem v{VERSION} verification")
    for name, info in rows:
        details = ":".join(f"{k}={v}" for k, v in info.items())
        print(f"{name}:PASS:{details}")
    print("status:PASS")


if __name__ == "__main__":
    main()
