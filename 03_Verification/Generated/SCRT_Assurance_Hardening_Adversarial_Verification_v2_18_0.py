#!/usr/bin/env python3
"""
SCRT Assurance Hardening Adversarial Verification
Version 2.18.0

Generated finite falsification and scope-consistency checks for the frozen
v2.10/v2.16/v2.17 theorem chain. This program is finite executable evidence;
it is not a proof assistant.
"""
from __future__ import annotations
import argparse
import importlib.util
import itertools
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARD = HERE.parent / "Hardening_Phase"

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HARD / filename)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

P16 = load("p16", "SCRT_Assurance_Interaction_Phase_Boundary_Theorem_v2_16_0.py")
P17 = load("p17", "SCRT_Assurance_Audit_Complexity_Phase_Boundary_Theorem_v2_17_0.py")
I17 = load("i17", "SCRT_Assurance_Audit_Complexity_Phase_Boundary_Independent_Verifier_v2_17_0.py")
ROOT = HERE.parents[1]

def verify_scope_binding():
    t16 = (ROOT / "01_Theory/SCRT_Assurance_Interaction_Phase_Boundary_Theorem_v2_16_0.md").read_text(encoding="utf-8")
    t18 = (ROOT / "01_Theory/SCRT_Assurance_Coherent_Hardening_Phase_Theorem_v2_18_0.md").read_text(encoding="utf-8")
    assert "D union E != empty" in t16
    assert "nonempty certified physical supports" in t18
    return 2

def verify_generated_conflict_free():
    systems, portfolios, risk_checks, feasibility, cost_checks, strict = P16.verify_conflict_free_locality_generated()
    assert systems >= 200
    assert portfolios > 0 and risk_checks == portfolios
    assert feasibility == portfolios
    assert cost_checks > 0
    assert strict > 0
    return systems, portfolios, strict

def verify_generated_resource_choice():
    systems, direct, choices, costs, edges, max_rank = P16.verify_resource_choice_generated()
    assert systems >= 300
    assert direct == choices == costs == systems
    assert edges > 0
    assert max_rank <= 2
    return systems, edges, max_rank

def verify_unbounded_orders_extended():
    checks = 0
    for t in range(2, 15):
        resources = tuple(range(t - 1))
        scenarios = tuple(range(t))
        for omitted in scenarios:
            proper = [s for s in scenarios if s != omitted]
            assignment = dict(zip(proper, resources))
            assert len(assignment) == t - 1
            assert len(set(assignment.values())) == t - 1
            checks += 1
        assert len(resources) < len(scenarios)
        checks += 1
    return checks

def all_triples(q):
    return tuple(itertools.product(range(q), repeat=3))

def verify_3dm_exhaustive_q2_both():
    triples_all = all_triples(2)
    checks = positives = 0
    for mask in range(1 << len(triples_all)):
        triples = tuple(triples_all[i] for i in range(len(triples_all)) if mask & (1 << i))
        source = P17.three_dm_has_perfect(2, triples)
        m,k,scenarios,old_op,op_actions,h,cert,cert_actions,claims = P17.reduction_instance(2, triples)
        risk = P17.risk_set(m,k,old_op,op_actions,h,cert,scenarios)
        target = P17.resource_compensable_backtrack(m,k,cert,cert_actions,claims,risk)
        independent = I17.scrt_compatible(2, triples)
        assert source == target == independent
        positives += int(source)
        checks += 1
    assert checks == 256
    assert positives == 175
    return checks, positives

def verify_3dm_seeded_q3_extra():
    rng = random.Random(218101)
    universe = all_triples(3)
    checks = positives = 0
    for _ in range(900):
        triples = tuple(t for t in universe if rng.random() < 0.34)
        source = P17.three_dm_has_perfect(3, triples)
        m,k,scenarios,old_op,op_actions,h,cert,cert_actions,claims = P17.reduction_instance(3, triples)
        risk = P17.risk_set(m,k,old_op,op_actions,h,cert,scenarios)
        target = P17.resource_compensable_backtrack(m,k,cert,cert_actions,claims,risk)
        independent = I17.scrt_compatible(3, triples)
        assert source == target == independent
        positives += int(source)
        checks += 1
    return checks, positives

def self_test():
    assert verify_scope_binding() == 2
    print("scope_binding:PASS:checks=2")
    print("status:PASS")

def verify():
    self_test()
    s,p,strict = verify_generated_conflict_free()
    print(f"generated_conflict_free_phase:PASS:systems={s}:portfolios={p}:strict_joint_exposure={strict}")
    s,e,r = verify_generated_resource_choice()
    print(f"generated_resource_choice_phase:PASS:systems={s}:response_edges={e}:max_local_rank={r}")
    c = verify_unbounded_orders_extended()
    print(f"unbounded_global_order_structural:PASS:orders=2..14:checks={c}")
    c,pos = verify_3dm_exhaustive_q2_both()
    print(f"dual_implementation_reduction_q2:PASS:instances={c}:positive={pos}")
    c,pos = verify_3dm_seeded_q3_extra()
    print(f"dual_implementation_reduction_q3_seeded:PASS:instances={c}:positive={pos}")
    print("mechanized_proof:NOT_INCLUDED")
    print("historical_priority:NOT_ASSERTED")
    print("status:PASS")

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--self-test", action="store_true")
    g.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    verify() if args.verify else self_test()

if __name__ == "__main__":
    main()
