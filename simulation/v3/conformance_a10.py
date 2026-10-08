"""Executable A10 certification assertions ported from the Codex certifier.

The inherited F1 rejection is replaced by acceptance with an explicit decision
 deadline. All other certified arithmetic and constructed-state assertions are
retained. These are not simulation outcomes or empirical preferences.
"""


def certificate_checks():
    import ast
    import copy
    from dataclasses import asdict, replace
    from decimal import Decimal, localcontext
    import hashlib
    import json
    import math
    from pathlib import Path
    import random
    import sys
    from unittest.mock import patch

    sys.dont_write_bytecode = True
    ROOT = Path(__file__).resolve().parents[2]
    SOURCE = ROOT / "simulation"
    sys.path.insert(0, str(SOURCE))
    import numpy as np
    from v3.cohort import floor_welfare, mortality_numerator
    from v3.context import reproductive_support
    from v3.engine import PopulationBatch, RuleBatch
    from v3.objective import ValueBound, discounted_flow
    from v3.plans import Epoch, CompletePlan, compare_plans, plan_value
    from v3.policies import execution_policy_class
    from v3.stocks import neighbor_probabilities, stock_step, targets, MICROSTEPS

    EXPECTED_CAL = "fd86358a39e3b643fb9adc4e81a2372915ca50a1866e9b0e330a874b41746e01"
    cal_bytes = (SOURCE / "v3/runs/registered/v3_rerun_calibration.json").read_bytes()
    cal = json.loads(cal_bytes)
    assert hashlib.sha256(cal_bytes).hexdigest() == EXPECTED_CAL
    canonical = json.dumps(cal["payload"], sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False).encode()
    assert hashlib.sha256(canonical).hexdigest() == cal["sha256"]
    p = cal["payload"]["values"]
    from v3.instrument import validate_constants
    provenance = validate_constants()["provenance"]
    ref = provenance["record"]
    reference_bytes = (json.dumps(ref, sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
    assert hashlib.sha256(reference_bytes).hexdigest() == provenance["record_sha256"]
    WREF, TRREF = 0.8029014082336364, 0.7292628000000001
    assert ref["w_ref"] == WREF and ref["tr_ref"] == TRREF
    EPS = p["epsilon_l"]
    VMAX = math.log(500) / 30
    BETA = math.exp(-0.01)
    CLIP_CAP = 0.014666388971338522
    KAPPAS = (0.75, 8.0)
    ARMS = (1.5, 1.8, 2.3)


    def bmin(k):
        return min(CLIP_CAP, math.log(k) / 30 * 0.325 / (WREF * TRREF))


    def theta(v, b, tr, alpha, k):
        return math.exp(-(1 - tr) * v / VMAX
                        - alpha * max(0, v / max(b, bmin(k)) - 1))


    def he(c, x, power):
        return -math.expm1(-2.5 * c**power * x)


    out = {"scope": "analytic checks and constructed states; no study workloads or outcome rates",
           "calibration_file_sha256": EXPECTED_CAL,
           "calibration_payload_sha256": cal["sha256"],
           "reference_record": ref}

    floor_rows = []
    with localcontext() as dc:
        dc.prec = 70
        vd = Decimal(500).ln() / 30
        ed = Decimal("0.001412790614729507")
        capd = Decimal("0.014666388971338522")
        theoretical_cap = vd / (1 + 2 * (1 / ed).ln())
        for k in ARMS:
            bd = min(capd, Decimal(str(k)).ln() / 30 * Decimal("0.325") /
                     (Decimal(str(WREF)) * Decimal(str(TRREF))))
            td = (-(vd / bd - 1) / 2).exp()
            assert td <= ed
            floor_rows.append({"k_star": k, "b_min": float(bd),
                               "worst_theta": float(td),
                               "exact_decimal_theta_le_epsilon": True,
                               "max_pace_over_bandwidth": VMAX / bmin(k)})
        out["floor_cap_decimal"] = {"specified": str(capd),
                                     "largest_permitted_by_formula": str(theoretical_cap)}
    out["floor_guarantee"] = floor_rows

    count = 0
    for k in ARMS:
        for alpha in (0.5, 0.75, 1.0, 1.25, 1.5):
            for tr in (0.0, 0.01, 0.5, 0.73, 1.0):
                for b in (0.0, bmin(k) / 2, bmin(k), bmin(k) * 2, 0.1):
                    assert theta(0, b, tr, alpha, k) == 1
                    for v in (0.0, 1e-12, bmin(k), VMAX):
                        assert 0 < theta(v, b, tr, alpha, k) <= 1
                        count += 1
                assert theta(VMAX, 0, tr, alpha, k) == theta(VMAX, bmin(k) / 2, tr, alpha, k)
    out["theta_checks"] = {"constructed_evaluations": count,
                            "no_time_jump_example": theta(math.log(1.2) / 30, 0, 1, 0.5, 1.5),
                            "zero_technology_with_recent_cap_jump": theta(math.log(5) / 30, 0, 0, 0.5, 1.5)}

    # Construct a supported stock path, using the actual microstep probabilities.
    # No agents, mortality sampling or full simulation executor are involved.
    action = np.full((1, 6), 1 / 6)
    units = np.array([[50, 30, 50, 50]], dtype=np.uint8)
    technology = [50]
    minimum_selected_interval = 1.0
    for step in range(1, 38):
        wanted = max(1, 50 - 16 * step) if step <= 4 else (1 if step <= 7 else min(100, 1 + 16 * (step - 7)))
        micro = units.astype(np.int16).copy()
        draws = np.empty((MICROSTEPS, 4))
        target = targets(action)
        for m in range(MICROSTEPS):
            up, down = neighbor_probabilities(micro, target)
            assert np.all(up + down < 1)
            draws[m] = (1 + up[0] + down[0]) / 2  # self-move on other stocks
            direction = int(wanted > micro[0, 2]) - int(wanted < micro[0, 2])
            if direction > 0:
                draws[m, 2] = up[0, 2] / 2
                width = up[0, 2]
            elif direction < 0:
                draws[m, 2] = up[0, 2] + down[0, 2] / 2
                width = down[0, 2]
            else:
                width = 1 - up[0, 2] - down[0, 2]
            assert width > 0
            minimum_selected_interval = min(minimum_selected_interval, float(width))
            micro[0, 2] += direction
        units = stock_step(units, action, draws)
        assert int(units[0, 2]) == wanted
        technology.append(wanted)
    f7, f37 = 1 * max(technology[7] / 100, .01), 5 * max(technology[37] / 100, .01)
    assert f7 == .01 and f37 == 5
    assert math.isclose(math.log(f37 / f7) / 30, VMAX, rel_tol=0, abs_tol=1e-16)
    out["pace_support_witness"] = {"T_units_0_through_37": technology,
                                    "assumed_accepted_handover": {"time": 10, "from": 1, "to": 5},
                                    "F_7": f7, "F_37": f37, "pace_37": VMAX,
                                    "all_selected_stock_intervals_positive": minimum_selected_interval > 0,
                                    "qualification": "kernel support conditional on acceptance; no claim that the online objective selects this handover"}

    hmax = 5 * math.log2(1 + 1 / p["sigma_squared"])
    out["flow_bounds"] = []
    for kap in KAPPAS:
        lower = 5 * math.log(p["epsilon_n"]) + 3 * math.log(p["epsilon_e"]) + kap * math.log(EPS)
        upper = 5 * math.log(hmax + p["epsilon_n"]) + 3 * math.log(1 + p["epsilon_e"]) + kap * math.log(1 + EPS)
        out["flow_bounds"].append({"kappa": kap, "H_N_max": hmax, "lower": lower, "upper": upper})

    rules = execution_policy_class()
    stressed = RuleBatch(rules).actions(np.tile([0, 0, 0, 0, 0, 0], (len(rules), 1)))
    assert np.any(stressed[:, 0] == 0)
    for power in (1.0, 0.5):
        for c in (1, 1.2, 5):
            assert he(c, 0, power) == 0
            assert 0 <= he(c, 1, power) <= 1
    ages = np.arange(1, 101)[:, None]
    welfare = np.arange(1001)[None, :]
    floor = floor_welfare(ages, welfare)
    welfare_checks = 0
    for power in (1.0, 0.5):
        for c in (1, 1.2, 5):
            for share in (1 / 6, .25, .4, .6, 1):
                increment = max(40, 38 + 12 * c**power * share)
                lower_rounding = np.floor(np.clip(welfare + increment - ages, 0, 1000)).astype(int)
                assert np.all(lower_rounding >= floor)
                assert np.all(mortality_numerator(ages, lower_rounding) <= mortality_numerator(ages, floor))
                welfare_checks += lower_rounding.size
    out["execution_welfare"] = {"shared_execution_minimum": 0,
                                "max_increment_linear": 98,
                                "max_increment_sqrt": 38 + 12 * math.sqrt(5),
                                "grid_comparisons": welfare_checks,
                                "all_lower_rounding_outcomes_above_floor": True}

    # A C2-dependent support issue in the supplied table code, not a study run.
    single = PopulationBatch(np.array([[48]]), np.array([[485]]), np.array([[0]]),
                             np.full((1, 10), .2), np.array([[50, 30, 50, 50]]),
                             np.zeros((1, 10, 64, 10)), np.zeros((1, 10), int), np.zeros(1))
    assert not reproductive_support(single)[0]
    new_welfares = {str(power): math.floor(485 + max(40, 38 + 12 * 5**power) - 49)
                    for power in (1.0, .5)}
    assert all(w >= 500 for w in new_welfares.values())
    out["old_support_counterexample_under_C2"] = {"age": 48, "welfare_units": 485,
        "capability": 5, "welfare_share": 1, "old_support": False,
        "next_age": 49, "C2_lower_rounded_next_welfare": new_welfares}

    # Correct reward offsets and the inherited terminal-time guard.
    epoch = Epoch("e", 0, 25, BETA, .5, -100., "p", "i")
    def make_plan(name, now, terminal, first_yield, flow, admitted=True):
        return CompletePlan(name, "e", "p", "i", -100., now, terminal, first_yield,
                            (flow,) * (terminal - now), ValueBound(flow), flow,
                            admitted, "constructed" if admitted else "", 0.)

    offsets = []
    for now, deadline, origin in ((0,25,0), (10,25,0), (20,25,0), (30,50,25), (40,50,25)):
        h = deadline + 30 - now
        rows = (2.,) * h
        d = discounted_flow(rows, BETA, ValueBound(2.))
        assert math.isclose(d.value, 2., abs_tol=1e-12)
        epoch_tail_discount = BETA**(now-origin) * BETA**h
        assert math.isclose(epoch_tail_discount, BETA**55, abs_tol=1e-15)
        offsets.append({"review": now, "horizon": h, "epoch_continuation_discount": epoch_tail_discount})
    f1 = replace(make_plan("F1", 10, 55, 20, 2.), decision_deadline=25)
    assert math.isclose(plan_value(f1, epoch, 10).value, .5*BETA**10*2 + .5*2, abs_tol=1e-12)
    out["F1_bookkeeping"] = {"offsets": offsets, "A10_explicit_endpoint_accepted": True}

    # compare_plans does no sampling and changes no supplied object or RNG state.
    tie = [make_plan("immediate", 10, 25, 10, 2.), make_plan("wait", 10, 25, 20, 2.),
           make_plan("hold", 10, 25, None, 2.)]
    original = copy.deepcopy(tie)
    global_before = copy.deepcopy(np.random.get_state())
    std_before = random.getstate()
    private_generator = np.random.default_rng(20261007)
    private_before = copy.deepcopy(private_generator.bit_generator.state)
    with patch("numpy.random.default_rng", side_effect=AssertionError("unexpected generator")), \
         patch("numpy.random.random", side_effect=AssertionError("unexpected sample")), \
         patch("random.random", side_effect=AssertionError("unexpected sample")):
        held = compare_plans(tie, epoch, 10)
        shadow_plans = [replace(tie[0], flows=(3.,)*15, continuation=ValueBound(3.), lambda_f=3.,
                                admitted=False, admission_evidence=""),
                        replace(tie[2], admitted=False, admission_evidence="")]
        shadow = compare_plans(shadow_plans, epoch, 10)
    assert held.yield_now is False and held.selected_plan == "hold"
    assert shadow.yield_now and shadow.survival_first
    assert tie == original and random.getstate() == std_before
    assert private_generator.bit_generator.state == private_before
    global_after = np.random.get_state()
    assert global_before[0] == global_after[0]
    assert np.array_equal(global_before[1], global_after[1]) and global_before[2:] == global_after[2:]
    out["comparison_purity"] = {"tie_holds": True, "inputs_unchanged": True,
        "global_and_private_rng_states_unchanged": True,
        "unadmitted_shadow_can_select_immediate": shadow.yield_now,
        "qualification": "actual execution must retain an explicit admission gate; comparison alone is not that gate"}

    # Different histories at the identical current physical state need different C.
    b = math.log(1.8) / 30 * (.8 * .73) / (WREF * TRREF)
    history_theta = [theta(max(0, math.log(.5 / old)) / 30, b, .73, .5, 1.8)
                     for old in (.01, 1., .5)]
    assert history_theta[0] < history_theta[1] == history_theta[2] == 1
    out["history_counterexample"] = {"current_and_next_T": .5, "constant_capability": 1.2,
        "old_Ts": [.01, 1., .5], "theta_for_each_old_T": history_theta,
        "welfare": .8, "transfer": .73, "alpha": .5}

    # A physical institutional deficit need not disappear after 30 steps.
    pair_stocks = np.array([[77, 30, 77, 73], [67, 30, 77, 73]], dtype=np.uint8)
    for _ in range(31):
        pair_stocks = stock_step(pair_stocks, np.full((2, 6), 1/6), np.full((16, 4), .999))
    assert pair_stocks[:, 0].tolist() == [77, 67]
    out["persistent_transition_counterexample"] = {"steps_after_drawdown": 31,
        "institution_units_undisrupted_and_disrupted": pair_stocks[:, 0].tolist(),
        "all_stock_draws": .999, "rule": "balanced"}

    j = math.log(1.5)/30
    b = math.log(1.8)/30 * (.8*.5)/(WREF*TRREF)
    cost_examples = []
    for future_T in (.3, .5):
        z = math.log(future_T/.5)/30
        v_with, v_without = max(0, z+j), max(0, z)
        t_with = theta(v_with, b, .5, 1.5, 1.8)
        t_without = theta(v_without, b, .5, 1.5, 1.8)
        cost = 8*math.log((.2*t_without+EPS)/(.2*t_with+EPS))
        cost_examples.append({"candidate_future_T": future_T, "common_past_T": .5,
                              "common_jump": j, "pace_increment": v_with-v_without,
                              "flow_loss": cost})
    assert cost_examples[0]["flow_loss"] == 0 < cost_examples[1]["flow_loss"]
    out["allocation_noncommon_cost_counterexample"] = cost_examples

    history_bounds = []
    allocation_bounds = []
    for kap in KAPPAS:
        M = kap * math.log((1 + EPS) / EPS)
        history_bounds.append({"kappa": kap, "lineage_log_span": M,
            "exact_reset_C_difference_29_steps": (1-BETA**29)*M,
            "F1_per_plan_W_bound_theta_half": .5*BETA**55*(1-BETA**29)*M,
            "fixed_domain_fitted_C_bound_fmax_1": M,
            "F1_fitted_per_plan_W_bound_theta_half": .5*BETA**55*M})
        for k in ARMS:
            for ratio in (1.2, 1.5, 5.0):
                jump = math.log(ratio) / 30
                dmax = (1/VMAX + 1.5/bmin(k)) * jump
                cost = kap * math.log((1+EPS)/(math.exp(-dmax)+EPS))
                allocation_bounds.append({"kappa": kap, "k_star": k, "capability_ratio": ratio,
                    "per_flow_direct_jump_cost_bound": cost,
                    "pairwise_order_change_bound_theta_half_10_steps": .5*BETA**20*(1-BETA**10)*cost})
    out["history_bounds"] = history_bounds
    out["allocation_direct_jump_bounds"] = allocation_bounds

    # S3/S4 stationary-flow illustration, not a prediction of the biological chain.
    # Common balanced action, frozen other observables, I in [.67,.77] for ten
    # rewards, restored to .77 thereafter; pace penalty bounded for 30 rewards.
    # All recovery/conditioning assumptions
    # must be read together with the report. No empirical table values are used.
    jump = math.log(1.2) / 30
    transfer = .73
    worst_phi = math.exp(-(1-transfer)*jump/VMAX)
    institution_loss = 8 * math.log(.77/.67)
    pace_loss = 8 * (1-transfer)*jump/VMAX
    loss_bound = institution_loss + pace_loss
    discounted_loss = (1-BETA**10)*institution_loss + (1-BETA**30)*pace_loss
    witness = []
    for power in (1., .5):
        benefit = 3*math.log((he(1.2,1/6,power)+p["epsilon_e"])/(he(1,1/6,power)+p["epsilon_e"]))
        discounted_gain_lower = benefit - discounted_loss
        value_lower = benefit - .5*discounted_loss
        assert value_lower > 0 and discounted_gain_lower > 0
        witness.append({"g_power": power, "stationary_execution_flow_gain": benefit,
                        "transition_flow_loss_upper": loss_bound,
                        "discounted_gain_lower": discounted_gain_lower,
                        "objective_difference_lower": value_lower})
    raw = .10 + .05*.2 + .03 + .05*(1-1/6)
    buffering = .5*.77 + .3/6 + .2/6
    post_drawdown = .77 - raw*(1-buffering)
    assert math.floor(100*post_drawdown) == 67
    assert jump < min(bmin(k) for k in ARMS)
    out["stationary_flow_witness"] = {"assumed_I_before": .77,
        "actual_drawdown_unrounded_I": post_drawdown, "I_lower_grid_outcome": .67,
        "transfer": transfer, "pace": jump, "phi": worst_phi,
        "assumed_physical_recovery_steps": 10, "discounted_transition_loss_upper": discounted_loss,
        "overload_term_zero_all_k_arms": True, "comparisons": witness}

    # A separate exact algebraic existence witness in the requested stationary-flow
    # model: identical traits give D_gen=0, so every lineage term is log(epsilon_L).
    # Hold the nonexecution observables common and all rules unstressed. The maximum
    # compute share in the actual declared class is 1/2, for w0_p1_t1_g3.
    unstressed_actions = RuleBatch(rules).actions(np.tile([3, 3, 3, 1, 3, 2], (len(rules), 1)))
    best_index = int(np.argmax(unstressed_actions[:, 0]))
    assert unstressed_actions[best_index, 0] == .5
    assert rules[best_index].rule_id == "w0_p1_t1_g3"
    zero_lineage_gains = {}
    for power in (1., .5):
        values_before = 3*np.log(-np.expm1(-2.5*unstressed_actions[:, 0])+p["epsilon_e"])
        values_after = 3*np.log(-np.expm1(-2.5*1.2**power*unstressed_actions[:, 0])+p["epsilon_e"])
        gain = float(values_after.max()-values_before.max())
        assert gain > 0
        zero_lineage_gains[str(power)] = gain
    out["zero_lineage_stationary_witness"] = {"best_rule": rules[best_index].rule_id,
        "compute_share": .5, "lineage": 0, "stationary_best_flow_gains": zero_lineage_gains,
        "qualification": "common frozen nonexecution observables and stationary-flow approximation, not full-kernel optimality"}

    # Source-location evidence, without importing or executing study runners.
    locations = {}
    for filename in ("engine.py", "integration.py", "cohort.py", "plans.py", "stocks.py",
                     "objective.py", "calibration.py", "context.py", "continuation.py",
                     "offline_estimator.py", "production_tables.py", "recording.py", "policies.py"):
        tree = ast.parse((SOURCE / "v3" / filename).read_text(encoding="utf-8"))
        locations[filename] = {node.name: node.lineno for node in ast.walk(tree)
                               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    out["source_function_lines"] = locations
    return out
