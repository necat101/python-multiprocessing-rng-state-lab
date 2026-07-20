# RESULTS

Python: 3.12.3

NumPy available: True
NumPy version: 2.4.6

PyTorch available: False

Start methods: fork, forkserver, spawn
Root seed: 26767441
Workers: 4
Draws per worker: 6
Cases: 10
Methods: 4
Rows: 40

## Classification counts

- pass: 25
- expected_duplicate: 4
- expected_distinct: 3
- local_observation: 0
- platform_skip: 0
- dependency_skip: 0
- context_only: 8
- not_applicable: 0
- fail: 0

## Observations

- Serial same-seed: duplicate sequences observed (expected).
- Fork legacy RNG: duplicate sequences observed (expected).
- Fork generator copy: duplicate sequences observed (expected).
- Fork worker_id reseed: distinct sequences, reproducible.
- Fork SeedSequence children: distinct sequences, reproducible.
- Spawn same seed: duplicate sequences observed (expected).
- Spawn SeedSequence children: distinct sequences, reproducible.
- Spawn repeatability: pass.

## Distinctions

- duplicate sequence observations: yes, in deliberately constructed same-seed cases
- distinct sequence observations: yes, with per-worker SeedSequence
- repeatability observations: yes, deterministic per worker_id
- platform availability: fork=True, spawn=True
- dependency availability: numpy=True, torch=False
- broader claims not tested: see no_global_rng_or_ml_validity_claim_marker

## Evidence categories

1. What the linked article claimed in 2021: RNG state duplication via fork in PyTorch DataLoader workers; claimed "over 95%" prevalence – attributed to the article, NOT reproduced by this repository.

2. What Hacker News commenters argued: _coveredInBees (worker seeding easy to get wrong, custom worker_init_fn), nurpax (torch.utils.data.get_worker_info().seed), shoyer (against hidden mutable global RNG, prefer explicit Generator), warsheep (explicit generator state can still be copied by fork), acdha (fork optimization makes RNG init easy to misunderstand), OskarS (programmers treat PRNG as true randomness), timzaman (python/numpy/torch/distributed each need deliberate seeding), jeeeb (unit tests may miss worker-process-only problems), _delirium (fork vs Windows spawn), ynik (macOS changed multiprocessing default, favor explicit start-method), rurban (reseeding workers while preserving reproducibility), anon_tor_12345 (challenged clickbait framing and unsupported "over 95%" claim).

3. What current official Python, NumPy, and PyTorch documentation says: see README.md links (multiprocessing fork/spawn, random, numpy.random.Generator, SeedSequence, parallel RNG, PyTorch data-loading / randomness).

4. What the local installed environment reported: Python 3.12.3 CPython, NumPy 2.4.6, PyTorch not available, OS posix, start_methods fork/forkserver/spawn.

5. What the deterministic lab directly observed: serial same-seed duplicate, fork legacy duplicate, fork generator duplicate, fork worker_id distinct+reproducible, fork SeedSequence distinct+reproducible, spawn same-seed duplicate, spawn SeedSequence distinct+reproducible, spawn repeatability pass.

6. What the lab did NOT test: ML training, RNG statistical quality, security, GPU, full PyTorch DataLoader, production pipeline validation, cross-version reproducibility, statistical independence, model accuracy impact, article's GitHub-scale percentage.

This lab does not prove numpy is unsafe, pytorch dataloaders are broken, RNG quality, ML augmentation validity, article github-wide percentage, statistical independence, full reproducibility, or production-readiness.
