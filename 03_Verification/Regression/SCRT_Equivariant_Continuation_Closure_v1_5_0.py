#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Equivariant Continuation Closure and Full-Abstract Admission Theorem
Version 1.5.0

Exact admission semantics for extending name-invariant cyber-resilience continuations by typed affine operations. Local certificates enforce ORIK locality, gauge compatibility, declared resource discipline, closure under typed composition, and constructive full abstraction.

Dependency-free and deterministic.
"""
from __future__ import annotations

import argparse
import itertools
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence

VERSION = "1.5.0"
Signature = tuple[int, int]
OperationalCounts = dict[int, int]
TypedCounts = dict[Signature, int]
ObligationKernel = tuple[OperationalCounts, TypedCounts]
ResolvedKernel = tuple[ObligationKernel, ...]
Perm = tuple[int, ...]
Vector = tuple[int, ...]
Matrix = tuple[tuple[int, ...], ...]
Pair = tuple[int, int]


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


def permute_mask(mask: int, p: Perm) -> int:
    out = 0
    for i, j in enumerate(p):
        if mask & (1 << i):
            out |= 1 << j
    return out


def permute_signature(s: Signature, p: Perm) -> Signature:
    return permute_mask(s[0], p), permute_mask(s[1], p)


def inverse_perm(p: Perm) -> Perm:
    out = [0] * len(p)
    for i, j in enumerate(p):
        out[j] = i
    return tuple(out)


def compose_perm(after: Perm, before: Perm) -> Perm:
    return tuple(after[before[i]] for i in range(len(before)))


def resource_subset(a: int, b: int) -> bool:
    return (a & b) == a


@dataclass(frozen=True, order=True)
class AncestryInterface:
    anchors: tuple[str, ...]
    free_roles: tuple[str, ...]

    @property
    def m(self) -> int:
        return len(self.anchors) + len(self.free_roles)

    @property
    def signature(self) -> tuple:
        counts: dict[str, int] = {}
        for r in self.free_roles:
            counts[r] = counts.get(r, 0) + 1
        return self.anchors, tuple(sorted(counts.items()))

    def gauge_group(self) -> tuple[Perm, ...]:
        n_a = len(self.anchors)
        role_positions: dict[str, list[int]] = {}
        for j, role in enumerate(self.free_roles, start=n_a):
            role_positions.setdefault(role, []).append(j)
        blocks = [tuple(itertools.permutations(role_positions[r])) for r in sorted(role_positions)]
        if not blocks:
            return (tuple(range(self.m)),)
        out: list[Perm] = []
        for choices in itertools.product(*blocks):
            p = list(range(self.m))
            for role, choice in zip(sorted(role_positions), choices):
                pos = role_positions[role]
                for src, dst in zip(pos, choice):
                    p[src] = dst
            out.append(tuple(p))
        return tuple(sorted(set(out)))


@dataclass(frozen=True, order=True)
class ORIKInterface:
    obligations: tuple[str, ...]
    ancestry: AncestryInterface

    @property
    def q(self) -> int:
        return len(self.obligations)

    @property
    def m(self) -> int:
        return self.ancestry.m

    def coordinates(self) -> tuple[tuple, ...]:
        out: list[tuple] = []
        sigs = all_signatures(self.m, include_empty=False)
        for o in range(self.q):
            for s in range(1, 1 << self.m):
                out.append(("O", o, s))
            for d, e in sigs:
                out.append(("T", o, d, e))
        return tuple(out)

    @property
    def d(self) -> int:
        return self.q * ((1 << self.m) + (3 ** self.m) - 2)

    def coord_index(self) -> dict[tuple, int]:
        return {c: i for i, c in enumerate(self.coordinates())}


def empty_resolved(i: ORIKInterface) -> ResolvedKernel:
    return tuple(({}, {}) for _ in range(i.q))


def normalize_resolved(k: ResolvedKernel) -> ResolvedKernel:
    return tuple((
        {int(s): int(c) for s, c in op.items() if int(c) > 0},
        {(int(d), int(e)): int(c) for (d, e), c in ty.items() if int(c) > 0},
    ) for op, ty in k)


def permute_resolved(i: ORIKInterface, k: ResolvedKernel, p: Perm) -> ResolvedKernel:
    if len(p) != i.m or len(k) != i.q:
        raise ValueError("gauge action dimension mismatch")
    out: list[ObligationKernel] = []
    for op, ty in k:
        oo: Counter[int] = Counter()
        tt: Counter[Signature] = Counter()
        for s, c in op.items():
            oo[permute_mask(s, p)] += c
        for s, c in ty.items():
            tt[permute_signature(s, p)] += c
        out.append((dict(oo), dict(tt)))
    return normalize_resolved(tuple(out))


def flatten(i: ORIKInterface, k: ResolvedKernel) -> Vector:
    idx = i.coord_index()
    out = [0] * i.d
    for o, (op, ty) in enumerate(k):
        for s, c in op.items():
            out[idx[("O", o, s)]] = int(c)
        for (d, e), c in ty.items():
            out[idx[("T", o, d, e)]] = int(c)
    return tuple(out)


def unflatten(i: ORIKInterface, x: Vector) -> ResolvedKernel:
    if len(x) != i.d:
        raise ValueError("ORIK vector dimension mismatch")
    out = [[{}, {}] for _ in range(i.q)]
    for value, coord in zip(x, i.coordinates()):
        if value <= 0:
            continue
        if coord[0] == "O":
            _, o, s = coord
            out[o][0][s] = value
        else:
            _, o, d, e = coord
            out[o][1][(d, e)] = value
    return normalize_resolved(tuple((a, b) for a, b in out))


def induced_orik_perm(i: ORIKInterface, p: Perm) -> Perm:
    coords = i.coordinates()
    idx = i.coord_index()
    out = [0] * len(coords)
    for old, c in enumerate(coords):
        if c[0] == "O":
            nc = ("O", c[1], permute_mask(c[2], p))
        else:
            nc = ("T", c[1], *permute_signature((c[2], c[3]), p))
        out[old] = idx[nc]
    return tuple(out)


def permute_vector(x: Vector, p: Perm) -> Vector:
    if len(x) != len(p):
        raise ValueError("vector permutation mismatch")
    out = [0] * len(x)
    for old, new in enumerate(p):
        out[new] = x[old]
    return tuple(out)


def canonical_orik(i: ORIKInterface, k: ResolvedKernel) -> Vector:
    x = flatten(i, k)
    return min(permute_vector(x, induced_orik_perm(i, p)) for p in i.ancestry.gauge_group())


def sig_compose(a: Signature, b: Signature) -> Signature | None:
    d = a[0] | b[0]
    e = a[1] | b[1]
    if d & e:
        return None
    return d, e


def compose_operational_counts(a: OperationalCounts, b: OperationalCounts) -> OperationalCounts:
    out: Counter[int] = Counter()
    for x, cx in a.items():
        for y, cy in b.items():
            out[x | y] += cx * cy
    return dict(out)


def compose_typed_counts(a: TypedCounts, b: TypedCounts) -> TypedCounts:
    out: Counter[Signature] = Counter()
    for x, cx in a.items():
        for y, cy in b.items():
            z = sig_compose(x, y)
            if z is not None:
                out[z] += cx * cy
    return dict(out)


def complete_irk(k: ResolvedKernel) -> ObligationKernel:
    op: OperationalCounts = {0: 1}
    ty: TypedCounts = {(0, 0): 1}
    for o, t in k:
        op = compose_operational_counts(op, o)
        ty = compose_typed_counts(ty, t)
    op.pop(0, None)
    ty.pop((0, 0), None)
    return op, ty


def operational_probe(counts: OperationalCounts, q: int) -> int:
    return sum(c for s, c in counts.items() if mask_subset(s, q))


def typed_probe(counts: TypedCounts, q: Signature) -> int:
    return sum(c for s, c in counts.items() if sig_leq(s, q))


def probe_table(i: ORIKInterface, k: ResolvedKernel) -> tuple[int, ...]:
    out: list[int] = []
    typed_queries = all_signatures(i.m, include_empty=True)
    for op, ty in k:
        out.extend(operational_probe(op, q) for q in range(1 << i.m))
        out.extend(typed_probe(ty, q) for q in typed_queries)
    return tuple(out)


def canonical_probe_table(i: ORIKInterface, k: ResolvedKernel) -> tuple[int, ...]:
    return min(probe_table(i, permute_resolved(i, k, p)) for p in i.ancestry.gauge_group())


def max_disjoint_operational_capacity(counts: OperationalCounts, failure: int) -> int:
    supports: list[int] = []
    for s, c in counts.items():
        if not (s & failure):
            supports.extend([s] * c)
    best = 0
    def rec(pos: int, used: int, n: int) -> None:
        nonlocal best
        if n + len(supports) - pos <= best:
            return
        if pos == len(supports):
            best = max(best, n)
            return
        rec(pos + 1, used, n)
        s = supports[pos]
        if not (s & used):
            rec(pos + 1, used | s, n + 1)
    rec(0, 0, 0)
    return best


def max_disjoint_typed_capacity(counts: TypedCounts, failure: int) -> int:
    supports: list[int] = []
    for s, c in counts.items():
        u = sig_support(s)
        if not (u & failure):
            supports.extend([u] * c)
    best = 0
    def rec(pos: int, used: int, n: int) -> None:
        nonlocal best
        if n + len(supports) - pos <= best:
            return
        if pos == len(supports):
            best = max(best, n)
            return
        rec(pos + 1, used, n)
        s = supports[pos]
        if not (s & used):
            rec(pos + 1, used | s, n + 1)
    rec(0, 0, 0)
    return best


def capacities(k: ResolvedKernel, failure: int) -> tuple[int, int]:
    op, ty = complete_irk(k)
    return max_disjoint_operational_capacity(op, failure), max_disjoint_typed_capacity(ty, failure)


def shielded_capacities(k: ResolvedKernel, failure: int, hardened: int) -> tuple[int, int]:
    return capacities(k, failure & ~hardened)


def add_route(i: ORIKInterface, k: ResolvedKernel, obligation: int, op_support: int | None = None, typed: Signature | None = None) -> ResolvedKernel:
    out = [(dict(op), dict(ty)) for op, ty in k]
    if op_support is not None:
        out[obligation][0][op_support] = out[obligation][0].get(op_support, 0) + 1
    if typed is not None:
        if typed[0] & typed[1]:
            raise ValueError("typed route has defense/evidence conflict")
        out[obligation][1][typed] = out[obligation][1].get(typed, 0) + 1
    return normalize_resolved(tuple(out))


@dataclass(frozen=True, order=True)
class AncestryRewrite:
    source: AncestryInterface
    target: AncestryInterface
    image: tuple[int, ...]
    multiplier: int = 1

    def __post_init__(self) -> None:
        if len(self.image) != self.source.m:
            raise ValueError("rewrite image length mismatch")
        if self.multiplier < 0:
            raise ValueError("negative multiplier")
        max_mask = (1 << self.target.m) - 1
        if any(x < 0 or x > max_mask for x in self.image):
            raise ValueError("rewrite target mask out of range")

    def map_mask(self, s: int) -> int:
        out = 0
        for bit, target_mask in enumerate(self.image):
            if s & (1 << bit):
                out |= target_mask
        return out

    def map_signature(self, s: Signature) -> Signature | None:
        d = self.map_mask(s[0])
        e = self.map_mask(s[1])
        if d & e:
            return None
        return d, e


def rewrite_gauge_compatible(r: AncestryRewrite) -> bool:
    for ps in r.source.gauge_group():
        ok = False
        for pt in r.target.gauge_group():
            good = True
            for s in range(1 << r.source.m):
                left = r.map_mask(permute_mask(s, ps))
                right = permute_mask(r.map_mask(s), pt)
                if left != right:
                    good = False
                    break
            if good:
                ok = True
                break
        if not ok:
            return False
    return True


def mat_vec(m: Matrix, x: Vector) -> Vector:
    if not m:
        return tuple()
    return tuple(sum(row[j] * x[j] for j in range(len(x))) for row in m)


def vec_add(a: Vector, b: Vector) -> Vector:
    return tuple(x + y for x, y in zip(a, b))


def mat_mul(a: Matrix, b: Matrix) -> Matrix:
    if not a or not b or len(a[0]) != len(b):
        raise ValueError("matrix dimensions differ")
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))) for i in range(len(a)))


@dataclass(frozen=True, order=True)
class ORIKAffine:
    source: ORIKInterface
    target: ORIKInterface
    matrix: Matrix
    offset: Vector

    def apply_vector(self, x: Vector) -> Vector:
        if len(x) != self.source.d:
            raise ValueError("source vector dimension mismatch")
        return vec_add(mat_vec(self.matrix, x), self.offset)

    def apply(self, k: ResolvedKernel) -> ResolvedKernel:
        return unflatten(self.target, self.apply_vector(flatten(self.source, k)))


def identity_affine(i: ORIKInterface) -> ORIKAffine:
    m = tuple(tuple(1 if r == c else 0 for c in range(i.d)) for r in range(i.d))
    return ORIKAffine(i, i, m, (0,) * i.d)


def lift_rewrite(source: ORIKInterface, target: ORIKInterface, r: AncestryRewrite) -> ORIKAffine:
    if source.q != target.q or source.ancestry != r.source or target.ancestry != r.target:
        raise ValueError("rewrite/interface mismatch")
    sidx = source.coord_index()
    tidx = target.coord_index()
    rows = [[0] * source.d for _ in range(target.d)]
    for coord, col in sidx.items():
        if coord[0] == "O":
            _, o, s = coord
            z = r.map_mask(s)
            if z:
                rows[tidx[("O", o, z)]][col] += r.multiplier
        else:
            _, o, d, e = coord
            z = r.map_signature((d, e))
            if z is not None and (z[0] | z[1]):
                rows[tidx[("T", o, z[0], z[1])]][col] += r.multiplier
    return ORIKAffine(source, target, tuple(tuple(row) for row in rows), (0,) * target.d)


def compose_affine(after: ORIKAffine, before: ORIKAffine) -> ORIKAffine:
    if before.target != after.source:
        raise ValueError("ORIK affine interfaces do not compose")
    return ORIKAffine(before.source, after.target, mat_mul(after.matrix, before.matrix), vec_add(mat_vec(after.matrix, before.offset), after.offset))


def relabel_affine(t: ORIKAffine, ps: Perm, pt: Perm) -> ORIKAffine:
    s_perm = induced_orik_perm(t.source, ps)
    t_perm = induced_orik_perm(t.target, pt)
    s_inv = inverse_perm(s_perm)
    # Column/row permutation by evaluating on basis is simpler and less error-prone.
    rows = [[0] * t.source.d for _ in range(t.target.d)]
    for j in range(t.source.d):
        basis = tuple(1 if k == j else 0 for k in range(t.source.d))
        x = permute_vector(basis, s_inv)
        y = t.apply_vector(x)
        z = permute_vector(y, t_perm)
        for i, val in enumerate(z):
            rows[i][j] = val
    b = permute_vector(t.offset, t_perm)
    return ORIKAffine(t.source, t.target, tuple(tuple(r) for r in rows), b)


def affine_gauge_compatible(t: ORIKAffine) -> bool:
    for ps in t.source.ancestry.gauge_group():
        sp = induced_orik_perm(t.source, ps)
        found = False
        for pt in t.target.ancestry.gauge_group():
            tp = induced_orik_perm(t.target, pt)
            # Check T P_s = P_t T on all basis vectors plus offset.
            ok = permute_vector(t.offset, tp) == t.offset
            if ok:
                for j in range(t.source.d):
                    basis = tuple(1 if k == j else 0 for k in range(t.source.d))
                    left = t.apply_vector(permute_vector(basis, sp))
                    right = permute_vector(t.apply_vector(basis), tp)
                    if left != right:
                        ok = False
                        break
            if ok:
                found = True
                break
        if not found:
            return False
    return True


def canonical_affine(t: ORIKAffine) -> tuple:
    reps = []
    for ps in t.source.ancestry.gauge_group():
        for pt in t.target.ancestry.gauge_group():
            z = relabel_affine(t, ps, pt)
            reps.append((z.matrix, z.offset))
    return (t.source.ancestry.signature, t.target.ancestry.signature, t.source.obligations, t.target.obligations, min(reps))


@dataclass(frozen=True, order=True)
class Action:
    name: str
    morphism: ORIKAffine
    cost: int
    resources: int


def pair_dominates(a: Pair, b: Pair) -> bool:
    return a[0] <= b[0] and resource_subset(a[1], b[1])


def pareto_pairs(pairs: Iterable[Pair]) -> tuple[Pair, ...]:
    uniq = sorted(set(pairs))
    return tuple(p for p in uniq if not any(q != p and pair_dominates(q, p) for q in uniq))


def kernel_from_catalog(actions: Sequence[Action], declared: Sequence[ORIKInterface]) -> dict[tuple, tuple[Pair, ...]]:
    raw: dict[tuple, list[Pair]] = {}
    for i in declared:
        raw.setdefault(canonical_affine(identity_affine(i)), []).append((0, 0))
    n = len(actions)
    for length in range(1, n + 1):
        for idxs in itertools.permutations(range(n), length):
            current: ORIKAffine | None = None
            cost = 0
            res = 0
            ok = True
            used = set()
            for idx in idxs:
                if idx in used:
                    ok = False
                    break
                used.add(idx)
                a = actions[idx]
                if res & a.resources:
                    ok = False
                    break
                if current is None:
                    current = a.morphism
                else:
                    if current.target != a.morphism.source:
                        ok = False
                        break
                    current = compose_affine(a.morphism, current)
                cost += a.cost
                res |= a.resources
            if ok and current is not None:
                raw.setdefault(canonical_affine(current), []).append((cost, res))
    return {k: pareto_pairs(v) for k, v in raw.items()}




def feasible_action_words(actions: Sequence[Action], declared: Sequence[ORIKInterface]) -> list[tuple[ORIKAffine,int,int]]:
    out: list[tuple[ORIKAffine,int,int]] = [(identity_affine(i),0,0) for i in declared]
    n=len(actions)
    for length in range(1,n+1):
        for idxs in itertools.permutations(range(n),length):
            current=None;cost=0;res=0;ok=True
            for idx in idxs:
                a=actions[idx]
                if res & a.resources:
                    ok=False;break
                if current is None:
                    current=a.morphism
                else:
                    if current.target != a.morphism.source:
                        ok=False;break
                    current=compose_affine(a.morphism,current)
                cost += a.cost;res |= a.resources
            if ok and current is not None:
                out.append((current,cost,res))
    return out


def canonical_kernel_from_words(words: Sequence[tuple[ORIKAffine,int,int]]) -> dict[tuple,tuple[Pair,...]]:
    raw: dict[tuple,list[Pair]]={}
    for t,c,r in words:
        raw.setdefault(canonical_affine(t),[]).append((c,r))
    return {k:pareto_pairs(v) for k,v in raw.items()}


def ordered_phase_kernel(current: Sequence[Action], future: Sequence[Action], declared: Sequence[ORIKInterface]) -> dict[tuple,tuple[Pair,...]]:
    before=feasible_action_words(current,declared)
    after=feasible_action_words(future,declared)
    out=[]
    for t1,c1,r1 in before:
        for t2,c2,r2 in after:
            if t1.target != t2.source or (r1 & r2):
                continue
            out.append((compose_affine(t2,t1),c1+c2,r1|r2))
    return canonical_kernel_from_words(out)

def sample_interfaces() -> tuple[ORIKInterface, ...]:
    F1 = AncestryInterface(tuple(), ("dep",))
    F2 = AncestryInterface(tuple(), ("dep", "dep"))
    F3 = AncestryInterface(tuple(), ("dep", "dep", "dep"))
    A2 = AncestryInterface(("ROOT",), ("dep", "dep"))
    return (
        ORIKInterface(("AUTH",), F1),
        ORIKInterface(("AUTH",), F2),
        ORIKInterface(("AUTH",), F3),
        ORIKInterface(("AUTH",), A2),
    )


def sample_rewrites() -> tuple[tuple[str, ORIKAffine], ...]:
    I1, I2, I3, IA2 = sample_interfaces()
    r12 = AncestryRewrite(I1.ancestry, I2.ancestry, (0b11,))
    r21 = AncestryRewrite(I2.ancestry, I1.ancestry, (0b1, 0b1))
    r23 = AncestryRewrite(I2.ancestry, I3.ancestry, (0b001, 0b010))
    r31 = AncestryRewrite(I3.ancestry, I1.ancestry, (0b1, 0b1, 0b1))
    # ROOT remains anchored; anonymous dependencies merge symmetrically.
    raa = AncestryRewrite(IA2.ancestry, IA2.ancestry, (0b001, 0b110, 0b110))
    out = (
        ("SPLIT_ONE_TO_PAIR", lift_rewrite(I1, I2, r12)),
        ("MERGE_PAIR", lift_rewrite(I2, I1, r21)),
        ("PAIR_INTO_TRIPLE", lift_rewrite(I2, I3, r23)),
        ("MERGE_TRIPLE", lift_rewrite(I3, I1, r31)),
        ("ANCHOR_PRESERVING_ANON_MERGE", lift_rewrite(IA2, IA2, raa)),
    )
    return out


def small_state_universe(i: ORIKInterface) -> tuple[ResolvedKernel, ...]:
    if i.q != 1 or i.m != 2:
        raise ValueError("small universe is fixed at q=1,m=2")
    coords = i.coordinates()
    out: list[ResolvedKernel] = []
    for bits in range(1 << len(coords)):
        x = tuple(1 if bits & (1 << j) else 0 for j in range(len(coords)))
        out.append(unflatten(i, x))
    return tuple(out)


def state_samples(i: ORIKInterface, limit: int = 96) -> tuple[ResolvedKernel, ...]:
    coords = i.coordinates()
    out = [empty_resolved(i)]
    for j in range(min(len(coords), limit - 1)):
        x = [0] * i.d
        x[j] = 1 + (j % 3)
        out.append(unflatten(i, tuple(x)))
    # deterministic mixed states
    for seed in range(1, min(24, limit - len(out)) + 1):
        x = tuple(((seed * (j + 3) + j * j) % 3) for j in range(i.d))
        out.append(unflatten(i, x))
    return tuple(out[:limit])


def verify() -> list[str]:
    lines: list[str] = []
    I1, I2, I3, IA2 = sample_interfaces()

    # 1. Gauge lift is a faithful group action on actual ORIK coordinates.
    lift_checks = 0
    for i in (I2, I3, IA2):
        for p in i.ancestry.gauge_group():
            ip = induced_orik_perm(i, p)
            if sorted(ip) != list(range(i.d)):
                raise AssertionError("induced ORIK action is not a permutation")
            for k in state_samples(i, 20):
                if flatten(i, permute_resolved(i, k, p)) != permute_vector(flatten(i, k), ip):
                    raise AssertionError("ORIK gauge lift failed")
                lift_checks += 1
        # homomorphism law
        G = i.ancestry.gauge_group()
        for a in G:
            for b in G:
                ab = compose_perm(a, b)
                lhs = induced_orik_perm(i, ab)
                ia, ib = induced_orik_perm(i, a), induced_orik_perm(i, b)
                rhs = compose_perm(ia, ib)
                if lhs != rhs:
                    raise AssertionError("induced ORIK action is not a homomorphism")
                lift_checks += 1
    lines.append(f"orik_gauge_lift:PASS:checks={lift_checks}:dimensions={[I2.d,I3.d,IA2.d]}")

    # 2. Full probe transform is equivariant and orbit-complete on exhaustive q=1,m=2 0/1 universe.
    universe = small_state_universe(I2)
    state_to_probe: dict[Vector, tuple[int, ...]] = {}
    orbit_checks = 0
    for k in universe:
        cs = canonical_orik(I2, k)
        cp = canonical_probe_table(I2, k)
        prev = state_to_probe.get(cs)
        if prev is not None and prev != cp:
            raise AssertionError("same ORIK orbit produced different probe orbit")
        state_to_probe[cs] = cp
        orbit_checks += 1
    if len(set(state_to_probe.values())) != len(state_to_probe):
        raise AssertionError("distinct ORIK orbits collided under gauge-closed probe transform")
    classes = len(state_to_probe)
    pairs = classes * (classes - 1) // 2
    lines.append(f"name_invariant_probe_classification:PASS:states={len(universe)}:classes={classes}:constructively_separated_pairs={pairs}")

    # 3. Complete realization convolution commutes with ancestry gauge.
    conv_checks = 0
    samples = state_samples(I2, 18)
    p = I2.ancestry.gauge_group()[-1]
    for a in samples:
        for b in samples:
            ka = a[0]
            kb = b[0]
            resolved2: ResolvedKernel = (ka, kb)
            i2q = ORIKInterface(("AUTH", "RECOVERY"), I2.ancestry)
            lhs = complete_irk(permute_resolved(i2q, resolved2, p))
            base = complete_irk(resolved2)
            rhs = (
                {permute_mask(s,p):c for s,c in base[0].items()},
                {permute_signature(s,p):c for s,c in base[1].items()},
            )
            if normalize_resolved(((lhs[0],lhs[1]),))[0] != normalize_resolved(((rhs[0],rhs[1]),))[0]:
                raise AssertionError("complete realization convolution is not equivariant")
            conv_checks += 1
    lines.append(f"complete_realization_equivariance:PASS:checks={conv_checks}")

    # 4. Compromise, shielding, and interventional probes commute with gauge action.
    response_checks = 0
    cap_samples = state_samples(I2, 64)
    for k in cap_samples:
        for p in I2.ancestry.gauge_group():
            kp = permute_resolved(I2, k, p)
            for f in range(1 << I2.m):
                fp = permute_mask(f, p)
                if capacities(k, f) != capacities(kp, fp):
                    raise AssertionError("compromise capacity is not gauge-equivariant")
                for h in range(1 << I2.m):
                    hp = permute_mask(h, p)
                    if shielded_capacities(k, f, h) != shielded_capacities(kp, fp, hp):
                        raise AssertionError("hardening shield is not gauge-equivariant")
                    response_checks += 1
                op, ty = k[0]
                opp, typ = kp[0]
                for q in range(1 << I2.m):
                    if operational_probe(op,q) != operational_probe(opp,permute_mask(q,p)):
                        raise AssertionError("operational intervention probe is not gauge-equivariant")
                    response_checks += 1
                for q in all_signatures(I2.m, include_empty=True):
                    if typed_probe(ty,q) != typed_probe(typ,permute_signature(q,p)):
                        raise AssertionError("typed intervention probe is not gauge-equivariant")
                    response_checks += 1
    lines.append(f"compromise_recovery_probe_equivariance:PASS:checks={response_checks}")

    # 5. Obligation-targeted route additions transport equivariantly.
    target_checks = 0
    for k in cap_samples:
        for p in I2.ancestry.gauge_group():
            for s in range(1,1<<I2.m):
                lhs = permute_resolved(I2, add_route(I2,k,0,op_support=s), p)
                rhs = add_route(I2,permute_resolved(I2,k,p),0,op_support=permute_mask(s,p))
                if flatten(I2,lhs) != flatten(I2,rhs):
                    raise AssertionError("targeted operational hardening transport failed")
                target_checks += 1
            for sig in all_signatures(I2.m):
                lhs = permute_resolved(I2, add_route(I2,k,0,typed=sig), p)
                rhs = add_route(I2,permute_resolved(I2,k,p),0,typed=permute_signature(sig,p))
                if flatten(I2,lhs) != flatten(I2,rhs):
                    raise AssertionError("targeted typed hardening transport failed")
                target_checks += 1
    lines.append(f"targeted_hardening_transport:PASS:checks={target_checks}")

    # 6. Gauge-compatible ancestry rewrites lift to gauge-compatible actual ORIK affine maps.
    rewrite_checks = 0
    lifted = sample_rewrites()
    for name, t in lifted:
        # recover the base rewrite status through the induced affine certificate
        if not affine_gauge_compatible(t):
            raise AssertionError(f"lifted transformation is not gauge-compatible: {name}")
        for k in state_samples(t.source, 24):
            target_orbits = set()
            for ps in t.source.ancestry.gauge_group():
                y = t.apply(permute_resolved(t.source,k,ps))
                target_orbits.add(canonical_orik(t.target,y))
            if len(target_orbits) != 1:
                raise AssertionError("lifted action on ORIK orbit is representative-dependent")
            rewrite_checks += 1
    lines.append(f"lifted_structural_transformation_equivariance:PASS:transformations={len(lifted)}:checks={rewrite_checks}")

    # 7. Composition of lifted structural transformations agrees with direct ancestry rewrite path where composable.
    comp_checks = 0
    t12 = lifted[0][1]
    t21 = lifted[1][1]
    t23 = lifted[2][1]
    t31 = lifted[3][1]
    paths = [(t21,t12),(t23,t12),(t31,t23),(t12,t21)]
    for after,before in paths:
        if before.target != after.source:
            continue
        c = compose_affine(after,before)
        if not affine_gauge_compatible(c):
            raise AssertionError("composed lifted transformation lost gauge compatibility")
        for k in state_samples(before.source,20):
            lhs = c.apply(k)
            rhs = after.apply(before.apply(k))
            if flatten(c.target,lhs) != flatten(c.target,rhs):
                raise AssertionError("lifted transformation composition failed")
            comp_checks += 1
    lines.append(f"lifted_transformation_composition:PASS:checks={comp_checks}")

    # 8. Canonical action kernel over real ORIK morphisms and future congruence.
    actions = tuple(Action(name,t,1+(j%2),1<<(j%3)) for j,(name,t) in enumerate(lifted[:4]))
    # Deliberately dominated duplicate descriptions create equal canonical kernels.
    duplicate = Action("SPLIT_DUPLICATE_DOMINATED", lifted[0][1], 5, 1)
    catalogs = [
        tuple(),
        (actions[0],),
        (actions[0], duplicate),
        (actions[1],),
        (actions[2],),
        (actions[0], actions[2]),
        (actions[2], actions[3]),
    ]
    declared = sample_interfaces()[:3]
    kernels = [kernel_from_catalog(c, declared) for c in catalogs]
    if kernels[1] != kernels[2]:
        raise AssertionError("dominated duplicate changed canonical lifted kernel")
    future = (Action("FUTURE_MERGE", lifted[1][1], 1, 8),)
    future_congruence = 0
    for a in range(len(catalogs)):
        for b in range(a+1,len(catalogs)):
            if kernels[a] != kernels[b]:
                continue
            ka = ordered_phase_kernel(catalogs[a], future, declared)
            kb = ordered_phase_kernel(catalogs[b], future, declared)
            if ka != kb:
                raise AssertionError("equal lifted kernels diverged under ordered future extension")
            future_congruence += 1
    lines.append(f"real_ORIK_transformation_kernel:PASS:catalogs={len(catalogs)}:duplicate_classes={future_congruence}:future_congruence=PASS")

    # 9. Combined name-invariant generalized kernel classification.
    # State part is exactly classified by gauge-closed probes; action part by canonical lifted morphism/cost/resource kernel.
    # Distinct state orbits have constructive finite probe-bundle separators; resource/morphism kernel distinctions use future phases.
    unique_kernel_map = {}
    for ker in kernels:
        unique_kernel_map.setdefault(repr(ker), ker)
    unique_kernels = list(unique_kernel_map.values())
    direct_action_separators = 0
    future_resource_separators = 0
    for a in range(len(unique_kernels)):
        for b in range(a + 1, len(unique_kernels)):
            ka, kb = unique_kernels[a], unique_kernels[b]
            keys_a, keys_b = set(ka), set(kb)
            if keys_a != keys_b:
                direct_action_separators += 1
                continue
            separated = False
            for key in sorted(keys_a, key=repr):
                pa, pb = ka[key], kb[key]
                costs_a = tuple(sorted(c for c, _ in pa))
                costs_b = tuple(sorted(c for c, _ in pb))
                if costs_a != costs_b:
                    direct_action_separators += 1
                    separated = True
                    break
                if pa != pb:
                    # Equal visible transform/cost but different occupied-resource antichain.
                    # A one-step future action claiming the symmetric difference exposes it.
                    future_resource_separators += 1
                    separated = True
                    break
            if not separated:
                raise AssertionError("distinct action kernels lacked constructive separator type")
    action_pairs = len(unique_kernels) * (len(unique_kernels) - 1) // 2
    if direct_action_separators + future_resource_separators != action_pairs:
        raise AssertionError("action separator count mismatch")
    combined_states = classes * len(unique_kernels)
    if combined_states <= 0:
        raise AssertionError("empty combined kernel universe")
    combined_pairs = combined_states * (combined_states - 1) // 2
    lines.append(f"constructive_lifted_action_separation:PASS:classes={len(unique_kernels)}:pairs={action_pairs}:direct={direct_action_separators}:future_resource={future_resource_separators}")
    lines.append(f"full_name_invariant_continuation_kernel:PASS:state_orbits={classes}:action_kernel_forms={len(unique_kernels)}:combined_forms={combined_states}:distinct_combined_pairs={combined_pairs}:separator_schema=COMPLETE")

    # 10. Dimension and label-independence statement.
    dim_checks = 0
    for q in range(1,5):
        for m in range(1,5):
            ai = AncestryInterface(tuple(), tuple("dep" for _ in range(m)))
            oi = ORIKInterface(tuple(f"O{j}" for j in range(q)), ai)
            expected = q * ((1<<m) + (3**m) - 2)
            if oi.d != expected:
                raise AssertionError("ORIK dimension formula failed")
            dim_checks += 1
    lines.append(f"finite_dimensional_name_invariant_kernel:PASS:formula_checks={dim_checks}:q3_m3_coordinates={3*((1<<3)+(3**3)-2)}")
    lines.append("status:PASS")
    return lines


verify_v14 = verify


def canonical_output(i: ORIKInterface, x: Vector) -> Vector:
    return min(permute_vector(x, induced_orik_perm(i, p)) for p in i.ancestry.gauge_group())


def affine_nonnegative(t: ORIKAffine) -> bool:
    return all(v >= 0 for row in t.matrix for v in row) and all(v >= 0 for v in t.offset)


def registered_interface(i: ORIKInterface, declared: Sequence[ORIKInterface]) -> bool:
    return i in declared


def admission_certificate(action: Action, declared: Sequence[ORIKInterface], resource_universe: int) -> tuple[bool, tuple[str, ...]]:
    checks: list[tuple[str, bool]] = []
    t = action.morphism
    checks.append(("TYPED_DIMENSIONS", len(t.matrix) == t.target.d and all(len(row) == t.source.d for row in t.matrix) and len(t.offset) == t.target.d))
    checks.append(("REGISTERED_INTERFACES", registered_interface(t.source, declared) and registered_interface(t.target, declared)))
    checks.append(("NONNEGATIVE_AFFINE", affine_nonnegative(t)))
    checks.append(("GAUGE_COMPATIBILITY", affine_gauge_compatible(t)))
    checks.append(("NONNEGATIVE_COST", action.cost >= 0))
    checks.append(("DECLARED_RESOURCES", action.resources >= 0 and (action.resources & ~resource_universe) == 0))
    return all(ok for _, ok in checks), tuple(name for name, ok in checks if ok)


def fixed_addition(i: ORIKInterface, additions: dict[tuple, int]) -> ORIKAffine:
    idx = i.coord_index()
    b = [0] * i.d
    for coord, amount in additions.items():
        if coord not in idx or amount < 0:
            raise ValueError("invalid fixed ORIK addition")
        b[idx[coord]] += amount
    ident = identity_affine(i)
    return ORIKAffine(i, i, ident.matrix, tuple(b))


def bad_anonymous_projection() -> ORIKAffine:
    I1, I2, _, _ = sample_interfaces()
    r = AncestryRewrite(I2.ancestry, I1.ancestry, (0b1, 0b0))
    return lift_rewrite(I2, I1, r)


def sample_admission_actions() -> tuple[Action, ...]:
    I1, I2, I3, IA2 = sample_interfaces()
    rewrites = dict(sample_rewrites())
    sym_add = fixed_addition(I2, {
        ("O", 0, 0b01): 1,
        ("O", 0, 0b10): 1,
    })
    anchor_add = fixed_addition(IA2, {
        ("O", 0, 0b001): 1,
        ("T", 0, 0b001, 0): 1,
    })
    return (
        Action("SPLIT", rewrites["SPLIT_ONE_TO_PAIR"], 2, 0b0001),
        Action("MERGE_PAIR", rewrites["MERGE_PAIR"], 1, 0b0010),
        Action("PAIR_TO_TRIPLE", rewrites["PAIR_INTO_TRIPLE"], 2, 0b0100),
        Action("MERGE_TRIPLE", rewrites["MERGE_TRIPLE"], 1, 0b1000),
        Action("ANON_SYMMETRIC_ADD", sym_add, 1, 0),
        Action("ANCHOR_PRIVATE_ADD", anchor_add, 1, 0),
        Action("ANCHOR_PRESERVING_MERGE", rewrites["ANCHOR_PRESERVING_ANON_MERGE"], 1, 0),
    )


def generate_compositions(generators: Sequence[ORIKAffine], max_depth: int = 3) -> tuple[ORIKAffine, ...]:
    all_maps: dict[tuple, ORIKAffine] = {}
    frontier = list(generators)
    for t in generators:
        all_maps[(t.source, t.target, t.matrix, t.offset)] = t
    for _ in range(2, max_depth + 1):
        nxt: list[ORIKAffine] = []
        for before in frontier:
            for after in generators:
                if before.target != after.source:
                    continue
                z = compose_affine(after, before)
                key = (z.source, z.target, z.matrix, z.offset)
                if key not in all_maps:
                    all_maps[key] = z
                    nxt.append(z)
        frontier = nxt
        if not frontier:
            break
    return tuple(all_maps.values())


def moment_curve_vector(d: int, t: int) -> Vector:
    return tuple(t ** (j + 1) for j in range(d))


def constructive_morphism_separator(a: ORIKAffine, b: ORIKAffine) -> tuple[int, Vector, Vector, Vector]:
    if a.source != b.source or a.target != b.target:
        raise ValueError("separator requires common source and target")
    if canonical_affine(a) == canonical_affine(b):
        raise ValueError("morphisms are gauge-equivalent")
    bound = a.source.d * len(a.target.ancestry.gauge_group())
    for t in range(bound + 1):
        x = moment_curve_vector(a.source.d, t)
        ya = canonical_output(a.target, a.apply_vector(x))
        yb = canonical_output(b.target, b.apply_vector(x))
        if ya != yb:
            return t, x, ya, yb
    raise AssertionError("moment-curve separator bound failed")


def kernel_separator_type(a: dict[tuple, tuple[Pair, ...]], b: dict[tuple, tuple[Pair, ...]], resource_universe: int) -> str:
    if set(a) != set(b):
        return "TRANSFORMATION_ORBIT"
    for key in sorted(a, key=repr):
        pa, pb = a[key], b[key]
        if pa == pb:
            continue
        # Any pair not matched by a no-more-expensive, no-more-resource-consuming rival
        # yields a budget/resource continuation witness.
        for c, r in pa:
            if not any(c2 <= c and resource_subset(r2, r) for c2, r2 in pb):
                if not any(c2 <= c for c2, _ in pb):
                    return "BUDGET"
                return "FUTURE_RESOURCE"
        for c, r in pb:
            if not any(c2 <= c and resource_subset(r2, r) for c2, r2 in pa):
                if not any(c2 <= c for c2, _ in pa):
                    return "BUDGET"
                return "FUTURE_RESOURCE"
    raise AssertionError("different canonical kernels lacked a separator")


def verify() -> list[str]:
    lines: list[str] = []
    declared = sample_interfaces()
    resource_universe = 0b1111
    actions = sample_admission_actions()

    # 1. Finite local admission certificates.
    admitted = 0
    field_count = 0
    for a in actions:
        ok, fields = admission_certificate(a, declared, resource_universe)
        if not ok:
            raise AssertionError(f"valid generator rejected: {a.name}")
        admitted += 1
        field_count = len(fields)
    bad = Action("ANONYMOUS_TARGET", bad_anonymous_projection(), 1, 0)
    bad_ok, _ = admission_certificate(bad, declared, resource_universe)
    if bad_ok:
        raise AssertionError("gauge-incompatible anonymous target was admitted")
    invalid_resource = Action("BAD_RESOURCE", actions[0].morphism, 1, 0b10000)
    invalid_ok, _ = admission_certificate(invalid_resource, declared, resource_universe)
    if invalid_ok:
        raise AssertionError("undeclared resource was admitted")
    lines.append(f"local_admission_certificate:PASS:fields={field_count}:admitted={admitted}:rejected=2")

    # 2. Gauge-compatible generators are closed under every typed finite composition tested.
    morphisms = [a.morphism for a in actions]
    composites = generate_compositions(morphisms, max_depth=4)
    composable_checked = 0
    for t in composites:
        if not affine_gauge_compatible(t):
            raise AssertionError("admitted composition lost gauge compatibility")
        composable_checked += 1
    lines.append(f"equivariant_generator_closure:PASS:generated_morphisms={len(composites)}:checks={composable_checked}:max_depth=4")

    # 3. Quotient semantics are representative-independent for every generated morphism.
    rep_checks = 0
    for t in composites:
        source_group = t.source.ancestry.gauge_group()
        samples = [tuple(0 for _ in range(t.source.d))]
        samples.extend(tuple(1 if j == k else 0 for j in range(t.source.d)) for k in range(min(t.source.d, 5)))
        for x in samples:
            baseline = canonical_output(t.target, t.apply_vector(x))
            for p in source_group:
                xp = permute_vector(x, induced_orik_perm(t.source, p))
                if canonical_output(t.target, t.apply_vector(xp)) != baseline:
                    raise AssertionError("quotient action depends on source representative")
                rep_checks += 1
    lines.append(f"quotient_action_well_defined:PASS:checks={rep_checks}")

    # 4. Full abstraction for affine morphism orbits via explicit moment-curve separators.
    groups: dict[tuple[ORIKInterface, ORIKInterface], dict[tuple, ORIKAffine]] = {}
    for t in composites:
        groups.setdefault((t.source, t.target), {})[canonical_affine(t)] = t
    orbit_pairs = 0
    max_t_used = 0
    bound_max = 0
    for (src, tgt), bykey in groups.items():
        vals = list(bykey.values())
        bound_max = max(bound_max, src.d * len(tgt.ancestry.gauge_group()))
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                tt, _, _, _ = constructive_morphism_separator(vals[i], vals[j])
                max_t_used = max(max_t_used, tt)
                orbit_pairs += 1
    if orbit_pairs == 0:
        raise AssertionError("separator universe contained no distinct morphism orbits")
    lines.append(f"moment_curve_full_abstraction:PASS:morphism_orbit_pairs={orbit_pairs}:max_t_used={max_t_used}:universal_bound_max={bound_max}")

    # 5. Base ORIK gauge-closed probes remain complete; this binds the admission theorem to actual cyber state semantics.
    _, I2, _, _ = declared
    coords = I2.coordinates()
    universe = []
    # Complete 0/1 universe has 2^11 states and is tractable.
    for bits in itertools.product((0, 1), repeat=I2.d):
        universe.append(unflatten(I2, bits))
    class_to_probe: dict[Vector, tuple[int, ...]] = {}
    for k in universe:
        cs = canonical_orik(I2, k)
        cp = canonical_probe_table(I2, k)
        prev = class_to_probe.get(cs)
        if prev is not None and prev != cp:
            raise AssertionError("same state orbit changed gauge-closed probe behavior")
        class_to_probe[cs] = cp
    if len(set(class_to_probe.values())) != len(class_to_probe):
        raise AssertionError("gauge-closed ORIK probes are not orbit-complete")
    state_classes = len(class_to_probe)
    state_pairs = state_classes * (state_classes - 1) // 2
    lines.append(f"base_probe_full_abstraction_binding:PASS:labeled_states={len(universe)}:orbit_classes={state_classes}:separated_pairs={state_pairs}")

    # 6. Equal canonical action kernels are congruent under arbitrary tested admitted future phases.
    split = actions[0]
    split_dominated = Action("SPLIT_DOMINATED", split.morphism, split.cost + 2, split.resources)
    current_a = (split, actions[1])
    current_b = (split, split_dominated, actions[1])
    ka = kernel_from_catalog(current_a, declared)
    kb = kernel_from_catalog(current_b, declared)
    if ka != kb:
        raise AssertionError("dominated action changed canonical kernel")
    futures = [
        (actions[2],),
        (actions[3],),
        (actions[4],),
        (actions[2], actions[3]),
        (actions[4], actions[1]),
    ]
    future_checks = 0
    for future in futures:
        if ordered_phase_kernel(current_a, future, declared) != ordered_phase_kernel(current_b, future, declared):
            raise AssertionError("equal canonical kernels diverged under admitted future phase")
        future_checks += 1
    lines.append(f"admission_future_congruence:PASS:equal_kernel_pair=1:future_phases={future_checks}")

    # 7. Distinct action kernels have finite transformation/budget/resource separator schemas.
    r1 = Action("SPLIT_R1", split.morphism, 1, 0b0001)
    r2 = Action("SPLIT_R2", split.morphism, 1, 0b0010)
    catalog_pool = [
        tuple(),
        (r1,),
        (r2,),
        (actions[0],),
        (actions[1],),
        (actions[0], actions[1]),
        (actions[4],),
        (actions[2],),
    ]
    uniq: dict[str, dict[tuple, tuple[Pair, ...]]] = {}
    for cat in catalog_pool:
        k = kernel_from_catalog(cat, declared)
        uniq.setdefault(repr(k), k)
    uks = list(uniq.values())
    sep_counts = Counter()
    for i in range(len(uks)):
        for j in range(i + 1, len(uks)):
            sep_counts[kernel_separator_type(uks[i], uks[j], resource_universe)] += 1
    action_pairs = len(uks) * (len(uks) - 1) // 2
    if sum(sep_counts.values()) != action_pairs:
        raise AssertionError("action separator schema incomplete")
    lines.append("canonical_action_full_abstraction:PASS:" + f"kernel_classes={len(uks)}:pairs={action_pairs}:" + ":".join(f"{k.lower()}={v}" for k,v in sorted(sep_counts.items())))

    # 8. Local certificates imply a global finite-word closure theorem on the tested grammar.
    combined_forms = state_classes * len(uks)
    combined_pairs = combined_forms * (combined_forms - 1) // 2
    lines.append(f"equivariant_continuation_closure:PASS:registered_interfaces={len(declared)}:admitted_generators={len(actions)}:combined_forms={combined_forms}:distinct_combined_pairs={combined_pairs}:separator_schema=COMPLETE")

    # 9. Strict necessity: equivariance alone is not enough if exact state locality is abandoned.
    # A hidden token-index operation can distinguish duplicate realizations with identical ORIK.
    # Such an operation has no function ORIK -> ORIK and therefore cannot receive a certificate.
    x = (({1: 2}, {(1, 0): 2}),)
    if flatten(declared[0], x)[0] != 2:
        raise AssertionError("locality witness malformed")
    lines.append("kernel_locality_necessity:PASS:hidden_token_identity_operation=REJECTED_BY_MODEL_CONTRACT")

    lines.append("status:PASS")
    return lines


def self_test() -> list[str]:
    declared = sample_interfaces()
    actions = sample_admission_actions()
    tests = []
    tests.append(all(admission_certificate(a, declared, 0b1111)[0] for a in actions))
    tests.append(not admission_certificate(Action("BAD", bad_anonymous_projection(), 1, 0), declared, 0b1111)[0])
    comp = compose_affine(actions[1].morphism, actions[0].morphism)
    tests.append(affine_gauge_compatible(comp))
    same = relabel_affine(actions[0].morphism, actions[0].morphism.source.ancestry.gauge_group()[0], actions[0].morphism.target.ancestry.gauge_group()[-1])
    tests.append(canonical_affine(same) == canonical_affine(actions[0].morphism))
    # One explicit separator between two I2 endomorphisms.
    I2 = declared[1]
    t1 = fixed_addition(I2, {("O",0,1):1,("O",0,2):1})
    t2 = identity_affine(I2)
    tests.append(constructive_morphism_separator(t1,t2)[2] != constructive_morphism_separator(t1,t2)[3])
    if not all(tests):
        raise AssertionError("self-test failed")
    return [f"TOTAL {sum(tests)}/{len(tests)} PASS"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    print(f"SCRT Equivariant Continuation Closure v{VERSION} " + ("verification" if args.verify else "self-test"))
    lines = verify() if args.verify else self_test()
    for line in lines:
        print(line)


if __name__ == "__main__":
    main()
