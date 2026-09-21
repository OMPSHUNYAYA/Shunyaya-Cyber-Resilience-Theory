# SCRT Cryptographic Integrity Scope Policy v2.18.0

SCRT uses a two-layer integrity model.

## Frozen computational and machine-readable core

SHA-256 binding covers the canonical algorithm implementation, current principal/independent verification programs, generated falsification verifier, historical regression implementations, theorem record, claim map, dependency map, regression manifest, and verification metrics.

## Editable scientific presentation layer

README material, theorem/proof Markdown, threat-model and encoding-contract prose, research-positioning documents, examples, licenses, notices, workflow files, citation metadata, verification guides, and package manifests are intentionally outside the frozen computational identity.

This permits scientific exposition, navigation, and clarification to improve without silently changing the bound computational theorem identity.

## Presentation-file guard

The root verifier rejects any bound-core entry whose path is a Markdown, text, citation, workflow, README, license, or notice presentation artifact. This prevents editable scientific exposition from being accidentally incorporated into the frozen computational identity.
