#!/usr/bin/env python3
"""
Shunyaya Cyber Resilience Theory (SCRT)
Role-Polarized Assurance Obstruction Theorem
Version 2.1.0

Exact obstruction and recovery theory for silent assurance failure when defensive
ancestry compromise and evidence-ancestry compromise are distinct attack channels.
Certified packing independence remains defined on physical ancestry, while compromise
is represented on the doubled role space V_D disjoint_union V_E.

Dependency-free and deterministic.
"""
from __future__ import annotations

import argparse
import itertools
from dataclasses import dataclass
from typing import Iterable

VERSION = "2.1.0"
Mask = int
Typed = tuple[Mask, Mask]


def subsets(mask: Mask) -> tuple[Mask, ...]:
    out = []
    s = mask
    while True:
        out.append(s)
        if s == 0:
            break
        s = (s - 1) & mask
    return tuple(out)


def minimal_antichain(items: Iterable[Mask]) -> tuple[Mask, ...]:
    vals = sorted(set(items), key=lambda x: (x.bit_count(), x))
    out: list[Mask] = []
    for x in vals:
        if any((y & x) == y for y in out):
            continue
        out.append(x)
    return tuple(out)


def typed_support(t: Typed) -> Mask:
    return t[0] | t[1]


def valid_typed(t: Typed) -> bool:
    d, e = t
    return (d != 0 or e != 0) and (d & e) == 0


def typed_universe(m: int) -> tuple[Typed, ...]:
    full = (1 << m) - 1
    return tuple((d, e) for d in range(full + 1) for e in range(full + 1) if valid_typed((d, e)))


def role_mask(d: Mask, e: Mask, m: int) -> Mask:
    return d | (e << m)


def split_role_mask(c: Mask, m: int) -> tuple[Mask, Mask]:
    full = (1 << m) - 1
    return c & full, (c >> m) & full


def typed_exposure(t: Typed, m: int) -> Mask:
    return role_mask(t[0], t[1], m)


def pairwise_physically_disjoint(ts: tuple[Typed, ...]) -> bool:
    seen = 0
    for t in ts:
        s = typed_support(t)
        if seen & s:
            return False
        seen |= s
    return True


def pairwise_disjoint_masks(ms: tuple[Mask, ...]) -> bool:
    seen = 0
    for s in ms:
        if seen & s:
            return False
        seen |= s
    return True


def operational_packing_unions(op_routes: tuple[Mask, ...], k: int) -> tuple[Mask, ...]:
    if k <= 0:
        return (0,)
    out: set[Mask] = set()
    for idxs in itertools.combinations(range(len(op_routes)), k):
        chosen = tuple(op_routes[i] for i in idxs)
        if pairwise_disjoint_masks(chosen):
            u = 0
            for s in chosen:
                u |= s
            out.add(u)
    return tuple(sorted(out))


def certified_packing_exposures(cert_routes: tuple[Typed, ...], k: int, m: int) -> tuple[Mask, ...]:
    if k <= 0:
        return (0,)
    out: set[Mask] = set()
    for idxs in itertools.combinations(range(len(cert_routes)), k):
        chosen = tuple(cert_routes[i] for i in idxs)
        if pairwise_physically_disjoint(chosen):
            u = 0
            for t in chosen:
                u |= typed_exposure(t, m)
            out.add(u)
    return tuple(sorted(out))


def op_capacity(op_routes: tuple[Mask, ...], f_d: Mask, k: int) -> int:
    survivors = tuple(s for s in op_routes if (s & f_d) == 0)
    for q in range(k, 0, -1):
        if operational_packing_unions(survivors, q):
            return q
    return 0


def cert_capacity(cert_routes: tuple[Typed, ...], f_d: Mask, f_e: Mask, k: int) -> int:
    survivors = tuple(t for t in cert_routes if (t[0] & f_d) == 0 and (t[1] & f_e) == 0)
    for q in range(k, 0, -1):
        if certified_packing_exposures(survivors, q, max(1, max((typed_support(t).bit_length() for t in cert_routes), default=1))):
            # Independence depends only on physical supports, so the exact m used in
            # exposure encoding is irrelevant to the existence of a packing.
            return q
    return 0


def cert_capacity_m(cert_routes: tuple[Typed, ...], f_d: Mask, f_e: Mask, k: int, m: int) -> int:
    survivors = tuple(t for t in cert_routes if (t[0] & f_d) == 0 and (t[1] & f_e) == 0)
    for q in range(k, 0, -1):
        if certified_packing_exposures(survivors, q, m):
            return q
    return 0


def minimal_blockers(universe_mask: Mask, packings: tuple[Mask, ...]) -> tuple[Mask, ...]:
    if not packings:
        return (0,)
    blockers = [f for f in subsets(universe_mask) if all(f & u for u in packings)]
    return minimal_antichain(blockers)


def operational_blockers(m: int, op_routes: tuple[Mask, ...], k: int) -> tuple[Mask, ...]:
    return minimal_blockers((1 << m) - 1, operational_packing_unions(op_routes, k))


def certified_role_blockers(m: int, cert_routes: tuple[Typed, ...], k: int) -> tuple[Mask, ...]:
    full_role = (1 << (2 * m)) - 1
    return minimal_blockers(full_role, certified_packing_exposures(cert_routes, k, m))


def role_polarized_silent_formula(m: int, op_routes: tuple[Mask, ...], cert_routes: tuple[Typed, ...], k: int) -> tuple[Mask, ...]:
    op_packs = operational_packing_unions(op_routes, k)
    if not op_packs:
        return ()
    out = []
    for b in certified_role_blockers(m, cert_routes, k):
        f_d, _ = split_role_mask(b, m)
        if any((f_d & u) == 0 for u in op_packs):
            out.append(b)
    return tuple(sorted(out, key=lambda x: (x.bit_count(), x)))


def direct_role_polarized_silent(m: int, op_routes: tuple[Mask, ...], cert_routes: tuple[Typed, ...], k: int) -> tuple[Mask, ...]:
    full = (1 << (2 * m)) - 1
    silent = []
    for c in subsets(full):
        f_d, f_e = split_role_mask(c, m)
        if op_capacity(op_routes, f_d, k) >= k and cert_capacity_m(cert_routes, f_d, f_e, k, m) < k:
            silent.append(c)
    return minimal_antichain(silent)


def evidence_only_formula(m: int, op_routes: tuple[Mask, ...], cert_routes: tuple[Typed, ...], k: int) -> tuple[Mask, ...]:
    if op_capacity(op_routes, 0, k) < k:
        return ()
    exps = certified_packing_exposures(cert_routes, k, m)
    e_unions = tuple(sorted(set(split_role_mask(x, m)[1] for x in exps)))
    return minimal_blockers((1 << m) - 1, e_unions)


def defense_only_formula(m: int, op_routes: tuple[Mask, ...], cert_routes: tuple[Typed, ...], k: int) -> tuple[Mask, ...]:
    if op_capacity(op_routes, 0, k) < k:
        return ()
    exps = certified_packing_exposures(cert_routes, k, m)
    d_unions = tuple(sorted(set(split_role_mask(x, m)[0] for x in exps)))
    candidates = minimal_blockers((1 << m) - 1, d_unions)
    return tuple(sorted(b for b in candidates if op_capacity(op_routes, b, k) >= k))


def direct_evidence_only(m: int, op_routes: tuple[Mask, ...], cert_routes: tuple[Typed, ...], k: int) -> tuple[Mask, ...]:
    full = (1 << m) - 1
    vals = [f for f in subsets(full) if op_capacity(op_routes, 0, k) >= k and cert_capacity_m(cert_routes, 0, f, k, m) < k]
    return minimal_antichain(vals)


def direct_defense_only(m: int, op_routes: tuple[Mask, ...], cert_routes: tuple[Typed, ...], k: int) -> tuple[Mask, ...]:
    full = (1 << m) - 1
    vals = [f for f in subsets(full) if op_capacity(op_routes, f, k) >= k and cert_capacity_m(cert_routes, f, 0, k, m) < k]
    return minimal_antichain(vals)


def classify_obstruction(c: Mask, m: int) -> str:
    d, e = split_role_mask(c, m)
    if d == 0 and e != 0:
        return "EVIDENCE_ONLY"
    if d != 0 and e == 0:
        return "DEFENSE_ONLY"
    if d != 0 and e != 0:
        return "MIXED"
    return "EMPTY"


def contains_blocker(x: Mask, blockers: tuple[Mask, ...]) -> bool:
    return any((b & x) == b for b in blockers)


def add_recoveries(cert_routes: tuple[Typed, ...], recoveries: tuple[Typed, ...], hmask: int) -> tuple[Typed, ...]:
    out = list(cert_routes)
    for i, r in enumerate(recoveries):
        if hmask & (1 << i):
            out.append(r)
    return tuple(out)


@dataclass(frozen=True)
class RPADOK:
    op_blockers: tuple[Mask, ...]
    silent_profile: tuple[tuple[Mask, ...], ...]


def make_rpadok(m: int, op_routes: tuple[Mask, ...], cert_routes: tuple[Typed, ...], recoveries: tuple[Typed, ...], k: int) -> RPADOK:
    op_b = operational_blockers(m, op_routes, k)
    prof = tuple(role_polarized_silent_formula(m, op_routes, add_recoveries(cert_routes, recoveries, h), k) for h in range(1 << len(recoveries)))
    return RPADOK(op_b, prof)


def op_safe_kernel(kernel: RPADOK, c: Mask, m: int) -> bool:
    f_d, _ = split_role_mask(c, m)
    return not contains_blocker(f_d, kernel.op_blockers)


def kernel_safe(kernel: RPADOK, c: Mask, h: int, m: int) -> bool:
    return op_safe_kernel(kernel, c, m) and not contains_blocker(c, kernel.silent_profile[h])


def direct_safe(m: int, op_routes: tuple[Mask, ...], cert_routes: tuple[Typed, ...], recoveries: tuple[Typed, ...], c: Mask, h: int, k: int) -> bool:
    f_d, f_e = split_role_mask(c, m)
    if op_capacity(op_routes, f_d, k) < k:
        return False
    cr = add_recoveries(cert_routes, recoveries, h)
    return cert_capacity_m(cr, f_d, f_e, k, m) >= k


def minimal_recovery_portfolios(m: int, op_routes: tuple[Mask, ...], cert_routes: tuple[Typed, ...], recoveries: tuple[Typed, ...], c: Mask, k: int) -> tuple[int, ...]:
    f_d, f_e = split_role_mask(c, m)
    if op_capacity(op_routes, f_d, k) < k:
        return ()
    good = []
    for h in range(1 << len(recoveries)):
        if cert_capacity_m(add_recoveries(cert_routes, recoveries, h), f_d, f_e, k, m) >= k:
            good.append(h)
    good.sort(key=lambda x: (x.bit_count(), x))
    out: list[int] = []
    for h in good:
        if any((r & h) == r for r in out):
            continue
        out.append(h)
    return tuple(out)


def recovery_role_profile(recoveries: tuple[Typed, ...], h: int) -> tuple[int, int, int]:
    e_only = d_only = mixed = 0
    for i, (d, e) in enumerate(recoveries):
        if not (h & (1 << i)):
            continue
        if d == 0 and e != 0:
            e_only += 1
        elif d != 0 and e == 0:
            d_only += 1
        else:
            mixed += 1
    return e_only, d_only, mixed


def defense_choices(r: int, h: int) -> tuple[int | None, ...]:
    return (None, *tuple(i for i in range(r) if not (h & (1 << i))))


def legal_attacks(m: int, c: Mask, kernel: RPADOK) -> tuple[int, ...]:
    out = []
    for bit_index in range(2 * m):
        bit = 1 << bit_index
        if c & bit:
            continue
        cp = c | bit
        if op_safe_kernel(kernel, cp, m):
            out.append(bit_index)
    return tuple(out)


@dataclass
class GameSolution:
    winning: frozenset[tuple[Mask, int]]
    defender_choice: dict[tuple[Mask, int, int], int | None]
    attacker_choice: dict[tuple[Mask, int], int]
    losing_rank: dict[tuple[Mask, int], int]


def solve_kernel_game(m: int, r: int, kernel: RPADOK) -> GameSolution:
    safe_states = {(c, h) for c in range(1 << (2 * m)) for h in range(1 << r) if kernel_safe(kernel, c, h, m)}
    w = set(safe_states)
    attacker: dict[tuple[Mask, int], int] = {}
    losing_rank: dict[tuple[Mask, int], int] = {}
    rank = 0
    while True:
        remove: list[tuple[Mask, int]] = []
        witness: dict[tuple[Mask, int], int] = {}
        for c, h in sorted(w):
            bad = None
            for a in legal_attacks(m, c, kernel):
                cp = c | (1 << a)
                ok = False
                for d in defense_choices(r, h):
                    hp = h if d is None else h | (1 << d)
                    if kernel_safe(kernel, cp, hp, m) and (cp, hp) in w:
                        ok = True
                        break
                if not ok:
                    bad = a
                    break
            if bad is not None:
                remove.append((c, h))
                witness[(c, h)] = bad
        if not remove:
            break
        rank += 1
        for s in remove:
            w.remove(s)
            attacker[s] = witness[s]
            losing_rank[s] = rank
    defender: dict[tuple[Mask, int, int], int | None] = {}
    for c, h in sorted(w):
        for a in legal_attacks(m, c, kernel):
            cp = c | (1 << a)
            for d in defense_choices(r, h):
                hp = h if d is None else h | (1 << d)
                if kernel_safe(kernel, cp, hp, m) and (cp, hp) in w:
                    defender[(c, h, a)] = d
                    break
    return GameSolution(frozenset(w), defender, attacker, losing_rank)


def solve_direct_game(m: int, op_routes: tuple[Mask, ...], cert_routes: tuple[Typed, ...], recoveries: tuple[Typed, ...], k: int) -> frozenset[tuple[Mask, int]]:
    r = len(recoveries)
    safe_states = {(c, h) for c in range(1 << (2 * m)) for h in range(1 << r) if direct_safe(m, op_routes, cert_routes, recoveries, c, h, k)}
    w = set(safe_states)
    while True:
        remove = set()
        for c, h in w:
            for a in range(2 * m):
                bit = 1 << a
                if c & bit:
                    continue
                cp = c | bit
                f_d, _ = split_role_mask(cp, m)
                if op_capacity(op_routes, f_d, k) < k:
                    continue
                if not any(
                    direct_safe(m, op_routes, cert_routes, recoveries, cp, h if d is None else h | (1 << d), k)
                    and (cp, h if d is None else h | (1 << d)) in w
                    for d in defense_choices(r, h)
                ):
                    remove.add((c, h))
                    break
        if not remove:
            break
        w -= remove
    return frozenset(w)


def permute_mask(mask: Mask, p: tuple[int, ...]) -> Mask:
    out = 0
    for i, j in enumerate(p):
        if mask & (1 << i):
            out |= 1 << j
    return out


def permute_typed(t: Typed, p: tuple[int, ...]) -> Typed:
    return permute_mask(t[0], p), permute_mask(t[1], p)


def permute_role(c: Mask, p: tuple[int, ...], m: int) -> Mask:
    d, e = split_role_mask(c, m)
    return role_mask(permute_mask(d, p), permute_mask(e, p), m)


def permute_kernel(kernel: RPADOK, p: tuple[int, ...], m: int) -> RPADOK:
    return RPADOK(
        tuple(sorted((permute_mask(b, p) for b in kernel.op_blockers), key=lambda x: (x.bit_count(), x))),
        tuple(tuple(sorted((permute_role(b, p, m) for b in fam), key=lambda x: (x.bit_count(), x))) for fam in kernel.silent_profile),
    )


def architecture_samples_m3(limit: int = 120) -> tuple[tuple[tuple[Mask, ...], tuple[Typed, ...]], ...]:
    ops = tuple(range(1, 8))
    certs = typed_universe(3)
    out = []
    for seed in range(limit):
        op = tuple(s for i, s in enumerate(ops) if ((seed * 17 + i * 7 + 3) % 11) < 5)
        cr = tuple(t for i, t in enumerate(certs) if ((seed * 29 + i * 13 + 5) % 37) < 7)
        if op and cr:
            out.append((op, cr))
    return tuple(out)


def verify_role_blocker_duality() -> tuple[bool, int, int]:
    checks = 0
    architectures = 0
    m = 2
    ops = (1, 2, 3)
    certs = typed_universe(m)
    # Exhaust operational subsets and a deterministic broad sample of certified subsets.
    for om in range(1 << len(ops)):
        op = tuple(ops[i] for i in range(len(ops)) if om & (1 << i))
        for cm in range(1 << len(certs)):
            if (om * 257 + cm * 17) % 19 != 0:
                continue
            cr = tuple(certs[i] for i in range(len(certs)) if cm & (1 << i))
            for k in (1, 2):
                checks += 1
                if direct_role_polarized_silent(m, op, cr, k) != role_polarized_silent_formula(m, op, cr, k):
                    return False, checks, architectures
            architectures += 1
    for op, cr in architecture_samples_m3(90):
        for k in (1, 2):
            checks += 1
            if direct_role_polarized_silent(3, op, cr, k) != role_polarized_silent_formula(3, op, cr, k):
                return False, checks, architectures
        architectures += 1
    return True, checks, architectures


def verify_role_specific_obstructions() -> tuple[bool, int, tuple[int, int, int]]:
    checks = 0
    counts = [0, 0, 0]
    for op, cr in architecture_samples_m3(140):
        k = 2
        if op_capacity(op, 0, k) < k or cert_capacity_m(cr, 0, 0, k, 3) < k:
            continue
        eo = evidence_only_formula(3, op, cr, k)
        do = defense_only_formula(3, op, cr, k)
        checks += 2
        if eo != direct_evidence_only(3, op, cr, k):
            return False, checks, tuple(counts)
        if do != direct_defense_only(3, op, cr, k):
            return False, checks, tuple(counts)
        full = role_polarized_silent_formula(3, op, cr, k)
        classes = [classify_obstruction(x, 3) for x in full]
        counts[0] += classes.count("EVIDENCE_ONLY")
        counts[1] += classes.count("DEFENSE_ONLY")
        counts[2] += classes.count("MIXED")
        # Pure members of the full antichain agree with the separate formulas after role encoding.
        pure_e = tuple(sorted(split_role_mask(x, 3)[1] for x in full if classify_obstruction(x, 3) == "EVIDENCE_ONLY"))
        pure_d = tuple(sorted(split_role_mask(x, 3)[0] for x in full if classify_obstruction(x, 3) == "DEFENSE_ONLY"))
        checks += 2
        if pure_e != tuple(sorted(eo)) or pure_d != tuple(sorted(do)):
            return False, checks, tuple(counts)
    return True, checks, tuple(counts)


def verify_membership_law() -> tuple[bool, int]:
    checks = 0
    for op, cr in architecture_samples_m3(120):
        k = 2
        obs = role_polarized_silent_formula(3, op, cr, k)
        opb = operational_blockers(3, op, k)
        for c in range(1 << 6):
            fd, fe = split_role_mask(c, 3)
            actual = op_capacity(op, fd, k) >= k and cert_capacity_m(cr, fd, fe, k, 3) < k
            pred = (not contains_blocker(fd, opb)) and contains_blocker(c, obs)
            checks += 1
            if actual != pred:
                return False, checks
    return True, checks


def verify_recovery_duality() -> tuple[bool, int, tuple[int, int, int]]:
    checks = 0
    role_counts = [0, 0, 0]
    certs = typed_universe(3)
    for seed, (op, cr) in enumerate(architecture_samples_m3(90)):
        rec = tuple(certs[(seed * 11 + j * 7 + 2) % len(certs)] for j in range(3))
        kernel = make_rpadok(3, op, cr, rec, 2)
        for c in range(1 << 6):
            fd, _ = split_role_mask(c, 3)
            if contains_blocker(fd, kernel.op_blockers):
                continue
            resp = minimal_recovery_portfolios(3, op, cr, rec, c, 2)
            for h in range(1 << len(rec)):
                by_obs = not contains_blocker(c, kernel.silent_profile[h])
                by_resp = any((q & h) == q for q in resp)
                checks += 1
                if by_obs != by_resp:
                    return False, checks, tuple(role_counts)
            for q in resp:
                e, d, mx = recovery_role_profile(rec, q)
                role_counts[0] += int(e > 0 and d == 0 and mx == 0)
                role_counts[1] += int(d > 0 and e == 0 and mx == 0)
                role_counts[2] += int(mx > 0 or (e > 0 and d > 0))
    return True, checks, tuple(role_counts)


def verify_game_equivalence() -> tuple[bool, int, int, int]:
    checks = max_rank = winning = 0
    certs = typed_universe(3)
    for seed, (op, cr) in enumerate(architecture_samples_m3(80)):
        rec = tuple(certs[(seed * 5 + j * 13 + 1) % len(certs)] for j in range(2))
        kernel = make_rpadok(3, op, cr, rec, 2)
        ks = solve_kernel_game(3, len(rec), kernel)
        ds = solve_direct_game(3, op, cr, rec, 2)
        checks += 1
        if ks.winning != ds:
            return False, checks, max_rank, winning
        max_rank = max(max_rank, max(ks.losing_rank.values(), default=0))
        winning += len(ks.winning)
    return True, checks, max_rank, winning


def verify_constructive_strategies() -> tuple[bool, int, int]:
    checks = max_rank = 0
    certs = typed_universe(3)
    for seed, (op, cr) in enumerate(architecture_samples_m3(60)):
        rec = tuple(certs[(seed * 3 + j * 17 + 4) % len(certs)] for j in range(2))
        kernel = make_rpadok(3, op, cr, rec, 2)
        sol = solve_kernel_game(3, len(rec), kernel)
        for c, h in sol.winning:
            for a in legal_attacks(3, c, kernel):
                key = (c, h, a)
                checks += 1
                if key not in sol.defender_choice:
                    return False, checks, max_rank
                d = sol.defender_choice[key]
                cp = c | (1 << a)
                hp = h if d is None else h | (1 << d)
                if (cp, hp) not in sol.winning or not kernel_safe(kernel, cp, hp, 3):
                    return False, checks, max_rank
        for s, a in sol.attacker_choice.items():
            c, h = s
            r0 = sol.losing_rank[s]
            max_rank = max(max_rank, r0)
            cp = c | (1 << a)
            for d in defense_choices(len(rec), h):
                hp = h if d is None else h | (1 << d)
                checks += 1
                if not kernel_safe(kernel, cp, hp, 3):
                    continue
                if (cp, hp) in sol.winning:
                    return False, checks, max_rank
                if sol.losing_rank.get((cp, hp), 0) >= r0:
                    return False, checks, max_rank
    return True, checks, max_rank


def verify_evidence_only_witness() -> tuple[bool, int, tuple[int, ...]]:
    # Operation is independent of evidence ancestry. Two certified alternatives use
    # evidence ancestries 0 and 1, so compromising both evidence channels creates
    # silent failure while the operational route on ancestry 2 survives.
    m = 3
    k = 1
    op = (1 << 2,)
    cert = ((1 << 2, 1 << 0), (1 << 2, 1 << 1))
    # The two certified signatures share the same defensive ancestry, but k=1 needs
    # only one realization, so both are valid alternatives.
    eo = evidence_only_formula(m, op, cert, k)
    full = role_polarized_silent_formula(m, op, cert, k)
    expected_e = (0b011,)
    expected_role = (role_mask(0, 0b011, m),)
    return eo == expected_e and full == expected_role, len(full), eo



def verify_evidence_only_multi_round_game() -> tuple[bool, int, int]:
    m = 3
    k = 1
    op = (1 << 2,)
    cert = ((1 << 2, 1 << 0), (1 << 2, 1 << 1))
    rec: tuple[Typed, ...] = ()
    kernel = make_rpadok(m, op, cert, rec, k)
    sol = solve_kernel_game(m, 0, kernel)
    s0 = (0, 0)
    rank = sol.losing_rank.get(s0, 0)
    # Operational ancestry 2 cannot be legally compromised because that would drop
    # C_op below k. The two evidence coordinates form the unique minimal silent blocker.
    evidence_blocker = role_mask(0, 0b011, m)
    return s0 not in sol.winning and rank == 2 and kernel.silent_profile[0] == (evidence_blocker,), rank, len(kernel.silent_profile[0])

def verify_kernel_full_abstraction() -> tuple[bool, int, int, int]:
    checks = separators = 0
    m = 2
    certs = typed_universe(m)
    op_candidates = (1, 2, 3)
    rec = (certs[0], certs[-1])
    kernels: dict[RPADOK, list[tuple[tuple[Mask, ...], tuple[Typed, ...]]]] = {}
    for om in range(1 << len(op_candidates)):
        op = tuple(op_candidates[i] for i in range(len(op_candidates)) if om & (1 << i))
        for cm in range(1 << len(certs)):
            if (om * 31 + cm) % 5 != 0:
                continue
            cr = tuple(certs[i] for i in range(len(certs)) if cm & (1 << i))
            k = make_rpadok(m, op, cr, rec, 1)
            kernels.setdefault(k, []).append((op, cr))
    for kernel, group in kernels.items():
        base = solve_kernel_game(m, len(rec), kernel).winning
        for op, cr in group:
            checks += 1
            if solve_direct_game(m, op, cr, rec, 1) != base:
                return False, checks, separators, len(kernels)
    reps = list(kernels)
    for i in range(len(reps)):
        for j in range(i + 1, len(reps)):
            a, b = reps[i], reps[j]
            sep = False
            for c in range(1 << (2 * m)):
                for h in range(1 << len(rec)):
                    if kernel_safe(a, c, h, m) != kernel_safe(b, c, h, m):
                        sep = True
                        break
                if sep:
                    break
            checks += 1
            if not sep:
                return False, checks, separators, len(kernels)
            separators += 1
    return True, checks, separators, len(kernels)


def verify_name_transport() -> tuple[bool, int]:
    checks = 0
    perms = tuple(itertools.permutations(range(3)))
    certs = typed_universe(3)
    for seed, (op, cr) in enumerate(architecture_samples_m3(60)):
        rec = tuple(certs[(seed * 7 + j * 11) % len(certs)] for j in range(2))
        kernel = make_rpadok(3, op, cr, rec, 2)
        for p in perms:
            op2 = tuple(permute_mask(s, p) for s in op)
            cr2 = tuple(permute_typed(t, p) for t in cr)
            rec2 = tuple(permute_typed(t, p) for t in rec)
            k2 = make_rpadok(3, op2, cr2, rec2, 2)
            checks += 1
            if k2 != permute_kernel(kernel, p, 3):
                return False, checks
    return True, checks


def capacity_from_multiset_op(types: tuple[Mask, ...], counts: tuple[int, ...], f_d: Mask, k: int) -> int:
    routes = tuple(t for t, n in zip(types, counts) for _ in range(n))
    return op_capacity(routes, f_d, k)


def capacity_from_multiset_cert(types: tuple[Typed, ...], counts: tuple[int, ...], f_d: Mask, f_e: Mask, k: int, m: int) -> int:
    routes = tuple(t for t, n in zip(types, counts) for _ in range(n))
    return cert_capacity_m(routes, f_d, f_e, k, m)


def verify_target_saturation() -> tuple[bool, int]:
    checks = 0
    op_types = (1, 2, 4)
    cert_types = ((1, 2), (2, 4), (4, 1))
    for k in (1, 2, 3):
        for counts in itertools.product(range(k + 3), repeat=3):
            clipped = tuple(min(n, k) for n in counts)
            for fd in range(8):
                checks += 1
                if (capacity_from_multiset_op(op_types, counts, fd, k) >= k) != (capacity_from_multiset_op(op_types, clipped, fd, k) >= k):
                    return False, checks
            for fd in range(8):
                for fe in range(8):
                    checks += 1
                    if (capacity_from_multiset_cert(cert_types, counts, fd, fe, k, 3) >= k) != (capacity_from_multiset_cert(cert_types, clipped, fd, fe, k, 3) >= k):
                        return False, checks
    return True, checks


def self_test() -> int:
    tests = []
    m = 2
    t = (1, 2)
    tests.append(split_role_mask(typed_exposure(t, m), m) == t)
    op = (1, 2)
    cert = ((1, 2), (2, 1))
    tests.append(op_capacity(op, 0, 1) == 1)
    tests.append(cert_capacity_m(cert, 0, 0, 1, m) == 1)
    obs = role_polarized_silent_formula(m, op, cert, 1)
    tests.append(obs == direct_role_polarized_silent(m, op, cert, 1))
    tests.append(classify_obstruction(role_mask(0, 1, m), m) == "EVIDENCE_ONLY")
    tests.append(classify_obstruction(role_mask(1, 0, m), m) == "DEFENSE_ONLY")
    tests.append(classify_obstruction(role_mask(1, 2, m), m) == "MIXED")
    passed = sum(tests)
    print(f"SCRT Role-Polarized Assurance Obstruction Theorem v{VERSION} self-test")
    print(f"TOTAL {passed}/{len(tests)} PASS" if passed == len(tests) else f"TOTAL {passed}/{len(tests)} FAIL")
    return 0 if passed == len(tests) else 1


def verify() -> int:
    ok1, c1, a1 = verify_role_blocker_duality()
    ok2, c2, counts = verify_role_specific_obstructions()
    ok3, c3 = verify_membership_law()
    ok4, c4, rc = verify_recovery_duality()
    ok5, c5, r5, w5 = verify_game_equivalence()
    ok6, c6, r6 = verify_constructive_strategies()
    ok7, n7, eo7 = verify_evidence_only_witness()
    ok8, r8, n8 = verify_evidence_only_multi_round_game()
    ok9, c9, s9, k9 = verify_kernel_full_abstraction()
    ok10, c10 = verify_name_transport()
    ok11, c11 = verify_target_saturation()
    print(f"SCRT Role-Polarized Assurance Obstruction Theorem v{VERSION} verification")
    print(f"role_polarized_blocker_duality:{'PASS' if ok1 else 'FAIL'}:checks={c1}:architectures={a1}")
    print(f"role_specific_obstruction_partition:{'PASS' if ok2 else 'FAIL'}:checks={c2}:evidence_only={counts[0]}:defense_only={counts[1]}:mixed={counts[2]}")
    print(f"silent_membership_with_operational_exclusion:{'PASS' if ok3 else 'FAIL'}:checks={c3}")
    print(f"role_specific_recovery_response_duality:{'PASS' if ok4 else 'FAIL'}:checks={c4}:evidence_only_portfolios={rc[0]}:defense_only_portfolios={rc[1]}:mixed_portfolios={rc[2]}")
    print(f"polarized_obstruction_game_equivalence:{'PASS' if ok5 else 'FAIL'}:models={c5}:max_rank={r5}:winning_states={w5}")
    print(f"constructive_polarized_strategies:{'PASS' if ok6 else 'FAIL'}:checks={c6}:max_rank={r6}")
    print(f"evidence_only_silent_failure_witness:{'PASS' if ok7 else 'FAIL'}:minimal_obstructions={n7}:evidence_mask={eo7}")
    print(f"evidence_only_persistent_attack_witness:{'PASS' if ok8 else 'FAIL'}:initial_losing_rank={r8}:minimal_obstructions={n8}")
    print(f"role_polarized_obstruction_kernel:{'PASS' if ok9 else 'FAIL'}:kernel_classes={k9}:checks={c9}:constructive_separators={s9}")
    print(f"name_invariant_role_transport:{'PASS' if ok10 else 'FAIL'}:checks={c10}")
    print(f"target_saturation_binding:{'PASS' if ok11 else 'FAIL'}:checks={c11}")
    ok = all((ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8, ok9, ok10, ok11))
    print(f"status:{'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--verify", action="store_true")
    args = p.parse_args()
    if args.self_test:
        return self_test()
    if args.verify:
        return verify()
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
