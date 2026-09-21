# SCRT Definitions v2.7.0

## Finite ancestry interface

Let `V` be a finite dependency-ancestry set.

An operational realization has nonempty support `S subseteq V`.

A certified realization is a typed pair

`x=(D,E)`

with

`D subseteq V`,

`E subseteq V`,

`D intersect E = empty`,

`D union E != empty`.

Its physical ancestry support is `D union E`.

## Operational and certified capacity

For compromise set `F`, a realization survives when its relevant ancestry support is disjoint from `F`.

`C_op(X,F)` is the maximum number of pairwise physically ancestry-disjoint surviving operational realizations.

`C_cert(X,F)` is the corresponding maximum for surviving certified realizations.

Always under the declared certification semantics:

`C_cert <= C_op`

whenever certified realizations refine operational capability as specified by the model.

## Multiplicity kernels

For exact operational support `S`, let `nu_o(S)` be its realization-token multiplicity in obligation `o`.

For exact certified signature `(D,E)`, let `mu_o(D,E)` be its multiplicity in obligation `o`.

`ORIK(X)` is the collection of all `nu_o` and `mu_o` coordinates.

For `q` obligations and ancestry width `m`, the coordinate count is

`q(2^m + 3^m - 2)`.

The coordinates are nonnegative integers and are not globally bounded in the exact semantics.

## Role-polarized compromise

A polarized compromise is

`F=(F_D,F_E)`.

A certified signature `(D,E)` survives iff

`D intersect F_D = empty`

and

`E intersect F_E = empty`.

Operational realizations respond only to the declared operational/defensive compromise channel.

## Silent assurance failure

For target `k`, a silent assurance failure satisfies

`C_op >= k`

and

`C_cert < k`.

## Target saturation

For a nonnegative integer vector `x`, define

`Sat_k(x)_i = min(x_i,k)`.

An operation `T` is target-congruent when there exists `T_bar` with

`Sat_k(T(x)) = T_bar(Sat_k(x))`

for every admitted exact state `x`.

## Gauge

A gauge is a permitted permutation of anonymous ancestry identities that fixes semantically anchored identities.

Gauge-compatible transformations transport gauge-related states to gauge-related states.

## Continuation contract

A continuation contract is

`C=(S,G,O)`.

`S` is a declared state space, `G` a well-typed continuation generator family, and `O` the declared observer.

For `x,y in S`:

`x ~_C y`

iff

`O(w.x)=O(w.y)`

for every finite well-typed word `w` over `G`.

## Campaign residual

For a finite target-saturated campaign state `K`, registered extension alphabet `G_C`, and campaign observer `O_C`, define

`K ~_res L`

iff

`O_C(w.K)=O_C(w.L)`

for every finite `w` over `G_C`.

`CRK(K)` is the equivalence class of `K` under `~_res`.
