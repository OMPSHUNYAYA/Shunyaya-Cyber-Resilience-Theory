#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Base Resilience Kernel and Typed Assurance Continuation
Version 0.4.0

Exact finite semantics for defensive supports, typed defense/evidence assurance
signatures, compatible cyber composition, compromise conditioning, canonical
kernel reduction, and constructive continuation separation.

Dependency-free. Deterministic exhaustive verification is provided for complete
small universes.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Sequence

VERSION = "0.4.0"
CERTIFICATION_POLICY = "GLOBAL_ANCESTRY_DISJOINT"

Signature = tuple[int, int]  # (defense_mask, evidence_mask)


def popcount(x: int) -> int:
    return x.bit_count()


def powerset_masks(m: int) -> range:
    return range(1 << m)


def nonempty_masks(m: int) -> tuple[int, ...]:
    return tuple(range(1, 1 << m))


def minimal_masks(masks: Iterable[int]) -> tuple[int, ...]:
    xs = sorted(set(masks), key=lambda x: (popcount(x), x))
    out: list[int] = []
    for x in xs:
        if not any((y & x) == y for y in out):
            out.append(x)
    return tuple(out)


def mask_subset(a: int, b: int) -> bool:
    return (a & b) == a


def mask_to_names(mask: int, names: Sequence[str]) -> tuple[str, ...]:
    return tuple(names[i] for i in range(len(names)) if mask & (1 << i))


def packing_number(supports: Iterable[int], failure: int = 0) -> int:
    edges = [e for e in set(supports) if e != 0 and (e & failure) == 0]
    best: dict[int, int] = {0: 0}
    for e in edges:
        current = list(best.items())
        for used, value in current:
            if used & e == 0:
                nu = used | e
                nv = value + 1
                if nv > best.get(nu, -1):
                    best[nu] = nv
    return max(best.values(), default=0)


def operational_compose(a: Iterable[int], b: Iterable[int]) -> tuple[int, ...]:
    return minimal_masks(x | y for x in a for y in b)


def operational_response(state: Iterable[int], context: Iterable[int], failure: int) -> int:
    return packing_number(operational_compose(state, context), failure)


def operational_separator(a_nf: Sequence[int], b_nf: Sequence[int], m: int) -> tuple[int, int] | None:
    # Returns (context_support, failure) separating A from B, or None when A is
    # pointwise dominated by B. For distinct antichains, one orientation separates.
    for x in a_nf:
        if not any(mask_subset(y, x) for y in b_nf):
            failure = ((1 << m) - 1) ^ x
            return x, failure
    return None


def all_signatures(m: int) -> tuple[Signature, ...]:
    out = []
    for d in powerset_masks(m):
        for e in powerset_masks(m):
            if d & e:
                continue
            if (d | e) == 0:
                continue
            out.append((d, e))
    return tuple(out)


def sig_support(s: Signature) -> int:
    return s[0] | s[1]


def sig_leq(a: Signature, b: Signature) -> bool:
    return mask_subset(a[0], b[0]) and mask_subset(a[1], b[1])


def typed_minimal(state: Iterable[Signature]) -> tuple[Signature, ...]:
    xs = sorted(set(state), key=lambda s: (popcount(sig_support(s)), popcount(s[0]), s[0], s[1]))
    out: list[Signature] = []
    for x in xs:
        if not any(sig_leq(y, x) for y in out):
            out.append(x)
    return tuple(out)


def sig_compose(a: Signature, b: Signature) -> Signature | None:
    d = a[0] | b[0]
    e = a[1] | b[1]
    if d & e:
        return None
    return d, e


def typed_compose(a: Iterable[Signature], b: Iterable[Signature]) -> tuple[Signature, ...]:
    out = []
    for x in a:
        for y in b:
            z = sig_compose(x, y)
            if z is not None:
                out.append(z)
    return typed_minimal(out)


def typed_response(state: Iterable[Signature], context: Iterable[Signature], failure: int) -> int:
    composed = typed_compose(state, context)
    supports = [sig_support(s) for s in composed if (sig_support(s) & failure) == 0]
    return packing_number(supports, 0)


def typed_separator(a_nf: Sequence[Signature], b_nf: Sequence[Signature], m: int) -> tuple[Signature, int] | None:
    # If x has no B-signature below it, context {x} plus failure outside support(x)
    # preserves x, kills B signatures using outside ancestry, and conflicts with every
    # surviving B signature that has an opposite polarity inside support(x).
    full = (1 << m) - 1
    for x in a_nf:
        if not any(sig_leq(y, x) for y in b_nf):
            return x, full ^ sig_support(x)
    return None


def signature_to_dict(s: Signature, names: Sequence[str]) -> dict:
    return {
        "defense": list(mask_to_names(s[0], names)),
        "evidence": list(mask_to_names(s[1], names)),
    }


def typed_state_to_dict(state: Iterable[Signature], names: Sequence[str]) -> list[dict]:
    return [signature_to_dict(s, names) for s in typed_minimal(state)]


@dataclass(frozen=True)
class BaseResilienceState:
    names: tuple[str, ...]
    operational: tuple[int, ...]
    certified: tuple[Signature, ...]

    @property
    def m(self) -> int:
        return len(self.names)

    @property
    def kernel(self) -> tuple[tuple[int, ...], tuple[Signature, ...]]:
        return minimal_masks(self.operational), typed_minimal(self.certified)

    def compose(self, other: "BaseResilienceState") -> "BaseResilienceState":
        if self.names != other.names:
            raise ValueError("Boundary ancestry interfaces must agree")
        op = operational_compose(self.operational, other.operational)
        cert = typed_compose(self.certified, other.certified)
        return BaseResilienceState(self.names, op, cert)

    def response(self, context: "BaseResilienceState", failure: int) -> tuple[int, int]:
        if self.names != context.names:
            raise ValueError("Boundary ancestry interfaces must agree")
        return (
            operational_response(self.operational, context.operational, failure),
            typed_response(self.certified, context.certified, failure),
        )


def all_states(items: Sequence) -> tuple[tuple, ...]:
    out = []
    n = len(items)
    for sel in range(1 << n):
        out.append(tuple(items[i] for i in range(n) if sel & (1 << i)))
    return tuple(out)


def verify_naive_union_kernel_counterexample() -> dict:
    names = ("A", "B")
    a, b = 1, 2
    x = ((a, b),)
    y = ((b, a),)

    # Internally they have identical untyped certified supports and identical
    # compromise-conditioned certified capacities.
    x_union = tuple(sig_support(s) for s in x)
    y_union = tuple(sig_support(s) for s in y)
    if x_union != y_union:
        raise AssertionError("counterexample union mismatch")
    internal_x = tuple(packing_number(x_union, f) for f in powerset_masks(2))
    internal_y = tuple(packing_number(y_union, f) for f in powerset_masks(2))
    if internal_x != internal_y:
        raise AssertionError("counterexample internal profile mismatch")

    context = x
    rx = typed_response(x, context, 0)
    ry = typed_response(y, context, 0)
    if not (rx == 1 and ry == 0):
        raise AssertionError(("counterexample failed", rx, ry))

    return {
        "ancestry": list(names),
        "state_x": typed_state_to_dict(x, names),
        "state_y": typed_state_to_dict(y, names),
        "shared_untyped_support": [list(mask_to_names(x_union[0], names))],
        "internal_capacity_profiles_equal": True,
        "distinguishing_context": typed_state_to_dict(context, names),
        "response_x": rx,
        "response_y": ry,
    }


def verify_operational_continuation(max_m: int = 3) -> dict:
    states_checked = 0
    response_checks = 0
    separator_checks = 0
    class_counts = {}

    for m in range(1, max_m + 1):
        supports = nonempty_masks(m)
        states = all_states(supports)
        contexts = states
        nfs = {s: minimal_masks(s) for s in states}
        class_counts[str(m)] = len(set(nfs.values()))

        # Canonicalization preserves every response.
        for s in states:
            nf = nfs[s]
            states_checked += 1
            for z in contexts:
                for f in powerset_masks(m):
                    if operational_response(s, z, f) != operational_response(nf, z, f):
                        raise AssertionError(("operational_soundness", m, s, nf, z, f))
                    response_checks += 1

        # Every distinct pair of normal forms has a constructive separator in one orientation.
        unique_nfs = sorted(set(nfs.values()), key=repr)
        for i, a in enumerate(unique_nfs):
            for b in unique_nfs[i + 1:]:
                sep = operational_separator(a, b, m)
                orient = (a, b)
                if sep is None:
                    sep = operational_separator(b, a, m)
                    orient = (b, a)
                if sep is None:
                    raise AssertionError(("operational_no_separator", m, a, b))
                x, f = sep
                ra = operational_response(orient[0], (x,), f)
                rb = operational_response(orient[1], (x,), f)
                if not (ra >= 1 and rb == 0):
                    raise AssertionError(("operational_bad_separator", m, a, b, x, f, ra, rb))
                separator_checks += 1

    return {
        "states_checked": states_checked,
        "response_checks": response_checks,
        "separator_checks": separator_checks,
        "continuation_class_counts": class_counts,
    }


def verify_typed_continuation_full_m2() -> dict:
    m = 2
    sigs = all_signatures(m)
    states = all_states(sigs)
    contexts = states
    nfs = {s: typed_minimal(s) for s in states}
    unique_nfs = sorted(set(nfs.values()), key=repr)

    response_checks = 0
    fingerprints: dict[tuple[Signature, ...], tuple[int, ...]] = {}

    for s in states:
        nf = nfs[s]
        values = []
        nf_values = []
        for z in contexts:
            for f in powerset_masks(m):
                r = typed_response(s, z, f)
                rn = typed_response(nf, z, f)
                if r != rn:
                    raise AssertionError(("typed_soundness", s, nf, z, f, r, rn))
                values.append(r)
                nf_values.append(rn)
                response_checks += 1
        fp = tuple(values)
        if nf in fingerprints and fingerprints[nf] != fp:
            raise AssertionError(("same_nf_different_response", nf))
        fingerprints[nf] = fp

    # Distinct normal forms must have distinct complete continuation fingerprints.
    if len(set(fingerprints.values())) != len(fingerprints):
        raise AssertionError("typed normal form is not continuation-complete")

    separator_checks = 0
    for i, a in enumerate(unique_nfs):
        for b in unique_nfs[i + 1:]:
            sep = typed_separator(a, b, m)
            orient = (a, b)
            if sep is None:
                sep = typed_separator(b, a, m)
                orient = (b, a)
            if sep is None:
                raise AssertionError(("typed_no_separator", a, b))
            context_sig, failure = sep
            ra = typed_response(orient[0], (context_sig,), failure)
            rb = typed_response(orient[1], (context_sig,), failure)
            if not (ra >= 1 and rb == 0):
                raise AssertionError(("typed_bad_separator", a, b, context_sig, failure, ra, rb))
            separator_checks += 1

    return {
        "ancestry_classes": m,
        "signature_count": len(sigs),
        "states_checked": len(states),
        "continuation_classes": len(unique_nfs),
        "response_checks": response_checks,
        "separator_checks": separator_checks,
    }


def verify_typed_local_laws(max_m: int = 5) -> dict:
    signatures_checked = 0
    dominance_compose_checks = 0
    separator_logic_checks = 0

    for m in range(1, max_m + 1):
        sigs = all_signatures(m)
        signatures_checked += len(sigs)
        for a in sigs:
            for b in sigs:
                if not sig_leq(a, b):
                    continue
                for z in sigs:
                    bz = sig_compose(b, z)
                    if bz is None:
                        continue
                    az = sig_compose(a, z)
                    if az is None or not sig_leq(az, bz):
                        raise AssertionError(("typed_dominance_compose", m, a, b, z, az, bz))
                    dominance_compose_checks += 1

        # Pointwise verification of the constructive separator logic.
        full = (1 << m) - 1
        for x in sigs:
            failure = full ^ sig_support(x)
            for y in sigs:
                if sig_leq(y, x):
                    continue
                if sig_support(y) & failure:
                    separator_logic_checks += 1
                    continue
                if sig_compose(y, x) is not None:
                    raise AssertionError(("typed_separator_logic", m, x, y))
                separator_logic_checks += 1

    return {
        "signatures_checked": signatures_checked,
        "dominance_compose_checks": dominance_compose_checks,
        "separator_logic_checks": separator_logic_checks,
    }


def self_test() -> dict:
    checks = 0
    a, b = 1, 2
    x = (a, b)
    y = (b, a)
    assert sig_compose(x, x) == x
    checks += 1
    assert sig_compose(x, y) is None
    checks += 1
    assert typed_minimal(((a, 0), (a | b, 0))) == ((a, 0),)
    checks += 1
    assert operational_compose((a,), (b,)) == (a | b,)
    checks += 1
    c = verify_naive_union_kernel_counterexample()
    assert c["response_x"] == 1 and c["response_y"] == 0
    checks += 1
    return {"checks": checks}


def verify() -> dict:
    return {
        "version": VERSION,
        "certification_policy": CERTIFICATION_POLICY,
        "self_test": self_test(),
        "naive_union_kernel_counterexample": verify_naive_union_kernel_counterexample(),
        "operational_continuation": verify_operational_continuation(3),
        "typed_continuation_full_m2": verify_typed_continuation_full_m2(),
        "typed_local_laws": verify_typed_local_laws(5),
    }


def discovery_report() -> dict:
    counterexample = verify_naive_union_kernel_counterexample()
    return {
        "version": VERSION,
        "certification_policy": CERTIFICATION_POLICY,
        "structural_result": {
            "naive_untyped_kernel": "NOT_CONTINUATION_COMPLETE",
            "reason": "defense/evidence polarity is invisible after union-support collapse",
            "canonical_base_kernel": "(minimal operational supports, minimal typed defense/evidence signatures)",
            "constructive_separator": "context signature plus complement-support compromise",
        },
        "counterexample": counterexample,
    }


def print_summary(result: dict, mode: str) -> None:
    print(f"SCRT Base Resilience Kernel v{VERSION}")
    print(f"mode:{mode}")
    print(f"certification_policy:{CERTIFICATION_POLICY}")
    if mode == "self-test":
        print(f"TOTAL {result['checks']}/{result['checks']} PASS")
    elif mode == "verify":
        s = result["self_test"]
        o = result["operational_continuation"]
        t = result["typed_continuation_full_m2"]
        l = result["typed_local_laws"]
        print(f"self_test:PASS:{s['checks']}/{s['checks']}")
        print("naive_untyped_kernel:REJECTED_BY_CONSTRUCTIVE_COUNTEREXAMPLE")
        print(f"operational_response_checks:PASS:{o['response_checks']}")
        print(f"operational_separator_checks:PASS:{o['separator_checks']}")
        print(f"typed_full_m2_response_checks:PASS:{t['response_checks']}")
        print(f"typed_full_m2_continuation_classes:{t['continuation_classes']}")
        print(f"typed_full_m2_separator_checks:PASS:{t['separator_checks']}")
        print(f"typed_dominance_compose_checks:PASS:{l['dominance_compose_checks']}")
        print(f"typed_separator_logic_checks:PASS:{l['separator_logic_checks']}")
        print("status:PASS")
    else:
        print("naive_untyped_kernel:NOT_CONTINUATION_COMPLETE")
        print("canonical_base_kernel:TYPED_DEFENSE_EVIDENCE_ANTICHAIN")
        print("constructive_separator:AVAILABLE")
        print("status:PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="SCRT base resilience kernel discovery and verification")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--verify", action="store_true")
    group.add_argument("--discover", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        mode = "self-test"
    elif args.verify:
        result = verify()
        mode = "verify"
    else:
        result = discovery_report()
        mode = "discover"

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_summary(result, mode)


if __name__ == "__main__":
    main()
