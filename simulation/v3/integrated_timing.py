"""Small serial integrated-step timing experiment, never a registered batch.

python -B simulation/v3/integrated_timing.py --repeats 3 --threads 1
Each timed decision includes allocation, admission, actual population
advance, measurement and diagnostics. Review cases include complete plans.
No independent scientific jobs or worker pool are launched by this probe.
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
    parser.add_argument("--repeats", type=int, default=3, choices=range(1, 6))
    parser.add_argument("--threads", type=int, default=1, choices=(1, 2))
    args = parser.parse_args()
    started = time.perf_counter()
    for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = str(args.threads)
    sys.dont_write_bytecode = True
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root.parent))
    import numpy as np
    from agents import optimize_u_sys_v2
    from metrics import _build_state_from_model
    from model import GardenModel
    from v3.integration import V3Model
    from v3.policies import policy_class, execution_policy_class
    from v3.engine import advance, measurements_and_flow, ChannelRandom
    from v3.conformance import stock_path_validation, floor_audit
    from v3.tables import reduced_continuation_validation, canonical_hash
    verified = []
    for library in (Path(np.__file__).resolve().parent.parent / "numpy.libs").glob("*openblas*.dll"):
        dll = ctypes.CDLL(str(library))
        for symbol in ("scipy_openblas_get_num_threads64_", "openblas_get_num_threads64_", "scipy_openblas_get_num_threads", "openblas_get_num_threads"):
            try:
                query = getattr(dll, symbol)
            except AttributeError:
                continue
            query.restype = ctypes.c_int
            verified.append({"library": library.name, "effective": query()})
            break
    samples, medians, checksums = {}, {}, {}
    V3Model(200, rules=execution_policy_class()[:1], rollout_steps=1, successor_capability=None).step()
    for n in (200, 1600):
        for label, rules in (("full289", policy_class()), ("frozen25", execution_policy_class())):
            for review in (False, True):
                # Full-class review is measured once to bound probe cost.
                repeats = args.repeats if label == "frozen25" else 1
                name = f"N{n}_{label}_{'review' if review else 'ordinary'}"
                values = []
                for repeat in range(repeats):
                    if time.perf_counter() - started > 900:
                        raise RuntimeError("timing budget exhausted")
                    m = V3Model(n, rules=rules, seed=271828)
                    m._open_period()
                    if not review:
                        m.time = 1  # Same declared microstate at a non-review clock.
                    before = time.perf_counter()
                    record = m.step()
                    values.append(time.perf_counter() - before)
                    checksums[name] = {k: record[k] for k in ("chosen_rule", "population", "flow", "admission_bound")}
                samples[name] = values
                medians[name] = statistics.median(values)
        cfg = {"policy": "optimize_u_sys_v2", "random_seed": 271828, "n_candidates_v2": 300, "rollout_steps_v2": 20}
        legacy = GardenModel(n, "optimize_u_sys_v2", config=cfg)
        values = []
        for _ in range(args.repeats):
            before = time.perf_counter()
            optimize_u_sys_v2(legacy.ai, legacy)
            values.append(time.perf_counter() - before)
        samples[f"N{n}_v2_allocation300x20"] = values
        medians[f"N{n}_v2_allocation300x20"] = statistics.median(values)
        # Timing kernel throughput only. Shared-CRN rows are not independent
        # estimator particles; resampling and file publication are absent.
        m = V3Model(n)
        values = []
        for repeat in range(args.repeats):
            state = m.state.repeat(24)
            action = np.full((24, 6), 1 / 6)
            before = time.perf_counter()
            for step in range(10):
                advance(state, action, ChannelRandom(12345 + step), .08, 1600, m.protocol)
                measurements_and_flow(state, action, m.parameters, 1., 1.)
            values.append((time.perf_counter() - before) / 240)
        samples[f"N{n}_fixed_rule_particle_step"] = values
        medians[f"N{n}_fixed_rule_particle_step"] = statistics.median(values)
    efficiency = 39.15 / (16 * 2.6416)
    # No matched-machine speed ratio is present in the supplied reports.
    # Keep s explicit; s=1 is a planning assumption, not a measured ratio.
    divisor = 16 * 3600 * efficiency
    projection = {}
    for n in (200, 1600):
        for label in ("full289", "frozen25"):
            weighted = .9 * medians[f"N{n}_{label}_ordinary"] + .1 * medians[f"N{n}_{label}_review"]
            hours = 24900 * 500 * weighted / divisor
            projection[f"N{n}_{label}"] = {"weighted_seconds": weighted, "X2_hours_at_s1": hours,
                                                "required_speed_ratio_for_72h": hours / 72}
    particle = medians["N1600_fixed_rule_particle_step"]
    # Plain primary plus independent doubled-length sensitivity.
    plain_steps = 25 * 13 * 6 * (10000 + 20000)
    calibration_steps = 50 * 500
    # Explicit 32-occupied-bin scenario. Seven primary equivalents cover
    # primary, particles x2, length x2 and bins x2. Six replicates each.
    we_steps_per_rule_kernel = 6 * 32000 * 24 * 32 * 7
    table_cost = {"plain_steps_all_325_rule_kernels": plain_steps,
                  "plain_X2_hours_at_s1": plain_steps * particle / divisor,
                  "calibration_steps": calibration_steps,
                  "calibration_X2_hours_at_s1": calibration_steps * particle / divisor,
                  "we_particle_steps_per_rule_kernel": we_steps_per_rule_kernel,
                  "we_X2_hours_per_rule_kernel_at_s1": we_steps_per_rule_kernel * particle / divisor,
                  "we_25_rules_one_boundary_rr_X2_hours_at_s1": 25 * we_steps_per_rule_kernel * particle / divisor,
                  "resampling_io_continuation_validation_cost_included": False,
                  "occupied_bins_assumption": 32}
    report = {"scope": "B1 integrated fixtures; timing only", "registered": False,
              "machine": platform.node(), "platform": platform.platform(), "python": platform.python_version(), "numpy": np.__version__,
              "available_process_cpus": os.process_cpu_count(), "operator_cpu_budget": 16, "mode": "work",
              "worker_processes": 0, "timing_processes": 1, "threads_configured": args.threads, "threads_verified": verified,
              "samples_seconds": samples, "median_seconds": medians, "checksums": checksums,
              "planning_speed_ratio_s": 1., "speed_ratio_status": "assumed; matched X2/local workload ratio not supplied",
              "X2_study_efficiency_planning_factor": efficiency, "projections": projection, "table_cost": table_cost,
              "class_ids": [r.rule_id for r in execution_policy_class()],
              "class_hash": canonical_hash([r.__dict__ for r in execution_policy_class()]),
              "stock_validation": stock_path_validation(), "floor_audit": floor_audit(),
              "continuation_validation": reduced_continuation_validation(),
              "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.glob("*.py"))}}
    report["total_wall_seconds"] = time.perf_counter() - started
    target = root / "integrated_timing_results.json"
    target.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("median_seconds", "projections", "table_cost", "stock_validation", "continuation_validation", "threads_verified", "total_wall_seconds")}, indent=2))


if __name__ == "__main__":
    main()
