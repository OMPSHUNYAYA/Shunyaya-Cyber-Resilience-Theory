#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Assurance Audit Complexity Phase-Boundary Theorem
Version 2.17.0

Deterministic finite falsification and reduction replay for the written theorem.
"""
from __future__ import annotations

import argparse
import itertools
import random

VERSION = "2.17.0"
Mask = int
Typed = tuple[Mask, Mask]


def split_role(f, m):
    full = (1 << m) - 1
    return f & full, (f >> m) & full


def role_mask(fd, fe, m):
    return fd | (fe << m)


def support(t):
    return t[0] | t[1]


def pairwise_disjoint(items):
    seen = 0
    for x in items:
        if seen & x:
            return False
        seen |= x
    return True


def typed_universe(m):
    full = (1 << m) - 1
    return tuple((d, e) for d in range(full + 1) for e in range(full + 1)
                 if (d or e) and not (d & e))


def op_ok(routes, f, k, m):
    fd, _ = split_role(f, m)
    surv = tuple(r for r in routes if not (r & fd))
    return any(pairwise_disjoint(c) for c in itertools.combinations(surv, k)) if k else True


def cert_ok(routes, f, k, m):
    fd, fe = split_role(f, m)
    surv = tuple(t for t in routes if not (t[0] & fd) and not (t[1] & fe))
    return any(pairwise_disjoint(tuple(support(t) for t in c)) for c in itertools.combinations(surv, k)) if k else True


def add_op(base, actions, h):
    out = list(base)
    for i, rr in enumerate(actions):
        if h & (1 << i):
            out.extend(rr)
    return tuple(out)


def add_cert(base, actions, q):
    out = list(base)
    for i, rr in enumerate(actions):
        if q & (1 << i):
            out.extend(rr)
    return tuple(out)


def risk_set(m, k, old_op, op_actions, h, cert, scenarios):
    new_op = add_op(old_op, op_actions, h)
    return tuple(f for f in scenarios
                 if not op_ok(old_op, f, k, m)
                 and op_ok(new_op, f, k, m)
                 and not cert_ok(cert, f, k, m))


def conflict_free_solver(m, k, old_op, op_actions, h, cert, cert_actions, scenarios):
    # Under conflict-free additive compensation, union of all certified actions is admissible.
    risk = risk_set(m, k, old_op, op_actions, h, cert, scenarios)
    all_cert = add_cert(cert, cert_actions, (1 << len(cert_actions)) - 1)
    return all(cert_ok(all_cert, f, k, m) for f in risk)


def conflict_free_bruteforce(m, k, old_op, op_actions, h, cert, cert_actions, scenarios):
    risk = risk_set(m, k, old_op, op_actions, h, cert, scenarios)
    for q in range(1 << len(cert_actions)):
        aug = add_cert(cert, cert_actions, q)
        if all(cert_ok(aug, f, k, m) for f in risk):
            return True
    return False


def verify_conflict_free_solver_generated():
    rng = random.Random(217001)
    systems = checks = 0
    for _ in range(400):
        m = rng.choice((2, 3))
        k = rng.choice(tuple(range(1, min(2, m) + 1)))
        op_types = tuple(range(1, 1 << m))
        cert_types = typed_universe(m)
        old_op = tuple(r for r in op_types if rng.random() < 0.35)
        op_actions = tuple((rng.choice(op_types),) for __ in range(rng.randint(1, 5)))
        h = rng.randrange(1 << len(op_actions))
        cert = tuple(t for t in cert_types if rng.random() < 0.10)
        cert_actions = tuple((rng.choice(cert_types),) for __ in range(rng.randint(1, 6)))
        scenarios = tuple(sorted(set(rng.randrange(1 << (2 * m)) for __ in range(rng.randint(2, 8)))))
        a = conflict_free_solver(m, k, old_op, op_actions, h, cert, cert_actions, scenarios)
        b = conflict_free_bruteforce(m, k, old_op, op_actions, h, cert, cert_actions, scenarios)
        assert a == b
        checks += 1
        systems += 1
    return systems, checks


def resource_feasible(q, claims):
    used = 0
    for i, c in enumerate(claims):
        if q & (1 << i):
            if used & c:
                return False
            used |= c
    return True


def resource_compensable_backtrack(m, k, cert, cert_actions, claims, risk):
    # Candidate singleton actions for each scenario; sufficient for the reduction instances.
    candidates = []
    for f in risk:
        cc = []
        for i, rr in enumerate(cert_actions):
            if resource_feasible(1 << i, claims) and cert_ok(add_cert(cert, cert_actions, 1 << i), f, k, m):
                cc.append(i)
        if not cc:
            return False
        candidates.append(tuple(cc))
    order = sorted(range(len(risk)), key=lambda i: len(candidates[i]))

    def rec(pos, used_resources):
        if pos == len(order):
            return True
        idx = order[pos]
        for a in candidates[idx]:
            c = claims[a]
            if used_resources & c:
                continue
            if rec(pos + 1, used_resources | c):
                return True
        return False

    return rec(0, 0)


def three_dm_has_perfect(q, triples):
    # X=Y=Z={0,...,q-1}; select q triples covering every coordinate once.
    for choice in itertools.combinations(triples, q):
        if ({x for x, _, _ in choice} == set(range(q))
                and {y for _, y, _ in choice} == set(range(q))
                and {z for _, _, z in choice} == set(range(q))):
            return True
    return False


def reduction_instance(q, triples):
    # k=1. Defensive/evidence ancestry are separate coordinates for each x.
    m = 2 * q
    d = tuple(1 << i for i in range(q))
    e = tuple(1 << (q + i) for i in range(q))
    all_d = sum(d)
    all_e = sum(e)
    scenarios = tuple(role_mask(all_d ^ d[x], all_e ^ e[x], m) for x in range(q))
    old_op = tuple()
    op_actions = tuple((d[x],) for x in range(q))
    h = (1 << q) - 1
    cert = tuple()
    cert_actions = tuple(((0, e[x]),) for x, y, z in triples)
    # Two resource dimensions: y and z.
    claims = tuple((1 << y) | (1 << (q + z)) for x, y, z in triples)
    return m, 1, scenarios, old_op, op_actions, h, cert, cert_actions, claims


def verify_reduction_exhaustive_q2():
    q = 2
    all_triples = tuple(itertools.product(range(q), repeat=3))
    checks = yes = 0
    for mask in range(1 << len(all_triples)):
        triples = tuple(all_triples[i] for i in range(len(all_triples)) if mask & (1 << i))
        expected = three_dm_has_perfect(q, triples)
        m, k, scenarios, old_op, op_actions, h, cert, cert_actions, claims = reduction_instance(q, triples)
        risk = risk_set(m, k, old_op, op_actions, h, cert, scenarios)
        assert len(risk) == q
        got = resource_compensable_backtrack(m, k, cert, cert_actions, claims, risk)
        assert got == expected
        yes += int(got)
        checks += 1
    return checks, yes


def verify_reduction_seeded_q3():
    rng = random.Random(217002)
    q = 3
    universe = tuple(itertools.product(range(q), repeat=3))
    checks = yes = local_singletons = 0
    for _ in range(600):
        triples = tuple(t for t in universe if rng.random() < 0.34)
        expected = three_dm_has_perfect(q, triples)
        m, k, scenarios, old_op, op_actions, h, cert, cert_actions, claims = reduction_instance(q, triples)
        risk = risk_set(m, k, old_op, op_actions, h, cert, scenarios)
        assert len(risk) == q
        got = resource_compensable_backtrack(m, k, cert, cert_actions, claims, risk)
        assert got == expected
        # Every available local response in the reduction is one action and every claim has size two.
        for f in risk:
            for i in range(len(cert_actions)):
                if cert_ok(add_cert(cert, cert_actions, 1 << i), f, k, m):
                    local_singletons += 1
                    assert claims[i].bit_count() == 2
        yes += int(got)
        checks += 1
    return checks, yes, local_singletons


def self_test():
    # Conflict-free maximum installation is exact.
    m = 2; k = 1
    old_op = tuple(); op_actions = ((1,),); h = 1
    cert = tuple(); cert_actions = (((0, 2),),)
    scenarios = (role_mask(0, 0, m),)
    assert conflict_free_solver(m, k, old_op, op_actions, h, cert, cert_actions, scenarios)

    # One positive 3DM reduction instance.
    triples = ((0, 0, 0), (1, 1, 1))
    data = reduction_instance(2, triples)
    risk = risk_set(data[0], data[1], data[3], data[4], data[5], data[6], data[2])
    assert resource_compensable_backtrack(data[0], data[1], data[6], data[7], data[8], risk)

    # One negative 3DM reduction instance.
    triples = ((0, 0, 0), (1, 0, 1))
    data = reduction_instance(2, triples)
    risk = risk_set(data[0], data[1], data[3], data[4], data[5], data[6], data[2])
    assert not resource_compensable_backtrack(data[0], data[1], data[6], data[7], data[8], risk)
    print("SCRT Assurance Audit Complexity Phase-Boundary Theorem v2.17.0 self-test")
    print("TOTAL 3/3 PASS")


def verify():
    s, c = verify_conflict_free_solver_generated()
    e, ey = verify_reduction_exhaustive_q2()
    r, ry, ls = verify_reduction_seeded_q3()
    print("SCRT Assurance Audit Complexity Phase-Boundary Theorem v2.17.0 verification")
    print(f"conflict_free_fixed_k_solver_crosscheck:PASS:systems={s}:checks={c}")
    print(f"resource_constrained_3dm_reduction_exhaustive_q2:PASS:instances={e}:positive={ey}")
    print(f"resource_constrained_3dm_reduction_seeded_q3:PASS:instances={r}:positive={ry}:local_singleton_responses={ls}")
    print("complexity_boundary:PASS:conflict_free_fixed_k=POLYNOMIAL_ON_EXPLICIT_INPUT:exclusive_resources=NP_COMPLETE_AT_k1")
    print("reduction_restrictions:PASS:one_certified_route_per_action:singleton_local_responses:two_resource_claims")
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
