# SCRT Verification Guide v2.18.0

Run from the repository root:

```bash
python -B verify.py --self-test
python -B verify.py --verify
```

`--self-test` checks repository integrity and compact algorithm smoke tests.

`--verify` additionally runs historical regression self-tests, current principal and independent theorem implementations, generated finite-system falsification, assumption-sharpness countermodels, adversarial phase verification, and reduction replay.

Historical regression implementations remain directly runnable with their own `--verify` modes when a predecessor theorem needs full replay. The root verification intentionally uses compact predecessor self-tests and reserves full verification for the current principal/independent theorem components.

All bundled verification scripts use the Python standard library and require no network connection.

Executable verification is finite evidence. Universal theorem claims are supplied by the written proofs in `01_Theory/`.
