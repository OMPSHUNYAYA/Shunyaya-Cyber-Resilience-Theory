from __future__ import annotations


def sat_k(vector, k):
    if k < 0:
        raise ValueError("k must be nonnegative")
    return tuple(min(int(x), k) for x in vector)


def stable_residual_partition(states, observer, generators):
    """Return stable residual class IDs for a finite deterministic system.

    states: finite iterable of hashable states
    observer: state -> hashable current observation
    generators: iterable of deterministic state -> state functions
    """
    states = tuple(states)
    generators = tuple(generators)
    cls = {}
    obs_to_id = {}
    for s in states:
        o = observer(s)
        if o not in obs_to_id:
            obs_to_id[o] = len(obs_to_id)
        cls[s] = obs_to_id[o]

    while True:
        sig_to_id = {}
        nxt = {}
        for s in states:
            sig = (observer(s), tuple(cls[g(s)] for g in generators))
            if sig not in sig_to_id:
                sig_to_id[sig] = len(sig_to_id)
            nxt[s] = sig_to_id[sig]
        if all(nxt[s] == cls[s] for s in states):
            return nxt
        # Normalize class labels by signatures rather than previous numeric IDs.
        old_partition = {}
        new_partition = {}
        for s in states:
            old_partition.setdefault(cls[s], set()).add(s)
            new_partition.setdefault(nxt[s], set()).add(s)
        if {frozenset(v) for v in old_partition.values()} == {frozenset(v) for v in new_partition.values()}:
            return nxt
        cls = nxt


def contextual_equivalent(x, y, class_map):
    return class_map[x] == class_map[y]


def _self_test():
    assert sat_k((0, 2, 9), 3) == (0, 2, 3)
    states = tuple(range(4))
    gens = (lambda x: min(3, x + 1),)
    obs = lambda x: x >= 2
    classes = stable_residual_partition(states, obs, gens)
    assert classes[0] != classes[1]
    assert classes[2] == classes[3]
    return 3


if __name__ == "__main__":
    n = _self_test()
    print("SCRT Canonical Quotient Algorithms v2.7.0")
    print(f"self_test:PASS:{n}")
