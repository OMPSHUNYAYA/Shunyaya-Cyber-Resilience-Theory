#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Universal Assurance-Coherent Hardening Theorem
Version 2.10.0

Finite falsification and boundary verification for the written universal theorem.
The script is dependency-free and deterministic. It is not a proof assistant.
"""
from __future__ import annotations

import argparse
import itertools
import math
import random
from dataclasses import dataclass

VERSION = "2.10.0"
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


def maximal_masks(items):
    vals = sorted(set(items), key=lambda x: (-x.bit_count(), x))
    out = []
    for x in vals:
        if any((x & y) == x for y in out):
            continue
        out.append(x)
    return tuple(sorted(out))


def typed_universe(m: int):
    full = (1 << m) - 1
    return tuple((d, e) for d in range(full + 1) for e in range(full + 1)
                 if (d or e) and not (d & e))


def role_mask(d: Mask, e: Mask, m: int):
    return d | (e << m)


def split_role(f: Mask, m: int):
    full = (1 << m) - 1
    return f & full, (f >> m) & full


def support(t: Typed):
    return t[0] | t[1]


def disjoint_masks(items):
    seen = 0
    for x in items:
        if seen & x:
            return False
        seen |= x
    return True


def op_packings(routes: tuple[Mask, ...], k: int):
    if k == 0:
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


def cert_packings(routes: tuple[Typed, ...], k: int, m: int):
    if k == 0:
        return (0,)
    out = set()
    for idxs in itertools.combinations(range(len(routes)), k):
        chosen = tuple(routes[i] for i in idxs)
        if disjoint_masks(tuple(support(t) for t in chosen)):
            u = 0
            for d, e in chosen:
                u |= role_mask(d, e, m)
            out.add(u)
    return tuple(sorted(out))


def op_ok(routes: tuple[Mask, ...], f_d: Mask, k: int):
    return any((p & f_d) == 0 for p in op_packings(routes, k))


def cert_ok(routes: tuple[Typed, ...], f: Mask, k: int, m: int):
    return any((p & f) == 0 for p in cert_packings(routes, k, m))


def silent_set(m: int, op: tuple[Mask, ...], cert: tuple[Typed, ...], k: int):
    return frozenset(
        f for f in range(1 << (2 * m))
        if op_ok(op, split_role(f, m)[0], k) and not cert_ok(cert, f, k, m)
    )


def newly_operational(m: int, old_op: tuple[Mask, ...], new_op: tuple[Mask, ...], k: int):
    return frozenset(
        f for f in range(1 << (2 * m))
        if (not op_ok(old_op, split_role(f, m)[0], k))
        and op_ok(new_op, split_role(f, m)[0], k)
    )


def activation_risk(m: int, old_op: tuple[Mask, ...], new_op: tuple[Mask, ...], cert: tuple[Typed, ...], k: int):
    return frozenset(f for f in newly_operational(m, old_op, new_op, k) if not cert_ok(cert, f, k, m))


def certified_blockers(m: int, cert: tuple[Typed, ...], k: int):
    packs = cert_packings(cert, k, m)
    universe = (1 << (2 * m)) - 1
    if not packs:
        return (0,)
    return minimal_masks(f for f in subsets(universe) if all(f & p for p in packs))


def activation_formula(m: int, old_op: tuple[Mask, ...], new_op: tuple[Mask, ...], cert: tuple[Typed, ...], k: int):
    old_p = op_packings(old_op, k)
    new_p = op_packings(new_op, k)
    blockers = certified_blockers(m, cert, k)
    out = set()
    for f in range(1 << (2 * m)):
        f_d, _ = split_role(f, m)
        if (any((b & f) == b for b in blockers)
                and any((p & f_d) == 0 for p in new_p)
                and all((p & f_d) != 0 for p in old_p)):
            out.add(f)
    return frozenset(out)


def add_routes(base: tuple[Typed, ...], library: tuple[tuple[Typed, ...], ...], h: Mask):
    out = list(base)
    for i, bundle in enumerate(library):
        if h & (1 << i):
            out.extend(bundle)
    return tuple(out)


def good_portfolios(m: int, scenarios, cert: tuple[Typed, ...], library: tuple[tuple[Typed, ...], ...], k: int):
    good = []
    for h in range(1 << len(library)):
        aug = add_routes(cert, library, h)
        if all(cert_ok(aug, f, k, m) for f in scenarios):
            good.append(h)
    return tuple(good)


def responses(m: int, f: Mask, cert: tuple[Typed, ...], library: tuple[tuple[Typed, ...], ...], k: int):
    return minimal_masks(good_portfolios(m, (f,), cert, library, k))


def compensation_frontier(m: int, old_op: tuple[Mask, ...], new_op: tuple[Mask, ...], cert: tuple[Typed, ...], library: tuple[tuple[Typed, ...], ...], k: int, maximal_only=False):
    risk = activation_risk(m, old_op, new_op, cert, k)
    if maximal_only:
        risk = frozenset(maximal_masks(risk))
    return minimal_masks(good_portfolios(m, risk, cert, library, k))


def compensation_frontier_via_responses(m: int, old_op, new_op, cert, library, k):
    risk = activation_risk(m, old_op, new_op, cert, k)
    resp = {f: responses(m, f, cert, library, k) for f in risk}
    good = []
    for h in range(1 << len(library)):
        if all(any((q & h) == q for q in resp[f]) for f in risk):
            good.append(h)
    return minimal_masks(good)


def portfolio_cost(h: Mask, costs: tuple[int, ...]):
    return sum(costs[i] for i in range(len(costs)) if h & (1 << i))


def assurance_compensation_cost(m: int, old_op, new_op, cert, library, costs, k, maximal_only=False):
    frontier = compensation_frontier(m, old_op, new_op, cert, library, k, maximal_only=maximal_only)
    if not frontier:
        return math.inf
    return min(portfolio_cost(h, costs) for h in frontier)


def coherent_after_portfolio(m, old_op, new_op, cert, library, h, k):
    aug = add_routes(cert, library, h)
    return silent_set(m, new_op, aug, k) <= silent_set(m, old_op, cert, k)


def leq_ext(a, b):
    return a <= b


def verify_universal_laws_exhaustive_m2():
    m = 2
    op_types = tuple(range(1, 1 << m))
    cert_types = typed_universe(m)
    law_checks = 0
    strict_exposures = 0
    evidence_checks = 0
    contraction_checks = 0
    coherence_checks = 0
    blocker_checks = 0

    for op_sel in range(1 << len(op_types)):
        old_op = tuple(op_types[i] for i in range(len(op_types)) if op_sel & (1 << i))
        missing_op = [r for r in op_types if r not in old_op]
        for added in missing_op:
            new_op = tuple(sorted(old_op + (added,)))
            for cert_sel in range(1 << len(cert_types)):
                cert = tuple(cert_types[i] for i in range(len(cert_types)) if cert_sel & (1 << i))
                for k in (1, 2):
                    old_s = silent_set(m, old_op, cert, k)
                    new_s = silent_set(m, new_op, cert, k)
                    assert old_s <= new_s
                    law_checks += 1
                    strict_exposures += int(old_s < new_s)

                    activation = new_s - old_s
                    formula = activation_formula(m, old_op, new_op, cert, k)
                    assert activation == formula
                    blocker_checks += 1

                    if op_ok(old_op, 0, k):
                        for f_e in range(1 << m):
                            f = role_mask(0, f_e, m)
                            assert (f in old_s) == (f in new_s)
                            evidence_checks += 1
                        assert all(split_role(f, m)[0] != 0 for f in activation)

                    # one-route certified strengthening when available
                    for t in cert_types[:3]:
                        if t in cert:
                            continue
                        cert_plus = tuple(sorted(cert + (t,)))
                        plus_s = silent_set(m, old_op, cert_plus, k)
                        assert plus_s <= old_s
                        contraction_checks += 1
                        newly_op = newly_operational(m, old_op, new_op, k)
                        expected = all(cert_ok(cert_plus, f, k, m) for f in newly_op)
                        actual = silent_set(m, new_op, cert_plus, k) <= old_s
                        assert actual == expected
                        coherence_checks += 1
                        break

    assert strict_exposures > 0
    return law_checks, strict_exposures, evidence_checks, contraction_checks, coherence_checks, blocker_checks


def verify_compensation_laws_exhaustive_and_generated():
    # Exhaustive/sample-spread m=2 plus deterministic m=3 generated cases.
    m = 2
    op_types = tuple(range(1, 1 << m))
    cert_types = typed_universe(m)
    library = (((0, 1),), ((0, 2),), ((1, 0),), ((2, 0),))
    costs = (1, 2, 2, 3)
    dual_checks = 0
    compression_checks = 0
    coherence_cost_checks = 0
    op_mono_checks = 0
    lib_mono_checks = 0
    cost_mono_checks = 0
    certbase_mono_checks = 0
    stricts = [0, 0, 0, 0]

    total_arch = (1 << len(op_types)) * (1 << len(cert_types))
    for idx in range(0, total_arch, 11):
        op_sel = idx // (1 << len(cert_types))
        cert_sel = idx % (1 << len(cert_types))
        base = tuple(op_types[i] for i in range(len(op_types)) if op_sel & (1 << i))
        cert = tuple(cert_types[i] for i in range(len(cert_types)) if cert_sel & (1 << i))
        miss = [r for r in op_types if r not in base]
        if not miss:
            continue
        mid = tuple(sorted(base + (miss[0],)))
        strong = mid if len(miss) == 1 else tuple(sorted(mid + (miss[1],)))
        for k in (1, 2):
            f1 = compensation_frontier(m, base, mid, cert, library, k)
            f2 = compensation_frontier_via_responses(m, base, mid, cert, library, k)
            assert f1 == f2
            dual_checks += 1

            fm = compensation_frontier(m, base, mid, cert, library, k, maximal_only=True)
            assert f1 == fm
            compression_checks += 1

            # ACI is exactly minimum cost of making the combined hardening coherent.
            aci = assurance_compensation_cost(m, base, mid, cert, library, costs, k)
            coherent_costs = [portfolio_cost(h, costs) for h in range(1 << len(library))
                              if coherent_after_portfolio(m, base, mid, cert, library, h, k)]
            direct = min(coherent_costs) if coherent_costs else math.inf
            assert aci == direct
            coherence_cost_checks += 1

            c_mid = aci
            c_strong = assurance_compensation_cost(m, base, strong, cert, library, costs, k)
            assert c_mid <= c_strong
            op_mono_checks += 1
            stricts[0] += int(c_mid != c_strong)

            small_lib = library[:2]
            small_costs = costs[:2]
            c_small = assurance_compensation_cost(m, base, mid, cert, small_lib, small_costs, k)
            c_large = c_mid
            assert c_large <= c_small
            lib_mono_checks += 1
            stricts[1] += int(c_large != c_small)

            raised = tuple(x + 1 for x in costs)
            c_raised = assurance_compensation_cost(m, base, mid, cert, library, raised, k)
            assert c_mid <= c_raised
            cost_mono_checks += 1
            stricts[2] += int(c_mid != c_raised)

            # Strengthen baseline certified routes; compensation cost cannot increase.
            missing_c = [t for t in cert_types if t not in cert]
            if missing_c:
                cert_plus = tuple(sorted(cert + (missing_c[0],)))
                c_plus = assurance_compensation_cost(m, base, mid, cert_plus, library, costs, k)
                assert c_plus <= c_mid
                certbase_mono_checks += 1
                stricts[3] += int(c_plus != c_mid)

    # deterministic larger generated systems
    rng = random.Random(2100)
    generated = 0
    for _ in range(600):
        m = 3
        op_types = tuple(range(1, 1 << m))
        cert_types = typed_universe(m)
        base = tuple(sorted(r for r in op_types if rng.random() < 0.35))
        missing = [r for r in op_types if r not in base]
        if not missing:
            continue
        rng.shuffle(missing)
        mid = tuple(sorted(base + (missing[0],)))
        strong = mid if len(missing) == 1 else tuple(sorted(mid + (missing[1],)))
        cert = tuple(sorted(t for t in cert_types if rng.random() < 0.12))
        lib_routes = rng.sample(cert_types, 4)
        lib = tuple((t,) for t in lib_routes)
        costs = tuple(rng.randint(0, 4) for _ in lib)
        k = rng.choice((1, 2, 3))

        old_s = silent_set(m, base, cert, k)
        mid_s = silent_set(m, mid, cert, k)
        assert old_s <= mid_s
        assert mid_s - old_s == activation_formula(m, base, mid, cert, k)

        fdir = compensation_frontier(m, base, mid, cert, lib, k)
        fvia = compensation_frontier_via_responses(m, base, mid, cert, lib, k)
        assert fdir == fvia
        assert fdir == compensation_frontier(m, base, mid, cert, lib, k, maximal_only=True)

        c_mid = assurance_compensation_cost(m, base, mid, cert, lib, costs, k)
        c_strong = assurance_compensation_cost(m, base, strong, cert, lib, costs, k)
        assert c_mid <= c_strong
        generated += 1

    assert generated >= 500
    return (dual_checks, compression_checks, coherence_cost_checks, op_mono_checks,
            lib_mono_checks, cost_mono_checks, certbase_mono_checks, tuple(stricts), generated)


def verify_zero_cost_boundary_and_sharpness():
    m = 2
    k = 1
    base = (1,)
    hard = (1, 2)
    cert = ((0, 1),)

    # Evidence-only invariance assumption is sharp: without baseline operational target,
    # pure operational hardening can create evidence-only silent failure.
    no_op = ()
    new_op = (1,)
    f_e = role_mask(0, 1, m)
    assert f_e not in silent_set(m, no_op, cert, k)
    assert f_e in silent_set(m, new_op, cert, k)

    # General zero-cost law: a nonempty zero-cost portfolio may compensate exposure.
    lib = (((2, 0),),)
    c0 = assurance_compensation_cost(m, base, hard, cert, lib, (0,), k)
    assert c0 == 0
    assert activation_risk(m, base, hard, cert, k)
    assert compensation_frontier(m, base, hard, cert, lib, k) != (0,)

    # Positive-cost corollary: if activation risk is nonempty, ACI cannot be zero.
    c1 = assurance_compensation_cost(m, base, hard, cert, lib, (1,), k)
    assert c1 == 1

    # Infinity iff no global compensation exists in the unrestricted additive library model.
    ci = assurance_compensation_cost(m, base, hard, cert, (), (), k)
    assert ci == math.inf
    return c0, c1, ci


def self_test():
    b = verify_zero_cost_boundary_and_sharpness()
    tests = [b[0] == 0, b[1] == 1, b[2] == math.inf]
    print(f"SCRT Universal Assurance-Coherent Hardening Theorem v{VERSION} self-test")
    print(f"TOTAL {sum(tests)}/{len(tests)} PASS")


def verify():
    u = verify_universal_laws_exhaustive_m2()
    c = verify_compensation_laws_exhaustive_and_generated()
    b = verify_zero_cost_boundary_and_sharpness()
    print(f"SCRT Universal Assurance-Coherent Hardening Theorem v{VERSION} verification")
    print(f"operational_hardening_silent_set_monotonicity:PASS:checks={u[0]}:strict={u[1]}")
    print(f"activation_blocker_packing_characterization:PASS:checks={u[5]}")
    print(f"evidence_only_invariance:PASS:checks={u[2]}:assumption=BASELINE_TARGET_OPERATIONAL")
    print(f"certified_hardening_contraction:PASS:checks={u[3]}")
    print(f"assurance_coherence_iff:PASS:checks={u[4]}")
    print(f"compensation_response_antichain_duality:PASS:checks={c[0]}")
    print(f"maximal_activation_compression:PASS:checks={c[1]}")
    print(f"compensation_cost_equals_minimum_coherence_cost:PASS:checks={c[2]}")
    print(f"operational_strengthening_cost_monotonicity:PASS:checks={c[3]}:strict={c[7][0]}")
    print(f"certified_library_cost_monotonicity:PASS:checks={c[4]}:strict={c[7][1]}")
    print(f"action_cost_monotonicity:PASS:checks={c[5]}:strict={c[7][2]}")
    print(f"baseline_certification_strengthening_monotonicity:PASS:checks={c[6]}:strict={c[7][3]}")
    print(f"generated_m3_falsification:PASS:systems={c[8]}")
    print(f"zero_cost_boundary_correction:PASS:zero_cost_compensation={b[0]}:positive_cost={b[1]}:unrestorable=INF")
    print("proof_status:WRITTEN_UNIVERSAL_PROOF_SEPARATE")
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
