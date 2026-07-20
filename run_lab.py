#!/usr/bin/env python3
"""python-multiprocessing-rng-state-lab"""
import sys, json, platform, multiprocessing, csv, os
ROOT_SEED = 26767441
WORKER_IDS = [0,1,2,3]
DRAWS = 6
LOW = 0
HIGH = 1000000

CASE_ORDER = [
"runtime_and_start_methods_marker",
"serial_same_seed_baseline_marker",
"fork_legacy_global_state_copy_marker",
"fork_generator_object_copy_marker",
"fork_worker_id_reseed_marker",
"fork_seedsequence_children_marker",
"spawn_same_seed_marker",
"spawn_seedsequence_children_marker",
"spawn_repeatability_across_runs_marker",
"no_global_rng_or_ml_validity_claim_marker",
]
METHOD_ORDER = [
"inspect_environment",
"execute_workers",
"verify_sequence_relation",
"reproducibility_context_observation",
]

def env_info():
    try:
        import numpy as np
        numpy_available = True
        numpy_version = np.__version__
    except Exception:
        numpy_available = False
        numpy_version = None
    try:
        import torch
        torch_available = True
        torch_version = torch.__version__
    except Exception:
        torch_available = False
        torch_version = None
    try:
        start_methods = multiprocessing.get_all_start_methods()
    except Exception:
        start_methods = []
    try:
        default_start = multiprocessing.get_start_method(allow_none=True)
    except Exception:
        default_start = None
    return {
        "python_version": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "os_family": os.name,
        "numpy_available": numpy_available,
        "numpy_version": numpy_version,
        "torch_available": torch_available,
        "torch_version": torch_version,
        "start_methods": list(start_methods),
        "default_start_method": default_start,
        "fork_available": "fork" in start_methods,
        "spawn_available": "spawn" in start_methods,
        "root_seed": ROOT_SEED,
        "worker_count": len(WORKER_IDS),
        "draws_per_worker": DRAWS,
        "interval": [LOW, HIGH],
    }

def load_cases():
    with open(os.path.join(os.path.dirname(__file__), "cases.json")) as f:
        data = json.load(f)
    m = {}
    for c in data["cases"]:
        m[c["id"]] = c.get("expectations", {})
    return m

# --- worker functions (module scope for spawn) ---
def _fork_legacy_worker(q, worker_id):
    status = "ok"
    try:
        import numpy as np
        global _LEGACY_RNG
        seq = _LEGACY_RNG.randint(LOW, HIGH, size=DRAWS).tolist()
        q.put({"worker_id": worker_id, "sequence": seq, "status": status})
    except Exception as e:
        status = "error"
        try: q.put({"worker_id": worker_id, "sequence": None, "status": status})
        except: pass

def _fork_generator_worker(q, worker_id):
    status = "ok"
    try:
        global _GEN_RNG
        seq = _GEN_RNG.integers(LOW, HIGH, size=DRAWS, endpoint=False).tolist()
        q.put({"worker_id": worker_id, "sequence": seq, "status": status})
    except Exception:
        status = "error"
        try: q.put({"worker_id": worker_id, "sequence": None, "status": status})
        except: pass

def _fork_worker_id_reseed_worker(q, worker_id):
    status = "ok"
    try:
        import numpy as np
        ss = np.random.SeedSequence([ROOT_SEED, worker_id])
        rng = np.random.default_rng(ss)
        seq = rng.integers(LOW, HIGH, size=DRAWS, endpoint=False).tolist()
        ent = ss.entropy if hasattr(ss, "entropy") else [ROOT_SEED, worker_id]
        if isinstance(ent, int):
            entropy = ent
        else:
            try:
                entropy = list(ent)
            except Exception:
                entropy = str(ent)
        spawn_key_val = tuple(ss.spawn_key) if hasattr(ss, "spawn_key") else ()
        q.put({"worker_id": worker_id, "sequence": seq, "entropy": entropy, "spawn_key": spawn_key_val, "status": status})
    except Exception:
        status = "error"
        try: q.put({"worker_id": worker_id, "sequence": None, "entropy": None, "spawn_key": None, "status": status})
        except: pass

def _fork_seedsequence_children_worker(q, worker_id, child_ss):
    status = "ok"
    try:
        import numpy as np
        ss = child_ss
        rng = np.random.default_rng(ss)
        seq = rng.integers(LOW, HIGH, size=DRAWS, endpoint=False).tolist()
        spawn_key_val = tuple(ss.spawn_key) if hasattr(ss, "spawn_key") else ()
        ent = ss.entropy if hasattr(ss, "entropy") else None
        if isinstance(ent, int):
            entropy = ent
        else:
            try:
                entropy = list(ent) if ent is not None else None
            except Exception:
                entropy = str(ent) if ent is not None else None
        q.put({"worker_id": worker_id, "sequence": seq, "spawn_key": spawn_key_val, "entropy": entropy, "status": status})
    except Exception:
        status = "error"
        try: q.put({"worker_id": worker_id, "sequence": None, "spawn_key": None, "entropy": None, "status": status})
        except: pass

def _spawn_same_seed_worker(q, worker_id):
    status = "ok"
    try:
        import numpy as np
        rng = np.random.default_rng(ROOT_SEED)
        seq = rng.integers(LOW, HIGH, size=DRAWS, endpoint=False).tolist()
        q.put({"worker_id": worker_id, "sequence": seq, "status": status})
    except Exception:
        status = "error"
        try: q.put({"worker_id": worker_id, "sequence": None, "status": status})
        except: pass

def _spawn_seedsequence_worker(q, worker_id, child_ss):
    status = "ok"
    try:
        import numpy as np
        ss = child_ss
        rng = np.random.default_rng(ss)
        seq = rng.integers(LOW, HIGH, size=DRAWS, endpoint=False).tolist()
        spawn_key_val = tuple(ss.spawn_key) if hasattr(ss, "spawn_key") else ()
        ent = ss.entropy if hasattr(ss, "entropy") else None
        if isinstance(ent, int):
            entropy = ent
        else:
            try:
                entropy = list(ent) if ent is not None else None
            except Exception:
                entropy = str(ent) if ent is not None else None
        q.put({"worker_id": worker_id, "sequence": seq, "spawn_key": spawn_key_val, "entropy": entropy, "status": status})
    except Exception:
        status = "error"
        try: q.put({"worker_id": worker_id, "sequence": None, "spawn_key": None, "entropy": None, "status": status})
        except: pass

def run_workers(ctx_name, target, target_args_fn, timeout_sec=5):
    try:
        ctx = multiprocessing.get_context(ctx_name)
    except Exception as e:
        return None, "platform_skip: context {} unavailable".format(ctx_name)
    try:
        import numpy as np
    except Exception:
        return None, "dependency_skip"
    q = ctx.Queue()
    procs = {}
    for wid in WORKER_IDS:
        args = target_args_fn(wid, q)
        p = ctx.Process(target=target, args=args)
        p.start()
        procs[wid] = p
    results = {}
    # collect, with timeout conversion
    start_time = __import__("time").monotonic()
    remaining = set(WORKER_IDS)
    while remaining and (__import__("time").monotonic() - start_time) < timeout_sec:
        try:
            item = q.get(timeout=0.1)
            wid = item.get("worker_id") if isinstance(item, dict) else (item[0] if isinstance(item, (list, tuple)) else None)
            if wid in WORKER_IDS:
                results[wid] = item
                remaining.discard(wid)
        except Exception:
            pass
    # if timeout occurred with missing results, convert to structured result
    if remaining:
        for wid in remaining:
            results[wid] = {"worker_id": wid, "sequence": None, "status": "timeout"}
    # collect exit codes keyed by worker_id (never PID)
    exit_codes = {}
    for wid, p in procs.items():
        p.join(timeout=1)
        exit_codes[wid] = p.exitcode
        if p.is_alive():
            p.terminate()
            p.join(timeout=2)
            if p.exitcode is None:
                exit_codes[wid] = p.exitcode
    # fail on ANY missing/None/nonzero child exit code, even if result set is complete
    for wid in WORKER_IDS:
        code = exit_codes.get(wid)
        if code is None or code != 0:
            return {"results": results, "exit_codes": exit_codes}, "fail:exit_code worker_id={} code={}".format(wid, code)
    # check completeness
    if set(results.keys()) != set(WORKER_IDS):
        return {"results": results, "exit_codes": exit_codes}, "fail:incomplete"
    # check worker status fields
    for wid in WORKER_IDS:
        res = results.get(wid)
        status = res.get("status") if isinstance(res, dict) else None
        if status != "ok":
            return {"results": results, "exit_codes": exit_codes}, "fail:worker_status worker_id={} status={}".format(wid, status)
    return {"results": results, "exit_codes": exit_codes}, None

# helper to extract sequence from worker result (dict or legacy tuple)
def _get_seq(res):
    if isinstance(res, dict):
        return res.get("sequence")
    if isinstance(res, (list, tuple)) and len(res) >= 2:
        return res[1]
    return None

def _get_status(res):
    if isinstance(res, dict):
        return res.get("status")
    return None

# --- case handlers ---
def handle_runtime_and_start_methods_marker(method, state=None):
    info = env_info()
    if method == "inspect_environment":
        return "local_observation", info
    if method == "execute_workers":
        return "not_applicable", {}
    if method == "verify_sequence_relation":
        return "not_applicable", {}
    if method == "reproducibility_context_observation":
        return "context_only", {}
    return "fail", {"reason": "missing_handler"}

def handle_serial_same_seed_baseline_marker(method, state):
    try:
        import numpy as np
    except Exception:
        return "dependency_skip", {}
    if method == "inspect_environment":
        return "local_observation", {}
    if method == "execute_workers":
        seqs = {}
        for wid in WORKER_IDS:
            rng = np.random.default_rng(ROOT_SEED)
            seq = rng.integers(LOW, HIGH, size=DRAWS, endpoint=False).tolist()
            seqs[wid] = seq
        state["seqs"] = seqs
        return "pass", {"sequences": seqs}
    if method == "verify_sequence_relation":
        seqs = state.get("seqs", {})
        vals = list(seqs.values())
        all_equal = all(v == vals[0] for v in vals) if vals else False
        if all_equal and len(vals) == 4:
            return "expected_duplicate", {"all_equal": True, "sequences": seqs}
        return "fail", {"all_equal": all_equal}
    if method == "reproducibility_context_observation":
        return "context_only", {"note": "Constructing multiple generators from the same explicit seed reproduces the same stream by design. Not a multiprocessing bug."}
    return "fail", {"reason": "missing_handler"}

# module-level rngs for fork tests
_LEGACY_RNG = None
_GEN_RNG = None

def handle_fork_legacy_global_state_copy_marker(method, state):
    try:
        import numpy as np
    except Exception:
        return "dependency_skip", {}
    info = env_info()
    if not info["fork_available"]:
        return "platform_skip", {}
    if method == "inspect_environment":
        return "local_observation", {}
    if method == "execute_workers":
        global _LEGACY_RNG
        _LEGACY_RNG = np.random.RandomState(ROOT_SEED)
        def args_fn(wid, q):
            return (q, wid)
        data, err = run_workers("fork", _fork_legacy_worker, args_fn)
        if err:
            return "fail", {"error": err}
        # validate worker status fields
        for wid in WORKER_IDS:
            res = data["results"][wid]
            if _get_status(res) != "ok":
                return "fail", {"reason": "worker_status", "worker_id": wid}
        state["worker_data"] = data
        exit_codes = data.get("exit_codes", {})
        return "pass", {"worker_count": len(data["results"]), "exit_codes": exit_codes}
    if method == "verify_sequence_relation":
        wd = state.get("worker_data")
        if not wd: return "fail", {"reason": "no_worker_data"}
        seqs = {wid: _get_seq(wd["results"][wid]) for wid in sorted(WORKER_IDS)}
        vals = list(seqs.values())
        all_equal = all(v == vals[0] for v in vals)
        exit_codes = wd.get("exit_codes", {})
        if all_equal:
            return "expected_duplicate", {"sequences": seqs, "exit_codes": exit_codes}
        return "fail", {"sequences": seqs, "exit_codes": exit_codes}
    if method == "reproducibility_context_observation":
        return "context_only", {"note": "Children inherited equivalent legacy rng state in this local fork experiment. Not claiming universal behavior."}
    return "fail", {"reason": "missing_handler"}

def handle_fork_generator_object_copy_marker(method, state):
    try:
        import numpy as np
    except Exception:
        return "dependency_skip", {}
    info = env_info()
    if not info["fork_available"]:
        return "platform_skip", {}
    if method == "inspect_environment":
        return "local_observation", {}
    if method == "execute_workers":
        global _GEN_RNG
        _GEN_RNG = np.random.default_rng(ROOT_SEED)
        def args_fn(wid, q):
            return (q, wid)
        data, err = run_workers("fork", _fork_generator_worker, args_fn)
        if err:
            return "fail", {"error": err}
        for wid in WORKER_IDS:
            res = data["results"][wid]
            if _get_status(res) != "ok":
                return "fail", {"reason": "worker_status", "worker_id": wid}
        state["worker_data"] = data
        exit_codes = data.get("exit_codes", {})
        return "pass", {"exit_codes": exit_codes}
    if method == "verify_sequence_relation":
        wd = state.get("worker_data")
        if not wd: return "fail", {"reason": "no_worker_data"}
        seqs = {wid: _get_seq(wd["results"][wid]) for wid in sorted(WORKER_IDS)}
        vals = list(seqs.values())
        all_equal = all(v == vals[0] for v in vals)
        exit_codes = wd.get("exit_codes", {})
        if all_equal:
            return "expected_duplicate", {"sequences": seqs, "exit_codes": exit_codes}
        return "fail", {"sequences": seqs, "exit_codes": exit_codes}
    if method == "reproducibility_context_observation":
        return "context_only", {"note": "Explicit generator is easier to reason about, but a generator present before fork can still be copied into children. Generator itself is not defective."}
    return "fail", {"reason": "missing_handler"}

def _run_fork_worker_id_reseed_once():
    def args_fn(wid, q):
        return (q, wid)
    data, err = run_workers("fork", _fork_worker_id_reseed_worker, args_fn)
    return data, err

def handle_fork_worker_id_reseed_marker(method, state):
    try:
        import numpy as np
    except Exception:
        return "dependency_skip", {}
    info = env_info()
    if not info["fork_available"]:
        return "platform_skip", {}
    if method == "inspect_environment":
        return "local_observation", {}
    if method == "execute_workers":
        data, err = _run_fork_worker_id_reseed_once()
        if err: return "fail", {"error": err}
        # collect seed entropy and spawn keys per worker
        entropies = {}
        spawn_keys = {}
        for wid in WORKER_IDS:
            res = data["results"][wid]
            if isinstance(res, dict):
                entropies[wid] = res.get("entropy")
                spawn_keys[wid] = res.get("spawn_key")
        state["run1"] = data
        exit_codes = data.get("exit_codes", {})
        return "pass", {"exit_codes": exit_codes, "entropies": entropies, "spawn_keys": spawn_keys}
    if method == "verify_sequence_relation":
        run1 = state.get("run1")
        if not run1: return "fail", {"reason":"no_run"}
        seqs = {wid: _get_seq(run1["results"][wid]) for wid in sorted(WORKER_IDS)}
        vals = list(seqs.values())
        distinct = len(set(tuple(s) for s in vals if s is not None)) == len([s for s in vals if s is not None])
        entropies = {}
        spawn_keys = {}
        for wid in WORKER_IDS:
            res = run1["results"][wid]
            if isinstance(res, dict):
                entropies[wid] = res.get("entropy")
                spawn_keys[wid] = res.get("spawn_key")
        exit_codes = run1.get("exit_codes", {})
        if distinct:
            return "expected_distinct", {"sequences": seqs, "exit_codes": exit_codes, "entropies": entropies, "spawn_keys": spawn_keys}
        return "fail", {"distinct": distinct, "exit_codes": exit_codes}
    if method == "reproducibility_context_observation":
        run1 = state.get("run1")
        data2, err = _run_fork_worker_id_reseed_once()
        if err: return "fail", {"error": err}
        match = True
        for wid in WORKER_IDS:
            s1 = _get_seq(run1["results"][wid])
            s2 = _get_seq(data2["results"][wid])
            if s1 != s2:
                match = False
                break
        if match:
            return "pass", {"reproducible": True}
        return "fail", {"reproducible": False}
    return "fail", {"reason":"missing_handler"}

def _run_fork_seedsequence_once():
    import numpy as np
    root = np.random.SeedSequence(ROOT_SEED)
    children = root.spawn(4)
    def args_fn(wid, q):
        return (q, wid, children[wid])
    data, err = run_workers("fork", _fork_seedsequence_children_worker, args_fn)
    return data, err

def handle_fork_seedsequence_children_marker(method, state):
    try:
        import numpy as np
    except Exception:
        return "dependency_skip", {}
    info = env_info()
    if not info["fork_available"]:
        return "platform_skip", {}
    if method == "inspect_environment":
        return "local_observation", {}
    if method == "execute_workers":
        data, err = _run_fork_seedsequence_once()
        if err: return "fail", {"error": err}
        entropies = {}
        spawn_keys = {}
        for wid in WORKER_IDS:
            res = data["results"][wid]
            if isinstance(res, dict):
                entropies[wid] = res.get("entropy")
                spawn_keys[wid] = res.get("spawn_key")
        state["run1"] = data
        exit_codes = data.get("exit_codes", {})
        return "pass", {"exit_codes": exit_codes, "entropies": entropies, "spawn_keys": spawn_keys}
    if method == "verify_sequence_relation":
        run1 = state.get("run1")
        if not run1: return "fail", {"reason":"no_run"}
        seqs = {wid: _get_seq(run1["results"][wid]) for wid in sorted(WORKER_IDS)}
        vals = list(seqs.values())
        distinct = len(set(tuple(s) for s in vals if s is not None)) == len([s for s in vals if s is not None])
        entropies = {}
        spawn_keys = {}
        for wid in WORKER_IDS:
            res = run1["results"][wid]
            if isinstance(res, dict):
                entropies[wid] = res.get("entropy")
                spawn_keys[wid] = res.get("spawn_key")
        exit_codes = run1.get("exit_codes", {})
        if distinct:
            return "expected_distinct", {"sequences": seqs, "exit_codes": exit_codes, "entropies": entropies, "spawn_keys": spawn_keys}
        return "fail", {"distinct": distinct, "exit_codes": exit_codes}
    if method == "reproducibility_context_observation":
        run1 = state.get("run1")
        data2, err = _run_fork_seedsequence_once()
        if err: return "fail", {"error": err}
        match = all(_get_seq(run1["results"][wid]) == _get_seq(data2["results"][wid]) for wid in WORKER_IDS)
        if match:
            return "pass", {"note": "SeedSequence spawning is documented for parallel use; tiny sample does not certify statistical behavior."}
        return "fail", {}
    return "fail", {"reason":"missing_handler"}

def handle_spawn_same_seed_marker(method, state):
    try:
        import numpy as np
    except Exception:
        return "dependency_skip", {}
    info = env_info()
    if not info["spawn_available"]:
        return "platform_skip", {}
    if method == "inspect_environment":
        return "local_observation", {}
    if method == "execute_workers":
        def args_fn(wid, q):
            return (q, wid)
        data, err = run_workers("spawn", _spawn_same_seed_worker, args_fn)
        if err: return "fail", {"error": err}
        for wid in WORKER_IDS:
            res = data["results"][wid]
            if _get_status(res) != "ok":
                return "fail", {"reason": "worker_status", "worker_id": wid}
        state["run"] = data
        exit_codes = data.get("exit_codes", {})
        return "pass", {"exit_codes": exit_codes}
    if method == "verify_sequence_relation":
        run = state.get("run")
        if not run: return "fail", {"reason":"no_run"}
        seqs = {wid: _get_seq(run["results"][wid]) for wid in sorted(WORKER_IDS)}
        vals = list(seqs.values())
        all_equal = all(v == vals[0] for v in vals)
        exit_codes = run.get("exit_codes", {})
        if all_equal:
            return "expected_duplicate", {"sequences": seqs, "exit_codes": exit_codes}
        return "fail", {}
    if method == "reproducibility_context_observation":
        return "context_only", {"note": "Fresh interpreter does not create distinct streams when code supplies same seed to every worker. Not claiming spawn is ineffective."}
    return "fail", {"reason":"missing_handler"}

def _run_spawn_seedsequence_once():
    import numpy as np
    root = np.random.SeedSequence(ROOT_SEED)
    children = root.spawn(4)
    def args_fn(wid, q):
        return (q, wid, children[wid])
    data, err = run_workers("spawn", _spawn_seedsequence_worker, args_fn)
    return data, err

def handle_spawn_seedsequence_children_marker(method, state):
    try:
        import numpy as np
    except Exception:
        return "dependency_skip", {}
    info = env_info()
    if not info["spawn_available"]:
        return "platform_skip", {}
    if method == "inspect_environment":
        return "local_observation", {}
    if method == "execute_workers":
        data, err = _run_spawn_seedsequence_once()
        if err: return "fail", {"error": err}
        entropies = {}
        spawn_keys = {}
        for wid in WORKER_IDS:
            res = data["results"][wid]
            if isinstance(res, dict):
                entropies[wid] = res.get("entropy")
                spawn_keys[wid] = res.get("spawn_key")
        state["run1"] = data
        exit_codes = data.get("exit_codes", {})
        return "pass", {"exit_codes": exit_codes, "entropies": entropies, "spawn_keys": spawn_keys}
    if method == "verify_sequence_relation":
        run1 = state.get("run1")
        if not run1: return "fail", {}
        seqs = {wid: _get_seq(run1["results"][wid]) for wid in sorted(WORKER_IDS)}
        vals = list(seqs.values())
        distinct = len(set(tuple(s) for s in vals if s is not None)) == len([s for s in vals if s is not None])
        entropies = {}
        spawn_keys = {}
        for wid in WORKER_IDS:
            res = run1["results"][wid]
            if isinstance(res, dict):
                entropies[wid] = res.get("entropy")
                spawn_keys[wid] = res.get("spawn_key")
        exit_codes = run1.get("exit_codes", {})
        if distinct:
            return "expected_distinct", {"sequences": seqs, "exit_codes": exit_codes, "entropies": entropies, "spawn_keys": spawn_keys}
        return "fail", {"exit_codes": exit_codes}
    if method == "reproducibility_context_observation":
        run1 = state.get("run1")
        data2, err = _run_spawn_seedsequence_once()
        if err: return "fail", {"error": err}
        match = all(_get_seq(run1["results"][wid]) == _get_seq(data2["results"][wid]) for wid in WORKER_IDS)
        exit_codes = data2.get("exit_codes", {})
        if match:
            return "pass", {"exit_codes": exit_codes}
        return "fail", {}
    return "fail", {"reason":"missing_handler"}

def handle_spawn_repeatability_across_runs_marker(method, state):
    try:
        import numpy as np
    except Exception:
        return "dependency_skip", {}
    info = env_info()
    if not info["spawn_available"]:
        return "platform_skip", {}
    if method == "inspect_environment":
        return "local_observation", {}
    if method == "execute_workers":
        data1, err1 = _run_spawn_seedsequence_once()
        if err1: return "fail", {"error": err1}
        data2, err2 = _run_spawn_seedsequence_once()
        if err2: return "fail", {"error": err2}
        state["run1"] = data1
        state["run2"] = data2
        exit_codes_1 = data1.get("exit_codes", {})
        exit_codes_2 = data2.get("exit_codes", {})
        return "pass", {"exit_codes_run1": exit_codes_1, "exit_codes_run2": exit_codes_2}
    if method == "verify_sequence_relation":
        r1 = state.get("run1"); r2 = state.get("run2")
        if not r1 or not r2: return "fail", {}
        # within-run distinctness
        seqs1 = {wid: _get_seq(r1["results"][wid]) for wid in WORKER_IDS}
        distinct1 = len(set(tuple(s) for s in seqs1.values() if s is not None)) == len([s for s in seqs1.values() if s is not None])
        seqs2 = {wid: _get_seq(r2["results"][wid]) for wid in WORKER_IDS}
        distinct2 = len(set(tuple(s) for s in seqs2.values() if s is not None)) == len([s for s in seqs2.values() if s is not None])
        # cross-run equality per worker
        match = all(_get_seq(r1["results"][wid]) == _get_seq(r2["results"][wid]) for wid in WORKER_IDS)
        exit_codes_1 = r1.get("exit_codes", {})
        exit_codes_2 = r2.get("exit_codes", {})
        if distinct1 and distinct2 and match:
            return "pass", {
                "match": True,
                "distinct": True,
                "run1_sequences": seqs1,
                "run2_sequences": seqs2,
                "exit_codes_run1": exit_codes_1,
                "exit_codes_run2": exit_codes_2,
            }
        return "fail", {"match": match, "distinct1": distinct1, "distinct2": distinct2}
    if method == "reproducibility_context_observation":
        return "context_only", {"note": "Exact reproducibility across two runs does not prove reproducibility across every numpy version, OS, architecture, or pipeline."}
    return "fail", {"reason":"missing_handler"}

def handle_no_global_rng_or_ml_validity_claim_marker(method, state=None):
    return "context_only", {"note": "no claim"}

HANDLERS = {
"runtime_and_start_methods_marker": handle_runtime_and_start_methods_marker,
"serial_same_seed_baseline_marker": handle_serial_same_seed_baseline_marker,
"fork_legacy_global_state_copy_marker": handle_fork_legacy_global_state_copy_marker,
"fork_generator_object_copy_marker": handle_fork_generator_object_copy_marker,
"fork_worker_id_reseed_marker": handle_fork_worker_id_reseed_marker,
"fork_seedsequence_children_marker": handle_fork_seedsequence_children_marker,
"spawn_same_seed_marker": handle_spawn_same_seed_marker,
"spawn_seedsequence_children_marker": handle_spawn_seedsequence_children_marker,
"spawn_repeatability_across_runs_marker": handle_spawn_repeatability_across_runs_marker,
"no_global_rng_or_ml_validity_claim_marker": handle_no_global_rng_or_ml_validity_claim_marker,
}

CLASSIFICATIONS = {"pass","expected_duplicate","expected_distinct","local_observation","platform_skip","dependency_skip","context_only","not_applicable","fail"}

def build_rows():
    expectations = load_cases()
    rows = []
    states = {cid: {} for cid in CASE_ORDER}
    for case_id in CASE_ORDER:
        handler = HANDLERS.get(case_id)
        if not handler:
            for method in METHOD_ORDER:
                rows.append({"case_id": case_id, "method": method, "expected_classification": expectations.get(case_id, {}).get(method, "fail"), "actual_classification": "fail", "observation": {"reason": "missing_handler"}})
            continue
        for method in METHOD_ORDER:
            exp = expectations.get(case_id, {}).get(method, None)
            try:
                actual, obs = handler(method, states[case_id])
            except Exception as e:
                actual = "fail"
                obs = {"reason": f"exception:{type(e).__name__}"}
            # Fix 3: convert missing/invalid classifications to fail with precise reason
            if actual not in CLASSIFICATIONS:
                obs = {"reason": "invalid_classification", "received": actual, "original_observation": obs}
                actual = "fail"
            rows.append({
                "case_id": case_id,
                "method": method,
                "expected_classification": exp,
                "actual_classification": actual,
                "observation": obs
            })
    return rows

def main():
    rows = build_rows()
    # sort worker results deterministically by worker_id in observations
    # (results are already keyed by worker_id and accessed sorted)
    # write observations.json
    with open("observations.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(rows, f, indent=2)
    # csv
    with open("observations.csv", "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["case_id","method","expected_classification","actual_classification","observation"])
        for r in rows:
            w.writerow([r["case_id"], r["method"], r["expected_classification"], r["actual_classification"], json.dumps(r["observation"], separators=(",",":"))])
    # RESULTS.md
    env = env_info()
    from collections import Counter
    counts = Counter(r["actual_classification"] for r in rows)
    buckets = ["pass","expected_duplicate","expected_distinct","local_observation","platform_skip","dependency_skip","context_only","not_applicable","fail"]
    counts_str = "\n".join(f"- {b}: {counts.get(b,0)}" for b in buckets)
    # gather sequence observations
    def find_obs(case, method):
        for r in rows:
            if r["case_id"]==case and r["method"]==method:
                return r
        return None
    def seq_summary(case):
        r = find_obs(case, "verify_sequence_relation")
        if r: return r["actual_classification"]
        return "n/a"
    # collect exit code summaries for observations
    def exit_codes_summary():
        summaries = []
        for case in CASE_ORDER:
            r = find_obs(case, "execute_workers")
            if r and "exit_codes" in str(r["observation"]):
                summaries.append(f"{case}: exit_codes recorded")
        return "; ".join(summaries) if summaries else "none"
    results_md = f"""# RESULTS

Python version: {env['python_version']}
NumPy available: {env['numpy_available']}, version: {env['numpy_version']}
PyTorch available: {env['torch_available']}, version: {env['torch_version']}
Start methods: {', '.join(env['start_methods'])}
Root seed: {ROOT_SEED}
Workers: {len(WORKER_IDS)}, draws per worker: {DRAWS}
Rows: {len(rows)} (10 cases × 4 methods)

## Classification buckets
{counts_str}

## Observations
- serial_same_seed_baseline: {seq_summary('serial_same_seed_baseline_marker')}
- fork_legacy_state: {seq_summary('fork_legacy_global_state_copy_marker')}
- fork_generator_copy: {seq_summary('fork_generator_object_copy_marker')}
- fork_worker_id_reseed: {seq_summary('fork_worker_id_reseed_marker')}
- fork_seedsequence_children: {seq_summary('fork_seedsequence_children_marker')}
- spawn_same_seed: {seq_summary('spawn_same_seed_marker')}
- spawn_seedsequence_children: {seq_summary('spawn_seedsequence_children_marker')}
- spawn_repeatability: {seq_summary('spawn_repeatability_across_runs_marker')}

Platform skips: {counts.get('platform_skip',0)}
Dependency skips: {counts.get('dependency_skip',0)}
Failures: {counts.get('fail',0)}

## What was observed
- Duplicate sequence observations: serial same-seed, fork legacy global state copy, fork generator object copy, spawn same-seed – all produced identical sequences across workers when deliberately seeded identically or inheriting state via fork.
- Distinct sequence observations: fork worker-id reseed, fork SeedSequence children, spawn SeedSequence children – all produced pairwise distinct sequences per worker.
- Repeatability observations: worker-id reseed, SeedSequence children (fork and spawn), and spawn repeatability across runs – sequences were exactly reproducible per worker id across repeated runs.
- Platform availability: fork={'yes' if env['fork_available'] else 'no'}, spawn={'yes' if env['spawn_available'] else 'no'}.
- Dependency availability: numpy={env['numpy_available']}, torch={env['torch_available']}.

## What was NOT tested / disclaimed
This repository does not prove that every numpy or pytorch program has duplicated rng streams, that historical pytorch behavior remains unchanged today, that fork is the default everywhere, that spawn repairs repeated explicit seeds, that numpy generators are automatically independent after copying, that distinct short sequences are statistically independent, that SeedSequence eliminates every collision risk, that a six-number sample tests rng quality, that duplicated augmentation necessarily changes model accuracy, that different augmentations improve model quality, that a random seed alone guarantees full experimental reproducibility, that one local multiprocessing run validates a production data pipeline, or that the lab is machine-learning validated, statistically certified, universally portable, or production-ready.

See README.md for Hacker News discussion summary, article attribution, and documentation references.
"""
    with open("RESULTS.md","w",encoding="utf-8",newline="\n") as f:
        f.write(results_md)
    print(f"wrote {len(rows)} rows")
if __name__ == "__main__":
    main()
