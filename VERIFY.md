# VERIFY.md

Repository: https://github.com/necat101/python-multiprocessing-rng-state-lab
Implementation SHA: 8e353f677c770bae218524d674f6ead6f22db21d

## Clean checkout verification

Clone and checkout:
```
git clone https://github.com/necat101/python-multiprocessing-rng-state-lab /clean-checkout
cd /clean-checkout
git checkout 8e353f677c770bae218524d674f6ead6f22db21d
```

Environment:
- Python version: 3.12.3
- Python implementation: CPython
- OS family: posix (Linux)
- NumPy available: True
- NumPy version: 2.4.6
- PyTorch available: False
- PyTorch version: N/A
- Available start methods: fork, forkserver, spawn
- Fork available: True
- Spawn available: True

Commands:
```
python -m py_compile run_lab.py test_lab.py
# exit code: 0

python run_lab.py
# exit code: 0

python -m unittest -v
# tests discovered: 26
# tests executed: 26
# tests skipped: 0
# tests failed: 0
# exit code: 0

./run.sh
# exit code: 0 – runs py_compile → run_lab → unittest end-to-end
```

Results:
- Cases: 10
- Methods: 4
- Rows: 40
- Classification counts:
  - pass: 12
  - expected_duplicate: 4
  - expected_distinct: 3
  - local_observation: 9
  - platform_skip: 0
  - dependency_skip: 0
  - context_only: 10
  - not_applicable: 2
  - fail: 0
- Fork cases ran: yes
- Spawn cases ran: yes
- Child-process failures: 0
- Dependency skips: 0
- Platform skips: 0

Artifact comparison:
- observations.json: bit-identical
- observations.csv: bit-identical
- RESULTS.md: bit-identical
- git diff --exit-code: 0

Scanner result: pass – no private paths, credentials, PIDs, hostnames, etc. found in committed artifacts, including run.sh / run.bat

Final status:
```
git status --porcelain
# (empty)
```

## Notes

Convenience wrappers added in the implementation commit:
- `run.sh` – Linux/macOS: py_compile → run_lab → unittest
- `run.bat` – Windows: py_compile → run_lab → unittest

Both wrappers are thin process invocators with no effect on lab results, exit codes, or generated artifacts. Test suite (26 tests) passes with wrappers present, including artifact scanner.

All 10 repair checklist items from the 2026-07-20 code review remain fixed:
1. exit-code tracking keyed by worker_id, never PID; fails on missing/None/nonzero
2. exit-code test exercises real production path
3. missing/invalid handler classification → fail via real row builder
4. timeout conversion tested via production boundary
5. observations include per-worker exit codes, seed entropy, spawn keys, sequences, and structured repeatability result sets
6. scanner: complete category coverage, narrow line-specific allowances only
7. RESULTS tests compare exact counts and substantive values
8. classification totals verify every bucket
9. deterministic worker ordering, no PIDs/hostnames/paths/timestamps, all required files present (including run.sh/run.bat)
10. HN discussion covers all 12 commenters, evidence categories separated, "over 95%" attributed

## Narrow conclusions

- Serial same-seed: duplicate sequences observed (expected)
- Fork legacy RNG: duplicate sequences observed (expected)
- Fork generator copy: duplicate sequences observed (expected)
- Fork worker_id reseed: distinct sequences, reproducible
- Fork SeedSequence children: distinct sequences, reproducible
- Spawn same seed: duplicate sequences observed (expected)
- Spawn SeedSequence children: distinct sequences, reproducible
- Spawn repeatability: pass

This lab does not prove numpy is unsafe, pytorch dataloaders are broken, RNG quality, ML augmentation validity, article github-wide percentage, statistical independence, full reproducibility, or production-readiness.
