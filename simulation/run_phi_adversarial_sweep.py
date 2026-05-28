"""
run_phi_adversarial_sweep.py -- Phi Under Corrupted U_sys (Path 1)

Purpose
-------
Test whether phi differential appears under adversarial conditions that corrupt
or degrade U_sys fidelity. Phi modulates the planning horizon over U_sys but does
not change whether well-being is in the objective function. The architectural
prediction is that phi matters most when U_sys fidelity is degraded: temporal-drift
attacks (Sub_Threshold_Drift, Successor_Contamination, Opaque_Reasoning,
Evaluator_Collusion) should show larger phi differential than infrastructure-
corruption attacks (Measurement_Tampering, Ledger_Compromise, Sybil_Capture,
Engineered_Fragility, Domain_Masking, Bootstrap_Subversion).

The sweep threads PHI_VALUES = [1.0, 5.0, 10.0, 15.0, 25.0] through all 10
attack vectors from the comprehensive adversarial sweep. Output goes to a new
file (comprehensive_adversarial_sweeps_v1x2_phi.csv); the existing
comprehensive_adversarial_sweeps.csv is not modified.

Parameter grid (live tasks)
---------------------------
Sybil_Capture            : 3 pop_sizes x 2 defense x 5 phi x 20 it  =  600
Measurement_Tampering    : 3 costs x 2 defense x 5 phi x 20 it      =  600
Ledger_Compromise        : 2 x 2 defense x 5 phi x 20 it            =  400
Successor_Contamination  : 3 costs x 2 defense x 5 phi x 20 it      =  600
Opaque_Reasoning         : 3 pop_sizes x 2 defense x 5 phi x 20 it  =  600
Bootstrap_Subversion     : 5 phi x 2 defense x 20 it                =  200
Evaluator_Collusion      : 3 pop_sizes x 2 defense x 5 phi x 20 it  =  600
Sub_Threshold_Drift      : 5 phi x 2 defense x 20 it                =  200
Engineered_Fragility     : 3 shock_mags x 2 defense x 5 phi x 20 it =  600
Domain_Masking stub      : 5 phi x 2 defense x 20 it                =  200 (injected)
Total live               : 4,400 runs + 200 stub = 4,600 records

Usage
-----
    python run_phi_adversarial_sweep.py           # full 4,400-run sweep
    python run_phi_adversarial_sweep.py --sample  # 10-run timing sample
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

from deps import check_and_install
check_and_install('numpy')

import argparse
import time
from datetime import timedelta

import numpy as np

from monte_carlo import (
    _run_single_comp_sweep,
    _domain_masking_legacy_stub,
    run_phi_adversarial_sweep,
    PHI_VALUES,
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')


def run_sample():
    """10-run sequential timing sample: Sub_Threshold_Drift, phi=25.0, cusum_active=False, seeds 0-9."""
    print("\nTiming sample: Sub_Threshold_Drift, phi=25.0, cusum_active=False, seeds 0-9")
    tasks = [{'attack_type': 'sub_threshold_drift', 'phi_val': 25.0, 'cusum_active': False, 'it': i}
             for i in range(10)]

    times = []
    for task in tasks:
        t0 = time.time()
        _run_single_comp_sweep(task)
        times.append(time.time() - t0)

    mean_t  = float(np.mean(times))
    std_t   = float(np.std(times))
    total_t = sum(times)
    live_tasks = 4400
    cores = max(1, (os.cpu_count() or 4) - 1)
    cap_cores = min(15, cores)

    extrap_serial = mean_t * live_tasks * 1.25
    extrap_wall   = extrap_serial / cap_cores

    print(f"\n  Sample runs completed : {len(times)}")
    print(f"  Wall-clock total      : {total_t:.1f}s")
    print(f"  Mean per run          : {mean_t:.2f}s")
    print(f"  Std per run           : {std_t:.2f}s")
    print(f"  Full sweep live tasks : {live_tasks}")
    print(f"  Cores (capped at 15)  : {cap_cores}")
    print(f"  Extrapolated wall time: {extrap_wall:.0f}s ({extrap_wall/60:.1f} min) "
          f"[mean x {live_tasks} x 1.25 / {cap_cores} cores]")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Phi under corrupted U_sys adversarial sweep.')
    parser.add_argument('--sample', action='store_true',
                        help='Run 10-run timing sample only.')
    args = parser.parse_args()

    if args.sample:
        run_sample()
    else:
        run_phi_adversarial_sweep(iterations=20)
