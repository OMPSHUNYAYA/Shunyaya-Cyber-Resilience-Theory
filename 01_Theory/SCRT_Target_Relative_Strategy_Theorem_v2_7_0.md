# SCRT Target-Relative Strategy Theorem v2.7.0

Fix target `k>=1`.

## Saturation theorem

For every admitted target-congruent transformation `T`:

`Sat_k(T(x)) = T_bar(Sat_k(x))`.

For target packing questions, no witness needs more than `k` copies of any exact realization type. Therefore

`C(x)>=k iff C(Sat_k(x))>=k`.

Thus `Sat_k` induces an exact target-relative continuation quotient.

## Sharpness

No uniform threshold `h<k` preserves every target-`k` question.

The states containing `k-1` and `k` copies collapse under `Sat_h` when `h<k`, but only one attains capacity `k`.

Hence the universal clipping threshold `k` is sharp.

## Finite bound

For `D` multiplicity coordinates:

`Sat_k(x) in {0,1,...,k}^D`,

so the raw target-state count is at most

`(k+1)^D`

before gauge reduction and finite control/resource factors.

## Infinite-horizon strategy

On the finite target quotient, define safe target states and the predecessor operator

`Phi(W) = Safe_k intersect {s : for every attack a, exists defense d with d(a(s)) in W}`.

The infinite-horizon defender winning region is the greatest fixed point

`W_* = gfp(Phi)`.

Winning states admit memoryless canonical defender strategies. Losing states receive finite removal ranks that give constructive attacker spoiling strategies.

## Universal operation admission

A future operation can join the target strategy grammar when its local certificate establishes target congruence, gauge compatibility, target-local availability, finite control/resource declarations, and kernel locality.

Once admitted, arbitrary finite composition preserves the target quotient and the infinite-horizon theorem.
