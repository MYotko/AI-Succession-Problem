"""Tabular unconditional Bellman fitting from pre-resampling transitions."""
import math
import numpy as np


def fit_transitions(before_bins, after_bins, rewards, extinct, groups, lower, upper, beta=math.exp(-.01), min_visits=4):
    """Split whole independent groups, never random correlated transitions.

    The last two of six groups are held out. Clone edges never appear here.
    Missing bins stay missing. The returned enclosure covers the flow
    domain; empirical residuals alone do not certify microstate aggregation.
    """
    shape = rewards.shape
    group_grid = np.broadcast_to(np.asarray(groups)[None, :], shape)
    train = group_grid < max(1, int(np.max(groups)) - 1)
    heldout = ~train
    keys = np.asarray(before_bins).reshape(-1, 6)
    next_keys = np.asarray(after_bins).reshape(-1, 6)
    observed = np.unique(keys[train.ravel()], axis=0)
    # Sparse fixed-point iteration avoids a 6144 by 6144 dense solve.
    encoded = {tuple(map(int, key)): i for i, key in enumerate(observed)}
    current = np.array([encoded.get(tuple(key), -1) for key in keys])
    following = np.array([encoded.get(tuple(key), -1) for key in next_keys])
    rr, dead = np.asarray(rewards).ravel(), np.asarray(extinct).ravel()
    keep = train.ravel() & (current >= 0)
    counts = np.bincount(current[keep], minlength=len(observed))
    midpoint = (lower + upper) / 2
    value = np.full(len(observed), midpoint)
    unknown_next = (following < 0) & ~dead
    # Aggregate repeated bin transitions once. This preserves their weights.
    size = len(value)
    destination = np.where(dead, size, np.where(following < 0, size + 1, following))
    edges, frequency = np.unique(current[keep] * (size + 2) + destination[keep], return_counts=True)
    source, dest = edges // (size + 2), edges % (size + 2)
    probability = frequency / counts[source]
    reward_mean = np.bincount(current[keep], weights=rr[keep], minlength=size) / np.maximum(counts, 1)
    for iteration in range(2500):
        extension = np.concatenate((value, [lower, midpoint]))
        new = (1 - beta) * reward_mean + beta * np.bincount(source, weights=probability * extension[dest], minlength=size)
        if np.max(abs(new - value), initial=0) < 1e-9:
            value = new
            break
        value = new
    next_value = np.full(len(rr), midpoint)
    known = following >= 0
    next_value[known] = value[following[known]]
    next_value[dead] = lower
    target = (1 - beta) * rr + beta * next_value
    covered = heldout.ravel() & (current >= 0) & ~unknown_next
    residuals = target[covered] - value[current[covered]]
    count_heldout = int(heldout.sum())
    # Conditional empirical mean residual per covered held-out bin.
    hc = np.bincount(current[covered], minlength=len(value))
    hs = np.bincount(current[covered], weights=residuals, minlength=len(value))
    maximum = float(np.max(abs(hs[hc > 0] / hc[hc > 0]), initial=0))
    entries = []
    for i, key in enumerate(observed):
        if counts[i] >= min_visits:
            entries.append({"bin": key.tolist(), "value": float(value[i]), "error": max(float(value[i] - lower), float(upper - value[i])),
                            "training_visits": int(counts[i]), "heldout_visits": int(hc[i])})
    return {"entries": entries, "heldout_transitions": count_heldout,
            "heldout_coverage": float(covered.sum() / max(1, count_heldout)),
            "bellman_residual_empirical": maximum,
            "bellman_rmse": float(np.sqrt(np.mean(residuals**2))) if len(residuals) else None,
            "iterations": iteration + 1, "missing_next_training_transitions": int((keep & unknown_next).sum()),
            "training_fixed_point_converged": iteration < 2499,
            "uniform_residual_certified": False, "aggregation_bias_covered": False,
            "error_method": "bounded-flow-domain enclosure", "split": "last two independent groups held out"}
