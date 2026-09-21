# SCRT Verification Scope v2.18.0

## Repository integrity

`verify.py --self-test` checks repository structure, bound-core hashes, machine-readable records, local README links, line endings, and repository hygiene. These checks do not evaluate universal mathematics.

## Finite mathematical evidence

`verify.py --verify` adds historical regression self-tests, generated finite-system falsification and assumption-sharpness countermodels, current continuation-classification principal/independent verification, the v2.10/v2.16/v2.17 hardening-phase principal/independent verification programs, and the v2.18 adversarial hardening-phase verification layer.

These are finite checks and reduction replays. They can expose counterexamples or implementation disagreement but are not proof assistants.

## Written proof scope

Universal claims are carried by the written theorem documents under explicit finite SCRT hypotheses.

`proof_status: WRITTEN_COMPLETE_NOT_MECHANIZED`

## Historical replay

Every bound historical regression implementation remains directly runnable with its own `--verify` mode. Those full historical modes are not aggregated into the root verification contract because their combined runtime is intentionally unbounded by the repository workflow.
