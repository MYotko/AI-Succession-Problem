"""R13 plain and synchronous Fleming-Viot estimators on complete v3 states.

Full-scale intervals describe sampling and finite-algorithm variation.
They are not certified bounds on QSD bias. WE is deliberately unavailable.
"""
from dataclasses import replace
import math
import time
import numpy as np
from .artifacts import digest
from .context import Context, reproductive_support, observable_features, score_features
from .engine import RuleBatch, advance
from .policies import execution_policy_class
from .continuation import fit_transitions
from .cohort import initial_law_bound

# Proposed A1, 2026-09-28: time bias and sparse continuation bins both
# failed. Thresholds and the predeclared sensitivity subset are unchanged.
PRIMARY = {"groups": 6, "runs_per_group": 64, "particles": 256, "burn": 1024, "measure": 2048}
SENSITIVITY_RULES = ("balanced", "w0_p0_t1_g3", "w3_p5_t1_g3")
SENSITIVITY_RR = (.055, .064, .070)


def settings_for(name="primary"):
    value = dict(PRIMARY)
    if name == "double_population":
        value["runs_per_group"] *= 2
        value["particles"] *= 2
    elif name == "double_length":
        value["burn"] *= 2
        value["measure"] *= 2
    elif name != "primary":
        raise ValueError("unknown frozen sensitivity setting")
    return value


def _rule(rule_id):
    return next(r for r in execution_policy_class() if r.rule_id == rule_id)


def simulate(context, rule, settings, seed, route):
    if route not in ("plain", "fv"):
        raise ValueError("WE is not implemented; row must be not_estimable")
    groups = settings["groups"]
    per_group = settings["runs_per_group"] if route == "plain" else settings["particles"]
    if groups < 3 or per_group < 2 or settings["burn"] < 0 or settings["measure"] < 4:
        raise ValueError("insufficient estimator setting")
    count, length = groups * per_group, settings["burn"] + settings["measure"]
    rng = np.random.default_rng(seed)
    state = context.population(count, rng)
    batch = RuleBatch([rule])
    indices = np.zeros(count, dtype=int)
    features = np.empty((length, count, 9 if context.instrument.a10 else 8))
    conditioned = np.empty_like(features)
    before = np.empty((length, count, 6), dtype=np.int8)
    after = np.empty_like(before)
    support = np.empty((length, count), dtype=bool)
    deaths = np.zeros((length, groups), dtype=int)
    collapsed = []
    for step in range(length):
        bins = state.summary_bins(context.config.get("carrying_capacity", 1600))
        before[step] = bins
        actions = batch.actions(bins, indices)
        advance(state, actions, rng, context.config.get("reproduction_rate", .08), context.config.get("carrying_capacity", 1600),
                context.protocol, crowding=context.config.get("crowding", "total"), independent=True,
                **({"capability": context.config.get("capability", 1.), "instrument": context.instrument} if context.instrument.a10 else {}))
        after[step] = state.summary_bins(context.config.get("carrying_capacity", 1600))
        features[step] = observable_features(state, actions, **({"capability": context.config.get("capability", 1.), "instrument": context.instrument} if context.instrument.a10 else {}))
        viable = (reproductive_support(state, context.config.get("capability", 1.), context.instrument)
                  if context.instrument.a10 else reproductive_support(state))
        support[step] = viable
        copy_indices = np.arange(count)
        if route == "fv":
            for group in range(groups):
                members = np.arange(group * per_group, (group + 1) * per_group)
                killed, survivors = members[~viable[members]], members[viable[members]]
                deaths[step, group] = len(killed)
                if not len(survivors):
                    collapsed.append({"step": step, "group": group})
                elif len(killed):
                    copy_indices[killed] = rng.choice(survivors, len(killed), replace=True)
            if collapsed:
                length = step + 1
                conditioned[step] = features[step]
                break
            # Duplicate the entire surviving state, including windows and
            # propensities. The next independent=True advance gives each
            # descendant independent environmental draws, never copied RNGs.
            state = state.copy_rows(copy_indices)
        conditioned[step] = features[step, copy_indices]
    return {"features": features[:length], "conditioned": conditioned[:length],
            "before": before[:length], "after": after[:length], "support": support[:length],
            "deaths": deaths[:length], "groups": np.repeat(np.arange(groups), per_group),
            "per_group": per_group, "route": route, "collapsed": collapsed,
            "survivor_counts": support[:length].sum(axis=1).tolist()}


def interval(values, lower, upper):
    values = np.asarray(values, float)
    if len(values) < 2 or not np.isfinite(values).all():
        return {"mean": None, "interval95": [lower, upper], "half_width": upper - lower, "replicates": []}
    mean = float(values.mean())
    # Six groups in production. 4.303 also conservatively covers >=3 groups.
    critical = 2.571 if len(values) >= 6 else 4.303
    half = critical * float(values.std(ddof=1)) / math.sqrt(len(values))
    return {"mean": mean, "interval95": [max(lower, mean - half), min(upper, mean + half)],
            "half_width": half, "replicates": values.tolist()}


def _plain_mean(flow, keep):
    counts = keep.sum(axis=1)
    if np.any(counts == 0):
        return None
    return float(np.mean(np.sum(np.where(keep, flow, 0), axis=1) / counts))


def summarize(trace, context, setting, alpha, capability):
    start = setting["burn"]
    if context.instrument.a10 and len(trace["features"]) <= 30:
        return {"status": "not_estimable", "reason": "no full-history continuation transitions", "lambda_f": None,
                "zeta": {"status": "unresolved", "upper": 1.}, "continuation": None}
    if trace["collapsed"] or len(trace["features"]) <= start:
        return {"status": "not_estimable", "reason": "FV ensemble collapsed; WE unavailable", "lambda_f": None,
                "zeta": {"status": "unresolved", "upper": 1.}, "continuation": None}
    flows = score_features(trace["features"], context, alpha, capability)
    conditioned = score_features(trace["conditioned"], context, alpha, capability)
    keep = trace["support"]
    group = trace["groups"]
    means = []
    for g in range(setting["groups"]):
        mask = group == g
        value = (float(conditioned[start:, mask].mean()) if trace["route"] == "fv" else
                 _plain_mean(flows[start:, mask], keep[start:, mask]))
        means.append(np.nan if value is None else value)
    p = context.parameters
    summary = interval(means, p.extinction_flow, p.upper_bound)
    # Bonferroni over the frozen 13,750 primary scoring rows. Independent
    # group means are bounded even though within-group FV paths correlate.
    # This encloses the finite-algorithm expectation, not its QSD bias.
    allocation = .05 / 13750
    finite_half = (p.upper_bound - p.extinction_flow) * math.sqrt(math.log(2 / allocation) / (2 * setting["groups"]))
    mean = summary["mean"]
    summary.update(family_alpha=.05, row_alpha=allocation,
                   finite_algorithm_interval=[p.extinction_flow, p.upper_bound] if mean is None else
                   [max(p.extinction_flow, mean - finite_half), min(p.upper_bound, mean + finite_half)],
                   finite_algorithm_method="bounded independent group means; excludes conditioning and QSD bias")
    halves = []
    middle = start + setting["measure"] // 2
    for section in (slice(start, middle), slice(middle, None)):
        halves.append(float(conditioned[section].mean()) if trace["route"] == "fv" else _plain_mean(flows[section], keep[section]))
    survive_fraction = float(keep[-1].mean())
    route_ok = trace["route"] == "fv" or survive_fraction >= .5
    span = p.upper_bound - p.extinction_flow
    drift_ok = None not in halves and abs(halves[1] - halves[0]) <= .05 * span
    stable = summary["mean"] is not None and summary["half_width"] <= .05 * span and drift_ok and route_ok
    fit_start = 30 if context.instrument.a10 else 0
    empirical = fit_transitions(trace["before"][fit_start:], trace["after"][fit_start:], flows[fit_start:], trace["features"][fit_start:, ..., 0] == 0, group,
                                p.extinction_flow, p.upper_bound)
    if context.instrument.a10:
        empirical["first_source_step"] = fit_start
    continuation_ok = empirical["heldout_coverage"] >= .9 and empirical["bellman_residual_empirical"] <= .05 * span and bool(empirical["entries"]) and empirical["training_fixed_point_converged"]
    if trace["route"] == "fv":
        rates = trace["deaths"][start:].mean(axis=0) / trace["per_group"]
        zeta = interval(rates, 0, 1)
        total = trace["deaths"][start:].sum(axis=0)
        rate = zeta["mean"]
        half_rates = [float(trace["deaths"][section].mean() / trace["per_group"]) for section in (slice(start, middle), slice(middle, None))]
        concentration = float(total.max() / max(1, total.sum()))
        ratio = half_rates[1] / half_rates[0] if half_rates[0] else None
        resolved = rate is not None and rate >= 1e-4 and zeta["half_width"] <= .3 * rate and bool(np.all(total > 0))
        resolved &= concentration <= .35 and ratio is not None and 2 / 3 <= ratio <= 1.5
        zeta.update(status="estimated_diagnostic" if resolved else "unresolved", upper=1.,
                    replicate_death_concentration=concentration, half_window_rate_ratio=ratio,
                    upper_method="trivial chain domain; sampling interval is not a true-rate upper certificate",
                    coverage_including_bias=False, binding_rejection=False)
    else:
        zeta = {"status": "unresolved", "mean": None, "upper": 1., "reason": "no FV rate in plain route", "binding_rejection": False}
    return {"status": "estimated" if stable and continuation_ok else "not_estimable",
            "reason": None if stable and continuation_ok else "row stability or continuation coverage screen failed; WE unavailable",
            "lambda_f": summary, "zeta": zeta, "continuation": empirical,
            "screens": {"route_applicable": route_ok, "flow_half_width": summary["half_width"] <= .05 * span,
                        "half_window_drift": drift_ok, "continuation": continuation_ok},
            "half_window_means": halves, "surviving_fraction": survive_fraction,
            "bias_coverage": False, "full_chain_dominance": "R14 reduced checks plus stability; not a theorem"}


def estimate(config, seed, calibration=None):
    started = time.perf_counter()
    setting = dict(config.get("settings", PRIMARY))
    context = Context.build(config.get("kernel", {}), calibration)
    rule = _rule(config.get("rule_id", "balanced"))
    requested = config.get("route", "auto")
    if requested == "we":
        return {"status": "not_estimable", "reason": "WE not implemented", "rows": [], "seconds": 0.}
    plain = simulate(context, rule, setting, seed, "plain")
    fraction = plain["support"][-1].mean()
    route = ("plain" if fraction >= .5 else "fv") if requested == "auto" else requested
    trace = plain if route == "plain" else simulate(context, rule, setting, seed ^ 0x5A17B03D, "fv")
    trajectories_finished = time.perf_counter()
    contexts = config.get("scoring", [{"alpha": 1., "capability": 1., "kappa": 8.}])
    if context.instrument.a10:
        from .instrument import declaration
        for scoring in contexts:
            declared = declaration({k: scoring[k] for k in ("mapping", "k_star", "g")})
            if declared.g != context.instrument.g or round(scoring["capability"], 12) != round(context.config.get("capability", 1.), 12):
                raise ValueError("A10 scoring must match the physical capability and g")
    rows = []
    scoring_seconds = {}
    for scoring in contexts:
        scoring_started = time.perf_counter()
        ctx = replace(context, parameters=replace(context.parameters, kappa=scoring.get("kappa", 8.)))
        if context.instrument.a10:
            from .instrument import Instrument
            ctx = replace(ctx, instrument=Instrument("A10", scoring.get("k_star", context.instrument.k_star), context.instrument.g))
        summary = summarize(trace, ctx, setting, scoring["alpha"], scoring["capability"])
        raw = score_features(plain["features"], ctx, scoring["alpha"], scoring["capability"])
        alive = plain["features"][..., 0] > 0
        lambda_b = _plain_mean(raw[setting["burn"]:], alive[setting["burn"]:])
        ls_paths = (raw - ctx.parameters.extinction_flow).sum(axis=0)
        uncensored = not bool(alive[-1].any())
        summary.update(rule_id=rule.rule_id, rule_hash=digest(rule.__dict__), kernel_hash=context.kernel_hash,
                       initial_population=context.config.get("n_agents", 200),
                       calibration_hash=context.calibration_hash, scoring=scoring,
                       lambda_b=lambda_b, lambda_b_status="finite_window_conditional_estimate" if lambda_b is not None else "unresolved_no_survivors",
                       LS=float(ls_paths.mean()) if uncensored else None,
                       LS_truncated=float(ls_paths.mean()), LS_horizon=len(raw),
                       LS_status="sampled_complete_lifetimes" if uncensored else "censored_lower_surplus",
                       ranking_flag="requires_comparator", route=route,
                       flow_range=ctx.parameters.upper_bound - ctx.parameters.extinction_flow,
                       initial_law_admission={"bound": initial_law_bound(context.config.get("n_agents", 200)).upper,
                                              "horizon": 50, "alpha_spent": 0})
        rows.append(summary)
        if context.instrument.a10:
            arm = str(scoring["k_star"])
            scoring_seconds[arm] = scoring_seconds.get(arm, 0.) + time.perf_counter() - scoring_started
    extra = {"scoring_seconds_by_k_star": scoring_seconds} if context.instrument.a10 else {}
    return {"rows": rows, "route": route, "requested_route": requested, "settings": setting, **extra,
            "plain_survivor_counts": plain["survivor_counts"], "conditioned_survivor_counts": trace["survivor_counts"],
            "ensemble_collapses": trace["collapsed"], "independent_environment": True,
            "continuation_uses_pre_resampling_transitions": True, "kernel": context.config,
            "seed": seed, "fixture_calibration": context.fixture, "calibration_hash": context.calibration_hash,
            "population_steps": int(np.prod(plain["features"].shape[:2]) + (0 if route == "plain" else np.prod(trace["features"].shape[:2]))),
            "population_mean": float(trace["features"][..., 0].mean()), "population_max": int(trace["features"][..., 0].max()),
            "trajectory_seconds": trajectories_finished - started,
            "rescore_seconds": time.perf_counter() - trajectories_finished,
            "seconds": time.perf_counter() - started}


def add_ranking_flags(rows):
    families = {}
    for row in rows:
        key = digest({"kernel": row["kernel_hash"], "scoring": row["scoring"], "calibration": row["calibration_hash"],
                      "initial_population": row.get("initial_population", 200)})
        families.setdefault(key, []).append(row)
    for comparable in families.values():
        for row in comparable:
            flags = []
            for other in comparable:
                if other is row:
                    continue
                if row.get("LS") is not None and other.get("LS") is not None and row.get("lambda_f") and other.get("lambda_f"):
                    a, b = row["lambda_f"]["mean"], other["lambda_f"]["mean"]
                    if a is not None and b is not None:
                        flags.append((a - b) * (row["LS"] - other["LS"]) < 0)
            row["ranking_flag"] = bool(any(flags)) if flags else "unresolved"
    return rows


def reduced_reference_validation(seed=18181):
    """Actual reduced plain/FV experiments against exact Perron references."""
    from .spectral import perron_flow
    rng = np.random.default_rng(seed)
    records = []
    for death in (.001, .01, .05):
        q = (1 - death) * np.array([[.75, .25], [.4, .6]])
        exact = perron_flow(q, [2., 5.], [0, 1])
        count, groups, length, burn = 128, 6, 600, 100
        state = rng.integers(0, 2, (groups, count))
        values, rates = [], []
        for t in range(length):
            draw = rng.random(state.shape)
            killed = draw >= 1 - death
            nxt = (draw >= q[state, 0]).astype(int)
            for g in range(groups):
                survivors = np.flatnonzero(~killed[g])
                if not len(survivors):
                    raise AssertionError("reduced FV collapsed")
                nxt[g, killed[g]] = nxt[g, rng.choice(survivors, int(killed[g].sum()), replace=True)]
            state = nxt
            if t >= burn:
                values.append(np.where(state == 0, 2., 5.).mean(axis=1))
                rates.append(killed.mean(axis=1))
        means, estimates = np.mean(values, axis=0), np.mean(rates, axis=0)
        flow = interval(means, 2, 5)
        rate = interval(estimates, 0, 1)
        passed = abs(flow["mean"] - exact.lambda_f) < max(.015 * exact.lambda_f, 4 * flow["half_width"])
        passed &= abs(rate["mean"] - exact.zeta) < max(.1 * exact.zeta, 4 * rate["half_width"])
        records.append({"death": death, "exact_flow": exact.lambda_f, "exact_zeta": exact.zeta,
                        "FV_flow": flow, "FV_zeta": rate, "passed": bool(passed)})
    # Plain directly conditions independently simulated runs at each time.
    q = .999 * np.array([[.75, .25], [.4, .6]])
    exact = perron_flow(q, [2., 5.], [0, 1])
    state = rng.integers(0, 2, 8192)
    living = np.ones(8192, bool)
    plain_means = []
    for t in range(200):
        draw = rng.random(8192)
        living &= draw < .999
        state = (draw >= q[state, 0]).astype(int)
        state[~living] = 0
        if t >= 100:
            plain_means.append(float(np.where(state[living] == 0, 2, 5).mean()))
    plain_error = abs(np.mean(plain_means) - exact.lambda_f)
    return {"validated": bool(all(r["passed"] for r in records) and plain_error < .03),
            "FV": records, "plain_error": float(plain_error), "plain_survivors": int(living.sum()),
            "full_scale_bias_certified": False}
