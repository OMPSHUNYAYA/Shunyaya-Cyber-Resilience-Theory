# SCRT Exact Structural Classification v2.7.0

## Base typed continuation

For passive finite continuation, the Base Resilience Kernel is

`BRK(X)=(MinO(X),MinT(X))`,

where `MinO` is the inclusion-minimal operational support family and `MinT` the minimal typed certified-signature family under componentwise inclusion.

Within the frozen passive semantics:

`X ~_BRK Y iff BRK(X)=BRK(Y)`.

Unequal kernels admit finite constructive distinguishing contexts.

## Multiplicity-sensitive intervention

Structural diversification can expose duplicate or passively dominated realization tokens. Therefore passive minimal-support reduction is not intervention-complete.

The Interventional Resilience Kernel retains exact multiplicities:

`IRK(X)=(nu_X,mu_X)`.

For ancestry width `m`, its dimension is

`2^m + 3^m - 2`.

Operational multiplicities are reconstructible from the cumulative probes

`Z_O(Q)=sum_{S subseteq Q} nu_X(S)`

by subset inversion.

Typed multiplicities are reconstructible analogously from

`Z_T(Q_D,Q_E)=sum_{D subseteq Q_D, E subseteq Q_E} mu_X(D,E)`.

## Obligation resolution

If future hardening may target named obligations, complete-realization convolution loses continuation-relevant obligation ownership.

The Obligation-Resolved Interventional Kernel stores one multiplicity kernel per obligation:

`ORIK(X)=(K_o)_(o in O)`.

Complete realization behavior is recovered by convolution of the obligation factors.

## Structural transformations

Deterministic tokenwise hardening rewrites act on flattened ORIK coordinates as nonnegative affine maps

`T(x)=Mx+b`.

Fixed-interface transformations compose associatively and need not commute.

Interface-changing hardening uses rectangular affine maps between finite ORIK spaces.

Anonymous ancestry names are quotiented only under gauge-compatible transformations; deterministic targeting of an anonymous identity is not admitted unless the target becomes semantically anchored.

## Exact state cardinality

At fixed finite interface width, exact ORIK is finite-dimensional but not finite-valued.

A one-coordinate family with multiplicity `n=1,2,3,...` remains pairwise distinguishable under exact multiplicity-sensitive continuation.

Therefore:

`fixed finite interface width != finite exact contextual state space`.

The exact classification is a finite-dimensional integer-kernel theory, not a finite-state theory.
