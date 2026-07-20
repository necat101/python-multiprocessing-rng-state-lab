# VERIFY

Repository: https://github.com/necat101/python-multiprocessing-rng-state-lab

Implementation SHA: b45a72a3c764448244fcf06d808159f0ccff45ff

## Clean checkout verification

```
git clone https://github.com/necat101/python-multiprocessing-rng-state-lab.git /clean-checkout
cd /clean-checkout
git checkout b45a72a3c764448244fcf06d808159f0ccff45ff
python -m py_compile run_lab.py test_lab.py
python run_lab.py
python -m unittest -v
```

- Python version: 3.12.3
- NumPy available: True, version: 2.4.6
- PyTorch available: False, version: None
- Platform family: posix (Linux)
- Available multiprocessing start methods: fork, spawn, forkserver
- Commands exit codes: py_compile 0, run_lab 0, unittest 0
- Tests discovered: 26
- Tests executed: 26
- Tests skipped: 0
- Tests failed: 0

## Lab counts

- Cases: 10
- Methods per case: 4
- Rows: 40

Classification buckets (actual):
- pass: 12
- expected_duplicate: 4
- expected_distinct: 3
- local_observation: 9
- platform_skip: 0
- dependency_skip: 0
- context_only: 10
- not_applicable: 2
- fail: 0

Fork skips: 0
Dependency skips: 0
Child-process failures: 0

## Artifact comparison

Regenerated in clean checkout:
- observations.json – bit-identical
- observations.csv – bit-identical
- RESULTS.md – bit-identical

`git diff --exit-code` → exit 0

Working tree after regeneration:
```
git status --porcelain
```
(empty)

## Scanner

Artifact scanner (test_lab.TestLab.test_artifact_scanner) – PASS
No private paths, credentials, PIDs, hostnames, or object addresses in committed artifacts.

## Conclusions (narrow)

- Duplicate sequence observations matched expectations for serial same-seed, fork legacy global state, fork generator object copy, and spawn same-seed.
- Distinct sequence observations matched expectations for fork worker-id reseed, fork SeedSequence children, and spawn SeedSequence children.
- Repeatability per worker_id confirmed across repeated runs.
- No platform or dependency skips on this Linux / CPython 3.12 / NumPy 2.4.6 environment.
- No failures.

This verification does not prove NumPy is unsafe, PyTorch DataLoaders are broken, RNG quality is validated, ML augmentation is validated, the article's GitHub-wide percentage is reproduced, statistical independence is guaranteed, full experiment reproducibility is guaranteed, or that the lab is production-ready.
