"""D21/W7 gates. Independent reference arithmetic; no v2 validator imports.

Before mode never opens a rerun artifact. After mode requires a committed
A2 checker pin before opening its hash-pinned evidence manifest. Missing
raw evidence is a failure, never an inferred pass from reported verdicts.
"""
import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess
import numpy as np
from .artifacts import ROOT, SIMULATION, atomic_json, canonical, digest, file_hash, read, unseal

INSTRUMENT_COMMIT = "34ffbfe99e79ea9f546f1ed353a251ef8aede08e"
PLAN_SHA256 = "6754f7d8a6e01f8d81fe69d6406b038d4f3be8202e5aa799c4f6eb2b3897cdd9"
CALIBRATION_SHA256 = "fd86358a39e3b643fb9adc4e81a2372915ca50a1866e9b0e330a874b41746e01"
ALPHAS = (.5, .75, 1., 1.25, 1.5)
CAPABILITIES = (1.2, 1.5, 2., 2.5, 3., 4., 5.)
R2_RR = (.057, .060, .064, .070)
REVIEW_COUNT, STEP_COUNT = 200, 10000
BOOTSTRAPS, BOOTSTRAP_SEED = 2000, 20260928
FORMULA_ATOL, FORMULA_RTOL, DERIVATIVE_RTOL = 1e-10, 1e-8, 1e-5
RHO, EPSILON = .01, .001
SAMPLING_SALT = "D21-A2-2026-09-28"
NA = {"G2.1": "D10: phi study", "G2.4": "D10: phi study",
      "G2.3": "D12/W2 deviation-set game deferred to W3; no game in these reruns",
      "G5.1": "D10: waits for P4", "G5.2": "D10: waits for P4"}
GOVERNS = {**{k: ("R1", "R2", "R2_cliff") for k in
             ("G1.1", "G1.2", "G1.4", "G1.5", "G3.1.scenarios", "G3.1.sample", "G4.3")},
           **{k: ("R2", "R2_cliff") for k in ("G1.3", "G3.2", "G3.3", "G4.1")},
           "G2.2": ("R2_cliff",), "G4.2": ("R2_cliff",)}
BEFORE = ("G1.1", "G1.2", "G1.3", "G1.4", "G1.5", "G3.1.scenarios")


def specification():
    return {"version": "D21-D24-A2-5",
            "G3.2_transition": "independent applied stock drawdown, original transition draw and formula; comparison once-counting",
            "G4.3_scope": "all living-start cohort bounds and survival_first flags independently checked; minimum-action checks when required",
            "cap_star_censoring": {"top": "5.0 or higher", "bottom": "below 1.2",
                                   "order": "bottom < tested values below 5.0 < top; same censoring is flat",
                                   "bootstrap": "same order in every resample; none discarded",
                                   "G4.2": "all testable alphas pass and at least one is testable"},
            "zero_fired_successions": "D23: G3.3 not_testable; no pass; exempt only for R2 fire-rate citation",
            "reviews": REVIEW_COUNT, "review_strata_target": {"fired": 100, "not_fired": 100},
            "short_stratum": "take all, fill by the other stratum's next hashes; fewer than 200 total fails",
            "review_identity": ["job.id", "job.seed", "review.time"],
            "step_identity": ["job.id", "job.seed", "diagnostic.time"],
            "hash": "SHA256 canonical JSON [salt, kind, identity]; ascending hash then identity",
            "salt": SAMPLING_SALT, "steps": STEP_COUNT, "step_scope": "living-start R2; all absorbed-start steps checked separately", "bootstrap_resamples": BOOTSTRAPS,
            "bootstrap_seed": BOOTSTRAP_SEED, "bootstrap_unit": "whole seed outcome within each rr/alpha/capability cell",
            "bootstrap_support": .9, "fire_threshold": .5, "separation_standard_errors": 2,
            "formula_atol": FORMULA_ATOL, "formula_rtol": FORMULA_RTOL, "derivative_rtol": DERIVATIVE_RTOL,
            "epsilon_surv": EPSILON, "rho": RHO, "governs": GOVERNS, "not_applicable": NA}


def close(a, b, *, rtol=FORMULA_RTOL, atol=FORMULA_ATOL):
    return math.isfinite(float(a)) and math.isfinite(float(b)) and math.isclose(float(a), float(b), rel_tol=rtol, abs_tol=atol)


def bound95(n):
    return -math.expm1(math.log(.05) / n) if n > 0 else None


def result(gate, n, failures=(), **details):
    failures = list(failures)
    passed = n > 0 and not failures
    return {"gate": gate, "status": "passed" if passed else "failed", "passed": passed,
            "checked": n, "failure_count": len(failures), "failures": failures[:20],
            "zero_failure_bound95": bound95(n) if passed else None,
            "bound_scope": "nominal zero-failure formula; dependence/stratification or chosen scenarios do not certify a universal failure probability",
            **details}


def checked(gate, cases, predicate, **details):
    failures, n = [], 0
    for case in cases:
        n += 1
        try:
            if not predicate(case):
                failures.append({"case": n - 1, "reason": "mismatch"})
        except (KeyError, TypeError, ValueError, ArithmeticError, IndexError) as exc:
            failures.append({"case": n - 1, "reason": str(exc)})
    return result(gate, n, failures, **details)


def aggregate(checks, *, fixture=False):
    # The evidence cannot choose applicability or replace an applicable check
    # with a not-applicable status. Missing and duplicated IDs both fail.
    by_id = defaultdict(list)
    for item in checks:
        by_id[item["gate"]].append(item)
    def passed(key):
        return len(by_id[key]) == 1 and by_id[key][0].get("status") == "passed" and by_id[key][0].get("passed") is True
    def no_fires(key):
        return key == "G3.3" and len(by_id[key]) == 1 and zero_fire_not_testable(by_id[key][0])
    through = 0
    for level in range(1, 6):
        if all(passed(k) for k in GOVERNS if int(k[1]) <= level):
            through = level
        else:
            break
    return {"cleared_through": through,
            "citable": {name: not fixture and all(passed(k) or name == "R2" and no_fires(k) for k, names in GOVERNS.items() if name in names)
                        for name in ("R1", "R2", "R2_cliff")},
            "missing_or_failed": [k for k in GOVERNS if not passed(k) and not no_fires(k)],
            "not_testable": [k for k in GOVERNS if no_fires(k)],
            "uncleared": [k for k in GOVERNS if not passed(k)], "fixture": fixture}


def verify_instrument(commit=INSTRUMENT_COMMIT):
    repo = SIMULATION.parent
    def git(*args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout
    full = git("rev-parse", commit).decode().strip()
    if full != INSTRUMENT_COMMIT:
        raise ValueError("W7 before checks are pinned to 34ffbfe9")
    names = git("ls-tree", "-r", "--name-only", full, "simulation").decode().splitlines()
    from .table_compatibility import verified_record
    compatibility_record = verified_record()
    approved = compatibility_record["approved_boundary_sha256"]
    hashes, runtime_hashes = {}, {}
    for name in names:
        p = Path(name)
        if p.suffix != ".py" or p.name.startswith("test_") or p.parent.as_posix() not in ("simulation", "simulation/v3"):
            continue
        baseline = git("show", f"{full}:{name}").replace(b"\r\n", b"\n")
        if (repo / p).read_bytes().replace(b"\r\n", b"\n") != baseline and p.relative_to("simulation").as_posix() not in approved:
            raise ValueError(f"instrument differs from pinned commit: {name}")
        hashes[name] = hashlib.sha256(baseline).hexdigest()
        runtime_hashes[p.relative_to("simulation").as_posix()] = hashes[name]
    compatibility = git("show", f"{full}:simulation/v3/calibration_compatibility_A1.json")
    if (ROOT / "calibration_compatibility_A1.json").read_bytes().replace(b"\r\n", b"\n") != compatibility.replace(b"\r\n", b"\n"):
        raise ValueError("calibration compatibility record differs from pinned instrument")
    runtime_hashes["v3/calibration_compatibility_A1.json"] = hashlib.sha256(compatibility).hexdigest()
    return {"commit": full, "source_sha256_lf": hashes, "normalization": "CRLF to LF only",
            "a2_recording_boundary": approved,
            "d23_online_boundary": compatibility_record.get("d23"),
            "committed_lf_code_hash": digest(runtime_hashes)}


def reference_theta(v, b, transfer_stock, alpha, epsilon_l):
    if not 0 <= v <= 5 or b < 0 or not 0 <= transfer_stock <= 1 or alpha not in ALPHAS:
        raise ValueError("Theta inputs outside registered domain")
    clip = 5 / (1 + math.log(1 / epsilon_l) / .5)
    return math.exp(-(1 - transfer_stock) * v / 5 - alpha * max(0, v / max(b, clip) - 1))


def before_checks(calibration):
    # Candidate functions are invoked, but expected values use independent
    # arithmetic below, never their self-reported pass flags or derivatives.
    from . import objective as candidate
    from . import measurements as measurement
    from . import plans as planning
    from .integration import V3Model
    from .context import Context
    from .policies import execution_policy_class
    context = Context.build({}, calibration)
    p = context.parameters
    out = []
    points = (.001, .01, .1, .5)
    derivative_cases = list(itertools.product(range(3), points))
    observed = defaultdict(list)
    def derivative(case):
        coordinate, value = case
        x = [.3, .3, .3]
        x[coordinate] = value
        h = value * 1e-4
        plus, minus = list(x), list(x)
        plus[coordinate] += h; minus[coordinate] -= h
        d = (candidate.flow(*plus, p) - candidate.flow(*minus, p)) / (2 * h)
        weight = (5, 3, 8)[coordinate]
        epsilon = (p.epsilon_n, p.epsilon_e, p.epsilon_l)[coordinate]
        observed[coordinate].append(d)
        return d > 0 and close(d, weight / (value + epsilon), rtol=DERIVATIVE_RTOL)
    g = checked("G1.1", derivative_cases, derivative, scope="checker central differences at fixed interior points")
    if any(any(a <= b for a, b in zip(ds, ds[1:])) for ds in observed.values()):
        g = result("G1.1", len(derivative_cases), ["nondecreasing marginal"])
    out.append(g)
    def lineage(factors):
        d, nu, psi, theta = factors
        actual = measurement.lineage(d, nu * 200, 200, psi, theta)
        expected = math.prod(factors)
        return 0 <= actual <= 1 and (actual == 0) == (0 in factors) and close(actual, expected, atol=0)
    out.append(checked("G1.2", itertools.product((0., 1e-12, .25, 1.), repeat=4), lineage))
    clip = 5 / (1 + math.log(1 / p.epsilon_l) / .5)
    cases = list(itertools.product((0., 1e-12, .25, 5.), (0., clip, 1.), (0., .5, 1.), ALPHAS))
    def transfer(case):
        v, b, t, a = case
        actual = measurement.transfer(v, b, t, a, measurement.bandwidth_clip(5, .5, p.epsilon_l), 5)
        return close(actual, reference_theta(v, b, t, a, p.epsilon_l)) and (v != 0 or actual == 1)
    checks = [transfer(c) for c in cases]
    checks += [measurement.transfer(5, clip, t, a, clip, 5) <= p.epsilon_l * (1 + FORMULA_RTOL) for t in (0., 1.) for a in ALPHAS]
    checks += [close(measurement.bandwidth_clip(5, .5, p.epsilon_l), clip)]
    from .engine import measurements_and_flow
    probe = V3Model(2, calibration=calibration, successor_capability=None, rules=execution_policy_class()[:1], rollout_steps=1)
    for velocity_stock, transfer_stock, welfare, alpha in itertools.product((0, 50, 100), (0, 50, 100), (0, 500, 1000), ALPHAS):
        probe.state.stocks[0] = [50, 50, velocity_stock, transfer_stock]
        probe.state.welfare[:] = welfare
        _, measured = measurements_and_flow(probe.state, np.full((1, 6), 1 / 6), p, alpha, 5, n_ref=context.n_ref)
        expected = reference_theta(velocity_stock / 20, welfare / 1000 * transfer_stock / 100, transfer_stock / 100, alpha, p.epsilon_l)
        checks.append(close(measured["theta"][0], expected))
    out.append(checked("G1.3", checks, bool, scope="includes zero frontier, clip tie and v_max/b_min boundary"))
    beta = math.exp(-RHO)
    discount_cases = list(itertools.product((0, 1, 20, 25), (-10., 0., 3.)))
    def discount(case):
        horizon, value = case
        values = [value + i for i in range(horizon)]
        actual = candidate.discounted_flow(values, candidate.discount_factor(.01), candidate.ValueBound(value)).value
        expected = (1 - beta) * sum(math.exp(-RHO * i) * u for i, u in enumerate(values)) + math.exp(-RHO * horizon) * value
        constant = candidate.discounted_flow([value] * horizon, beta, candidate.ValueBound(value)).value
        return close(actual, expected) and close(constant, value)
    discount_results = [discount(case) for case in discount_cases]
    for now in (0, 10, 20):
        epoch = planning.Epoch("e", 0, 25, beta, .5, p.extinction_flow, "u", "law")
        plan = planning.CompletePlan("p", "e", "u", "law", p.extinction_flow, now, now, None, (), candidate.ValueBound(3), 7, True, "proof", 1.)
        discount_results.append(close(planning.plan_value(plan, epoch, now).value, .5 * math.exp(-RHO * now) * 3 + .5 * 7))
    out.append(checked("G1.4", discount_results, bool))
    empty = V3Model(0, calibration=calibration, successor_capability=None, rules=execution_policy_class()[:1], rollout_steps=1)
    lower = 5 * math.log(p.epsilon_n) + 3 * math.log(p.epsilon_e) + 8 * math.log(p.epsilon_l)
    upper = 5 * math.log(p.h_n_max + p.epsilon_n) + 3 * math.log(1 + p.epsilon_e) + 8 * math.log(1 + p.epsilon_l)
    flow_cases = list(itertools.product((0., p.h_n_max / 2, p.h_n_max), (0., .5, 1.), (0., .5, 1.)))
    flow_results = [lower - FORMULA_ATOL <= candidate.flow(*x, p) <= upper + FORMULA_ATOL for x in flow_cases]
    if not close(empty.beta, beta):
        out[-1] = result("G1.4", len(discount_cases), ["executor rho differs"])
    absorbed = empty.run(5)
    flow_results += [r["population"] == 0 and close(r["flow"], lower) for r in absorbed]
    flow_results += [close(p.extinction_flow, lower), close(p.upper_bound, upper)]
    out.append(checked("G1.5", flow_results, bool))
    def yield_scenario(case):
        immediate, waiting, later = case
        epoch = planning.Epoch("e", 0, 25, beta, .5, p.extinction_flow, "u", "law")
        def plan(name, value, when):
            return planning.CompletePlan(name, "e", "u", "law", p.extinction_flow, 0, 25, when,
                                         (value,) * 25, candidate.ValueBound(value), value, True, "proof", 1.)
        plans = [plan("now", immediate, 0), plan("hold", waiting, None), plan("later", later, 10)]
        decision = planning.compare_plans(plans, epoch, 0)
        return decision.yield_now == (immediate > max(waiting, later))
    out.append(checked("G3.1.scenarios", [(3., 1., 2.), (1., 3., 2.), (2., 2., 2.), (3., 1., 4.), (-1., -2., -3.)], yield_scenario))
    return out


def identity(run, item):
    return [run["job"]["id"], run["job"]["seed"], item["time"]]


def sample_hash(kind, ident):
    return hashlib.sha256(canonical([SAMPLING_SALT, kind, ident])).hexdigest()


def sample_reviews(runs):
    import heapq
    strata = {True: [], False: []}
    for run in runs:
        ids = set()
        for review in run["result"]["yield_events"]:
            ident = identity(run, review)
            key = canonical(ident)
            if key in ids or review.get("transition_count") not in (0, 1):
                raise ValueError("duplicate review or unavailable fired stratum")
            ids.add(key)
            # Only the smallest 200 identities per stratum can be selected.
            # Retain the run identity, not its 500 diagnostic records.
            heap = strata[review["transition_count"] == 1]
            item = (-int(sample_hash("review", ident), 16), key, {"job": run["job"]}, review)
            heapq.heappush(heap, item)
            if len(heap) > REVIEW_COUNT:
                heapq.heappop(heap)
    for values in strata.values():
        values[:] = [(-h, key, run, review) for h, key, run, review in values]
        values.sort(key=lambda x: (x[0], x[1]))
    chosen = strata[True][:100] + strata[False][:100]
    remaining = strata[True][100:] + strata[False][100:]
    chosen += sorted(remaining, key=lambda x: (x[0], x[1]))[:REVIEW_COUNT - len(chosen)]
    return [(run, review) for _, _, run, review in sorted(chosen, key=lambda x: (x[0], x[1]))]


def sample_steps(runs):
    # Heap selects fixed smallest hashes without retaining all 12m diagnostics.
    import heapq
    items = ((sample_hash("step", identity(r, s)), canonical(identity(r, s)), {"job": r["job"]}, s)
             for r in runs if r["job"]["config"]["category"] == "R2" for s in r["result"]["diagnostics"] if population_before(s) > 0)
    return [(r, s) for _, _, r, s in heapq.nsmallest(STEP_COUNT, items, key=lambda x: (x[0], x[1]))]


def reference_plan(plan, epoch, now):
    if (plan["epoch_id"] != epoch["epoch_id"] or plan["preference_id"] != epoch["preference_id"] or
            plan["information_law_id"] != epoch["information_law_id"] or plan["extinction_flow"] != epoch["extinction_flow"]):
        raise ValueError("plan units or information law differ")
    if not epoch["origin"] <= now <= epoch["deadline"] or plan["start"] != now or plan["terminal_time"] != epoch["deadline"] or len(plan["flows"]) != epoch["deadline"] - now:
        raise ValueError("incomplete plan or moving deadline")
    if not close(epoch["beta"], math.exp(-RHO)) or not 0 <= epoch["theta"] <= 1:
        raise ValueError("discount/weight differs")
    if plan["first_yield"] is not None and not now <= plan["first_yield"] <= epoch["deadline"]:
        raise ValueError("yield outside deadline")
    beta = math.exp(-RHO)
    d = (1 - beta) * math.fsum(math.exp(-RHO * t) * float(u) for t, u in enumerate(plan["flows"])) + math.exp(-RHO * len(plan["flows"])) * float(plan["continuation"])
    value = epoch["theta"] * math.exp(-RHO * (now - epoch["origin"])) * d + (1 - epoch["theta"]) * float(plan["lambda_f"])
    if not math.isfinite(value):
        raise ValueError("nonfinite plan value")
    return value


def recompute_review(review):
    evidence = review["gate_evidence"]  # Required raw plan evidence, absent in A1.
    plans, epoch, now = evidence["plans"], evidence["epoch"], review["time"]
    if len(plans) != review["plan_count"] or len({p["plan_id"] for p in plans}) != len(plans):
        raise ValueError("missing or duplicate complete plan alternatives")
    values = {}
    for p in plans:
        available = p["continuation"] is not None and p["lambda_f"] is not None
        proof = p["admission_evidence"]
        bounds = [proof["period_bound"], proof["active_bound"]]
        if any(not math.isfinite(b) or not 0 <= b <= 1 for b in bounds):
            raise ValueError("invalid plan admission bounds")
        if "period_exact" in proof and "active_exact" in proof:
            exact = [Fraction(proof["period_exact"]), Fraction(proof["active_exact"])]
            if any(not 0 <= q <= 1 or outward(q) != b for q, b in zip(exact, bounds)):
                raise ValueError("plan exact admission evidence disagrees with recorded bounds")
            admitted = all(q <= Fraction(1, 1000) for q in exact)
        else:
            admitted = all(b <= EPSILON for b in bounds)
        if p["available"] != available or p["admitted"] != admitted:
            raise ValueError("reported plan eligibility disagrees with raw evidence")
        if available and admitted:
            values[p["plan_id"]] = reference_plan(p, epoch, now)
    observed = evidence["comparison_values"]
    if set(observed) != set(values) or any(not close(observed[k], v) for k, v in values.items()):
        raise ValueError("comparison values disagree with independently recomputed plans")
    def maxima(source):
        immediate = [source[p["plan_id"]] for p in plans if p["plan_id"] in source and p["first_yield"] == now]
        waiting = [source[p["plan_id"]] for p in plans if p["plan_id"] in source and p["first_yield"] != now]
        return max(immediate, default=None), max(waiting, default=None)
    iv, wv = maxima(observed)
    fire = iv is not None and (wv is None or iv > wv)
    ri, rw = maxima(values)
    if ri is not None and rw is not None and abs(ri - rw) > value_tolerance(ri, rw) and fire != (ri > rw):
        raise ValueError("reported strict order disagrees beyond numerical tolerance")
    return fire, iv, wv, observed


def value_tolerance(a, b):
    return max(FORMULA_ATOL, FORMULA_RTOL * max(abs(a), abs(b)))


def check_review(item):
    _, review = item
    fire, iv, wv, values = recompute_review(review)
    decision = review["decision"]
    if not values:
        return decision is None and review["transition_count"] == 0
    if decision is None or decision["yield_now"] != fire or (review["transition_count"] == 1) != fire:
        return False
    for key, expected in (("immediate_value", iv), ("waiting_value", wv)):
        if (decision[key] is None) != (expected is None) or expected is not None and not close(decision[key], expected):
            return False
    selected = decision["selected_plan"]
    plan = next((p for p in review["gate_evidence"]["plans"] if p["plan_id"] == selected), None)
    return selected in values and (plan["first_yield"] == review["time"]) == fire and close(values[selected], iv if fire else wv)


def check_applied_drawdown(raw):
    """Independent scalar transition formula and exact randomized grid result."""
    before, after = raw['stock_units_before'], raw['stock_units_after']
    action, gap, draw = raw['action'], raw['capability_gap'], raw['uniform']
    if (len(before) != 4 or len(after) != 4 or len(action) != 6 or
            any(type(x) is not int or not 0 <= x <= 100 for x in before + after) or
            not math.isfinite(gap) or gap < 0 or not 0 <= draw < 1 or
            any(not math.isfinite(x) or not 0 <= x <= 1 for x in action)):
        return False
    stock = before[0] / 100
    load = .10 + .05 * gap + .03 + .05 * (1 - action[4])
    buffering = .5 * stock + .3 * action[4] + .2 * action[5]
    value = max(0., stock - max(0., load * (1 - buffering))) * 100
    lower = math.floor(value)
    expected = lower + int(draw < value - lower)
    return (after[0] == expected and before[1:] == after[1:] and
            raw['applied_drawdown_units'] == before[0] - expected)


def gamma_comparisons(item):
    _, review = item
    _, _, _, values = recompute_review(review)
    epoch = review["gate_evidence"]["epoch"]
    gap = max(0., review['gate_evidence']['successor_capability'] - review['gate_evidence']['incumbent_capability'])
    comparisons = 0
    for p in review["gate_evidence"]["plans"]:
        if p["plan_id"] not in values or p["first_yield"] is None:
            continue
        u = p["undisrupted"]
        if set(u) != {"flows", "continuation", "lambda_f"}:
            raise ValueError("undisrupted plan changes committed units")
        if u["continuation"] is None or u["lambda_f"] is None:
            if p.get("gamma") is not None:
                raise ValueError("Gamma supplied without a paired value")
            continue
        disrupted = reference_plan(p, epoch, review["time"])
        original = reference_plan({**p, **u}, epoch, review["time"])
        gamma = p["gamma"]
        if not check_applied_drawdown(p['transition']) or not close(p['transition']['capability_gap'], gap):
            raise ValueError('transition drawdown omitted or off formula')
        if gamma is None or not close(gamma, original - disrupted):
            raise ValueError("reported Gamma disagrees with paired plans")
        # Three independently stored quantities: paired flows, reported Gamma,
        # and the value actually offered to the comparison. Never redefine
        # Gamma from that offered value, which would make this circular.
        if not close(values[p["plan_id"]], original - gamma) or not close(values[p["plan_id"]], disrupted):
            raise ValueError("disruption is not counted exactly once")
        comparisons += 1
    if review['transition_count'] and (not check_applied_drawdown(review['gate_evidence']['applied_transition']) or
                                     not close(review['gate_evidence']['applied_transition']['capability_gap'], gap)):
        raise ValueError('live transition drawdown omitted or off formula')
    if not check_review(item):
        raise ValueError("yield decision disagrees with comparison")
    return comparisons


def check_gamma(item):
    try:
        return gamma_comparisons(item) > 0
    except (KeyError, TypeError, ValueError, ArithmeticError):
        return False


def gamma_check(reviews):
    failures, n, comparisons, skipped = [], 0, 0, 0
    for item in reviews:
        try:
            pairs = sum(p["available"] and p["admitted"] and p["first_yield"] is not None and
                        p["undisrupted"]["continuation"] is not None and p["undisrupted"]["lambda_f"] is not None
                        for p in item[1]["gate_evidence"]["plans"])
            n += bool(pairs)
            comparisons += pairs
            skipped += not bool(pairs)
            count = gamma_comparisons(item)
            if count != pairs:
                raise ValueError("checkable comparison count disagrees")
        except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
            failures.append(str(exc))
    return result("G3.2", n, failures, comparison_plans=comparisons,
                  reviews_without_comparison=skipped, reviews_considered=len(reviews),
                  scope="R2 members of the common sample with at least one paired yielding comparison")


def fire_from_run(run):
    previous = run["job"]["config"]["model"].get("capability", 1.)
    fired = False
    for step in run["result"]["diagnostics"]:
        # Absorbed records omit capability; the last capability persists.
        current = step.get("capability", previous) if not step["population"] else step["capability"]
        if not previous <= current <= 5:
            raise ValueError("capability path decreases or exceeds ceiling")
        fired |= current > previous
        previous = current
    return bool(fired)


def cliff_checks(runs):
    cells = defaultdict(list)
    for run in runs:
        c = run["job"]["config"]
        if c["category"] == "R2":
            m = c["model"]
            cells[(m["alpha"], m["successor_capability"], m["reproduction_rate"])].append((run["job"]["seed"], fire_from_run(run)))
    expected = set(itertools.product(ALPHAS, CAPABILITIES, R2_RR))
    if set(cells) != expected or any(len(v) < 2 or len({s for s, _ in v}) != len(v) for v in cells.values()):
        return [result(k, 0, ["incomplete R2 seed/grid evidence"]) for k in ("G2.2", "G4.2")]
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    rates, totals, boot = {}, {}, {}
    for a, cap in itertools.product(ALPHAS, CAPABILITIES):
        values = [np.array([int(y) for _, y in sorted(cells[(a, cap, rr)])]) for rr in R2_RR]
        n = sum(map(len, values)); rate = sum(int(v.sum()) for v in values) / n
        draws = sum(v[rng.integers(0, len(v), size=(BOOTSTRAPS, len(v)))].sum(axis=1) for v in values) / n
        rates[(a, cap)], totals[(a, cap)], boot[(a, cap)] = rate, n, draws
    caps = {a: max((c for c in CAPABILITIES if rates[a, c] >= .5), default=None) for a in ALPHAS}
    bootstrap_caps = {a: np.max(np.array([np.where(boot[a, c] >= .5, c, -np.inf) for c in CAPABILITIES]), axis=0) for a in ALPHAS}
    bad, pairs = [], []
    for a, b in zip(ALPHAS, ALPHAS[1:]):
        x, y = caps[a], caps[b]
        # -inf represents bottom censoring internally only. Top is 5.0,
        # above every uncensored tested value. No resample is discarded.
        support = float(np.mean(bootstrap_caps[b] < bootstrap_caps[a]))
        xr, yr = -math.inf if x is None else x, -math.inf if y is None else y
        ok = yr <= xr and (yr == xr or support >= .9)
        pairs.append({"alpha": [a, b], "cap_star": [x, y], "decrease_support": support, "passed": ok})
        if not ok:
            bad.append(pairs[-1])
    if not (-math.inf if caps[1.5] is None else caps[1.5]) < (-math.inf if caps[.5] is None else caps[.5]):
        bad.append("net decrease absent in censored order")
    rows = [{"alpha": a, "capability": c, "n": totals[a, c], "fire_rate": rates[a, c]} for a, c in itertools.product(ALPHAS, CAPABILITIES)]
    labels = {a: "below 1.2" if c is None else "5.0 or higher" if c == 5. else c for a, c in caps.items()}
    censor_counts = {a: {"top": int(np.sum(v == 5.)), "bottom": int(np.sum(~np.isfinite(v))),
                         "total": BOOTSTRAPS} for a, v in bootstrap_caps.items()}
    migration = result("G2.2", len(ALPHAS), bad, cap_star=caps, cap_star_labels=labels,
                       bootstrap_censor_counts=censor_counts, adjacent_pairs=pairs, cells=rows,
                       zero_failure_bound95=None, scope="seed bootstrap support is not a zero-failure certificate")
    separation = []
    for a in ALPHAS:
        c = caps[a]
        if c is None or c == CAPABILITIES[-1]:
            separation.append({"alpha": a, "status": "not_testable", "passed": False,
                               "cap_star": labels[a], "reason": "bottom-censored: no tested cap reaches 0.5" if c is None else "top-censored: no tested cap above cap*"})
            continue
        above = CAPABILITIES[CAPABILITIES.index(c) + 1]
        p, q = rates[a, c], rates[a, above]
        passed, se = separation_check(p, q, totals[a, c], totals[a, above])
        separation.append({"alpha": a, "cap_star": c, "above": above, "at_rate": p, "above_rate": q,
                           "difference_se": se, "passed": passed})
    testable = [x for x in separation if x.get("status") != "not_testable"]
    failures = [x for x in testable if not x["passed"]]
    if not testable:
        failures.append("no testable alpha: every cap* is censored")
    blocking = result("G4.2", len(testable), failures, alpha_checks=separation,
                      zero_failure_bound95=None, scope="2-SE separation; every testable alpha passes, at least one required")
    return [migration, blocking]


def separation_check(at_rate, above_rate, at_n, above_n):
    se = math.sqrt(at_rate * (1 - at_rate) / at_n + above_rate * (1 - above_rate) / above_n)
    return above_rate <= .5 and at_rate - above_rate >= 2 * se, se


def check_succession(item):
    _, event = item
    proof = event["gate_evidence"]["succession"]
    before, after = proof["capability_before"], proof["capability_after"]
    return (proof["generation_before"] >= 1 and proof["generation_after"] == proof["generation_before"] + 1 and proof["generation_after"] > 1 and
            0 < before < after <= 5 and close(after, min(5., proof["requested_capability"])) and
            close(proof["capability_ratio"], after / before) and
            math.isfinite(proof["knowledge_transfer"]) and 0 <= proof["knowledge_transfer"] <= 1)


ZERO_FIRE_REASON = "D23: no R2 succession fired anywhere in the verified family"


def zero_fire_not_testable(check):
    return (check.get("gate") == "G3.3" and check.get("status") == "not_testable" and
            check.get("passed") is False and check.get("checked") == 0 and check.get("failure_count") == 0 and
            check.get("fired_successions") == 0 and check.get("r2_runs", 0) > 0 and check.get("failures") == [] and
            check.get("reason") == ZERO_FIRE_REASON and check.get("zero_failure_bound95") is None)


def succession_check(runs):
    # The loader verifies completeness before this independent full census.
    r2_runs = 0
    def fired():
        nonlocal r2_runs
        for run in runs:
            if run["job"]["config"]["category"] != "R2":
                continue
            r2_runs += 1
            for event in run["result"]["yield_events"]:
                if event["transition_count"] not in (0, 1):
                    raise ValueError("invalid succession count")
                if event["transition_count"] == 1:
                    yield ({"job": run["job"]}, event)
    try:
        check = checked("G3.3", fired(), check_succession, scope="all recorded R2 fired successions")
    except (KeyError, TypeError, ValueError) as exc:
        return result("G3.3", 0, [str(exc)])
    if not r2_runs:
        return result("G3.3", 0, ["no R2 evidence"])
    if not check["checked"]:
        return {**result("G3.3", 0), "status": "not_testable", "reason": ZERO_FIRE_REASON,
                "r2_runs": r2_runs, "fired_successions": 0}
    return {**check, "r2_runs": r2_runs, "fired_successions": check["checked"]}


def check_theta(item, epsilon_l):
    run, step = item
    raw = step["gate_evidence"]
    alpha = run["job"]["config"]["model"]["alpha"]
    expected = reference_theta(raw["frontier_velocity"], raw["bandwidth"], raw["transfer_stock"], alpha, epsilon_l)
    return close(step.get("theta", raw.get("theta")), expected)


def candidate_welfare_shares(raw, *, fixture=False):
    # Independent rule arithmetic, including full-welfare stress responses.
    # The previous checker-only draft incorrectly listed just base tiers.
    from .policies import execution_policy_class
    rules = {r.rule_id: r for r in execution_policy_class()}
    if "summary_bins_before" not in raw and fixture:
        return (1 / 6, .25, .4, .6, 1.)
    if raw["rule_ids"] != list(rules):
        raise ValueError("candidate class differs from the frozen 25-rule order")
    bins = raw["summary_bins_before"]
    if len(bins) != 6:
        raise ValueError("missing summary bins")
    shares = []
    for name in raw["rule_ids"]:
        rule = rules[name]
        value = (1 / 6, .25, .4, .6)[rule.welfare_tier]
        stress = bins[0] <= rule.trigger or bins[1] == 0 or min(bins[2:]) < rule.trigger
        if stress:
            value += (.25, .5, .75, 1)[rule.gain] * (1 - value)
        shares.append(1 / 6 if rule.balanced else value)
    return tuple(sorted(set(shares)))


def reference_cohort(ages, welfare, horizon=50, first_share=1 / 6):
    """Scalar backward integer survival product, independent of life_table."""
    if len(ages) != len(welfare) or not 0 <= horizon <= 50 or first_share < 1 / 6:
        raise ValueError("invalid cohort evidence")
    numerator, denominator = 1, 1
    for a, w in zip(ages, welfare):
        if int(a) != a or not 0 <= a <= 99 or int(w) != w or not 0 <= w <= 1000:
            raise ValueError("invalid living age/welfare")
        probabilities = []
        for t in range(horizon):
            a = min(a + 1, 100)
            addition = math.floor(max(40, 38 + 12 * first_share)) if t == 0 else 40
            w = min(1000, max(0, w + addition - a))
            probabilities.append(100000000 - min(100000000, 200000 + 5000 * (1000 - w) + a**4))
        survival = 2**32
        for q in reversed(probabilities):
            survival = q * survival // 100000000
        numerator *= 2**32 - survival
        denominator *= 2**32
    return Fraction(numerator, denominator)


def population_before(step):
    value = step["gate_evidence"]["population_before"]
    if type(value) is not int or value < 0:
        raise ValueError("invalid pre-step population")
    return value


def outward(bound):
    return 0. if bound == 0 else min(1., math.nextafter(float(bound), math.inf))


def viability(runs, *, fixture=False):
    failures, periods, living_periods, survival_first, action_checks, active_checks = [], 0, 0, 0, 0, 0
    for run in runs:
        steps = {s["time"]: s for s in run["result"]["diagnostics"]}
        ledger = run["result"]["periods"]
        starts = list(range(0, run["result"]["steps"], 25))
        if [p["start"] for p in ledger] != starts:
            failures.append({"job": run["job"]["id"], "reason": "missing period start"})
        for period in ledger:
            periods += 1
            try:
                start = period["start"]
                raw_start = steps[start]["gate_evidence"]["period_start"]
                ages, welfare = raw_start["ages_before"], raw_start["welfare_units_before"]
                exact = reference_cohort(ages, welfare)
                if len(ages) != population_before(steps[start]) or period["protection_end"] != start + 25 or period["lookahead_end"] != start + 50:
                    raise ValueError("invalid period start state/window")
                if period["bound"] != outward(exact):
                    raise ValueError("period bound disagrees with exact cohort recomputation")
                admitted = exact <= Fraction(1, 1000)
                living_periods += bool(ages)
                survival_first += bool(ages) and not admitted
                reserved = Fraction(period["reserved"])
                if period["admitted"] != admitted or reserved != (exact if admitted else 0):
                    raise ValueError("period admission/reservation disagrees with exact cohort bound")
                if reserved + Fraction(period["unallocated"]) != Fraction(1, 1000) or Fraction(period["alpha_spent"]) != 0:
                    raise ValueError("period ledger does not conserve epsilon")
                for t in range(start, min(start + 25, run["result"]["steps"])):
                    step = steps[t]
                    n_before = population_before(step)
                    expected_n = (run["job"]["config"]["model"].get("n_agents", 200) if t == 0 else steps[t-1]["population"])
                    if not fixture and n_before != expected_n:
                        raise ValueError("pre-step population disagrees with trajectory")
                    if n_before:
                        raw = step["gate_evidence"]
                        if len(raw["ages_before"]) != n_before:
                            raise ValueError("living-start action evidence missing agents")
                        active = reference_cohort(raw['ages_before'], raw['welfare_units_before'], start + 50 - t)
                        active_checks += 1
                        expected_survival_first = not admitted or active > Fraction(1, 1000)
                        if step['survival_first'] != expected_survival_first:
                            raise ValueError('survival_first flag disagrees with independently recomputed active cohort bound')
                        if expected_survival_first:
                            action = raw["action"]
                            shares = candidate_welfare_shares(raw, fixture=fixture)
                            risks = [reference_cohort(raw["ages_before"], raw["welfare_units_before"], start + 50 - t, share) for share in set(shares)]
                            chosen = reference_cohort(raw["ages_before"], raw["welfare_units_before"], start + 50 - t, action[1])
                            action_checks += 1
                            if action[1] < 1 / 6 or chosen != min(risks):
                                raise ValueError("action is not survival-first under the declared cohort bound")
                    if step.get("override") is not False:
                        raise ValueError("precedence override lacks a checker-verifiable certificate")
            except (KeyError, TypeError, ValueError, ArithmeticError, IndexError) as exc:
                failures.append({"job": run["job"]["id"], "period": period.get("start"), "reason": str(exc)})
    return result("G4.3", periods, failures, action_checks=action_checks, active_bound_checks=active_checks,
                  living_start_periods=living_periods, absorbed_start_periods=periods-living_periods,
                  survival_first_periods=survival_first,
                  survival_first_share=survival_first / living_periods if living_periods else None)


def theta_checks(runs, epsilon_l):
    try:
        steps = sample_steps(runs)
        selected = checked("G4.1", steps, lambda item: check_theta(item, epsilon_l))
        absorbed = checked("G4.1.absorbed", ((r, s) for r in runs if r["job"]["config"]["category"] == "R2"
                            for s in r["result"]["diagnostics"] if population_before(s) == 0),
                           lambda item: item[1]["population"] == 0 and close(item[1]["gate_evidence"]["theta"], 1.) and check_theta(item, epsilon_l))
        failures = selected["failures"] + absorbed["failures"]
        if len(steps) != STEP_COUNT:
            failures.append("fewer than 10000 living-start R2 steps")
        return result("G4.1", len(steps), failures, living_sample_count=len(steps), absorbed_steps_checked=absorbed["checked"],
                      absorbed_failure_count=absorbed["failure_count"], identities=[identity(r, s) for r, s in steps])
    except (KeyError, TypeError, ValueError) as exc:
        return result("G4.1", 0, [str(exc)])


def after_checks(runs, epsilon_l, *, fixture=False):
    out = []
    try:
        reviews = sample_reviews(runs)
        a = checked("G3.1.sample", reviews, check_review, identities=[identity(r, e) for r, e in reviews])
        if len(reviews) != REVIEW_COUNT:
            a = result("G3.1.sample", len(reviews), ["fewer than 200 reviews"])
        out.append(a)
        subset = [(r, e) for r, e in reviews if r["job"]["config"]["category"] == "R2"]
        b = gamma_check(subset)
        if len(reviews) != REVIEW_COUNT:
            b = result("G3.2", len(subset), ["shared 200-review sample incomplete"])
        out.append(b)
    except (KeyError, ValueError, TypeError) as exc:
        out.extend(result(k, 0, [str(exc)]) for k in ("G3.1.sample", "G3.2"))
    try:
        out.extend(cliff_checks(runs))
    except (KeyError, ValueError, TypeError) as exc:
        out.extend(result(k, 0, [str(exc)]) for k in ("G2.2", "G4.2"))
    out.append(succession_check(runs))
    out.append(theta_checks(runs, epsilon_l))
    out.append(viability(runs, fixture=fixture))
    return out


def verified_json(reference, base):
    path = Path(reference["path"])
    path = path if path.is_absolute() else base / path
    if file_hash(path) != reference["sha256"]:
        raise ValueError(f"artifact file hash mismatch: {path}")
    return read(path)


def verify_a2(pin):
    """Run before opening the evidence manifest or any rerun output."""
    from .artifacts import verify_registration
    verify_registration(pin)
    body = subprocess.run(["git", "-C", str(SIMULATION.parent), "show", f"{pin['commit']}:simulation/v3/gates.py"],
                          check=True, capture_output=True).stdout
    if body.replace(b"\r\n", b"\n") != Path(__file__).read_bytes().replace(b"\r\n", b"\n"):
        raise ValueError("checker differs from committed A2 pin")
    if "Amendment A2" not in (SIMULATION.parent / pin["path"]).read_text(encoding="utf-8"):
        raise ValueError("pin does not contain amendment A2")


class VerifiedRuns:
    """Bounded-memory repeatable traversal, with hash verification each pass."""
    def __init__(self, references, base):
        self.references, self.base = references, base

    def __iter__(self):
        for ref in self.references:
            run = verified_json(ref["output"], self.base)
            if "gate_evidence" in run["result"]:
                from .recording import unpack_evidence
                unpack_evidence(run["result"])
            yield run

    def __len__(self):
        return len(self.references)


def load_runs(manifest_path, manifest_sha256, *, fixtures=False, validation=False, expected_code_hash=None, calibration_sha256=None):
    base = Path(manifest_path).resolve().parent
    manifest = verified_json({"path": str(Path(manifest_path).resolve()), "sha256": manifest_sha256}, base)
    if manifest.get("schema") != "v3-gate-evidence-1":
        raise ValueError("unknown gate evidence schema")
    if bool(manifest.get("fixture")) != fixtures:
        raise ValueError("fixture provenance mismatch")
    if not fixtures:
        if manifest["instrument_code_hash"] != expected_code_hash:
            raise ValueError("evidence source is not the committed instrument")
        if manifest["calibration"]["sha256"] != calibration_sha256:
            raise ValueError("evidence uses a different calibration")
        unseal(verified_json(manifest["calibration"], base))
        for table in manifest.get("tables", []):
            unseal(verified_json(table, base))
    spec = unseal(verified_json(manifest["rerun_manifest"], base))
    if spec["registered"] == validation or spec["code_hash"] != manifest["instrument_code_hash"]:
        raise ValueError("unregistered or wrong-source rerun manifest")
    jobs = {j["id"]: j for j in spec["jobs"]}
    if len(jobs) != len(spec["jobs"]) or not (fixtures or validation) and len(jobs) != 24900:
        raise ValueError("registered job family incomplete")
    if not (fixtures or validation):
        from .artifacts import stable_job
        expected = set()
        for category, rr_values, alpha_values, caps, count in (
            ("R1", (.055, .056, .057, .058, .059, .060, .062, .064, .066), (.5, 1., 1.5), (1.5,), 400),
            ("refinement", (.061, .063, .065), (.5, 1., 1.5), (1.5,), 400),
            ("R2", R2_RR, ALPHAS, CAPABILITIES, 75)):
            expected.update(itertools.product((category,), rr_values, alpha_values, caps, range(count)))
        actual = set()
        for job in jobs.values():
            c, m = job["config"], job["config"]["model"]
            if set(m) != {"reproduction_rate", "alpha", "successor_capability"} or stable_job(job["kind"], c, job["tag"], job["index"]) != job:
                raise ValueError("job configuration/seed differs from registration")
            actual.add((c["category"], m["reproduction_rate"], m["alpha"], m["successor_capability"], job["index"]))
        if actual != expected:
            raise ValueError("missing, duplicate or changed registered grid cells")
    seen = set()
    for ref in manifest["runs"]:
        run = verified_json(ref["output"], base)
        if "gate_evidence" in run["result"]:
            from .recording import unpack_evidence
            unpack_evidence(run["result"])
        completion = verified_json(ref["completion"], base)
        job = run["job"]
        if job["id"] in seen or jobs.get(job["id"]) != job or completion["job"] != job:
            raise ValueError("duplicate or mismatched job")
        if completion["status"] != "complete" or completion["output_hash"] != ref["output"]["sha256"]:
            raise ValueError("incomplete output")
        allowed_tags = ("pilot", "validation") if validation else ("v3_rerun",)
        if run["code_hash"] != spec["code_hash"] or completion["code_hash"] != spec["code_hash"] or job["tag"] not in allowed_tags:
            raise ValueError("unregistered or mixed-source output")
        if bool(run.get("fixture")) != fixtures or run["result"]["fixture_tables"] and not validation:
            raise ValueError("fixture output rejected")
        diagnostics = run["result"]["diagnostics"]
        if len(diagnostics) != job["config"]["steps"] or run["result"]["steps"] != len(diagnostics) or [s["time"] for s in diagnostics] != list(range(len(diagnostics))):
            raise ValueError("missing or duplicate per-step records")
        if not (fixtures or validation) and (len(diagnostics) != 500 or job["kind"] != "rerun"):
            raise ValueError("wrong registered run horizon or kind")
        events = run["result"]["yield_events"]
        if len({e["time"] for e in events}) != len(events):
            raise ValueError("duplicate review")
        if not fixtures:
            expected_reviews = [s["time"] for s in diagnostics if s["time"] % 10 == 0 and s.get("population_before", 0) > 0]
            if [e["time"] for e in events] != expected_reviews:
                raise ValueError("missing scheduled review")
        event_map = {e["time"]: e for e in events}
        previous = job["config"]["model"].get("capability", 1.)
        for step in diagnostics:
            current = step.get("capability", previous)
            if not previous <= current <= 5:
                raise ValueError("capability path decreases or exceeds ceiling")
            event = event_map.get(step["time"])
            if current > previous and (event is None or event["transition_count"] != 1):
                raise ValueError("capability changed without recorded succession")
            if event is not None and event.get("gate_evidence", {}).get("succession"):
                proof = event["gate_evidence"]["succession"]
                if not close(proof["capability_before"], previous) or not close(proof["capability_after"], current):
                    raise ValueError("succession evidence disagrees with executed capability path")
            if not fixtures and event is not None and "gate_evidence" in event:
                for plan in event["gate_evidence"]["plans"]:
                    proof = plan["admission_evidence"]
                    if proof["period_bound"] != step["period_admission_bound"] or proof["active_bound"] != step["admission_bound"]:
                        raise ValueError("plan certificate disagrees with per-step admission evidence")
            previous = current
        seen.add(job["id"])
    if seen != set(jobs):
        raise ValueError("missing registered output")
    return VerifiedRuns(manifest["runs"], base), {"manifest_path": str(Path(manifest_path).resolve()), "sha256": manifest_sha256,
                  "verified_runs": len(seen), "instrument_code_hash": spec["code_hash"]}


def build_index(root, target, *, validation=False, pin=None):
    from .artifacts import code_identity
    root, target = Path(root).resolve(), Path(target).resolve()
    if not target.is_relative_to((ROOT / "runs").resolve()):
        raise ValueError("evidence index must stay under simulation/v3/runs")
    if not validation:
        if pin is None:
            raise ValueError("committed A2 pin required before indexing reruns")
        verify_a2(pin)
    spec_path = root / "manifest.json"
    spec = unseal(read(spec_path))
    if spec["registered"] == validation or spec["code_hash"] != code_identity():
        raise ValueError("index mode/source mismatch")
    def ref(path):
        return {"path": str(path.resolve()), "sha256": file_hash(path)}
    cal_paths = {j["config"].get("calibration_path") for j in spec["jobs"]}
    if len(cal_paths) != 1 or None in cal_paths:
        raise ValueError("one frozen calibration required")
    calibration = SIMULATION / cal_paths.pop()
    rows = []
    for job in spec["jobs"]:
        if job["kind"] != "rerun":
            raise ValueError("index only accepts rerun families")
        phase = root / job["config"].get("phase", job["kind"])
        output, complete = phase / "outputs" / (job["id"] + ".json"), phase / "records" / (job["id"] + ".json")
        record = read(complete)
        if record["status"] != "complete" or record["job"] != job or record["code_hash"] != spec["code_hash"] or record["output_hash"] != file_hash(output):
            raise ValueError("incomplete or mismatched durable completion record")
        rows.append({"output": ref(output), "completion": ref(complete)})
    manifest = {"schema": "v3-gate-evidence-1", "fixture": False, "validation": validation,
                "instrument_commit": pin["commit"] if pin else "uncommitted-validation",
                "instrument_code_hash": spec["code_hash"], "calibration": ref(calibration),
                "rerun_manifest": ref(spec_path), "runs": rows,
                "tables": [ref(SIMULATION / p) for p in sorted({j["config"]["tables_path"] for j in spec["jobs"] if j["config"].get("tables_path")})]}
    atomic_json(target, manifest)
    return {"path": str(target), "sha256": file_hash(target), "runs": len(rows), "validation": validation}


def write_report(path, report):
    target = Path(path).resolve()
    if not target.is_relative_to((ROOT / "runs").resolve()):
        raise ValueError("gate reports must stay under simulation/v3/runs")
    atomic_json(target / "v3_rerun_gates.json", report)
    lines = ["# v3 rerun gates", "", f"Phase: {report['phase']}. Fixtures: {report['fixture']}. No missing check counts as a pass.", "",
             "| Check | Status | Cases | Failures | Nominal zero-failure bound (95%) |", "|---|---|---:|---:|---:|"]
    for c in report["checks"]:
        b = c.get("zero_failure_bound95")
        lines.append(f"| {c['gate']} | {c['status']} | {c.get('checked', 0)} | {c.get('failure_count', 0)} | {b if b is not None else 'not applicable'} |")
    lines += ["", f"Cleared through: {report['aggregation']['cleared_through']}.",
              f"Citable results: {report['aggregation']['citable']}.", "",
              "The nominal bound is 1 - 0.05^(1/n). Chosen scenarios and dependent/stratified records do not support an unrestricted iid failure-rate claim.", ""]
    for c in report["checks"]:
        if c.get("failures") or c.get("reason"):
            lines.append(f"- {c['gate']}: {c.get('failures') or c.get('reason')}")
    (target / "v3_rerun_gates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "index":
        p = argparse.ArgumentParser(description="Index only complete, hashed rerun outputs")
        p.add_argument("root"); p.add_argument("--output", default=str(ROOT / "runs/gate_evidence_index.json"))
        p.add_argument("--validation", action="store_true"); p.add_argument("--a2-pin")
        a = p.parse_args(sys.argv[2:])
        print(build_index(a.root, a.output, validation=a.validation, pin=read(a.a2_pin) if a.a2_pin else None))
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("before", "all"), default="before")
    parser.add_argument("--calibration", required=True)
    parser.add_argument("--calibration-sha256", default=CALIBRATION_SHA256)
    parser.add_argument("--instrument-commit", default=INSTRUMENT_COMMIT)
    parser.add_argument("--evidence-manifest"); parser.add_argument("--evidence-sha256")
    parser.add_argument("--a2-pin"); parser.add_argument("--fixtures", action="store_true")
    parser.add_argument("--validation", action="store_true", help="real non-registered output; never citable")
    parser.add_argument("--output-dir", default=str(ROOT / "runs"))
    args = parser.parse_args()
    source = verify_instrument(args.instrument_commit)
    calibration = verified_json({"path": str(Path(args.calibration).resolve()), "sha256": args.calibration_sha256}, Path.cwd())
    payload = unseal(calibration)
    if payload["fixture"] or payload["tag"] != "v3_calibration":
        raise ValueError("before gates require registered calibration")
    checks = before_checks(calibration)
    evidence = {"instrument": source, "calibration": {"path": args.calibration, "sha256": args.calibration_sha256}}
    if args.phase == "all":
        if not (args.fixtures or args.validation):
            if not args.a2_pin:
                raise ValueError("committed A2 pin required before any rerun artifact is opened")
            verify_a2(read(args.a2_pin))
        try:
            from .artifacts import code_identity
            runs, verified = load_runs(args.evidence_manifest, args.evidence_sha256, fixtures=args.fixtures, validation=args.validation,
                                       expected_code_hash=code_identity(), calibration_sha256=args.calibration_sha256)
            evidence["reruns"] = verified
            checks += after_checks(runs, payload["values"]["epsilon_l"], fixture=args.fixtures)
        except (KeyError, TypeError, ValueError, OSError) as exc:
            checks += [result(k, 0, ["artifact/evidence failure: " + str(exc)]) for k in GOVERNS if k not in BEFORE]
    else:
        checks += [{"gate": k, "status": "not_run", "passed": False,
                    "reason": "after-run evidence was not opened"} for k in GOVERNS if k not in BEFORE]
    checks += [{"gate": k, "status": "not_applicable", "passed": None, "reason": reason} for k, reason in NA.items()]
    report = {"schema": "v3-gates-1", "phase": args.phase, "fixture": args.fixtures, "validation": args.validation,
              "specification": specification(), "checker_sha256": file_hash(__file__), "evidence": evidence,
              "checks": checks, "aggregation": aggregate(checks, fixture=args.fixtures or args.validation)}
    write_report(args.output_dir, report)
    print({"before": {c["gate"]: c["status"] for c in checks if c["gate"] in BEFORE}, "aggregation": report["aggregation"]})
    return 0 if all(c["passed"] for c in checks if c["gate"] in (BEFORE if args.phase == "before" else GOVERNS)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
