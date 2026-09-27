"""Static, create-only provenance inventory. Never imports simulation code.

Run with python -B. Existing outputs are refused. All generated files remain
beside this script. Numeric occurrences are retained, including housekeeping,
so a reviewer can distinguish coverage from sensitivity-analysis priorities.
"""

import ast
import collections
import csv
import hashlib
import io
import json
import operator
from pathlib import Path
import re
import subprocess
import tokenize

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FIELDS = (
    "name", "file", "line", "value", "units_if_stated", "used_in",
    "documented_rationale", "suggested_class", "class_evidence",
    "confidence", "needs_operator_decision",
)
CORE_FILES = {
    "agents.py", "model.py", "metrics.py", "working_factor.py",
    "constants_v2_stage15.py", "constants_v2_stage18.py",
    "attack_adapter_v2.py", "defection.py",
}


def git(*args):
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr)
    return result.stdout


def numeric(node):
    return isinstance(node, ast.Constant) and type(node.value) in (int, float, complex)


class Source:
    def __init__(self, path):
        self.path = path
        self.rel = path.relative_to(ROOT).as_posix()
        self.text = path.read_text(encoding="utf-8-sig")
        self.lines = self.text.splitlines()
        self.tree = ast.parse(self.text, filename=self.rel)
        self.parents = {child: parent for parent in ast.walk(self.tree)
                        for child in ast.iter_child_nodes(parent)}
        self.comments = {}
        for token in tokenize.generate_tokens(io.StringIO(self.text).readline):
            if token.type == tokenize.COMMENT:
                self.comments[token.start[0]] = token.string
        self.numeric_nodes = [node for node in ast.walk(self.tree) if numeric(node)]

    def ancestry(self, node):
        while node in self.parents:
            node = self.parents[node]
            yield node

    def segment(self, node):
        return ast.get_source_segment(self.text, node) or ast.unparse(node)

    def scope(self, node):
        names = [item.name for item in self.ancestry(node)
                 if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        return ".".join(reversed(names)) or "<module>"

    def label(self, node):
        trail = []
        lookup = set()
        child = node
        for parent in self.ancestry(node):
            if isinstance(parent, ast.Call):
                function = parent.func
                if isinstance(function, ast.Attribute) and function.attr in ("get", "setdefault"):
                    if len(parent.args) > 1 and child is parent.args[1]:
                        key = parent.args[0]
                        if isinstance(key, ast.Constant) and isinstance(key.value, str):
                            return key.value + ".default" + "".join(trail), {key.value}, key.value
                if isinstance(function, ast.Name) and function.id == "getattr":
                    if len(parent.args) > 2 and child is parent.args[2]:
                        key = parent.args[1]
                        if isinstance(key, ast.Constant) and isinstance(key.value, str):
                            return key.value + ".fallback" + "".join(trail), {key.value}, key.value
            if isinstance(parent, ast.Dict):
                for key, value in zip(parent.keys, parent.values):
                    if child is value and isinstance(key, ast.Constant):
                        trail.insert(0, "[" + repr(key.value) + "]")
                        if isinstance(key.value, str):
                            lookup.add(key.value)
                        break
            if isinstance(parent, (ast.List, ast.Tuple, ast.Set)):
                trail.insert(0, f"[{parent.elts.index(child)}]")
            if isinstance(parent, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = parent.targets if isinstance(parent, ast.Assign) else [parent.target]
                base = ",".join(ast.unparse(target) for target in targets)
                lookup.update(re.findall(r"[A-Za-z_]\w*", base))
                return base + "".join(trail), lookup, base
            if isinstance(parent, ast.arguments):
                positional = parent.posonlyargs + parent.args
                pairs = list(zip(positional[len(positional) - len(parent.defaults):], parent.defaults))
                pairs += list(zip(parent.kwonlyargs, parent.kw_defaults))
                for argument, default in pairs:
                    if child is default:
                        return argument.arg + ".argument_default", {argument.arg}, argument.arg
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                break
            child = parent
        return "literal", lookup, ""

    def rationale(self, node):
        quotes = []
        # Inline comment plus the contiguous comment block above the statement.
        if node.lineno in self.comments:
            quotes.append((node.lineno, self.comments[node.lineno]))
        statement = next((item for item in (node, *self.ancestry(node))
                          if isinstance(item, ast.stmt)), node)
        line = statement.lineno - 1
        # A block can document several adjacent assignments, such as the
        # welfare coefficients. Cross those assignments, but not blank lines.
        while line > 0 and self.lines[line - 1].strip() and line not in self.comments:
            if not re.match(r"\s*[A-Z_]\w*\s*=", self.lines[line - 1]):
                break
            line -= 1
        block = []
        while line > 0 and line in self.comments:
            block.append((line, self.comments[line]))
            line -= 1
        quotes.extend(reversed(block))
        # Enclosing dictionary entries can carry the only adjacent comment.
        if not quotes:
            line = node.lineno - 1
            while line > max(0, node.lineno - 8):
                if line in self.comments:
                    quotes.append((line, self.comments[line]))
                elif self.lines[line - 1].strip() and quotes:
                    break
                line -= 1
            quotes.sort()
        text = " | ".join(f"{self.rel}:{line} " + json.dumps(quote, ensure_ascii=True)
                          for line, quote in quotes)
        if not quotes:
            owner = next((item for item in self.ancestry(node)
                          if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))), self.tree)
            doc = ast.get_docstring(owner, clean=False)
            if doc:
                # Preserve the complete first paragraph as a verbatim excerpt.
                excerpt = doc.split("\n\n", 1)[0]
                docline = owner.body[0].lineno
                text = f"Enclosing docstring {self.rel}:{docline} " + json.dumps(excerpt, ensure_ascii=True)
        return text or "No adjacent comment or enclosing docstring states a basis."


def constant_value(node, symbols):
    """Evaluate only literal containers and a small arithmetic whitelist."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return symbols[node.id]
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return tuple(constant_value(item, symbols) for item in node.elts)
    if isinstance(node, ast.UnaryOp):
        operation = {ast.USub: operator.neg, ast.UAdd: operator.pos}[type(node.op)]
        return operation(constant_value(node.operand, symbols))
    if isinstance(node, ast.BinOp):
        operation = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                     ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
                     ast.Pow: operator.pow, ast.Mod: operator.mod}[type(node.op)]
        return operation(constant_value(node.left, symbols), constant_value(node.right, symbols))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "len":
        return len(constant_value(node.args[0], symbols))
    raise ValueError("Not a statically evaluable constant")


def classify(source, node, base, label, kind="literal"):
    leaf = base.split(".")[-1]
    filename = source.path.name
    scope = source.scope(node)
    expression = source.segment(node)
    where = f"{source.rel}:{node.lineno}"
    if kind == "nonfinite":
        return "derived", f"{where}: IEEE infinity or NaN sentinel, {expression}; a numerical representation or ordering identity, not a calibrated magnitude.", "high", "no"
    if kind == "numeric_string":
        return "arbitrary", f"{where}: numeric text used in code, {expression}; retained conservatively for environment settings, parsing or numeric labels. No stated numerical basis.", "low", "yes"
    if kind == "expression":
        return "derived", f"{where}: exact static expression {expression}; numeric result recorded alongside the expression. Inputs retain their own classifications.", "high", "no"
    if kind == "alias":
        return "arbitrary", f"{where}: named fallback {expression}; consult its definition's separate row. Inheritance alone is not an empirical or theoretical basis.", "low", "yes"
    if filename == "metrics.py" and leaf in {"H_N_V_REF", "H_N_V_PROJ_K"}:
        return "calibrated", (f"{where}: internal simulated honest-baseline statistic or projection fit, not an external measurement. "
                              "See simulation/diagnostics/estimator_repair_report.md:65 and simulation/diagnostics/planner_d3_report.md:65."), "high", "no"
    if filename == "constants_v2_stage15.py" and leaf in {"BIRTH_WB_MEAN", "BIRTH_AGE_MEAN"}:
        return "derived", f"{where}: adjacent comment derives the mean of the configured uniform distribution, (0.5+0.8)/2 or (50-1)/2.", "high", "no"
    if filename == "constants_v2_stage15.py" and leaf in {"WB_TARGET", "K_RESILIENCE_INVESTMENT"}:
        return "calibrated", f"{where}: adjacent comment explicitly anchors to simulated equilibrium or calibrates against a target steady state.", "high", "no"
    if filename == "constants_v2_stage18.py" and leaf == "STATE_ALLOCATION_MAPPING":
        return "calibrated", (f"{where}: module's adjacent placeholder rationale explicitly chooses coefficients for response within 5-10 steps and plausible operating values. "
                              "This is provisional behavioral tuning, not economic theory or external measurement; operator review remains necessary."), "medium", "yes"
    if leaf in {"BRIDGE_R_BALANCED_HEALTHY", "_BRIDGE_R_BALANCED_HEALTHY"}:
        return "calibrated", "simulation/model.py:101-110: balanced-allocation bridge anchor matched to the v1.x.2 optimizer's r=0.9 equilibrium; agent copy mirrors it.", "high", "no"
    if leaf == "k1_transition" and filename == "model.py":
        return "derived", f"{where}: adjacent formula k1 = 1.5 / ln(2), rounded to 2.164; the 1.5 normalization anchor remains an arbitrary input.", "high", "no"
    if leaf in {"CUSUM_K", "CUSUM_H", "CUSUM_PENALTY"} and filename == "model.py":
        return "calibrated", "simulation/model.py:44-54: documented tuning against aligned noise and systematic 8% claim inflation, with immediate saturation on rejection.", "medium", "no"
    if scope == "_smoothstep":
        return "derived", f"{where}: coefficients of the documented cubic Hermite smoothstep 3*x^2-2*x^3.", "high", "no"
    ancestors = list(source.ancestry(node))
    if leaf in {"BRIDGE_BALANCED_SHARE", "_BRIDGE_BALANCED_SHARE"}:
        return "derived", f"{where}: equal shares across the six declared resource categories, 1/6.", "high", "no"
    parent = source.parents.get(node)
    if isinstance(parent, ast.Subscript) and parent.slice is node:
        return "derived", f"{where}: literal sequence index in {source.segment(parent)}; structural position, not a fitted dynamic coefficient.", "high", "no"
    if isinstance(parent, ast.Slice):
        return "derived", f"{where}: sequence slice boundary in the stated traversal; retained for exhaustive literal coverage.", "medium", "no"
    if isinstance(parent, ast.UnaryOp) and isinstance(source.parents.get(parent), (ast.Subscript, ast.Slice)):
        return "derived", f"{where}: signed sequence index or slice boundary; retained for exhaustive literal coverage.", "high", "no"
    if numeric(node) and node.value in (0, 1):
        clamp = next((ancestor for ancestor in ancestors[:3] if isinstance(ancestor, ast.Call)
                      and ast.unparse(ancestor.func) in ("np.clip", "min", "max")), None)
        if clamp is not None and any(word in source.segment(clamp).lower()
                                     for word in ("prob", "well_being", "avg_wb", "shape", "stock", "suppression")):
            return "derived", f"{where}: endpoint of the explicitly normalized probability, well-being, shape or stock interval in {source.segment(clamp)}.", "medium", "no"
    return "arbitrary", (f"{where}: no unambiguous external measurement, behavioral fit, or derivation establishes this numeric choice. "
                         "A purpose, inherited default, sweep setting, or governance preference alone does not establish its numerical basis."), "low", "yes"


def units(source, node, base, rationale):
    # Units are never guessed from a floating-point value or a suggestive name.
    known = {
        "SHRINKAGE_FLOOR": "% per step (value stored as fraction)",
        "SHRINKAGE_CRISIS": "% per step (value stored as fraction)",
        "GROWTH_ACTIVE": "% per step (value stored as fraction)",
        "TREND_SCALE": "% per step (value stored as fraction)",
        "PSI_INST_DECAY_RATE": "per step",
        "PSI_INST_OVERLOAD_DAMAGE": "per step",
    }
    return known.get(base, "")


def main():
    output_paths = [OUT / "parameter_register.csv", OUT / "parameter_register_summary.md",
                    OUT / "coverage_manifest.json"]
    if any(path.exists() for path in output_paths):
        raise FileExistsError("Create-only generator refuses to overwrite an existing artifact")
    paths = [path for path in (ROOT / "simulation").rglob("*.py")
             if "diagnostics" not in path.relative_to(ROOT / "simulation").parts
             and "tests" not in path.parts and not path.name.startswith("test_")
             and not path.name.endswith("_test.py") and path.name != "conftest.py"]
    paths += list((ROOT / "bootstrap_gate_validator").rglob("*.py"))
    sources = [Source(path) for path in sorted(paths)]
    readers = collections.defaultdict(set)
    for source in sources:
        import_aliases = {alias.asname or alias.name: alias.name
                          for node in ast.walk(source.tree) if isinstance(node, ast.ImportFrom)
                          for alias in node.names}
        for node in ast.walk(source.tree):
            symbol = None
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                symbol = import_aliases.get(node.id, node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
                symbol = node.attr
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("get", "setdefault"):
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    symbol = node.args[0].value
            if symbol:
                readers[symbol].add(source.rel + "::" + source.scope(node))

    records = []
    for source in sources:
        for node in sorted(source.numeric_nodes, key=lambda item: (item.lineno, item.col_offset)):
            label, lookup, base = source.label(node)
            signed = source.parents.get(node)
            value_node = signed if isinstance(signed, ast.UnaryOp) and isinstance(signed.op, (ast.USub, ast.UAdd)) else node
            records.append((source, node, label, lookup, base, source.segment(value_node), "literal"))
        for node in ast.walk(source.tree):
            nonfinite = (
                isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                and node.value.id in {"np", "numpy", "math"} and node.attr in {"inf", "nan"}
            ) or (
                isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "float" and len(node.args) == 1
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and node.args[0].value.lower() in {"inf", "+inf", "-inf", "infinity", "nan"}
            )
            numeric_string = (isinstance(node, ast.Constant) and isinstance(node.value, str)
                              and re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", node.value))
            if nonfinite or numeric_string:
                label, lookup, base = source.label(node)
                signed = source.parents.get(node)
                value_node = signed if isinstance(signed, ast.UnaryOp) else node
                records.append((source, node, label, lookup, base, source.segment(value_node),
                                "nonfinite" if nonfinite else "numeric_string"))
        symbols = {}
        for statement in source.tree.body:
            if isinstance(statement, (ast.Assign, ast.AnnAssign)) and statement.value is not None:
                targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                for target in targets:
                    if not isinstance(target, ast.Name):
                        continue
                    try:
                        value = constant_value(statement.value, symbols)
                    except (ValueError, KeyError, TypeError, ZeroDivisionError, OverflowError):
                        continue
                    symbols[target.id] = value
                    if type(value) in (int, float, complex) and not numeric(statement.value) and not isinstance(statement.value, ast.UnaryOp):
                        records.append((source, statement.value, target.id + ".expression", {target.id}, target.id,
                                        source.segment(statement.value) + " = " + repr(value), "expression"))
        # Named numeric defaults are call-site occurrences even without literals.
        for node in ast.walk(source.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("get", "setdefault") and len(node.args) > 1:
                default = node.args[1]
                if isinstance(default, ast.Name) and default.id.upper() == default.id:
                    label, lookup, base = source.label(default)
                    records.append((source, default, label, lookup | {default.id}, base, default.id, "alias"))

    # Run git grep itself, with fixed whole-word patterns. Match lines to each
    # identifier to retain all tracked docs/ and diagnostics Markdown references.
    query_names = sorted({name for _, _, _, names, _, _, _ in records for name in names
                          if re.fullmatch(r"[A-Za-z_]\w*", name) and name != "self"})
    references = collections.defaultdict(set)
    for start in range(0, len(query_names), 80):
        batch = query_names[start:start + 80]
        arguments = ["grep", "-n", "-I", "-w", "-F"]
        for name in batch:
            arguments += ["-e", name]
        found = git(*arguments, "--", "docs", "simulation/diagnostics/*.md")
        batch_set = set(batch)
        for line in found.splitlines():
            match = re.match(r"^(.*?):(\d+):(.*)$", line)
            if match:
                path, number, content = match.groups()
                for name in set(re.findall(r"[A-Za-z_]\w*", content)) & batch_set:
                    references[name].add(f"{path}:{number}")

    rows, metadata = [], []
    for source, node, label, lookup, base, value, kind in records:
        location = f"L{node.lineno}:C{node.col_offset + 1}"
        name = f"{label}@{location}" + (f"/{kind}" if kind != "literal" else "")
        rationale = source.rationale(node)
        refs = sorted({ref for symbol in lookup for ref in references[symbol]})
        rationale += " | git grep references: " + ("; ".join(refs) if refs else "none")
        scope = source.scope(node)
        use = {source.rel + "::" + scope}
        if scope == "<module>":
            use = set(readers.get(base, ()))
            if not use:
                use = {source.rel + "::<module> (no in-scope named reader found)"}
        elif base.startswith("self."):
            use |= {reader for reader in readers.get(base.split(".")[-1], ())
                    if reader.startswith(source.rel + "::")}
        # A config default can initialize self.x. Include later attribute
        # reads as well as the constructor that reads the default itself.
        assignment = next((ancestor for ancestor in source.ancestry(node)
                           if isinstance(ancestor, (ast.Assign, ast.AnnAssign))), None)
        if assignment is not None:
            targets = assignment.targets if isinstance(assignment, ast.Assign) else [assignment.target]
            for target in targets:
                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                    use |= {reader for reader in readers.get(target.attr, ())
                            if reader.startswith(source.rel + "::")}
        category, evidence, confidence, decision = classify(source, node, base, label, kind)
        row = dict(zip(FIELDS, (
            name, source.rel, node.lineno, value, units(source, node, base, rationale),
            "; ".join(sorted(use)), rationale, category, evidence, confidence, decision,
        )))
        rows.append(row)
        metadata.append(dict(file=source.rel, line=node.lineno, column=node.col_offset + 1,
                             kind=kind, name=name, base=base, scope=scope,
                             core=source.path.name in CORE_FILES))

    order = sorted(range(len(rows)), key=lambda i: (rows[i]["file"], rows[i]["line"], metadata[i]["column"], metadata[i]["kind"]))
    rows, metadata = [rows[i] for i in order], [metadata[i] for i in order]
    literal_keys = {(m["file"], m["line"], m["column"]) for m in metadata if m["kind"] == "literal"}
    expected_keys = {(s.rel, n.lineno, n.col_offset + 1) for s in sources for n in s.numeric_nodes}
    assert literal_keys == expected_keys
    assert len(literal_keys) == sum(m["kind"] == "literal" for m in metadata)
    assert len({(row["file"], row["name"]) for row in rows}) == len(rows)
    counts = collections.Counter(row["suggested_class"] for row in rows)
    decisions = sum(row["needs_operator_decision"] == "yes" for row in rows)
    priority = [(row, meta) for row, meta in zip(rows, metadata)
                if row["suggested_class"] == "arbitrary" and meta["core"]]
    summary = [
        "# Parameter provenance register", "",
        f"Read-only source snapshot: `{git('rev-parse', 'HEAD').strip()}` on `main`.", "",
        f"{len(rows)} occurrence records across {len(sources)} Python files: {len(expected_keys)} numeric literal occurrences, "
        f"{sum(m['kind'] == 'expression' for m in metadata)} computed named bindings, and "
        f"{sum(m['kind'] == 'alias' for m in metadata)} named fallback references, "
        f"{sum(m['kind'] == 'nonfinite' for m in metadata)} nonfinite sentinels, and "
        f"{sum(m['kind'] == 'numeric_string' for m in metadata)} numeric string constants.", "",
        "| Suggested class | Records |", "| --- | ---: |",
        *[f"| {category} | {counts[category]} |" for category in ("measured", "calibrated", "derived", "arbitrary")], "",
        f"Operator decision required: **{decisions}** records.", "",
        "## Coverage and interpretation", "",
        "Each numeric AST literal has a row, including defaults, seeds, sweep grids, tolerances, indices, "
        "plotting settings, counters, and neutral placeholders. Counts describe source occurrences, not independent "
        "scientific parameters. Repeated defaults and mirrors are intentionally not deduplicated. Signed literals "
        "retain their sign. Computed named bindings supplement their constituent literal rows. Named fallback "
        "references supplement definitions. Infinity/NaN expressions and numeric strings are separately tagged "
        "and included conservatively, including numerical-library thread settings and numeric labels. Booleans, "
        "version strings, format specifications, and numbers appearing only in prose are not numeric constants "
        "in this inventory. No comma-separated numeric argparse string defaults were found. External JSON or "
        "CSV configuration files require separate configuration provenance before a future batch.", "",
        "All non-test Python under simulation/ is included except simulation/diagnostics/. All bootstrap validator "
        "Python is included conservatively, including decision thresholds and extra report identifiers. Tests, "
        "conftest.py, and test directories are excluded. No source module was imported to build the register.", "",
        "The manifest records every source hash, literal location, supplemental row, and a zero-missing-literal "
        "coverage assertion. The generator uses exclusive creation and refuses existing outputs.", "",
        "Names end with original source line and 1-based UTF-8 AST byte column, making anonymous literals and "
        "duplicate names unambiguous. Value cells retain source spelling. used_in records the enclosing reader "
        "and indexed direct symbol readers for module constants, including imported aliases. This is static "
        "name-based evidence, not a whole-program dynamic call graph. Unused, legacy, and retired constants remain "
        "visible. Module initialization is explicitly identified when no named reader is found.", "",
        "Comments and enclosing docstring excerpts are quoted losslessly as JSON strings. Decode escapes to recover "
        "the original wording, including source Unicode punctuation. This preserves quotes without introducing "
        "literal em dash characters into these artifacts. Every tracked git grep whole-word name reference in "
        "docs/ and simulation/diagnostics/*.md is included as path:line. A mention is not proof of calibration. "
        "Blank units mean no units confidently stated for that constant.", "",
        "No row is measured: H_N_V_REF is a measurement of simulated baseline behavior, so it is calibrated, "
        "not an external empirical measurement. H_N_V_PROJ_K is a fitted simulation projection coefficient. "
        "STATE_ALLOCATION_MAPPING coefficients are explicitly provisional behavioral tuning, with operator "
        "review retained. All ambiguous choices remain arbitrary. Derived rows explain their arithmetic or "
        "structural basis; a derived row can still depend on arbitrary inputs.", "",
        "## Proposed sensitivity analysis", "",
        "1. Resolve the operator-decision rows before certifying a v3 parameter set. Separate free choices "
        "from identities, counters, output settings, and inactive legacy mechanisms. Do not perturb duplicated "
        "live and projection constants independently.",
        "2. Objective: jointly sweep lambda_n, lambda_e, epsilon and LAMBDA_LINEAGE_COUPLING; compare novelty "
        "and scarcity marginals at fixed L and total derivatives through L. Include H_N_FLOOR, H_E_BASE_FLOOR, "
        "H_E_COMPUTE_SAT_K, the 0.01 factor floors, population scaling 200, viability limits 0.1 and 5.0, "
        "rho, and legacy phi/h_e_multiplier where that path is in scope.",
        "3. Survival: reproduction_rate, carrying_capacity, min_viable_population, wb_repro_floor/threshold, "
        "mortality_base, mortality_wb_penalty, mortality_age_power, age scale 100, reproductive ages 18 and 50, "
        "well-being resource pivot 0.5, gain 0.1 and age drag 0.001, newborn well-being/age bounds, "
        "novelty propensities, network-contagion factors, and shock settings.",
        "4. Infrastructure and succession: ALPHA_DEFAULT, FRONTIER_FLOOR, RUNAWAY_THRESHOLD, "
        "CONVERGENCE_STRENGTH, initial stocks, PSI_INST_* and SUCCESSION_* choices, transition-cost defaults, "
        "successor capability growth/cap, opacity parameters, and the welfare bridge. Review calibrated "
        "STATE_ALLOCATION_MAPPING rates and targets too; calibration does not remove sensitivity risk.",
        "5. Policy and defenses: candidate counts, Dirichlet concentrations, constraint grid and anchors, "
        "LEAKAGE_K, rollout horizon and gamma parameters, defense/attack thresholds, trust/CUSUM settings, "
        "and G2.3 tolerance. Label attack-specific and inactive Stage 1.5 coefficients separately.",
        "6. Only after certification, specify ranges and paired seeds in a separate authorized experiment. "
        "This task ran no simulations and proposes no empirical sensitivity conclusions.", "",
        "## Arbitrary choices with direct current-v2 relevance", "",
        "These are the primary named choices and inline coefficients to review first. Source locations, "
        "exact occurrences, readers, and evidence appear in the CSV and the exhaustive table below. "
        "A family name here refers to all of its registered elements, not a new independent parameter.", "",
        "| Mechanism | Arbitrary choices and current values |", "| --- | --- |",
        "| Per-step objective | lambda_n=5, lambda_e=3, epsilon=1e-6, rho=0.01, LAMBDA_LINEAGE_COUPLING=10; H_E_COMPUTE_SAT_K=2.5, H_E_BASE_FLOOR=0.05, H_N_FLOOR=0.01; population scale 200 and viability limits 0.1 and 5; h_eff, psi_inst, theta_tech and bandwidth floors 0.01. |",
        "| Novelty generation and measurement | NOVELTY_DIMS=10 in both modules; H_N_MAGNITUDE_SAT_K=3; covariance eigenvalue floor 1e-9; nov_prop_min=0.05, nov_prop_max=0.5; Gaussian loc=0, scale=1; contagion floor 0.1 in the agent and clipping 0.5 to 2 in the model; LEAKAGE_K and LEAKAGE_K_LOCAL=0.35, protective leakage exponent 2. |",
        "| Biological survival | reproduction_rate=0.08, carrying_capacity=1600, min_viable_population=50; wb_repro_threshold=wb_repro_floor=0.5; mortality_base=0.002, mortality_wb_penalty=0.05, mortality_age_power=4, age denominator 100; reproductive ages 18 and 50; resource pivot 0.5, well-being gain 0.1, age drag 0.001; human_max_start_age=50, wb_min=0.5, wb_max=0.8. |",
        "| Welfare and initial stocks | BRIDGE_R_MIN=0.1, BRIDGE_R_MAX=1 and agent mirrors; PSI_INST_INITIAL=0.5, RESILIENCE_STOCK_INITIAL=0.30, THETA_CAPABILITY_INITIAL=TRANSFER_STATE_INITIAL=0.5. The balanced bridge anchor is calibrated and the 1/6 share is derived. |",
        "| Capability and lineage transfer | FRONTIER_FLOOR=0.02, RUNAWAY_THRESHOLD=1.5, ALPHA_DEFAULT=1, CONVERGENCE_STRENGTH=1; max_capability=1e100, successor_capability_growth_rate=1.5; base_transition_cost=1.5, k2_transition=1, beta_transition=0.5; transition-cost psi floor 0.01. k1_transition=2.164 is separately classified as derived. |",
        "| Succession stock damage | SUCCESSION_BASE_LOAD=0.10, SUCCESSION_CAPABILITY_GAP_FACTOR=0.05, SUCCESSION_GENERATION_GAP_FACTOR=0.03, SUCCESSION_OPACITY_FACTOR=0.05, SUCCESSION_PSI_BUFFER_K=0.5, SUCCESSION_TRANSFER_BUFFER_K=0.3, SUCCESSION_RESILIENCE_BUFFER_K=0.2. |",
        "| Shocks | shock_step=0 (disabled by default), shock_magnitude=0.15, RESILIENCE_MAX_ATTENUATION=0.7, K_RESILIENCE_CONSUMPTION=1.5; post-shock well-being floor 0.01, kill-fraction multiplier 0.2 and cap 0.8, shock seed offset 100000. |",
        "| Policy objective and exploration | phi=25, GAMMA_MIN=0.5, GAMMA_MAX=0.95, PHI_HALF=10, rollout_steps_v2=20, n_candidates_v2=300; stratified counts N_UNIFORM_DIRICHLET=100, N_BALANCED_DIRICHLET=100, N_SINGLE_FOCAL_SPARSE=60, N_DUAL_FOCAL_SPARSE=20, N_ANCHORS=20; ALPHA_UNIFORM, ALPHA_BALANCED, ALPHA_FOCAL_HIGH/LOW, ALPHA_DUAL_HIGH/LOW, CONSTRAINT_GRID_VALUES, and all ANCHOR_ALLOCATIONS elements. |",
        "| Conditional adversarial paths | attack_adapter_v2 thresholds, fabricated payoff values, suppression/opacity changes, capture controls, and defection default weights/bonuses; each occurrence is registered with its reader. These depend on attack and defense configuration. |", "",
        "Stage 1.5 composite urgency coefficients and legacy PSI_INST_* update rates remain registered but "
        "are retired from the current v2 state-update path. They must not be mistaken for active v2 factors. "
        "Trends are still recorded; the retired urgency layer no longer routes them into per-step U_sys. "
        "The active STATE_ALLOCATION_MAPPING rates and targets are provisionally calibrated, not arbitrary.", "",
        "## Arbitrary constants on objective and survival code paths", "",
        f"The following exhaustive conservative review list contains {len(priority)} arbitrary occurrences from "
        "metrics, agents, model, working-factor, constants, attack-adapter, and defection modules. It includes "
        "direct objective coefficients, survival dynamics, policy/projection influences, retired paths and "
        "bookkeeping in those same modules. Inclusion does not claim every literal is active in default v2. "
        "Review used_in in the CSV before assigning an experimental factor.", "",
        "| File and line | Name | Value | Reader |", "| --- | --- | --- | --- |",
    ]
    for row, meta in priority:
        value = row["value"].replace("|", "\\|").replace("\n", " ")
        summary.append(f"| {row['file']}:{row['line']} | `{row['name']}` | `{value}` | `{meta['scope']}` |")
    manifest = dict(
        code_identity=git("rev-parse", "HEAD").strip(), files=[
            dict(path=source.rel, sha256=hashlib.sha256(source.path.read_bytes()).hexdigest(),
                 numeric_literal_occurrences=len(source.numeric_nodes)) for source in sources
        ], rows=len(rows), counts_by_class={key: counts[key] for key in ("measured", "calibrated", "derived", "arbitrary")},
        needs_operator_decision=decisions, missing_numeric_literals=0, duplicate_literal_locations=0,
        git_grep_names=query_names, occurrences=metadata,
    )
    assert all("\u2014" not in str(value) for row in rows for value in row.values())
    assert "\u2014" not in "\n".join(summary)
    with output_paths[0].open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with output_paths[1].open("x", encoding="utf-8") as handle:
        handle.write("\n".join(summary) + "\n")
    with output_paths[2].open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=True)
        handle.write("\n")
    print(json.dumps({key: manifest[key] for key in ("rows", "counts_by_class", "needs_operator_decision", "missing_numeric_literals")}))


if __name__ == "__main__":
    main()
