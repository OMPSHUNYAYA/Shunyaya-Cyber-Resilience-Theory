# SCRT Cyber Architecture Encoding Contract v2.18.0

## Purpose

SCRT separates the modeling of a cyber architecture from the mathematical classification of an admitted SCRT state.

`real or designed cyber architecture -> SCRT encoding`

is a modeling step.

`admissible SCRT encoding -> continuation classification`

is the theorem step.

The continuation theorems apply to the declared SCRT encoding and its registered operation/observer contract. They do not establish that the source architecture has been modeled completely or that implementation evidence is authentic.

## Required encoding declarations

An admissible encoding declares, as applicable to its semantic level:

- a finite set of named security obligations;
- a finite dependency-ancestry interface;
- operational defensive-route families;
- typed certified-route families `(D,E)` with explicit defensive and evidence ancestry;
- the physical-independence rule used for complete realizations;
- compromise semantics, including role-polarized channels where used;
- permanent hardening and adaptive recovery operations;
- semantic anchors and anonymous ancestry classes;
- allowed gauge permutations;
- cost and resource claims for attacker and defender actions;
- target capacity `k` for target-relative semantics;
- action timing and persistence rules for campaign semantics;
- the registered continuation generator family;
- the registered observer or campaign-value profile.

## Well-formedness conditions

The encoding must satisfy the following structural conditions before a theorem layer is applied:

1. every route references declared ancestry identities;
2. every typed signature satisfies `D intersect E = empty`;
3. every certified physical support is evaluated as `D union E` for independence unless a theorem explicitly states another rule;
4. named obligations are distinct semantic anchors when obligation-targeted continuation is admitted;
5. anonymous ancestry may be quotiented only under declared gauge-compatible continuation;
6. target saturation is applied only when operation availability and observation are target-local;
7. campaign residual minimization is applied only to a finite registered target-saturated campaign state system and finite registered extension alphabet;
8. costs and resource claims are finite declared control state where required;
9. all action timing, persistence, and reuse rules are explicit.

## Modeling responsibility

The encoding step determines what real-world distinctions enter the mathematical model.

Examples of modeling choices that SCRT does not infer automatically include:

- whether two controls truly share one administrative authority;
- whether two evidence sources are genuinely independent;
- whether a backup or telemetry source should be trusted;
- whether an attacker action can affect one or several ancestry components;
- whether a recovery action remains available after a particular compromise;
- whether a resource conflict is physical, administrative, temporal, or policy-defined;
- whether an identity should be semantically anchored or treated as anonymous.

The classification theorem cannot recover a distinction omitted from the encoding contract.

## Classification responsibility

Once a state is admitted, the SCRT theorem layer determines continuation equivalence relative to the declared contract.

For `C=(S,G,O)`:

`x ~_C y`

iff

`O(w.x)=O(w.y)`

for every admitted finite well-typed continuation word `w`.

The canonical quotient is therefore complete and information-minimal only for the registered mathematical semantics.

## Validation boundary

SCRT does not by itself establish:

- correctness of a deployed control implementation;
- authenticity or completeness of evidence;
- absence of undeclared dependencies;
- completeness of the registered attacker grammar;
- completeness of the registered recovery grammar;
- correctness of externally supplied costs, budgets, or resource constraints;
- operational safety of a physical deployment;
- regulatory or certification conformity.

Those remain separate validation obligations.

## Reimplementation requirement

An independent implementation claiming compatibility with SCRT v2.18.0 should preserve:

- the declared finite interface and obligation identities;
- route typing and physical-support rules;
- exact or target-saturated multiplicity semantics appropriate to the contract;
- gauge anchors and permitted anonymity;
- action timing, cost, resource, and persistence rules;
- observer definitions;
- canonical quotient equality under the corresponding continuation contract.


## Assurance-hardening declarations

An encoding that invokes the v2.18 hardening phase theorem must additionally declare:

- the operational hardening action library and the operational routes supplied by each action;
- the certified compensation action library and typed certified routes supplied by each action;
- nonnegative action costs when `ACI_k` is queried;
- the explicit finite compromise-scenario family used for design/audit questions; and
- whether certified actions are conflict-free or carry exclusive resource claims.

The theorem classifies the declared mathematical instance. It does not infer whether two real recovery actions actually share a resource, whether a claimed independence relation is operationally valid, or whether the scenario family is complete.
