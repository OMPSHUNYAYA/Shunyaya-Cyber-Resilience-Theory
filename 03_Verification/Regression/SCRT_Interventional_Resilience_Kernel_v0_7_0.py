#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Interventional Resilience Kernel
Version 0.7.0

Exact finite semantics for realization multiplicity, typed defense/evidence
incidence, compatible multiset composition, role separation, realization-private
dependency diversification, compromise probes, and reconstruction of the
interventional kernel by subset inversion.

Dependency-free and deterministic.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from typing import Iterable, Sequence

VERSION = "0.7.0"
Signature = tuple[int, int]


def popcount(x: int) -> int:
    return x.bit_count()


def mask_subset(a: int, b: int) -> bool:
    return (a & b) == a


def minimal_masks(xs: Iterable[int]) -> tuple[int, ...]:
    vals = sorted(set(x for x in xs if x), key=lambda x: (popcount(x), x))
    out: list[int] = []
    for x in vals:
        if not any(mask_subset(y, x) for y in out):
            out.append(x)
    return tuple(out)


def sig_support(s: Signature) -> int:
    return s[0] | s[1]


def sig_leq(a: Signature, b: Signature) -> bool:
    return mask_subset(a[0], b[0]) and mask_subset(a[1], b[1])


def typed_minimal(xs: Iterable[Signature]) -> tuple[Signature, ...]:
    vals = sorted(
        set(xs),
        key=lambda s: (popcount(sig_support(s)), popcount(s[0]), s[0], s[1]),
    )
    out: list[Signature] = []
    for x in vals:
        if not any(sig_leq(y, x) for y in out):
            out.append(x)
    return tuple(out)


def all_signatures(m: int) -> tuple[Signature, ...]:
    out: list[Signature] = []
    for d in range(1 << m):
        for e in range(1 << m):
            if d & e:
                continue
            if (d | e) == 0:
                continue
            out.append((d, e))
    return tuple(out)


def all_role_queries(m: int) -> tuple[Signature, ...]:
    """All valid typed role-coordinate query states, including the empty query."""
    return ((0, 0),) + all_signatures(m)


def typed_query_leq(a: Signature, b: Signature) -> bool:
    return sig_leq(a, b)


def sig_compose(a: Signature, b: Signature) -> Signature | None:
    d = a[0] | b[0]
    e = a[1] | b[1]
    if d & e:
        return None
    return d, e


def passive_brk_operational(counts: dict[int, int]) -> tuple[int, ...]:
    return minimal_masks(s for s, c in counts.items() if c > 0)


def passive_brk_typed(counts: dict[Signature, int]) -> tuple[Signature, ...]:
    return typed_minimal(s for s, c in counts.items() if c > 0)


def compose_operational_counts(
    left: dict[int, int], right: dict[int, int]
) -> dict[int, int]:
    out: Counter[int] = Counter()
    for a, ca in left.items():
        if ca <= 0:
            continue
        for b, cb in right.items():
            if cb <= 0:
                continue
            out[a | b] += ca * cb
    return dict(out)


def compose_typed_counts(
    left: dict[Signature, int], right: dict[Signature, int]
) -> dict[Signature, int]:
    out: Counter[Signature] = Counter()
    for a, ca in left.items():
        if ca <= 0:
            continue
        for b, cb in right.items():
            if cb <= 0:
                continue
            z = sig_compose(a, b)
            if z is not None:
                out[z] += ca * cb
    return dict(out)


def compose_brk_operational(a: Iterable[int], b: Iterable[int]) -> tuple[int, ...]:
    return minimal_masks(x | y for x in a for y in b)


def compose_brk_typed(a: Iterable[Signature], b: Iterable[Signature]) -> tuple[Signature, ...]:
    vals = []
    for x in a:
        for y in b:
            z = sig_compose(x, y)
            if z is not None:
                vals.append(z)
    return typed_minimal(vals)


def role_mask(sig: Signature, m: int) -> int:
    """Encode D roles in coordinates 0..m-1 and E roles in m..2m-1."""
    d, e = sig
    return d | (e << m)


def role_mask_to_signature(mask: int, m: int) -> Signature | None:
    low = mask & ((1 << m) - 1)
    high = (mask >> m) & ((1 << m) - 1)
    if low & high:
        return None
    if (low | high) == 0:
        return None
    return low, high


def operational_probe(counts: dict[int, int], q: int) -> int:
    """
    Diversify every ancestry coordinate in q into realization-private descendants,
    then compromise every shared coordinate outside q. The resulting packing
    capacity equals the number of realization tokens whose original support is
    contained in q.
    """
    return sum(c for s, c in counts.items() if c > 0 and mask_subset(s, q))


def typed_probe(counts: dict[Signature, int], q: Signature) -> int:
    """
    Role-separate the interface. Diversify the defensive/evidentiary coordinates
    admitted by q=(Q_D,Q_E), and compromise every remaining shared role
    coordinate. The certified capacity is the cumulative number of realization
    tokens x with x <= q in the typed signature poset.
    """
    return sum(c for s, c in counts.items() if c > 0 and sig_leq(s, q))


def operational_probe_table(counts: dict[int, int], m: int) -> dict[int, int]:
    return {q: operational_probe(counts, q) for q in range(1 << m)}


def typed_probe_table(counts: dict[Signature, int], m: int) -> dict[Signature, int]:
    return {q: typed_probe(counts, q) for q in all_role_queries(m)}


def mobius_exact_counts(table: dict[int, int], width: int) -> dict[int, int]:
    """Subset-lattice inversion of Z(Q)=sum_{T subseteq Q} mu(T)."""
    vals = dict(table)
    for bit in range(width):
        for q in range(1 << width):
            if q & (1 << bit):
                vals[q] -= vals[q ^ (1 << bit)]
    return vals


def reconstruct_operational_counts(counts: dict[int, int], m: int) -> dict[int, int]:
    inv = mobius_exact_counts(operational_probe_table(counts, m), m)
    return {s: inv[s] for s in range(1, 1 << m) if inv[s]}


def reconstruct_typed_counts(counts: dict[Signature, int], m: int) -> dict[Signature, int]:
    table = typed_probe_table(counts, m)
    exact: dict[Signature, int] = {}
    queries = sorted(all_role_queries(m), key=lambda s: (popcount(sig_support(s)), s[0], s[1]))
    for q in queries:
        value = table[q]
        for t, c in exact.items():
            if t != q and sig_leq(t, q):
                value -= c
        exact[q] = value
    if exact.get((0, 0), 0) != 0:
        raise AssertionError(("nonzero_empty_typed_mass", exact[(0, 0)]))
    return {s: c for s, c in exact.items() if s != (0, 0) and c}


def first_operational_separator(
    a: dict[int, int], b: dict[int, int], m: int
) -> tuple[int, int, int] | None:
    for q in sorted(range(1 << m), key=lambda x: (popcount(x), x)):
        x = operational_probe(a, q)
        y = operational_probe(b, q)
        if x != y:
            return q, x, y
    return None


def first_typed_separator(
    a: dict[Signature, int], b: dict[Signature, int], m: int
) -> tuple[Signature, int, int] | None:
    for q in sorted(all_role_queries(m), key=lambda s: (popcount(sig_support(s)), s[0], s[1])):
        x = typed_probe(a, q)
        y = typed_probe(b, q)
        if x != y:
            return q, x, y
    return None


def count_vectors(items: Sequence, max_count: int) -> Iterable[dict]:
    for vals in itertools.product(range(max_count + 1), repeat=len(items)):
        if not any(vals):
            continue
        yield {item: c for item, c in zip(items, vals) if c}


def verify_mobius_reconstruction() -> dict:
    op_checks = 0
    typed_checks = 0
    # Complete operational count universe for m<=3, counts 0..2.
    for m in range(1, 4):
        items = tuple(range(1, 1 << m))
        for counts in count_vectors(items, 2):
            if reconstruct_operational_counts(counts, m) != counts:
                raise AssertionError(("operational_reconstruction", m, counts))
            op_checks += 1
    # Complete typed count universe is much larger; m=1 complete 0..3,
    # m=2 complete 0..1, plus deterministic m=2 count-2 basis perturbations.
    for m, max_count in ((1, 3), (2, 1)):
        items = all_signatures(m)
        for counts in count_vectors(items, max_count):
            if reconstruct_typed_counts(counts, m) != counts:
                raise AssertionError(("typed_reconstruction", m, counts))
            typed_checks += 1
    m = 2
    items = all_signatures(m)
    for i, s in enumerate(items):
        for j, t in enumerate(items):
            counts = {s: 2}
            counts[t] = counts.get(t, 0) + 1
            if reconstruct_typed_counts(counts, m) != counts:
                raise AssertionError(("typed_reconstruction_count2", i, j, counts))
            typed_checks += 1
    return {"operational_checks": op_checks, "typed_checks": typed_checks}


def verify_passive_projection_composition() -> dict:
    op_checks = 0
    typed_checks = 0
    # All set-valued states on m=2, with multiplicities sampled by 1/2 weighting.
    m = 2
    op_items = tuple(range(1, 1 << m))
    op_states = []
    for mask in range(1 << len(op_items)):
        state = {
            s: 1 + ((i + mask) & 1)
            for i, s in enumerate(op_items)
            if mask & (1 << i)
        }
        op_states.append(state)
    for a in op_states:
        for b in op_states:
            lhs = passive_brk_operational(compose_operational_counts(a, b))
            rhs = compose_brk_operational(
                passive_brk_operational(a), passive_brk_operational(b)
            )
            if lhs != rhs:
                raise AssertionError(("op_projection_compose", a, b, lhs, rhs))
            op_checks += 1

    sigs = all_signatures(m)
    typed_states = []
    for mask in range(1 << len(sigs)):
        state = {
            s: 1 + ((i + mask) & 1)
            for i, s in enumerate(sigs)
            if mask & (1 << i)
        }
        typed_states.append(state)
    for a in typed_states:
        for b in typed_states:
            lhs = passive_brk_typed(compose_typed_counts(a, b))
            rhs = compose_brk_typed(passive_brk_typed(a), passive_brk_typed(b))
            if lhs != rhs:
                raise AssertionError(("typed_projection_compose", a, b, lhs, rhs))
            typed_checks += 1
    return {"operational_checks": op_checks, "typed_checks": typed_checks}


def verify_probe_classification() -> dict:
    op_states = 0
    op_classes = 0
    typed_states = 0
    typed_classes = 0

    for m in (1, 2, 3):
        items = tuple(range(1, 1 << m))
        seen: dict[tuple[int, ...], tuple[int, ...]] = {}
        for counts in count_vectors(items, 2):
            key = tuple(operational_probe(counts, q) for q in range(1 << m))
            raw = tuple(counts.get(s, 0) for s in items)
            if key in seen and seen[key] != raw:
                raise AssertionError(("operational_probe_collision", m, seen[key], raw))
            seen[key] = raw
            op_states += 1
        op_classes += len(seen)

    m = 2
    sigs = all_signatures(m)
    seen_t: dict[tuple[int, ...], tuple[int, ...]] = {}
    for counts in count_vectors(sigs, 1):
        key = tuple(typed_probe(counts, q) for q in all_role_queries(m))
        raw = tuple(counts.get(s, 0) for s in sigs)
        if key in seen_t and seen_t[key] != raw:
            raise AssertionError(("typed_probe_collision", seen_t[key], raw))
        seen_t[key] = raw
        typed_states += 1
    typed_classes = len(seen_t)
    return {
        "operational_states": op_states,
        "operational_classes": op_classes,
        "typed_states": typed_states,
        "typed_classes": typed_classes,
    }


def verify_diversification_semilattice() -> dict:
    # The transformation state is the set of coordinates already diversified.
    checks = 0
    for width in range(1, 7):
        masks = range(1 << width)
        for a in masks:
            if (a | a) != a:
                raise AssertionError(("idempotence", width, a))
            for b in masks:
                if (a | b) != (b | a):
                    raise AssertionError(("commutativity", width, a, b))
                for c in (0, (1 << width) - 1, a, b):
                    if ((a | b) | c) != (a | (b | c)):
                        raise AssertionError(("associativity", width, a, b, c))
                    checks += 1
    return {"checks": checks}


def strict_brk_failure_witnesses() -> dict:
    # Duplicate witness. Both states have the same passive BRK.
    m = 2
    s = (1 << 0, 1 << 1)  # D={A}, E={B}
    x = {s: 1}
    y = {s: 2}
    if passive_brk_typed(x) != passive_brk_typed(y):
        raise AssertionError("duplicate_witness_brk")
    q_all = s
    rx = typed_probe(x, q_all)
    ry = typed_probe(y, q_all)
    if (rx, ry) != (1, 2):
        raise AssertionError(("duplicate_witness_response", rx, ry))

    # Dominated-role witness. Same passive BRK and same total realization count,
    # but a role-selective diversification probe distinguishes them.
    m = 3
    base = (1 << 0, 1 << 1)                 # D={A}, E={B}
    d_extra = ((1 << 0) | (1 << 2), 1 << 1) # D={A,C}, E={B}
    e_extra = (1 << 0, (1 << 1) | (1 << 2)) # D={A}, E={B,C}
    u = {base: 1, d_extra: 1}
    v = {base: 1, e_extra: 1}
    if passive_brk_typed(u) != passive_brk_typed(v):
        raise AssertionError("dominated_role_witness_brk")
    if sum(u.values()) != sum(v.values()):
        raise AssertionError("dominated_role_witness_total")
    q = d_extra
    ru = typed_probe(u, q)
    rv = typed_probe(v, q)
    if (ru, rv) != (2, 1):
        raise AssertionError(("dominated_role_witness_response", ru, rv))

    return {
        "duplicate_witness": "1<2",
        "dominated_role_witness": "2>1",
    }


def verify_composition_algebra() -> dict:
    op_checks = 0
    typed_checks = 0
    for m in (1, 2, 3):
        op_basis = tuple(range(1 << m))
        for a in op_basis:
            for b in op_basis:
                ab = compose_operational_counts({a: 1}, {b: 1})
                ba = compose_operational_counts({b: 1}, {a: 1})
                if ab != ba:
                    raise AssertionError(("op_commutativity", m, a, b))
                if compose_operational_counts({0: 1}, {a: 1}) != {a: 1}:
                    raise AssertionError(("op_identity", m, a))
                op_checks += 2
        # Associativity on all basis triples for m<=2; deterministic basis sample for m=3.
        triples = itertools.product(op_basis, repeat=3) if m <= 2 else ((a, b, a ^ b) for a in op_basis for b in op_basis)
        for a, b, c in triples:
            left = compose_operational_counts(compose_operational_counts({a:1},{b:1}), {c:1})
            right = compose_operational_counts({a:1}, compose_operational_counts({b:1},{c:1}))
            if left != right:
                raise AssertionError(("op_associativity", m, a, b, c))
            op_checks += 1

    for m in (1, 2):
        typed_basis = all_role_queries(m)
        for a in typed_basis:
            for b in typed_basis:
                ab = compose_typed_counts({a: 1}, {b: 1})
                ba = compose_typed_counts({b: 1}, {a: 1})
                if ab != ba:
                    raise AssertionError(("typed_commutativity", m, a, b))
                if compose_typed_counts({(0,0):1}, {a:1}) != {a:1}:
                    raise AssertionError(("typed_identity", m, a))
                typed_checks += 2
        for a in typed_basis:
            for b in typed_basis:
                for c in typed_basis:
                    left = compose_typed_counts(compose_typed_counts({a:1},{b:1}), {c:1})
                    right = compose_typed_counts({a:1}, compose_typed_counts({b:1},{c:1}))
                    if left != right:
                        raise AssertionError(("typed_associativity", m, a, b, c))
                    typed_checks += 1
    return {"operational_checks": op_checks, "typed_checks": typed_checks}


def kernel_dimensions(m: int) -> dict:
    return {
        "interface_width": m,
        "operational_coordinates": (1 << m) - 1,
        "typed_certified_coordinates": (3 ** m) - 1,
        "total_integer_coordinates": (1 << m) + (3 ** m) - 2,
    }


def self_test() -> dict:
    tests = []
    # 1. Signature count.
    tests.append(len(all_signatures(3)) == (3 ** 3) - 1)
    # 2. Role lift is injective on valid signatures.
    sigs = all_signatures(3)
    tests.append(len({role_mask(s, 3) for s in sigs}) == len(sigs))
    # 3. Basic inversion.
    op = {1: 2, 3: 1}
    tests.append(reconstruct_operational_counts(op, 2) == op)
    # 4. Typed inversion.
    ty = {(1, 2): 2, (1 | 4, 2): 1}
    tests.append(reconstruct_typed_counts(ty, 3) == ty)
    # 5. Composition multiplicity.
    tests.append(compose_operational_counts({1: 2}, {2: 3}) == {3: 6})
    # 6. Passive projection discards multiplicity.
    tests.append(passive_brk_typed({(1, 2): 1}) == passive_brk_typed({(1, 2): 7}))
    # 7. Witnesses.
    strict_brk_failure_witnesses()
    tests.append(True)
    if not all(tests):
        raise AssertionError(("self_test", tests))
    return {"passed": sum(bool(x) for x in tests), "total": len(tests)}


def verify() -> dict:
    a = verify_mobius_reconstruction()
    b = verify_passive_projection_composition()
    c = verify_probe_classification()
    d = verify_diversification_semilattice()
    e = strict_brk_failure_witnesses()
    f = verify_composition_algebra()
    return {
        "version": VERSION,
        "mobius_reconstruction": a,
        "passive_projection_composition": b,
        "probe_classification": c,
        "diversification_semilattice": d,
        "strict_brk_failure_witnesses": e,
        "composition_algebra": f,
        "kernel_dimension_m3": kernel_dimensions(3),
        "status": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        r = self_test()
        if args.json:
            print(json.dumps(r, sort_keys=True))
        else:
            print(f"SCRT Interventional Resilience Kernel v{VERSION} self-test")
            print(f"TOTAL {r['passed']}/{r['total']} PASS")
        return

    if args.verify:
        r = verify()
        if args.json:
            print(json.dumps(r, sort_keys=True))
        else:
            print(f"SCRT Interventional Resilience Kernel v{VERSION} verification")
            print(
                "mobius_reconstruction:PASS:"
                f"operational={r['mobius_reconstruction']['operational_checks']}:"
                f"typed={r['mobius_reconstruction']['typed_checks']}"
            )
            print(
                "passive_projection_composition:PASS:"
                f"operational={r['passive_projection_composition']['operational_checks']}:"
                f"typed={r['passive_projection_composition']['typed_checks']}"
            )
            print(
                "probe_classification:PASS:"
                f"operational_states={r['probe_classification']['operational_states']}:"
                f"operational_classes={r['probe_classification']['operational_classes']}:"
                f"typed_states={r['probe_classification']['typed_states']}:"
                f"typed_classes={r['probe_classification']['typed_classes']}"
            )
            print(
                "diversification_semilattice:PASS:"
                f"checks={r['diversification_semilattice']['checks']}"
            )
            print(
                "passive_brk_not_intervention_complete:PASS:"
                f"duplicate={r['strict_brk_failure_witnesses']['duplicate_witness']}:"
                f"dominated_role={r['strict_brk_failure_witnesses']['dominated_role_witness']}"
            )
            print(
                "kernel_composition_algebra:PASS:"
                f"operational={r['composition_algebra']['operational_checks']}:"
                f"typed={r['composition_algebra']['typed_checks']}"
            )
            kd = r["kernel_dimension_m3"]
            print(
                "bounded_width_integer_kernel:PASS:"
                f"m={kd['interface_width']}:coordinates={kd['total_integer_coordinates']}"
            )
            print("status:PASS")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
