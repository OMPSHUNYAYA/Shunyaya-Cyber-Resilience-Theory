# SCRT Campaign Residual Theorem v2.7.0

Let `K` be a finite target-saturated round-resolved campaign state.

Let `G_C` be the finite registered future campaign-extension alphabet and `O_C(K)` the exact campaign-value profile.

Define

`K ~_res L`

iff

`O_C(w.K)=O_C(w.L)`

for every finite extension word `w` over `G_C`.

## Residual theorem

`~_res` is a right congruence.

Its quotient is continuation-complete for pure future campaign values.

For a finite registered state space, it is the coarsest right congruence refining the present campaign observer and is computable by stable partition refinement.

Start with

`P_0(K)=O_C(K)`.

Refine by

`P_(n+1)(K)=(O_C(K),(P_n(g.K))_(g in G_C))`.

The finite refinement stabilizes exactly at the campaign residual classes.

Distinct residual classes receive finite distinguishing future campaign words from the refinement construction.

Therefore the Campaign Residual Kernel is information-minimal up to injective recoding of semantic classes for the registered pure campaign-value continuation contract.

Current campaign value alone can be strictly coarser because hidden resource or generator correlation may become observable only after future extension.
