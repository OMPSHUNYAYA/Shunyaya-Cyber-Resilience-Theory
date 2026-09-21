# SCRT Worked Example — Supply-Chain Assurance Under Continued Operation

## Purpose

This example maps SCRT's operational/certified distinction to a recognizable software-supply-chain deployment using provenance, signatures, transparency records, and an SBOM as evidence objects.

The example is illustrative. Independence, compromise, and recovery relationships below are **declared properties of this modeled deployment**. They are not implied automatically by SLSA, in-toto, Sigstore, an SBOM format, or any other product or standard.

## 1. Deployment

A production service runs two healthy replicas of one container image.

The organization admits the image only when at least two independent evidence routes support the declared trust decision.

Target:

`k = 2`.

Operational support:

- replica `R1` remains healthy;
- replica `R2` remains healthy.

Certified evidence support:

- `E1`: a release signature rooted in an HSM-held release authority `A1`;
- `E2`: build provenance and transparency evidence rooted in a separately administered builder/log authority `A2`.

For this example the modeler declares:

`A1 != A2`

and treats them as independent ancestry for the target observer.

Therefore at `t0`:

`C_op = 2`

`C_cert = 2`.

## 2. Evidence-only compromise

At `t1`, the organization determines that the signing authority `A1` was exposed.

The declared attack is:

`F_D = empty`

`F_E = {A1}`.

The running replicas continue serving traffic, so:

`C_op = 2`.

The `E1` route is no longer admitted as certified evidence, while `E2` remains valid:

`C_cert = 1`.

Hence:

`C_op >= k and C_cert < k`.

This is a silent assurance failure in the SCRT model: operation remains at target while the independent certified basis for trusting that operation falls below target.

## 3. Two recovery architectures with the same pre-attack capacities

Now compare two architectures that have identical pre-attack values:

`(C_op,C_cert) = (2,2)`.

They differ only in the declared recovery continuation.

### Architecture X — recovery coupled to the compromised authority

The only admitted recovery for `E1` requires an authorization path rooted in the same compromised administrative ancestry `A1`.

After `A1` is compromised, that recovery is unavailable under the declared contract.

Architecture X therefore remains at:

`C_cert = 1`.

### Architecture Y — independent recovery authority

The recovery route is authorized by a separately administered recovery authority `A3`, declared independent of `A1` and `A2` for the observer.

A registered `ROTATE_AND_REATTEST` action produces a replacement certified evidence route rooted in `A3`.

After the response:

`C_cert = 2`.

Thus X and Y have the same current capacities at `t0` but different future assurance behavior under the same admitted evidence compromise.

## 4. SCRT encoding

| SCRT object | Modeled deployment meaning |
|---|---|
| security obligation | continue service with at least `k=2` independently supported trust lanes |
| operational route | one healthy service replica |
| evidence route | one admitted evidence chain supporting the image trust decision |
| ancestry | root of compromise/failure relevant to that route |
| `F_D` | compromise affecting operational defensive ancestry |
| `F_E` | compromise invalidating evidence ancestry |
| recovery action | declared key rotation / rebuild / re-attestation path |
| observer | target-relative operational and certified capacity |

The important modeling rule is:

**distinct evidence objects are not counted as independent unless their relevant ancestry is declared independent.**

## 5. What the example demonstrates

The example demonstrates four SCRT ideas.

First, an operationally healthy service can enter a mathematically distinct assurance state without crashing.

Second, artifact count is not independence. Shared roots of trust remain visible through ancestry.

Third, two architectures with the same present capacities can differ under future recovery continuation.

Fourth, the distinction is determined by the declared cyber architecture and continuation contract rather than by the names of the technologies used to instantiate it.

## 6. What the example does not establish

This example does not establish:

- that the two authorities are independent in any particular real deployment;
- that the evidence objects are authentic;
- that the provenance is complete;
- that the SBOM is correct;
- that a particular signing implementation is secure;
- that the registered attack grammar covers every real attacker capability;
- that the target `k=2` is an appropriate organizational policy.

Those remain external validation obligations under the Cyber Architecture Encoding Contract and the SCRT Threat Model and Assumption Boundary.

## 7. Generic implementation context

The example can be instantiated using common supply-chain mechanisms such as signed artifacts, provenance attestations, transparency records, and software bills of materials. Specific products or standards are illustrative implementation contexts rather than mathematical dependencies of SCRT.
