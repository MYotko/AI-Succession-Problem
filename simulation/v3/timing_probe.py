"""Serial microbenchmark, not a simulation batch or integrated v3 timing.

Run: python -B simulation/v3/timing_probe.py --repeats 3 --threads 1
The v3 comparison deliberately shares the v2 aggregate state projector;
it measures incremental policy/measurement arithmetic without claiming
to validate that projector as a v3 kernel. It writes only its JSON report.
"""

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--threads", type=int, default=1, choices=(1, 2))
    args = parser.parse_args()
    if not 1 <= args.repeats <= 5:
        parser.error("small probe limited to 1..5 repeats")
    for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[key] = str(args.threads)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import numpy as np
    from agents import optimize_u_sys_v2, _project_diagnostic_state_step
    from metrics import _build_state_from_model
    from model import GardenModel
    from v3.measurements import NoveltyProtocol, NoveltyWindow, advance_window, novelty, execution, responsiveness, lineage, transfer, bandwidth_clip
    from v3.objective import FlowParameters, discounted_flow, domain_continuation, objective
    from v3.policies import policy_class, Summary

    process_cpus = os.process_cpu_count() if hasattr(os, "process_cpu_count") else None
    affinity_count = None
    if os.name == "nt":
        process_mask, system_mask = ctypes.c_size_t(), ctypes.c_size_t()
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetCurrentProcess.restype = ctypes.c_void_p
        kernel32.GetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
        if kernel32.GetProcessAffinityMask(kernel32.GetCurrentProcess(), ctypes.byref(process_mask), ctypes.byref(system_mask)):
            affinity_count = process_mask.value.bit_count()
    verified_threads = []
    # Query the loaded NumPy OpenBLAS library directly, without threadpoolctl.
    libs = Path(np.__file__).resolve().parent.parent / "numpy.libs"
    if os.name == "nt" and libs.exists():
        for library in libs.glob("*openblas*.dll"):
            dll = ctypes.CDLL(str(library))
            for symbol in ("scipy_openblas_get_num_threads64_", "openblas_get_num_threads64_", "scipy_openblas_get_num_threads", "openblas_get_num_threads"):
                try:
                    query = getattr(dll, symbol)
                except AttributeError:
                    continue
                query.restype = ctypes.c_int
                verified_threads.append({"library": library.name, "symbol": symbol, "effective": query()})
                break
    cfg = {"policy": "optimize_u_sys_v2", "random_seed": 271828, "n_candidates_v2": 300, "rollout_steps_v2": 20, "reproduction_rate": 0.08, "alpha": 1.0}
    model = GardenModel(200, "optimize_u_sys_v2", config=cfg)
    initial = _build_state_from_model(model)
    protocol = NoveltyProtocol((0.0,) * 10, 0.00024)
    params = FlowParameters(5, 3, 8, 1e-6, 1e-6, 1e-6, 0, protocol.upper_bound)
    continuation = domain_continuation(params.extinction_flow, params.upper_bound)
    beta = float(np.exp(-0.01))
    rules = policy_class()
    normals = np.random.default_rng(314159).normal(size=(20, 64, 10))
    clip = bandwidth_clip(5, 0.5, 1e-6)

    def v2():
        return optimize_u_sys_v2(model.ai, model)[1]["selected_u_sys"]

    def v3_components():
        from v3.objective import flow
        scores = []
        for rule in rules:
            state, window, flows = initial, NoveltyWindow(), []
            rng = np.random.default_rng(161803)
            for t in range(20):
                summary = Summary(state.population / 1600, state.avg_wb, (state.psi_inst_stock, state.resilience_stock, state.theta_capability, state.transfer_state))
                action = rule.allocation(summary)
                state = _project_diagnostic_state_step(state, action, cfg)
                # Proxy samples only. Full individual transitions and the
                # finite grid are absent and are explicitly not timed here.
                samples = normals[t] * 0.25 * state.avg_wb * (1 - 0.1315)
                window = advance_window(window, samples, protocol, rng)
                h_n = novelty(window, protocol)
                psi = responsiveness([state.psi_inst_stock])
                theta = transfer(min(5, state.theta_capability), state.avg_wb * state.transfer_state, state.transfer_state, 1.0, clip, 5)
                l_value = lineage(0.5, state.population, 200, psi, theta)
                flows.append(flow(h_n, execution(action["x_compute"]), l_value, params))
            d = discounted_flow(flows, beta, continuation)
            scores.append(objective(d.value, 0.0, 0.5))  # Dummy frozen lookup.
        return max(scores)

    started = time.perf_counter()
    timings = {"v2_300x20": [], "v3_components_289x20": []}
    checksums = {}
    # One serial warmup and alternating timed sections, with no worker pool.
    v2()
    v3_components()
    for _ in range(args.repeats):
        for name, function in (("v2_300x20", v2), ("v3_components_289x20", v3_components)):
            if time.perf_counter() - started > 840:
                raise RuntimeError("probe time budget exhausted")
            before = time.perf_counter()
            checksums[name] = function()
            timings[name].append(time.perf_counter() - before)
    medians = {name: statistics.median(values) for name, values in timings.items()}
    report = {
        "registered": False, "scope": "component proxy, not integrated v3",
        "machine": platform.node(), "platform": platform.platform(),
        "python": platform.python_version(), "numpy": np.__version__,
        "process_cpus": process_cpus, "affinity_cpu_count": affinity_count,
        "operator_budget": 16, "mode": "work", "worker_processes": 0,
        "configured_threads": args.threads, "verified_threads": verified_threads,
        "seconds": timings, "median_seconds": medians,
        "ratio": medians["v3_components_289x20"] / medians["v2_300x20"],
        "total_wall_seconds": time.perf_counter() - started,
        "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_sha256": {str(p.relative_to(Path(__file__).resolve().parents[1])): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).resolve().parent.glob("*.py"))},
        "checksums": checksums,
        "omitted": ["agent-level finite v3 transition kernel", "admission/ledger evaluation", "offline estimator", "complete-plan search", "validated continuation"],
    }
    target = Path(__file__).resolve().parent / "timing_results.json"
    target.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
