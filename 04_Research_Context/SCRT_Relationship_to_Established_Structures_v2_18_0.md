# SCRT Relationship to Established Structures v2.18.0

This document positions SCRT at the level of mathematical and cybersecurity categories. It is intentionally non-bibliographic and makes no claim of historical priority.

## Established mathematical structures used as tools

SCRT uses several established structures where they fit the declared cyber semantics. None is presented as an SCRT invention in isolation:

- **finite reliability and bounded witness structure** for target-relative survivability;
- **behavioral equivalence and right congruences** for continuation classification;
- **finite residual minimization and partition refinement** for canonical state compression;
- **packing, covering, and blocker duality** for survivability and obstruction;
- **matching and resource-compatible selection** for exclusive certified-resource constraints;
- **finite optimization and Pareto-style minimization** for compensation cost;
- **fixed-point reasoning** for target-relative strategy semantics; and
- **complexity classification and polynomial reduction** for the computational phase boundary.

On the cybersecurity side, SCRT is compatible with established categories including assurance and evidence-based confidence, resilience and hardening, recovery planning, shared dependency ancestry, and trust/provenance concerns.

## SCRT-specific theorem structure

SCRT's mathematical content is the integrated structure induced by its declared operational/certified semantics:

1. **Operational/certified separation.** `C_op` and `C_cert` are distinct target-relative quantities, and `C_op >= k` with `C_cert < k` defines silent assurance failure.

2. **Assurance exposure under hardening.** Operational-only hardening can enlarge the silent-assurance region, while certified hardening contracts it. `ACI_k` gives the exact minimum registered certified compensation required for assurance coherence.

3. **Target-bounded local structure.** Operational activation witnesses and individual certified responses have rank at most `k`.

4. **Resource-dependent global phase boundary.** Conflict-free certified resources lift local target bounds to a global audit order `k`; exclusive certified resources can produce globally unbounded assurance incompatibility even at `k=1`, without increasing local witness rank.

5. **Computational phase boundary.** For fixed `k` on explicit finite inputs, the conflict-free assurance audit is polynomial-time, whereas exclusive-resource assurance compatibility is NP-complete already at `k=1` under the stated restricted construction.

6. **Continuation and campaign classification.** SCRT places these assurance results inside a contract-relative continuation semantics with exact structural, target-relative, and campaign-residual levels.

## Comparison boundary

The repository does not claim invention of the general mathematical or cybersecurity categories listed above. Its scientific claim is the SCRT-specific semantic construction and the theorem chain proved within that construction.

No claim of historical priority is made.
