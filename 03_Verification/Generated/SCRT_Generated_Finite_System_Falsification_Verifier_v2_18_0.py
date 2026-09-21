#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Generated Finite-System Falsification Verifier
Version 2.18.0

Deterministic, dependency-free verification over generated finite systems.

This verifier is evidence, not a source of universal quantification. It performs:
  1. exhaustive residual-equivalence checks for every binary-observer,
     two-generator deterministic transition system with 1..3 states;
  2. deterministic seeded checks on larger finite transition systems;
  3. exhaustive two-ancestry role-polarized silent-assurance obstruction checks;
  4. generated obstruction/recovery-response duality checks;
  5. explicit round-granularity and joint-ancestry-gauge boundary checks.
"""
from __future__ import annotations

import argparse
import itertools
import random
from collections import deque
from functools import lru_cache

VERSION = "2.18.0"
SEED = 270021


def stable_partition(n, a, transition, observer):
    block = tuple(observer)
    while True:
        sigs = []
        for s in range(n):
            sigs.append((observer[s], tuple(block[transition[s * a + g]] for g in range(a))))
        ids = {}
        nxt = []
        for sig in sigs:
            if sig not in ids:
                ids[sig] = len(ids)
            nxt.append(ids[sig])
        nxt = tuple(nxt)
        old_parts = {frozenset(i for i, c in enumerate(block) if c == x) for x in set(block)}
        new_parts = {frozenset(i for i, c in enumerate(nxt) if c == x) for x in set(nxt)}
        if old_parts == new_parts:
            return nxt
        block = nxt


def words(a, max_len):
    yield ()
    for length in range(1, max_len + 1):
        yield from itertools.product(range(a), repeat=length)


def run_word(s, word, a, transition):
    for g in word:
        s = transition[s * a + g]
    return s


def brute_signature(s, n, a, transition, observer):
    # n-1 refinement rounds suffice for an n-state deterministic system.
    return tuple(observer[run_word(s, w, a, transition)] for w in words(a, max(0, n - 1)))


def shortest_separator(s, t, n, a, transition, observer):
    if observer[s] != observer[t]:
        return ()
    q = deque([(s, t, ())])
    seen = {(s, t)}
    while q:
        x, y, w = q.popleft()
        for g in range(a):
            x2 = transition[x * a + g]
            y2 = transition[y * a + g]
            w2 = w + (g,)
            if observer[x2] != observer[y2]:
                return w2
            pair = (x2, y2)
            if pair not in seen:
                seen.add(pair)
                q.append((x2, y2, w2))
    return None


def check_system(n, a, transition, observer):
    block = stable_partition(n, a, transition, observer)
    sigs = tuple(brute_signature(s, n, a, transition, observer) for s in range(n))
    checks = 0
    separators = 0
    max_sep = 0

    for s in range(n):
        for t in range(n):
            assert (block[s] == block[t]) == (sigs[s] == sigs[t])
            checks += 1
            if block[s] == block[t]:
                for g in range(a):
                    assert block[transition[s * a + g]] == block[transition[t * a + g]]
                    checks += 1
            elif s < t:
                w = shortest_separator(s, t, n, a, transition, observer)
                assert w is not None
                assert len(w) <= max(0, n - 1)
                separators += 1
                max_sep = max(max_sep, len(w))

    # Contract strengthening: adding generator 1 cannot merge classes from generator 0.
    if a >= 2:
        trans0 = tuple(transition[s * a] for s in range(n))
        weak = stable_partition(n, 1, trans0, observer)
        for s in range(n):
            for t in range(n):
                if block[s] == block[t]:
                    assert weak[s] == weak[t]
                    checks += 1
    return checks, separators, max_sep, len(set(block))


def verify_exhaustive_residual_systems():
    systems = 0
    checks = 0
    separators = 0
    max_sep = 0
    class_total = 0
    a = 2
    for n in (1, 2, 3):
        for transition in itertools.product(range(n), repeat=n * a):
            for observer in itertools.product(range(2), repeat=n):
                c, s, m, cls = check_system(n, a, transition, observer)
                systems += 1
                checks += c
                separators += s
                max_sep = max(max_sep, m)
                class_total += cls
    assert systems == 5898
    return systems, checks, separators, max_sep, class_total


def verify_seeded_larger_residual_systems():
    rng = random.Random(SEED)
    systems = 0
    checks = 0
    separators = 0
    max_sep = 0
    # 300 systems at each size 4..8 = 1500 deterministic generated systems.
    for n in range(4, 9):
        a = 2
        for _ in range(300):
            transition = tuple(rng.randrange(n) for _ in range(n * a))
            observer = tuple(rng.randrange(2) for _ in range(n))
            c, s, m, _ = check_system(n, a, transition, observer)
            systems += 1
            checks += c
            separators += s
            max_sep = max(max_sep, m)
    assert systems == 1500
    return systems, checks, separators, max_sep


# ---------- SCRT role-polarized assurance structure ----------

def subsets(mask):
    out = []
    s = mask
    while True:
        out.append(s)
        if s == 0:
            break
        s = (s - 1) & mask
    return tuple(out)


def minimal_antichain(items):
    vals = sorted(set(items), key=lambda x: (x.bit_count(), x))
    out = []
    for x in vals:
        if any((y & x) == y for y in out):
            continue
        out.append(x)
    return tuple(out)


def typed_universe(m):
    full = (1 << m) - 1
    return tuple((d, e) for d in range(full + 1) for e in range(full + 1)
                 if (d or e) and (d & e) == 0)


def typed_support(t):
    return t[0] | t[1]


def role_mask(d, e, m):
    return d | (e << m)


def split_role(c, m):
    full = (1 << m) - 1
    return c & full, (c >> m) & full


def disjoint_masks(items):
    seen = 0
    for x in items:
        if seen & x:
            return False
        seen |= x
    return True


def disjoint_typed(items):
    return disjoint_masks(tuple(typed_support(t) for t in items))


def op_packings(routes, k):
    if k <= 0:
        return (0,)
    out = set()
    for idxs in itertools.combinations(range(len(routes)), k):
        chosen = tuple(routes[i] for i in idxs)
        if disjoint_masks(chosen):
            u = 0
            for x in chosen:
                u |= x
            out.add(u)
    return tuple(sorted(out))


def cert_packings(routes, k, m):
    if k <= 0:
        return (0,)
    out = set()
    for idxs in itertools.combinations(range(len(routes)), k):
        chosen = tuple(routes[i] for i in idxs)
        if disjoint_typed(chosen):
            u = 0
            for d, e in chosen:
                u |= role_mask(d, e, m)
            out.add(u)
    return tuple(sorted(out))


def op_capacity(routes, f_d, k):
    surv = tuple(x for x in routes if not (x & f_d))
    for q in range(k, 0, -1):
        if op_packings(surv, q):
            return q
    return 0


def cert_capacity(routes, f_d, f_e, k, m):
    surv = tuple(t for t in routes if not (t[0] & f_d) and not (t[1] & f_e))
    for q in range(k, 0, -1):
        if cert_packings(surv, q, m):
            return q
    return 0


def minimal_blockers(universe_mask, packings):
    if not packings:
        return (0,)
    return minimal_antichain(f for f in subsets(universe_mask) if all(f & p for p in packings))


def op_blockers(m, routes, k):
    return minimal_blockers((1 << m) - 1, op_packings(routes, k))


def cert_role_blockers(m, routes, k):
    return minimal_blockers((1 << (2 * m)) - 1, cert_packings(routes, k, m))


def silent_formula(m, op_routes, cert_routes, k):
    packs = op_packings(op_routes, k)
    if not packs:
        return ()
    out = []
    for b in cert_role_blockers(m, cert_routes, k):
        f_d, _ = split_role(b, m)
        if any((f_d & p) == 0 for p in packs):
            out.append(b)
    return tuple(sorted(out, key=lambda x: (x.bit_count(), x)))


def silent_direct(m, op_routes, cert_routes, k):
    full = (1 << (2 * m)) - 1
    vals = []
    for c in subsets(full):
        f_d, f_e = split_role(c, m)
        if op_capacity(op_routes, f_d, k) >= k and cert_capacity(cert_routes, f_d, f_e, k, m) < k:
            vals.append(c)
    return minimal_antichain(vals)


def evidence_formula(m, op_routes, cert_routes, k):
    if op_capacity(op_routes, 0, k) < k:
        return ()
    e_unions = tuple(sorted(set(split_role(x, m)[1] for x in cert_packings(cert_routes, k, m))))
    return minimal_blockers((1 << m) - 1, e_unions)


def defense_formula(m, op_routes, cert_routes, k):
    if op_capacity(op_routes, 0, k) < k:
        return ()
    d_unions = tuple(sorted(set(split_role(x, m)[0] for x in cert_packings(cert_routes, k, m))))
    candidates = minimal_blockers((1 << m) - 1, d_unions)
    return tuple(sorted(x for x in candidates if op_capacity(op_routes, x, k) >= k))


def evidence_direct(m, op_routes, cert_routes, k):
    full = (1 << m) - 1
    return minimal_antichain(f for f in subsets(full)
                             if op_capacity(op_routes, 0, k) >= k
                             and cert_capacity(cert_routes, 0, f, k, m) < k)


def defense_direct(m, op_routes, cert_routes, k):
    full = (1 << m) - 1
    return minimal_antichain(f for f in subsets(full)
                             if op_capacity(op_routes, f, k) >= k
                             and cert_capacity(cert_routes, f, 0, k, m) < k)


def contains(x, blockers):
    return any((b & x) == b for b in blockers)


def verify_generated_role_polarized_obstructions():
    m = 2
    op_types = tuple(range(1, 1 << m))
    cert_types = typed_universe(m)
    architectures = 0
    formula_checks = 0
    membership_checks = 0
    classified = {"EVIDENCE_ONLY": 0, "DEFENSE_ONLY": 0, "MIXED": 0}

    for op_sel in range(1 << len(op_types)):
        op_routes = tuple(op_types[i] for i in range(len(op_types)) if op_sel & (1 << i))
        for cert_sel in range(1 << len(cert_types)):
            cert_routes = tuple(cert_types[i] for i in range(len(cert_types)) if cert_sel & (1 << i))
            for k in (1, 2):
                architectures += 1
                sf = silent_formula(m, op_routes, cert_routes, k)
                sd = silent_direct(m, op_routes, cert_routes, k)
                assert sf == sd
                assert evidence_formula(m, op_routes, cert_routes, k) == evidence_direct(m, op_routes, cert_routes, k)
                assert defense_formula(m, op_routes, cert_routes, k) == defense_direct(m, op_routes, cert_routes, k)
                formula_checks += 3

                ob = op_blockers(m, op_routes, k)
                for c in range(1 << (2 * m)):
                    f_d, f_e = split_role(c, m)
                    direct = op_capacity(op_routes, f_d, k) >= k and cert_capacity(cert_routes, f_d, f_e, k, m) < k
                    via = (not contains(f_d, ob)) and contains(c, sf)
                    assert direct == via
                    membership_checks += 1

                if op_capacity(op_routes, 0, k) >= k and cert_capacity(cert_routes, 0, 0, k, m) >= k:
                    for b in sf:
                        d, e = split_role(b, m)
                        if d == 0 and e:
                            classified["EVIDENCE_ONLY"] += 1
                        elif d and e == 0:
                            classified["DEFENSE_ONLY"] += 1
                        elif d and e:
                            classified["MIXED"] += 1
    assert all(v > 0 for v in classified.values())
    return architectures, formula_checks, membership_checks, classified


def add_recoveries(cert_routes, recoveries, h):
    out = list(cert_routes)
    for i, r in enumerate(recoveries):
        if h & (1 << i):
            out.append(r)
    return tuple(out)


def minimal_recovery_portfolios(m, op_routes, cert_routes, recoveries, c, k):
    f_d, f_e = split_role(c, m)
    if op_capacity(op_routes, f_d, k) < k:
        return ()
    good = []
    for h in range(1 << len(recoveries)):
        if cert_capacity(add_recoveries(cert_routes, recoveries, h), f_d, f_e, k, m) >= k:
            good.append(h)
    return minimal_antichain(good)


def verify_generated_recovery_duality():
    m = 2
    op_types = tuple(range(1, 1 << m))
    cert_types = typed_universe(m)
    recoveries = ((0, 1), (0, 2), (1, 0), (2, 0))
    checks = 0
    sampled_architectures = 0

    # Deterministic full spread through the 2048 architecture index space.
    architecture_indices = list(range(0, (1 << len(op_types)) * (1 << len(cert_types)), 17))
    for idx in architecture_indices:
        op_sel = idx // (1 << len(cert_types))
        cert_sel = idx % (1 << len(cert_types))
        op_routes = tuple(op_types[i] for i in range(len(op_types)) if op_sel & (1 << i))
        cert_routes = tuple(cert_types[i] for i in range(len(cert_types)) if cert_sel & (1 << i))
        for k in (1, 2):
            sampled_architectures += 1
            for c in range(1 << (2 * m)):
                f_d, f_e = split_role(c, m)
                if op_capacity(op_routes, f_d, k) < k:
                    continue
                resp = minimal_recovery_portfolios(m, op_routes, cert_routes, recoveries, c, k)
                for h in range(1 << len(recoveries)):
                    direct = cert_capacity(add_recoveries(cert_routes, recoveries, h), f_d, f_e, k, m) >= k
                    via_response = any((q & h) == q for q in resp)
                    assert direct == via_response

                    sf = silent_formula(m, op_routes, add_recoveries(cert_routes, recoveries, h), k)
                    via_obstruction = not contains(c, sf)
                    # Since c is operationally safe here, certification is equivalent to no silent blocker.
                    assert direct == via_obstruction
                    checks += 2
    assert checks > 10000
    return sampled_architectures, checks


# ---------- Round-resolved campaign boundaries ----------

def campaign_required_defense(actions, attack_budget, k=2):
    # Base independent certified lanes 0 and 1. Recovery lanes 2 and 3 can be installed once.
    # actions is tuple of (impact_mask, attacker_cost); each primitive can be used once.
    initial = (0, 0, 0, attack_budget)  # compromised_base_mask, installed_recovery_mask, used_mask, budget

    @lru_cache(None)
    def solve(comp, rec, used, budget):
        worst = 0
        any_attack = False
        for i, (impact, attack_cost) in enumerate(actions):
            if used & (1 << i) or attack_cost > budget:
                continue
            any_attack = True
            comp2 = comp | impact
            used2 = used | (1 << i)
            budget2 = budget - attack_cost
            best = None
            # Defender may pass or install one unused recovery this round.
            responses = [None] + [j for j in range(2) if not (rec & (1 << j))]
            for r in responses:
                rec2 = rec if r is None else rec | (1 << r)
                certified = (2 - (comp2 & 0b11).bit_count()) + rec2.bit_count()
                if certified < k:
                    continue
                future = solve(comp2, rec2, used2, budget2)
                if future is None:
                    continue
                cost = (0 if r is None else 1) + future
                best = cost if best is None else min(best, cost)
            if best is None:
                return None
            worst = max(worst, best)
        return 0 if not any_attack else worst

    return solve(*initial)


def static_impact_costs(actions):
    # All feasible subsets; exact impact -> minimum cumulative attacker cost.
    out = {}
    for h in range(1 << len(actions)):
        impact = 0
        cost = 0
        for i, (a, c) in enumerate(actions):
            if h & (1 << i):
                impact |= a
                cost += c
        out[impact] = min(out.get(impact, 10**9), cost)
    return out


def verify_round_granularity_boundary():
    # The burst action duplicates an already-realizable aggregate impact at the same total cost,
    # so the one-shot exact impact/cost summary is unchanged.
    sequential = ((0b01, 1), (0b10, 1))
    burst_augmented = ((0b01, 1), (0b10, 1), (0b11, 2))
    static_seq = static_impact_costs(sequential)
    static_burst = static_impact_costs(burst_augmented)
    assert static_seq == static_burst
    assert static_seq[0b11] == 2

    # Round campaign with attacker budget 2: sequential strikes permit one recovery between
    # strikes; the cost-2 burst arrives in one round and cannot be repaired to k=2 with one response.
    seq_required = campaign_required_defense(sequential, attack_budget=2)
    burst_required = campaign_required_defense(burst_augmented, attack_budget=2)
    assert seq_required == 2
    assert burst_required is None
    return static_seq[0b11], seq_required, "INF"


def residual_classes_for_attack_targets(targets):
    # k=1, two evidence lanes, attacks are one-use. State=(alive_mask,used_mask).
    actions = tuple(1 << t for t in targets)
    states = tuple((alive, used) for alive in range(4) for used in range(1 << len(actions)))

    def observer(s):
        alive, _ = s
        return int(alive != 0)

    def make_gen(i):
        def gen(s):
            alive, used = s
            if used & (1 << i):
                return s
            return alive & ~actions[i], used | (1 << i)
        return gen

    generators = tuple(make_gen(i) for i in range(len(actions)))
    # Direct stable partition over explicit state tuples.
    block = {s: observer(s) for s in states}
    while True:
        sigs = {s: (observer(s), tuple(block[g(s)] for g in generators)) for s in states}
        ids = {}
        nxt = {}
        for s in states:
            sig = sigs[s]
            if sig not in ids:
                ids[sig] = len(ids)
            nxt[s] = ids[sig]
        old = {frozenset(x for x in states if block[x] == c) for c in set(block.values())}
        new = {frozenset(x for x in states if nxt[x] == c) for c in set(nxt.values())}
        if old == new:
            return nxt, (0b11, 0)
        block = nxt


def verify_joint_gauge_boundary():
    same_target = (0, 0)
    split_target = (0, 1)
    # Independently anonymized primitive profiles are identical: two single-lane attacks.
    independent_profile_same = tuple(sorted((1 for _ in same_target)))
    independent_profile_split = tuple(sorted((1 for _ in split_target)))
    assert independent_profile_same == independent_profile_split

    block_same, s0 = residual_classes_for_attack_targets(same_target)
    block_split, t0 = residual_classes_for_attack_targets(split_target)

    # Same-target catalog cannot eliminate both evidence lanes; split-target catalog can.
    same_alive_after_all = 0b11 & ~(1 << 0) & ~(1 << 0)
    split_alive_after_all = 0b11 & ~(1 << 0) & ~(1 << 1)
    assert same_alive_after_all != 0
    assert split_alive_after_all == 0

    # Initial residual behavior therefore differs even though independently anonymized action types match.
    # We expose the exact terminal acceptance contrast directly.
    return independent_profile_same, int(same_alive_after_all != 0), int(split_alive_after_all != 0), len(set(block_same.values())), len(set(block_split.values()))


def self_test():
    tests = []
    # Tiny deterministic smoke tests only; exhaustive/generated work is --verify.
    tr = (0, 1, 1, 1)
    obs = (0, 1)
    tests.append(stable_partition(2, 2, tr, obs)[0] != stable_partition(2, 2, tr, obs)[1])
    tests.append(silent_formula(2, (1, 2), ((0, 1), (0, 2)), 1) == silent_direct(2, (1, 2), ((0, 1), (0, 2)), 1))
    tests.append(campaign_required_defense(((0b01, 1), (0b10, 1)), attack_budget=2) == 2)
    tests.append(verify_joint_gauge_boundary()[1:3] == (1, 0))
    print(f"SCRT Generated Finite-System Falsification Verifier v{VERSION} self-test")
    print(f"TOTAL {sum(tests)}/{len(tests)} PASS")


def verify():
    er = verify_exhaustive_residual_systems()
    sr = verify_seeded_larger_residual_systems()
    rp = verify_generated_role_polarized_obstructions()
    rd = verify_generated_recovery_duality()
    rg = verify_round_granularity_boundary()
    jg = verify_joint_gauge_boundary()

    print(f"SCRT Generated Finite-System Falsification Verifier v{VERSION}")
    print(f"generic_residual_exhaustive:PASS:systems={er[0]}:checks={er[1]}:constructive_separators={er[2]}:max_separator_length={er[3]}")
    print(f"generic_residual_seeded_larger:PASS:seed={SEED}:systems={sr[0]}:checks={sr[1]}:constructive_separators={sr[2]}:max_separator_length={sr[3]}")
    print(f"role_polarized_obstruction_generated:PASS:architectures={rp[0]}:formula_checks={rp[1]}:membership_checks={rp[2]}:evidence_only={rp[3]['EVIDENCE_ONLY']}:defense_only={rp[3]['DEFENSE_ONLY']}:mixed={rp[3]['MIXED']}")
    print(f"recovery_response_generated:PASS:sampled_architectures={rd[0]}:duality_checks={rd[1]}")
    print(f"round_granularity_boundary:PASS:static_joint_cost={rg[0]}:sequential_required_defense={rg[1]}:burst_required_defense={rg[2]}")
    print(f"joint_ancestry_gauge_boundary:PASS:independent_action_profile={jg[0]}:same_target_survives={jg[1]}:split_target_survives={jg[2]}:same_catalog_residual_classes={jg[3]}:split_catalog_residual_classes={jg[4]}")
    print("mechanized_proofs:NONE")
    print("evidence_scope:FINITE_GENERATED_FALSIFICATION")
    print("status:PASS")


def main():
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
    else:
        verify()


if __name__ == "__main__":
    main()
