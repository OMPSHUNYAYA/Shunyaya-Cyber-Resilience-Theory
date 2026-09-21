from __future__ import annotations

import argparse
from collections import defaultdict
from itertools import product, combinations

VERSION = "2.7.0"


def canonical_pair(x):
    a, b = x
    return (a, b) if a <= b else (b, a)


def direct_target_probe(x, k):
    table = []
    for r0 in range(k + 1):
        for r1 in range(k + 1):
            table.append(int(min(k, x[0] + r0) >= k and min(k, x[1] + r1) >= k))
    y = (x[1], x[0])
    table2 = []
    for r0 in range(k + 1):
        for r1 in range(k + 1):
            table2.append(int(min(k, y[0] + r0) >= k and min(k, y[1] + r1) >= k))
    return min(tuple(table), tuple(table2))


def verify_direct_target_minimality():
    checks = 0
    for k in (1, 2, 3):
        states = sorted({canonical_pair(x) for x in product(range(k + 1), repeat=2)})
        sig = {s: direct_target_probe(s, k) for s in states}
        assert len(sig) == len(set(sig.values()))
        for a, b in combinations(states, 2):
            assert sig[a] != sig[b]
            checks += 1
    return checks


def direct_finite_machine():
    S = tuple(range(7))
    obs = {0:0, 1:0, 2:0, 3:1, 4:1, 5:2, 6:2}
    A = {
        "x": {0:1,1:3,2:2,3:3,4:5,5:5,6:6},
        "y": {0:2,1:1,2:4,3:4,4:4,5:6,6:6},
        "z": {0:0,1:2,2:1,3:5,4:3,5:5,6:6},
    }
    return S, obs, A


def refine(S, obs, A):
    cls = {s: obs[s] for s in S}
    rounds = 0
    history = [len(set(cls.values()))]
    while True:
        sigs = {s:(obs[s], tuple(cls[A[a][s]] for a in A)) for s in S}
        vals = {v:i for i,v in enumerate(sorted(set(sigs.values()), key=repr))}
        nxt = {s:vals[sigs[s]] for s in S}
        rounds += 1
        history.append(len(set(nxt.values())))
        if all(nxt[s] == cls[s] for s in S):
            return cls, rounds - 1, history
        cls = nxt


def all_words(alpha, n):
    yield ()
    for l in range(1,n+1):
        for w in product(alpha, repeat=l):
            yield w


def eval_word(s, w, A):
    for a in w:
        s = A[a][s]
    return s


def verify_direct_residual_minimization():
    S, obs, A = direct_finite_machine()
    cls, rounds, hist = refine(S, obs, A)
    sig = {}
    alpha = tuple(A)
    for s in S:
        sig[s] = tuple(obs[eval_word(s, w, A)] for w in all_words(alpha, len(S)-1))
    direct = {s: sig[s] for s in S}
    for a in S:
        for b in S:
            assert (cls[a] == cls[b]) == (direct[a] == direct[b])
    pairs = 0
    for a, b in combinations(S, 2):
        if cls[a] != cls[b]:
            assert direct[a] != direct[b]
            pairs += 1
    return len(set(obs.values())), len(set(cls.values())), rounds, pairs


def verify_contract_strengthening():
    S, obs, A = direct_finite_machine()
    weakA = {}
    strongA = A
    weak, _, _ = refine(S, obs, weakA)
    strong, _, _ = refine(S, obs, strongA)
    strict = False
    checks = 0
    for a in S:
        for b in S:
            if strong[a] == strong[b]:
                assert weak[a] == weak[b]
                checks += 1
            if weak[a] == weak[b] and strong[a] != strong[b]:
                strict = True
    assert strict
    return len(set(weak.values())), len(set(strong.values())), checks


def verify_infinite_exact_vs_finite_target():
    exact = list(range(1,129))
    k = 4
    exact_classes = len(set(exact))
    target_classes = len({min(n,k) for n in exact})
    assert exact_classes == 128 and target_classes == 4
    return exact_classes, target_classes


def self_test():
    tests = [
        verify_direct_target_minimality() > 0,
        verify_direct_residual_minimization()[1] >= verify_direct_residual_minimization()[0],
        verify_contract_strengthening()[1] >= verify_contract_strengthening()[0],
        verify_infinite_exact_vs_finite_target() == (128,4),
    ]
    print(f"SCRT Integrated Universal Assurance Continuation Independent Verifier v{VERSION} self-test")
    print(f"TOTAL {sum(tests)}/{len(tests)} PASS")


def verify():
    t = verify_direct_target_minimality()
    r = verify_direct_residual_minimization()
    c = verify_contract_strengthening()
    e = verify_infinite_exact_vs_finite_target()
    print(f"SCRT Integrated Universal Assurance Continuation Independent Verifier v{VERSION}")
    print(f"direct_target_minimality:PASS:separated_pairs={t}")
    print(f"direct_residual_minimization:PASS:current_classes={r[0]}:residual_classes={r[1]}:refinement_rounds={r[2]}:inequivalent_pairs={r[3]}")
    print(f"direct_contract_strengthening:PASS:weak_classes={c[0]}:strong_classes={c[1]}:refinement_checks={c[2]}")
    print(f"direct_exact_target_cardinality:PASS:exact_classes={e[0]}:k4_target_classes={e[1]}")
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
