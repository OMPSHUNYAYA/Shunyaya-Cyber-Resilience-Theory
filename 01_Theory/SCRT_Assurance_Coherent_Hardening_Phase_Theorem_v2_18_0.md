# SCRT Assurance-Coherent Hardening Phase Theorem v2.18.0

## 1. Status

`theorem_status: INTEGRATED_WRITTEN_THEOREM_CHAIN`

`component_proofs: v2.10 + v2.16 + v2.17`

No claim of historical priority is made.

This theorem binds the assurance-hardening results into one scope-controlled statement. No new mathematical mechanism is introduced at v2.18.0.

---

## 2. Scope

The theorem concerns finite SCRT architectures with:

- nonempty operational routes and nonempty certified physical supports;
- ancestry-independent operational and certified route packings;
- target `k>=1`;
- role-polarized defensive/evidence compromise;
- additive operational hardening;
- additive certified compensation;
- an explicitly declared finite compromise-scenario family; and
- either conflict-free or exclusive-resource certified-action composition.

The exact hypotheses and proofs are supplied in the bound v2.10, v2.16, and v2.17 theorem documents.

---

## 3. Integrated phase theorem

For the frozen semantics, operational hardening and assurance compensation separate into the following exact structural regimes.

### Phase A — Assurance exposure

Operational-only hardening is monotone in operational survivability and can strictly enlarge the silent-assurance region:

`S_k(O,C) subseteq S_k(O+,C)`.

If the baseline is already operational at target `k`, operational-only hardening leaves evidence-only silent-assurance judgments invariant; newly activated silent states necessarily contain defensive compromise.

A newly activated silent state has an exact operational-packing / certified-blocker witness.

### Phase B — Assurance coherence and compensation

Certified hardening can only contract the silent-assurance region.

An operational hardening is assurance-coherent exactly when every newly operationally survivable declared compromise is certified target-safe after the selected compensation.

The Assurance Compensation Cost `ACI_k` is the exact minimum registered certified-action cost required to achieve coherence.

It obeys the monotonicities proved in v2.10:

`stronger operational hardening -> ACI cannot decrease`

`larger certified-action library -> ACI cannot increase`

`higher certified-action costs -> ACI cannot decrease`

`stronger baseline certification -> ACI cannot increase`.

### Phase C — Target-bounded local interaction

Every newly operationally survivable scenario has an activating hardening subportfolio of size at most `k`:

`Gain_k(H) = union_{J subseteq H, |J|<=k} Gain_k(J)`.

Every inclusion-minimal successful certified response, including under exclusive-resource constraints, has size at most `k`.

Both bounds are sharp.

### Phase D — Conflict-free global lift

When certified actions are freely composable, the target-bounded local structure lifts to a complete global audit:

`H is assurance-compensable`

iff

`every J subseteq H with |J|<=k is assurance-compensable`.

The universal audit order is exactly `k` in the worst case.

For every fixed `k` and explicit finite scenario/action representation, the exact assurance-compensability decision is polynomial-time computable.

### Phase E — Exclusive-resource global nonlocality

When certified actions carry mutually exclusive resource claims, the local rank bounds remain unchanged:

`operational activation rank <= k`

`local certified response rank <= k`.

Nevertheless, no global hardening-audit order determined only by `k` exists.

Already at `k=1`, for every `t>=2` there are `t` operational hardening actions such that every proper hardening subportfolio is assurance-compensable while the full `t`-action portfolio is not.

The exact global criterion is a compatible selection of one minimal certified response per triggered assurance-risk scenario.

### Phase F — Computational transition

For fixed `k` and explicit finite inputs:

`conflict-free compensation -> assurance-compensability is in P`.

With exclusive certified resources:

`assurance-compensability is NP-complete already at k=1`,

and the hardness persists when:

- every operational activation is singleton;
- every certified local response is singleton;
- every certified action supplies one route; and
- every certified action claims exactly two resources.

Thus the computational transition is caused by global resource compatibility rather than by large local target witnesses.

---

## 4. Phase diagram

The theorem chain can be summarized as:

`operational hardening`

`-> newly survivable compromise region`

`-> possible silent-assurance exposure`

`-> exact assurance compensation requirement`.

Then the compensation contract determines the phase:

### Conflict-free certified resources

`local order <= k`

`-> global audit order = k`

`-> fixed-k explicit decision in P`.

### Exclusive certified resources

`local order <= k`

but

`global audit order unbounded by k`

and

`decision NP-complete already at k=1`.

---

## 5. Why the phase boundary is not a contradiction

The target `k` controls how many route-providing actions are needed to witness one operational activation or one local certified restoration.

It does not control how many distinct assurance-risk scenarios must be restored simultaneously.

Under conflict-free compensation, successful local responses can be unioned, so local target structure lifts to global structure.

Under exclusive resources, individually valid responses may compete. The obstruction therefore lives in cross-scenario compatibility rather than in any one target packing.

This explains how both local ranks can remain `1` while global obstruction order and computational difficulty become unbounded.

---

## 6. Mathematical dependency

The integrated theorem depends on:

1. `SCRT Universal Assurance-Coherent Hardening Theorem v2.10.0` — exposure, evidence-only invariance, compensation duality, and `ACI_k` monotonicity.
2. `SCRT Assurance Interaction Phase-Boundary Theorem v2.16.0` — bounded local ranks, conflict-free order-`k` audit, exact resource-compatible response selection, and unbounded global resource obstruction.
3. `SCRT Assurance Audit Complexity Phase-Boundary Theorem v2.17.0` — fixed-target conflict-free polynomial tractability and exclusive-resource NP-completeness at target `1`.

Each component contains its own universal proof and separate finite falsification implementation.

---

## 7. Claim boundary

The integrated theorem does not claim novelty for:

- security assurance as a general concept;
- redundancy or `k`-out-of-`n` reliability;
- hardening optimization;
- matching or resource allocation;
- Pareto optimization;
- NP-completeness techniques; or
- fixed-target enumeration.

The SCRT-specific contribution is the integrated cyber-resilience phase structure under the declared semantics: operational hardening can create assurance exposure; target `k` bounds local activation and response structure; conflict-free compensation lifts that locality globally; exclusive certified resources destroy the global bound without changing local ranks; and the same semantic transition separates polynomial fixed-target auditability from NP-complete global compatibility.

No claim of historical priority is made.
