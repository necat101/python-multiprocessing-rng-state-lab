# python-multiprocessing-rng-state-lab

Deterministic correctness lab for NumPy PRNG state inheritance across Python multiprocessing start methods (fork / spawn).

This is a **correctness and evidence lab**, not an ML benchmark, randomness certification, statistical-quality test, or security test.

- Root seed: `26767441`
- Workers: 4 (ids 0,1,2,3)
- Draws per worker: 6 integers in `[0, 1000000)`
- No model training, no GPU, no downloads, no pip installs
- Python stdlib + NumPy only (PyTorch inspected for version if present, not required)

## Hacker News thread access

```
hackernews get-item --id 26767441
```

Relevant public thread evidence was captured before the discussion summary was written. See `hn_thread_evidence.md` and `hn_comments_sanitized.json`.

## Discussion summary (HN #26767441)

The thread discusses "A common mistake when NumPy's RNG is used with PyTorch" (tanelp.github.io, 2021).

Commenter summary:

- **_coveredInBees**: worker seeding is easy to get wrong even in official tutorials; described using a custom `worker_init_fn` (`np.random.seed(torch.initial_seed() // 2**32 + id)`) and making it the default for all trainer instances.
- **nurpax**: pointed to the worker-specific seed exposed by PyTorch: `torch.utils.data.get_worker_info().seed`, suggested `worker_init_fn=lambda id: np.random.seed(torch.utils.data.get_worker_info().seed)`.
- **shoyer**: argued against hidden mutable global RNG state and preferred explicit generator state (`numpy.random.Generator`); JAX goes further with pure functions. Explicit state avoids spooky action-at-a-distance.
- **warsheep**: replied that an explicitly created generator can still have its state copied by fork – explicit ownership helps reasoning, but does not magically avoid fork-copy.
- **acdha**: described fork as an optimization that makes setup such as RNG initialization easy to misunderstand and easy for tutorials to omit, especially when seed/fork are far apart in non-trivial programs.
- **OskarS**: said some programmers mentally treat pseudorandom values as fresh external randomness ("give me random numbers"), not as a deterministic seeded sequence – they think they're reading `/dev/random`, not `rand()`.
- **timzaman**: warned that python, numpy, torch, and distributed workers may each need deliberate seeding; also noted multi-GPU data-parallel seed duplication.
- **jeeeb**: said ordinary unit tests may miss a problem that appears only with worker processes; recommended logging input samples to TensorBoard.
- **_delirium**: distinguished fork-based behavior (children inherit RNG state, produce identical sequences) from Windows spawn behavior (fresh interpreter).
- **ynik**: noted that macOS changed its multiprocessing default (Python 3.8+, spawn on macOS), favored explicit cross-platform start-method choices (`multiprocessing.set_start_method('spawn')`).
- **rurban**: discussed reseeding workers while preserving reproducibility; noted forked/threaded RNGs keeping the same seed is a well-known trap; good RNGs have an advance function.
- **anon_tor_12345**: challenged the article's clickbait framing and its unsupported "over 95%" prevalence claim; noted no actual stats, just hand-waving, and that PyTorch exposes `worker_init_fn`.

## What the thread does NOT prove

- that every NumPy program duplicates random sequences
- that every PyTorch DataLoader currently has the historical behavior described by the 2021 article
- that explicit generator objects cannot be copied
- that spawn automatically makes poorly seeded code correct
- that different sequences are statistically independent merely because they differ
- that repeated augmentations necessarily damage model quality
- that one deterministic multiprocessing experiment measures production training behavior
- that the article's repository-wide percentage has been independently reproduced

## Evidence categories

1. **What the linked article claimed in 2021**: RNG state duplication via fork in PyTorch DataLoader workers can lead to identical augmentations; claimed "over 95%" prevalence across open-source ML projects (attributed to the article – this repository does **not** reproduce the article's GitHub-scale analysis).

2. **What Hacker News commenters argued**: see Discussion summary above.

3. **What current official Python, NumPy, and PyTorch documentation says**:
   - Python `multiprocessing`: https://docs.python.org/3/library/multiprocessing.html – fork copies process state, spawn starts fresh interpreter
   - Python `random`: https://docs.python.org/3/library/random.html
   - NumPy random: https://numpy.org/doc/stable/reference/random/index.html
   - NumPy Generator: https://numpy.org/doc/stable/reference/random/generator.html
   - NumPy parallel RNG: https://numpy.org/doc/stable/reference/random/parallel.html
   - NumPy SeedSequence: https://numpy.org/doc/stable/reference/random/bit_generators/generated/numpy.random.SeedSequence.html
   - PyTorch data-loading: https://docs.pytorch.org/docs/stable/data.html
   - PyTorch reproducibility: https://docs.pytorch.org/docs/stable/notes/randomness.html

4. **What the local installed environment reported**: see `observations.json`, `RESULTS.md` – Python 3.12.3, NumPy 2.4.6, PyTorch not installed, start methods: fork, forkserver, spawn.

5. **What the deterministic lab directly observed**:
   - Serial same-seed: duplicate sequences (expected)
   - Fork legacy RNG: duplicate sequences (expected)
   - Fork generator copy: duplicate sequences (expected)
   - Fork worker_id reseed: distinct sequences, reproducible
   - Fork SeedSequence children: distinct sequences, reproducible
   - Spawn same seed: duplicate sequences (expected)
   - Spawn SeedSequence children: distinct sequences, reproducible
   - Spawn repeatability: pass

6. **What the lab did NOT test**: ML training, RNG statistical quality, security, GPU/accelerator behavior, full PyTorch DataLoader stack, production pipeline validation, cross-version reproducibility, statistical independence proofs, model accuracy impact.

## Cases

1. `runtime_and_start_methods_marker`
2. `serial_same_seed_baseline_marker`
3. `fork_legacy_global_state_copy_marker`
4. `fork_generator_object_copy_marker`
5. `fork_worker_id_reseed_marker`
6. `fork_seedsequence_children_marker`
7. `spawn_same_seed_marker`
8. `spawn_seedsequence_children_marker`
9. `spawn_repeatability_across_runs_marker`
10. `no_global_rng_or_ml_validity_claim_marker`

Each case tested with 4 methods: `inspect_environment`, `execute_workers`, `verify_sequence_relation`, `reproducibility_context_observation` → 40 rows total.

## Reproduce

```bash
python run_lab.py
python -m unittest -v
```

## License

MIT
