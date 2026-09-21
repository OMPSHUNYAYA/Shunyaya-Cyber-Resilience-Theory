# SCRT Adversarial Assurance Campaign Theorem v2.7.0

## Coupled attack impacts

Each adversarial action has a polarized impact, cost, and resource claim.

A feasible portfolio has aggregate impact equal to the union of primitive impacts.

The Attack Impact Kernel maps each exact aggregate impact to its Pareto-minimal `(cost,resources)` realizations.

This is exact for one-shot impact/cost/resource queries but does not preserve round granularity.

## Recovery effects

Recovery portfolios analogously induce target-saturated certified recovery effects with Pareto-minimal cost/resource realizations.

## One-shot budget duality

For operationally safe attack impact `F`, let

`a(F)` = minimum attacker cost to realize `F`,

`d(F)` = minimum defender recovery cost restoring certified target `k`, with `INF` if impossible.

Define

`Alpha_k(b_D) = min {a(F) : d(F)>b_D}`

and

`Delta_k(b_A) = max {d(F) : a(F)<=b_A}`.

Then

`Alpha_k(b_D)>b_A iff Delta_k(b_A)<=b_D`.

## Round-resolved campaign boundary

Static portfolio equivalence is not campaign-complete.

A primitive joint attack that hits two assurance coordinates in one round can differ from two sequential one-coordinate attacks even when their aggregate one-shot impact/cost summary is identical, because the defender may recover between rounds.

Therefore the campaign state retains primitive round-resolved generators and their joint ancestry correlations.

## Persistent campaign value

For campaign state `s` and attacker budget `b_A`, define `Delta_C(s,b_A)` as the minimum cumulative recovery expenditure sufficient against every feasible attacker campaign within budget `b_A`.

The exact recursion has attacker maximization over feasible next attacks and defender minimization over safe recovery responses of immediate recovery cost plus future required expenditure.

Its inverse threshold view `Alpha_C` satisfies

`Alpha_C(s,b_D)>b_A iff Delta_C(s,b_A)<=b_D`.

The campaign solver is finite under the registered one-use action grammar and target-saturated state contract.
