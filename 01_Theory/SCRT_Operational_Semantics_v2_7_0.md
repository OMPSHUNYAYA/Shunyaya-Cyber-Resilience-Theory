# SCRT Operational Semantics v2.7.0

## 1. State components

SCRT uses finite declared cyber interfaces. Depending on the theorem layer, a state may contain:

- obligation-resolved operational route multiplicities;
- obligation-resolved typed certified-route multiplicities;
- compromise state;
- installed hardening or recovery state;
- attacker and defender cost/resource state;
- semantic ancestry anchors and anonymous ancestry identities;
- campaign action-use and persistence state.

The exact multiplicity coordinates are nonnegative integers.

## 2. Operational and certified realization semantics

An operational route has support `S subseteq V`.

A certified route is a typed signature

`(D,E)`

with

`D intersect E = empty`.

Its physical ancestry support is

`D union E`.

Complete capacities are maximum cardinalities of pairwise physically ancestry-disjoint surviving realizations under the declared obligation semantics.

The model distinguishes

`C_op`

from

`C_cert`.

## 3. Compromise semantics

In unpolarized layers, compromise removes routes whose relevant support intersects the compromise set.

In role-polarized layers, compromise is

`F=(F_D,F_E)`.

A certified route `(D,E)` survives iff

`D intersect F_D = empty`

and

`E intersect F_E = empty`.

Operational routes respond only to the declared operational/defensive channel.

## 4. Continuation semantics

A continuation contract is

`C=(S,G,O)`.

A finite word `w` is admissible when every generator application is well typed and satisfies the registered availability, resource, target-locality, and gauge conditions.

Two states are contextually equivalent when

`O(w.x)=O(w.y)`

for every admitted finite word `w`.

Composition order is semantic. Round-resolved campaign operations are not replaced by unordered portfolio union when recovery may intervene between rounds.

## 5. Structural transformations

For exact multiplicity coordinates, deterministic tokenwise rewrites act as nonnegative affine transformations where the registered interface is fixed or changes through a typed rectangular map.

Gauge-compatible transformations preserve anonymous-name equivalence.

A future operation may join a target-relative grammar only when its local certificate establishes target congruence and target-local availability.

## 6. Target-relative semantics

For fixed `k`:

`Sat_k(x)_i=min(x_i,k)`.

A transformation is target-congruent when

`Sat_k(T(x))=T_bar(Sat_k(x))`.

Only target-congruent operations and target-local observers are admitted to the finite target-relative theorem.

## 7. Assurance obstruction semantics

A silent assurance failure satisfies

`C_op>=k`

and

`C_cert<k`.

Minimal role-polarized silent obstructions are minimal certified-packing blockers whose defensive component still leaves an operational target packing intact.

Recovery-response antichains encode minimal recovery portfolios that restore certified target after a fixed impact.

## 8. Campaign semantics

A campaign is round resolved.

Attacker impacts, defender recoveries, costs, action-use state, and resource claims evolve according to the registered campaign grammar.

`Delta_C(s,b_A)` is the minimum cumulative defender recovery expenditure sufficient against every admitted attacker campaign within attacker budget `b_A`.

`Alpha_C` is its inverse budget-threshold view.

## 9. Campaign residual semantics

For finite registered target-saturated campaign state `K`, extension alphabet `G_C`, and campaign observer `O_C`:

`K ~_res L`

iff

`O_C(w.K)=O_C(w.L)`

for every finite extension word `w`.

Stable partition refinement computes the coarsest right congruence preserving this observer.

## 10. Canonicalization

Canonicalization is always contract-relative.

A representation may discard information only when that information cannot alter any observer value under any continuation admitted by the current contract.

Strengthening the continuation grammar or observer may therefore require a strict refinement of the canonical state.
