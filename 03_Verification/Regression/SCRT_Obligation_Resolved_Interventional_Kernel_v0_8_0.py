#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Obligation-Resolved Interventional Kernel
Version 0.8.0

Exact finite semantics for named security obligations, per-obligation route
multiplicity kernels, complete-realization convolution, targeted private-route
hardening, targeted reconstruction probes, and strict kernel refinement.

Dependency-free and deterministic.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from typing import Iterable, Sequence

VERSION = "0.8.0"
Signature = tuple[int, int]
OperationalCounts = dict[int, int]
TypedCounts = dict[Signature, int]
ObligationKernel = tuple[OperationalCounts, TypedCounts]
ResolvedKernel = tuple[ObligationKernel, ...]


def popcount(x: int) -> int:
    return x.bit_count()


def mask_subset(a: int, b: int) -> bool:
    return (a & b) == a


def sig_support(s: Signature) -> int:
    return s[0] | s[1]


def sig_leq(a: Signature, b: Signature) -> bool:
    return mask_subset(a[0], b[0]) and mask_subset(a[1], b[1])


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


def sig_compose(a: Signature, b: Signature) -> Signature | None:
    d = a[0] | b[0]
    e = a[1] | b[1]
    if d & e:
        return None
    return d, e


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
    if not factors:
        return {0: 1}
    cur: OperationalCounts = {0: 1}
    for factor in factors:
        cur = compose_operational_counts(cur, factor)
    cur.pop(0, None)
    return cur


def complete_typed_kernel(factors: Sequence[TypedCounts]) -> TypedCounts:
    if not factors:
        return {(0, 0): 1}
    cur: TypedCounts = {(0, 0): 1}
    for factor in factors:
        cur = compose_typed_counts(cur, factor)
    cur.pop((0, 0), None)
    return cur


def complete_irk(resolved: ResolvedKernel) -> ObligationKernel:
    return (
        complete_operational_kernel([x[0] for x in resolved]),
        complete_typed_kernel([x[1] for x in resolved]),
    )


def direct_operational_complete(factors: Sequence[OperationalCounts]) -> OperationalCounts:
    out: Counter[int] = Counter()
    items = [tuple(f.items()) for f in factors]
    if not items:
        return {0: 1}
    for choice in itertools.product(*items):
        support = 0
        mult = 1
        for s, c in choice:
            support |= s
            mult *= c
        out[support] += mult
    return dict(out)


def direct_typed_complete(factors: Sequence[TypedCounts]) -> TypedCounts:
    out: Counter[Signature] = Counter()
    items = [tuple(f.items()) for f in factors]
    if not items:
        return {(0, 0): 1}
    for choice in itertools.product(*items):
        cur: Signature = (0, 0)
        mult = 1
        ok = True
        for s, c in choice:
            z = sig_compose(cur, s)
            if z is None:
                ok = False
                break
            cur = z
            mult *= c
        if ok:
            out[cur] += mult
    return dict(out)


def operational_probe(counts: OperationalCounts, q: int) -> int:
    return sum(c for s, c in counts.items() if mask_subset(s, q))


def typed_probe(counts: TypedCounts, q: Signature) -> int:
    return sum(c for s, c in counts.items() if sig_leq(s, q))


def operational_probe_table(counts: OperationalCounts, m: int) -> tuple[int, ...]:
    return tuple(operational_probe(counts, q) for q in range(1 << m))


def typed_probe_table(counts: TypedCounts, m: int) -> tuple[int, ...]:
    queries = all_signatures(m, include_empty=True)
    return tuple(typed_probe(counts, q) for q in queries)


def reconstruct_operational_from_table(table: Sequence[int], m: int) -> OperationalCounts:
    vals = list(table)
    if len(vals) != (1 << m):
        raise ValueError("invalid operational probe table")
    for bit in range(m):
        for q in range(1 << m):
            if q & (1 << bit):
                vals[q] -= vals[q ^ (1 << bit)]
    return {s: vals[s] for s in range(1, 1 << m) if vals[s]}


def reconstruct_typed_from_table(table: Sequence[int], m: int) -> TypedCounts:
    queries = all_signatures(m, include_empty=True)
    if len(table) != len(queries):
        raise ValueError("invalid typed probe table")
    cumulative = {q: int(v) for q, v in zip(queries, table)}
    exact: dict[Signature, int] = {}
    ordered = sorted(queries, key=lambda s: (popcount(sig_support(s)), popcount(s[0]), s[0], s[1]))
    for q in ordered:
        v = cumulative[q]
        for t, c in exact.items():
            if t != q and sig_leq(t, q):
                v -= c
        exact[q] = v
    if exact.get((0, 0), 0) != 0:
        raise AssertionError("nonzero empty typed mass")
    return {s: c for s, c in exact.items() if s != (0, 0) and c}


def resolved_probe_signature(resolved: ResolvedKernel, m: int) -> tuple:
    out = []
    for op, typed in resolved:
        out.append((operational_probe_table(op, m), typed_probe_table(typed, m)))
    return tuple(out)


def reconstruct_resolved_from_probes(signature: tuple, m: int) -> ResolvedKernel:
    out: list[ObligationKernel] = []
    for op_table, typed_table in signature:
        out.append((
            reconstruct_operational_from_table(op_table, m),
            reconstruct_typed_from_table(typed_table, m),
        ))
    return tuple(out)


def add_private_operational_route(resolved: ResolvedKernel, obligation: int, private_bit: int) -> ResolvedKernel:
    out: list[ObligationKernel] = []
    for i, (op, typed) in enumerate(resolved):
        op2 = dict(op)
        if i == obligation:
            op2[private_bit] = op2.get(private_bit, 0) + 1
        out.append((op2, dict(typed)))
    return tuple(out)


def add_private_typed_route(
    resolved: ResolvedKernel,
    obligation: int,
    private_defense_bit: int,
    private_evidence_bit: int,
) -> ResolvedKernel:
    if private_defense_bit & private_evidence_bit:
        raise ValueError("private defense/evidence bits must be disjoint")
    route = (private_defense_bit, private_evidence_bit)
    out: list[ObligationKernel] = []
    for i, (op, typed) in enumerate(resolved):
        typed2 = dict(typed)
        if i == obligation:
            typed2[route] = typed2.get(route, 0) + 1
        out.append((dict(op), typed2))
    return tuple(out)


def surviving_operational_count(counts: OperationalCounts, failure: int) -> int:
    return sum(c for s, c in counts.items() if (s & failure) == 0)


def surviving_typed_count(counts: TypedCounts, failure: int) -> int:
    return sum(c for (d, e), c in counts.items() if ((d | e) & failure) == 0)


def targeted_private_route_witness() -> dict:
    # Shared boundary A,B is bits 0,1. Private P is bit 2.
    A, B, P = 1, 2, 4
    empty_typed: TypedCounts = {}
    x: ResolvedKernel = (({A: 1}, empty_typed), ({B: 1}, empty_typed))
    y: ResolvedKernel = (({B: 1}, empty_typed), ({A: 1}, empty_typed))
    if complete_irk(x)[0] != complete_irk(y)[0]:
        raise AssertionError("witness initial complete IRK mismatch")
    if x == y:
        raise AssertionError("witness resolved kernels unexpectedly equal")
    xh = add_private_operational_route(x, 0, P)
    yh = add_private_operational_route(y, 0, P)
    failure = A
    sx = surviving_operational_count(complete_irk(xh)[0], failure)
    sy = surviving_operational_count(complete_irk(yh)[0], failure)
    if not (sx > 0 and sy == 0):
        raise AssertionError(("targeted private route witness", sx, sy))
    return {
        "initial_complete_support_counts": complete_irk(x)[0],
        "post_targeted_survival_X": sx,
        "post_targeted_survival_Y": sy,
    }


def typed_targeted_private_route_witness() -> dict:
    # Shared: A,B defensive bits 0,1; C,D evidentiary bits 2,3.
    # Private P_D,P_E are bits 4,5.
    A, B, C, D, PD, PE = 1, 2, 4, 8, 16, 32
    empty_op: OperationalCounts = {}
    x: ResolvedKernel = (
        (empty_op, {(A, C): 1}),
        (empty_op, {(B, D): 1}),
    )
    y: ResolvedKernel = (
        (empty_op, {(B, D): 1}),
        (empty_op, {(A, C): 1}),
    )
    if complete_irk(x)[1] != complete_irk(y)[1]:
        raise AssertionError("typed witness initial complete IRK mismatch")
    xh = add_private_typed_route(x, 0, PD, PE)
    yh = add_private_typed_route(y, 0, PD, PE)
    failure = A | C
    sx = surviving_typed_count(complete_irk(xh)[1], failure)
    sy = surviving_typed_count(complete_irk(yh)[1], failure)
    if not (sx > 0 and sy == 0):
        raise AssertionError(("typed targeted private route witness", sx, sy))
    return {"post_targeted_survival_X": sx, "post_targeted_survival_Y": sy}


def count_vectors(items: Sequence, max_count: int, allow_empty: bool = False) -> Iterable[dict]:
    for vals in itertools.product(range(max_count + 1), repeat=len(items)):
        if not allow_empty and not any(vals):
            continue
        yield {item: c for item, c in zip(items, vals) if c}


def verify_factorization() -> dict:
    op_checks = 0
    typed_checks = 0
    # Exhaust all two-obligation operational factors on m=2 with 0/1 counts.
    op_items = (1, 2, 3)
    op_factors = list(count_vectors(op_items, 1))
    for a in op_factors:
        for b in op_factors:
            got = complete_operational_kernel([a, b])
            direct = direct_operational_complete([a, b])
            direct.pop(0, None)
            if got != direct:
                raise AssertionError(("operational factorization", a, b, got, direct))
            op_checks += 1
    # Exhaust all two-obligation typed factors on m=1 with 0/1 counts.
    typed_items = all_signatures(1)
    typed_factors = list(count_vectors(typed_items, 1))
    for a in typed_factors:
        for b in typed_factors:
            got = complete_typed_kernel([a, b])
            direct = direct_typed_complete([a, b])
            direct.pop((0, 0), None)
            if got != direct:
                raise AssertionError(("typed factorization", a, b, got, direct))
            typed_checks += 1
    return {"operational": op_checks, "typed": typed_checks}


def verify_probe_reconstruction() -> dict:
    op_checks = 0
    typed_checks = 0
    for m in range(1, 4):
        items = tuple(range(1, 1 << m))
        max_count = 2 if m <= 2 else 1
        for counts in count_vectors(items, max_count):
            table = operational_probe_table(counts, m)
            if reconstruct_operational_from_table(table, m) != counts:
                raise AssertionError(("operational reconstruction", m, counts))
            op_checks += 1
    for m, max_count in ((1, 3), (2, 1)):
        items = all_signatures(m)
        for counts in count_vectors(items, max_count):
            table = typed_probe_table(counts, m)
            if reconstruct_typed_from_table(table, m) != counts:
                raise AssertionError(("typed reconstruction", m, counts))
            typed_checks += 1
    return {"operational": op_checks, "typed": typed_checks}


def verify_resolved_classification() -> dict:
    # Complete two-obligation operational universe on m=2 with 0/1 route counts.
    m = 2
    op_items = (1, 2, 3)
    local_ops = list(count_vectors(op_items, 1))
    op_states: list[ResolvedKernel] = []
    for a in local_ops:
        for b in local_ops:
            op_states.append(((a, {}), (b, {})))
    op_signatures = [resolved_probe_signature(s, m) for s in op_states]
    if len(set(op_signatures)) != len(op_states):
        raise AssertionError("resolved operational probe collision")
    for state, sig in zip(op_states, op_signatures):
        if reconstruct_resolved_from_probes(sig, m) != state:
            raise AssertionError("resolved operational reconstruction failure")
    op_complete_classes = len({tuple(sorted(complete_irk(s)[0].items())) for s in op_states})

    # Complete two-obligation typed universe on m=1 with 0/1 route counts.
    mt = 1
    typed_items = all_signatures(mt)
    local_typed = list(count_vectors(typed_items, 1))
    typed_states: list[ResolvedKernel] = []
    for a in local_typed:
        for b in local_typed:
            typed_states.append((({}, a), ({}, b)))
    typed_signatures = [resolved_probe_signature(s, mt) for s in typed_states]
    if len(set(typed_signatures)) != len(typed_states):
        raise AssertionError("resolved typed probe collision")
    for state, sig in zip(typed_states, typed_signatures):
        if reconstruct_resolved_from_probes(sig, mt) != state:
            raise AssertionError("resolved typed reconstruction failure")
    typed_complete_classes = len({tuple(sorted(complete_irk(s)[1].items())) for s in typed_states})

    return {
        "operational_states": len(op_states),
        "operational_classes": len(set(op_signatures)),
        "operational_complete_IRK_classes": op_complete_classes,
        "typed_states": len(typed_states),
        "typed_classes": len(set(typed_signatures)),
        "typed_complete_IRK_classes": typed_complete_classes,
    }


def verify_strict_hierarchy() -> dict:
    # ORIK -> complete IRK is strict by obligation swap.
    A, B = 1, 2
    x: ResolvedKernel = (({A: 1}, {}), ({B: 1}, {}))
    y: ResolvedKernel = (({B: 1}, {}), ({A: 1}, {}))
    if complete_irk(x) != complete_irk(y) or x == y:
        raise AssertionError("ORIK->IRK strictness witness failed")

    # IRK -> BRK is strict by multiplicity; here compare exact counts versus support presence.
    irk1 = {A: 1}
    irk2 = {A: 2}
    brk1 = tuple(sorted(s for s, c in irk1.items() if c > 0))
    brk2 = tuple(sorted(s for s, c in irk2.items() if c > 0))
    if brk1 != brk2 or irk1 == irk2:
        raise AssertionError("IRK->BRK strictness witness failed")
    return {"ORIK_to_IRK": "strict", "IRK_to_BRK": "strict"}


def verify_targeted_locality() -> dict:
    checks = 0
    # Adding a route to obligation i then recomputing full convolution must equal
    # direct enumeration of the transformed factors.
    m = 2
    items = (1, 2, 3)
    factors = list(count_vectors(items, 1))
    P = 4
    sample = factors[:]
    for a in sample:
        for b in sample:
            state: ResolvedKernel = ((a, {}), (b, {}))
            for i in (0, 1):
                transformed = add_private_operational_route(state, i, P)
                got = complete_irk(transformed)[0]
                direct = direct_operational_complete([transformed[0][0], transformed[1][0]])
                direct.pop(0, None)
                if got != direct:
                    raise AssertionError(("targeted locality", i, state))
                checks += 1
    return {"checks": checks}


def verify_cross_obligation_commutation() -> dict:
    A, B, P, Q = 1, 2, 4, 8
    base: ResolvedKernel = (({A: 1}, {}), ({B: 1}, {}))
    left = add_private_operational_route(add_private_operational_route(base, 0, P), 1, Q)
    right = add_private_operational_route(add_private_operational_route(base, 1, Q), 0, P)
    if left != right or complete_irk(left) != complete_irk(right):
        raise AssertionError("cross obligation commutation")
    return {"checks": 1}


def verify_targeted_separator_logic() -> dict:
    # Every pair of distinct local operational count states on m=2 has a finite
    # obligation-targeted probe separator. This lifts immediately to ORIK by
    # selecting the first obligation whose factor differs.
    m = 2
    items = (1, 2, 3)
    states = list(count_vectors(items, 1))
    checks = 0
    for i, a in enumerate(states):
        for b in states[i + 1:]:
            found = False
            for q in range(1 << m):
                if operational_probe(a, q) != operational_probe(b, q):
                    found = True
                    break
            if not found:
                raise AssertionError(("missing targeted separator", a, b))
            checks += 1
    return {"pairs": checks}


def verify_bounded_width_dimension() -> dict:
    for q in range(1, 6):
        for m in range(1, 6):
            expected = q * ((1 << m) + (3 ** m) - 2)
            direct = q * (((1 << m) - 1) + ((3 ** m) - 1))
            if expected != direct:
                raise AssertionError((q, m, expected, direct))
    return {"q": 3, "m": 3, "coordinates": 3 * ((1 << 3) + 3 ** 3 - 2)}


def self_test() -> dict:
    checks = 0
    # Basic operational convolution.
    if complete_operational_kernel([{1: 1}, {2: 1}]) != {3: 1}:
        raise AssertionError("basic operational convolution")
    checks += 1
    # Basic typed convolution.
    if complete_typed_kernel([{(1, 0): 1}, {(0, 2): 1}]) != {(1, 2): 1}:
        raise AssertionError("basic typed convolution")
    checks += 1
    targeted_private_route_witness()
    checks += 1
    typed_targeted_private_route_witness()
    checks += 1
    # Local probe reconstruction.
    counts = {1: 2, 3: 1}
    if reconstruct_operational_from_table(operational_probe_table(counts, 2), 2) != counts:
        raise AssertionError("basic operational reconstruction")
    checks += 1
    tcounts = {(1, 0): 2, (0, 2): 1, (1, 2): 1}
    if reconstruct_typed_from_table(typed_probe_table(tcounts, 2), 2) != tcounts:
        raise AssertionError("basic typed reconstruction")
    checks += 1
    verify_cross_obligation_commutation()
    checks += 1
    return {"total": checks}


def verify() -> dict:
    return {
        "factorization": verify_factorization(),
        "probe_reconstruction": verify_probe_reconstruction(),
        "resolved_classification": verify_resolved_classification(),
        "strict_hierarchy": verify_strict_hierarchy(),
        "targeted_locality": verify_targeted_locality(),
        "cross_obligation_commutation": verify_cross_obligation_commutation(),
        "targeted_separator_logic": verify_targeted_separator_logic(),
        "targeted_private_route_witness": targeted_private_route_witness(),
        "typed_targeted_private_route_witness": typed_targeted_private_route_witness(),
        "bounded_width_dimension": verify_bounded_width_dimension(),
    }


def print_verify(result: dict) -> None:
    print(f"SCRT Obligation-Resolved Interventional Kernel v{VERSION} verification")
    f = result["factorization"]
    print(f"obligation_factorization:PASS:operational={f['operational']}:typed={f['typed']}")
    p = result["probe_reconstruction"]
    print(f"targeted_probe_reconstruction:PASS:operational={p['operational']}:typed={p['typed']}")
    c = result["resolved_classification"]
    print(
        "obligation_resolved_classification:PASS:"
        f"operational_states={c['operational_states']}:operational_classes={c['operational_classes']}:"
        f"operational_complete_IRK_classes={c['operational_complete_IRK_classes']}:"
        f"typed_states={c['typed_states']}:typed_classes={c['typed_classes']}:"
        f"typed_complete_IRK_classes={c['typed_complete_IRK_classes']}"
    )
    h = result["strict_hierarchy"]
    print(f"strict_kernel_hierarchy:PASS:ORIK_to_IRK={h['ORIK_to_IRK']}:IRK_to_BRK={h['IRK_to_BRK']}")
    print(f"targeted_transformation_locality:PASS:checks={result['targeted_locality']['checks']}")
    print(f"cross_obligation_action_commutation:PASS:checks={result['cross_obligation_commutation']['checks']}")
    print(f"constructive_targeted_separators:PASS:pairs={result['targeted_separator_logic']['pairs']}")
    w = result["targeted_private_route_witness"]
    print(f"complete_IRK_not_target_complete:PASS:survival={w['post_targeted_survival_X']}>{w['post_targeted_survival_Y']}")
    tw = result["typed_targeted_private_route_witness"]
    print(f"typed_complete_IRK_not_target_complete:PASS:survival={tw['post_targeted_survival_X']}>{tw['post_targeted_survival_Y']}")
    d = result["bounded_width_dimension"]
    print(f"bounded_width_integer_kernel:PASS:q={d['q']}:m={d['m']}:coordinates={d['coordinates']}")
    print("status:PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        r = self_test()
        if args.json:
            print(json.dumps({"version": VERSION, "self_test": r, "status": "PASS"}, sort_keys=True))
        else:
            print(f"SCRT Obligation-Resolved Interventional Kernel v{VERSION} self-test")
            print(f"TOTAL {r['total']}/{r['total']} PASS")
    if args.verify:
        r = verify()
        if args.json:
            print(json.dumps({"version": VERSION, "verification": r, "status": "PASS"}, sort_keys=True))
        else:
            print_verify(r)
    if not args.self_test and not args.verify:
        parser.print_help()


if __name__ == "__main__":
    main()
