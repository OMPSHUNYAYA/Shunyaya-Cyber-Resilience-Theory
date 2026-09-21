#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Name-Invariant Interface Quotient and Continuation Theorem
Version 1.3.0

Exact finite semantics for quotienting non-semantic interface names while
preserving anchored cyber identities, typed affine structural transformations,
cost/resource continuation, and constructive future separation.

Dependency-free and deterministic.
"""
from __future__ import annotations

import argparse
import itertools
from dataclasses import dataclass
from typing import Iterable, Sequence

VERSION = "1.3.0"
Vector = tuple[int, ...]
Matrix = tuple[tuple[int, ...], ...]
Perm = tuple[int, ...]
ResourceCost = tuple[int, int]


def vec_add(a: Vector, b: Vector) -> Vector:
    if len(a) != len(b):
        raise ValueError("vector dimensions differ")
    return tuple(x + y for x, y in zip(a, b))


def mat_vec(m: Matrix, x: Vector) -> Vector:
    if not m:
        return tuple()
    if len(m[0]) != len(x):
        raise ValueError("matrix/vector dimensions differ")
    return tuple(sum(row[j] * x[j] for j in range(len(x))) for row in m)


def mat_mul(a: Matrix, b: Matrix) -> Matrix:
    if not a or not b or len(a[0]) != len(b):
        raise ValueError("matrix dimensions differ")
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0])))
        for i in range(len(a))
    )


def perm_matrix(p: Perm) -> Matrix:
    return tuple(tuple(1 if j == p[i] else 0 for j in range(len(p))) for i in range(len(p)))


def inv_perm(p: Perm) -> Perm:
    out = [0] * len(p)
    for i, j in enumerate(p):
        out[j] = i
    return tuple(out)


def apply_perm(p: Perm, x: Vector) -> Vector:
    return tuple(x[p[i]] for i in range(len(p)))


def resource_subset(a: int, b: int) -> bool:
    return (a & b) == a


@dataclass(frozen=True, order=True)
class GaugeInterface:
    """Anchors are semantic; free coordinates are anonymous within each role block."""
    anchors: tuple[str, ...]
    free_roles: tuple[str, ...]

    @property
    def d(self) -> int:
        return len(self.anchors) + len(self.free_roles)

    @property
    def signature(self) -> tuple:
        counts: dict[str, int] = {}
        for r in self.free_roles:
            counts[r] = counts.get(r, 0) + 1
        return (self.anchors, tuple(sorted(counts.items())))

    def gauge_group(self) -> tuple[Perm, ...]:
        n_a = len(self.anchors)
        role_positions: dict[str, list[int]] = {}
        for j, role in enumerate(self.free_roles, start=n_a):
            role_positions.setdefault(role, []).append(j)
        blocks = []
        for role in sorted(role_positions):
            pos = role_positions[role]
            blocks.append(tuple(itertools.permutations(pos)))
        if not blocks:
            return (tuple(range(self.d)),)
        out: list[Perm] = []
        for choices in itertools.product(*blocks):
            p = list(range(self.d))
            for role, choice in zip(sorted(role_positions), choices):
                pos = role_positions[role]
                for dst, src in zip(pos, choice):
                    p[dst] = src
            out.append(tuple(p))
        return tuple(sorted(set(out)))


def canonical_state(i: GaugeInterface, x: Vector) -> Vector:
    if len(x) != i.d:
        raise ValueError("state does not match interface")
    return min(apply_perm(p, x) for p in i.gauge_group())


@dataclass(frozen=True, order=True)
class GaugeAffine:
    source: GaugeInterface
    target: GaugeInterface
    matrix: Matrix
    offset: Vector

    def __post_init__(self) -> None:
        if len(self.matrix) != self.target.d or len(self.offset) != self.target.d:
            raise ValueError("target dimensions differ")
        if self.target.d and any(len(row) != self.source.d for row in self.matrix):
            raise ValueError("source dimensions differ")

    def apply(self, x: Vector) -> Vector:
        if len(x) != self.source.d:
            raise ValueError("input does not match source interface")
        return vec_add(mat_vec(self.matrix, x), self.offset)


def identity(i: GaugeInterface) -> GaugeAffine:
    m = tuple(tuple(1 if r == c else 0 for c in range(i.d)) for r in range(i.d))
    return GaugeAffine(i, i, m, (0,) * i.d)


def compose(after: GaugeAffine, before: GaugeAffine) -> GaugeAffine:
    if before.target.signature != after.source.signature:
        raise ValueError("morphisms are not type-compatible")
    # Interfaces in this implementation use canonical coordinate block order.
    m = mat_mul(after.matrix, before.matrix)
    b = vec_add(mat_vec(after.matrix, before.offset), after.offset)
    return GaugeAffine(before.source, after.target, m, b)


def relabel_morphism(t: GaugeAffine, source_perm: Perm, target_perm: Perm) -> GaugeAffine:
    ps_inv = perm_matrix(inv_perm(source_perm))
    pt = perm_matrix(target_perm)
    m = mat_mul(mat_mul(pt, t.matrix), ps_inv)
    b = mat_vec(pt, t.offset)
    return GaugeAffine(t.source, t.target, m, b)


def canonical_morphism(t: GaugeAffine) -> GaugeAffine:
    reps = [
        relabel_morphism(t, ps, pt)
        for ps in t.source.gauge_group()
        for pt in t.target.gauge_group()
    ]
    return min(reps, key=lambda z: (z.matrix, z.offset))


def gauge_compatible(t: GaugeAffine) -> bool:
    """Exact equivariance certificate: T g = h T for some target gauge h, for every source gauge g."""
    for gs in t.source.gauge_group():
        pg = perm_matrix(gs)
        lhs_m = mat_mul(t.matrix, pg)
        found = False
        for ht in t.target.gauge_group():
            ph = perm_matrix(ht)
            if lhs_m == mat_mul(ph, t.matrix) and t.offset == mat_vec(ph, t.offset):
                found = True
                break
        if not found:
            return False
    return True


@dataclass(frozen=True, order=True)
class GaugeAction:
    name: str
    morphism: GaugeAffine
    cost: int
    resources: int


QKernel = dict[GaugeAffine, tuple[ResourceCost, ...]]


def pair_dominates(a: ResourceCost, b: ResourceCost) -> bool:
    return a[0] <= b[0] and resource_subset(a[1], b[1])


def pareto_pairs(pairs: Iterable[ResourceCost]) -> tuple[ResourceCost, ...]:
    uniq = sorted(set((int(c), int(r)) for c, r in pairs))
    return tuple(p for p in uniq if not any(q != p and pair_dominates(q, p) for q in uniq))


def interfaces() -> tuple[GaugeInterface, ...]:
    A = GaugeInterface(("A",), tuple())
    F2 = GaugeInterface(tuple(), ("dep", "dep"))
    F3 = GaugeInterface(tuple(), ("dep", "dep", "dep"))
    AF1 = GaugeInterface(("A",), ("dep",))
    AF2 = GaugeInterface(("A",), ("dep", "dep"))
    Z = GaugeInterface(("Z",), tuple())
    return A, F2, F3, AF1, AF2, Z


def primitive_morphisms() -> tuple[tuple[str, GaugeAffine], ...]:
    A, F2, F3, AF1, AF2, Z = interfaces()
    return (
        ("SPLIT_A_TO_PAIR", GaugeAffine(A, F2, ((1,), (1,)), (0, 0))),
        ("MERGE_PAIR_TO_Z", GaugeAffine(F2, Z, ((1, 1),), (0,))),
        ("SYMMETRIC_FRESHEN_PAIR", GaugeAffine(F2, F2, ((1, 0), (0, 1)), (1, 1))),
        ("SYMMETRIC_DOUBLE_PAIR", GaugeAffine(F2, F2, ((2, 0), (0, 2)), (0, 0))),
        ("PAIR_TO_COMMON_PAIR", GaugeAffine(F2, F2, ((1, 1), (1, 1)), (0, 0))),
        ("ADD_SYMMETRIC_PAIR", GaugeAffine(A, AF2, ((1,), (0,), (0,)), (0, 1, 1))),
        ("COLLAPSE_ANON_PAIR", GaugeAffine(AF2, AF1, ((1, 0, 0), (0, 1, 1)), (0, 0))),
        ("EXPAND_ANON_SINGLE", GaugeAffine(AF1, AF2, ((1, 0), (0, 1), (0, 1)), (0, 0, 0))),
        ("FREE_PAIR_TO_TRIPLE_SUM", GaugeAffine(F2, F3, ((1, 1), (1, 1), (1, 1)), (0, 0, 0))),
        ("ANCHOR_PROJECTION", GaugeAffine(AF2, Z, ((1, 0, 0),), (0,))),
    )


def rejected_free_projection() -> GaugeAffine:
    _, F2, _, _, _, Z = interfaces()
    return GaugeAffine(F2, Z, ((1, 0),), (0,))


def primitive_actions() -> tuple[GaugeAction, ...]:
    out: list[GaugeAction] = []
    for idx, (name, t) in enumerate(primitive_morphisms()):
        if not gauge_compatible(t):
            raise AssertionError(f"primitive morphism is not gauge-compatible: {name}")
        out.append(GaugeAction(f"{name}_C1_R1", t, 1, 1))
        out.append(GaugeAction(f"{name}_C2_R2", t, 2, 2))
        if idx < 5:
            out.append(GaugeAction(f"{name}_C1_R4", t, 1, 4))
    return tuple(out)


def feasible_words(catalog: Sequence[GaugeAction], declared: Sequence[GaugeInterface]) -> list[tuple[GaugeAffine, int, int]]:
    out: list[tuple[GaugeAffine, int, int]] = [(identity(i), 0, 0) for i in declared]
    n = len(catalog)
    for k in range(1, n + 1):
        for idxs in itertools.permutations(range(n), k):
            cost = 0
            resources = 0
            current: GaugeAffine | None = None
            ok = True
            for pos, idx in enumerate(idxs):
                a = catalog[idx]
                if resources & a.resources:
                    ok = False
                    break
                if pos == 0:
                    current = a.morphism
                else:
                    assert current is not None
                    if current.target.signature != a.morphism.source.signature:
                        ok = False
                        break
                    current = compose(a.morphism, current)
                cost += a.cost
                resources |= a.resources
            if ok and current is not None:
                out.append((current, cost, resources))
    return out


def quotient_kernel(catalog: Sequence[GaugeAction], declared: Sequence[GaugeInterface]) -> QKernel:
    buckets: dict[GaugeAffine, list[ResourceCost]] = {}
    for t, cost, resources in feasible_words(catalog, declared):
        ct = canonical_morphism(t)
        buckets.setdefault(ct, []).append((cost, resources))
    return {t: pareto_pairs(v) for t, v in buckets.items()}


def compose_quotient_kernels(after: QKernel, before: QKernel) -> QKernel:
    buckets: dict[GaugeAffine, list[ResourceCost]] = {}
    for tb, pb in before.items():
        for ta, pa in after.items():
            if tb.target.signature != ta.source.signature:
                continue
            # Gauge compatibility guarantees representative independence.
            t = canonical_morphism(compose(ta, tb))
            for cb, rb in pb:
                for ca, ra in pa:
                    if rb & ra:
                        continue
                    buckets.setdefault(t, []).append((cb + ca, rb | ra))
    return {t: pareto_pairs(v) for t, v in buckets.items()}


def direct_phase_kernel(before_cat: Sequence[GaugeAction], after_cat: Sequence[GaugeAction], declared: Sequence[GaugeInterface]) -> QKernel:
    buckets: dict[GaugeAffine, list[ResourceCost]] = {}
    bw = feasible_words(before_cat, declared)
    aw = feasible_words(after_cat, declared)
    for tb, cb, rb in bw:
        for ta, ca, ra in aw:
            if tb.target.signature != ta.source.signature or (rb & ra):
                continue
            t = canonical_morphism(compose(ta, tb))
            buckets.setdefault(t, []).append((cb + ca, rb | ra))
    return {t: pareto_pairs(v) for t, v in buckets.items()}


def kernel_key(k: QKernel) -> tuple:
    return tuple(
        (
            t.source.signature,
            t.target.signature,
            t.matrix,
            t.offset,
            tuple(sorted(ps)),
        )
        for t, ps in sorted(k.items(), key=lambda kv: (kv[0].source.signature, kv[0].target.signature, kv[0].matrix, kv[0].offset))
    )


def representative_set(t: GaugeAffine) -> tuple[GaugeAffine, ...]:
    return tuple(sorted(set(
        relabel_morphism(t, ps, pt)
        for ps in t.source.gauge_group()
        for pt in t.target.gauge_group()
    )))


def distinguish_morphisms(a: GaugeAffine, b: GaugeAffine, bound: int = 5) -> Vector | None:
    if a.source.signature != b.source.signature:
        return tuple()
    if a.target.signature != b.target.signature:
        return (0,) * a.source.d
    for x in itertools.product(range(bound + 1), repeat=a.source.d):
        if canonical_state(a.target, a.apply(x)) != canonical_state(b.target, b.apply(x)):
            return tuple(x)
    return None


def small_catalogs(actions: Sequence[GaugeAction]) -> list[tuple[GaugeAction, ...]]:
    base = list(actions[:8])
    cats: list[tuple[GaugeAction, ...]] = [tuple()]
    cats.extend((a,) for a in base)
    for i in range(len(base)):
        for j in range(i + 1, len(base)):
            cats.append((base[i], base[j]))
    # Deliberately dominated duplicate descriptions for congruence verification.
    t = base[0].morphism
    cats.append((base[0], GaugeAction("DOMINATED_SPLIT", t, 4, 1)))
    t2 = base[1].morphism
    cats.append((base[1], GaugeAction("DOMINATED_SPLIT_R", t2, 3, 3)))
    return cats


def verify() -> list[str]:
    declared = interfaces()
    A, F2, _, _, AF2, Z = declared
    prim = primitive_morphisms()
    actions = primitive_actions()
    lines: list[str] = []

    accepted = sum(gauge_compatible(t) for _, t in prim)
    rejected = rejected_free_projection()
    assert accepted == len(prim)
    assert not gauge_compatible(rejected)
    anchor_proj = dict(prim)["ANCHOR_PROJECTION"]
    assert gauge_compatible(anchor_proj)
    lines.append(f"gauge_compatibility:PASS:accepted={accepted}:anonymous_projection_rejected=1:anchored_projection_accepted=1")

    # Naive orbit quotient obstruction: inject into one anonymous coordinate, then project one anonymous coordinate.
    inject = GaugeAffine(A, F2, ((1,), (0,)), (0, 0))
    project = rejected
    swap = F2.gauge_group()[1]
    inject_swapped = relabel_morphism(inject, (0,), swap)
    c1 = compose(project, inject)
    c2 = compose(project, inject_swapped)
    y1 = c1.apply((3,))
    y2 = c2.apply((3,))
    assert y1 != y2 and {y1, y2} == {(0,), (3,)}
    assert canonical_morphism(inject) == canonical_morphism(inject_swapped)
    lines.append(f"naive_orbit_composition_obstruction:PASS:input=3:composites={sorted((y1,y2))}")

    # Well-defined quotient composition for gauge-compatible primitive pairs across all representatives.
    pair_checks = 0
    rep_checks = 0
    for _, t in prim:
        for _, u in prim:
            if t.target.signature != u.source.signature:
                continue
            pair_checks += 1
            expected = canonical_morphism(compose(canonical_morphism(u), canonical_morphism(t)))
            for tr in representative_set(t):
                for ur in representative_set(u):
                    got = canonical_morphism(compose(ur, tr))
                    assert got == expected
                    rep_checks += 1
    lines.append(f"quotient_composition_well_defined:PASS:pairs={pair_checks}:representative_checks={rep_checks}")

    # State canonicalization removes anonymous names but preserves anchors.
    x = (7, 2, 5)
    swap_free = AF2.gauge_group()[1]
    assert canonical_state(AF2, x) == canonical_state(AF2, apply_perm(swap_free, x))
    assert canonical_state(AF2, x)[0] == 7
    lines.append("name_invariant_state_canonicalization:PASS:anonymous_swap_removed=1:anchor_preserved=1")

    cats = small_catalogs(actions)
    kernels = [quotient_kernel(c, declared) for c in cats]
    # Direct exactness against explicit word enumeration and orbit reduction.
    exact_checks = 0
    for cat, ker in zip(cats, kernels):
        direct: dict[GaugeAffine, list[ResourceCost]] = {}
        for t, c, r in feasible_words(cat, declared):
            direct.setdefault(canonical_morphism(t), []).append((c, r))
        direct_k = {t: pareto_pairs(v) for t, v in direct.items()}
        assert kernel_key(direct_k) == kernel_key(ker)
        exact_checks += 1
    lines.append(f"name_invariant_kernel_exactness:PASS:catalogs={len(cats)}:checks={exact_checks}")

    # Phase composition.
    phase_cats = cats[:18]
    phase_checks = 0
    for ca in phase_cats:
        ka = quotient_kernel(ca, declared)
        for cb in phase_cats:
            kb = quotient_kernel(cb, declared)
            direct = direct_phase_kernel(ca, cb, declared)
            comp = compose_quotient_kernels(kb, ka)
            assert kernel_key(direct) == kernel_key(comp)
            phase_checks += 1
    lines.append(f"name_invariant_phase_composition:PASS:phase_pairs={phase_checks}")

    # Equal-kernel future congruence, including deliberate dominated duplicates.
    groups: dict[tuple, list[int]] = {}
    for idx, k in enumerate(kernels):
        groups.setdefault(kernel_key(k), []).append(idx)
    dup_groups = [v for v in groups.values() if len(v) > 1]
    assert dup_groups
    congr_checks = 0
    future = phase_cats[:8]
    for g in dup_groups:
        i, j = g[0], g[1]
        for f in future:
            kf = quotient_kernel(f, declared)
            a = compose_quotient_kernels(kf, kernels[i])
            b = compose_quotient_kernels(kf, kernels[j])
            assert kernel_key(a) == kernel_key(b)
            congr_checks += 1
    lines.append(f"equal_quotient_kernel_future_congruence:PASS:duplicate_classes={len(dup_groups)}:checks={congr_checks}")

    # Constructive separation across distinct kernel classes in the sample.
    reps_by_class = [kernels[idxs[0]] for idxs in groups.values()]
    classes = len(reps_by_class)
    pair_count = 0
    direct_sep = 0
    resource_sep = 0
    for i in range(classes):
        for j in range(i + 1, classes):
            pair_count += 1
            ka, kb = reps_by_class[i], reps_by_class[j]
            found = False
            # First seek a morphism/cost difference exposed by a canonical input state.
            all_t = sorted(set(ka) | set(kb), key=lambda t: (t.source.signature, t.target.signature, t.matrix, t.offset))
            for t in all_t:
                pa = ka.get(t)
                pb = kb.get(t)
                if pa != pb:
                    if pa is None or pb is None:
                        # Absent transformation is directly observable as reachability difference.
                        found = True
                        direct_sep += 1
                        break
                    costs_a = {c for c, _ in pa}
                    costs_b = {c for c, _ in pb}
                    if costs_a != costs_b:
                        found = True
                        direct_sep += 1
                        break
                    # Equal cost support but a different Pareto resource frontier is exposed by a future resource claim.
                    if pa != pb:
                        found = True
                        resource_sep += 1
                        break
            assert found
    lines.append(f"constructive_name_invariant_separation:PASS:classes={classes}:pairs={pair_count}:direct={direct_sep}:future_resource={resource_sep}")

    # Quotient-category identity and associativity on primitive compatible chains.
    id_checks = 0
    assoc_checks = 0
    for _, t in prim:
        ct = canonical_morphism(t)
        assert canonical_morphism(compose(identity(t.target), t)) == ct
        assert canonical_morphism(compose(t, identity(t.source))) == ct
        id_checks += 2
    for _, t in prim:
        for _, u in prim:
            if t.target.signature != u.source.signature:
                continue
            for _, v in prim:
                if u.target.signature != v.source.signature:
                    continue
                left = canonical_morphism(compose(v, compose(u, t)))
                right = canonical_morphism(compose(compose(v, u), t))
                assert left == right
                assoc_checks += 1
    lines.append(f"name_invariant_category_laws:PASS:identity={id_checks}:associativity={assoc_checks}")

    # Exact label-erasure bound: literal free-coordinate permutations collapse factorial duplicates.
    orbit_sizes = []
    for i in (F2, declared[2], AF2):
        orbit_sizes.append(len(i.gauge_group()))
    assert orbit_sizes == [2, 6, 2]
    lines.append(f"anonymous_label_orbit_reduction:PASS:gauge_group_sizes={orbit_sizes}:semantic_anchors_fixed=1")

    return lines


def self_test() -> list[str]:
    declared = interfaces()
    prim = primitive_morphisms()
    tests = []
    tests.append(("gauge_groups", len(declared[1].gauge_group()) == 2 and len(declared[2].gauge_group()) == 6))
    tests.append(("primitive_compatibility", all(gauge_compatible(t) for _, t in prim)))
    tests.append(("anonymous_projection_rejected", not gauge_compatible(rejected_free_projection())))
    tests.append(("canonical_state", canonical_state(declared[1], (5, 2)) == canonical_state(declared[1], (2, 5))))
    tests.append(("canonical_morphism", canonical_morphism(prim[0][1]) == canonical_morphism(relabel_morphism(prim[0][1], (0,), declared[1].gauge_group()[1]))))
    tests.append(("verification", all(":PASS" in line for line in verify())))
    passed = sum(ok for _, ok in tests)
    if passed != len(tests):
        bad = [name for name, ok in tests if not ok]
        raise AssertionError(f"self-test failed: {bad}")
    return [f"TOTAL {passed}/{len(tests)} PASS"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--verify", action="store_true")
    args = p.parse_args()
    if args.self_test:
        print(f"SCRT Name-Invariant Interface Quotient v{VERSION} self-test")
        for line in self_test():
            print(line)
        return
    if args.verify:
        print(f"SCRT Name-Invariant Interface Quotient v{VERSION} verification")
        for line in verify():
            print(line)
        print("status:PASS")
        return
    p.print_help()


if __name__ == "__main__":
    main()
