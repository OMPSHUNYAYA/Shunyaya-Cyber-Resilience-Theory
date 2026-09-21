# Operational/Certified Divergence Example

Fix `k=2`.

Architecture `X` concentrates two certified units in one ancestry lane:

`((2,2),(0,0))`.

Architecture `Y` distributes them across two lanes:

`((1,1),(1,1))`.

Both have current values

`(C_op,C_cert)=(2,2)`.

But `X` has one certification-support lane while `Y` has two. Under the frozen certification-strip/recovery grammar, `X` is assurance-forceable while `Y` has a memoryless assurance-preservation strategy.

Therefore current scalar capacities are not continuation-complete.
