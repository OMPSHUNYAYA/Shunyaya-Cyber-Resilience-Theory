# SCRT Assurance Audit Complexity Phase-Boundary Theorem v2.17.0

## 1. Status

`theorem_status: WRITTEN_UNIVERSAL_PROOF`

`verification_status: PRINCIPAL_AND_INDEPENDENT_FINITE_REDUCTION_REPLAY_PASS`

No claim of historical priority is made.

The theorem is stated for explicit finite SCRT instances. The accompanying programs replay finite instances of the reduction and cross-check the tractable case; they are not proof assistants.

---

## 2. Input model

Fix a target `k>=1`.

The explicit input lists:

- the finite ancestry universe;
- baseline operational routes;
- baseline certified typed routes;
- operational hardening actions and the selected hardening portfolio `H`;
- certified compensation actions;
- the finite declared compromise-scenario family; and
- when enabled, exclusive resource claims of certified actions.

All route families and scenario families are explicitly represented. Complexity statements below are measured in the length of this explicit input.

The hardening-induced assurance-risk family is

`Risk_k(H) = {F : baseline operation is below k, hardened operation is at least k, baseline certification is below k}`.

The decision question is whether there exists an admissible certified compensation portfolio that restores certified target `k` for every `F in Risk_k(H)`.

Two compensation contracts are compared.

### Conflict-free contract

Every finite union of certified actions is admissible.

### Exclusive-resource contract

Each certified action has a finite resource claim. A selected portfolio is admissible exactly when the claims of distinct selected actions are pairwise disjoint.

---

## 3. Complexity phase-boundary theorem

### Theorem 1 — Fixed-target conflict-free tractability

For every fixed target `k`, assurance-compensability of a specified operational hardening portfolio under conflict-free additive certified compensation is decidable in polynomial time on the explicit SCRT input.

The same holds for the universal question asking whether every operational hardening subportfolio is assurance-compensable.

### Theorem 2 — Exclusive-resource hardness at target one

Under exclusive certified resources, assurance-compensability of a specified hardening portfolio is NP-complete already for target

`k=1`,

under all of the following restrictions:

- the operational baseline is empty;
- each operational hardening action supplies one operational route;
- the certified baseline is empty;
- each certified action supplies exactly one certified route;
- every successful local response is a singleton certified action; and
- every certified action claims exactly two exclusive resources.

The corresponding universal hardening-library assurance audit is NP-complete under the same restrictions.

### Corollary — Computational assurance phase boundary

Within the frozen SCRT semantics:

`fixed-k conflict-free compensation -> polynomial-time exact assurance audit`

while

`exclusive certified resources -> NP-complete assurance compatibility already at k=1`.

This computational transition occurs even though the local structural ranks from v2.16 remain minimal in the hardness construction:

`operational activation rank = 1`

and

`certified response rank = 1`.

---

## 4. Proof of Theorem 1

Let `k` be fixed.

### Step 1 — Compute the risk family

For every explicitly listed compromise scenario `F`, determine whether baseline operation is below target and hardened operation reaches target.

A target test asks whether there exist `k` surviving routes with pairwise-disjoint physical ancestry supports.

If `R` surviving routes are explicitly listed, this can be decided by enumerating at most

`C(R,k)`

route tuples and testing pairwise disjointness.

Because `k` is fixed, this is polynomial in `R`.

The same fixed-`k` enumeration decides whether the baseline certified layer is below target.

Repeating these tests over the explicit finite scenario list computes `Risk_k(H)` in polynomial time.

### Step 2 — Conflict-free compensation reduces to the maximal certified installation

Let `A_C` be the entire certified-action library and let `C_all` denote the certified route family obtained by installing every certified action.

Because certified action addition is monotone and every action union is admissible,

`Risk_k(H) is compensable`

iff

`C_cert(C_all,F)>=k for every F in Risk_k(H)`.

The forward implication holds because any successful portfolio is a subset of the maximal installation.

The reverse implication holds because the maximal installation itself is admissible.

Each certified target test is again a fixed-`k` pairwise-disjoint packing test and is polynomial in the explicit number of routes.

Therefore the specified-portfolio assurance-compensability problem is in polynomial time for every fixed `k`.

### Universal-library audit

Hardening-induced risk is monotone under operational hardening:

`J subseteq H => Risk_k(J) subseteq Risk_k(H)`.

Let `H_all` contain every operational hardening action.

If `Risk_k(H_all)` is compensable, the same certified portfolio compensates every smaller risk family `Risk_k(J)`. The converse is immediate because the universal audit includes `H_all`.

Thus the universal conflict-free audit is decided by the same polynomial test applied to `H_all`.

This complexity statement is for fixed `k` and explicit scenario/action representation. It does not claim polynomial complexity for an implicitly represented exponentially large scenario universe or for variable `k`.

---

## 5. Membership in NP for the exclusive-resource problem

A certificate is a selected certified-action portfolio `Q`.

In polynomial time one can verify:

1. the resource claims of selected actions are pairwise disjoint;
2. the routes supplied by `Q` are added to the certified baseline; and
3. for every explicitly listed scenario in `Risk_k(H)`, the resulting certified routes supply target `k`.

For the hardness theorem `k=1`, the target test is simply existence of one surviving certified route.

Therefore the exclusive-resource assurance-compensability problem is in NP.

---

## 6. NP-hardness reduction

Use the standard NP-complete 3-dimensional matching decision problem.

An instance consists of three sets

`X`, `Y`, `Z`

with

`|X|=|Y|=|Z|=q`

and a finite triple set

`T subseteq X x Y x Z`.

The question is whether there exist `q` triples whose `X`, `Y`, and `Z` coordinates are each pairwise distinct.

Construct the following SCRT instance in polynomial time.

### Ancestry

For every `x in X`, create two physical ancestry coordinates:

`d_x` for operational ancestry,

`e_x` for evidence ancestry.

Set target

`k=1`.

### Operational side

The operational baseline is empty.

For each `x in X`, create hardening action `h_x` supplying the singleton operational route

`{d_x}`.

The selected hardening portfolio contains every `h_x`.

For each `x`, define scenario `F_x` so that

- every defensive coordinate except `d_x` is compromised; and
- every evidence coordinate except `e_x` is compromised.

Then `h_x` is the unique hardening action whose supplied route survives `F_x`.

Therefore the full hardening portfolio makes every `F_x` newly operationally survivable, and the empty certified baseline leaves every `F_x` in the assurance-risk family.

Thus

`Risk_1(H_all) = {F_x : x in X}`.

### Certified side

The certified baseline is empty.

For every triple

`t=(x,y,z) in T`,

create certified action `a_t` that supplies exactly one certified route:

`(empty,{e_x})`.

This route survives `F_x` and survives no `F_x'` with `x'!=x`.

Give `a_t` exactly two exclusive resource claims:

`y`

and

`z`.

Hence every available local response is a singleton action, and two selected actions are resource-compatible exactly when they share neither a `Y` coordinate nor a `Z` coordinate.

### Correctness: matching implies compensation

Suppose the 3-dimensional matching instance has a perfect matching `M` of `q` triples.

Select the corresponding `q` certified actions.

The matching contains one triple for every `x`, so every scenario `F_x` receives a surviving certified route.

The selected triples have pairwise-distinct `Y` and `Z` coordinates, so the action resource claims are pairwise disjoint.

Thus the SCRT assurance-risk family is jointly compensable.

### Correctness: compensation implies matching

Suppose the SCRT risk family is jointly compensable by some resource-feasible certified portfolio `Q`.

Every scenario `F_x` requires at least one selected action whose triple has first coordinate `x`, because no other certified route survives `F_x`.

Therefore `Q` contains at least `q` actions.

Each action claims one `Y` resource, and resource feasibility forbids two selected actions from sharing that resource. Since there are only `q` `Y` resources, `Q` contains at most `q` actions.

Hence `Q` contains exactly `q` actions, one for every `x`.

Resource feasibility also makes their `Y` coordinates pairwise distinct and their `Z` coordinates pairwise distinct.

The corresponding triples therefore form a perfect 3-dimensional matching.

Thus the 3-dimensional matching instance is positive iff the constructed SCRT assurance-compensability instance is positive.

The construction is polynomial, so the exclusive-resource problem is NP-hard. Together with membership in NP it is NP-complete.

---

## 7. Universal-audit corollary

In the reduction, and generally under additive operational hardening with a fixed certified baseline,

`J subseteq H => Risk_k(J) subseteq Risk_k(H)`.

If the full hardening portfolio is compensable, the same certified portfolio compensates every hardening subportfolio. Therefore

`every hardening subportfolio is compensable`

iff

`the full hardening portfolio is compensable`.

Applying this to the reduction transfers NP-completeness to the universal hardening-library assurance-audit decision problem.

---

## 8. Relationship to the v2.16 structural boundary

The reduction uses

`k=1`.

Each assurance-risk scenario is activated by one operational hardening action, so

`operational activation rank = 1`.

Every available minimal certified response is one certified action, so

`certified response rank = 1`.

Nevertheless, selecting one mutually compatible response for every scenario encodes an NP-complete global selection problem.

Therefore the computational hardness is not caused by large local activation or response witnesses. It arises entirely from cross-scenario compatibility of exclusive certified resources.

This is the computational counterpart of the v2.16 local/global assurance interaction phase boundary.

---

## 9. Claim boundary

The theorem does not claim novelty for generic NP-completeness reductions, matching, resource allocation, set packing, `k`-out-of-`n` reliability, or fixed-parameter enumeration.

The SCRT result is the exact complexity transition inside the declared assurance-hardening semantics:

- fixed-target conflict-free compensation is polynomial on explicit instances;
- exclusive certified resources make assurance compatibility NP-complete already at target `1`;
- the hardness survives singleton local activation and singleton local response structure.

No claim of historical priority is made.
