# SCRT Assurance Interaction Phase-Boundary Theorem v2.16.0

## 1. Status

`theorem_status: WRITTEN_UNIVERSAL_PROOF`

`verification_status: PRINCIPAL_AND_INDEPENDENT_FINITE_FALSIFICATION_PASS`

No claim of historical priority is made.

This document states and proves the theorem for the frozen v2.16 semantics. The accompanying programs provide finite falsification and boundary verification; they are not proof assistants.

---

## 2. Frozen semantics

Let `V` be a finite ancestry universe and let `k>=1` be the resilience target.

An operational route is a nonempty subset of `V`.

A certified route is a typed pair `(D,E)` with `D,E subseteq V`, `D intersect E=empty`, and `D union E != empty`. Its physical ancestry support is `D union E`.

A role-polarized compromise is `F=(F_D,F_E)`.

An operational route `S` survives `F` exactly when

`S intersect F_D = empty`.

A certified route `(D,E)` survives `F` exactly when

`D intersect F_D = empty`

and

`E intersect F_E = empty`.

A family of surviving routes supplies target `k` when it contains `k` routes whose physical ancestry supports are pairwise disjoint.

Let `O` be the baseline operational route family and `C` the baseline certified route family.

Operational hardening actions are additive: each action supplies a finite family of operational routes. For a hardening portfolio `H`, write `O_H` for the union of `O` with all operational routes supplied by actions in `H`.

Certified compensation actions are additive: each action supplies a finite family of certified routes. For a certified portfolio `Q`, write `C_Q` for the union of `C` with all certified routes supplied by actions in `Q`.

Let `S` be a finite declared compromise-scenario family.

Define the newly operationally survivable scenario set

`Gain_k(H) = {F in S : C_op(O,F)<k and C_op(O_H,F)>=k}`.

Define the hardening-induced silent-assurance risk set

`Risk_k(H) = {F in Gain_k(H) : C_cert(C,F)<k}`.

Thus `Risk_k(H)` contains exactly the declared compromises that become operationally survivable because of `H` while the unchanged certified layer remains below target.

Two certified-action contracts are considered.

### Conflict-free compensation

Every finite union of certified actions is admissible.

### Exclusive-resource compensation

Each certified action `a` has a finite resource claim `rho(a)`. A portfolio is admissible exactly when no resource is claimed by two distinct selected actions. Feasibility is therefore hereditary under taking subportfolios.

For a scenario `F`, `Resp_k(F)` denotes the inclusion-minimal admissible certified portfolios that restore certified target `k` at `F`.

---

## 3. The phase-boundary theorem

### Theorem 1 — Operational activation rank

For every operational hardening portfolio `H`,

`Gain_k(H) = union_{J subseteq H, |J|<=k} Gain_k(J)`.

Consequently every inclusion-minimal operational activator has size at most `k`.

The bound is sharp for every `k>=1`.

### Theorem 2 — Risk rank

Because the certified baseline is fixed while operational hardening is chosen,

`Risk_k(H) = union_{J subseteq H, |J|<=k} Risk_k(J)`.

### Theorem 3 — Local certified-response rank, including exclusive resources

For every scenario `F`, every inclusion-minimal admissible certified response satisfies

`Q in Resp_k(F) => |Q|<=k`.

This remains true under exclusive-resource constraints.

The bound is sharp for every `k>=1`.

### Theorem 4 — Conflict-free universal assurance audit

Under conflict-free compensation, for every hardening portfolio `H`,

`Risk_k(H) is compensable`

iff

`Risk_k(J) is compensable for every J subseteq H with |J|<=k`.

Therefore a complete assurance-compensability audit of an arbitrary finite hardening library needs only hardening subportfolios of order at most `k`.

No smaller universal order than `k` suffices.

### Theorem 5 — Exact resource-compatible response criterion

Under exclusive-resource compensation, a finite risk family `R` is jointly compensable iff there exists a choice

`Q_F in Resp_k(F)` for every `F in R`

such that

`union_{F in R} Q_F`

is resource-feasible.

For nonnegative action costs `c`, the exact minimum compensation cost is

`min c(union_F Q_F)`

over all such resource-compatible choices.

### Theorem 6 — Unbounded global audit order under exclusive resources

Under exclusive-resource compensation there is no universal hardening-audit order determined only by target `k`.

More strongly, already for `k=1`, for every integer `t>=2` there exists a finite SCRT instance with `t` operational hardening actions such that

`every proper hardening subportfolio is assurance-compensable`

but

`the full t-action hardening portfolio is not assurance-compensable`.

In the same instance:

`every minimal operational activation witness has size 1`

and

`every minimal certified response has size 1`.

Hence the obstruction is purely global resource incompatibility.

### Corollary — Assurance interaction phase boundary

The frozen SCRT semantics has the exact phase boundary

`conflict-free certified compensation -> universal audit order exactly k`

while

`exclusive certified resources -> no universal audit order bounded by k`.

At the same time, both local structural ranks remain target-bounded:

`operational activation rank <= k`

and

`certified response rank <= k`.

---

## 4. Proof of Theorem 1

Take `F in Gain_k(H)`.

By definition, baseline `O` does not supply an operational `k`-packing at `F`, while `O_H` does. Choose one surviving operational `k`-packing `P` in `O_H`.

For every route of `P` that is not already available from `O`, choose one hardening action in `H` that supplies that route. Let `J` be the set of chosen actions.

The packing has exactly `k` routes, so

`|J|<=k`.

Every route of `P` is present in `O_J`, hence `O_J` supplies target `k` at `F`. The baseline still does not. Therefore

`F in Gain_k(J)`.

Thus

`Gain_k(H) subseteq union_{J subseteq H, |J|<=k} Gain_k(J)`.

The reverse inclusion follows from monotonicity of additive operational hardening: if `J subseteq H`, every route available under `J` is also available under `H`.

Therefore equality holds.

For sharpness, take baseline `O=empty`, one declared compromise that removes none of `k` pairwise-disjoint ancestry coordinates, and `k` hardening actions each supplying exactly one of those `k` singleton operational routes. The target is reached only when all `k` actions are selected. Hence no universal order below `k` suffices.

---

## 5. Proof of Theorem 2

For fixed `C`, whether `C_cert(C,F)<k` depends only on `F` and the certified baseline, not on operational hardening `H`.

Therefore

`Risk_k(H) = Gain_k(H) intersect BadCert_k(C)`.

Intersecting the equality from Theorem 1 with the fixed set `BadCert_k(C)` gives

`Risk_k(H) = union_{J subseteq H, |J|<=k} Risk_k(J)`.

---

## 6. Proof of Theorem 3

Let `Q in Resp_k(F)` be an inclusion-minimal admissible certified response.

Choose one surviving certified `k`-packing `P` in `C_Q` at `F`.

For each route of `P` not already present in baseline `C`, choose one action of `Q` that supplies that route. Let `Q'` be the set of chosen actions.

At most one action is chosen for each of the `k` packing routes, so

`|Q'|<=k`.

Also `Q' subseteq Q`.

Because resource feasibility is hereditary under taking subsets, `Q'` is admissible whenever `Q` is admissible. The packing `P` is present in `C_Q'`, so `Q'` is already a successful response to `F`.

Minimality of `Q` therefore forces

`Q=Q'`.

Hence

`|Q|<=k`.

Sharpness is witnessed by a baseline with no certified route and a scenario in which target `k` can be restored only by `k` actions supplying `k` pairwise-disjoint certified routes.

---

## 7. Proof of Theorem 4

Assume first that `Risk_k(H)` is compensable by certified portfolio `Q`.

For every `J subseteq H`, Theorem 2 gives

`Risk_k(J) subseteq Risk_k(H)`.

The same `Q` therefore compensates every `Risk_k(J)`, in particular every one with `|J|<=k`.

Conversely, suppose every `Risk_k(J)` with `J subseteq H` and `|J|<=k` is compensable. Choose one successful certified portfolio `Q_J` for each such `J`.

There are finitely many such `J`. Under the conflict-free contract, their union

`Q = union_J Q_J`

is admissible.

Certified route addition is monotone, so `Q` compensates every scenario compensated by any `Q_J`.

By Theorem 2, every scenario in `Risk_k(H)` lies in at least one `Risk_k(J)` with `|J|<=k`. Hence `Q` compensates all of `Risk_k(H)`.

Thus the equivalence holds.

Sharpness follows from the sharpness construction in Theorem 1 with a certified layer that is unable to compensate the unique scenario activated only by the full `k`-action portfolio.

---

## 8. Proof of Theorem 5

Suppose first that `R` is jointly compensated by one admissible portfolio `Q`.

For every `F in R`, the finite set of subportfolios of `Q` that restore `F` contains an inclusion-minimal member `Q_F`. Thus

`Q_F in Resp_k(F)`

and

`Q_F subseteq Q`.

Therefore

`union_F Q_F subseteq Q`.

Resource feasibility is hereditary, so the union is resource-feasible.

Conversely, suppose there is a choice `Q_F in Resp_k(F)` whose union `Q*` is resource-feasible.

For each `F`, `Q_F subseteq Q*`. Certified route addition is monotone, so `Q*` restores every `F in R`. Hence `R` is jointly compensable.

For nonnegative additive action costs, every globally successful portfolio contains minimal successful responses to each scenario as above. Removing actions not needed by the selected minimal responses cannot increase cost. Therefore minimizing over all globally successful portfolios is equivalent to minimizing

`c(union_F Q_F)`

over all resource-compatible selections of one minimal response per scenario.

---

## 9. Proof of Theorem 6

Fix any integer `t>=2` and set target `k=1`.

Create defensive ancestry coordinates

`d_1,...,d_t`

and evidence ancestry coordinates

`e_1,...,e_t`.

The operational baseline is empty.

For each `i`, operational hardening action `h_i` supplies the singleton route `{d_i}`.

Define scenario `F_i` so that every defensive coordinate except `d_i` is compromised and every evidence coordinate except `e_i` is compromised.

Then `h_i` survives exactly `F_i` among the declared scenarios. Hence for every hardening portfolio `H`,

`Risk_1(H) = {F_i : h_i in H}`,

because the certified baseline is empty.

Now provide exactly `t-1` mutually exclusive certified resources

`r_1,...,r_(t-1)`.

For every pair `(i,j)`, provide a certified action `a_(i,j)` that

- supplies the singleton evidence route `(empty,{e_i})`; and
- exclusively claims resource `r_j`.

For scenario `F_i`, every `a_(i,j)` is a singleton successful certified response, so every local minimal response has size `1=k`.

Take any proper hardening subportfolio. It triggers at most `t-1` scenarios. Assign those scenarios injectively to the `t-1` resources and choose the corresponding certified actions. Their claims are disjoint, so the subportfolio is compensable.

The full hardening portfolio triggers all `t` scenarios. Any response to each scenario must consume one of only `t-1` mutually exclusive resources. A resource-feasible selection for all `t` scenarios would therefore require `t` distinct resources, but only `t-1` exist. The full portfolio is not compensable.

Because `t` is arbitrary, no finite hardening-audit cutoff depending only on `k=1` can be universally sufficient.

The operational activation witness for each `F_i` is the singleton `{h_i}`, and each local certified response is a singleton `{a_(i,j)}`. Thus both local ranks remain `1`, proving that the unbounded obstruction order is entirely a global compatibility phenomenon.

---

## 10. Consequences

The theorem separates two notions that coincide only in the conflict-free model.

Local target structure is controlled by `k`:

`activation witness size <= k`

and

`minimal response size <= k`.

Global assurance auditability is controlled by the compensation-composition contract.

Without certified-action conflicts, the local rank bound lifts to a global audit bound.

With exclusive resources, that lift fails completely: arbitrary-order global incompatibility can be generated while every local object remains target-bounded.

This is the v2.16 assurance interaction phase boundary.

---

## 11. Claim boundary

The theorem does not claim novelty for generic matching, resource allocation, set systems, bounded path witnesses, or finite combinatorial selection.

The SCRT claim is the exact result inside the declared cyber-resilience semantics: ancestry-independent target packings produce target-bounded operational activation and certified response structure, while exclusive certified resources create an unbounded global assurance-audit obstruction order without changing either local bound.

No claim of historical priority is made.
