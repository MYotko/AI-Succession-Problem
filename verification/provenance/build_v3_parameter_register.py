"""Build the v3 instrument parameter provenance register (W11 item 2).

One row per distinct model-driving parameter, plus an excluded list that
accounts for every remaining numeric literal in the scoped modules. The build
is deterministic and create-only: it refuses to overwrite existing outputs
unless run with --force, checks that every scoped literal is either claimed by
a register row or covered by an excluded entry, verifies every evidence quote
verbatim against its source, and writes a manifest with source hashes.

Scope is the import closure of the registered rerun and offline-table path
(``v3.production_runner`` and the modules it reaches, over both
``from .X import`` and ``from . import X`` import forms), which is exactly the
code the registered A4 tables and the R1/R2 reruns run. Off-path diagnostic
and probe scripts under simulation/v3 are recorded in the excluded file at
file granularity, with the closure criterion as the reason.

Evidence quotes are not hand-typed: each row cites one or more exact anchor
substrings, and the build locates each anchor in its source file and renders
the full source line at ``path:line``. A missing anchor fails the build, so a
quote can never be abridged, paraphrased, or attributed to the wrong line.

External constants that v3 imports for its dynamics (the SUCCESSION_* load
factors from simulation/model.py and H_N_V_REF from simulation/metrics.py) are
carried as register rows; their anchors point at the v3 import site. Frozen
calibration file values are carried as rows anchored on the code that produces
them. No simulation code is imported; values are read statically from source.
"""

import argparse
import ast
import collections
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
V3 = ROOT / "simulation" / "v3"

SCOPE_MODULES = (
    "admission", "artifacts", "calibration", "calibration_compatibility",
    "cohort", "context", "continuation", "continuation_validation", "engine",
    "gates", "guards", "integration", "measurements", "objective",
    "offline_estimator", "pilot", "plans", "policies", "production_runner",
    "production_tables", "recording", "recording_validation", "service",
    "spectral", "stocks", "study", "table_compatibility",
    "table_compatibility_a3", "table_repair_a3", "table_validation_a4",
    "tables", "unpublished_bins",
)

# Non-test v3 modules NOT in the registered-path closure. Nothing on the
# production path imports them; they are standalone diagnostic, probe or
# validation harnesses, recorded in the excluded file at file granularity.
OFFPATH_MODULES = (
    "__init__", "a1_screen_diagnosis", "conformance",
    "d23_validation", "diagnose_tables", "integrated_timing", "support",
    "timing_probe",
)


def numeric(node):
    return isinstance(node, ast.Constant) and type(node.value) in (int, float, complex)


class Source:
    def __init__(self, path):
        self.path = path
        self.rel = path.relative_to(ROOT).as_posix()
        self.text = path.read_text(encoding="utf-8-sig")
        self.lines = self.text.splitlines()
        self.tree = ast.parse(self.text, filename=self.rel)
        self.parents = {c: p for p in ast.walk(self.tree) for c in ast.iter_child_nodes(p)}
        self.literals = [n for n in ast.walk(self.tree) if numeric(n)]

    def parent(self, node):
        return self.parents.get(node)

    def ancestry(self, node):
        while node in self.parents:
            node = self.parents[node]
            yield node

    def scope(self, node):
        names = [i.name for i in self.ancestry(node)
                 if isinstance(i, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        return ".".join(reversed(names)) or "<module>"

    def unparse(self, node):
        signed = self.parent(node)
        if isinstance(signed, ast.UnaryOp) and isinstance(signed.op, (ast.USub, ast.UAdd)):
            return ast.unparse(signed)
        return ast.unparse(node)

    def base(self, node):
        """AST-derived owner name for a numeric literal (reduced v2 labeler)."""
        child = node
        for parent in self.ancestry(node):
            if isinstance(parent, ast.Call):
                fn = parent.func
                if isinstance(fn, ast.Attribute) and fn.attr in ("get", "setdefault") \
                        and len(parent.args) > 1 and child is parent.args[1]:
                    key = parent.args[0]
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        return key.value + ".default"
                if isinstance(fn, ast.Name) and fn.id == "getattr" \
                        and len(parent.args) > 2 and child is parent.args[2]:
                    key = parent.args[1]
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        return key.value + ".fallback"
            if isinstance(parent, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = parent.targets if isinstance(parent, ast.Assign) else [parent.target]
                return ",".join(ast.unparse(t) for t in targets)
            if isinstance(parent, ast.arguments):
                pos = parent.posonlyargs + parent.args
                pairs = list(zip(pos[len(pos) - len(parent.defaults):], parent.defaults))
                pairs += list(zip(parent.kwonlyargs, parent.kw_defaults))
                for arg, default in pairs:
                    if child is default:
                        return arg.arg + ".arg"
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                break
            child = parent
        return ""

    def locate_anchor(self, anchor):
        """Return (line, exact_source_span) for the first verbatim occurrence of
        `anchor`. The span is the source line(s) the anchor occupies. Raises if
        the anchor is not a verbatim substring of the file."""
        idx = self.text.find(anchor)
        if idx < 0:
            raise LookupError(f"anchor not found verbatim in {self.rel}: {anchor!r}")
        line = self.text.count("\n", 0, idx) + 1
        end_line = line + anchor.count("\n")
        span = "\n".join(self.lines[line - 1:end_line]).strip()
        return line, span


# ---------------------------------------------------------------------------
# The curated register. `claim` owns literal occurrences; `ev` cites exact
# source anchors that the build verifies verbatim and renders as the quote.
def R(**kw):
    kw.setdefault("units", "")
    kw.setdefault("decided_by", "")
    kw.setdefault("v2_lineage", "")
    kw.setdefault("sensitivity_candidate", "no")
    kw.setdefault("proposed_range", "")
    kw.setdefault("needs_operator_decision", "no")
    kw.setdefault("confidence", "high")
    kw.setdefault("notes", "")
    kw.setdefault("claim", [])
    kw.setdefault("ev", [])          # anchors: "text" (row file) or (file, "text")
    kw.setdefault("evnote", "")      # unverified context (decisions, JSON values)
    return kw


def load_register():
    reg = []

    # === objective / flow weights and discount ===
    reg.append(R(
        name="lambda_n", value="5", units="flow weight (nats)", role="objective",
        used_in="context.FlowParameters; engine.measurements_and_flow; context.score_features",
        cls="arbitrary",
        ev=[("simulation/v3/context.py", "params = FlowParameters(5, 3, config.get(\"kappa\", 8.)")],
        evnote="v3 objective spec S3 (D6-D18); components @ [lambda_n, mu, kappa].",
        decided_by="D6-D18 v3 objective spec S3",
        v2_lineage="lambda_n (v2 objective novelty weight, value 5)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {2, 5, 10} or continuous [1, 10]; joint with mu, kappa (relative weights)",
        notes="Novelty (H_N) log-flow weight. Hardcoded positional arg in Context.build; v2 legacy value 5.",
        file="simulation/v3/context.py", claim=[("lit", 31, "5")]))
    reg.append(R(
        name="mu", value="3", units="flow weight (nats)", role="objective",
        used_in="context.FlowParameters; engine.measurements_and_flow; context.score_features",
        cls="arbitrary",
        ev=[("simulation/v3/context.py", "params = FlowParameters(5, 3, config.get(\"kappa\", 8.)")],
        evnote="v3 objective spec S3; second positional weight on log(H_E).",
        decided_by="D6-D18 v3 objective spec S3",
        v2_lineage="lambda_e (v2 objective execution weight, value 3)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {1, 3, 6} or continuous [1, 10]; joint with lambda_n, kappa",
        notes="Execution (H_E) log-flow weight. Hardcoded positional arg. v2 legacy value 3.",
        file="simulation/v3/context.py", claim=[("lit", 31, "3")]))
    reg.append(R(
        name="kappa", value="8.0 (center; corners 0.75 and 8)", units="flow weight (nats)", role="objective",
        used_in="context.Context.build; integration.V3Model; offline_estimator/table_validation_a4/study/production_tables scoring",
        cls="arbitrary",
        ev=[("simulation/v3/context.py", "config.get(\"kappa\", 8.)"),
            ("simulation/v3/integration.py", "kappa=8.")],
        evnote="D18 item 2 weight-region center kappa=8; design note section 5 corners kappa in {0.75, 8}.",
        decided_by="D18 item 2 (weight region center kappa=8); design note section 5",
        v2_lineage="LAMBDA_LINEAGE_COUPLING (v2 lineage coupling)",
        sensitivity_candidate="yes",
        proposed_range="proposal: pre-registered corners kappa in {0.75, 8} (design note section 5); wider [0.5, 16]",
        notes="Lineage (L) log-flow weight. Default 8 is the declared weight-region center; corners 0.75 and 8 pre-registered.",
        file="simulation/v3/context.py",
        claim=[("lit", 31, "8.0"), ("lit", 31, "8."),
               ("valin", 8.0, ("simulation/v3/integration.py", "simulation/v3/offline_estimator.py",
                               "simulation/v3/table_validation_a4.py", "simulation/v3/study.py",
                               "simulation/v3/production_tables.py"))]))
    reg.append(R(
        name="theta", value="0.5", units="objective mixing weight", role="objective",
        used_in="integration.V3Model; objective.objective; plans.Epoch",
        cls="arbitrary",
        ev=[("simulation/v3/integration.py", "theta=.5"),
            ("simulation/v3/objective.py", "return theta * finite(discounted, \"D_rho\") + (1 - theta) * finite(lambda_f, \"Lambda_F\")")],
        evnote="D18 item 2 weight-region center theta=0.5; corners theta in {0.25, 0.75}.",
        decided_by="D18 item 2 (weight region center theta=0.5); design note section 5",
        sensitivity_candidate="yes",
        proposed_range="proposal: pre-registered corners theta in {0.25, 0.75} (design note section 5); [0, 1]",
        notes="Mixes discounted flow D_rho against lineage surplus Lambda_F: W = theta*D_rho + (1-theta)*Lambda_F.",
        file="simulation/v3/integration.py", claim=[("lit", 53, "0.5"), ("lit", 53, ".5")]))
    reg.append(R(
        name="rho", value="0.01", units="per step (discount rate)", role="objective",
        used_in="objective.discount_factor; integration.beta; continuation; continuation_validation; tables; gates RHO",
        cls="arbitrary",
        ev=[("simulation/v3/integration.py", "self.theta, self.beta, self.rollout_steps, self.crowding = theta, math.exp(-.01)"),
            ("simulation/v3/continuation_validation.py", "BETA = math.exp(-0.01)")],
        evnote="R6: rho=0.01 per step, Delta=1 step; beta=exp(-rho*Delta)=exp(-0.01).",
        decided_by="R6 (rho=0.01 per step, Delta=1 step); design note sections 3, 5",
        sensitivity_candidate="yes",
        proposed_range="proposal: {0.005, 0.01, 0.02} (one decade band); [0.001, 0.05]",
        notes="Per-step discount; beta=exp(-0.01) recurs across integration, continuation, continuation_validation, tables, and as RHO=0.01 in the gate reference arithmetic.",
        file="simulation/v3/integration.py",
        claim=[("valin", -0.01, ("simulation/v3/integration.py", "simulation/v3/continuation.py",
                                 "simulation/v3/continuation_validation.py", "simulation/v3/tables.py")),
               ("litf", "simulation/v3/gates.py", 28, "0.01")]))
    reg.append(R(
        name="delta_step", value="1.0", units="steps", role="objective",
        used_in="objective.discount_factor default", cls="arbitrary",
        ev=[("simulation/v3/objective.py", "def discount_factor(rho, delta=1.0):")],
        decided_by="R6 (Delta=1 step)",
        notes="Discount interval; one step per reward. Fixed by R6.",
        file="simulation/v3/objective.py", claim=[("base", "delta.arg")]))
    reg.append(R(
        name="c_e", value="2.5", units="execution saturation rate", role="objective",
        used_in="measurements.execution; engine/context H_E = -expm1(-2.5*x); calibration values; frozen kernel requirement",
        cls="arbitrary",
        ev=[("simulation/v3/measurements.py", "def execution(x_compute, c_e=2.5):"),
            ("simulation/v3/engine.py", "h_e = -np.expm1(-2.5 * actions[:, 0])"),
            ("simulation/v3/context.py", "if values[\"c_e\"] != 2.5:")],
        evnote="design note section 5: c_E=2.5, the legacy value; also calibration key c_e; frozen kernel raises unless c_E=2.5.",
        decided_by="design note section 5 (c_E=2.5 legacy); calibration key c_e",
        v2_lineage="H_E_COMPUTE_SAT_K (v2 execution saturation, value 2.5)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {1.5, 2.5, 4.0}; [1, 5]. Requires a code change: the engine hard-codes 2.5 and the freeze refuses any other value.",
        needs_operator_decision="yes",
        notes="H_E = -expm1(-c_e * x_compute). Declared, not calibrated. Owns every 2.5 execution-rate literal across measurements, context, engine, calibration. LATENT COUPLING: c_e is frozen at 2.5 by context.py:32 and calibration.py:129, but the engine hard-codes it at engine.py:272 (and context.observable_features at context.py:72) as -expm1(-2.5*x) instead of reading parameters.c_e; a sensitivity screen that varies it must first lift the freeze and replace the hard-coded literal.",
        file="simulation/v3/measurements.py",
        claim=[("base", "c_e.arg"),
               ("valin", 2.5, ("simulation/v3/engine.py", "simulation/v3/context.py", "simulation/v3/calibration.py")),
               ("valin", -2.5, ("simulation/v3/engine.py", "simulation/v3/context.py"))]))
    reg.append(R(
        name="h_e_min", value="0", units="execution flow floor", role="objective",
        used_in="context.build FlowParameters(...,0,...) -> parameters.h_e_min; objective.FlowParameters",
        cls="arbitrary",
        ev=[("simulation/v3/context.py", "params = FlowParameters(5, 3, config.get(\"kappa\", 8.)")],
        evnote="design note section 3: one common H_E^min; the 7th FlowParameters positional arg is 0.",
        decided_by="R3 (one common H_E^min)",
        notes="Common execution-flow floor H_E^min, passed as 0 to FlowParameters. The extinction flow uses log(h_e_min + epsilon_e).",
        file="simulation/v3/context.py", claim=[("lit", 31, "0")]))
    reg.append(R(
        name="fixture_epsilon_defaults", value="1e-6 (epsilon_n/e/l), n_ref 200., center 0.", units="flow floor / ref", role="objective",
        used_in="context.build fixture values (B1-fixture only)",
        cls="arbitrary",
        ev=[("simulation/v3/context.py", "\"epsilon_n\": 1e-6, \"epsilon_e\": 1e-6, \"epsilon_l\": 1e-6, \"n_ref\": 200., \"c_e\": 2.5")],
        evnote="B1-fixture placeholders; superseded on the registered path by the calibrated values (require_production refuses fixtures).",
        sensitivity_candidate="no",
        notes="Fixture flow floors, fixture n_ref=200 and center=0. The fixture c_e=2.5 on the same line is owned by the c_e row.",
        file="simulation/v3/context.py", claim=[("lit", 23, "1e-06"), ("lit", 23, "200.0"), ("lit", 22, "0.0")]))

    # === novelty protocol ===
    reg.append(R(
        name="novelty_sample_size", value="64", units="samples (n)", role="dynamics",
        used_in="measurements.NoveltyProtocol; engine.update_novelty; calibration pooled_samples; context window shape",
        cls="arbitrary",
        ev=[("simulation/v3/measurements.py", "sample_size: int = 64")],
        evnote="R3, D18 item 9: H_N n=64.",
        decided_by="R3, D18 item 9 (H_N n=64)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {32, 64, 128}; must exceed dimension 10",
        notes="Novelty second-moment pooled sample count. Also 64 in calibration (64*sigma) and context window shape.",
        file="simulation/v3/measurements.py", claim=[("base", "sample_size.arg")]))
    reg.append(R(
        name="novelty_lookback", value="10", units="steps", role="dynamics",
        used_in="measurements.NoveltyProtocol; advance_window; novelty; engine window depth",
        cls="arbitrary",
        ev=[("simulation/v3/measurements.py", "lookback: int = 10")],
        evnote="R3, D18 item 9: lookback 10 steps. Distinct from the 10 novelty dimensions.",
        decided_by="R3, D18 item 9 (lookback 10 steps)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {5, 10, 20} steps",
        notes="Novelty window depth in steps.",
        file="simulation/v3/measurements.py", claim=[("base", "lookback.arg")]))
    reg.append(R(
        name="novelty_coordinate_bound", value="1.0", units="deviation from center", role="dynamics",
        used_in="measurements.NoveltyProtocol; bounded_samples/engine/calibration clip",
        cls="arbitrary",
        ev=[("simulation/v3/measurements.py", "coordinate_bound: float = 1.0")],
        evnote="R3: each coordinate clipped at 1.0 from the center.",
        decided_by="R3",
        sensitivity_candidate="yes",
        proposed_range="proposal: {0.5, 1.0, 2.0}",
        notes="Environmental clip on novelty sample coordinates about the fixed center.",
        file="simulation/v3/measurements.py", claim=[("base", "coordinate_bound.arg")]))
    reg.append(R(
        name="novelty_dimensions", value="10", units="dimensions (d)", role="dynamics",
        used_in="measurements/engine/context novelty and propensity length",
        cls="derived",
        ev=[("simulation/v3/measurements.py", "if len(self.novelty_propensity) != 10:")],
        evnote="NOVELTY_DIMS=10 (v2). Fixed trait-space dimension; sets center length and np.eye(10).",
        v2_lineage="NOVELTY_DIMS=10 (v2)",
        notes="Fixed novelty/propensity dimension d=10, structural to the trait space. Not an independent tunable in the reruns.",
        file="simulation/v3/measurements.py", claim=[("lit", 64, "10")]))
    reg.append(R(
        name="propensity_bounds", value="lower 0.05, upper 0.5", units="trait value", role="dynamics",
        used_in="measurements.propensity_diversity; engine child_traits; context.population bank; D_gen normalizer",
        cls="arbitrary",
        ev=[("simulation/v3/measurements.py", "def propensity_diversity(propensities, lower=0.05, upper=0.5):"),
            ("simulation/v3/engine.py", "child_traits = rng.uniform(.05, .5,"),
            ("simulation/v3/engine.py", "result = 2 * distance / (np.maximum(n * (n - 1), 1) * 10 * .45)")],
        evnote="v2 nov_prop_min=0.05, nov_prop_max=0.5. Newborn draw and D_gen span (upper-lower=0.45). measurements.propensity_diversity uses (upper-lower); engine.diversity hard-codes the band width as .45 (with 10 the trait dimension).",
        v2_lineage="nov_prop_min=0.05, nov_prop_max=0.5 (v2 novelty propensity bounds)",
        sensitivity_candidate="yes",
        proposed_range="proposal: widen/narrow the [0.05, 0.5] band, e.g. [0.0, 0.6]. Requires a code change: engine.diversity hard-codes the band width 0.45.",
        needs_operator_decision="yes",
        notes="Newborn novelty-propensity draw bounds and the D_gen normalization span. Mirrored in engine.advance and context.population. LATENT COUPLING: the D_gen normalizer at engine.py:258 hard-codes the band width as 10 * .45, where 0.45 = upper - lower (0.5 - 0.05) and 10 is the trait dimension; measurements.propensity_diversity computes (upper - lower) from the bounds, but engine.diversity does not, so 0.45 does not move if the band is varied. A sensitivity screen must replace the hard-coded 0.45.",
        file="simulation/v3/measurements.py",
        claim=[("base", "lower.arg"), ("base", "upper.arg"),
               ("litf", "simulation/v3/engine.py", 163, "0.05"), ("litf", "simulation/v3/engine.py", 163, "0.5"),
               ("litf", "simulation/v3/context.py", 45, "0.05"), ("litf", "simulation/v3/context.py", 45, "0.5"),
               ("litf", "simulation/v3/engine.py", 258, "0.45")]))

    # === capability / lineage geometry ===
    reg.append(R(
        name="v_max", value="5.0", units="frontier velocity / capability ceiling", role="dynamics",
        used_in="engine.measurements_and_flow; context.score_features; integration admission; capability ceiling",
        cls="arbitrary",
        ev=[("simulation/v3/engine.py", "def measurements_and_flow(batch, actions, parameters, alpha, capability, *, n_ref=200, v_max=5):"),
            ("simulation/v3/context.py", "v / 5 - alpha")],
        evnote="D18 item 3: capability ceiling 5.0; design note section 5: v_max = 5.0.",
        decided_by="D18 item 3 (capability ceiling 5.0, inclusive); design note section 5",
        sensitivity_candidate="yes",
        proposed_range="proposal: {3, 5, 8}; frontier normalization and ceiling move together. Requires a code change: the offline scoring path hard-codes 5.",
        needs_operator_decision="yes",
        notes="Frontier-velocity normalizer and successor capability ceiling. engine.measurements_and_flow reads the v_max parameter, but LATENT COUPLING: the offline scoring path context.score_features (context.py:83) hard-codes it as v / 5 and bandwidth_clip(5, ...) rather than reading v_max, and the integration capability-ceiling checks hard-code 5.; a sensitivity screen that varies v_max must replace those literals too. Owns v_max=5 default and the context.score_features 5 literals.",
        file="simulation/v3/engine.py",
        claim=[("base", "v_max.arg"),
               ("litf", "simulation/v3/context.py", 83, "5")]))
    reg.append(R(
        name="alpha_min", value="0.5", units="alpha", role="dynamics",
        used_in="engine/context bandwidth_clip; measurements.bandwidth_clip",
        cls="arbitrary",
        ev=[("simulation/v3/engine.py", "clip = bandwidth_clip(v_max, .5, parameters.epsilon_l)"),
            ("simulation/v3/context.py", "bandwidth_clip(5, .5, p.epsilon_l)")],
        evnote="R4: b_min = v_max / (1 + ln(1/eps_L)/alpha_min), alpha_min = 0.5.",
        decided_by="R4 (b_min formula with alpha_min=0.5)",
        sensitivity_candidate="yes",
        proposed_range="proposal: tie to the alpha grid minimum; {0.25, 0.5, 1.0}",
        notes="Smallest declared positive alpha, setting the conservative bandwidth clip b_min. Hardcoded .5 in engine and context bandwidth_clip calls.",
        file="simulation/v3/engine.py",
        claim=[("litf", "simulation/v3/engine.py", 268, "0.5"),
               ("litf", "simulation/v3/context.py", 83, "0.5")]))
    reg.append(R(
        name="contagion_clip", value="lower 0.5, upper 2", units="contagion multiplier", role="dynamics",
        used_in="engine.update_novelty", cls="arbitrary",
        ev=[("simulation/v3/engine.py", "contagion = np.clip(batch.h_n / np.maximum(n, 1), .5, 2)")],
        v2_lineage="network-contagion clip 0.5 to 2 (v2 model)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {[0.5,2] baseline, [1,1] off, [0.25,4] wider}",
        notes="Bounds the per-capita novelty contagion multiplier feeding the next novelty draw.",
        file="simulation/v3/engine.py", claim=[("lit", 208, "0.5"), ("lit", 208, ".5"), ("lit", 208, "2")]))
    reg.append(R(
        name="novelty_generation_scale", value="0.8685", units="sample scale", role="dynamics",
        used_in="engine.update_novelty novelty sample draw", cls="arbitrary",
        ev=[("simulation/v3/engine.py", "* .8685 *")],
        v2_lineage="novelty generation scale (v2 agent novelty draw)",
        sensitivity_candidate="yes",
        proposed_range="proposal: +/- 30%, [0.6, 1.1]",
        confidence="medium",
        notes="Magnitude scale on the per-agent novelty sample draw; arbitrary tuned scale carried from v2 novelty generation.",
        file="simulation/v3/engine.py", claim=[("lit", 210, "0.8685"), ("lit", 210, ".8685")]))

    # === demographic kernel ===
    reg.append(R(
        name="reproduction_rate", value="0.08", units="per-step birth rate", role="dynamics",
        used_in="context.kernel_hash; calibration; integration default; engine.advance; offline/study/pilot",
        cls="arbitrary",
        ev=[("simulation/v3/integration.py", "reproduction_rate=.08"),
            ("simulation/v3/calibration.py", "config.get(\"reproduction_rate\", .08) != .08")],
        evnote="v2 KEEP (lead corrected RETIRED->KEEP). Calibration operating point rr=.080; reruns sweep rr on the R1/R2 grids.",
        v2_lineage="reproduction_rate=0.08 (v2 demographic KEEP)",
        notes="Baseline birth rate. KEEP demographic constant and the calibration operating point; not itself a sensitivity target (swept on registered grids). BLIND: not a survival/extinction quantity.",
        file="simulation/v3/integration.py",
        claim=[("valin", 0.08, ("simulation/v3/integration.py", "simulation/v3/calibration.py", "simulation/v3/context.py",
                                "simulation/v3/offline_estimator.py", "simulation/v3/study.py", "simulation/v3/pilot.py"))]))
    reg.append(R(
        name="carrying_capacity", value="1600", units="agents (K)", role="dynamics",
        used_in="context.kernel_hash; calibration; integration default; engine.advance crowding",
        cls="arbitrary",
        ev=[("simulation/v3/integration.py", "carrying_capacity=1600"),
            ("simulation/v3/calibration.py", "advance(state, action, rng, .08, 1600, ctx.protocol, independent=True)")],
        evnote="v2 KEEP. Logistic K in p_birth = rr*max(0,1-crowd/K).",
        v2_lineage="carrying_capacity=1600 (v2 demographic KEEP)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {800, 1600, 3200}",
        notes="Logistic carrying capacity in the birth crowding term.",
        file="simulation/v3/integration.py",
        claim=[("valin", 1600, ("simulation/v3/integration.py", "simulation/v3/calibration.py",
                                "simulation/v3/context.py", "simulation/v3/offline_estimator.py"))]))
    reg.append(R(
        name="mortality_base_numerator", value="200000 (mortality_base 0.002)", units="per 1e8", role="dynamics",
        used_in="cohort.mortality_numerator; engine.advance mortality; life_table",
        cls="arbitrary",
        ev=[("simulation/v3/cohort.py", "return np.minimum(MORTALITY_DENOMINATOR, 200_000 + 5000 * (1000 - welfare) + age**4)")],
        evnote="v2 KEEP: mortality_base=0.002; 0.002*1e8=200000.",
        v2_lineage="mortality_base=0.002 (v2 demographic KEEP)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {0.001, 0.002, 0.004} as a fraction",
        notes="Baseline mortality intercept in the integer mortality law (denominator 1e8). BLIND: a rate input, not a measured rate.",
        file="simulation/v3/cohort.py", claim=[("lit", 22, "200000"), ("lit", 22, "200_000")]))
    reg.append(R(
        name="mortality_welfare_penalty", value="5000 (mortality_wb_penalty 0.05)", units="per 1e8 per welfare-milli", role="dynamics",
        used_in="cohort.mortality_numerator", cls="arbitrary",
        ev=[("simulation/v3/cohort.py", "return np.minimum(MORTALITY_DENOMINATOR, 200_000 + 5000 * (1000 - welfare) + age**4)")],
        evnote="v2 KEEP: mortality_wb_penalty=0.05; 5000 per welfare-thousandth = 0.05 at zero welfare.",
        v2_lineage="mortality_wb_penalty=0.05 (v2 demographic KEEP)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {0.025, 0.05, 0.10} as the fractional penalty",
        notes="Welfare shortfall penalty on mortality.",
        file="simulation/v3/cohort.py", claim=[("lit", 22, "5000")]))
    reg.append(R(
        name="mortality_age_power", value="4", units="exponent", role="dynamics",
        used_in="cohort.mortality_numerator age**4", cls="arbitrary",
        ev=[("simulation/v3/cohort.py", "+ age**4)")],
        evnote="v2 KEEP: mortality_age_power=4.",
        v2_lineage="mortality_age_power=4 (v2 demographic KEEP)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {3, 4, 5}",
        notes="Quartic age term in the mortality numerator.",
        file="simulation/v3/cohort.py", claim=[("lit", 22, "4")]))
    reg.append(R(
        name="mortality_denominator", value="100000000 (1e8)", units="per (1e8)", role="dynamics",
        used_in="cohort.MORTALITY_DENOMINATOR; engine.advance mortality sampling", cls="derived",
        ev=[("simulation/v3/cohort.py", "MORTALITY_DENOMINATOR = 100_000_000")],
        evnote="Docstring: 2**32 * 10**8 < 2**64. Fixed-point scale for exact integer mortality.",
        notes="Fixed-point denominator (1e8) for exact integer mortality sampling; chosen with SCALE=2**32 for overflow safety.",
        file="simulation/v3/cohort.py", claim=[("base", "MORTALITY_DENOMINATOR")]))
    reg.append(R(
        name="welfare_units", value="1000", units="welfare grid resolution", role="dynamics",
        used_in="cohort.WELFARE_UNITS; engine/context welfare thousandths; life_table shape", cls="derived",
        ev=[("simulation/v3/cohort.py", "WELFARE_UNITS = 1000")],
        evnote="R4/R14: welfare on a 0.001 grid; integer thousandths.",
        decided_by="R4/R14 (welfare on a 0.001 grid)",
        notes="Welfare discretization: integer thousandths, i.e. the 0.001 welfare grid.",
        file="simulation/v3/cohort.py", claim=[("base", "WELFARE_UNITS")]))
    reg.append(R(
        name="scale_2_32", value="4294967296 (2**32)", units="survival fixed-point scale", role="dynamics",
        used_in="cohort.SCALE; life_table; cohort_bound; initial_law_bound", cls="derived",
        ev=[("simulation/v3/cohort.py", "SCALE = 2**32")],
        evnote="Docstring: A uint64 multiplication cannot overflow: 2**32 * 10**8 < 2**64.",
        notes="Per-agent survival fixed-point scale for the exact integer cohort life-table. Structural; chosen for overflow safety.",
        file="simulation/v3/cohort.py", claim=[("base", "SCALE")]))
    reg.append(R(
        name="reproductive_age_window", value="lower >18, upper <50; last fertile 49", units="age (years)", role="dynamics",
        used_in="engine.advance fertile/crowding; context.reproductive_support; cohort child_ages",
        cls="arbitrary",
        ev=[("simulation/v3/engine.py", "fertile = alive & (ages > 18) & (ages < 50) & (welfare >= 500)"),
            ("simulation/v3/context.py", "possible = (ages >= 0) & (ages < 49) & (state.welfare + remaining * (remaining + 1) // 2 >= 500)")],
        evnote="v2 KEEP: reproductive ages 18 and 50; reproductive_support uses last fertile age 49; reproductive-crowding variant on the same window.",
        v2_lineage="reproductive ages 18 and 50 (v2 demographic KEEP)",
        sensitivity_candidate="yes",
        proposed_range="proposal: shift the [18,50] window, e.g. [15,45] or [20,55]",
        notes="Fertile age window; also the reproductive-crowding variant (engine.advance) and reproductive_support (ages<49).",
        file="simulation/v3/engine.py",
        claim=[("lit", 139, "18"), ("lit", 139, "50"), ("litf", "simulation/v3/engine.py", 140, "18"),
               ("litf", "simulation/v3/engine.py", 140, "50"),
               ("litf", "simulation/v3/context.py", 62, "49"), ("litf", "simulation/v3/context.py", 64, "49")]))
    reg.append(R(
        name="reproduction_welfare_threshold", value="500 (welfare 0.5)", units="welfare thousandths", role="dynamics",
        used_in="engine.advance fertile; cohort initial_law band; context.reproductive_support",
        cls="arbitrary",
        ev=[("simulation/v3/engine.py", "fertile = alive & (ages > 18) & (ages < 50) & (welfare >= 500)")],
        evnote="v2 KEEP: wb_repro_threshold=wb_repro_floor=0.5; 500 on the 0.001 grid.",
        v2_lineage="wb_repro_threshold = wb_repro_floor = 0.5 (v2 demographic KEEP)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {0.4, 0.5, 0.6}",
        notes="Minimum welfare for fertility (500 = 0.5). Same pivot in the initial-law band and reproductive_support.",
        file="simulation/v3/engine.py",
        claim=[("lit", 139, "500"), ("litf", "simulation/v3/context.py", 64, "500")]))
    reg.append(R(
        name="newborn_welfare_band", value="[0.5, 0.8]", units="well-being", role="dynamics",
        used_in="engine.advance child_raw_welfare; context.population; cohort.initial_law_bound 500:800",
        cls="arbitrary",
        ev=[("simulation/v3/engine.py", "child_raw_welfare = rng.uniform(.5, .8, child_shape)"),
            ("simulation/v3/context.py", "welfare = randomized_units(rng.uniform(.5, .8, (count, n)), 1000, rng.random((count, n)))")],
        evnote="v2 wb_min=0.5, wb_max=0.8. Uniform newborn/entrant well-being; initial_law integrates the same band via welfare indices 500:800.",
        v2_lineage="wb_min=0.5, wb_max=0.8 (v2 newborn/entrant well-being band)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {[0.5,0.8] baseline, [0.4,0.7], [0.6,0.9]}",
        notes="Uniform newborn (and entrant) well-being draw.",
        file="simulation/v3/engine.py",
        claim=[("litf", "simulation/v3/engine.py", 161, "0.5"), ("litf", "simulation/v3/engine.py", 161, "0.8"),
               ("litf", "simulation/v3/context.py", 44, "0.5"), ("litf", "simulation/v3/context.py", 44, "0.8")]))
    reg.append(R(
        name="newborn_max_start_age", value="50", units="age (years)", role="dynamics",
        used_in="engine.advance child_ages; context.population ages", cls="arbitrary",
        ev=[("simulation/v3/engine.py", "child_ages = rng.integers(0, 50, child_shape, dtype=np.int16)"),
            ("simulation/v3/context.py", "ages = rng.integers(0, 50, (count, n), dtype=np.int16)")],
        evnote="v2 human_max_start_age=50. Upper bound (exclusive) on newborn/entrant starting age.",
        v2_lineage="human_max_start_age=50 (v2)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {30, 50, 70}",
        confidence="medium",
        notes="Newborn/entrant starting-age ceiling; a distinct choice from the fertile-age ceiling though it shares the value 50.",
        file="simulation/v3/engine.py",
        claim=[("litf", "simulation/v3/engine.py", 160, "50"), ("litf", "simulation/v3/context.py", 43, "50")]))
    reg.append(R(
        name="welfare_response_gain", value="offset 38, slope 12 (r=0.9+0.12*(share-1/6)); floor 40", units="welfare units per step", role="dynamics",
        used_in="engine.advance increment; cohort.floor_welfare; cohort.first_action_log_bounds",
        cls="derived",
        ev=[("simulation/v3/cohort.py", "# r = .9 + .12*(share-1/6), so 100*(r-.5) = 38+12*share."),
            ("simulation/v3/engine.py", "increment = np.maximum(40, 38 + 12 * actions[:, 1])[:, None]")],
        evnote="Derived from the r=0.9 balanced anchor and 0.12 slope; both arbitrary inputs. Mirrored in cohort.first_action_log_bounds.",
        v2_lineage="well-being resource pivot / r=0.9 balanced anchor (v2)",
        sensitivity_candidate="yes",
        proposed_range="proposal: perturb the r=0.9 balanced anchor and the 0.12 slope that generate 38 and 12",
        confidence="medium",
        notes="Per-step welfare increment vs the bio-welfare share. 40 is the balanced-floor increment; 38 and 12 are the affine coefficients from r=0.9+0.12*(share-1/6).",
        file="simulation/v3/engine.py",
        claim=[("lit", 132, "40"), ("lit", 132, "38"), ("lit", 132, "12"),
               ("litf", "simulation/v3/cohort.py", 111, "38"), ("litf", "simulation/v3/cohort.py", 111, "12")]))
    reg.append(R(
        name="welfare_floor_increment", value="40", units="welfare units per step", role="dynamics",
        used_in="cohort.floor_welfare; cohort.first_action_log_bounds", cls="derived",
        ev=[("simulation/v3/cohort.py", "return np.clip(np.asarray(welfare_units) + 40 - np.asarray(age_after_aging), 0, 1000)")],
        evnote="Docstring: The balanced floor adds 40-age units. Derived from r=0.9.",
        v2_lineage="r=0.9 balanced anchor (v2 well-being)",
        notes="Balanced-allocation welfare increment floor used by the cohort survival lower bound. Same 40 as the engine welfare-response floor.",
        file="simulation/v3/cohort.py", claim=[("lit", 26, "40"), ("litf", "simulation/v3/cohort.py", 111, "40")]))

    # === initial stocks ===
    reg.append(R(
        name="initial_stocks", value="[50, 30, 50, 50] (0.50, 0.30, 0.50, 0.50)", units="stock hundredths", role="dynamics",
        used_in="engine.initial_batch; context.population", cls="arbitrary",
        ev=[("simulation/v3/engine.py", "np.array([[50, 30, 50, 50]], dtype=np.uint8)"),
            ("simulation/v3/context.py", "stocks = np.tile([50, 30, 50, 50], (count, 1)).astype(np.uint8)")],
        evnote="v2: PSI_INST_INITIAL=0.5, RESILIENCE=0.30, THETA_CAPABILITY=0.5, TRANSFER=0.5. On the 0.01 grid.",
        v2_lineage="PSI_INST_INITIAL=0.5, RESILIENCE_STOCK_INITIAL=0.30, THETA_CAPABILITY_INITIAL=0.5, TRANSFER_STATE_INITIAL=0.5 (v2)",
        sensitivity_candidate="yes",
        proposed_range="proposal: perturb each initial stock +/- 0.1 within [0,1]",
        notes="Initial institutional, resilience, capability(theta) and transfer stocks. Owns both the engine and context (entrant) occurrences.",
        file="simulation/v3/engine.py",
        claim=[("litf", "simulation/v3/engine.py", 90, "50"), ("litf", "simulation/v3/engine.py", 90, "30"),
               ("litf", "simulation/v3/context.py", 46, "50"), ("litf", "simulation/v3/context.py", 46, "30")]))

    # === stock kernel ===
    reg.append(R(
        name="stock_relaxation_rates", value="[0.10, 0.12, 0.05, 0.10]", units="per step", role="dynamics",
        used_in="stocks.RATES; continuous_step; MICRO_RATES", cls="arbitrary",
        ev=[("simulation/v3/stocks.py", "RATES = np.array([0.10, 0.12, 0.05, 0.10])")],
        v2_lineage="stock relaxation rates (v2 model R4 stock kernel)",
        sensitivity_candidate="yes",
        proposed_range="proposal: scale each rate +/- 50%",
        notes="Per-step relaxation of the four stocks toward their action targets.",
        file="simulation/v3/stocks.py", claim=[("base", "RATES")]))
    reg.append(R(
        name="stock_target_intercepts", value="[0.4, 0.2, 0.5, 0.4]", units="stock level", role="dynamics",
        used_in="stocks.targets", cls="arbitrary",
        ev=[("simulation/v3/stocks.py", "return np.minimum(1, np.array([0.4, 0.2, 0.5, 0.4]) + np.array([2.2, 3.5, 1.6, 2.0]) * x)")],
        v2_lineage="stock target mapping (v2)",
        sensitivity_candidate="yes",
        proposed_range="proposal: perturb intercepts within [0,1]",
        notes="Baseline (zero-action) stock targets before the action-driven gain.",
        file="simulation/v3/stocks.py", claim=[("lit", 19, "0.4"), ("lit", 19, "0.2"), ("lit", 19, "0.5")]))
    reg.append(R(
        name="stock_target_gains", value="[2.2, 3.5, 1.6, 2.0]", units="stock per unit action", role="dynamics",
        used_in="stocks.targets", cls="arbitrary",
        ev=[("simulation/v3/stocks.py", "np.array([2.2, 3.5, 1.6, 2.0]) * x)")],
        v2_lineage="stock target action gains (v2)",
        sensitivity_candidate="yes",
        proposed_range="proposal: scale gains +/- 30%",
        notes="Action-share slope into each stock target (clipped at 1).",
        file="simulation/v3/stocks.py", claim=[("lit", 19, "2.2"), ("lit", 19, "3.5"), ("lit", 19, "1.6"), ("lit", 19, "2.0")]))
    reg.append(R(
        name="stock_microsteps", value="16", units="microsteps per step", role="dynamics",
        used_in="stocks.MICROSTEPS; engine.advance; tables.kernel_identity", cls="arbitrary",
        ev=[("simulation/v3/stocks.py", "MICROSTEPS = 16")],
        evnote="design note section 3: 16 environmental microsteps per step.",
        decided_by="R4/R14 (16 environmental microsteps per step)",
        notes="Environmental microsteps per stock step on the 0.01 grid; convergence setting. Mirrored in tables.kernel_identity.",
        file="simulation/v3/stocks.py", claim=[("base", "MICROSTEPS"), ("litf", "simulation/v3/tables.py", 18, "16")]))
    reg.append(R(
        name="stock_neighbor_noise", value="0.005", units="probability", role="dynamics",
        used_in="stocks.NEIGHBOR_NOISE; neighbor_probabilities; tables.kernel_identity", cls="arbitrary",
        ev=[("simulation/v3/stocks.py", "NEIGHBOR_NOISE = 0.005")],
        evnote="Docstring: small symmetric neighbor noise supplies two-way support and self moves.",
        decided_by="R4",
        sensitivity_candidate="yes",
        proposed_range="proposal: {0.0025, 0.005, 0.01}",
        notes="Symmetric neighbor transition floor giving two-way support. Mirrored in tables.kernel_identity.",
        file="simulation/v3/stocks.py", claim=[("base", "NEIGHBOR_NOISE"), ("litf", "simulation/v3/tables.py", 19, "0.005")]))
    reg.append(R(
        name="stock_grid", value="0.01", units="stock resolution", role="dynamics",
        used_in="tables.kernel_identity; stocks units/100; design note", cls="arbitrary",
        ev=[("simulation/v3/tables.py", "\"stock_grid\": .01,")],
        evnote="design note section 3: stocks on a 0.01 grid.",
        decided_by="R4/R14 (stocks on a 0.01 grid)",
        notes="Stock discretization (hundredths) embedded in the kernel hash.",
        file="simulation/v3/tables.py", claim=[("lit", 17, "0.01")]))
    reg.append(R(
        name="welfare_grid", value="0.001", units="welfare resolution", role="dynamics",
        used_in="tables.kernel_identity", cls="arbitrary",
        ev=[("simulation/v3/tables.py", "\"welfare_grid\": .001, \"stock_microsteps\": 16,")],
        evnote="design note section 3: welfare on a 0.001 grid; same grid as WELFARE_UNITS=1000.",
        decided_by="R4/R14 (welfare on a 0.001 grid)",
        notes="Welfare discretization embedded in the kernel hash.",
        file="simulation/v3/tables.py", claim=[("lit", 18, "0.001")]))
    reg.append(R(
        name="channel_indices", value="[3, 5, 0, 4]", units="action-channel indices", role="dynamics",
        used_in="stocks.CHANNEL_INDICES; targets", cls="derived",
        ev=[("simulation/v3/stocks.py", "CHANNEL_INDICES = np.array([3, 5, 0, 4])")],
        notes="Which of the six allocation channels drive each of the four stocks. Structural mapping, not a magnitude.",
        file="simulation/v3/stocks.py", claim=[("base", "CHANNEL_INDICES")]))

    # === succession transition load (external model.py) ===
    reg.append(R(
        name="succession_load_factors", value="BASE 0.10, CAPABILITY_GAP 0.05, GENERATION_GAP 0.03, OPACITY 0.05",
        units="stock drawdown fraction", role="dynamics",
        used_in="stocks.transition_drawdown (from model.py); integration; gate G3.2", cls="arbitrary",
        ev=[("simulation/v3/stocks.py", "from model import (SUCCESSION_BASE_LOAD, SUCCESSION_CAPABILITY_GAP_FACTOR,"),
            ("simulation/v3/gates.py", "load = .10 + .05 * gap + .03 + .05 * (1 - action[4])")],
        evnote="EXTERNAL (simulation/model.py, v2 register). Values confirmed by design-note A2 G3.2 load formula. Not re-scoped for v3 coverage.",
        v2_lineage="SUCCESSION_BASE_LOAD=0.10, SUCCESSION_CAPABILITY_GAP_FACTOR=0.05, SUCCESSION_GENERATION_GAP_FACTOR=0.03, SUCCESSION_OPACITY_FACTOR=0.05 (v2 model.py)",
        sensitivity_candidate="yes",
        proposed_range="proposal: scale each load factor +/- 50%",
        notes="Succession-cliff drawdown load factors imported unchanged from model.py; the gate G3.2 reference formula reproduces them.",
        file="", claim=[]))
    reg.append(R(
        name="succession_buffer_factors", value="PSI_BUFFER_K 0.5, TRANSFER_BUFFER_K 0.3, RESILIENCE_BUFFER_K 0.2",
        units="buffering coefficient", role="dynamics",
        used_in="stocks.transition_drawdown (from model.py); gate G3.2 buffer", cls="arbitrary",
        ev=[("simulation/v3/stocks.py", "SUCCESSION_PSI_BUFFER_K, SUCCESSION_TRANSFER_BUFFER_K,"),
            ("simulation/v3/gates.py", "buffering = .5 * stock + .3 * action[4] + .2 * action[5]")],
        evnote="EXTERNAL (simulation/model.py). Values confirmed by design-note A2 G3.2 buffer formula.",
        v2_lineage="SUCCESSION_PSI_BUFFER_K=0.5, SUCCESSION_TRANSFER_BUFFER_K=0.3, SUCCESSION_RESILIENCE_BUFFER_K=0.2 (v2 model.py)",
        sensitivity_candidate="yes",
        proposed_range="proposal: scale each buffer factor +/- 50%",
        notes="Buffering of the succession drawdown by institutional stock, transfer and resilience; the gate G3.2 reference formula reproduces them.",
        file="", claim=[]))
    reg.append(R(
        name="successor_capability_growth", value="1.5", units="capability ratio", role="decision",
        used_in="integration.V3Model default; review_yield min(5., capability*1.5); study.capabilities",
        cls="arbitrary",
        ev=[("simulation/v3/integration.py", "self.successor_capability = min(5., self.capability * 1.5)")],
        evnote="design note section 3: successor built at 1.5x incumbent capability (unchanged from v2.0). R2 sweeps successor capability on its own grid.",
        decided_by="design note section 3 (successor construction at 1.5x, unchanged from v2.0)",
        v2_lineage="successor_capability_growth_rate=1.5 (v2)",
        notes="Successor built at 1.5x incumbent capability, capped at 5.0.",
        file="simulation/v3/integration.py", claim=[("lit", 53, "1.5"), ("lit", 299, "1.5")]))

    # === admission / survival-first / risk ===
    reg.append(R(
        name="epsilon_surv", value="1e-3 (Fraction 1/1000)", units="extinction probability", role="decision",
        used_in="admission.chance_admitted; cohort.CohortBound.admitted; ProtectionPeriod.epsilon; gates EPSILON",
        cls="arbitrary",
        ev=[("simulation/v3/admission.py", "def chance_admitted(model_risk_upper_bounds, epsilon_surv=1e-3):"),
            ("simulation/v3/cohort.py", "def admitted(self, epsilon=Fraction(1, 1000)):")],
        evnote="D18 item 5: eps_surv=10^-3; design note section 4.",
        decided_by="D18 item 5 (eps_surv=10^-3); design note section 4",
        sensitivity_candidate="yes",
        proposed_range="proposal: {1e-2, 1e-3, 1e-4}",
        notes="Cohort admission tolerance on P(extinction within the window). Owns the gates EPSILON=.001 mirror.",
        file="simulation/v3/admission.py",
        claim=[("base", "epsilon_surv.arg"), ("base", "epsilon.arg"),
               ("litf", "simulation/v3/gates.py", 28, "0.001")]))
    reg.append(R(
        name="no_write_off_gamma", value="0.05", units="relative extinction-probability tolerance", role="decision",
        used_in="admission.no_write_off; plans.compare_plans; integration._eligible log1p(.05)",
        cls="arbitrary",
        ev=[("simulation/v3/admission.py", "def no_write_off(extinction_probabilities, pointwise_admissible, gamma=0.05):"),
            ("simulation/v3/integration.py", "return logs <= logs.min() + math.log1p(.05), logs, True")],
        evnote="R7, D18 item 9: no-write-off tolerance gamma=0.05, applied as log1p(.05).",
        decided_by="R7, D18 item 9 (no-write-off tolerance gamma=0.05)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {0.02, 0.05, 0.10}",
        notes="R7 relative tolerance for the survival-first eligibility mask.",
        file="simulation/v3/admission.py",
        claim=[("base", "gamma.arg"), ("lit", 203, "0.05"), ("lit", 203, ".05")]))
    reg.append(R(
        name="family_alpha_total", value="0.01", units="confidence budget alpha", role="decision",
        used_in="admission.family_alpha total=0.01", cls="arbitrary",
        ev=[("simulation/v3/admission.py", "def family_alpha(check_count, total=0.01):")],
        evnote="D18 item 6: alpha=0.01 ledger stays unspent (admission is deterministic).",
        decided_by="D18 item 6",
        notes="Statistical confidence budget for the tail standard; the ledger stays unspent. Not a dynamics sensitivity target.",
        file="simulation/v3/admission.py", claim=[("base", "total.arg")]))
    reg.append(R(
        name="cohort_window_horizon", value="50", units="steps (H)", role="decision",
        used_in="cohort.life_table/cohort_bound/initial_law_bound; integration lookahead",
        cls="arbitrary",
        ev=[("simulation/v3/cohort.py", "def life_table(max_horizon=50):"),
            ("simulation/v3/integration.py", "self.period = ProtectionPeriod(self.time, self.time + 25, self.time + 50,")],
        evnote="D18 item 5 (H via T_P/H split R6); design note section 3: 50-step lookahead. Results cannot speak beyond 50 steps.",
        decided_by="D18 item 5, R6; design note section 3",
        notes="Cohort certificate lookahead window (50 steps).",
        file="simulation/v3/cohort.py", claim=[("base", "max_horizon.arg"), ("base", "horizon.arg")]))
    reg.append(R(
        name="protection_period_T_P", value="25", units="steps (T_P)", role="decision",
        used_in="integration._open_period; ProtectionPeriod.protection_end; Epoch deadline",
        cls="arbitrary",
        ev=[("simulation/v3/integration.py", "self.period = ProtectionPeriod(self.time, self.time + 25, self.time + 50,")],
        evnote="D18 item 5, R6: T_P=25, H=25 split; lookahead 50 from each period start.",
        decided_by="D18 item 5, R6 (T_P=25)",
        sensitivity_candidate="yes",
        proposed_range="proposal: {10, 25, 50} steps",
        notes="Protection-period length: a new cohort ledger opens every 25 steps.",
        file="simulation/v3/integration.py", claim=[("lit", 133, "25")]))
    reg.append(R(
        name="initial_law_entrants", value="200", units="agents", role="decision",
        used_in="cohort.initial_law_bound; integration/context/study/pilot defaults n_agents=200",
        cls="arbitrary",
        ev=[("simulation/v3/cohort.py", "def initial_law_bound(n_agents=200, horizon=50):")],
        evnote="design note section 3: the in-law cohort certificate uses 200 independent entrants (bound 5.209e-7). Also the default n_agents.",
        decided_by="design note section 3 (200 entrants)",
        v2_lineage="n_agents=200 default population",
        notes="Default entrant population. Owns the cohort default plus the context.population and engine.measurements_and_flow n_ref default occurrences.",
        file="simulation/v3/cohort.py",
        claim=[("base", "n_agents.arg"),
               ("litf", "simulation/v3/context.py", 42, "200"), ("litf", "simulation/v3/engine.py", 262, "200")]))

    # === policy class ===
    reg.append(R(
        name="population_cuts", value="(0.05, 0.125, 0.25, 0.5, 1.0)", units="N/K ratio", role="estimation",
        used_in="policies.POPULATION_CUTS; engine.summary_bins; Summary.bins", cls="arbitrary",
        ev=[("simulation/v3/policies.py", "POPULATION_CUTS = (0.05, 0.125, 0.25, 0.5, 1.0)")],
        evnote="R6: per-rule continuation table over the rule summary bins.",
        decided_by="R6",
        sensitivity_candidate="yes",
        proposed_range="proposal: coarsen/refine the N/K bin edges",
        notes="Population-ratio summary-bin cut points for the rollout continuation tables and the rule stress trigger.",
        file="simulation/v3/policies.py", claim=[("base", "POPULATION_CUTS")]))
    reg.append(R(
        name="welfare_cuts", value="(0.5, 0.65, 0.8)", units="mean welfare", role="estimation",
        used_in="policies.WELFARE_CUTS; engine.summary_bins; Summary.bins", cls="arbitrary",
        ev=[("simulation/v3/policies.py", "WELFARE_CUTS = (0.5, 0.65, 0.8)")],
        decided_by="R6",
        sensitivity_candidate="yes",
        proposed_range="proposal: adjust the welfare bin edges",
        notes="Mean-welfare summary-bin cut points.",
        file="simulation/v3/policies.py", claim=[("base", "WELFARE_CUTS")]))
    reg.append(R(
        name="stock_cuts", value="(0.25, 0.5, 0.75)", units="stock level", role="estimation",
        used_in="policies.STOCK_CUTS; engine.summary_bins; Summary.bins", cls="arbitrary",
        ev=[("simulation/v3/policies.py", "STOCK_CUTS = (0.25, 0.5, 0.75)")],
        decided_by="R6",
        sensitivity_candidate="yes",
        proposed_range="proposal: adjust the stock bin edges",
        notes="Per-stock summary-bin cut points.",
        file="simulation/v3/policies.py", claim=[("base", "STOCK_CUTS")]))
    reg.append(R(
        name="balanced_share", value="1/6", units="allocation share", role="decision",
        used_in="policies.BALANCED_SHARE; Rule.allocation; engine welfare floor; admission shares>=1/6; integration",
        cls="derived",
        ev=[("simulation/v3/policies.py", "BALANCED_SHARE = 1 / 6"),
            ("simulation/v3/engine.py", "actions[self.balanced[ix]] = 1 / 6")],
        evnote="v2 equal share of six channels; also the pointwise welfare floor. The balanced rule's allocation is set inline to 1 / 6 at engine.py:111.",
        v2_lineage="BRIDGE_BALANCED_SHARE = 1/6 (v2 equal share)",
        notes="Equal share across the six channels; also the welfare floor. Owns the named constant and the balanced-allocation assignment engine.py:111. Other inline 1 / 6 uses are welfare-floor comparisons whose numerator 1 (identity) and denominator 6 (the channel count) remain excluded as structural.",
        file="simulation/v3/policies.py",
        claim=[("base", "BALANCED_SHARE"),
               ("litf", "simulation/v3/engine.py", 111, "1"), ("litf", "simulation/v3/engine.py", 111, "6")]))
    reg.append(R(
        name="rule_welfare_tiers", value="(1/6, 0.25, 0.4, 0.6)", units="welfare allocation share", role="decision",
        used_in="policies.Rule.allocation; engine.RuleBatch.welfare", cls="arbitrary",
        ev=[("simulation/v3/policies.py", "welfare = (BALANCED_SHARE, 0.25, 0.4, 0.6)[self.welfare_tier]"),
            ("simulation/v3/engine.py", "self.welfare = np.array([(1 / 6, .25, .4, .6)[r.welfare_tier] for r in rules])")],
        evnote="R5/R11 (25-rule class). Base bio-welfare share per welfare tier; mirrored in engine.RuleBatch.",
        decided_by="R5/R11",
        sensitivity_candidate="yes",
        proposed_range="proposal: shift the base welfare-tier shares",
        notes="Base bio-welfare allocation share per rule welfare tier (before stress gain).",
        file="simulation/v3/policies.py",
        claim=[("lit", 47, "0.25"), ("lit", 47, "0.4"), ("lit", 47, "0.6"),
               ("litf", "simulation/v3/engine.py", 98, "0.25"), ("litf", "simulation/v3/engine.py", 98, "0.4"),
               ("litf", "simulation/v3/engine.py", 98, "0.6")]))
    reg.append(R(
        name="rule_stress_gain", value="(0.25, 0.5, 0.75, 1.0)", units="fraction of remaining welfare", role="decision",
        used_in="policies.Rule.allocation gain; engine.RuleBatch.gain", cls="arbitrary",
        ev=[("simulation/v3/policies.py", "welfare += (1 - welfare) * (0.25, 0.5, 0.75, 1.0)[self.gain]"),
            ("simulation/v3/engine.py", "self.gain = np.array([(.25, .5, .75, 1)[r.gain] for r in rules])")],
        evnote="R5/R11; the frozen execution class uses only gain index 3 (full welfare under stress).",
        decided_by="R5/R11",
        sensitivity_candidate="yes",
        proposed_range="proposal: the frozen 25-rule class uses gain=3 (=1.0); a screen could vary this",
        notes="Stress-triggered welfare top-up fraction. Mirrored in engine.RuleBatch.",
        file="simulation/v3/policies.py",
        claim=[("lit", 50, "0.25"), ("lit", 50, "0.5"), ("lit", 50, "0.75"), ("lit", 50, "1.0"),
               ("litf", "simulation/v3/engine.py", 100, "0.25"), ("litf", "simulation/v3/engine.py", 100, "0.5"),
               ("litf", "simulation/v3/engine.py", 100, "0.75"), ("litf", "simulation/v3/engine.py", 100, "1")]))
    reg.append(R(
        name="rule_profile_shares", value="uniform 0.2; focal 0.6 / 0.1", units="non-welfare channel share", role="decision",
        used_in="policies.Rule.allocation proportions; engine.RuleBatch.profiles", cls="arbitrary",
        ev=[("simulation/v3/policies.py", "proportions = [0.2] * 5 if self.profile == 0 else [0.6 if i == self.profile - 1 else 0.1 for i in range(5)]"),
            ("simulation/v3/engine.py", "self.profiles = np.array([[.2] * 5 if r.profile == 0 else [.6 if i == r.profile - 1 else .1 for i in range(5)] for r in rules])")],
        evnote="R5/R11. Uniform (0.2 each) or one focal channel at 0.6 with 0.1 elsewhere; mirrored in engine.RuleBatch.",
        decided_by="R5/R11",
        sensitivity_candidate="yes",
        proposed_range="proposal: vary the focal emphasis 0.6 and off-focus 0.1",
        notes="Distribution of the non-welfare remainder across the five other channels.",
        file="simulation/v3/policies.py",
        claim=[("lit", 53, "0.2"), ("lit", 53, "0.6"), ("lit", 53, "0.1"),
               ("litf", "simulation/v3/engine.py", 102, "0.2"), ("litf", "simulation/v3/engine.py", 102, "0.6"),
               ("litf", "simulation/v3/engine.py", 102, "0.1")]))
    reg.append(R(
        name="defense_action_constants", value="c_protective 0.3, c_suppressive 0.1", units="defense control", role="dynamics",
        used_in="policies.Rule.allocation action.update(...)", cls="arbitrary",
        ev=[("simulation/v3/policies.py", "action.update(c_protective=0.3, c_suppressive=0.1)")],
        evnote="Legacy defense-control fields on every action dict; the B1 kernel forbids attacks/defenses.",
        v2_lineage="c_protective / c_suppressive defense controls (v2)",
        confidence="medium",
        needs_operator_decision="yes",
        notes="Legacy defense-control fields attached to every action dict. The B1 kernel forbids attacks/defenses (integration raises), so these appear inert on the rerun path; operator should confirm they do not enter v3 dynamics before deciding sensitivity scope.",
        file="simulation/v3/policies.py", claim=[("lit", 57, "0.3"), ("lit", 57, "0.1")]))
    reg.append(R(
        name="policy_class_grid", value="welfare_tier 4, profile 6, trigger 3, gain 4 (289 rules)", units="rule counts", role="decision",
        used_in="policies.policy_class; Rule.__post_init__ ranges", cls="arbitrary",
        ev=[("simulation/v3/policies.py", "for w, p, t, g in product(range(4), range(6), range(3), range(4))")],
        evnote="R5/R11: 289-rule class reduced to 25.",
        decided_by="R5/R11",
        notes="Cardinalities of the full 289-rule stationary class; the runs use the 25-rule execution subclass.",
        file="simulation/v3/policies.py", claim=[("lit", 64, "4"), ("lit", 64, "6"), ("lit", 64, "3")]))
    reg.append(R(
        name="execution_class_freeze", value="trigger==1, gain==3 (plus balanced) -> 25 rules", units="rule selector", role="decision",
        used_in="policies.execution_policy_class", cls="arbitrary",
        ev=[("simulation/v3/policies.py", "return tuple(r for r in policy_class() if r.balanced or (r.trigger == 1 and r.gain == 3))")],
        evnote="R5, R11: 25 rules frozen 2026-09-27 before any table estimate.",
        decided_by="R5, R11",
        notes="The frozen 25-rule evaluation class Pi: every welfare tier and residual profile, fixed trigger=1 and gain=3, plus the balanced witness.",
        file="simulation/v3/policies.py", claim=[("lit", 75, "1"), ("lit", 75, "3")]))

    # === calibration protocol ===
    reg.append(R(
        name="sigma0_variance_factor", value="0.1 (of per-direction variance)", units="factor", role="estimation",
        used_in="calibration.freeze; context.build fixture", cls="arbitrary",
        ev=[("simulation/v3/calibration.py", "sigma = .1 * total_variance / 10"),
            ("simulation/v3/context.py", "\"sigma_squared\": .1 * H_N_V_REF / 10,")],
        evnote="D9, R3: sigma0^2 = 0.1 x V_ref/d (d=10). The resulting sigma_squared is calibrated.",
        decided_by="D9, R3",
        sensitivity_candidate="yes",
        proposed_range="proposal: one decade either side (design note: sensitivity on sigma0^2 at x0.1 and x10)",
        notes="Declared factor setting sigma0^2 to one tenth of the per-direction baseline variance. The fixture path uses the same factor with H_N_V_REF.",
        file="simulation/v3/calibration.py", claim=[("lit", 63, "0.1"), ("litf", "simulation/v3/context.py", 22, "0.1")]))
    reg.append(R(
        name="epsilon_calibration_factor", value="0.01 (1% of protected level)", units="factor", role="estimation",
        used_in="calibration.freeze epsilon_n/e/l", cls="arbitrary",
        ev=[("simulation/v3/calibration.py", "\"epsilon_n\": .01 * reliable[0], \"epsilon_e\": .01 * reliable[1], \"epsilon_l\": .01 * reliable[2],")],
        evnote="design note section 5: each epsilon at 1% of its reliable protected level. The resulting epsilons are calibrated.",
        decided_by="design note section 5; R3",
        sensitivity_candidate="yes",
        proposed_range="proposal: the epsilons are floors; a screen could vary the 1% convention",
        notes="Declared convention: each flow floor epsilon = 1% of its reliable protected level.",
        file="simulation/v3/calibration.py", claim=[("lit", 94, "0.01")]))
    reg.append(R(
        name="reliability_se_multiplier", value="4 (four standard errors)", units="standard errors", role="estimation",
        used_in="calibration.freeze lower = means - 4*se", cls="arbitrary",
        ev=[("simulation/v3/calibration.py", "lower = means - 4 * se")],
        evnote="design note section 5 reliability method: four-standard-error lower block means.",
        decided_by="design note section 5",
        notes="Conservative reliability margin (4 SE) for the calibration lower measurement bound.",
        file="simulation/v3/calibration.py", claim=[("lit", 85, "4")]))
    reg.append(R(
        name="calibration_block_count", value="10", units="blocks", role="estimation",
        used_in="calibration.freeze block_count", cls="arbitrary",
        ev=[("simulation/v3/calibration.py", "block_count = min(10, measurements.shape[1])")],
        confidence="medium",
        notes="Number of trajectory blocks for the block-mean reliability estimate (calibration only).",
        file="simulation/v3/calibration.py", claim=[("lit", 81, "10")]))
    reg.append(R(
        name="calibration_steps", value="500", units="steps", role="run-setting",
        used_in="calibration.run_seed/freeze/validate; V3Model horizon; design note", cls="arbitrary",
        ev=[("simulation/v3/calibration.py", "500-step balanced trajectories and a verified pre-registration pin.")],
        evnote="design note sections 3, 5: horizon 500 steps; horizon sensitivity uses 1000 steps.",
        decided_by="design note sections 3, 5",
        notes="Registered horizon: 500 steps, for calibration and reruns.",
        file="simulation/v3/calibration.py", claim=[("valin", 500, ("simulation/v3/calibration.py",))]))
    reg.append(R(
        name="calibration_trajectories", value="50", units="seeds/trajectories", role="run-setting",
        used_in="calibration.freeze registered check; study/pilot", cls="arbitrary",
        ev=[("simulation/v3/calibration.py", "Production requires 50 disjoint-tag")],
        evnote="design note section 5: 50 seeds and 500 steps.",
        decided_by="design note section 5",
        notes="Independent balanced honest-baseline trajectories the registered calibration requires.",
        file="simulation/v3/calibration.py", claim=[("lit", 49, "50")]))
    reg.append(R(
        name="H_N_V_REF", value="internal simulated honest-baseline novelty statistic", units="bits", role="estimation",
        used_in="context.build fixture sigma (imported from metrics.py)", cls="calibrated",
        ev=[("simulation/v3/context.py", "from metrics import H_N_V_REF")],
        evnote="EXTERNAL (simulation/metrics.py). Frozen internal honest-baseline novelty variance reference. v2 register class calibrated (a measurement of simulated behavior, not external); leads' explicit calibrated override. Used only for the B1 fixture default; the registered path uses the calibrated sigma_squared.",
        v2_lineage="H_N_V_REF (v2 metrics.py; v2 register class calibrated)",
        notes="Classified calibrated per the v2 register and the leads' override.",
        file="", claim=[]))

    # === frozen calibration file values ===
    reg.append(R(
        name="calibrated_epsilon_n", value="0.16136550941334515", units="novelty flow floor", role="objective",
        used_in="v3_rerun_calibration.json values.epsilon_n -> FlowParameters.epsilon_n", cls="calibrated",
        ev=[("simulation/v3/calibration.py", "\"epsilon_n\": .01 * reliable[0], \"epsilon_e\": .01 * reliable[1], \"epsilon_l\": .01 * reliable[2],")],
        evnote="Frozen value epsilon_n=0.16136550941334515 in v3_rerun_calibration.json (SHA256 bf0f7c3f...); 1% of the reliable protected novelty level.",
        decided_by="calibration protocol (design note section 5); frozen SHA256 bf0f7c3f...",
        notes="Config value produced by calibration.freeze; carried for provenance.",
        file="", claim=[]))
    reg.append(R(
        name="calibrated_epsilon_e", value="0.0034075936979955646", units="execution flow floor", role="objective",
        used_in="v3_rerun_calibration.json values.epsilon_e -> FlowParameters.epsilon_e", cls="calibrated",
        ev=[("simulation/v3/calibration.py", "\"epsilon_n\": .01 * reliable[0], \"epsilon_e\": .01 * reliable[1], \"epsilon_l\": .01 * reliable[2],")],
        evnote="Frozen value epsilon_e=0.0034075936979955646 in v3_rerun_calibration.json (SHA256 bf0f7c3f...).",
        decided_by="calibration protocol; frozen SHA256 bf0f7c3f...",
        notes="Frozen calibrated execution floor.",
        file="", claim=[]))
    reg.append(R(
        name="calibrated_epsilon_l", value="0.001412790614729507", units="lineage flow floor", role="objective",
        used_in="v3_rerun_calibration.json values.epsilon_l -> FlowParameters.epsilon_l", cls="calibrated",
        ev=[("simulation/v3/calibration.py", "# Use the unclipped bandwidth response as a lower observable for L.")],
        evnote="Frozen value epsilon_l=0.001412790614729507 in v3_rerun_calibration.json (SHA256 bf0f7c3f...); from the unclipped bandwidth lower observable.",
        decided_by="calibration protocol; frozen SHA256 bf0f7c3f...",
        notes="Frozen calibrated lineage floor.",
        file="", claim=[]))
    reg.append(R(
        name="calibrated_sigma_squared", value="0.0011729260815883749", units="novelty resolution sigma0^2", role="dynamics",
        used_in="v3_rerun_calibration.json values.sigma_squared -> NoveltyProtocol.sigma_squared", cls="calibrated",
        ev=[("simulation/v3/calibration.py", "sigma = .1 * total_variance / 10")],
        evnote="Frozen value sigma_squared=0.0011729260815883749 = 0.1*V_ref_total/10 (V_ref_total=0.11729...) in v3_rerun_calibration.json (SHA256 bf0f7c3f...).",
        decided_by="D9, R3; frozen SHA256 bf0f7c3f...",
        notes="Frozen calibrated novelty resolution.",
        file="", claim=[]))
    reg.append(R(
        name="calibrated_n_ref", value="317.73672", units="reference population", role="objective",
        used_in="v3_rerun_calibration.json values.n_ref -> lineage N/N_ref term", cls="calibrated",
        ev=[("simulation/v3/calibration.py", "n_ref = max(1., float(population[:, population.shape[1] // 2:].mean()))")],
        evnote="Frozen value n_ref=317.73672 in v3_rerun_calibration.json; mean of the second-half baseline populations. Supersedes the source default n_ref=200 on the registered path.",
        decided_by="calibration protocol (design note section 5)",
        v2_lineage="population scaling 200 (v2)",
        notes="Frozen calibrated reference population.",
        file="", claim=[]))
    reg.append(R(
        name="calibrated_center", value="10-vector near 0 (e.g. 8.26e-05, ...)", units="novelty center", role="dynamics",
        used_in="v3_rerun_calibration.json values.center -> NoveltyProtocol.center", cls="calibrated",
        ev=[("simulation/v3/calibration.py", "center = np.sum([r[\"sample_sum\"] for r in records], axis=0) / count")],
        evnote="Frozen value center=[8.26e-05, 1.91e-04, ...] (10-vector) in v3_rerun_calibration.json; pooled baseline sample mean. Fixture default is the zero vector.",
        decided_by="R3 (H_N fixed center from calibration)",
        notes="Frozen calibrated fixed novelty center.",
        file="", claim=[]))

    # === gate constants ===
    reg.append(R(
        name="gate_equality_tolerances", value="atol 1e-10, rtol 1e-8", units="tolerance", role="gate",
        used_in="gates.FORMULA_ATOL/FORMULA_RTOL; G1.x/G3.x/G4.x equality checks", cls="arbitrary",
        ev=[("simulation/v3/gates.py", "FORMULA_ATOL, FORMULA_RTOL, DERIVATIVE_RTOL = 1e-10, 1e-8, 1e-5")],
        evnote="design note A2: absolute tolerance 1e-10 and relative tolerance 1e-8.",
        decided_by="A2 (D21 gate arithmetic tolerances)",
        notes="Absolute/relative float-equality tolerances for the gate reference-arithmetic checks.",
        file="simulation/v3/gates.py", claim=[("valin", 1e-10, ("simulation/v3/gates.py",)), ("valin", 1e-8, ("simulation/v3/gates.py",))]))
    reg.append(R(
        name="gate_derivative_tolerance", value="rtol 1e-5, step h=value*1e-4", units="tolerance / step", role="gate",
        used_in="gates.py G1.1 central-difference marginal check", cls="arbitrary",
        ev=[("simulation/v3/gates.py", "FORMULA_ATOL, FORMULA_RTOL, DERIVATIVE_RTOL = 1e-10, 1e-8, 1e-5")],
        evnote="design note A2: G1.1 uses h = 1e-4 times the varied coordinate, relative derivative tolerance 1e-5.",
        decided_by="A2",
        notes="Finite-difference relative tolerance (1e-5) and relative step (1e-4) for the G1.1 derivative check.",
        file="simulation/v3/gates.py", claim=[("valin", 1e-5, ("simulation/v3/gates.py",)), ("valin", 0.0001, ("simulation/v3/gates.py",))]))
    reg.append(R(
        name="gate_bootstrap", value="resamples 2000, seed 20260928", units="resamples / seed", role="gate",
        used_in="gates.py G2.2 cliff bootstrap support", cls="arbitrary",
        ev=[("simulation/v3/gates.py", "BOOTSTRAPS, BOOTSTRAP_SEED = 2000, 20260928")],
        evnote="design note A2: 2,000 NumPy default_rng bootstrap resamples, seed 20260928.",
        decided_by="A2 (D21/G2.2)",
        notes="Seed-bootstrap resample count and RNG seed for the G2.2 cap* cliff support statistic.",
        file="simulation/v3/gates.py", claim=[("valin", 2000, ("simulation/v3/gates.py",)), ("valin", 20260928, ("simulation/v3/gates.py",))]))
    reg.append(R(
        name="gate_cliff_thresholds", value="fire-rate 0.5, bootstrap support 0.90, separation 2 SE", units="fire rate / support / SE", role="gate",
        used_in="gates.py G2.2 (cap* 0.5, support 0.90), G4.2 (2 SE)", cls="arbitrary",
        ev=[("simulation/v3/gates.py", "\"bootstrap_support\": .9, \"fire_threshold\": .5, \"separation_standard_errors\": 2,")],
        evnote="design note A2/D24: cap* at fire rate 0.5; each adjacent strict decrease needs 0.90 bootstrap support; G4.2 needs a 2 standard-error separation.",
        decided_by="A2, D24 (G2.2/G4.2 cliff test)",
        notes="The succession-cliff decision thresholds. BLIND: gate thresholds, not measured fire rates.",
        file="simulation/v3/gates.py",
        claim=[("litf", "simulation/v3/gates.py", 56, "0.9"), ("litf", "simulation/v3/gates.py", 56, "0.5"),
               ("litf", "simulation/v3/gates.py", 56, "2"),
               ("litf", "simulation/v3/gates.py", 479, "0.5"), ("litf", "simulation/v3/gates.py", 480, "0.5"),
               ("litf", "simulation/v3/gates.py", 488, "0.9")]))
    reg.append(R(
        name="gate_review_sample_target", value="200 (100 fired + 100 not fired)", units="reviews", role="gate",
        used_in="gates.py G3.1 sampled reviews; G3.2 subset", cls="arbitrary",
        ev=[("simulation/v3/gates.py", "REVIEW_COUNT, STEP_COUNT = 200, 10000")],
        evnote="design note A2: reviews target 100 fired and 100 not fired; fewer than 200 total fails.",
        decided_by="A2 (D21 frozen sampling)",
        notes="Target size of the frozen G3.1 review sample, stratified 100 fired / 100 not fired.",
        file="simulation/v3/gates.py", claim=[("litf", "simulation/v3/gates.py", 25, "200")]))
    reg.append(R(
        name="gate_step_sample_target", value="10000", units="living-start steps", role="gate",
        used_in="gates.py G4.1 theta sample", cls="arbitrary",
        ev=[("simulation/v3/gates.py", "REVIEW_COUNT, STEP_COUNT = 200, 10000")],
        evnote="design note A2: G4.1 on 10,000 hash-selected living-start R2 steps.",
        decided_by="A2 (G4.1)",
        notes="Target number of hash-selected living-start R2 steps for the G4.1 Theta check.",
        file="simulation/v3/gates.py", claim=[("litf", "simulation/v3/gates.py", 25, "10000")]))
    reg.append(R(
        name="gate_zero_failure_confidence", value="0.05 (95%)", units="confidence", role="gate",
        used_in="gates.py zero-failure sample bound 1 - 0.05^(1/n)", cls="arbitrary",
        ev=[("simulation/v3/gates.py", "return -math.expm1(math.log(.05) / n) if n > 0 else None")],
        evnote="design note A2: reports 1 - 0.05^(1/n), the nominal 95 percent bound.",
        decided_by="A2",
        notes="95% confidence level in the nominal zero-failure sample bound reported for passed gate samples.",
        file="simulation/v3/gates.py", claim=[("litf", "simulation/v3/gates.py", 67, "0.05")]))
    reg.append(R(
        name="gate_g1_fixed_scenarios", value="G1.1-G1.5 and G3.1 fixed coordinate scenarios", units="test coordinates", role="gate",
        used_in="gates.py before-check fixed scenarios", cls="arbitrary",
        ev=[("simulation/v3/gates.py", "ALPHAS = (.5, .75, 1., 1.25, 1.5)")],
        evnote="design note A2 (D21) lists every fixed before-check scenario grid (G1.1 points, G1.2/G1.3 grids, G1.4 horizons/rewards, G1.5 products, G3.1 value triples). Individual coordinates stay in the excluded gate-scenario category; this row records the family. The gate ALPHAS/CAPABILITIES/R2_RR reference grids equal the registered run grids (see the R1/R2 rows).",
        decided_by="A2 (D21 before-check scenarios)",
        confidence="medium",
        notes="Family of fixed test-coordinate scenarios the before-checks probe; decision-fixed test inputs, not model parameters.",
        file="", claim=[]))

    # === registered run design ===
    reg.append(R(
        name="R1_reproduction_rate_grid", value="(0.055,0.056,0.057,0.058,0.059,0.060,0.062,0.064,0.066)", units="reproduction rate", role="run-setting",
        used_in="study.R1_RR; gates loader registered-grid check", cls="arbitrary",
        ev=[("simulation/v3/study.py", "R1_RR = (.055, .056, .057, .058, .059, .060, .062, .064, .066)")],
        evnote="design note section 6: R1 phase-boundary grid, v2.0 grid minus phi.",
        decided_by="design note section 6",
        notes="Pre-registered R1 phase-boundary reproduction-rate grid. BLIND: grid coordinates, not measured survival values.",
        file="simulation/v3/study.py", claim=[("base", "R1_RR")]))
    reg.append(R(
        name="refinement_reproduction_rate_grid", value="(0.061, 0.063, 0.065)", units="reproduction rate", role="run-setting",
        used_in="study.REFINEMENT_RR; gates loader", cls="arbitrary",
        ev=[("simulation/v3/study.py", "REFINEMENT_RR = (.061, .063, .065)")],
        evnote="design note section 6: refinement grid, same seeds per cell.",
        decided_by="design note section 6",
        notes="Pre-registered R1 refinement grid.",
        file="simulation/v3/study.py", claim=[("base", "REFINEMENT_RR")]))
    reg.append(R(
        name="R2_reproduction_rate_grid", value="(0.057, 0.060, 0.064, 0.070)", units="reproduction rate", role="run-setting",
        used_in="study.R2_RR; gates loader; offline/unpublished sensitivity subset overlap", cls="arbitrary",
        ev=[("simulation/v3/study.py", "R2_RR = (.057, .060, .064, .070)")],
        evnote="design note section 6: R2 cliff grid.",
        decided_by="design note section 6",
        notes="Pre-registered R2 succession-cliff reproduction-rate grid.",
        file="simulation/v3/study.py", claim=[("base", "R2_RR")]))
    reg.append(R(
        name="alpha_grid", value="(0.5, 0.75, 1.0, 1.25, 1.5)", units="alpha", role="run-setting",
        used_in="study.R1_ALPHA/R2_ALPHA; integration domain check; gates.ALPHAS", cls="arbitrary",
        ev=[("simulation/v3/study.py", "R2_ALPHA = (.5, .75, 1., 1.25, 1.5)"),
            ("simulation/v3/integration.py", "alpha not in (.5, .75, 1., 1.25, 1.5)")],
        evnote="design note section 6: alpha grid (v2.0 grid). R1 uses the subset {0.5,1.0,1.5} (R1_ALPHA); R2 uses all five.",
        decided_by="design note section 6",
        v2_lineage="ALPHA_DEFAULT / alpha sweep (v2)",
        notes="Admissible alpha values (frontier penalty strength). Swept by the grids, so not itself a sensitivity target.",
        file="simulation/v3/study.py", claim=[("base", "R2_ALPHA"), ("base", "R1_ALPHA"), ("basef", "simulation/v3/gates.py", "ALPHAS")]))
    reg.append(R(
        name="R2_capability_grid", value="(1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0)", units="successor capability", role="run-setting",
        used_in="study.R2_CAP; gates.CAPABILITIES; G2.2/G4.2 cliff", cls="arbitrary",
        ev=[("simulation/v3/study.py", "R2_CAP = (1.2, 1.5, 2., 2.5, 3., 4., 5.)"),
            ("simulation/v3/gates.py", "CAPABILITIES = (1.2, 1.5, 2., 2.5, 3., 4., 5.)")],
        evnote="design note section 6: R2 successor-capability grid, ceiling 5.0.",
        decided_by="design note section 6",
        notes="Pre-registered R2 successor-capability grid.",
        file="simulation/v3/study.py", claim=[("base", "R2_CAP"), ("basef", "simulation/v3/gates.py", "CAPABILITIES")]))
    reg.append(R(
        name="seeds_per_cell", value="R1/refinement 400, R2 75", units="seeds", role="run-setting",
        used_in="study.rerun_jobs seed counts; design note section 6", cls="arbitrary",
        ev=[("simulation/v3/study.py", "(\"R1\", R1_RR, R1_ALPHA, (1.5,), 400),"),
            ("simulation/v3/study.py", "(\"R2\", R2_RR, R2_ALPHA, R2_CAP, 75),")],
        evnote="design note section 6: R1 keeps 1,200 per rr as 3 alpha x 400 seeds; R2 uses 75 seeds per cell.",
        decided_by="design note section 6",
        notes="Pre-registered seeds per cell: 400 for R1/refinement, 75 for R2.",
        file="simulation/v3/study.py", claim=[("valin", 400, ("simulation/v3/study.py",)), ("valin", 75, ("simulation/v3/study.py",))]))
    reg.append(R(
        name="survival_threshold", value="30", units="agents (final population)", role="gate",
        used_in="production_runner survived_threshold_30; design note", cls="arbitrary",
        ev=[("simulation/v3/production_runner.py", "\"survived_threshold_30\": model.population >= 30,")],
        evnote="design note section 3: final population of at least 30 at the horizon (unchanged from v2.0).",
        decided_by="design note section 3",
        v2_lineage="survival threshold: final population >= 30 (v2.0)",
        notes="Survival criterion: a run survives if its final population is at least 30 at the 500-step horizon. BLIND: the survival-rule threshold, not a measured survival rate.",
        file="simulation/v3/production_runner.py", claim=[("litf", "simulation/v3/production_runner.py", 211, "30")]))
    reg.append(R(
        name="rerun_horizon_steps", value="500", units="steps", role="run-setting",
        used_in="production_runner steps default; gates loader registered horizon; design note", cls="arbitrary",
        ev=[("simulation/v3/production_runner.py", "records = model.run(config.get(\"steps\", 500))")],
        evnote="design note section 3: horizon 500 steps; horizon sensitivity uses 1000 steps.",
        decided_by="design note section 3",
        notes="Registered rerun horizon (500 steps).",
        file="simulation/v3/production_runner.py", claim=[("litf", "simulation/v3/production_runner.py", 197, "500")]))

    # === offline table estimation ===
    reg.append(R(
        name="primary_estimator_settings", value="6 groups, 64 plain runs/group, 256 FV particles/group, burn-in 1024, measure 2048", units="counts / steps", role="estimation",
        used_in="offline_estimator.PRIMARY; table_validation_a4 anchor; A4 replacement family", cls="arbitrary",
        ev=[("simulation/v3/offline_estimator.py", "PRIMARY = {\"groups\": 6, \"runs_per_group\": 64, \"particles\": 256, \"burn\": 1024, \"measure\": 2048}")],
        evnote="design note A1: six groups, 64 plain runs per group, 256 FV particles per group, burn-in 1,024 and 2,048 measurement steps.",
        decided_by="A1 (replacement family primary setting)",
        notes="Offline continuation/Lambda_F estimator primary sampling. Sensitivity jobs double population or length.",
        file="simulation/v3/offline_estimator.py", claim=[("base", "PRIMARY")]))
    reg.append(R(
        name="estimator_group_split", value="6 groups, last 2 held out", units="groups", role="estimation",
        used_in="continuation.fit_transitions train/holdout split", cls="derived",
        ev=[("simulation/v3/continuation.py", "train = group_grid < max(1, int(np.max(groups)) - 1)")],
        evnote="R13. Docstring: the last two of six groups are held out.",
        decided_by="R13",
        notes="Train/held-out split: with 6 groups the last two are held out for the empirical residual.",
        file="simulation/v3/continuation.py", claim=[("lit", 17, "1")]))
    reg.append(R(
        name="min_training_visits", value="4", units="visits", role="estimation",
        used_in="continuation.fit_transitions min_visits; continuation_validation.MIN_VISITS", cls="arbitrary",
        ev=[("simulation/v3/continuation.py", "min_visits=4"),
            ("simulation/v3/continuation_validation.py", "MIN_VISITS = 4")],
        evnote="design note A4: C0 published only with at least four fitting visits, the committed minimum.",
        decided_by="A4 (committed minimum fitting visits)",
        notes="A continuation bin (and the A4 plain C0 cell) is published only with at least 4 training/fitting visits.",
        file="simulation/v3/continuation.py", claim=[("base", "min_visits.arg"), ("basef", "simulation/v3/continuation_validation.py", "MIN_VISITS")]))
    reg.append(R(
        name="bellman_fixed_point", value="max 2500 iterations, tolerance 1e-9", units="iterations / tolerance", role="estimation",
        used_in="continuation.fit_transitions value iteration", cls="arbitrary",
        ev=[("simulation/v3/continuation.py", "for iteration in range(2500):"),
            ("simulation/v3/continuation.py", "if np.max(abs(new - value), initial=0) < 1e-9:")],
        notes="Sparse Bellman fixed-point solve: convergence tolerance 1e-9, capped at 2500 sweeps.",
        file="simulation/v3/continuation.py", claim=[("lit", 37, "2500"), ("lit", 40, "1e-09")]))
    reg.append(R(
        name="bonferroni_family", value="alpha 0.05 over M=13750 primary rows", units="alpha / rows", role="estimation",
        used_in="offline_estimator Bonferroni half-width; A4/A1 primary row family", cls="arbitrary",
        ev=[("simulation/v3/offline_estimator.py", "allocation = .05 / 13750")],
        evnote="design note A4: the Bonferroni allocation over 13,750 primary rows. 13,750 derived from the table design.",
        decided_by="A1, A4",
        notes="Family-wise alpha 0.05 split Bonferroni over the 13,750 frozen primary scoring rows.",
        file="simulation/v3/offline_estimator.py", claim=[("valin", 13750, ("simulation/v3/offline_estimator.py",))]))
    reg.append(R(
        name="span_fraction_screen", value="0.05 (5% of flow span)", units="fraction of flow range", role="gate",
        used_in="offline_estimator half-width/drift/residual screens; study/table_validation contrast; A4 tau=0.05 W", cls="arbitrary",
        ev=[("simulation/v3/offline_estimator.py", "empirical[\"bellman_residual_empirical\"] <= .05 * span"),
            ("simulation/v3/study.py", "ok = abs(difference) + half <= .05 * row[\"flow_range\"]")],
        evnote="design note A4: tolerance stays tau = 0.05 W. One convention reused across flow half-width, drift, the A4 residual tolerance, and the sensitivity contrast.",
        decided_by="A1, A4 (tau=0.05 W); R13 screens",
        notes="The 5%-of-flow-span tolerance reused across screens.",
        file="simulation/v3/offline_estimator.py", claim=[("valin", 0.05, ("simulation/v3/offline_estimator.py", "simulation/v3/study.py"))]))
    reg.append(R(
        name="heldout_coverage_floor", value="0.90", units="fraction", role="gate",
        used_in="offline_estimator coverage screen; table_validation_a4 A1-screen rebuild", cls="arbitrary",
        ev=[("simulation/v3/offline_estimator.py", "continuation_ok = empirical[\"heldout_coverage\"] >= .9")],
        evnote="design note A1: the 90 percent coverage floor.",
        decided_by="A1",
        notes="Minimum held-out transition coverage for a continuation table row to pass.",
        file="simulation/v3/offline_estimator.py", claim=[("valin", 0.9, ("simulation/v3/offline_estimator.py",))]))
    reg.append(R(
        name="plain_route_survival_threshold", value="0.5", units="surviving fraction", role="decision",
        used_in="offline_estimator route screen; study.table_design plain_route_minimum_surviving_fraction", cls="arbitrary",
        ev=[("simulation/v3/study.py", "\"plain_route_minimum_surviving_fraction\": .5,")],
        evnote="design note section 3: Lambda_F from plain runs wherever at least half the runs survive; else Fleming-Viot.",
        decided_by="R13",
        notes="Plain route used only when at least half the runs survive the measurement window. BLIND: a route-selection threshold, not a measured survival rate.",
        file="simulation/v3/study.py", claim=[("litf", "simulation/v3/study.py", 98, "0.5"), ("valin", 0.5, ("simulation/v3/offline_estimator.py",))]))
    reg.append(R(
        name="zeta_resolution_screens", value="rate floor 1e-4, rel half-width 0.3, death concentration cap 0.35, half-window rate ratio [2/3, 1.5]", units="various", role="gate",
        used_in="offline_estimator zeta resolution screens", cls="arbitrary",
        ev=[("simulation/v3/offline_estimator.py", "resolved = rate is not None and rate >= 1e-4 and zeta[\"half_width\"] <= .3 * rate and bool(np.all(total > 0))"),
            ("simulation/v3/offline_estimator.py", "resolved &= concentration <= .35 and ratio is not None and 2 / 3 <= ratio <= 1.5")],
        evnote="R13: zeta reported where it resolves the rate. BLIND: gates a diagnostic rate's reportability, not a survival result.",
        decided_by="R13",
        confidence="medium",
        notes="Screens deciding whether the extinction rate zeta is reported as resolved.",
        file="simulation/v3/offline_estimator.py",
        claim=[("valin", 0.0001, ("simulation/v3/offline_estimator.py",)), ("valin", 0.3, ("simulation/v3/offline_estimator.py",)),
               ("valin", 0.35, ("simulation/v3/offline_estimator.py",)), ("valin", 1.5, ("simulation/v3/offline_estimator.py",))]))
    reg.append(R(
        name="group_mean_t_critical", value="2.571 (df 5), 4.303 (df 2)", units="Student-t quantile", role="estimation",
        used_in="offline_estimator group-mean half-width", cls="derived",
        ev=[("simulation/v3/offline_estimator.py", "critical = 2.571 if len(values) >= 6 else 4.303")],
        evnote="Comment: six groups in production; 4.303 also conservatively covers >=3 groups. Student-t 95% two-sided df5/df2.",
        notes="Student-t 95% two-sided critical values for the group-mean half-width, from the group count.",
        file="simulation/v3/offline_estimator.py", claim=[("valin", 2.571, ("simulation/v3/offline_estimator.py",)), ("valin", 4.303, ("simulation/v3/offline_estimator.py",))]))
    reg.append(R(
        name="sensitivity_contrast_t_critical", value="2.015 (df 5, 90%)", units="Student-t quantile", role="estimation",
        used_in="study.assemble_tables sensitivity contrast; table_validation_a4 numerical contrast", cls="derived",
        ev=[("simulation/v3/study.py", "half = 2.015 * math.sqrt(float(av.var(ddof=1) / len(av) + bv.var(ddof=1) / len(bv)))")],
        evnote="A3/R13. Student-t 90% one-sided critical value (df=5) for the doubled-population/length contrast half-width.",
        decided_by="A3; R13 nine-pair contrasts",
        notes="Sensitivity contrast half-width t multiplier.",
        file="simulation/v3/study.py", claim=[("valin", 2.015, ("simulation/v3/study.py", "simulation/v3/table_validation_a4.py"))]))
    reg.append(R(
        name="sensitivity_reproduction_rate_subset", value="(0.055, 0.064, 0.070)", units="reproduction rate", role="run-setting",
        used_in="offline_estimator.SENSITIVITY_RR; the 3-rule x 3-rr subset", cls="arbitrary",
        ev=[("simulation/v3/offline_estimator.py", "SENSITIVITY_RR = (.055, .064, .070)")],
        evnote="design note section 3: sensitivity settings on a declared subset of 3 rules x 3 rr.",
        decided_by="R13 (frozen nine-pair sensitivity subset)",
        confidence="medium",
        notes="Pre-declared reproduction-rate subset for the table sensitivity contrasts.",
        file="simulation/v3/offline_estimator.py", claim=[("base", "SENSITIVITY_RR")]))
    reg.append(R(
        name="census_window", value="500 start steps, 20-step endpoint horizon", units="steps", role="estimation",
        used_in="unpublished_bins.endpoint_counts; table_validation_a4 census; continuation_validation census", cls="arbitrary",
        ev=[("simulation/v3/unpublished_bins.py", "Use t+20 along held-out plain paths, omitting already extinct starts.")],
        evnote="design note A4: 20-step endpoints over 500 start steps on the census seed.",
        decided_by="A4 (availability census law)",
        notes="Availability census / endpoint diagnostic window.",
        file="simulation/v3/unpublished_bins.py", claim=[("valin", 20, ("simulation/v3/unpublished_bins.py", "simulation/v3/table_validation_a4.py")),
                                                         ("valin", 500, ("simulation/v3/unpublished_bins.py", "simulation/v3/table_validation_a4.py"))]))

    # === A4 certification (continuation_validation.py) ===
    reg.append(R(
        name="a4_certification_alpha", value="0.05", units="confidence alpha", role="gate",
        used_in="continuation_validation.ALPHA; empirical_bernstein; fv_cell_test", cls="arbitrary",
        ev=[("simulation/v3/continuation_validation.py", "ALPHA = 0.05")],
        evnote="design note A4: alpha = 0.05 (0.95 simultaneous coverage).",
        decided_by="A4/D30",
        notes="Simultaneous confidence level for the A4 plain empirical-Bernstein certificate and the FV interval tests.",
        file="simulation/v3/continuation_validation.py", claim=[("base", "ALPHA")]))
    reg.append(R(
        name="a4_validation_groups", value="32 groups; plain 64 runs/group (2048 traj), FV 256 particles/group", units="counts", role="run-setting",
        used_in="continuation_validation GROUPS/PLAIN_RUNS_PER_GROUP/FV_PARTICLES", cls="arbitrary",
        ev=[("simulation/v3/continuation_validation.py", "GROUPS = 32"),
            ("simulation/v3/continuation_validation.py", "PLAIN_RUNS_PER_GROUP = 64          # 2,048 independent trajectories per replicate")],
        evnote="design note A4: every replicate has 32 groups; plain 64 runs/group (2,048 trajectories), FV 256 particles/group.",
        decided_by="A4/D30",
        notes="A4 validation sampling.",
        file="simulation/v3/continuation_validation.py", claim=[("base", "GROUPS"), ("base", "PLAIN_RUNS_PER_GROUP"), ("base", "FV_PARTICLES")]))
    reg.append(R(
        name="a4_replicate_schedule", value="fit 0, plain validate (1,2,3), FV validate 1, census 0", units="replicate indices", role="run-setting",
        used_in="continuation_validation FIT/VALIDATE/FV_VALIDATE/CENSUS replicates; seed derivation", cls="arbitrary",
        ev=[("simulation/v3/continuation_validation.py", "VALIDATE_REPLICATES = (1, 2, 3)    # plain"),
            ("simulation/v3/continuation_validation.py", "FV_VALIDATE_REPLICATE = 1          # FV gets one validation replicate")],
        evnote="design note A4: one plain fitting replicate and three plain validation replicates; one FV validation replicate.",
        decided_by="A4/D30",
        notes="A4 replicate indices.",
        file="simulation/v3/continuation_validation.py", claim=[("base", "FIT_REPLICATE"), ("base", "VALIDATE_REPLICATES"), ("base", "FV_VALIDATE_REPLICATE"), ("base", "CENSUS_REPLICATE")]))
    reg.append(R(
        name="a4_fv_min_groups", value="16", units="groups", role="gate",
        used_in="continuation_validation.FV_MIN_GROUPS; fv_cell_test", cls="arbitrary",
        ev=[("simulation/v3/continuation_validation.py", "FV_MIN_GROUPS = 16")],
        evnote="design note A4: cells with fewer than 16 contributing groups are unresolved.",
        decided_by="A4/D30",
        notes="An FV cell is unresolved below 16 contributing groups.",
        file="simulation/v3/continuation_validation.py", claim=[("base", "FV_MIN_GROUPS")]))
    reg.append(R(
        name="a4_bernstein_constants", value="7 and 3 (Maurer-Pontil), 4M/alpha log argument", units="bound constants", role="estimation",
        used_in="continuation_validation.empirical_bernstein", cls="derived",
        ev=[("simulation/v3/continuation_validation.py", "rho = math.sqrt(2 * var * log_term / n) + 7 * width * log_term / (3 * (n - 1))"),
            ("simulation/v3/continuation_validation.py", "log_term = math.log(4 * M / alpha)")],
        evnote="design note A4 gives the same Maurer-Pontil formula. Constants fixed by the inequality, not tunable.",
        decided_by="A4/D30",
        notes="Constants of the two-sided Maurer-Pontil empirical Bernstein bound.",
        file="simulation/v3/continuation_validation.py", claim=[("lit", 291, "2"), ("lit", 291, "7"), ("lit", 291, "3"), ("lit", 290, "4")]))
    reg.append(R(
        name="a4_availability_floor", value="living cap 0.02, low-population cap 0.05, low minimum 50", units="fraction / count", role="gate",
        used_in="continuation_validation.census_floor", cls="arbitrary",
        ev=[("simulation/v3/continuation_validation.py", "def census_floor(fractions, living_cap=0.02, low_cap=0.05, low_minimum=50):")],
        evnote="design note A4: at most 2% of living endpoints, and at most 5% of low-population living endpoints (assessed only with at least 50), outside the validated support.",
        decided_by="A4/D30 (availability floor)",
        notes="A4 availability floor.",
        file="simulation/v3/continuation_validation.py", claim=[("base", "living_cap.arg"), ("base", "low_cap.arg"), ("base", "low_minimum.arg")]))
    reg.append(R(
        name="a4_seed_truncation_bits", value="60 (hexdigest[:15])", units="bits", role="run-setting",
        used_in="continuation_validation._truncated_sha seed derivation", cls="arbitrary",
        ev=[("simulation/v3/continuation_validation.py", "return int(m.hexdigest()[:15], 16)")],
        evnote="design note A4: SHA-256 digests truncated to 60 bits (15 hex chars).",
        decided_by="A4/D30",
        notes="Validation-seed SHA-256 truncation to 60 bits. Structural seed derivation.",
        file="simulation/v3/continuation_validation.py", claim=[("lit", 60, "15")]))
    reg.append(R(
        name="a4_cell_encoding", value="radix 8 (base-8 over 6 coords), POP0 offset 100", units="code", role="estimation",
        used_in="continuation_validation RADIX/COARSE_BASE/POP0_CELL; low-population = code % 8 == 0", cls="derived",
        ev=[("simulation/v3/continuation_validation.py", "RADIX = np.array([8 ** i for i in range(6)], dtype=np.int64)"),
            ("simulation/v3/continuation_validation.py", "POP0_CELL = COARSE_BASE + 100")],
        evnote="Base-8 encoding of the six summary-bin coordinates into one cell code; POP0_CELL merges every population-category-0 bin. Structural to the bin space.",
        notes="Cell-code encoding for the A4 tiers.",
        file="simulation/v3/continuation_validation.py", claim=[("lit", 38, "8"), ("lit", 39, "8"), ("lit", 40, "100")]))

    # === guards ===
    reg.append(R(
        name="succession_gate_quorum", value="count 4, fault_budget 1 (count >= 3f+1); required (count+f+2)//2 = 3", units="validators / votes", role="decision",
        used_in="guards.ExecutionGuards succession authorization", cls="derived",
        ev=[("simulation/v3/guards.py", "def __init__(self, count=4, fault_budget=1, authority=None):"),
            ("simulation/v3/guards.py", "self.required = (count + fault_budget + 2) // 2")],
        evnote="Docstring: a local simulation gate, not certification of D10-D12 institutions.",
        confidence="medium",
        needs_operator_decision="yes",
        notes="Local B1 succession gate quorum (4 validators, 1-fault budget, 3 required votes). A governance/authorization sizing; the docstring calls it a local simulation gate. Operator should confirm whether it belongs in the sensitivity scope of the reruns.",
        file="simulation/v3/guards.py", claim=[("base", "count.arg"), ("base", "fault_budget.arg"), ("lit", 29, "3"), ("lit", 32, "2")]))

    return reg


# ---------------------------------------------------------------------------
# Excluded categorizer. Runs only on literals NOT claimed by a register row.
_ARRAY_FNS = {
    "reshape", "arange", "range", "eye", "identity", "zeros", "ones", "empty",
    "full", "tile", "broadcast_to", "argpartition", "array_split", "swapaxes",
    "moveaxis", "expand_dims", "column_stack", "stack", "concatenate",
    "fill_diagonal", "nextafter", "SeedSequence", "generate_state", "repeat",
    "take_along_axis", "argsort", "sort", "cumsum", "roll", "diff", "unique",
    "searchsorted", "bincount", "ix_", "fromkeys", "round",
}
_STRUCT_KW = {"axis", "ndmin", "decimals", "maxsize", "minlength", "ddof",
              "side", "kind", "initial", "base", "dtype", "copy", "indent",
              "repeat", "return_inverse", "return_counts"}


def _structural_context(src, node):
    child = node
    for parent in src.ancestry(node):
        if isinstance(parent, ast.Subscript):
            if child is parent.slice:
                return "subscript-index", "Fixed sequence or array index; structural position, not a tunable magnitude."
        if isinstance(parent, ast.Slice):
            return "slice-bound", "Sequence slice boundary; structural traversal, not a tunable magnitude."
        if isinstance(parent, ast.Call):
            fn = parent.func
            name = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
            if name in _ARRAY_FNS and any(child is a or (isinstance(a, (ast.Tuple, ast.List)) and child in ast.walk(a)) for a in parent.args):
                return "array-shape-or-construction", "Array shape, axis-count or construction argument; structural, not a model magnitude."
        if isinstance(parent, ast.keyword) and parent.arg in _STRUCT_KW:
            return "call-keyword", f"Structural {parent.arg}= keyword argument, not a model magnitude."
        if isinstance(parent, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Return,
                               ast.FunctionDef, ast.AsyncFunctionDef, ast.If, ast.For, ast.While)):
            break
        child = parent
    return None


def excluded_category(src, node):
    value = node.value
    struct = _structural_context(src, node)
    if struct is not None:
        return struct
    if isinstance(value, float) and value != 0 and abs(value) <= 1e-3:
        return "numerical-tolerance", "Floating-point tolerance, convergence slack or divide/log guard, not a model magnitude."
    if value in (0, 1, -1, 2, 0.5, 1.0, 0.0, -1.0, 2.0):
        return "identity-or-endpoint", "Normalization identity, probability/unit endpoint, or small structural factor (halving, two-sided, 1-x complement), not a distinct tunable parameter."
    if value in (100, 1000):
        return "unit-scale", "Unit-scale divisor or multiplier (welfare thousandths /1000, stock hundredths /100); the grids themselves are registered, these are conversions."
    return ("operational-scenario-or-mirror",
            "In-scope numeric that is not a distinct new parameter: an "
            "operational/runtime setting (worker, thread, timeout, memory, poll, "
            "retry, buffer, deadline, hash length), a fixed validation test "
            "scenario or fixture value, a structural count (channels, dimensions, "
            "stocks, groups), or a duplicated occurrence of a parameter registered "
            "from its defining module (see the register row of the same value).")


# ---------------------------------------------------------------------------
def normalize_claim(row):
    out = []
    rfile = row["file"]
    for m in row["claim"]:
        if m[0] == "base":
            out.append(("base", rfile, m[1]))
        elif m[0] == "lit":
            out.append(("lit", rfile, m[1], m[2]))
        else:
            out.append(m)
    return out


def match(src, node, m):
    if m[0] in ("base", "basef"):
        return src.rel == m[1] and src.base(node) == m[2]
    if m[0] in ("lit", "litf"):
        return src.rel == m[1] and node.lineno == m[2] and src.unparse(node) == m[3]
    if m[0] == "valin":
        signed = node.value
        p = src.parent(node)
        if isinstance(p, ast.UnaryOp) and isinstance(p.op, ast.USub):
            signed = -node.value
        return src.rel in m[2] and signed == m[1] and type(signed) is type(m[1])
    if m[0] == "linef":
        return src.rel == m[1] and node.lineno == m[2]
    return False


def offpath_report():
    rows = []
    for name in OFFPATH_MODULES:
        path = V3 / f"{name}.py"
        if not path.exists():
            continue
        src = Source(path)
        rows.append(dict(
            file=src.rel, category="off-path-module", count=len(src.literals),
            reason=("Not in the registered rerun / offline-table import closure; nothing on the "
                    "production path imports it. Standalone diagnostic, probe or validation harness. "
                    "Its literals are test scaffolding, not instrument parameters."),
            locations=f"{src.rel}:1-{len(src.lines)} (whole file)"))
    return rows


FIELDS = ("id", "name", "value", "units", "role", "class", "class_evidence",
          "decided_by", "v2_lineage", "sensitivity_candidate", "proposed_range",
          "needs_operator_decision", "confidence", "used_in", "locations", "notes")


def render_and_verify_evidence(register, sources):
    """Locate every evidence anchor verbatim in its source and render the quote.
    Returns (quotes_checked, failures). Sets row['class_evidence']."""
    quotes_checked = 0
    failures = []
    for row in register:
        segments = []
        for anchor in row["ev"]:
            afile, atext = anchor if isinstance(anchor, tuple) else (row["file"], anchor)
            src = sources.get(_mod(afile))
            if src is None:
                failures.append((row["name"], afile, "file not scoped"))
                continue
            try:
                line, span = src.locate_anchor(atext)
            except LookupError as exc:
                failures.append((row["name"], afile, str(exc)))
                continue
            quotes_checked += 1
            segments.append(f"{afile}:{line}: {span}")
        if row["evnote"]:
            segments.append("context: " + row["evnote"])
        row["class_evidence"] = " | ".join(segments)
    return quotes_checked, failures


def _mod(rel):
    return Path(rel).stem


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="overwrite existing outputs")
    parser.add_argument("--report-unclaimed", action="store_true",
                        help="print literals not yet claimed by a register row, then exit")
    args = parser.parse_args()

    out_csv = OUT / "v3_parameter_register.csv"
    out_jsonl = OUT / "v3_parameter_register.jsonl"
    out_excl = OUT / "v3_parameter_register_excluded.csv"
    out_manifest = OUT / "v3_parameter_register_manifest.json"
    out_summary = OUT / "v3_parameter_register_summary.md"
    outputs = [out_csv, out_jsonl, out_excl, out_manifest, out_summary]
    if not args.report_unclaimed and not args.force and any(p.exists() for p in outputs):
        raise SystemExit("outputs exist; pass --force to overwrite")

    sources = {name: Source(V3 / f"{name}.py") for name in SCOPE_MODULES}
    register = load_register()
    for row in register:
        row["_claim"] = normalize_claim(row)

    # Verify every evidence quote verbatim against source.
    quotes_checked, failures = render_and_verify_evidence(register, sources)
    if failures:
        for name, afile, why in failures:
            print(f"EVIDENCE FAIL [{name}] {afile}: {why}")
        raise SystemExit(f"{len(failures)} evidence anchors did not verify verbatim")

    all_locs = {}
    for src in sources.values():
        for node in src.literals:
            all_locs[(src.rel, node.lineno, node.col_offset)] = (src, node)

    claimed = {}
    row_locs = collections.defaultdict(list)
    for loc, (src, node) in all_locs.items():
        for ridx, row in enumerate(register):
            if any(match(src, node, m) for m in row["_claim"]):
                if loc in claimed:
                    raise SystemExit(
                        f"double claim at {loc}: rows '{register[claimed[loc]]['name']}' and '{row['name']}'")
                claimed[loc] = ridx
                row_locs[ridx].append(loc)

    excluded = collections.defaultdict(list)
    for loc, (src, node) in all_locs.items():
        if loc in claimed:
            continue
        cat, reason = excluded_category(src, node)
        excluded[(src.rel, cat, reason)].append(loc)

    if args.report_unclaimed:
        for (f, cat, reason), locs in sorted(excluded.items()):
            if cat != "operational-scenario-or-mirror":
                continue
            print(f"\n== {f} [{cat}] {len(locs)} ==")
            for (ff, ln, co) in sorted(locs):
                src, node = all_locs[(ff, ln, co)]
                print(f"  {ff}:{ln}  {src.unparse(node)!r}  in {src.scope(node)}")
        return

    total = len(all_locs)
    covered = len(claimed) + sum(len(v) for v in excluded.values())
    assert covered == total, f"coverage mismatch: {covered} != {total}"

    order = sorted(range(len(register)), key=lambda i: (register[i]["file"] or "zzz", register[i]["name"]))
    reg_rows, jsonl_rows = [], []
    counts_class = collections.Counter()
    counts_role = collections.Counter()
    n_candidates = n_operator = 0
    for new_id, ridx in enumerate(order, start=1):
        row = register[ridx]
        locs = sorted(row_locs.get(ridx, []))
        loc_text = "; ".join(f"{f}:{ln}" for (f, ln, co) in locs) or row.get("used_in", "")
        rec = {
            "id": f"V-{new_id:04d}", "name": row["name"], "value": row["value"],
            "units": row["units"], "role": row["role"], "class": row["cls"],
            "class_evidence": row["class_evidence"], "decided_by": row["decided_by"],
            "v2_lineage": row["v2_lineage"], "sensitivity_candidate": row["sensitivity_candidate"],
            "proposed_range": row["proposed_range"], "needs_operator_decision": row["needs_operator_decision"],
            "confidence": row["confidence"], "used_in": row["used_in"],
            "locations": loc_text, "notes": row["notes"],
        }
        reg_rows.append(rec)
        jsonl_rows.append({**rec, "claim_locations": [f"{f}:{ln}:{co}" for (f, ln, co) in locs]})
        counts_class[row["cls"]] += 1
        counts_role[row["role"]] += 1
        n_candidates += row["sensitivity_candidate"] == "yes"
        n_operator += row["needs_operator_decision"] == "yes"

    excl_rows = []
    for (f, cat, reason), locs in sorted(excluded.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        lines = sorted({ln for (ff, ln, co) in locs})
        excl_rows.append(dict(file=f, category=cat, count=len(locs), reason=reason,
                              locations="; ".join(f"{f}:{ln}" for ln in lines)))
    excl_rows.extend(offpath_report())

    manifest = {
        "generator": "build_v3_parameter_register.py",
        "scope_criterion": ("import closure of the registered rerun / offline-table entry points "
                            "(v3.production_runner and the modules it reaches, over both "
                            "'from .X import' and 'from . import X' forms)"),
        "scope_modules": list(SCOPE_MODULES),
        "offpath_modules_excluded": list(OFFPATH_MODULES),
        # Hashes are of LF-normalized bytes, as table_compatibility.dependency_hash does, so a
        # Windows checkout (CRLF) and the X2 (LF) record the same identity as the git blobs.
        "hash_normalization": "CRLF to LF before SHA-256",
        "files": [{"path": src.rel, "sha256": hashlib.sha256(src.path.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
                   "numeric_literals": len(src.literals)}
                  for src in sorted(sources.values(), key=lambda s: s.rel)],
        "external_config": {
            "path": "simulation/v3/runs/registered/v3_rerun_calibration.json",
            "sha256": hashlib.sha256((ROOT / "simulation/v3/runs/registered/v3_rerun_calibration.json").read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            if (ROOT / "simulation/v3/runs/registered/v3_rerun_calibration.json").exists() else None},
        "scoped_numeric_literals": total,
        "claimed_by_register": len(claimed),
        "covered_by_excluded": sum(len(v) for v in excluded.values()),
        "register_rows_total": len(reg_rows),
        "register_rows_external": sum(1 for r in register if not r["file"]),
        "excluded_buckets": len(excl_rows),
        "evidence_quotes_verified_verbatim": quotes_checked,
        "counts_by_class": {k: counts_class[k] for k in ("measured", "calibrated", "derived", "arbitrary")},
        "counts_by_role": dict(sorted(counts_role.items())),
        "sensitivity_candidates": n_candidates,
        "needs_operator_decision": n_operator,
        "coverage_complete": covered == total,
    }

    with out_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader(); w.writerows(reg_rows)
    with out_jsonl.open("w", encoding="utf-8") as fh:
        for rec in jsonl_rows:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    with out_excl.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=("file", "category", "count", "reason", "locations"))
        w.writeheader(); w.writerows(excl_rows)
    with out_manifest.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=True); fh.write("\n")

    summary = build_summary(reg_rows, excl_rows, manifest)
    assert "—" not in summary, "no em-dashes"
    for rec in reg_rows:
        assert all("—" not in str(v) for v in rec.values()), f"em-dash in {rec['id']}"
    with out_summary.open("w", encoding="utf-8") as fh:
        fh.write(summary)

    print(json.dumps({k: manifest[k] for k in (
        "scoped_numeric_literals", "claimed_by_register", "covered_by_excluded",
        "register_rows_total", "evidence_quotes_verified_verbatim", "counts_by_class",
        "sensitivity_candidates", "needs_operator_decision", "coverage_complete")}, indent=2))


def build_summary(reg_rows, excl_rows, manifest):
    L = ["# v3 instrument parameter provenance register (W11 item 2)", "",
         "Read-only static build. One row per distinct model-driving parameter, plus an",
         "excluded list that accounts for every remaining numeric literal in the scoped",
         "modules. No simulation code was imported; values are read from source. Every",
         "evidence quote is located and verified verbatim against its source line.", "",
         "## Scope", "",
         f"- Criterion: {manifest['scope_criterion']}.",
         f"- Scoped modules: {len(manifest['scope_modules'])} ("
         + ", ".join(manifest["scope_modules"]) + ").",
         "- Off-path modules excluded at file granularity: "
         + ", ".join(manifest["offpath_modules_excluded"]) + ".",
         f"- Scoped numeric literals: {manifest['scoped_numeric_literals']}. "
         f"Claimed by register rows: {manifest['claimed_by_register']}. "
         f"Covered by excluded buckets: {manifest['covered_by_excluded']}.",
         f"- Evidence quotes verified verbatim: **{manifest['evidence_quotes_verified_verbatim']}**.",
         f"- Coverage complete (every scoped literal claimed or excluded exactly once): "
         f"**{manifest['coverage_complete']}**.",
         "- External constants v3 imports for its dynamics (SUCCESSION_* from",
         "  simulation/model.py, H_N_V_REF from simulation/metrics.py) and the frozen",
         "  calibration file values are carried as register rows; their defining modules",
         "  belong to the v2 register and are not re-scoped for coverage.", "",
         "## Counts by class", "", "| Class | Rows |", "| --- | ---: |"]
    for k in ("measured", "calibrated", "derived", "arbitrary"):
        L.append(f"| {k} | {manifest['counts_by_class'][k]} |")
    L.append(f"| **total** | **{manifest['register_rows_total']}** |")
    L += ["", "## Counts by role", "", "| Role | Rows |", "| --- | ---: |"]
    for k, v in manifest["counts_by_role"].items():
        L.append(f"| {k} | {v} |")
    L += ["", f"Sensitivity candidates: **{manifest['sensitivity_candidates']}**. "
          f"Rows needing an operator decision: **{manifest['needs_operator_decision']}**.", "",
          "## Sensitivity candidates and proposed ranges", "",
          "Arbitrary constants that enter the dynamics, objective or a decision. Every range",
          "is a PROPOSAL only; the operator and a later pre-registration set the real ones.", "",
          "| id | name | value | role | proposed range (proposal) |", "| --- | --- | --- | --- | --- |"]
    for r in reg_rows:
        if r["sensitivity_candidate"] == "yes":
            L.append(f"| {r['id']} | {r['name']} | {_c(r['value'])} | {r['role']} | {_c(r['proposed_range'])} |")
    L += ["", "## Constants needing an operator decision", ""]
    ops = [r for r in reg_rows if r["needs_operator_decision"] == "yes"]
    if ops:
        L += ["| id | name | class | why |", "| --- | --- | --- | --- |"]
        for r in ops:
            L.append(f"| {r['id']} | {r['name']} | {r['class']} | {_c(r['notes'])} |")
    else:
        L.append("None.")
    L += ["", "## First-pass (local-model lead) errors corrected", "",
          "- `reproduction_rate` 0.08 was tagged RETIRED by the first pass; it is KEEP. Here",
          "  it is an arbitrary demographic constant and the calibration operating point,",
          "  swept on its own registered grids in the reruns (see the R1/R2 rr grid rows).",
          "- Sweep-script config keys duplicated the canonical names; this register keys on",
          "  one row per distinct parameter and lists every code location, so duplicated",
          "  occurrences (calibration/design overrides, cross-file copies, RuleBatch mirrors)",
          "  attach to a single parameter rather than spawning new entries.",
          "- The leads are v2-code-keyed and noisy on the CALIBRATION/RETIRED/REPLACED",
          "  boundary; every class here was set from the v3 source and the decision record.",
          "- Scope correction: continuation_validation.py (the A4 certification numerics)",
          "  enters the registered path through `from . import continuation_validation`, an",
          "  import form a first closure pass missed. It is scoped and its A4 constants",
          "  are registered.", "",
          "## Coverage result", "",
          f"Every one of the {manifest['scoped_numeric_literals']} numeric literals in the",
          f"{len(manifest['scope_modules'])} scoped modules is accounted for: "
          f"{manifest['claimed_by_register']} claimed by the "
          f"{manifest['register_rows_total'] - manifest['register_rows_external']} register",
          f"rows with in-file claims, and {manifest['covered_by_excluded']} covered by the",
          f"excluded buckets. {manifest['register_rows_external']} further register rows carry",
          "external constants and frozen calibration values that have no v3 source literal.",
          "The build asserts this partition, verifies every evidence quote verbatim, and",
          "records per-file SHA-256 hashes and literal counts in the manifest.", "",
          "## Excluded categories", "", "| category | files | buckets | literals |",
          "| --- | ---: | ---: | ---: |"]
    bycat = collections.defaultdict(lambda: [set(), 0, 0])
    for r in excl_rows:
        e = bycat[r["category"]]
        e[0].add(r["file"]); e[1] += 1; e[2] += r["count"]
    for cat, (files, buckets, lits) in sorted(bycat.items(), key=lambda kv: -kv[1][2]):
        L.append(f"| {cat} | {len(files)} | {buckets} | {lits} |")
    L.append("")
    return "\n".join(L) + "\n"


def _c(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    main()
