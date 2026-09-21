# SCRT Threat Model and Assumption Boundary v2.18.0

## Purpose

This document states the adversarial, defensive, evidentiary, and modeling assumptions under which SCRT claims are interpreted. It separates the mathematical semantics of an admitted SCRT encoding from the external task of determining whether a deployed cyber system has been encoded adequately.

## 1. Declared finite architecture

An SCRT instance begins with a finite declared architecture containing:

- security obligations;
- operational defensive routes;
- typed certified routes `(D,E)`;
- dependency-ancestry classes;
- admissible attack, compromise, hardening, and recovery actions;
- action costs and resource claims where used;
- semantic anchors and admissible anonymity gauges;
- target values such as `k`;
- an observer contract.

The mathematical theorems range over the admitted encoding. They do not assert that the encoding is a complete description of a deployed system.

## 2. Adversary model

The adversary acts only through the attack or compromise operations registered by the continuation contract.

A registered adversarial action may declare:

- defensive/control ancestry impact `F_D`;
- evidence/assurance ancestry impact `F_E`;
- coupled impacts on several ancestry coordinates;
- cost;
- exclusive or shared resource claims;
- persistence rules;
- one-use or reusable action status;
- action availability conditions.

SCRT does not assume that real adversaries are limited to these operations. Completeness of the registered attack grammar is an external threat-modeling obligation.

## 3. Defender model

The defender acts only through registered hardening and recovery operations.

A defensive action may declare:

- new operational or certified routes;
- ancestry changes;
- resource requirements;
- action cost;
- persistence or release rules;
- phase ordering;
- target-local availability conditions.

When a theorem assumes adaptive recovery, the defender may choose a response after observing the declared realized attack state. When the contract specifies a different information pattern, that pattern governs the game.

## 4. Operational and certified capacity

`C_op` measures the declared operational defensive capacity.

`C_cert` measures the declared independently certified capacity under the typed defensive/evidentiary ancestry semantics.

For target `k`, silent assurance failure is:

`C_op >= k and C_cert < k`.

This is a mathematical classification inside the encoding. It does not independently establish whether a real service is safe, trustworthy, compliant, or fit for operation.

## 5. Independence assumption

Independence is a property of the declared ancestry model, not of product names or artifact count.

Two controls, signatures, attestations, logs, builders, recovery systems, or evidence objects are not treated as independent merely because they are distinct objects. If they share a modeled root of compromise or failure relevant to the declared observer, that shared ancestry must remain visible.

Likewise, distinct ancestry labels are independent only to the extent justified by the external system model.

## 6. Evidence assumptions

SCRT reasons about the availability and compromise status of declared evidence routes. It does not itself establish:

- authenticity of an evidence object;
- correctness of a signature implementation;
- security of key custody;
- correctness of provenance generation;
- completeness of logging;
- integrity of an external transparency service;
- correctness of a software bill of materials;
- truth of a human or organizational assertion.

Those facts enter SCRT only through the encoding contract.

## 7. Persistence and time

Compromise and recovery persistence are not universal defaults. They are contract parameters.

Round-resolved campaign results assume the declared campaign grammar, including which impacts persist, whether resources remain occupied, whether actions can repeat, and when the defender may respond.

Static portfolio equivalence is not assumed to imply campaign equivalence.

## 8. Observability

Contextual equivalence is observer-relative.

The observer may expose, for example:

- operational target satisfaction;
- certified target satisfaction;
- exact capacity;
- a campaign value such as `Delta_C`;
- another explicitly registered finite observation.

Strengthening the observer or admitted continuation grammar can refine the canonical quotient.

## 9. Finite registered campaign assumption

The finite campaign-residual theorem requires a finite target-saturated registered campaign state system and finite registered extension alphabet.

Unregistered attacker capabilities, unbounded fresh state, hidden resource semantics, or operations that violate the frozen target-congruence contract require a different or stronger model.

## 10. Probability and empirical rates

The principal SCRT semantics are exact and non-probabilistic. Attack likelihoods, empirical frequencies, detection probabilities, economic priors, and stochastic failure rates are outside the principal theorem unless explicitly introduced by a separate extension.

## 11. Validation boundary

Before applying SCRT conclusions to a deployed system, a modeler must independently justify at least:

- route completeness relative to the declared obligations;
- ancestry assignments;
- independence assertions;
- attack-action coverage;
- recovery-action feasibility;
- cost and resource semantics;
- evidence validity assumptions;
- observer selection;
- target selection;
- persistence and information-pattern assumptions.

The SCRT classification theorem begins after those modeling commitments are fixed.

## 12. Security scope

SCRT is a defensive mathematical framework. It does not require exploit construction, credential theft procedures, malware development, persistence instructions, evasion techniques, or unauthorized-access guidance.

## 13. Status

`version: 2.18.0`

`threat_model: EXPLICIT_DECLARED_OPERATION_GRAMMAR`

`real_world_model_completeness: EXTERNAL_VALIDATION_OBLIGATION`

`evidence_authenticity: EXTERNAL_VALIDATION_OBLIGATION`

No claim of historical priority is made.


## Assurance-hardening resource boundary

The hardening phase theory distinguishes two certified-action contracts. Under **conflict-free** compensation, registered certified actions may be composed freely. Under **exclusive-resource** compensation, selected actions must respect declared resource incompatibilities. The phase theorem does not infer resource conflicts from deployment labels; they must be declared by the encoding.

Complexity statements use explicitly represented finite scenarios, routes, actions, and resource claims. The fixed-target polynomial result does not apply to an implicitly represented exponentially large scenario universe.
