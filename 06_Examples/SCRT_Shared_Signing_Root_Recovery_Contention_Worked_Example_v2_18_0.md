# SCRT Worked Example — Shared Signing Root, Continued Operation, and Recovery Contention

## Purpose

This example encodes a recognizable class of incident: a shared build/signing
system that many downstream services depend on is compromised, the services keep
running, and incident response must re-establish independent trust for each of
them while the recovery actions compete for a scarce resource.

It is chosen to exercise three SCRT ideas the other examples do not combine:

1. **silent assurance failure at scale** — many services enter a distinct
   assurance state at once without any of them going down;
2. the **exclusive-resource phase** — individually valid recoveries that become
   globally infeasible; and
3. the exact correspondence between that infeasibility and the 3-dimensional
   matching structure used in the
   [complexity phase-boundary theorem](../01_Theory/SCRT_Assurance_Audit_Complexity_Phase_Boundary_Theorem_v2_17_0.md).

The example is illustrative. Every independence, compromise, and recovery
relationship below is a **declared property of this modeled deployment**. Nothing
here is implied automatically by any signing system, CI platform, key-management
product, or standard, and no specific real incident is asserted.

## 1. Deployment

An organization operates a set of production services

`s_1, ..., s_q`

each of which is admitted to production only while it has an independent
certified trust lane. The policy target is one independent certified lane per
service:

`k = 1`.

All services consume artifacts signed through one shared signing system whose
trust roots include per-service evidence ancestry

`e_1, ..., e_q`

and whose operational (serving) ancestry is `d_1, ..., d_q`.

At `t0`, every service is healthy and certified:

`C_op(s_x) = 1` and `C_cert(s_x) = 1` for every `x`.

## 2. The compromise (operation continues)

At `t1` the shared signing system is found to be compromised. The running
replicas keep serving traffic — nothing crashes — so operation is preserved. But
the certified evidence lane of every affected service is no longer admissible.

In the SCRT encoding, the post-compromise scenario for service `x` is the declared
compromise

`F_x = (F_D, F_E)`

that leaves `s_x` operationally survivable while invalidating every certified lane
except the one that a valid recovery would rebuild. Concretely, following the
construction in the complexity theorem, `F_x` compromises every defensive
coordinate except `d_x` and every evidence coordinate except `e_x`.

For every service:

`C_op(s_x) >= k` and `C_cert(s_x) < k`.

Every service is now in **silent assurance failure** simultaneously. The
hardening-induced assurance-risk family is the whole fleet:

`Risk_1 = { F_1, ..., F_q }`.

## 3. Recovery, and why it contends

Incident response must give each service a fresh, independently rooted certified
lane — a `ROTATE_AND_REATTEST` action that re-issues that service's evidence from
a clean root. The catalogue of admissible recovery actions is

`a_t` for each `t = (x, y, z)`

where:

- `x` is the service the action re-certifies (its route survives `F_x` and no
  other `F_{x'}`);
- `y` is an **exclusive offline-root ceremony slot** the action must hold; and
- `z` is an **exclusive approver-quorum window** the action must hold.

Each recovery action therefore claims exactly two exclusive resources, `y` and
`z`. Two recovery actions can run in the same response only if they need neither
the same ceremony slot nor the same approver window:

`a_t and a_{t'} are compatible  iff  y != y'  and  z != z'`.

This is the operational reality behind the abstraction: an offline root-key
ceremony and a quorum of trusted approvers are genuinely scarce and cannot be run
in two places at once during a single response window.

## 4. The exact obstruction

The incident is resolvable — every silently-failing service can be given back an
independent certified lane within the response window — **exactly when** the
recovery catalogue contains a selection

`{ a_{t_1}, ..., a_{t_q} }`

with

- one action per service `x` (so every `F_x` is compensated), and
- pairwise-distinct ceremony slots `y` and pairwise-distinct approver windows `z`
  (so the selection is resource-feasible).

That is precisely a **perfect 3-dimensional matching** on the triple set
`{ (x, y, z) }`. So for this modeled deployment:

`incident is recoverable within the window`

iff

`the recovery catalogue admits a perfect 3-dimensional matching`.

By the complexity phase-boundary theorem, deciding this is **NP-complete already at
`k = 1`**, even though:

- every service's silent failure is activated by one operational fact
  (`operational activation rank = 1`); and
- every service's repair is a single recovery action
  (`certified response rank = 1`).

The difficulty is not local. Each service, taken alone, is trivially recoverable.
The hardness is entirely in the **cross-service contention** for the exclusive
ceremony and approver resources.

## 5. A concrete small instance

Take `q = 2` services and a recovery catalogue (reading `y in {a, b}` as the
ceremony slot and `z in {p, q}` as the approver window)

`T = { (1, a, p), (2, b, q), (1, b, q), (2, a, p) }`.

- Selecting `(1, a, p)` and `(2, b, q)` covers both services with distinct slots
  (`a`, `b`) and distinct windows (`p`, `q`) — a resource-feasible response. The
  incident is recoverable.
- Now suppose only `T' = { (1, a, p), (2, a, q) }` is available. Both remaining
  actions need ceremony slot `a`, so at most one can run in the window. Each
  service is individually recoverable — service 1 by `(1, a, p)`, service 2 by
  `(2, a, q)` — yet the two cannot run together, so **the incident is not
  recoverable within one window** even though every local rank is 1.

Both outcomes were confirmed against the verifier below (mapping
`a,p -> 0` and `b,q -> 1`, services `0`-indexed): `T` gives
`3DM_perfect_matching = True` and `SCRT_compatible = True`; `T'` gives `False` and
`False`.

This matches the exhaustive `q = 2` cross-check in
[`SCRT_Assurance_Audit_Complexity_Phase_Boundary_Independent_Verifier_v2_17_0.py`](../03_Verification/Hardening_Phase/SCRT_Assurance_Audit_Complexity_Phase_Boundary_Independent_Verifier_v2_17_0.py):
the SCRT compatibility decision agrees with the 3-dimensional matching decision on
every sub-catalogue.

## 6. What the example demonstrates

First, a single shared trust root can put an entire fleet into silent assurance
failure at once, with zero availability impact — the failure is in the certified
lane, not the serving path.

Second, recovery cost is not additive across services when recovery resources are
exclusive. `q` services that are each one action away from recovery can still be
collectively unrecoverable inside one response window.

Third, the model exposes a design implication: **where feasible, reducing
contention among assurance-recovery resources can move the declared architecture
toward the conflict-free regime.** Independent per-service ceremony capacity and
non-contended approval paths remove the specific cross-service resource conflicts
responsible for the exclusive-resource obstruction; under the corresponding
conflict-free SCRT contract, fixed-target assurance auditability is polynomial.

## 7. What the example does not establish

This example does not establish:

- that any particular real signing system or incident has this structure;
- that the declared per-service ancestry is independent in any real deployment;
- that the ceremony slot and approver window are the only real recovery
  constraints, or that two per action is the real number;
- that the target `k = 1` is an appropriate organizational policy;
- that the registered recovery catalogue exhausts real response options; or
- that operational survival implies the artifacts or provenance were authentic.

Those remain external validation obligations under the
[Cyber Architecture Encoding Contract](../01_Theory/SCRT_Cyber_Architecture_Encoding_Contract_v2_18_0.md)
and the
[Threat Model and Assumption Boundary](../01_Theory/SCRT_Threat_Model_and_Assumption_Boundary_v2_18_0.md).

## 8. Generic implementation context

The pattern can be instantiated with common mechanisms such as offline root-key
ceremonies, hardware security modules, approver quorums, signing transparency
records, and per-service re-attestation. Specific products or standards are
illustrative implementation contexts rather than mathematical dependencies of
SCRT.
