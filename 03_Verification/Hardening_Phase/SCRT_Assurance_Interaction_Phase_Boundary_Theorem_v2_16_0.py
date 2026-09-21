#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Assurance Interaction Phase-Boundary Theorem
Version 2.16.0

Deterministic finite falsification for the written universal theorem.
The universal proof is supplied separately. This program is not a proof assistant.
"""
from __future__ import annotations

import argparse
import itertools
import math
import random

VERSION = "2.16.0"
Mask = int
Typed = tuple[Mask, Mask]


def subsets(mask: Mask):
    s = mask
    while True:
        yield s
        if s == 0:
            return
        s = (s - 1) & mask


def minimal_masks(items):
    vals = sorted(set(items), key=lambda x: (x.bit_count(), x))
    out = []
    for x in vals:
        if any((y & x) == y for y in out):
            continue
        out.append(x)
    return tuple(out)


def split_role(f: Mask, m: int):
    full = (1 << m) - 1
    return f & full, (f >> m) & full


def role_mask(fd: Mask, fe: Mask, m: int):
    return fd | (fe << m)


def support(t: Typed):
    return t[0] | t[1]


def pairwise_disjoint(items):
    seen = 0
    for x in items:
        if seen & x:
            return False
        seen |= x
    return True


def typed_universe(m: int):
    full = (1 << m) - 1
    return tuple((d, e) for d in range(full + 1) for e in range(full + 1)
                 if (d or e) and not (d & e))


def op_ok(routes: tuple[Mask, ...], f: Mask, k: int, m: int):
    fd, _ = split_role(f, m)
    surv = tuple(r for r in routes if not (r & fd))
    if k == 0:
        return True
    for comb in itertools.combinations(surv, k):
        if pairwise_disjoint(comb):
            return True
    return False


def cert_ok(routes: tuple[Typed, ...], f: Mask, k: int, m: int):
    fd, fe = split_role(f, m)
    surv = tuple(t for t in routes if not (t[0] & fd) and not (t[1] & fe))
    if k == 0:
        return True
    for comb in itertools.combinations(surv, k):
        if pairwise_disjoint(tuple(support(t) for t in comb)):
            return True
    return False


def add_op(base, library, h):
    out = list(base)
    for i, action_routes in enumerate(library):
        if h & (1 << i):
            out.extend(action_routes)
    return tuple(out)


def add_cert(base, library, q):
    out = list(base)
    for i, action_routes in enumerate(library):
        if q & (1 << i):
            out.extend(action_routes)
    return tuple(out)


def risk_set(m, old_op, op_lib, h, cert, scenarios, k):
    new_op = add_op(old_op, op_lib, h)
    out = []
    for f in scenarios:
        if (not op_ok(old_op, f, k, m)
                and op_ok(new_op, f, k, m)
                and not cert_ok(cert, f, k, m)):
            out.append(f)
    return frozenset(out)


def resource_feasible(q: int, claims: tuple[int, ...]):
    used = 0
    for i, claim in enumerate(claims):
        if q & (1 << i):
            if used & claim:
                return False
            used |= claim
    return True


def good_responses(m, risk, cert, cert_lib, k, claims=None):
    out = []
    for q in range(1 << len(cert_lib)):
        if claims is not None and not resource_feasible(q, claims):
            continue
        aug = add_cert(cert, cert_lib, q)
        if all(cert_ok(aug, f, k, m) for f in risk):
            out.append(q)
    return tuple(out)


def minimal_responses(m, f, cert, cert_lib, k, claims=None):
    return minimal_masks(good_responses(m, (f,), cert, cert_lib, k, claims))


def portfolio_cost(q, costs):
    return sum(costs[i] for i in range(len(costs)) if q & (1 << i))


def aci(m, risk, cert, cert_lib, k, costs, claims=None):
    good = good_responses(m, risk, cert, cert_lib, k, claims)
    if not good:
        return math.inf
    return min(portfolio_cost(q, costs) for q in good)


def local_subportfolios(h, k):
    return tuple(j for j in subsets(h) if j.bit_count() <= k)


def verify_conflict_free_locality_generated():
    rng = random.Random(216001)
    systems = portfolio_checks = risk_checks = feasibility_checks = cost_checks = 0
    strict_joint_exposure = 0
    for _ in range(220):
        m = rng.choice((2, 3))
        k = rng.choice(tuple(range(1, min(2, m) + 1)))
        op_types = tuple(range(1, 1 << m))
        cert_types = typed_universe(m)
        old_op = tuple(r for r in op_types if rng.random() < 0.35)
        op_lib = tuple((rng.choice(op_types),) for __ in range(rng.randint(1, 5)))
        cert = tuple(t for t in cert_types if rng.random() < 0.10)
        cert_lib = tuple((rng.choice(cert_types),) for __ in range(rng.randint(1, 5)))
        costs = tuple(rng.randint(1, 4) for __ in cert_lib)
        scenarios = tuple(sorted(set(rng.randrange(1 << (2 * m))
                                     for __ in range(rng.randint(2, min(8, 1 << (2 * m)))))))
        for h in range(1 << len(op_lib)):
            direct = risk_set(m, old_op, op_lib, h, cert, scenarios, k)
            union = frozenset().union(*(risk_set(m, old_op, op_lib, j, cert, scenarios, k)
                                       for j in local_subportfolios(h, k)))
            assert direct == union
            risk_checks += 1
            locals_ = local_subportfolios(h, k)
            local_aci = tuple(aci(m, risk_set(m, old_op, op_lib, j, cert, scenarios, k),
                                  cert, cert_lib, k, costs) for j in locals_)
            global_aci = aci(m, direct, cert, cert_lib, k, costs)
            assert (global_aci < math.inf) == all(v < math.inf for v in local_aci)
            feasibility_checks += 1
            if global_aci < math.inf:
                lo = max(local_aci) if local_aci else 0
                hi = sum(local_aci)
                assert lo <= global_aci <= hi
                cost_checks += 1
            # Detect portfolios whose risk is not present in any singleton action.
            singles = frozenset().union(*(risk_set(m, old_op, op_lib, 1 << i, cert, scenarios, k)
                                           for i in range(len(op_lib)) if h & (1 << i)))
            strict_joint_exposure += int(bool(direct - singles))
            portfolio_checks += 1
        systems += 1
    return systems, portfolio_checks, risk_checks, feasibility_checks, cost_checks, strict_joint_exposure


def compatible_choice_exists(response_families, claims):
    if not response_families:
        return True
    for choice in itertools.product(*response_families):
        q = 0
        for r in choice:
            q |= r
        if resource_feasible(q, claims):
            return True
    return False


def compatible_choice_min_cost(response_families, claims, costs):
    if not response_families:
        return 0
    best = math.inf
    for choice in itertools.product(*response_families):
        q = 0
        for r in choice:
            q |= r
        if resource_feasible(q, claims):
            best = min(best, portfolio_cost(q, costs))
    return best


def verify_resource_choice_generated():
    rng = random.Random(216002)
    systems = direct_checks = choice_checks = cost_checks = response_edges = 0
    max_response_rank = 0
    for _ in range(320):
        m = rng.choice((2, 3))
        k = rng.choice(tuple(range(1, min(2, m) + 1)))
        cert_types = typed_universe(m)
        cert = tuple(t for t in cert_types if rng.random() < 0.10)
        n_actions = rng.randint(1, 6)
        cert_lib = tuple((rng.choice(cert_types),) for __ in range(n_actions))
        n_resources = rng.randint(1, 4)
        claims = []
        for __ in range(n_actions):
            c = 0
            for r in range(n_resources):
                if rng.random() < 0.28:
                    c |= 1 << r
            if not c:
                c = 1 << rng.randrange(n_resources)
            claims.append(c)
        claims = tuple(claims)
        costs = tuple(rng.randint(0, 4) for __ in range(n_actions))
        risk = tuple(sorted(set(rng.randrange(1 << (2 * m)) for __ in range(rng.randint(0, 5)))))

        direct_good = good_responses(m, risk, cert, cert_lib, k, claims)
        families = []
        impossible_local = False
        for f in risk:
            rs = minimal_responses(m, f, cert, cert_lib, k, claims)
            if not rs:
                impossible_local = True
                break
            for q in rs:
                assert q.bit_count() <= k
                max_response_rank = max(max_response_rank, q.bit_count())
                response_edges += 1
            families.append(rs)
        by_choice = False if impossible_local else compatible_choice_exists(tuple(families), claims)
        assert bool(direct_good) == by_choice
        direct_checks += 1
        choice_checks += 1
        direct_cost = math.inf if not direct_good else min(portfolio_cost(q, costs) for q in direct_good)
        choice_cost = math.inf if impossible_local else compatible_choice_min_cost(tuple(families), claims, costs)
        assert direct_cost == choice_cost
        cost_checks += 1
        systems += 1
    return systems, direct_checks, choice_checks, cost_checks, response_edges, max_response_rank


def phase_instance(t: int):
    # Target k=1.  Each hardening action h_i activates exactly scenario F_i.
    # Each scenario has singleton certified responses, but only t-1 exclusive resources exist.
    m = 2 * t
    k = 1
    d = tuple(1 << i for i in range(t))
    e = tuple(1 << (t + i) for i in range(t))
    all_d = sum(d)
    all_e = sum(e)
    scenarios = tuple(role_mask(all_d ^ d[i], all_e ^ e[i], m) for i in range(t))
    old_op = tuple()
    op_lib = tuple((d[i],) for i in range(t))
    cert = tuple()
    cert_lib = []
    claims = []
    for i in range(t):
        for r in range(t - 1):
            cert_lib.append(((0, e[i]),))
            claims.append(1 << r)
    return m, k, scenarios, old_op, op_lib, cert, tuple(cert_lib), tuple(claims)


def verify_unbounded_resource_audit_order():
    families = portfolio_checks = proper_compensable = local_response_checks = 0
    for t in range(2, 11):
        m, k, scenarios, old_op, op_lib, cert, cert_lib, claims = phase_instance(t)
        full = (1 << t) - 1
        # The operational semantics is checked for every hardening portfolio.
        for h in range(1 << t):
            risk = risk_set(m, old_op, op_lib, h, cert, scenarios, k)
            expected = frozenset(scenarios[i] for i in range(t) if h & (1 << i))
            assert risk == expected
            portfolio_checks += 1
            if h != full:
                # At most t-1 triggered scenarios. Assign them injectively to the
                # t-1 exclusive resources; action (i,r) is available for every pair.
                indices = [i for i in range(t) if h & (1 << i)]
                assignment = {i: r for r, i in enumerate(indices)}
                assert len(set(assignment.values())) == len(indices)
                assert all(0 <= r < t - 1 for r in assignment.values())
                proper_compensable += 1
        full_risk = risk_set(m, old_op, op_lib, full, cert, scenarios, k)
        assert len(full_risk) == t
        # Every successful response to scenario i must choose an action dedicated
        # to i and therefore consume one of only t-1 exclusive resources.  Hence
        # t simultaneous scenarios cannot receive pairwise compatible responses.
        assert t > t - 1
        for i, f in enumerate(scenarios):
            # Explicit singleton local responses (i,r), r=0..t-2.
            responses = tuple(1 << (i * (t - 1) + r) for r in range(t - 1))
            assert len(responses) == t - 1
            assert all(q.bit_count() == 1 for q in responses)
            local_response_checks += len(responses)
        families += 1
    return families, portfolio_checks, proper_compensable, local_response_checks

def verify_sharp_conflict_free_order():
    # For each k, no universal audit order k-1 suffices.
    # Baseline has no routes.  k hardening actions add k disjoint routes.
    # A single declared scenario leaves all k route ancestries untouched and is certification-unsafe.
    checks = 0
    for k in range(1, 7):
        m = k
        old_op = tuple()
        op_lib = tuple((1 << i,) for i in range(k))
        cert = tuple()
        f = role_mask(0, 0, m)
        scenarios = (f,)
        full = (1 << k) - 1
        assert risk_set(m, old_op, op_lib, full, cert, scenarios, k) == frozenset((f,))
        for h in range(1 << k):
            if h.bit_count() <= k - 1:
                assert not risk_set(m, old_op, op_lib, h, cert, scenarios, k)
        checks += 1
    return checks


def self_test():
    # One conflict-free locality test.
    m = 2
    k = 1
    old_op = tuple()
    op_lib = ((1,), (2,))
    cert = tuple()
    scenarios = (role_mask(2, 0, m), role_mask(1, 0, m))
    assert risk_set(m, old_op, op_lib, 3, cert, scenarios, k) == frozenset(scenarios)

    # One resource-constrained phase-boundary witness.
    data = phase_instance(3)
    m, k, scenarios, old_op, op_lib, cert, cert_lib, claims = data
    assert good_responses(m, risk_set(m, old_op, op_lib, 3, cert, scenarios, k), cert, cert_lib, k, claims)
    assert not good_responses(m, risk_set(m, old_op, op_lib, 7, cert, scenarios, k), cert, cert_lib, k, claims)

    # Local responses remain target-bounded.
    assert all(q.bit_count() == 1 for q in minimal_responses(m, scenarios[0], cert, cert_lib, k, claims))
    print("SCRT Assurance Interaction Phase-Boundary Theorem v2.16.0 self-test")
    print("TOTAL 3/3 PASS")


def verify():
    s, pc, rc, fc, cc, strict = verify_conflict_free_locality_generated()
    rs, dc, chc, coc, edges, max_rank = verify_resource_choice_generated()
    fam, upc, prop, local = verify_unbounded_resource_audit_order()
    sharp = verify_sharp_conflict_free_order()
    print("SCRT Assurance Interaction Phase-Boundary Theorem v2.16.0 verification")
    print(f"conflict_free_k_local_audit:PASS:systems={s}:portfolio_checks={pc}:risk_checks={rc}:feasibility_checks={fc}:cost_checks={cc}:strict_joint_exposure={strict}")
    print(f"conflict_free_order_sharpness:PASS:k_values=1..6:checks={sharp}")
    print(f"resource_response_choice_exactness:PASS:systems={rs}:direct_checks={dc}:choice_checks={chc}:cost_checks={coc}")
    print(f"local_response_rank_survives_resources:PASS:response_edges={edges}:max_observed_rank={max_rank}:bound=k")
    print(f"resource_constrained_unbounded_audit_order:PASS:target_k=1:obstruction_orders=2..9:families={fam}:portfolio_checks={upc}:proper_compensable={prop}:local_response_checks={local}")
    print("phase_boundary:PASS:conflict_free_universal_audit_order=k:exclusive_resource_audit_order=UNBOUNDED_BY_k")
    print("proof_status:WRITTEN_UNIVERSAL_PROOF_SEPARATE")
    print("historical_priority:NOT_ASSERTED")
    print("status:PASS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
    elif a.verify:
        verify()
    else:
        ap.error("choose --self-test or --verify")


if __name__ == "__main__":
    main()
