# SCRT Assumption Sharpness Audit v2.18.0

This audit records small countermodels showing why several hypotheses in the v2.18 theorem chain are explicit.

- **Baseline target-operational sufficiency** is necessary for evidence-only invariance: if the baseline is below target, operational hardening can create a new evidence-only silent-assurance state.
- **Additive operational hardening** is necessary for silent-set monotonicity: a replacement operation that deletes old routes can remove old operational survivability.
- **Additive certified hardening** is necessary for certified-hardening contraction: a transformation that deletes certification routes can create silent states.
- **Hereditary resource feasibility** is necessary for the local certified-response rank proof: a non-hereditary admissibility rule can force a minimal admissible response larger than `k` even when one action supplies the target route.
- **Conflict-free composition** is necessary for the order-`k` global audit lift: exclusive resource conflicts can make individually compensable local responses globally incompatible.
- **Strictly positive nonempty-portfolio cost** is necessary if `ACI_k=0` is interpreted as “no compensating action is required”; zero-cost nonempty responses are otherwise possible.
- **Exact gain identity** cannot generally be compressed to gain cardinality: equal-size gain sets may be distinguished by future scenario-specific queries.

The executable countermodel audit is under `03_Verification/Generated/`.

These countermodels delimit theorem scope; they do not weaken the results inside the stated hypotheses.
