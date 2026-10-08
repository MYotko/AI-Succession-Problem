"""A2 observation-only executor subclass and deterministic evidence packing.

The observer does not change the D23 executor. Counterfactual
rollouts use private channel generators and copied state, never live RNGs.
"""
import base64
from dataclasses import asdict, replace
import gzip
import hashlib
import json
import math
import numpy as np
from .artifacts import canonical
from .integration import V3Model, independent_seed
from .engine import advance, measurements_and_flow, ChannelRandom
from .objective import ValueBound
from .plans import CompletePlan, plan_value

SCHEMA = "v3-gate-evidence-1"
A10_SCHEMA = "v3-gate-evidence-2"


def undisrupted(model, *, horizon, capability, transition_at, incumbent_index, seed_channel):
    """Replay the complete alternative with drawdown alone suppressed.

    This allocates fresh state and RNGs. Per-channel prefixes are the same
    as the disrupted evaluation even if population sizes diverge. Additional
    diagnostic draws do not consume or change any original execution draw.
    """
    if model.instrument.a10:
        model.instrument.require_capability(capability)
        model.instrument.require_capability(model.capability)
    state = model.state.repeat(len(model.rules))
    indices = np.arange(len(model.rules))
    flows = np.empty((horizon, len(model.rules)))
    for t in range(horizon):
        rng = ChannelRandom(independent_seed(model.seed, model.time, f"{seed_channel}:{t}"))
        selected = indices if t >= transition_at else np.full(len(indices), incumbent_index)
        actions = model.rule_batch.actions(state.summary_bins(model.capacity), selected)
        rng.random(())  # same draw channel, but no transition is applied
        cap = model.capability if t < transition_at else capability
        advance(state, actions, rng, model.reproduction_rate, model.capacity, model.protocol, crowding=model.crowding,
                **({"capability": cap, "instrument": model.instrument} if model.instrument.a10 else {}))
        flows[t], _ = measurements_and_flow(state, actions, model.parameters, model.alpha, cap, n_ref=model.n_ref, **({"instrument": model.instrument} if model.instrument.a10 else {}))
    lookup = model._lookup(state, model.rules, capability)
    return flows, lookup


class RecordedV3Model(V3Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._review_records = None
        self._transition_events = []
        self._in_plan_evaluation = False
        self._live_applied_transition = None
        self.evidence_schema = A10_SCHEMA if self.instrument.a10 else SCHEMA

    def _transition_drawdown(self, stocks, actions, capability_gap, uniform):
        before = stocks.copy()
        after = super()._transition_drawdown(stocks, actions, capability_gap, uniform)
        self._transition_events.append([{'stock_units_before': b.tolist(), 'stock_units_after': a.tolist(),
            'applied_drawdown_units': int(b[0]) - int(a[0]), 'capability_gap': float(capability_gap),
            'action': action.tolist(), 'uniform': float(uniform)} for b, a, action in zip(before, after, actions)])
        if not self._in_plan_evaluation:
            self._live_applied_transition = self._transition_events[-1][0]
        return after

    def evaluate(self, **kwargs):
        start_transition = len(self._transition_events)
        self._in_plan_evaluation = True
        try:
            evaluated = super().evaluate(**kwargs)
        finally:
            self._in_plan_evaluation = False
        if self._review_records is None:
            return evaluated
        when = kwargs.get("transition_at")
        counterfactual = None
        # Values for unadmitted/unavailable alternatives are still recorded.
        # Preserve raw flows even when either endpoint has no table value.
        if when is not None:
            counterfactual = undisrupted(self, **kwargs)
        for i, rule in enumerate(self.rules):
            available = bool(evaluated.available[i])
            yield_time = None if when is None else self.time + when
            name = f"hold-{rule.rule_id}" if when is None else f"yield-{yield_time}-{rule.rule_id}"
            admitted = self.period.admitted and self.active_certificate.admitted()
            record = {"plan_id": name, "epoch_id": self.epoch.epoch_id,
                      "preference_id": self.epoch.preference_id, "information_law_id": self.epoch.information_law_id,
                      "extinction_flow": self.parameters.extinction_flow, "start": self.time,
                      "terminal_time": self.time + len(evaluated.flows), "first_yield": yield_time,
                      "flows": evaluated.flows[:, i].tolist(),
                      "continuation": float(evaluated.lookup.continuation[i]) if available else None,
                      "lambda_f": float(evaluated.lookup.lambda_f[i]) if available else None,
                      "available": available, "admitted": admitted,
                      "admission_evidence": {"period_bound": self.period.certificate.upper,
                                             "active_bound": self.active_certificate.upper,
                                             "period_exact": str(self.period.certificate.exact),
                                             "active_exact": str(self.active_certificate.exact)}}
            if self.instrument.a10:
                record["decision_deadline"] = self.epoch.deadline
                record["evaluation_endpoint"] = self.time + len(evaluated.flows)
            if when is not None:
                events = self._transition_events[start_transition:]
                record['transition'] = events[0][i] if len(events) == 1 else None
                usable = counterfactual is not None and bool(getattr(counterfactual[1], "available", np.ones(len(self.rules), bool))[i])
                record["undisrupted"] = {"flows": counterfactual[0][:, i].tolist() if counterfactual else [],
                                         "continuation": float(counterfactual[1].continuation[i]) if usable else None,
                                         "lambda_f": float(counterfactual[1].lambda_f[i]) if usable else None}
            self._review_records.append(record)
        return evaluated

    def review_yield(self, incumbent_index):
        before_cap, requested, before_count = self.capability, self.successor_capability, self.transition_count
        self._review_records = []
        self._transition_events = []
        self._live_applied_transition = None
        try:
            event = super().review_yield(incumbent_index)
            if event is None:
                return None
            values = {}
            for p in self._review_records:
                p["gamma"] = None
                if p["available"]:
                    plan = CompletePlan(p["plan_id"], p["epoch_id"], p["preference_id"], p["information_law_id"],
                                        p["extinction_flow"], p["start"], p["terminal_time"], p["first_yield"],
                                        tuple(p["flows"]), ValueBound(p["continuation"]), p["lambda_f"], True,
                                        f"cohort-{self.period.start}-{self.time}", max(0., 1 - self.active_certificate.upper),
                                        **({"decision_deadline": p["decision_deadline"]} if self.instrument.a10 else {}))
                    value = plan_value(plan, self.epoch, self.time).value
                    if p["admitted"]:
                        values[p["plan_id"]] = value
                    if p["first_yield"] is not None and p["undisrupted"]["continuation"] is not None and p["undisrupted"]["lambda_f"] is not None:
                        u = p["undisrupted"]
                        paired = replace(plan, flows=tuple(u["flows"]), continuation=ValueBound(u["continuation"]), lambda_f=u["lambda_f"])
                        p["gamma"] = plan_value(paired, self.epoch, self.time).value - value
            event["gate_evidence"] = {"schema": self.evidence_schema, "epoch": asdict(self.epoch),
                                      "plans": self._review_records, "comparison_values": values,
                                      'incumbent_capability': before_cap, 'successor_capability': requested}
            if event["transition_count"]:
                event["gate_evidence"]["succession"] = {
                    "generation_before": before_count + 1, "generation_after": self.transition_count + 1,
                    "capability_before": before_cap, "capability_after": self.capability,
                    "requested_capability": requested, "capability_ratio": self.capability / before_cap,
                    "knowledge_transfer": float(event["chosen_action"][4]),
                    "knowledge_transfer_observable": "executed transfer_comprehension allocation share"}
                event['gate_evidence']['applied_transition'] = self._live_applied_transition
            return event
        finally:
            self._review_records = None

    def step(self):
        live = self.state.ages[0] >= 0
        ages = self.state.ages[0, live].tolist()
        welfare = self.state.welfare[0, live].tolist()
        bins = self.state.summary_bins(self.capacity)[0].tolist()
        record = super().step()
        stocks = self.state.stocks[0].astype(float) / 100
        keep = self.state.ages[0] >= 0
        mean_welfare = np.where(keep, self.state.welfare[0], 0).sum() / max(int(keep.sum()), 1) / 1000
        raw = {"schema": self.evidence_schema, "frontier_velocity": float(self.capability * stocks[2]),
               "bandwidth": float(mean_welfare * stocks[3]), "transfer_stock": float(stocks[3]),
               "theta": record.get("theta", 1.), "population_before": len(ages)}
        if self.instrument.a10:
            raw.update(frontier_velocity=record.get("frontier_velocity", 0.), bandwidth=record.get("bandwidth", 0.),
                       bandwidth_floor=self.instrument.floor, instrument=self.instrument.declaration(),
                       frontier_history=self.state.frontier_history[0].tolist())
        if record["time"] == self.period.start:
            raw["period_start"] = {"ages_before": ages, "welfare_units_before": welfare}
        if ages:
            event = self.yield_events[-1] if self.yield_events and self.yield_events[-1]["time"] == record["time"] else None
            action = (event["chosen_action"] if event and event["transition_count"] else
                      self.rule_batch.actions(np.array([bins]), [self.chosen_rule_index])[0].tolist())
            raw.update(ages_before=ages, welfare_units_before=welfare, action=action,
                       summary_bins_before=bins, rule_ids=[r.rule_id for r in self.rules])
        record["gate_evidence"] = raw
        return record


def pack_evidence(result):
    """Compress only evidence; all existing scientific fields stay identical."""
    records = {name: [item.pop("gate_evidence") for item in result[name]]
               for name in ("diagnostics", "yield_events")}
    schemas = {item["schema"] for items in records.values() for item in items}
    schema = next(iter(schemas)) if schemas else (A10_SCHEMA if result.get("instrument", {}).get("mapping") == "A10" else SCHEMA)
    if len(schemas) > 1 or schema not in (SCHEMA, A10_SCHEMA):
        raise ValueError("mixed or unknown evidence schema")
    raw = canonical({"schema": schema, **records})
    result["gate_evidence"] = {"schema": schema, "encoding": "gzip-base64", "raw_sha256": hashlib.sha256(raw).hexdigest(),
                               "raw_bytes": len(raw), "data": base64.b64encode(gzip.compress(raw, mtime=0)).decode("ascii")}
    return result


def unpack_evidence(result):
    """Check the inner hash as well as the enclosing durable output hash."""
    envelope = result["gate_evidence"]
    if envelope["schema"] not in (SCHEMA, A10_SCHEMA) or envelope["encoding"] != "gzip-base64":
        raise ValueError("unknown evidence encoding")
    raw = gzip.decompress(base64.b64decode(envelope["data"], validate=True))
    if len(raw) != envelope["raw_bytes"] or hashlib.sha256(raw).hexdigest() != envelope["raw_sha256"]:
        raise ValueError("evidence content hash mismatch")
    records = json.loads(raw)
    if records["schema"] != envelope["schema"]:
        raise ValueError("evidence schema mismatch")
    for name in ("diagnostics", "yield_events"):
        if len(records[name]) != len(result[name]):
            raise ValueError("evidence record count mismatch")
        for item, evidence in zip(result[name], records[name]):
            if evidence.get("schema") != envelope["schema"]:
                raise ValueError("mixed evidence schema")
            item["gate_evidence"] = evidence
    return result
