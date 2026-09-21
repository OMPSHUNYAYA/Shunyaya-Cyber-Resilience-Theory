#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Universal Assurance-Coherent Hardening Independent Verifier
Version 2.10.0

Independent set-based finite falsification implementation.
"""
from __future__ import annotations

import argparse
import itertools
import math
import random

VERSION = "2.10.0"


def powerset(items):
    xs = tuple(items)
    for r in range(len(xs) + 1):
        for comb in itertools.combinations(xs, r):
            yield frozenset(comb)


def pairwise_disjoint(sets_):
    sets_ = tuple(sets_)
    return all(not (sets_[i] & sets_[j]) for i in range(len(sets_)) for j in range(i + 1, len(sets_)))


def op_ok(routes, f_d, k):
    surv = [r for r in routes if not (r & f_d)]
    return any(pairwise_disjoint(c) for c in itertools.combinations(surv, k)) if k else True


def cert_ok(routes, compromise, k):
    f_d, f_e = compromise
    surv = [(d, e) for d, e in routes if not (d & f_d) and not (e & f_e)]
    if k == 0:
        return True
    for comb in itertools.combinations(surv, k):
        if pairwise_disjoint([d | e for d, e in comb]):
            return True
    return False


def compromises(V):
    ps = tuple(powerset(V))
    return tuple((d, e) for d in ps for e in ps)


def silent(V, op, cert, k):
    return frozenset(F for F in compromises(V) if op_ok(op, F[0], k) and not cert_ok(cert, F, k))


def newly_op(V, old, new, k):
    return frozenset(F for F in compromises(V) if not op_ok(old, F[0], k) and op_ok(new, F[0], k))


def risk(V, old, new, cert, k):
    return frozenset(F for F in newly_op(V, old, new, k) if not cert_ok(cert, F, k))


def add_cert(cert, library, H):
    out = list(cert)
    for i in H:
        out.extend(library[i])
    return tuple(out)


def good(V, scenarios, cert, library, k):
    idx = range(len(library))
    return tuple(H for H in powerset(idx) if all(cert_ok(add_cert(cert, library, H), F, k) for F in scenarios))


def minimal_portfolios(portfolios):
    P = sorted(set(portfolios), key=lambda h: (len(h), tuple(sorted(h))))
    out = []
    for h in P:
        if any(q <= h for q in out):
            continue
        out.append(h)
    return tuple(out)


def maximal_scenarios(scenarios):
    S = list(scenarios)
    def leq(a, b):
        return a[0] <= b[0] and a[1] <= b[1]
    return frozenset(a for a in S if not any(a != b and leq(a, b) for b in S))


def cost(H, costs):
    return sum(costs[i] for i in H)


def aci(V, old, new, cert, library, costs, k, max_only=False):
    A = risk(V, old, new, cert, k)
    if max_only:
        A = maximal_scenarios(A)
    G = good(V, A, cert, library, k)
    return min((cost(H, costs) for H in G), default=math.inf)


def random_route_family(rng, V, p):
    nonempty = [s for s in powerset(V) if s]
    return tuple(s for s in nonempty if rng.random() < p)


def random_cert_family(rng, V, p):
    ps = tuple(powerset(V))
    types = [(d, e) for d in ps for e in ps if (d or e) and not (d & e)]
    return tuple(t for t in types if rng.random() < p)


def verify_direct_laws():
    V = frozenset({0, 1})
    op_types = tuple(s for s in powerset(V) if s)
    ps = tuple(powerset(V))
    cert_types = tuple((d, e) for d in ps for e in ps if (d or e) and not (d & e))
    checks = 0
    strict = 0
    evidence = 0
    coherent = 0

    for old_sel in powerset(range(len(op_types))):
        old = tuple(op_types[i] for i in old_sel)
        missing = [i for i in range(len(op_types)) if i not in old_sel]
        for ai in missing:
            new = tuple(sorted(old + (op_types[ai],), key=lambda x: (len(x), tuple(sorted(x)))))
            for ci, cert in enumerate(((), cert_types[:1], cert_types[::3], cert_types)):
                for k in (1, 2):
                    so = silent(V, old, cert, k)
                    sn = silent(V, new, cert, k)
                    assert so <= sn
                    checks += 1
                    strict += int(so < sn)
                    if op_ok(old, frozenset(), k):
                        for e in powerset(V):
                            F = (frozenset(), e)
                            assert (F in so) == (F in sn)
                            evidence += 1
                    # combined coherence with deterministic certified extension
                    cp = cert
                    for t in cert_types:
                        if t not in cert:
                            cp = cert + (t,)
                            break
                    actual = silent(V, new, cp, k) <= so
                    expected = all(cert_ok(cp, F, k) for F in newly_op(V, old, new, k))
                    assert actual == expected
                    coherent += 1
    assert strict > 0
    return checks, strict, evidence, coherent


def verify_generated_cost_laws():
    rng = random.Random(2101)
    V = frozenset({0, 1, 2, 3})
    route_types = [s for s in powerset(V) if s]
    ps = tuple(powerset(V))
    cert_types = [(d, e) for d in ps for e in ps if (d or e) and not (d & e)]
    systems = 0
    dual = 0
    maximal = 0
    opmono = 0
    libmono = 0
    costmono = 0
    certmono = 0

    for _ in range(450):
        old = tuple(r for r in route_types if rng.random() < 0.18)
        miss = [r for r in route_types if r not in old]
        if len(miss) < 1:
            continue
        rng.shuffle(miss)
        mid = old + (miss[0],)
        strong = mid + ((miss[1],) if len(miss) > 1 else ())
        cert = tuple(t for t in cert_types if rng.random() < 0.035)
        chosen = rng.sample(cert_types, 5)
        library = tuple((t,) for t in chosen)
        costs = tuple(rng.randint(0, 5) for _ in library)
        k = rng.choice((1, 2, 3))

        A = risk(V, old, mid, cert, k)
        responses = {F: minimal_portfolios(good(V, (F,), cert, library, k)) for F in A}
        direct = minimal_portfolios(good(V, A, cert, library, k))
        via = minimal_portfolios(
            H for H in powerset(range(len(library)))
            if all(any(Q <= H for Q in responses[F]) for F in A)
        )
        assert direct == via
        dual += 1

        assert minimal_portfolios(good(V, A, cert, library, k)) == minimal_portfolios(good(V, maximal_scenarios(A), cert, library, k))
        maximal += 1

        c_mid = aci(V, old, mid, cert, library, costs, k)
        c_strong = aci(V, old, strong, cert, library, costs, k)
        assert c_mid <= c_strong
        opmono += 1

        small = library[:3]
        c_small = aci(V, old, mid, cert, small, costs[:3], k)
        assert c_mid <= c_small
        libmono += 1

        raised = tuple(x + 2 for x in costs)
        assert c_mid <= aci(V, old, mid, cert, library, raised, k)
        costmono += 1

        missing_c = [t for t in cert_types if t not in cert]
        if missing_c:
            cp = cert + (missing_c[0],)
            assert aci(V, old, mid, cp, library, costs, k) <= c_mid
            certmono += 1
        systems += 1

    assert systems >= 400
    return systems, dual, maximal, opmono, libmono, costmono, certmono


def verify_boundaries():
    V = frozenset({0, 1})
    base = (frozenset({0}),)
    hard = (frozenset({0}), frozenset({1}))
    cert = ((frozenset(), frozenset({0})),)
    lib = (((frozenset({1}), frozenset()),),)

    # Zero-cost action can compensate a nonempty risk family.
    assert risk(V, base, hard, cert, 1)
    assert aci(V, base, hard, cert, lib, (0,), 1) == 0
    assert aci(V, base, hard, cert, lib, (1,), 1) == 1
    assert aci(V, base, hard, cert, (), (), 1) == math.inf

    # Evidence-only invariance assumption is sharp.
    no_op = ()
    after = (frozenset({0}),)
    F = (frozenset(), frozenset({0}))
    assert F not in silent(V, no_op, cert, 1)
    assert F in silent(V, after, cert, 1)
    return 4


def self_test():
    b = verify_boundaries()
    print(f"SCRT Universal Assurance-Coherent Hardening Independent Verifier v{VERSION} self-test")
    print(f"TOTAL {b}/{b} PASS")


def verify():
    d = verify_direct_laws()
    g = verify_generated_cost_laws()
    b = verify_boundaries()
    print(f"SCRT Universal Assurance-Coherent Hardening Independent Verifier v{VERSION}")
    print(f"direct_hardening_laws:PASS:checks={d[0]}:strict={d[1]}:evidence_only_checks={d[2]}:coherence_checks={d[3]}")
    print(f"generated_compensation_duality:PASS:systems={g[0]}:checks={g[1]}")
    print(f"generated_maximal_scenario_compression:PASS:checks={g[2]}")
    print(f"generated_operational_strengthening_monotonicity:PASS:checks={g[3]}")
    print(f"generated_library_monotonicity:PASS:checks={g[4]}")
    print(f"generated_cost_monotonicity:PASS:checks={g[5]}")
    print(f"generated_baseline_certification_monotonicity:PASS:checks={g[6]}")
    print(f"boundary_and_sharpness_cases:PASS:checks={b}")
    print("implementation:SET_BASED_INDEPENDENT")
    print("historical_priority:NOT_ASSERTED")
    print("status:PASS")


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--self-test", action="store_true")
    g.add_argument("--verify", action="store_true")
    a = p.parse_args()
    self_test() if a.self_test else verify()


if __name__ == "__main__":
    main()
