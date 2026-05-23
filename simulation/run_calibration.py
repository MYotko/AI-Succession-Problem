"""
run_calibration.py -- 10-run calibration sample for Task 2b.

Runs: one seed across all 5 cap values (rr=0.064, phi=10, alpha=1, seed=0)
      plus 5 seeds at cap=25.0 (seeds 0-4) to capture variance.
Reports wall time, per-run stats, memory footprint, and full-sweep projection.
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import sys
import time
import resource

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import GardenModel
from agents import AIAgent

RR          = 0.064
PHI         = 10.0
ALPHA       = 1.0
MAX_STEPS   = 50_000
CONV_WINDOW = 300
CONV_CV_THRESHOLD = 0.05

import numpy as np

def _converged(l_history):
    if len(l_history) < CONV_WINDOW:
        return False
    recent = np.array(l_history[-CONV_WINDOW:], dtype=float)
    if not np.all(np.isfinite(recent)):
        return False
    mean = recent.mean()
    if mean < 1e-4:
        return False
    return (recent.std() / mean) < CONV_CV_THRESHOLD


def run_single(rr, phi, alpha, seed, cap, label=''):
    config = {
        'random_seed':       seed,
        'reproduction_rate': rr,
        'phi':               phi,
        'alpha':             alpha,
        'max_capability':    cap,
        'frontier_floor':    0.02,
        'k1_transition':     2.164,
        'k2_transition':     1.0,
        'beta_transition':   0.5,
    }
    successor = AIAgent(policy='optimize_u_sys', generation=2,
                        capability=cap, config=config)
    model = GardenModel(
        n_agents=200,
        ai_policy='optimize_u_sys',
        successor_ai=successor,
        config=config,
        cop_cost_audit=True,
    )
    t0 = time.time()
    reason = 'max_steps'
    for step in range(MAX_STEPS):
        alive = model.step()
        if not alive:
            reason = 'extinction'
            break
        if step >= CONV_WINDOW and _converged(model.datacollector['L_t']):
            reason = 'convergence'
            break
    elapsed = time.time() - t0
    steps   = len(model.datacollector['U_sys'])
    gen     = model.datacollector['ai_generation'][-1]
    print(f'  {label:<28} cap={cap:5.1f} seed={seed}  -> {reason:<11} '
          f'steps={steps:>7,}  gen={gen:>5}  t={elapsed:.2f}s', flush=True)
    return elapsed


def main():
    FULL_TOTAL = 2025
    MARGIN     = 1.25

    print('=' * 72, flush=True)
    print('  Calibration run -- 10 samples', flush=True)
    print('  rr=0.064, phi=10.0, alpha=1.0', flush=True)
    print('=' * 72, flush=True)
    print(flush=True)

    tasks = [
        # One seed across all 5 cap values
        (RR, PHI, ALPHA, 0, 5.0,   'all-caps seed=0'),
        (RR, PHI, ALPHA, 0, 10.0,  'all-caps seed=0'),
        (RR, PHI, ALPHA, 0, 25.0,  'all-caps seed=0'),
        (RR, PHI, ALPHA, 0, 50.0,  'all-caps seed=0'),
        (RR, PHI, ALPHA, 0, 100.0, 'all-caps seed=0'),
        # 5 seeds at cap=25.0 to measure variance
        (RR, PHI, ALPHA, 1, 25.0,  'cap25 variance'),
        (RR, PHI, ALPHA, 2, 25.0,  'cap25 variance'),
        (RR, PHI, ALPHA, 3, 25.0,  'cap25 variance'),
        (RR, PHI, ALPHA, 4, 25.0,  'cap25 variance'),
        # Extra at cap=100 for high-cap variance
        (RR, PHI, ALPHA, 1, 100.0, 'cap100 variance'),
    ]

    # Peak RSS before runs
    rss_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    wall_start = time.time()
    times_by_cap = {5.0: [], 10.0: [], 25.0: [], 50.0: [], 100.0: []}
    all_times    = []

    for rr, phi, alpha, seed, cap, label in tasks:
        t = run_single(rr, phi, alpha, seed, cap, label)
        all_times.append(t)
        times_by_cap[cap].append(t)

    wall_total = time.time() - wall_start
    rss_after  = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_delta  = rss_after - rss_before

    print(flush=True)
    print('  -- Per-cap timing (seconds) --', flush=True)
    for cap in sorted(times_by_cap):
        ts = times_by_cap[cap]
        if ts:
            mean = sum(ts) / len(ts)
            std  = (sum((x - mean)**2 for x in ts) / max(1, len(ts)-1)) ** 0.5
            print(f'    cap={cap:5.1f}: n={len(ts)} mean={mean:.2f}s  std={std:.2f}s', flush=True)

    overall_mean = sum(all_times) / len(all_times)
    overall_std  = (sum((x - overall_mean)**2 for x in all_times) / max(1, len(all_times)-1)) ** 0.5

    projected_s = overall_mean * FULL_TOTAL * MARGIN
    projected_min = projected_s / 60
    projected_h   = projected_min / 60

    print(flush=True)
    print(f'  Wall-clock total (10 runs):  {wall_total:.1f}s', flush=True)
    print(f'  Per-run mean:                {overall_mean:.2f}s', flush=True)
    print(f'  Per-run std:                 {overall_std:.2f}s', flush=True)
    print(f'  RSS delta (peak):            {rss_delta / 1024:.1f} MB', flush=True)
    print(flush=True)
    print(f'  Full sweep projection (2,025 runs x {MARGIN}x margin):', flush=True)
    print(f'    {projected_s:.0f}s  ({projected_min:.0f} min  /  {projected_h:.1f}h)', flush=True)
    print(flush=True)
    cores = max(1, (os.cpu_count() or 4) - 1)
    projected_parallel = projected_s / cores
    print(f'  With {cores} worker cores: {projected_parallel:.0f}s  '
          f'({projected_parallel/60:.0f} min  /  {projected_parallel/3600:.1f}h)', flush=True)
    print('=' * 72, flush=True)
    print(flush=True)
    print('  STOP: awaiting go/no-go before launching full 2,025-run sweep.', flush=True)


if __name__ == '__main__':
    main()
