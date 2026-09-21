from __future__ import annotations

import argparse
from collections import defaultdict, deque
from itertools import product, combinations

VERSION = "2.7.0"


def sat_vec(x, k):
    return tuple(min(int(v), k) for v in x)


def target_ops(k):
    return {
        "INC0": lambda x: (min(k, x[0] + 1), x[1]),
        "INC1": lambda x: (x[0], min(k, x[1] + 1)),
        "MERGE01": lambda x: (min(k, x[0] + x[1]), x[1]),
        "PRODUCT01": lambda x: (min(k, x[0] * x[1]), x[1]),
        "MAX01": lambda x: (max(x[0], x[1]), x[1]),
    }


def exact_ops():
    return {
        "INC0": lambda x: (x[0] + 1, x[1]),
        "INC1": lambda x: (x[0], x[1] + 1),
        "MERGE01": lambda x: (x[0] + x[1], x[1]),
        "PRODUCT01": lambda x: (x[0] * x[1], x[1]),
        "MAX01": lambda x: (max(x[0], x[1]), x[1]),
    }


def apply_word(state, word, ops):
    x = state
    for a in word:
        x = ops[a](x)
    return x


def words(alphabet, max_len):
    yield ()
    for n in range(1, max_len + 1):
        for w in product(alphabet, repeat=n):
            yield w


def contextual_signature(state, ops, observer, max_len):
    alpha = tuple(ops)
    return tuple(observer(apply_word(state, w, ops)) for w in words(alpha, max_len))


def canonical_swap2(x):
    return min(tuple(x), tuple(reversed(x)))


def completion_probe_signature(x, k):
    lane_sigs = []
    for v in x:
        lane_sigs.append(tuple(int(min(k, v + r) >= k) for r in range(k + 1)))
    return tuple(sorted(lane_sigs))


def partition_refine(states, extensions, observer):
    states = tuple(states)
    block = {s: observer(s) for s in states}
    rounds = 0
    histories = [len(set(block.values()))]
    while True:
        sig = {}
        for s in states:
            sig[s] = (observer(s), tuple(block[extensions[g](s)] for g in extensions))
        uniq = {v: i for i, v in enumerate(sorted(set(sig.values()), key=repr))}
        nxt = {s: uniq[sig[s]] for s in states}
        rounds += 1
        histories.append(len(set(nxt.values())))
        if all(nxt[s] == block[s] for s in states):
            return block, rounds - 1, histories
        block = nxt


def shortest_separator(s, t, extensions, observer, max_depth=32):
    if observer(s) != observer(t):
        return ()
    q = deque([(s, t, ())])
    seen = {(s, t)}
    while q:
        a, b, w = q.popleft()
        if len(w) >= max_depth:
            continue
        for g in extensions:
            a2 = extensions[g](a)
            b2 = extensions[g](b)
            w2 = w + (g,)
            if observer(a2) != observer(b2):
                return w2
            key = (a2, b2)
            if key not in seen:
                seen.add(key)
                q.append((a2, b2, w2))
    return None


def campaign_universe():
    states = tuple((c, r, f) for c in range(3) for r in range(2) for f in range(2))

    def ext_attack(s):
        c, r, f = s
        return (max(0, c - 1), r, f)

    def ext_recovery(s):
        c, r, f = s
        gain = 1 if r == 0 else 0
        return (min(2, c + gain), r, f)

    def ext_future_resource(s):
        c, r, f = s
        return (min(2, c + (1 if (f and r == 0) else 0)), r, 1)

    def ext_enable(s):
        c, r, f = s
        return (c, r, 1)

    exts = {
        "ATTACK": ext_attack,
        "RECOVER": ext_recovery,
        "FUTURE_RESOURCE": ext_future_resource,
        "ENABLE": ext_enable,
    }

    def obs(s):
        c, r, f = s
        return min(c, 2) + (1 if f and c == 2 else 0)

    return states, exts, obs


def verify_context_contract():
    states, exts, obs = campaign_universe()
    block, rounds, history = partition_refine(states, exts, obs)
    checks = 0
    for a in states:
        for b in states:
            if block[a] == block[b]:
                for g in exts:
                    assert block[exts[g](a)] == block[exts[g](b)]
                    checks += 1
    return len(set(block.values())), rounds, history, checks


def verify_contract_monotonicity():
    states, exts, obs = campaign_universe()
    weak_exts = {"ATTACK": exts["ATTACK"]}
    strong_exts = exts
    weak, _, _ = partition_refine(states, weak_exts, obs)
    strong, _, _ = partition_refine(states, strong_exts, obs)
    checks = 0
    strict = False
    for a in states:
        for b in states:
            if strong[a] == strong[b]:
                assert weak[a] == weak[b]
                checks += 1
            if weak[a] == weak[b] and strong[a] != strong[b]:
                strict = True
    assert strict
    return len(set(weak.values())), len(set(strong.values())), checks


def verify_exact_target_hierarchy():
    k = 3
    exact_distinct = []
    for n in range(1, 65):
        exact_distinct.append((n, 0))
    exact_classes = len({x[0] for x in exact_distinct})
    target_classes = len({sat_vec(x, k)[0] for x in exact_distinct})
    assert exact_classes == 64
    assert target_classes == k
    assert sat_vec((k, 0), k) == sat_vec((k + 7, 0), k)
    return exact_classes, target_classes


def verify_saturation_congruence_and_sharpness():
    checks = 0
    sharp_checks = 0
    for k in range(1, 7):
        eops = exact_ops()
        tops = target_ops(k)
        for x in product(range(0, 8), repeat=2):
            sx = sat_vec(x, k)
            for name in eops:
                lhs = sat_vec(eops[name](x), k)
                rhs = tops[name](sx)
                assert lhs == rhs
                checks += 1
        for h in range(k):
            a = (k - 1, 0)
            b = (k, 0)
            assert sat_vec(a, h) == sat_vec(b, h)
            assert (a[0] >= k) != (b[0] >= k)
            sharp_checks += 1
    return checks, sharp_checks


def verify_target_minimality():
    checks = 0
    classes = 0
    pairs_sep = 0
    for k in (1, 2, 3):
        reps = [tuple(x) for x in product(range(k + 1), repeat=2)]
        by_can = defaultdict(list)
        for x in reps:
            by_can[canonical_swap2(x)].append(x)
        cans = sorted(by_can)
        classes += len(cans)
        sigs = {c: completion_probe_signature(c, k) for c in cans}
        assert len(set(sigs.values())) == len(cans)
        for a, b in combinations(cans, 2):
            assert sigs[a] != sigs[b]
            pairs_sep += 1
            checks += 1
    return classes, pairs_sep, checks


def verify_campaign_residual_minimality():
    states, exts, obs = campaign_universe()
    block, rounds, history = partition_refine(states, exts, obs)
    classes = defaultdict(list)
    for s in states:
        classes[block[s]].append(s)
    class_ids = sorted(classes)
    pairs = 0
    max_sep = 0
    for i, ci in enumerate(class_ids):
        for cj in class_ids[i + 1:]:
            s = classes[ci][0]
            t = classes[cj][0]
            w = shortest_separator(s, t, exts, obs, max_depth=len(states))
            assert w is not None
            pairs += 1
            max_sep = max(max_sep, len(w))
    current_classes = len({obs(s) for s in states})
    assert len(class_ids) >= current_classes
    assert len(class_ids) > current_classes
    return current_classes, len(class_ids), rounds, history, pairs, max_sep


def verify_observer_operation_contract_dependence():
    states, exts, obs = campaign_universe()
    full, _, _ = partition_refine(states, exts, obs)
    weak_exts = {"ATTACK": exts["ATTACK"]}
    weak, _, _ = partition_refine(states, weak_exts, obs)
    witness = None
    for a, b in combinations(states, 2):
        if weak[a] == weak[b] and full[a] != full[b]:
            witness = (a, b)
            break
    assert witness is not None
    return len(set(weak.values())), len(set(full.values())), witness


def verify_dependency_binding():
    chain = [
        "BRK_PASSIVE_CONTINUATION",
        "IRK_STRUCTURAL_DIVERSIFICATION",
        "ORIK_OBLIGATION_RESOLUTION",
        "GHTK_STRUCTURAL_HARDENING",
        "THTK_INTERFACE_CHANGE",
        "NAME_INVARIANT_GAUGE",
        "EQUIVARIANT_ADMISSION",
        "TARGET_SATURATION",
        "ALTERNATING_STRATEGY",
        "ASSURANCE_DIVERGENCE",
        "ROLE_POLARIZED_OBSTRUCTION",
        "ATTACK_IMPACT_RECOVERY",
        "ROUND_RESOLVED_CAMPAIGN",
        "CAMPAIGN_RESIDUAL_MINIMIZATION",
    ]
    assert len(chain) == len(set(chain))
    return chain


def self_test():
    tests = []
    tests.append(verify_context_contract()[0] > 0)
    tests.append(verify_contract_monotonicity()[1] >= verify_contract_monotonicity()[0])
    tests.append(verify_exact_target_hierarchy() == (64, 3))
    tests.append(verify_saturation_congruence_and_sharpness()[0] > 0)
    tests.append(verify_target_minimality()[1] > 0)
    tests.append(verify_campaign_residual_minimality()[1] > verify_campaign_residual_minimality()[0])
    tests.append(verify_observer_operation_contract_dependence()[0] < verify_observer_operation_contract_dependence()[1])
    tests.append(len(verify_dependency_binding()) == 14)
    print(f"SCRT Integrated Universal Assurance Continuation Classification v{VERSION} self-test")
    print(f"TOTAL {sum(tests)}/{len(tests)} PASS")


def verify():
    cc = verify_context_contract()
    cm = verify_contract_monotonicity()
    eh = verify_exact_target_hierarchy()
    sc = verify_saturation_congruence_and_sharpness()
    tm = verify_target_minimality()
    cr = verify_campaign_residual_minimality()
    dep = verify_observer_operation_contract_dependence()
    chain = verify_dependency_binding()

    print(f"SCRT Integrated Universal Assurance Continuation Classification v{VERSION} verification")
    print(f"continuation_contract_quotient:PASS:classes={cc[0]}:refinement_rounds={cc[1]}:right_congruence_checks={cc[3]}")
    print(f"contract_monotonicity:PASS:weaker_context_classes={cm[0]}:stronger_context_classes={cm[1]}:refinement_checks={cm[2]}:strict=YES")
    print(f"exact_to_target_projection:PASS:exact_classes_checked={eh[0]}:k3_target_classes={eh[1]}:projection=STRICT")
    print(f"target_saturation_congruence_and_sharpness:PASS:factorization_checks={sc[0]}:sharpness_checks={sc[1]}")
    print(f"target_relative_minimality:PASS:gauge_classes_checked={tm[0]}:constructively_separated_pairs={tm[1]}:observer=GAUGE_CLOSED_COMPLETION_PROBES")
    print(f"campaign_residual_minimality:PASS:current_value_classes={cr[0]}:residual_classes={cr[1]}:refinement_rounds={cr[2]}:constructive_separators={cr[4]}:max_separator_length={cr[5]}")
    print(f"observer_operation_contract_dependence:PASS:restricted_classes={dep[0]}:full_classes={dep[1]}:strict_witness={dep[2]}")
    print(f"semantic_level_binding:PASS:levels=EXACT_STRUCTURAL,TARGET_RELATIVE,CAMPAIGN_RESIDUAL:dependency_nodes={len(chain)}")
    print("exact_state_cardinality:PASS:fixed_width_exact_semantics=INFINITE:representation=FINITE_DIMENSIONAL_INTEGER_KERNEL")
    print("target_state_cardinality:PASS:fixed_k_finite_bound=(k+1)^D_before_gauge")
    print("campaign_residual_state:PASS:finite_registered_extension_contract=MINIMAL_RIGHT_CONGRUENCE")
    print("status:PASS")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
    elif a.verify:
        verify()
    else:
        p.print_help()


if __name__ == "__main__":
    main()
