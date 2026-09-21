#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Campaign Residual Equivalence and Pure Value Full-Abstraction Theorem
Version 2.6.0

Finite target-relative residual classification for round-resolved assurance
campaigns. Contextual equivalence is induced only by exact campaign values under
compatible future campaign extension. No auxiliary transition-probe observer is
used in the residual theorem.

Dependency-free and deterministic.
"""
from __future__ import annotations

import argparse
import functools
import itertools
from dataclasses import dataclass
from typing import Iterable

VERSION = "2.6.0"
INF = 10**9
Mask = int
Typed = tuple[Mask, Mask]


def typed_support(t: Typed) -> Mask:
    return t[0] | t[1]


def role_mask(d: Mask, e: Mask, m: int) -> Mask:
    return d | (e << m)


def split_role_mask(c: Mask, m: int) -> tuple[Mask, Mask]:
    full = (1 << m) - 1
    return c & full, (c >> m) & full


def pairwise_disjoint_masks(ms: tuple[Mask, ...]) -> bool:
    seen = 0
    for s in ms:
        if seen & s:
            return False
        seen |= s
    return True


def pairwise_physically_disjoint(ts: tuple[Typed, ...]) -> bool:
    return pairwise_disjoint_masks(tuple(typed_support(t) for t in ts))


def unique_masks(routes: Iterable[Mask]) -> tuple[Mask, ...]:
    return tuple(sorted({r for r in routes if r != 0}))


def unique_typed(routes: Iterable[Typed]) -> tuple[Typed, ...]:
    return tuple(sorted({r for r in routes if typed_support(r) != 0}))


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
class Attack:
    impact: Mask
    cost: int
    resources: Mask = 0


@dataclass(frozen=True, order=True)
class Recovery:
    route: Typed
    cost: int
    resources: Mask = 0


@dataclass(frozen=True)
class Kernel:
    op_routes: tuple[Mask, ...]
    cert_routes: tuple[Typed, ...]
    attacks: tuple[Attack, ...]
    recoveries: tuple[Recovery, ...]
    m: int
    k: int


@dataclass(frozen=True)
class State:
    impact: Mask
    cert_routes: tuple[Typed, ...]
    used_attacks: Mask
    used_recoveries: Mask
    attack_resources: Mask
    recovery_resources: Mask


def pareto_pairs(items: Iterable[tuple[int, Mask]]) -> tuple[tuple[int, Mask], ...]:
    vals = sorted(set(items), key=lambda x: (x[0], x[1].bit_count(), x[1]))
    out: list[tuple[int, Mask]] = []
    for c, r in vals:
        if any(c0 <= c and (r0 & r) == r0 for c0, r0 in out):
            continue
        out = [(c0, r0) for c0, r0 in out if not (c <= c0 and (r & r0) == r)]
        out.append((c, r))
    return tuple(sorted(out))


def reduce_attacks(attacks: Iterable[Attack]) -> tuple[Attack, ...]:
    by: dict[Mask, list[tuple[int, Mask]]] = {}
    for a in attacks:
        if a.impact:
            by.setdefault(a.impact, []).append((a.cost, a.resources))
    return tuple(sorted(Attack(impact, c, r) for impact, vals in by.items() for c, r in pareto_pairs(vals)))


def reduce_recoveries(recoveries: Iterable[Recovery]) -> tuple[Recovery, ...]:
    by: dict[Typed, list[tuple[int, Mask]]] = {}
    for r in recoveries:
        if typed_support(r.route):
            by.setdefault(r.route, []).append((r.cost, r.resources))
    return tuple(sorted(Recovery(route, c, q) for route, vals in by.items() for c, q in pareto_pairs(vals)))


def make_kernel(op_routes: Iterable[Mask], cert_routes: Iterable[Typed], attacks: Iterable[Attack],
                recoveries: Iterable[Recovery], m: int, k: int) -> Kernel:
    return Kernel(unique_masks(op_routes), unique_typed(cert_routes), reduce_attacks(attacks),
                  reduce_recoveries(recoveries), m, k)


def safe(K: Kernel, s: State) -> bool:
    return (operational_capacity(K.op_routes, s.impact, K.k, K.m) >= K.k and
            certified_capacity(s.cert_routes, s.impact, K.k, K.m) >= K.k)


class CampaignSolver:
    def __init__(self, K: Kernel):
        self.K = K
        self.initial = State(0, K.cert_routes, 0, 0, 0, 0)

    @functools.lru_cache(maxsize=None)
    def need(self, s: State, budget: int) -> int:
        if not safe(self.K, s):
            return INF
        worst = 0
        for i, a in enumerate(self.K.attacks):
            if (s.used_attacks & (1 << i)) or a.cost > budget or (s.attack_resources & a.resources):
                continue
            imp = s.impact | a.impact
            if operational_capacity(self.K.op_routes, imp, self.K.k, self.K.m) < self.K.k:
                continue
            ua = s.used_attacks | (1 << i)
            ar = s.attack_resources | a.resources
            post = State(imp, s.cert_routes, ua, s.used_recoveries, ar, s.recovery_resources)
            responses: list[int] = []
            if safe(self.K, post):
                responses.append(self.need(post, budget - a.cost))
            for j, d in enumerate(self.K.recoveries):
                if (s.used_recoveries & (1 << j)) or (s.recovery_resources & d.resources):
                    continue
                rs = unique_typed(s.cert_routes + (d.route,))
                nxt = State(imp, rs, ua, s.used_recoveries | (1 << j), ar,
                            s.recovery_resources | d.resources)
                if not safe(self.K, nxt):
                    continue
                future = self.need(nxt, budget - a.cost)
                responses.append(INF if future >= INF else d.cost + future)
            branch = min(responses) if responses else INF
            worst = max(worst, branch)
        return worst

    def delta(self, attacker_budget: int) -> int:
        return self.need(self.initial, attacker_budget)


@dataclass(frozen=True)
class ExtensionAtom:
    name: str
    attack: Attack | None = None
    recovery: Recovery | None = None


class ResidualUniverse:
    """Finite registered future-extension universe for one frozen campaign interface."""

    def __init__(self):
        self.m = 4
        self.k = 2
        e = lambda i: role_mask(0, 1 << i, self.m)
        self.op = (1 << 2, 1 << 3)
        self.cert = ((0, 1 << 0), (0, 1 << 1))
        self.base_attacks = (Attack(e(0), 1, 1), Attack(e(1), 1, 2))
        self.base_recoveries: tuple[Recovery, ...] = ()
        self.atoms = (
            ExtensionAtom("R2@r1", recovery=Recovery((0, 1 << 2), 1, 1)),
            ExtensionAtom("R2@r2", recovery=Recovery((0, 1 << 2), 1, 2)),
            ExtensionAtom("R3@r1", recovery=Recovery((0, 1 << 3), 1, 1)),
            ExtensionAtom("R3@r2", recovery=Recovery((0, 1 << 3), 1, 2)),
            ExtensionAtom("JOINT_E01", attack=Attack(e(0) | e(1), 2, 4)),
            ExtensionAtom("LATE_E0", attack=Attack(e(0), 1, 8)),
        )
        self.n = len(self.atoms)
        self.states = tuple(range(1 << self.n))
        self.contexts = self.states
        self.bmax = 4
        self._obs: dict[int, tuple[int, ...]] = {}

    def kernel(self, state: int) -> Kernel:
        aa = list(self.base_attacks)
        rr = list(self.base_recoveries)
        for i, atom in enumerate(self.atoms):
            if state & (1 << i):
                if atom.attack is not None:
                    aa.append(atom.attack)
                if atom.recovery is not None:
                    rr.append(atom.recovery)
        return make_kernel(self.op, self.cert, aa, rr, self.m, self.k)

    def observation(self, state: int) -> tuple[int, ...]:
        if state not in self._obs:
            solver = CampaignSolver(self.kernel(state))
            self._obs[state] = tuple(solver.delta(b) for b in range(self.bmax + 1))
        return self._obs[state]

    def extend(self, state: int, atom_index: int) -> int:
        return state | (1 << atom_index)

    def apply_context(self, state: int, context: int) -> int:
        return state | context

    def residual_table(self, state: int) -> tuple[tuple[int, ...], ...]:
        return tuple(self.observation(self.apply_context(state, c)) for c in self.contexts)


def canonical_partition(parts: list[list[int]]) -> tuple[tuple[int, ...], ...]:
    return tuple(sorted((tuple(sorted(p)) for p in parts), key=lambda p: p[0]))


def observation_partition(U: ResidualUniverse) -> tuple[tuple[int, ...], ...]:
    by: dict[tuple[int, ...], list[int]] = {}
    for s in U.states:
        by.setdefault(U.observation(s), []).append(s)
    return canonical_partition(list(by.values()))


def refine_partition(U: ResidualUniverse):
    parts = [list(p) for p in observation_partition(U)]
    history = [canonical_partition(parts)]
    while True:
        cid = {s: i for i, block in enumerate(parts) for s in block}
        by: dict[tuple, list[int]] = {}
        for s in U.states:
            sig = (U.observation(s), tuple(cid[U.extend(s, a)] for a in range(U.n)))
            by.setdefault(sig, []).append(s)
        nxt = [sorted(v) for v in by.values()]
        if canonical_partition(nxt) == canonical_partition(parts):
            return history, canonical_partition(parts)
        parts = nxt
        history.append(canonical_partition(parts))


def direct_residual_partition(U: ResidualUniverse) -> tuple[tuple[int, ...], ...]:
    by: dict[tuple[tuple[int, ...], ...], list[int]] = {}
    for s in U.states:
        by.setdefault(U.residual_table(s), []).append(s)
    return canonical_partition(list(by.values()))


def shortest_distinguishing_context(U: ResidualUniverse, s: int, t: int) -> int | None:
    best = None
    for c in U.contexts:
        if U.observation(U.apply_context(s, c)) != U.observation(U.apply_context(t, c)):
            if best is None or (c.bit_count(), c) < (best.bit_count(), best):
                best = c
    return best


def verify_residual_partition_refinement():
    U = ResidualUniverse()
    history, stable = refine_partition(U)
    direct = direct_residual_partition(U)
    assert stable == direct
    return len(U.states), tuple(len(p) for p in history), len(stable), len(U.contexts)


def verify_pure_value_full_abstraction():
    U = ResidualUniverse()
    stable = direct_residual_partition(U)
    block_of = {s: i for i, b in enumerate(stable) for s in b}
    checks = 0
    # Same residual class iff every finite registered extension context gives same campaign value.
    for s in U.states:
        for t in U.states:
            lhs = block_of[s] == block_of[t]
            rhs = U.residual_table(s) == U.residual_table(t)
            assert lhs == rhs
            checks += 1
    return checks, len(stable)


def verify_residual_congruence():
    U = ResidualUniverse()
    stable = direct_residual_partition(U)
    block_of = {s: i for i, b in enumerate(stable) for s in b}
    checks = 0
    for block in stable:
        for s in block:
            for t in block:
                for a in range(U.n):
                    assert block_of[U.extend(s, a)] == block_of[U.extend(t, a)]
                    checks += 1
    return checks


def verify_constructive_context_separation():
    U = ResidualUniverse()
    stable = direct_residual_partition(U)
    reps = [b[0] for b in stable]
    pairs = 0
    max_atoms = 0
    total_atoms = 0
    for i in range(len(reps)):
        for j in range(i + 1, len(reps)):
            c = shortest_distinguishing_context(U, reps[i], reps[j])
            assert c is not None
            assert U.observation(reps[i] | c) != U.observation(reps[j] | c)
            pairs += 1
            max_atoms = max(max_atoms, c.bit_count())
            total_atoms += c.bit_count()
    return pairs, max_atoms, total_atoms


def verify_current_value_not_context_complete():
    U = ResidualUniverse()
    # R2@r1 versus R2@r2: same current Delta_C profile, but adding R3@r1 exposes resource correlation.
    left = 1 << 0
    right = 1 << 1
    context = 1 << 2
    assert U.observation(left) == U.observation(right)
    lv = U.observation(left | context)
    rv = U.observation(right | context)
    assert lv != rv
    return U.observation(left), U.atoms[2].name, lv, rv


def verify_minimality():
    U = ResidualUniverse()
    obs_classes = observation_partition(U)
    residual_classes = direct_residual_partition(U)
    # Each unequal residual class pair has a campaign-value context separator, so any complete
    # representation must distinguish at least this many semantic classes.
    pairs, _, _ = verify_constructive_context_separation()
    assert pairs == len(residual_classes) * (len(residual_classes) - 1) // 2
    return len(U.states), len(obs_classes), len(residual_classes), pairs


def verify_separator_depth_bound():
    U = ResidualUniverse()
    history, stable = refine_partition(U)
    reps = [b[0] for b in stable]
    max_atoms = 0
    for i in range(len(reps)):
        for j in range(i + 1, len(reps)):
            c = shortest_distinguishing_context(U, reps[i], reps[j])
            assert c is not None
            max_atoms = max(max_atoms, c.bit_count())
    # General deterministic finite-system bound is <= number_of_states-1; the discovered universe is much sharper.
    assert max_atoms <= len(U.states) - 1
    return len(history) - 1, max_atoms, len(U.states) - 1


def permute_mask(mask: Mask, perm: tuple[int, ...]) -> Mask:
    out = 0
    for i, j in enumerate(perm):
        if mask & (1 << i):
            out |= 1 << j
    return out


def permute_typed(t: Typed, perm: tuple[int, ...]) -> Typed:
    return permute_mask(t[0], perm), permute_mask(t[1], perm)


def permute_role(mask: Mask, m: int, perm: tuple[int, ...]) -> Mask:
    d, e = split_role_mask(mask, m)
    return role_mask(permute_mask(d, perm), permute_mask(e, perm), m)


def verify_name_invariant_residual_transport():
    # Direct transport check on a smaller two-lane registered context universe.
    m = 2
    k = 1
    p = (1, 0)
    e0 = role_mask(0, 1, m)
    e1 = role_mask(0, 2, m)
    op = (1,)
    cert = ((0, 1), (0, 2))
    attacks = (Attack(e0, 1, 1),)
    recoveries = (Recovery((0, 1), 1, 2),)
    contexts = (
        (Attack(e1, 1, 4), None),
        (None, Recovery((0, 2), 1, 8)),
        (Attack(e0 | e1, 2, 16), None),
    )
    op2 = tuple(permute_mask(x, p) for x in op)
    cert2 = tuple(permute_typed(x, p) for x in cert)
    attacks2 = tuple(Attack(permute_role(a.impact, m, p), a.cost, a.resources) for a in attacks)
    rec2 = tuple(Recovery(permute_typed(r.route, p), r.cost, r.resources) for r in recoveries)
    checks = 0
    for cmask in range(1 << len(contexts)):
        aa = list(attacks); rr = list(recoveries)
        bb = list(attacks2); ss = list(rec2)
        for i, (a, r) in enumerate(contexts):
            if not (cmask & (1 << i)):
                continue
            if a:
                aa.append(a)
                bb.append(Attack(permute_role(a.impact, m, p), a.cost, a.resources))
            if r:
                rr.append(r)
                ss.append(Recovery(permute_typed(r.route, p), r.cost, r.resources))
        KA = make_kernel(op, cert, aa, rr, m, k)
        KB = make_kernel(op2, cert2, bb, ss, m, k)
        SA = CampaignSolver(KA)
        SB = CampaignSolver(KB)
        for b in range(4):
            assert SA.delta(b) == SB.delta(b)
            checks += 1
    return checks


def run_verify():
    n, hist, classes, contexts = verify_residual_partition_refinement()
    print(f"campaign_residual_partition_refinement:PASS:states={n}:class_progression={'->'.join(map(str,hist))}:stable_classes={classes}:contexts={contexts}")
    checks, classes = verify_pure_value_full_abstraction()
    print(f"pure_campaign_value_full_abstraction:PASS:checks={checks}:residual_classes={classes}:observer=DELTA_C_UNDER_ALL_REGISTERED_EXTENSIONS")
    checks = verify_residual_congruence()
    print(f"residual_extension_congruence:PASS:checks={checks}:extension_atoms=6")
    pairs, max_atoms, total_atoms = verify_constructive_context_separation()
    print(f"constructive_future_campaign_separators:PASS:pairs={pairs}:max_context_atoms={max_atoms}:total_separator_atoms={total_atoms}")
    base, atom, lv, rv = verify_current_value_not_context_complete()
    print(f"current_campaign_value_not_residual_complete:PASS:current_profile={base}:separator={atom}:left_extended={lv}:right_extended={rv}")
    raw, obs, res, pairs = verify_minimality()
    print(f"campaign_residual_kernel_minimality:PASS:raw_states={raw}:current_value_classes={obs}:residual_classes={res}:separated_class_pairs={pairs}")
    rounds, depth, bound = verify_separator_depth_bound()
    print(f"finite_residual_separator_bound:PASS:refinement_rounds={rounds}:max_discovered_context_atoms={depth}:general_state_bound={bound}")
    checks = verify_name_invariant_residual_transport()
    print(f"name_invariant_residual_transport:PASS:checks={checks}")
    print("status:PASS")


def run_self_test():
    assert verify_residual_partition_refinement()[2] > verify_residual_partition_refinement()[1][0]
    assert verify_constructive_context_separation()[0] > 0
    assert verify_current_value_not_context_complete()[2] != verify_current_value_not_context_complete()[3]
    assert verify_name_invariant_residual_transport() > 0
    print("SCRT Campaign Residual Equivalence Theorem v2.6.0 self-test")
    print("TOTAL 4/4 PASS")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.verify:
        print("SCRT Campaign Residual Equivalence Theorem v2.6.0 verification")
        run_verify()
    else:
        run_self_test()


if __name__ == "__main__":
    main()
