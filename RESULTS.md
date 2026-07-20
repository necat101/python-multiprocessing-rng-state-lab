# RESULTS

Python version: 3.12.3
NumPy available: True, version: 2.4.6
PyTorch available: False, version: None
Start methods: fork, spawn, forkserver
Root seed: 26767441
Workers: 4, draws per worker: 6
Rows: 40 (10 cases × 4 methods)

## Classification buckets
- pass: 12
- expected_duplicate: 4
- expected_distinct: 3
- local_observation: 9
- platform_skip: 0
- dependency_skip: 0
- context_only: 10
- not_applicable: 2
- fail: 0

## Observations
- serial_same_seed_baseline: expected_duplicate
- fork_legacy_state: expected_duplicate
- fork_generator_copy: expected_duplicate
- fork_worker_id_reseed: expected_distinct
- fork_seedsequence_children: expected_distinct
- spawn_same_seed: expected_duplicate
- spawn_seedsequence_children: expected_distinct
- spawn_repeatability: pass

Platform skips: 0
Dependency skips: 0
Failures: 0

## What was observed
- Duplicate sequence observations: serial same-seed, fork legacy global state copy, fork generator object copy, spawn same-seed – all produced identical sequences across workers when deliberately seeded identically or inheriting state via fork.
- Distinct sequence observations: fork worker-id reseed, fork SeedSequence children, spawn SeedSequence children – all produced pairwise distinct sequences per worker.
- Repeatability observations: worker-id reseed, SeedSequence children (fork and spawn), and spawn repeatability across runs – sequences were exactly reproducible per worker id across repeated runs.
- Platform availability: fork=yes, spawn=yes.
- Dependency availability: numpy=True, torch=False.

## What was NOT tested / disclaimed
This repository does not prove that every numpy or pytorch program has duplicated rng streams, that historical pytorch behavior remains unchanged today, that fork is the default everywhere, that spawn repairs repeated explicit seeds, that numpy generators are automatically independent after copying, that distinct short sequences are statistically independent, that SeedSequence eliminates every collision risk, that a six-number sample tests rng quality, that duplicated augmentation necessarily changes model accuracy, that different augmentations improve model quality, that a random seed alone guarantees full experimental reproducibility, that one local multiprocessing run validates a production data pipeline, or that the lab is machine-learning validated, statistically certified, universally portable, or production-ready.

See README.md for Hacker News discussion summary, article attribution, and documentation references.
