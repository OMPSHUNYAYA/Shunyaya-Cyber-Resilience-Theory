# SCRT Exclusive Recovery-Resource Worked Example v2.18.0

## Purpose

This illustrative encoding demonstrates the v2.18 phase boundary. It is not a claim about a specific deployed organization.

Set target `k=1`. Three services receive operational hardening actions `h1,h2,h3`. Under declared compromise scenarios `F1,F2,F3`, each `hi` makes service `i` newly operationally survivable while its certified recovery basis remains below target.

Each scenario has a singleton certified response:

`F1 -> q1`

`F2 -> q2`

`F3 -> q3`.

Thus every local response has rank `1`.

### Conflict-free encoding

If `q1,q2,q3` have no exclusive resource claims, the union `{q1,q2,q3}` is admissible. Every individually restorable scenario can therefore be restored simultaneously.

### Exclusive-resource encoding

Now declare that each response must occupy an exclusive recovery authority. Suppose only two compatible authorities are available across the three responses, so any two scenarios can be assigned distinct authorities but all three cannot.

Then every proper hardening subportfolio is assurance-compensable, while the full `{h1,h2,h3}` portfolio is not.

Nothing changed in the local target:

`operational activation rank = 1`

`local certified response rank = 1`.

The obstruction is entirely global: the selected certified responses cannot be composed under the declared exclusive-resource contract.

## Modeling boundary

The existence and exclusivity of a recovery authority are encoding assumptions that must be validated externally. SCRT does not infer those facts from role names or technology labels.
