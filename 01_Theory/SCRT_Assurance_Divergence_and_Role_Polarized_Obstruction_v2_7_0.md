# SCRT Assurance Divergence and Role-Polarized Obstruction v2.7.0

## Operational versus certified survival

SCRT distinguishes

`C_op`

from

`C_cert`.

For target `k`, define

`SilentFail_k = {x : C_op(x)>=k and C_cert(x)<k}`.

Two architectures can have identical current `(C_op,C_cert)` values and different future assurance behavior because certification may be concentrated in different ancestry patterns.

## Role-polarized compromise

Use distinct compromise channels

`F=(F_D,F_E)`.

Certified signature `(D,E)` survives iff

`D intersect F_D = empty`

and

`E intersect F_E = empty`.

Physical independence is still evaluated on underlying support `D union E`, so role separation does not manufacture false independence.

## Polarized blocker theorem

For each certified target-`k` packing `P`, form its doubled-role exposure

`Exp(P)=D(P)_D union E(P)_E`.

Let `B_cert,role,k` be the inclusion-minimal blockers of all certified packing exposures.

The minimal silent-assurance obstruction antichain is the subset of these blockers whose defensive component leaves at least one operational `k`-packing intact.

A polarized compromise causes silent assurance failure exactly when:

- its defensive component contains no operational-collapse blocker; and
- it contains at least one silent-assurance obstruction.

Minimal obstructions decompose into:

`EVIDENCE_ONLY`,

`DEFENSE_ONLY`,

`MIXED`.

For evidence-only attack, `F_D=empty`, so operational capability is untouched by construction.

## Recovery duality

For installed recovery portfolio `H`, let `B_silent,role,k^H` be the remaining minimal silent-obstruction antichain.

For fixed polarized compromise `F`, let `Resp_k(F)` be the minimal recovery portfolios restoring certified target `k`.

Then

`C_cert(X+H,F)>=k`

iff

`no B in B_silent,role,k^H satisfies B subseteq F`

iff

`exists Q in Resp_k(F) with Q subseteq H`.

This gives dual obstruction and response representations of the same assurance relation.
