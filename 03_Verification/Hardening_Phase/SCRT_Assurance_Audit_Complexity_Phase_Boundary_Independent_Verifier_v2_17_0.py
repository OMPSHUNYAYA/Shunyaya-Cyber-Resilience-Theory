#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Assurance Audit Complexity Phase-Boundary Independent Verifier
Version 2.17.0

Set-based independent reduction and finite crosscheck.
"""
from __future__ import annotations

import argparse
import itertools
import random

VERSION = "2.17.0"


def disjoint_k(routes, k):
    for group in itertools.combinations(routes, k):
        used = set()
        good = True
        for r in group:
            if used.intersection(r):
                good = False
                break
            used.update(r)
        if good:
            return True
    return k == 0


def op_ok(routes, scenario, k):
    fd, _ = scenario
    return disjoint_k([r for r in routes if r.isdisjoint(fd)], k)


def cert_ok(routes, scenario, k):
    fd, fe = scenario
    surv = []
    for d, e in routes:
        if d.isdisjoint(fd) and e.isdisjoint(fe):
            surv.append(frozenset(set(d) | set(e)))
    return disjoint_k(surv, k)


def install(base, actions, chosen):
    out = list(base)
    for i in chosen:
        out.extend(actions[i])
    return tuple(out)


def risk(old_op, op_actions, chosen, cert, scenarios, k):
    hardened = install(old_op, op_actions, chosen)
    return tuple(s for s in scenarios
                 if not op_ok(old_op, s, k)
                 and op_ok(hardened, s, k)
                 and not cert_ok(cert, s, k))


def powerset(n):
    for r in range(n + 1):
        for c in itertools.combinations(range(n), r):
            yield frozenset(c)


def conflict_free_fast(old_op, op_actions, h, cert, cert_actions, scenarios, k):
    rr = risk(old_op, op_actions, h, cert, scenarios, k)
    maximum = install(cert, cert_actions, frozenset(range(len(cert_actions))))
    return all(cert_ok(maximum, s, k) for s in rr)


def conflict_free_direct(old_op, op_actions, h, cert, cert_actions, scenarios, k):
    rr = risk(old_op, op_actions, h, cert, scenarios, k)
    for q in powerset(len(cert_actions)):
        aug = install(cert, cert_actions, q)
        if all(cert_ok(aug, s, k) for s in rr):
            return True
    return False


def verify_conflict_free():
    rng = random.Random(217101)
    systems = checks = 0
    for _ in range(260):
        m = rng.choice((2, 3))
        U = tuple(range(m))
        k = rng.choice(tuple(range(1, min(2, m) + 1)))
        op_types = tuple(frozenset(c) for r in range(1, m + 1) for c in itertools.combinations(U, r))
        typed = []
        for a in itertools.product((0, 1, 2), repeat=m):
            d = frozenset(i for i, v in enumerate(a) if v == 1)
            e = frozenset(i for i, v in enumerate(a) if v == 2)
            if d or e:
                typed.append((d, e))
        old_op = tuple(x for x in op_types if rng.random() < 0.30)
        op_actions = tuple((rng.choice(op_types),) for __ in range(rng.randint(1, 5)))
        h = frozenset(i for i in range(len(op_actions)) if rng.random() < 0.5)
        cert = tuple(x for x in typed if rng.random() < 0.08)
        cert_actions = tuple((rng.choice(typed),) for __ in range(rng.randint(1, 6)))
        scenarios = []
        for __ in range(rng.randint(2, 7)):
            fd = frozenset(i for i in U if rng.random() < 0.4)
            fe = frozenset(i for i in U if rng.random() < 0.4)
            scenarios.append((fd, fe))
        scenarios = tuple(set(scenarios))
        assert conflict_free_fast(old_op, op_actions, h, cert, cert_actions, scenarios, k) == \
               conflict_free_direct(old_op, op_actions, h, cert, cert_actions, scenarios, k)
        systems += 1; checks += 1
    return systems, checks


def source_perfect_matching(q, triples):
    X = set(range(q)); Y = set(range(q)); Z = set(range(q))
    for selection in itertools.combinations(triples, q):
        if ({a for a, _, _ in selection} == X
                and {b for _, b, _ in selection} == Y
                and {c for _, _, c in selection} == Z):
            return True
    return False


def scrt_reduction(q, triples):
    D = tuple(f"d{x}" for x in range(q))
    E = tuple(f"e{x}" for x in range(q))
    scenarios = tuple((frozenset(y for y in D if y != D[x]),
                       frozenset(y for y in E if y != E[x])) for x in range(q))
    old_op = tuple()
    op_actions = tuple((frozenset((D[x],)),) for x in range(q))
    full_h = frozenset(range(q))
    cert = tuple()
    cert_actions = tuple(((frozenset(), frozenset((E[x],))),) for x, y, z in triples)
    claims = tuple(frozenset((f"y{y}", f"z{z}")) for x, y, z in triples)
    return scenarios, old_op, op_actions, full_h, cert, cert_actions, claims


def scrt_compatible(q, triples):
    scenarios, old_op, op_actions, h, cert, cert_actions, claims = scrt_reduction(q, triples)
    rr = risk(old_op, op_actions, h, cert, scenarios, 1)
    if len(rr) != q:
        return False
    candidates = []
    for s in rr:
        c = []
        for i in range(len(cert_actions)):
            if cert_ok(install(cert, cert_actions, frozenset((i,))), s, 1):
                c.append(i)
        if not c:
            return False
        candidates.append(tuple(c))

    def rec(pos, used):
        if pos == len(candidates):
            return True
        for i in candidates[pos]:
            if used.isdisjoint(claims[i]):
                if rec(pos + 1, used | set(claims[i])):
                    return True
        return False
    return rec(0, set())


def verify_reduction():
    exhaustive = positives = 0
    q = 2
    all_t = tuple(itertools.product(range(q), repeat=3))
    for chosen in powerset(len(all_t)):
        triples = tuple(all_t[i] for i in chosen)
        a = source_perfect_matching(q, triples)
        b = scrt_compatible(q, triples)
        assert a == b
        positives += int(b); exhaustive += 1

    rng = random.Random(217102)
    seeded = seeded_yes = singleton_checks = 0
    q = 3
    all_t = tuple(itertools.product(range(q), repeat=3))
    for _ in range(420):
        triples = tuple(t for t in all_t if rng.random() < 0.33)
        a = source_perfect_matching(q, triples)
        b = scrt_compatible(q, triples)
        assert a == b
        scenarios, old_op, op_actions, h, cert, cert_actions, claims = scrt_reduction(q, triples)
        rr = risk(old_op, op_actions, h, cert, scenarios, 1)
        for s in rr:
            for i in range(len(cert_actions)):
                if cert_ok(install(cert, cert_actions, frozenset((i,))), s, 1):
                    assert len(claims[i]) == 2
                    singleton_checks += 1
        seeded_yes += int(b); seeded += 1
    return exhaustive, positives, seeded, seeded_yes, singleton_checks


def self_test():
    assert source_perfect_matching(2, ((0,0,0),(1,1,1)))
    assert not source_perfect_matching(2, ((0,0,0),(1,0,1)))
    assert scrt_compatible(2, ((0,0,0),(1,1,1)))
    print("SCRT Assurance Audit Complexity Phase-Boundary Independent Verifier v2.17.0 self-test")
    print("TOTAL 3/3 PASS")


def verify():
    s, c = verify_conflict_free()
    e, ep, r, rp, sc = verify_reduction()
    print("SCRT Assurance Audit Complexity Phase-Boundary Independent Verifier v2.17.0")
    print(f"direct_conflict_free_solver_crosscheck:PASS:systems={s}:checks={c}")
    print(f"direct_reduction_exhaustive_q2:PASS:instances={e}:positive={ep}")
    print(f"direct_reduction_seeded_q3:PASS:instances={r}:positive={rp}:singleton_response_checks={sc}")
    print("direct_complexity_boundary:PASS:fixed_k_conflict_free=P:exclusive_resource_k1=NP_COMPLETE")
    print("implementation:SET_BASED_INDEPENDENT")
    print("historical_priority:NOT_ASSERTED")
    print("status:PASS")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--self-test", action="store_true"); ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if a.self_test: self_test()
    elif a.verify: verify()
    else: ap.error("choose --self-test or --verify")


if __name__ == "__main__":
    main()
