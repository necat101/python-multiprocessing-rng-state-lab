# python-multiprocessing-rng-state-lab

A small deterministic Python correctness lab about NumPy pseudorandom state, multiprocessing start methods, fork state inheritance, repeated explicit seeds, per-worker seed derivation, numpy.random.Generator, numpy.random.SeedSequence.spawn, worker-result ordering, and reproducibility across repeated runs.

This is a correctness and evidence lab. It is not a machine-learning benchmark, a randomness certification, a statistical-quality test, a security test, or a claim about the current behavior of every PyTorch version.

No model training, no GPU, no pip installs. Python stdlib + NumPy only.

## Lab parameters

- Root seed: 26767441
- Workers: 0, 1, 2, 3
- Draws per worker: 6
- Interval: [0, 1000000)
- Results sorted by worker_id before recording

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

Each case implements four methods: `inspect_environment`, `execute_workers`, `verify_sequence_relation`, `reproducibility_context_observation` — 40 rows total.

## Results summary

See [RESULTS.md](RESULTS.md) for full classification counts, sequence observations, and disclaimers.

Duplicate streams observed (expected): serial same-seed, fork legacy global state copy, fork generator object copy, spawn same-seed.

Distinct streams observed (expected): fork worker-id reseed, fork SeedSequence children, spawn SeedSequence children.

Repeatability confirmed per worker_id across repeated runs.

## Hacker News thread access

Relevant public thread evidence was captured before the discussion summary was written.

Command:

```
hackernews get-item --id 26767441
```

Thread: https://news.ycombinator.com/item?id=26767441  
Linked article: https://tanelp.github.io/posts/a-bug-that-plagues-thousands-of-open-source-ml-projects/

Evidence files: [hn_thread_evidence.md](hn_thread_evidence.md), [hn_comments_sanitized.json](hn_comments_sanitized.json)

### What the linked article claimed in 2021

The article described a NumPy / PyTorch DataLoader interaction where forked worker processes inherit identical RNG state, leading to duplicated data augmentations across workers. It claimed the issue affected “thousands of open source ML projects” and included a GitHub-wide prevalence estimate (“over 95%”). This repository attributes that percentage to the article and does **not** reproduce the article’s GitHub-scale analysis.

### What Hacker News commenters argued

- **_coveredInBees**: worker seeding is easy to get wrong even in official tutorials; described using a custom `worker_init_fn` (`worker_init_fn=lambda id: np.random.seed(torch.initial_seed() // 2**32 + id)`) as a default in their PyTorch training framework.
- **nurpax**: pointed to the worker-specific seed exposed by PyTorch (`torch.utils.data.get_worker_info().seed`) as a basis for `worker_init_fn`.
- **shoyer**: argued against hidden mutable global RNG state; preferred explicit generator state (`numpy.random.Generator`); JAX-style pure functions avoid “action at a distance” and improve reproducibility.
- **warsheep**: replied that an explicitly created generator can still have its state copied by fork; the fix is reseeding after fork or using multiprocess-aware RNG APIs.
- **acdha**: described fork as an optimization that makes setup such as RNG initialization easy to misunderstand and easy for tutorials to omit; boilerplate gets ignored once code is non-trivial.
- **OskarS**: said some programmers mentally treat pseudorandom values as fresh external randomness (“give me random numbers”), not a seeded pseudo-random sequence, so identical sequences after fork are surprising.
- **timzaman**: warned that Python, NumPy, Torch, and distributed workers may each need deliberate seeding; multi-GPU data-parallel workers need distinct seeds too.
- **jeeeb**: said ordinary unit tests may miss a problem that appears only with worker processes; also noted DataLoader `num_workers != 0` is required to trigger.
- **_delirium**: distinguished fork-based behavior from Windows spawn behavior; NumPy auto-seeds from OS entropy by default, the fork-inheritance case is the subtle one; PyTorch DataLoaders fork transparently.
- **ynik**: noted that macOS changed its multiprocessing default (Python 3.8+ uses spawn on macOS); favored explicit cross-platform start-method choices (`multiprocessing.set_start_method('spawn')`).
- **rurban**: discussed reseeding workers while preserving reproducibility; for splitting sequential ranges, a good RNG typically has an advance function.
- **anon_tor_12345**: challenged the article’s clickbait framing and its unsupported “over 95%” prevalence claim; argued the issue is “using fork without understanding fork”, not NumPy-specific; noted PyTorch exposes `worker_init_fn` and questioned the lack of statistics backing the GitHub-wide claim.

### What current official documentation says

- Python multiprocessing: https://docs.python.org/3/library/multiprocessing.html — documents `fork`, `spawn`, `forkserver` start methods; `fork` copies process state including RNG state.
- Python random: https://docs.python.org/3/library/random.html
- NumPy random: https://numpy.org/doc/stable/reference/random/index.html
- NumPy Generator: https://numpy.org/doc/stable/reference/random/generator.html
- NumPy parallel random generation: https://numpy.org/doc/stable/reference/random/parallel.html
- NumPy SeedSequence: https://numpy.org/doc/stable/reference/random/bit_generators/generated/numpy.random.SeedSequence.html — `SeedSequence.spawn()` creates child streams intended for parallel use.
- PyTorch data loading: https://docs.pytorch.org/docs/stable/data.html
- PyTorch reproducibility: https://docs.pytorch.org/docs/stable/notes/randomness.html

### What the local installed environment reported

See RESULTS.md — Python 3.12.3, NumPy 2.4.6, PyTorch not installed, start methods: fork, spawn, forkserver.

We do not claim the installed versions are current or universally deployed.

### What the deterministic lab directly observed

- Constructing multiple `numpy.random.Generator` instances from the same explicit seed reproduces the same stream by design.
- Forked children inheriting a legacy `RandomState` or a `Generator` object produced identical sequences across 4 workers.
- Per-worker seed derivation via `SeedSequence([ROOT_SEED, worker_id])` produced pairwise distinct sequences, reproducible per worker_id.
- `SeedSequence.spawn(4)` child streams produced pairwise distinct sequences (fork and spawn), reproducible per worker_id.
- Spawned children given the same explicit seed produced identical sequences.
- Two consecutive spawn-SeedSequence runs produced identical per-worker sequences.

All observations are for 4 workers, 6 integers each, seed 26767441, on the tested platform only.

### What the lab did NOT test

This repository does not prove that every NumPy or PyTorch program has duplicated RNG streams, that the historical PyTorch behavior remains unchanged today, that fork is the default everywhere, that spawn repairs repeated explicit seeds, that NumPy generators are automatically independent after copying, that distinct short sequences are statistically independent, that SeedSequence eliminates every collision risk, that a six-number sample tests RNG quality, that duplicated augmentation necessarily changes model accuracy, that different augmentations improve model quality, that a random seed alone guarantees full experimental reproducibility, that one local multiprocessing run validates a production data pipeline, or that the lab is machine-learning validated, statistically certified, universally portable, or production-ready.

## Running

```
python run_lab.py
python -m unittest -v
```

Generated artifacts: `observations.json`, `observations.csv`, `RESULTS.md`

## License

MIT
