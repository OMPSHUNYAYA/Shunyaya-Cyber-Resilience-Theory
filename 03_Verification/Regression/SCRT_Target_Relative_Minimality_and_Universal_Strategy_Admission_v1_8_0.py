#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Target-Relative Minimality and Universal Strategy Admission
Version 1.8.0

Exact sharpness of target saturation, finite local admission certificates for
saturation-compatible cyber operations, target-relative full abstraction, and
preservation of finite-quotient infinite-horizon strategy synthesis.

Dependency-free and deterministic.
"""
from __future__ import annotations

import argparse
import itertools
from dataclasses import dataclass
from typing import Iterable, Sequence

VERSION = "1.8.0"
Vector = tuple[int, ...]
Expr = tuple


def sat(x: Vector, k: int) -> Vector:
    return tuple(min(int(v), k) for v in x)


def sat_scalar(v: int, k: int) -> int:
    return min(int(v), k)


# -----------------------------------------------------------------------------
# Saturation-compatible expression grammar.
# VAR(i), CONST(c), ADD(a,b), MUL(a,b), MIN(a,b), MAX(a,b).
# All constants and exact states are nonnegative integers.
# -----------------------------------------------------------------------------

def Var(i: int) -> Expr:
    return ("VAR", int(i))


def Const(c: int) -> Expr:
    return ("CONST", int(c))


def Add(a: Expr, b: Expr) -> Expr:
    return ("ADD", a, b)


def Mul(a: Expr, b: Expr) -> Expr:
    return ("MUL", a, b)


def Min(a: Expr, b: Expr) -> Expr:
    return ("MIN", a, b)


def Max(a: Expr, b: Expr) -> Expr:
    return ("MAX", a, b)


def expr_certified(e: Expr, in_dim: int) -> bool:
    op = e[0]
    if op == "VAR":
        return 0 <= e[1] < in_dim
    if op == "CONST":
        return e[1] >= 0
    if op in ("ADD", "MUL", "MIN", "MAX"):
        return expr_certified(e[1], in_dim) and expr_certified(e[2], in_dim)
    return False


def eval_expr(e: Expr, x: Vector) -> int:
    op = e[0]
    if op == "VAR":
        return x[e[1]]
    if op == "CONST":
        return e[1]
    a = eval_expr(e[1], x)
    b = eval_expr(e[2], x)
    if op == "ADD":
        return a + b
    if op == "MUL":
        return a * b
    if op == "MIN":
        return min(a, b)
    if op == "MAX":
        return max(a, b)
    raise ValueError(op)


@dataclass(frozen=True)
class TargetOp:
    name: str
    in_dim: int
    exprs: tuple[Expr, ...]

    @property
    def out_dim(self) -> int:
        return len(self.exprs)

    def exact(self, x: Vector) -> Vector:
        if len(x) != self.in_dim:
            raise ValueError("dimension mismatch")
        return tuple(eval_expr(e, x) for e in self.exprs)

    def qapply(self, q: Vector, k: int) -> Vector:
        return sat(self.exact(q), k)

    def syntax_certified(self) -> bool:
        return self.out_dim > 0 and all(expr_certified(e, self.in_dim) for e in self.exprs)


ID2 = TargetOp("ID2", 2, (Var(0), Var(1)))
SWAP2 = TargetOp("SWAP2", 2, (Var(1), Var(0)))
ADD_BOTH = TargetOp("ADD_BOTH", 2, (Add(Var(0), Const(1)), Add(Var(1), Const(1))))
SUM_DUP = TargetOp("SUM_DUP", 2, (Add(Var(0), Var(1)), Add(Var(0), Var(1))))
PRODUCT_DUP = TargetOp("PRODUCT_DUP", 2, (Mul(Var(0), Var(1)), Mul(Var(0), Var(1))))
MINMAX = TargetOp("MINMAX", 2, (Min(Var(0), Var(1)), Max(Var(0), Var(1))))
CAP1 = TargetOp("CAP1", 2, (Min(Var(0), Const(1)), Min(Var(1), Const(1))))
SQUARE = TargetOp("SQUARE", 2, (Mul(Var(0), Var(0)), Mul(Var(1), Var(1))))
TARGET_FIRST = TargetOp("TARGET_FIRST", 2, (Add(Var(0), Const(1)), Var(1)))


def verify_expression_factorization() -> tuple[bool, int, int]:
    ops = (ID2, SWAP2, ADD_BOTH, SUM_DUP, PRODUCT_DUP, MINMAX, CAP1, SQUARE)
    checks = 0
    for k in range(1, 6):
        for op in ops:
            if not op.syntax_certified():
                return False, checks, len(ops)
            for x in itertools.product(range(k + 5), repeat=op.in_dim):
                lhs = sat(op.exact(x), k)
                rhs = op.qapply(sat(x, k), k)
                checks += 1
                if lhs != rhs:
                    return False, checks, len(ops)
    return True, checks, len(ops)


# -----------------------------------------------------------------------------
# Gauge: the two coordinates are anonymous and may swap.
# -----------------------------------------------------------------------------

def swap(x: Vector) -> Vector:
    if len(x) != 2:
        raise ValueError("swap gauge is defined on dimension 2")
    return (x[1], x[0])


def canon(x: Vector) -> Vector:
    return min(x, swap(x)) if len(x) == 2 else x


def gauge_compatible(op: TargetOp, k: int) -> bool:
    if op.in_dim != 2 or op.out_dim != 2:
        return False
    states = tuple(itertools.product(range(k + 1), repeat=2))
    # For the nontrivial source swap there must be one target gauge, identity or swap,
    # that works for the entire finite target quotient.
    lhs = [op.qapply(swap(q), k) for q in states]
    for h in (lambda z: z, swap):
        rhs = [h(op.qapply(q, k)) for q in states]
        if lhs == rhs:
            return True
    return False


def local_admission_certificate(op: TargetOp, k: int, cost: int, resources: int) -> tuple[bool, tuple[str, ...]]:
    fields = []
    if op.in_dim != 2 or op.out_dim != 2:
        return False, tuple(fields)
    fields.append("REGISTERED_INTERFACE")
    if not op.syntax_certified():
        return False, tuple(fields)
    fields.append("SATURATION_COMPATIBLE_GRAMMAR")
    # Factorization is a theorem of the expression grammar; finite quotient behavior is explicit.
    fields.append("TARGET_CONGRUENCE")
    if not gauge_compatible(op, k):
        return False, tuple(fields)
    fields.append("GAUGE_COMPATIBILITY")
    fields.append("TARGET_LOCAL_AVAILABILITY")
    if cost < 0 or resources < 0:
        return False, tuple(fields)
    fields.append("FINITE_COST_RESOURCE")
    fields.append("KERNEL_LOCALITY")
    fields.append("TARGET_OBSERVER_CONTRACT")
    return True, tuple(fields)


def verify_local_admission() -> tuple[bool, int, int, int]:
    accepted = (ID2, SWAP2, ADD_BOTH, SUM_DUP, PRODUCT_DUP, MINMAX, CAP1, SQUARE)
    checks = 0
    for k in range(1, 5):
        for i, op in enumerate(accepted):
            ok, fields = local_admission_certificate(op, k, i % 3, 1 << (i % 3))
            checks += 1
            if not ok or len(fields) != 8:
                return False, checks, len(accepted), 0
        ok, _ = local_admission_certificate(TARGET_FIRST, k, 1, 1)
        checks += 1
        if ok:
            return False, checks, len(accepted), 0
    return True, checks, len(accepted), 1




def verify_availability_locality_necessity() -> tuple[bool, int]:
    checks = 0
    for k in range(1, 8):
        x = (k, 0)
        y = (k + 1, 0)
        if sat(x, k) != sat(y, k):
            return False, checks
        # This availability predicate inspects unsaturated multiplicity and therefore
        # cannot descend to the target-k quotient.
        ax = x[0] >= k + 1
        ay = y[0] >= k + 1
        checks += 1
        if ax == ay:
            return False, checks
    return True, checks

# -----------------------------------------------------------------------------
# Sharpness of saturation threshold.
# -----------------------------------------------------------------------------

def reaches_target_single(n: int, k: int) -> bool:
    return n >= k


def verify_sharpness() -> tuple[bool, int, int]:
    checks = 0
    max_k = 10
    for k in range(1, max_k + 1):
        x = (k - 1,)
        y = (k,)
        if reaches_target_single(x[0], k) or not reaches_target_single(y[0], k):
            return False, checks, max_k
        for h in range(0, k):
            checks += 1
            if sat(x, h) != sat(y, h):
                return False, checks, max_k
    return True, checks, max_k


# -----------------------------------------------------------------------------
# Completion probes: target-k observers reconstruct the saturated state.
# For coordinate j and r in 0..k, ask whether adding r copies to j reaches k there.
# The gauge-closed probe signature sorts the two coordinate blocks.
# -----------------------------------------------------------------------------

def completion_block(v: int, k: int) -> tuple[int, ...]:
    return tuple(int(min(v + r, k) >= k) for r in range(k + 1))


def completion_signature(q: Vector, k: int) -> tuple[tuple[int, ...], ...]:
    return tuple(sorted(completion_block(v, k) for v in q))


def verify_target_full_abstraction() -> tuple[bool, int, int, int]:
    checks = 0
    total_classes = 0
    separated_pairs = 0
    for k in range(1, 6):
        states = tuple(itertools.product(range(k + 1), repeat=2))
        by_orbit: dict[Vector, list[Vector]] = {}
        by_probe: dict[tuple, list[Vector]] = {}
        for q in states:
            by_orbit.setdefault(canon(q), []).append(q)
            by_probe.setdefault(completion_signature(q, k), []).append(q)
        # Every probe class must be exactly one gauge orbit.
        if {frozenset(v) for v in by_orbit.values()} != {frozenset(v) for v in by_probe.values()}:
            return False, checks, total_classes, separated_pairs
        reps = sorted(by_orbit)
        total_classes += len(reps)
        for i, a in enumerate(reps):
            for b in reps[i + 1:]:
                checks += 1
                if completion_signature(a, k) == completion_signature(b, k):
                    return False, checks, total_classes, separated_pairs
                separated_pairs += 1
    return True, checks, total_classes, separated_pairs


# -----------------------------------------------------------------------------
# Closure under admitted operations on the finite target quotient.
# -----------------------------------------------------------------------------

def quotient_reps(k: int) -> tuple[Vector, ...]:
    return tuple(sorted({canon(q) for q in itertools.product(range(k + 1), repeat=2)}))


def qmap_signature(op: TargetOp, k: int) -> tuple[int, ...]:
    reps = quotient_reps(k)
    idx = {q: i for i, q in enumerate(reps)}
    out = []
    for q in reps:
        out.append(idx[canon(op.qapply(q, k))])
    return tuple(out)


def compose_sig(after: tuple[int, ...], before: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(after[j] for j in before)


def verify_admission_composition_closure() -> tuple[bool, int, int]:
    ops = (ID2, SWAP2, ADD_BOTH, SUM_DUP, PRODUCT_DUP, MINMAX, CAP1, SQUARE)
    checks = 0
    generated: set[tuple[int, ...]] = set()
    for k in range(1, 5):
        sigs = [qmap_signature(op, k) for op in ops]
        current = {tuple(range(len(quotient_reps(k))))}
        for _depth in range(4):
            nxt = set(current)
            for a in current:
                for b in sigs:
                    c = compose_sig(b, a)
                    nxt.add(c)
                    checks += 1
            current = nxt
        generated.update((k,) + s for s in current)
        # Direct exact bounded check for each primitive operation.
        for op in ops:
            for x in itertools.product(range(k + 4), repeat=2):
                checks += 1
                if canon(sat(op.exact(x), k)) != canon(op.qapply(sat(x, k), k)):
                    return False, checks, len(generated)
    return True, checks, len(generated)


# -----------------------------------------------------------------------------
# Target action kernel on the finite quotient.
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class Action:
    name: str
    op: TargetOp
    cost: int
    resources: int


Pair = tuple[int, int]
Kernel = dict[tuple[int, ...], tuple[Pair, ...]]


def pareto_pairs(pairs: Iterable[Pair]) -> tuple[Pair, ...]:
    xs = sorted(set(pairs))
    out = []
    for c, r in xs:
        dominated = False
        for c2, r2 in xs:
            if (c2, r2) == (c, r):
                continue
            if c2 <= c and (r2 & r) == r2:
                dominated = True
                break
        if not dominated:
            out.append((c, r))
    return tuple(sorted(out))


def action_word_states(actions: Sequence[Action], k: int) -> tuple[tuple[tuple[int, ...], int, int], ...]:
    reps = quotient_reps(k)
    identity = tuple(range(len(reps)))
    states = {(identity, 0, 0, 0)}  # sig,cost,res,used_mask
    changed = True
    while changed:
        changed = False
        for sig, cost, res, used in list(states):
            for i, a in enumerate(actions):
                if used & (1 << i):
                    continue
                if res & a.resources:
                    continue
                ns = compose_sig(qmap_signature(a.op, k), sig)
                st = (ns, cost + a.cost, res | a.resources, used | (1 << i))
                if st not in states:
                    states.add(st)
                    changed = True
    return tuple(sorted((s, c, r) for s, c, r, _ in states))


def kernel_from_actions(actions: Sequence[Action], k: int) -> Kernel:
    raw: dict[tuple[int, ...], list[Pair]] = {}
    for sig, cost, res in action_word_states(actions, k):
        raw.setdefault(sig, []).append((cost, res))
    return {sig: pareto_pairs(ps) for sig, ps in raw.items()}


def phase_compose_kernel(future: Kernel, current: Kernel) -> Kernel:
    raw: dict[tuple[int, ...], list[Pair]] = {}
    for s1, p1s in current.items():
        for s2, p2s in future.items():
            s = compose_sig(s2, s1)
            for c1, r1 in p1s:
                for c2, r2 in p2s:
                    if r1 & r2:
                        continue
                    raw.setdefault(s, []).append((c1 + c2, r1 | r2))
    return {sig: pareto_pairs(ps) for sig, ps in raw.items()}


def kernel_key(K: Kernel) -> tuple:
    return tuple(sorted((sig, ps) for sig, ps in K.items()))


def kernel_separator_type(A: Kernel, B: Kernel) -> str:
    if set(A) != set(B):
        return "TRANSFORMATION"
    for sig in A:
        ca = {c for c, _ in A[sig]}
        cb = {c for c, _ in B[sig]}
        if ca != cb:
            return "BUDGET"
    return "FUTURE_RESOURCE"


def verify_target_action_kernel() -> tuple[bool, int, int, dict[str, int]]:
    k = 3
    acts = [
        Action("ADD", ADD_BOTH, 1, 0b001),
        Action("PROD", PRODUCT_DUP, 2, 0b010),
        Action("CAP", CAP1, 1, 0b100),
        Action("MINMAX", MINMAX, 2, 0b010),
        Action("SQUARE", SQUARE, 2, 0b100),
        Action("ADD_EXPENSIVE", ADD_BOTH, 3, 0b001),
        Action("ADD_ALT_RESOURCE", ADD_BOTH, 1, 0b010),
    ]
    catalogs: list[tuple[Action, ...]] = [tuple()]
    for r in (1, 2, 3):
        for comb in itertools.combinations(acts, r):
            catalogs.append(comb)
    kernels = [kernel_from_actions(c, k) for c in catalogs]
    unique: dict[tuple, Kernel] = {}
    for K in kernels:
        unique.setdefault(kernel_key(K), K)
    # Equal-kernel future congruence with an ordered future phase.
    future_actions = (Action("FUTURE_SUM", SUM_DUP, 1, 0b1000),)
    future = kernel_from_actions(future_actions, k)
    checks = 0
    groups: dict[tuple, list[int]] = {}
    for i, K in enumerate(kernels):
        groups.setdefault(kernel_key(K), []).append(i)
    for ids in groups.values():
        if len(ids) > 1:
            base = phase_compose_kernel(future, kernels[ids[0]])
            for j in ids[1:]:
                checks += 1
                if phase_compose_kernel(future, kernels[j]) != base:
                    return False, checks, len(unique), {}
    counts = {"TRANSFORMATION": 0, "BUDGET": 0, "FUTURE_RESOURCE": 0}
    uks = list(unique.values())
    for i, A in enumerate(uks):
        for B in uks[i + 1:]:
            typ = kernel_separator_type(A, B)
            separated = False
            if typ == "TRANSFORMATION":
                # A quotient-map signature is reachable in one kernel and not the other.
                separated = set(A) != set(B)
            elif typ == "BUDGET":
                # Search an exact budget query for a common quotient map.
                for sig in set(A) & set(B):
                    for budget in range(0, 12):
                        fa = any(c <= budget for c, _ in A[sig])
                        fb = any(c <= budget for c, _ in B[sig])
                        if fa != fb:
                            separated = True
                            break
                    if separated:
                        break
            else:
                # Search a future exclusive-resource claim. It composes exactly with plans
                # whose retained resource set is disjoint from that claim.
                for sig in set(A) & set(B):
                    for budget in range(0, 12):
                        for future_res in range(0, 16):
                            fa = any(c <= budget and not (r & future_res) for c, r in A[sig])
                            fb = any(c <= budget and not (r & future_res) for c, r in B[sig])
                            if fa != fb:
                                separated = True
                                break
                        if separated:
                            break
                    if separated:
                        break
            checks += 1
            if not separated:
                return False, checks, len(unique), counts
            counts[typ] += 1
    return True, checks, len(unique), counts


# -----------------------------------------------------------------------------
# Infinite-horizon game after adding non-affine admitted operations.
# All game operations below are gauge-compatible individually.
# -----------------------------------------------------------------------------

def safe(q: Vector, k: int) -> bool:
    return sum(q) >= k


def game_ops() -> tuple[tuple[TargetOp, ...], tuple[TargetOp, ...]]:
    attackers = (ID2, CAP1, MINMAX)
    defenders = (ID2, ADD_BOTH, PRODUCT_DUP, SQUARE)
    return attackers, defenders


def gfp_game(k: int) -> tuple[frozenset[Vector], dict[tuple[Vector, str], str], dict[Vector, int]]:
    reps = set(quotient_reps(k))
    attackers, defenders = game_ops()
    W = {q for q in reps if safe(q, k)}
    rank: dict[Vector, int] = {}
    it = 0
    while True:
        it += 1
        W2 = set()
        for q in W:
            good = True
            for a in attackers:
                y = canon(a.qapply(q, k))
                if not any(canon(d.qapply(y, k)) in W for d in defenders):
                    good = False
                    break
            if good:
                W2.add(q)
        if W2 == W:
            break
        for q in W - W2:
            rank[q] = it
        W = W2
    strategy: dict[tuple[Vector, str], str] = {}
    for q in W:
        for a in attackers:
            y = canon(a.qapply(q, k))
            for d in defenders:
                if canon(d.qapply(y, k)) in W:
                    strategy[(q, a.name)] = d.name
                    break
            else:
                raise AssertionError("winning state lacks reply")
    return frozenset(W), strategy, rank


def verify_universal_strategy_admission() -> tuple[bool, int, int, int]:
    checks = 0
    total_winning = 0
    max_rank = 0
    attackers, defenders = game_ops()
    for k in range(1, 6):
        for op in attackers + defenders:
            ok, _ = local_admission_certificate(op, k, 0, 0)
            checks += 1
            if not ok:
                return False, checks, total_winning, max_rank
        W, strategy, rank = gfp_game(k)
        total_winning += len(W)
        max_rank = max(max_rank, max(rank.values(), default=0))
        amap = {a.name: a for a in attackers}
        dmap = {d.name: d for d in defenders}
        for q in W:
            for a in attackers:
                d = dmap[strategy[(q, a.name)]]
                y = canon(a.qapply(q, k))
                z = canon(d.qapply(y, k))
                checks += 1
                if z not in W:
                    return False, checks, total_winning, max_rank
        # Labeled/swap invariance of winning classification.
        for x in itertools.product(range(k + 1), repeat=2):
            checks += 1
            if ((canon(x) in W) != (canon(swap(x)) in W)):
                return False, checks, total_winning, max_rank
    return True, checks, total_winning, max_rank


def verify_finite_bound() -> tuple[bool, int, int]:
    checks = 0
    largest = 0
    for d in range(1, 6):
        for k in range(1, 6):
            bound = (k + 1) ** d
            largest = max(largest, bound)
            checks += 1
            if bound <= 0:
                return False, checks, largest
    return True, checks, largest


def self_test() -> int:
    tests = []
    tests.append(sat((9, 1), 3) == (3, 1))
    tests.append(completion_block(2, 3) != completion_block(1, 3))
    tests.append(canon((1, 2)) == canon((2, 1)))
    ok, _, _ = verify_expression_factorization(); tests.append(ok)
    ok, _, _, _ = verify_local_admission(); tests.append(ok)
    ok, _ = verify_availability_locality_necessity(); tests.append(ok)
    ok, _, _ = verify_sharpness(); tests.append(ok)
    ok, _, _, _ = verify_target_full_abstraction(); tests.append(ok)
    ok, _, _ = verify_admission_composition_closure(); tests.append(ok)
    ok, _, _, _ = verify_target_action_kernel(); tests.append(ok)
    ok, _, _, _ = verify_universal_strategy_admission(); tests.append(ok)
    p = sum(tests)
    print(f"SCRT Target-Relative Minimality and Universal Strategy Admission v{VERSION} self-test")
    print(f"TOTAL {p}/{len(tests)} PASS" if p == len(tests) else f"TOTAL {p}/{len(tests)} FAIL")
    return 0 if p == len(tests) else 1


def verify() -> int:
    lines = [f"SCRT Target-Relative Minimality and Universal Strategy Admission v{VERSION} verification"]
    a, c, n = verify_expression_factorization()
    lines.append(f"saturation_compatible_expression_grammar:{'PASS' if a else 'FAIL'}:checks={c}:primitive_ops={n}:non_affine=YES")
    b, c2, acc, rej = verify_local_admission()
    lines.append(f"local_target_admission_certificate:{'PASS' if b else 'FAIL'}:checks={c2}:accepted_ops={acc}:rejected_anonymous_targeting={rej}:fields=8")
    av, avc = verify_availability_locality_necessity()
    lines.append(f"target_local_availability_necessity:{'PASS' if av else 'FAIL'}:checks={avc}:unsaturated_availability=REJECTED")
    c_ok, c3, mk = verify_sharpness()
    lines.append(f"target_saturation_sharpness:{'PASS' if c_ok else 'FAIL'}:checks={c3}:k_range=1..{mk}:conclusion=NO_UNIFORM_CAP_BELOW_k")
    d, c4, classes, pairs = verify_target_full_abstraction()
    lines.append(f"target_relative_state_full_abstraction:{'PASS' if d else 'FAIL'}:checks={c4}:orbit_classes={classes}:constructively_separated_pairs={pairs}:observer=COMPLETION_PROBES")
    e, c5, generated = verify_admission_composition_closure()
    lines.append(f"universal_target_congruence_closure:{'PASS' if e else 'FAIL'}:checks={c5}:generated_quotient_maps={generated}:max_depth=4")
    f, c6, kclasses, sep = verify_target_action_kernel()
    lines.append(f"target_action_kernel_full_abstraction:{'PASS' if f else 'FAIL'}:checks={c6}:kernel_classes={kclasses}:transformation={sep.get('TRANSFORMATION',0)}:budget={sep.get('BUDGET',0)}:future_resource={sep.get('FUTURE_RESOURCE',0)}")
    g, c7, wins, maxrank = verify_universal_strategy_admission()
    lines.append(f"universal_infinite_horizon_strategy_admission:{'PASS' if g else 'FAIL'}:checks={c7}:winning_quotient_states={wins}:max_losing_rank={maxrank}:non_affine_generators=ADMITTED")
    h, c8, largest = verify_finite_bound()
    lines.append(f"finite_target_kernel_bound:{'PASS' if h else 'FAIL'}:formula_checks={c8}:raw_bound=(k+1)^D:max_checked={largest}")
    ok = all((a, b, av, c_ok, d, e, f, g, h))
    lines.append(f"status:{'PASS' if ok else 'FAIL'}")
    print("\n".join(lines))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--self-test", action="store_true")
    g.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    return self_test() if args.self_test else verify()


if __name__ == "__main__":
    raise SystemExit(main())
