# Shunyaya Cyber Resilience Theory (SCRT)

## Exact assurance semantics and hardening-phase mathematics for cyber resilience

> **When operation survives, what still justifies trust?**

**Shunyaya Cyber Resilience Theory (SCRT) v2.18.0** develops an exact finite mathematical theory for cyber resilience under shared dependency ancestry, compromise, hardening, recovery, evidence loss, resource constraints, adversarial action, and future continuation.

Its central cyber distinction separates **operational capacity** from **independently certified capacity**. For target `k`,

`C_op >= k and C_cert < k`

is **silent assurance failure**: operation remains at target while the declared independent basis for trusting that operation has fallen below target.

The principal v2.18 result identifies an exact assurance-hardening phase boundary: target `k` bounds local operational activation and local certified response structure, yet exclusive certified-resource conflicts can create globally unbounded assurance incompatibility and an exact fixed-target transition from polynomial auditability to NP-complete compatibility.

### Security-reader summary

SCRT asks whether a hardened system can keep operating after the independent basis for trusting that operation has fallen below target. It models that gap explicitly, proves that operational hardening can enlarge the corresponding silent-assurance region, and characterizes the certified compensation needed to close it. The v2.18 phase theorem then separates target-bounded **local** resilience structure from **global** assurance compatibility: conflict-free recovery remains target-local, while exclusive recovery resources can create unbounded cross-scenario incompatibility even at `k=1`.

[![Version](https://img.shields.io/badge/Version-2.18.0-blue)](./VERSION)
[![Theorem chain](https://img.shields.io/badge/Theorem%20chain-frozen%20v2.18.0-brightgreen)](./04_Research_Context/SCRT_Theorem_Status_v2_18_0.md)
[![Hardening phase](https://img.shields.io/badge/Hardening%20phase-k--local%20%7C%20resource--global-brightgreen)](./01_Theory/SCRT_Assurance_Coherent_Hardening_Phase_Theorem_v2_18_0.md)
[![Complexity boundary](https://img.shields.io/badge/Complexity-fixed--k%20P%20%7C%20NP--complete-blue)](./01_Theory/SCRT_Assurance_Audit_Complexity_Phase_Boundary_Theorem_v2_17_0.md)
[![Proof](https://img.shields.io/badge/Proof-written%20complete%20%C2%B7%20not%20mechanized-orange)](./01_Theory/SCRT_Proof_Architecture_v2_18_0.md)
[![Generated falsification](https://img.shields.io/badge/Generated%20falsification-PASS-brightgreen)](./05_Reproduction_and_Verification/SCRT_Verification_Evidence_Report_v2_18_0.md)
[![Independent implementations](https://img.shields.io/badge/Independent%20implementations-PASS-brightgreen)](./03_Verification/README.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](./05_Reproduction_and_Verification/SCRT_Verification_Guide_v2_18_0.md)
[![Dependencies](https://img.shields.io/badge/Runtime-standard%20library%20only-blue)](./05_Reproduction_and_Verification/SCRT_Verification_Guide_v2_18_0.md)
[![Citation](https://img.shields.io/badge/Citation-CFF-blue)](./CITATION.cff)
[![License](https://img.shields.io/badge/License-Apache--2.0%20%7C%20CC%20BY--NC%204.0-blue)](./LICENSE)

[![Verify](https://github.com/OMPSHUNYAYA/Shunyaya-Cyber-Resilience-Theory/actions/workflows/verify.yml/badge.svg)](https://github.com/OMPSHUNYAYA/Shunyaya-Cyber-Resilience-Theory/actions/workflows/verify.yml)

[Theory at a glance](./01_Theory/SCRT_Theory_at_a_Glance_v2_18_0.md) · [Framework overview](./01_Theory/SCRT_Framework_Overview_v2_18_0.md) · [Principal hardening theorem](./01_Theory/SCRT_Assurance_Coherent_Hardening_Phase_Theorem_v2_18_0.md) · [Encoding contract](./01_Theory/SCRT_Cyber_Architecture_Encoding_Contract_v2_18_0.md) · [Worked encodings](./06_Examples/) · [Claim boundary](./04_Research_Context/SCRT_Claim_Boundary_v2_18_0.md) · [Verification evidence](./05_Reproduction_and_Verification/SCRT_Verification_Evidence_Report_v2_18_0.md)

---

## Principal assurance-hardening phase theorem

Operational hardening can make additional compromise states survivable without restoring the independent certified basis required to trust those states. SCRT makes this exposure exact and characterizes the compensation required to prevent it.

With certification fixed,

`S_k(O,C) subseteq S_k(O+,C)`.

For target `k`:

`operational activation rank <= k`

and

`local certified response rank <= k`.

These local bounds lead to two fundamentally different global regimes.

| Certified-resource contract | Local structure | Global assurance audit | Fixed-target explicit decision |
|---|---|---|---|
| **Conflict-free** | activation rank `<= k`; response rank `<= k` | audit order exactly `k` in the worst case | polynomial time |
| **Exclusive-resource** | activation rank `<= k`; response rank `<= k` | no audit cutoff determined only by `k` | NP-complete already at `k=1` |

The exclusive-resource phase persists even when every operational activation and every local certified response is a singleton. The nonlocality is therefore caused by **cross-scenario compatibility of assurance resources**, not by larger local target witnesses.

The phase boundary separates **local resilience structure** from **global assurance compatibility**: the difficult regime is created by competition among the resources required to re-establish independent trust across simultaneously survivable scenarios.

[Integrated phase theorem](./01_Theory/SCRT_Assurance_Coherent_Hardening_Phase_Theorem_v2_18_0.md) · [Universal assurance-coherent hardening theorem](./01_Theory/SCRT_Universal_Assurance_Coherent_Hardening_Theorem_v2_10_0.md) · [Interaction phase boundary](./01_Theory/SCRT_Assurance_Interaction_Phase_Boundary_Theorem_v2_16_0.md) · [Complexity phase boundary](./01_Theory/SCRT_Assurance_Audit_Complexity_Phase_Boundary_Theorem_v2_17_0.md) · [Proof and scope audit](./01_Theory/SCRT_Assurance_Hardening_Proof_and_Scope_Audit_v2_18_0.md)

---

## Assurance exposure and compensation

For target `k`, SCRT separates:

`C_op` = operational defensive capacity,

`C_cert` = independently certified defensive capacity.

An operational hardening may enlarge the set of silent-assurance states. Under baseline target-operational sufficiency, operational-only hardening leaves evidence-only silent-assurance judgments invariant; newly activated silent states necessarily involve defensive compromise.

Certified hardening can only contract the silent-assurance region. SCRT defines the **Assurance Compensation Cost** `ACI_k` as the minimum registered certified-action cost required to make an operational hardening assurance-coherent.

Under the declared semantics:

`stronger operational hardening -> ACI cannot decrease`

`larger certified-action library -> ACI cannot increase`

`higher certified-action costs -> ACI cannot decrease`

`stronger baseline certification -> ACI cannot increase`.

---

## Continuation-classification foundation

The assurance-hardening phase sits on the broader SCRT continuation framework.

For a declared continuation contract `C=(S,G,O)`, states are contextually equivalent when every admitted finite continuation gives the same declared observation. The minimum sufficient state is contract-relative: strengthening future operations or observers can strictly refine the canonical state.

SCRT separates three exact semantic levels:

`exact structural semantics -> finite-dimensional multiplicity-sensitive kernels`

`target-k semantics -> sharp finite target-saturated quotient`

`campaign semantics -> minimal residual right congruence for the registered campaign observer`.

[Continuation classification](./01_Theory/SCRT_Integrated_Universal_Assurance_Continuation_Classification_v2_7_0.md) · [Target-relative strategy theorem](./01_Theory/SCRT_Target_Relative_Strategy_Theorem_v2_7_0.md) · [Campaign residual theorem](./01_Theory/SCRT_Campaign_Residual_Theorem_v2_7_0.md)

---

## Why the phase boundary matters

Adding operational redundancy can improve availability without improving the independent evidence needed to trust the resulting operation.

For target `k`, newly operationally survivable scenarios have activating hardening witnesses of size at most `k`; individual certified restorations likewise need at most `k` actions. If certified actions compose freely, successful local responses can be united and order `k` is globally sufficient. If certified actions compete for exclusive resources, individually valid responses may become globally incompatible. That obstruction can involve arbitrarily many scenarios even when `k=1`.

SCRT therefore separates:

`local resilience structure`

from

`global assurance compatibility`.

---

## Verification evidence — deliberately separated

SCRT does **not** use repository-integrity counts as theorem-verification counts.

### Repository integrity

The root self-test checks required files, cryptographic binding of the frozen computational/machine-readable core, machine-readable theorem records, README links, UTF-8/LF normalization, and repository hygiene.

Editable scientific presentation files—including README, theorem/proof Markdown, examples, licenses, notices, workflows, and verification guides—are intentionally **not** part of the frozen SHA-256 identity.

### Executable mathematical falsification

Generated verification includes:

- `5,898` exhaustively enumerated small deterministic transition systems;
- `1,500` seeded larger transition systems;
- `4,096` complete two-ancestry role-polarized cyber architectures;
- `65,536` silent-assurance membership checks;
- `32,640` generated recovery-duality checks;
- additional generated conflict-free and exclusive-resource phase checks;
- exhaustive reduction replay over all `256` source instances in the smallest complete reduction universe; and
- independent replay on separately implemented solvers.

These are finite falsification surfaces and cross-implementation evidence. They do not establish universal quantifiers by themselves.

### Written proofs

The universal statements are supplied by written proofs under explicit hypotheses.

`proof_status: WRITTEN_COMPLETE_NOT_MECHANIZED`

`mechanized_proofs: NONE`.

Run from the repository root:

```bash
python -B verify.py --self-test
python -B verify.py --verify
```

[Verification evidence report](./05_Reproduction_and_Verification/SCRT_Verification_Evidence_Report_v2_18_0.md) · [Verification guide](./05_Reproduction_and_Verification/SCRT_Verification_Guide_v2_18_0.md) · [Verification scope](./05_Reproduction_and_Verification/SCRT_Verification_Scope_v2_18_0.md) · [Repository verification record](./05_Reproduction_and_Verification/SCRT_Package_Verification_v2_18_0.txt)

---

## Modeling contract and threat boundary

SCRT separates **modeling** from **classification**:

`cyber architecture -> declared SCRT encoding -> mathematical classification`.

The encoding declares obligations, operational and certified routes, ancestry, compromise channels, hardening/recovery actions, resource conflicts, targets, scenarios, continuation rules, and observers. The theorem classifies that declared finite object.

An SCRT result does not by itself establish that a deployed system has been encoded completely, that evidence is authentic, that a declared ancestry independence is operationally valid, or that the registered adversary grammar exhausts reality.

[Cyber Architecture Encoding Contract](./01_Theory/SCRT_Cyber_Architecture_Encoding_Contract_v2_18_0.md) · [Threat Model and Assumption Boundary](./01_Theory/SCRT_Threat_Model_and_Assumption_Boundary_v2_18_0.md) · [Claim Boundary](./04_Research_Context/SCRT_Claim_Boundary_v2_18_0.md)

---

## Structural lineage

SCRT extends the continuation-semantics line developed in **[Shunyaya Theorem Reproducibility Framework (STRF)](https://github.com/OMPSHUNYAYA/Shunyaya-Theorem-Reproducibility-Framework)** into independently derived cybersecurity semantics.

**STRF:**

`theorem reconstruction -> ancestry -> failure-adaptive rebuilding -> canonical continuation`

**SCRT:**

`security obligations -> defensive/evidence routes -> operational/certified capacity -> assurance divergence -> adversarial campaigns -> assurance-coherent hardening -> phase-boundary classification`.

STRF provides structural lineage and project context rather than proof input for SCRT.

---

## Mathematical positioning

SCRT uses established mathematical structures where appropriate, including finite reliability and packing models, behavioral equivalence, right congruences, finite residual minimization, saturation, blocker/covering duality, fixed-point reasoning, matching and resource-compatible selection, finite optimization, and complexity reductions. **No novelty is claimed for these general tools individually.**

SCRT's mathematical contribution is the exact cyber-resilience semantics built from the operational/certified distinction and the integrated theorem structure that follows from it: silent-assurance obstruction, assurance-coherent hardening, minimum certified compensation, target-bounded local activation and response, and the resulting resource-dependent local/global phase boundary.

In particular, the significance of the complexity result is not the reduction technique in isolation. It is the structural transition within one assurance model: conflict-free certified recovery admits a target-bounded global audit, whereas exclusive recovery resources destroy every audit bound depending only on the target and yield NP-complete assurance compatibility already at `k=1`, even though both local activation and local certified response remain singleton-bounded.

The repository therefore distinguishes between **established mathematical machinery** and the **SCRT-specific theorem structure induced by the declared cyber semantics**. No claim of historical priority is made.

[Research positioning](./04_Research_Context/SCRT_Research_Positioning_v2_18_0.md) · [Relationship to established structures](./04_Research_Context/SCRT_Relationship_to_Established_Structures_v2_18_0.md) · [Comparison categories](./04_Research_Context/SCRT_Comparison_Categories_v2_18_0.json) · [Theorem status](./04_Research_Context/SCRT_Theorem_Status_v2_18_0.md)

---

## Worked encodings

[Examples index](./06_Examples/README.md)

- [Shared signing-root recovery-contention example](./06_Examples/SCRT_Shared_Signing_Root_Recovery_Contention_Worked_Example_v2_18_0.md) — a fleet continues operating after a declared trust-root compromise while certified recovery actions compete for exclusive ceremony and approval resources.
- [Supply-chain assurance example](./06_Examples/SCRT_Realistic_Supply_Chain_Assurance_Worked_Example_v2_18_0.md) — operation continues while an evidence root becomes untrusted; declared independence and recovery assumptions are explicit.
- [Exclusive recovery-resource example](./06_Examples/SCRT_Exclusive_Recovery_Resource_Worked_Example_v2_18_0.md) — singleton local restorations become globally incompatible because of declared exclusive recovery resources.
- [Evidence-only silent-assurance example](./06_Examples/SCRT_Evidence_Only_Silent_Assurance_Example_v2_7_0.md).
- [Campaign residual example](./06_Examples/SCRT_Campaign_Residual_Example_v2_7_0.md).

---

## Repository map

| Area | Contents |
|---|---|
| [`01_Theory/`](./01_Theory/) | theory-at-a-glance, definitions, encoding/threat contracts, continuation theorems, hardening phase theorem, written proofs and scope audits |
| [`02_Algorithms_and_Software/`](./02_Algorithms_and_Software/) | compact canonical-quotient reference algorithms |
| [`03_Verification/`](./03_Verification/) | historical regression, generated falsification, adversarial verification, current principal/independent hardening-phase verifiers |
| [`04_Research_Context/`](./04_Research_Context/) | claim boundary, theorem status, dependency map, computational envelope, and category-level mathematical positioning |
| [`05_Reproduction_and_Verification/`](./05_Reproduction_and_Verification/) | verification evidence/guide, theorem record, metrics, integrity and binding records |
| [`06_Examples/`](./06_Examples/) | worked assurance, campaign, and resource-compatibility encodings |
| [`.github/workflows/`](./.github/workflows/) | automated repository verification |
| [`LICENSES/`](./LICENSES/) | complete local license texts |
| [`CITATION.cff`](./CITATION.cff) | repository citation metadata |

---

## Cryptographic integrity scope

The frozen **computational and machine-readable theorem core** is SHA-256 bound.

The editable scientific presentation layer is intentionally outside that identity. This includes README material, theorem/proof Markdown, encoding/threat-model prose, research-context prose, examples, citation metadata, licenses, notices, workflow files, verification guides, and package manifests.

This permits scientific exposition, navigation, and clarification to improve without silently changing the bound computation.

[Integrity scope policy](./05_Reproduction_and_Verification/SCRT_Cryptographic_Integrity_Scope_Policy_v2_18_0.md)

---

## Citation

Repository citation metadata is provided in [`CITATION.cff`](./CITATION.cff).

---

## License and rights

Software, verification code, workflows, and machine-readable scientific artifacts are provided under **Apache License 2.0**. Project-authored theorem exposition, proof documentation, README material, examples, and research-context writing are provided under **CC BY-NC 4.0**.

[License map](./LICENSE) · [Copyright notice](./COPYRIGHT_NOTICE.txt) · [Notices](./THIRD_PARTY_NOTICES.txt)

---

## Closing note

SCRT treats resilience and assurance as related but distinct mathematical obligations. Its central design question is not only whether a hardened system can keep operating, but whether the independent basis for trusting that operation remains sufficient under the same adversarial future.

The framework makes that distinction explicit through exact obstruction, compensation, continuation, interaction, and complexity structure under declared cyber semantics.
