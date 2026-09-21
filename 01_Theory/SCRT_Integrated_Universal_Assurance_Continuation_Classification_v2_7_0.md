# SCRT Integrated Universal Assurance Continuation Classification v2.7.0

## Theorem 1 — Continuation quotient

Let `C=(S,G,O)` be a frozen SCRT continuation contract.

Define

`x ~_C y`

iff

`O(w.x)=O(w.y)`

for every finite well-typed continuation word `w` over `G`.

Then:

1. `~_C` is an equivalence relation.
2. `~_C` is a right congruence under every admitted continuation generator.
3. `S/~_C` is continuation-complete for `O`.
4. If the registered state space is finite, different quotient classes have finite distinguishing continuation words.
5. Any representation complete for contract `C` must distinguish all distinct `~_C` classes.

Hence `S/~_C` is information-minimal up to injective recoding of semantic classes.

### Proof

Reflexivity, symmetry, and transitivity follow from equality of observer values over the same continuation set.

For right congruence, suppose `x ~_C y` and let `g in G` be well typed. For every later word `w`, the composite `wg` is an admitted continuation from `x` and `y`; therefore `O(w.g.x)=O(w.g.y)`.

Continuation completeness is immediate from the definition of `~_C`.

In a finite deterministic registered system, if two states are inequivalent, stable partition refinement separates them after finitely many rounds and reconstructs a finite distinguishing word.

If a purported complete representation mapped two inequivalent states to the same representation, its decoder/observer would be unable to distinguish them under the finite context guaranteed above, contradicting completeness.

## Theorem 2 — Contract monotonicity

Let `C1` and `C2` share the same state space and observer, and suppose every `C1` continuation is admitted by `C2`.

Then

`x ~_C2 y => x ~_C1 y`.

The same monotonicity holds when the observer family is enlarged.

### Proof

Equality under every continuation in the larger set implies equality under its subset. Enlarging the observer family adds equality obligations and therefore cannot merge contextual classes.

## Theorem 3 — Exact structural cardinality

Fixed finite interface width does not imply finitely many exact contextual states when exact multiplicity-sensitive continuation is admitted.

A single exact route type with multiplicity `n=1,2,3,...` yields pairwise distinguishable exact states under the corresponding reconstruction probe.

Therefore the exact SCRT representation is finite-dimensional but generally infinite-valued.

## Theorem 4 — Sharp target quotient

For fixed target `k`, target saturation

`Sat_k(x)_i=min(x_i,k)`

is an exact continuation quotient for every target-congruent operation and target observer.

No smaller universal clipping threshold preserves all target-`k` questions.

For `D` multiplicity coordinates, the raw finite state bound is

`(k+1)^D`

before gauge and finite control/resource reduction.

## Theorem 5 — Campaign residual minimality

For a finite registered target-saturated campaign contract, the Campaign Residual Kernel is the coarsest right congruence preserving every future exact campaign-value profile.

It is computable by stable partition refinement and different residual classes admit finite distinguishing future campaigns.

## Corollary — Semantic-level hierarchy

The three principal SCRT levels are:

`EXACT_STRUCTURAL`

`TARGET_RELATIVE`

`CAMPAIGN_RESIDUAL`.

The projections between them can be strict. No operation-independent canonical SCRT state is asserted.

The minimum sufficient state is relative to the declared future-operation and observer contract.
