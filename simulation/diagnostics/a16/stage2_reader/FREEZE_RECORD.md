# Stage 2 sealed readers: freeze record (D section 8.4)

- **FREEZE_RECORD.json sha256:** `6d2262fe596538c92b90a58d015e7c5d51064694dd79e1346b764724f467c705` [M]
- **Seal** (the JSON's `sha256` field, `v3.artifacts.digest(payload)`): `cc9cfc741a2e4e46d0814ddbd8d013caab2794e5bba3bc02999b01ebd92d8588` [M]
- **Form:** `canonical(seal(payload)) + "\n"`, native `v3.artifacts` from `R/simulation/`, 944211 bytes. Schema `a10-stage2-freeze-record-1`.
- **Assembled** 2026-11-23 by the interpreter's executor, per S/freeze/BRIEF.md. Brief sha256 `10767048812c147f9fa0da7945b9521358178c88113a06b9296028f572d7fe73`.
- **Path roots:** `S` is the interpreter's stage 2 reader record folder; `R` is the interpreter's clone at 4dcc18c2; `BA` is builder A's WSL area; `BB` is builder B's WSL area.
- **Repair:** this version applies the second check's findings 1 to 5 (`S/freeze/check/REPORT.md`): neutral assembly and source labels, path roots in place of absolute paths, and one labelled date. No hash, identity, registry entry, fixture outcome or comparison result changed.
- **Labels:** [M] measured (hashed or computed by the assembler); [R] read from the named source; [I] inferred. This file is the human rendering of the JSON. Three things are given here by digest or table and in full only in the JSON: each fixture's `reference` and `screens` blocks (by `v3.artifacts.digest` and key names), and the two raw registry exports (by digest, with their content as tables).
- **Written before any stage 2 output is read.** The assembler opened no registered output, root, inventory, table or reading, and no fixture output.

## 1. The specification set

| # | Document | sha256 [M] |
|---|---|---|
| 1 | `STAGE2_READER_SPEC_DRAFT.md` | `3ac0f425cd2b1f27c31a6cf0b757a7ba9e62515ab128a85049f3c5a33d835822` |
| 2 | `ADDENDUM_1.md` | `f1a26843212351823b4a940d5b5b94536282f414cd7587998bb887139a81f103` |
| 3 | `ADDENDUM_2.md` | `74f7c0a6b7023122457a42a2ea32358d4b8aa8ca9dfc7330830415c3daea2edc` |
| 4 | `ADDENDUM_3.md` | `e660247842db524f7241e40fe46dc1c59ee2208eb3106b5d31ff335dbe16a014` |
| 5 | `ADDENDUM_4.md` | `f0dce64b38b3f313d0e0618cd8328ddc69f9ea4620312c32b4b40edf02a97b85` |
| 6 | `ADDENDUM_5.md` | `b2b924d488a9d7732279ee2b7c67ec232fb0627d05cf3c1140ce83baac3ea388` |
| 7 | `ADDENDUM_6.md` | `6d6ea4a31f0412d1117415e982e974aeaa92b6e837a92b7522123f66979dec13` |
| 8 | `ADDENDUM_7.md` | `19983112126fb0aa9f0b559c3227facab8227aea433fa70d85129c97846448f8` |
| 9 | `ADDENDUM_8.md` | `a795fb12cdfe65c98a49d06448d021cf0e39dadd01e86e13d72709fb40221dff` |
| 10 | `ADDENDUM_9.md` | `01b42ad319dd2565e8b39da946704dc4345227f3e2717af80e52ec08d3707927` |
| 11 | `ADDENDUM_10.md` | `132956131d2faf87db4f7a3132bd05f2c27497b37e5f950a12980fcd8ea237f5` |
| 12 | `ADDENDUM_11.md` | `0389f2e99b6211a9b4c1a92ed4f7cb1ed86f8752ae7df45f9a57c2cb244ae34d` |

Addendum 6 is ADDENDUM_6.md only (its _v* working copies are excluded). Addenda 10 and 11 are the specification-set texts S/spec/ADDENDUM_10.md and S/spec/ADDENDUM_11.md.

- **REQ:** `R/simulation/diagnostics/a16/STAGE2_READER_REQUIREMENTS.public.md`, sha256 `685f05ec58cb2bb84914163de57107ee4f3e557650d7717e1c1a2e8be56a52d5` [M].
- **The set's digest:** `e790201f6060fa2ef8b30f668b834f16be364fefb91583298987b4d17452bd8a` [M]. Definition: v3.artifacts.digest of the ordered list of {name, sha256}: the draft, then Addenda 1 to 11.
- **Cross-checks [M]:** the draft matches `3ac0f425...5822` as cited by A10 and A11; A6 `6d6ea4a3...ec13`, A8 `a795fb12...1dff` and A9 `01b42ad3...7927` as cited by A10; A10 `13295613...37f5` as cited by A11; A11 `0389f2e9...e34d` as cited by DECISIONS s15 and builder A's round 2 report.
- **Packaged manifest [R/M]:** the packaged fixture manifest lists 10 documents (draft and Addenda 1 to 9), each at the sha256 above, digest 3bedd32b30c925667a989115e129c796a100adffe96d86e220dd5555f6e9dd1b. A10.9 item 1 and A11.4 item 1 add Addenda 10 and 11 at the next regeneration; no per-fixture list hash moves.

## 2. The readers

### Checkout and environment (both readers)

- **Commit:** `4dcc18c2a08026c56984e8f7faadaa7ef791fe2b` [M] git rev-parse HEAD with GIT_OPTIONAL_LOCKS=0 in R.
- **`code_identity()`:** `93a453b27c82a9cb16ed0d04b1029168014b73c1f3d97f5b884e1b6d52f161da` [M] v3.artifacts.code_identity() in R.
- **Python** 3.13.12, **NumPy** 2.4.4, [M] platform.python_version() and numpy.__version__ in the WSL Ubuntu-20.04 phaseb environment (the phaseb environment's python).

### Reader A

- **Identity:** `1c0fca4593af45918d405508cdab9ac01632bec50df97a762ae119f9adffea1d` [M], by `reading_stage2_a.common.identity()` from the copy in R, R/simulation/reading_stage2_a/. Expected `1c0fca45...ea1d`: matches. Equals the `reader_identity` of the build's results file: yes.
- **Definition (one line):** sha256 of v3.artifacts.canonical({"role": "A", "files": {package-relative POSIX path: sha256 of raw bytes}}) over every *.py found recursively (rglob) in the package; no newline.
- **Package:** `BA/repo/simulation/reading_stage2/`, 13 `*.py` files [M]. Copy in R: `R/simulation/reading_stage2_a/`, equal file list and hashes: yes [M]. The identity's file map equals the tree's hashes: yes [M]. No non-`.py` file and no `__pycache__` in either tree [M].

| File | sha256 [M] (builder tree = R copy) |
|---|---|
| `__init__.py` | `3fa1fe58eea9d4480958a24277e256a9a0ddfdf7c87b77c2488d5abb6316777d` |
| `__main__.py` | `3f6030fda10ae52cce565d477e58ea4fca97cdf7d853339a04fbe9d25a2657ce` |
| `collection.py` | `1b54da3ce52d480deebc9b8bcd544bac5c5837e7ecc864405b4ad93b2b454cd3` |
| `common.py` | `6e9e6c175721183bc0f17d1d48e5a6f5131fabda79a378f8b1202d3a12b5c776` |
| `comparison.py` | `24876c765fb156243d55aa739b6c87dccbc719944683e1236e5cf50e921c255a` |
| `contracts.py` | `844bdbfe2797b9649ebd8bb78800d1b8b07df413e171c93b18d9daa544ad4250` |
| `families.py` | `e7b6ea1a8c16f528ed8963f63f43804fba022b8a095978bab9b883c0aef5093f` |
| `incidence.py` | `6a9820d6867ee2ace67e8b44352a4b85df9e2b7740f3fb1d0e41b2496b239aa6` |
| `io.py` | `9dfc0448b4b40eeea600588e5ed8b8d6f9c0d99833f8b61995782dccc8663648` |
| `ladder.py` | `d0feb7caba57dc81cf3592230180dde7caf21a3bec4e15a909dcf424ce9f7b24` |
| `reader.py` | `d96e150f7202677b2f35c2ee4b196d2e03647149d3447f37f66f511655225f89` |
| `refusal.py` | `12972ffb89152ca7117d467e79135a503b4ca390234bb8716e0027aa4875cc10` |
| `registry.py` | `144b6583035ee8bd2004166a5e1ba2f2b12e198710e5f3e783268864ee46086c` |

**Tools** (`BA/repo/simulation/reading_stage2_tools/`, all files) [M]. Equal to the results file's `tools` block: yes.

| Tool | sha256 [M] | In R copy `R/simulation/reading_stage2_tools_a/` |
|---|---|---|
| `byte_identity.py` | `26cc37648f9b826fd6665f836d0248d97f0648261bee6e0f85de353081982554` | equal |
| `ladder.py` | `901604915a23ea43e2576b4b4ecf2deeee68cd26f11189b538e1b5ce2b61e167` | absent |
| `stream_checker.py` | `b461a437b5d294a4d217d3c84d1c01c3e2124f60ca41fab22a7c5bbf124ef71c` | absent |
| `values_compare.py` | `1bbd6a8f304589a251677843be88decc65893b1c971ff8af5c0807fdaace605d` | absent |

The R copy holds byte_identity.py only, at the same sha256 as the builder's. The other three tools exist only in the builder's clone. [M]

**Copied-module table (D section 7).** Stage 1 source: builder A's stage 1 tree, `simulation/reading_a10/`.

[M] common.py and refusal.py are the copied modules. Neither is identical to its stage 1 source; the unified diff of each is recorded. No other file is byte-identical to any stage 1 file. Same-named __init__.py, __main__.py, incidence.py and reader.py are new code (whole-file line ratio 0.000, 0.109, 0.049, 0.019) [I].

[M] every top-level function and class of the frozen package (R copy) was matched by name and by line-level difflib ratio against every top-level definition of the stage 1 *.py files directly in reading_a10/. Whole files with a stage 1 file of the same name were compared byte for byte. A definition is listed as adapted when its best stage 1 match has a line ratio of at least 0.5 under another name or another file, or shares a name and was evidently adapted [I]; all others are new code [I].

| Frozen | Stage 1 source | Result | Stage 1 sha256 | Frozen sha256 |
|---|---|---|---|---|
| `common.py` (module) | `reading_a10/common.py` | differs, diff below | `63243a1c66d966889281e036135fbaa4d5669759fc0f8f5f64e34f8ba93caa19` | `6e9e6c175721183bc0f17d1d48e5a6f5131fabda79a378f8b1202d3a12b5c776` |
| `refusal.py` (module) | `reading_a10/refusal.py` | differs, diff below | `b5caf67234f561496de33c2ba69041f3d607ccdd57f4fe33f4ccae381a8a5ba8` | `12972ffb89152ca7117d467e79135a503b4ca390234bb8716e0027aa4875cc10` |

Unified diff, `common.py` against stage 1 [M]:

```diff
--- stage1/A/reading_a10/common.py
+++ stage2/reading_stage2_a/common.py
@@ -5,6 +5,7 @@
 import os
 from pathlib import Path
 import tempfile
+from v3.artifacts import canonical as native_canonical, seal as native_seal
 
 
 class Refusal(ValueError):
@@ -17,7 +18,7 @@
 
 
 def canonical(obj):
-    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()
+    return native_canonical(obj)
 
 
 def digest(obj):
@@ -33,7 +34,7 @@
 
 
 def seal(payload):
-    return {"payload": payload, "sha256": digest(payload)}
+    return native_seal(payload)
 
 
 def unseal(doc):
@@ -66,10 +67,11 @@
 
 def safe(obj):
     if isinstance(obj, float) and not math.isfinite(obj):
-        require(not math.isnan(obj), "NaN result")
+        if math.isnan(obj):
+            return "nan"
         return "+inf" if obj > 0 else "-inf"
     if isinstance(obj, dict):
-        return {str(k): safe(v) for k, v in obj.items()}
+        return {repr(k) if isinstance(k, float) else str(k): safe(v) for k, v in obj.items()}
     if isinstance(obj, (list, tuple)):
         return [safe(v) for v in obj]
     if hasattr(obj, "item"):
@@ -77,94 +79,34 @@
     return obj
 
 
-def write(path, value):
-    """Atomic publication; identical existing bytes are allowed, replacement isn't."""
+def write(path, value, *, preserve_on_failure=False):
+    """Atomic JSON write; existing targets are never replaced."""
+    write_bytes(path, canonical(safe(value)) + b"\n", preserve_on_failure=preserve_on_failure)
+
+
+def write_bytes(path, data, *, preserve_on_failure=False):
+    """Publish prepared bytes, retaining publication debris when A11.1 requires it."""
     path = Path(path)
-    data = canonical(safe(value)) + b"\n"
     path.parent.mkdir(parents=True, exist_ok=True)
     if path.exists():
-        require(path.read_bytes() == data, "frozen analysis target: " + str(path))
-        return
+        raise Refusal("output target exists")
     fd, name = tempfile.mkstemp(prefix=".a10-", dir=path.parent)
     try:
         with os.fdopen(fd, "wb") as stream:
             stream.write(data)
             stream.flush()
             os.fsync(stream.fileno())
-        os.link(name, path)
+        os.rename(name, path)
     finally:
-        os.unlink(name)
+        if not preserve_on_failure and os.path.exists(name):
+            os.unlink(name)
 
 
-def identity(role="reader"):
+def identity(role="A"):
     root = Path(__file__).parent
     # Whole package is the analysis identity; role is separately bound. Tests and
     # documentation do not execute in a reading and are excluded explicitly.
-    files = {p.name: file_hash(p) for p in sorted(root.glob("*.py"))}
+    files = {p.relative_to(root).as_posix(): file_hash(p) for p in sorted(root.rglob("*.py"))}
     return {"role": role, "sha256": digest({"role": role, "files": files}), "files": files}
 
 
-def cell_of(row):
-    return tuple(row[k] for k in ("category", "rr", "alpha", "capability"))
-
-
-def cell_id(cell):
-    return "|".join(str(v) if isinstance(v, str) else repr(v) for v in cell)
-
-
-TAIL_REASON = "The registered runs did not record the tail-standard diagnostic; no value is reconstructed."
-
-
-class Ledger:
-    def __init__(self, base):
-        self.base = Path(base).resolve()
-        self.files = {}
-        self.producers = {}
-
-    def path(self, value):
-        p = Path(value).expanduser()
-        return (self.base / p).resolve() if not p.is_absolute() else p.resolve()
-
-    def load(self, value, expected=None):
-        path = self.path(value)
-        raw = path.read_bytes()
-        sha = hashlib.sha256(raw).hexdigest()
-        require(expected is None or expected == sha, "input hash: " + str(path))
-        entry = {"sha256": sha, "bytes": len(raw)}
-        require(str(path) not in self.files or self.files[str(path)] == entry, "input changed while reading")
-        self.files[str(path)] = entry
-        value = loads(raw)
-        fields = {}
-        def visit(item, prefix=""):
-            if isinstance(item, dict):
-                for key, child in item.items():
-                    name = prefix + "/" + key
-                    if key in ("code_hash", "producer_code_hash", "source_code_hash", "a1_source_code_hash") and isinstance(child, str):
-                        fields[name] = child
-                    visit(child, name)
-            elif isinstance(item, list):
-                for i, child in enumerate(item):
-                    visit(child, prefix + "/" + str(i))
-        visit(value)
-        self.producers[str(path)] = fields
-        return value
-
-    def verify(self):
-        for path, entry in self.files.items():
-            require(file_hash(path) == entry["sha256"], "input changed: " + path)
-
-    def protect_output(self, out, roots):
-        out = Path(out).resolve()
-        for root in roots:
-            require(not out.is_relative_to(self.path(root)), "output overlaps an input root")
-        require(str(out) not in self.files, "output overlaps an input file")
-
-
-def protect_destination(inputs_path, out):
-    """Check write locations using path metadata before even temporary writes."""
-    ledger = Ledger(Path(inputs_path).resolve().parent)
-    config = ledger.load(Path(inputs_path).resolve())
-    roots = [d["root"] for d in config["components"].values()] + [config["r4"]["root"]]
-    roots += [config["nominal"][k] for k in ("a4_root", "a5_root", "source") if k in config["nominal"]]
-    roots += [d["root"] for d in config.get("amendments", {}).values() if "root" in d]
-    ledger.protect_output(out, roots)
```

Unified diff, `refusal.py` against stage 1 [M]:

```diff
--- stage1/A/reading_a10/refusal.py
+++ stage2/reading_stage2_a/refusal.py
@@ -5,7 +5,7 @@
 from pathlib import Path
 from .common import Refusal
 
-_state = ContextVar("reading_a10_refusal_phase", default=None)
+_state = ContextVar("stage2_refusal_phase", default=None)
 
 
 def invocation(function):
@@ -15,7 +15,7 @@
         token = _state.set(state)
         try:
             return function(*args, **kwargs)
-        except Exception as exc:
+        except BaseException as exc:
             exc.reading_phase = state["phase"]
             raise
         finally:
@@ -42,19 +42,14 @@
                          node.args[0] if node.func.id == "Refusal" and node.args else None)
                 if isinstance(label, ast.Constant) and isinstance(label.value, str):
                     messages.add(label.value)
-    from .authorization import HASH_KEYS, PATH_KEYS
-    from .provenance import COMPONENTS
-    messages.update("full authorized hash required: " + key for key in HASH_KEYS)
-    messages.update("authorized path required: " + key for key in PATH_KEYS)
-    messages.update("approved " + key + " hash" for key in HASH_KEYS)
-    messages.update("authorized R4 " + key + " path" for key in ("root", "gates", "index"))
-    messages.update(prefix + name for prefix in ("wrong producer: ", "incomplete cell grid: ", "cell seed count: ",
-                    "registered job family differs from C19 builder: ") for name in (*COMPONENTS, "r4"))
     return messages
 
 
 def reason(exc):
     message = str(exc)
+    if getattr(exc,'reading_phase',None)=='after_computation_started':
+        permitted={'input changed','output target exists','reader source changed','excluded root inventory key','helper cell selection'}
+        return message if isinstance(exc,Refusal) and message in permitted else 'computation failed'
     if isinstance(exc, Refusal):
         if message in check_messages():
             return message
@@ -67,13 +62,14 @@
     tb = exc.__traceback__
     while tb is not None:
         module = tb.tb_frame.f_globals.get("__name__", "")
-        if module.startswith(("reading_a10.", "v3.")):
+        if module.startswith((__package__ + ".", "v3.")):
             frames.append((module, tb.tb_frame.f_code, tb.tb_lineno))
         tb = tb.tb_next
     if not isinstance(exc, (Refusal, OSError, KeyError, TypeError)) and frames:
         module, code, line = frames[-1]
         source = Path(code.co_filename).resolve()
-        native = Path(__file__).resolve().parent.parent / "v3"
+        from v3.artifacts import ROOT
+        native = ROOT.resolve()
         if module.startswith("v3.") and source.parent == native and source.suffix == ".py":
             for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
                 if isinstance(node, ast.Raise) and node.lineno <= line <= node.end_lineno:
@@ -88,9 +84,6 @@
                 "file operation failed" if isinstance(exc, OSError) else
                 "required key absent" if isinstance(exc, KeyError) else
                 "invalid input type" if isinstance(exc, TypeError) else "check failed")
-    if frames:
-        module, code, _ = frames[-1]
-        category += " at " + module + "." + code.co_qualname
     return category
 
 
@@ -98,4 +91,4 @@
     phase = getattr(exc, "reading_phase", "input_verification")
     if phase not in ("input_verification", "after_computation_started"):
         phase = "input_verification"
-    return {"label": "refused", "reason_class": reason(exc), "phase": phase}
+    return {"status": "refused", "reason_class": reason(exc), "phase": phase}
```

### Reader B

- **Identity:** `2ad63b7a9b07abb43309b656085890de32b752946be66ac5c2a7672f62bc72db` [M], by `reading_stage2_b.base.reader_identity()` from the copy in R, R/simulation/reading_stage2_b/. Expected `2ad63b7a...72db`: matches. Equals the `reader_identity` of the build's results file: yes.
- **Definition (one line):** sha256 of v3.artifacts.canonical({file name: sha256 of bytes with CRLF normalized to LF}) over every *.py directly in the package directory; role "B" is returned beside the hash and is not hashed.
- **Package:** `BB/repo/simulation/reading_stage2/`, 10 `*.py` files [M]. Copy in R: `R/simulation/reading_stage2_b/`, equal file list and hashes: yes [M]. The identity's file map equals the tree's hashes: yes [M]. No non-`.py` file and no `__pycache__` in either tree [M].

| File | sha256 [M] (builder tree = R copy) |
|---|---|
| `__init__.py` | `49e2f9c0c9645661ad18c63deed14e4c269f1975bc10cb94e2d0ab0942edb473` |
| `__main__.py` | `3b5b04c476bac17279e3db571d2991653352396b8e9520e537c17fa032542b4b` |
| `base.py` | `2c01be0bcc8b5f4c0425ec79757a7bd99fb058cbab1201784c0f31361d7037f4` |
| `common.py` | `1dda122fa916962e572b2aea5f01313b4b084ecdd4b4f1d0ad07e6b0c9ddbb40` |
| `compute.py` | `568de9f23d8af2c58a707779cd3d4a35767a8f1c13a2ad024d123cc9e9764bb8` |
| `gates.py` | `749d900547eed483f89e86c57ba6209ee66d43b73a450c27347722c0ed39419a` |
| `incidence.py` | `b3c20c48a849176113756c4ad0c9056814fd2f86b5e16f901a57be278b220c9f` |
| `inputs.py` | `62eb75c48dbffc8596d577951886d5a5c801bb99aad719386eb2313079acce85` |
| `labels.py` | `de58bbb1a6f7285445a6b8e937b4170d59e12d999cc0f3fe734512fbe38bf100` |
| `registry.py` | `09599dde3807951c212a127ae09ab7cfd3d0957903c6e855796d1a3e3ad46368` |

**Tools** (`BB/repo/simulation/reading_stage2_tools/`, all files) [M]. Equal to the results file's `tools` block: yes.

| Tool | sha256 [M] | In R copy `R/simulation/reading_stage2_tools_b/` |
|---|---|---|
| `byte_identity.py` | `e3df84fe34f6ce8de755185b8dbd724d244f669c70ec68445e32a447115d398f` | equal |
| `ladder_tool.py` | `e7a939826bbbf396591d28f1e14a8d64fdd1c1e305b6fd93ddd36d998333c75a` | absent |
| `stream_check.py` | `10c5be871a929582c1dc447ebab67e9f41fbe035905aebc4bf39961aeb2583a4` | absent |
| `values_compare.py` | `1851add7c9db093800ad18aa2ef3f0af0bb4c685f8dd72ed901e7867fcec4264` | absent |

The R copy holds byte_identity.py only, at the same sha256 as the builder's. The other three tools exist only in the builder's clone. [M]

**Copied-module table (D section 7).** Stage 1 source: builder B's stage 1 tree, `simulation/reading_a10/`.

[M] common.py is identical to its stage 1 source. Four functions in other files were adapted from stage 1 definitions: compute.wilson (from against_v2.wilson; only the docstring differs), base.sealed (from common.unseal, renamed, label made required, docstring added), incidence.validate (from incidence.validate, narrowed per A10.8 item 2), base.reader_identity (from reading.reader_identity, file names relative to the package directory, role returned). Each diff is recorded, with both texts. Same-named __init__.py, __main__.py, incidence.py and inputs.py are otherwise new code (whole-file line ratio 0.378, 0.135, 0.142, 0.006) [I].

[M] every top-level function and class of the frozen package (R copy) was matched by name and by line-level difflib ratio against every top-level definition of the stage 1 *.py files directly in reading_a10/. Whole files with a stage 1 file of the same name were compared byte for byte. A definition is listed as adapted when its best stage 1 match has a line ratio of at least 0.5 under another name or another file, or shares a name and was evidently adapted [I]; all others are new code [I].

| Frozen | Stage 1 source | Result | Stage 1 sha256 | Frozen sha256 |
|---|---|---|---|---|
| `common.py` (module) | `reading_a10/common.py` | identical | `1dda122fa916962e572b2aea5f01313b4b084ecdd4b4f1d0ad07e6b0c9ddbb40` | `1dda122fa916962e572b2aea5f01313b4b084ecdd4b4f1d0ad07e6b0c9ddbb40` |
| `compute.py:80-87 wilson` (function) | `reading_a10/against_v2.py:22-28 wilson` | adapted, diff below, line ratio 0.800 | `7be8fc250c0de42b172c571eb52f77c25d8a5a205dd4750bf2eccba98c7d0135` (text) | `08ff5b52280e7e858776abde0a07b5bb85ca341cae73a8f01c28608cabff618d` (text) |
| `base.py:118-122 sealed` (function) | `reading_a10/common.py:45-48 unseal` | adapted, diff below, line ratio 0.667 | `af5ff3e4db9bef53e70cfada147ea920e5e7590a03684d670797623ee2d4b0f8` (text) | `ba9c79448d66c152943629e8ddd6e67865a9aa4d0ac88a29c6379d262f744110` (text) |
| `incidence.py:69-83 validate` (function) | `reading_a10/incidence.py:116-135 validate` | adapted, diff below, line ratio 0.400 | `a69aed3cda04fc7a72ce4e191a5b803c4fd0832c3005e508f3aeb2f5a116b132` (text) | `516495b9de2e9871fe5fb84e57780e3c77d6076efba28d61279d434523c73007` (text) |
| `base.py:24-33 reader_identity` (function) | `reading_a10/reading.py:24-27 reader_identity` | adapted, diff below, line ratio 0.143 | `d4adfc68fe7b464f5cf63a5d5358dd5680e9f7525859d9918a11b50df52733ac` (text) | `9fbc3e0b72cf8ed1733e8c0b5ac4208f9f7503051b69d35d0191bb8e7ca6aa29` (text) |

Unified diff, `compute.py:80-87 wilson` against stage 1 `against_v2.py:22-28 wilson` [M]:

```diff
--- stage1/B/reading_a10/against_v2.py:22-28 wilson
+++ stage2/reading_stage2_b/compute.py:80-87 wilson
@@ -1,5 +1,6 @@
 def wilson(count, n):
-    """Section 8's Wilson interval at z = 2, as main_read.wilson."""
+    """Section 8's Wilson interval at z = 2 (D:511; the stage 1 reader's
+    ``against_v2.wilson``, copied)."""
     p = count / n
     d = 1 + 4 / n
     center = (p + 2 / n) / d
```

Unified diff, `base.py:118-122 sealed` against stage 1 `common.py:45-48 unseal` [M]:

```diff
--- stage1/B/reading_a10/common.py:45-48 unseal
+++ stage2/reading_stage2_b/base.py:118-122 sealed
@@ -1,4 +1,5 @@
-def unseal(document, label="seal"):
+def sealed(document, label):
+    """A sealed document's payload; the seal is verified."""
     require(isinstance(document, dict) and set(document) == {"payload", "sha256"}, label)
     require(digest(document["payload"]) == document["sha256"], label)
     return document["payload"]
```

Unified diff, `incidence.py:69-83 validate` against stage 1 `incidence.py:116-135 validate` [M]:

```diff
--- stage1/B/reading_a10/incidence.py:116-135 validate
+++ stage2/reading_stage2_b/incidence.py:69-83 validate
@@ -1,20 +1,15 @@
-def validate(value, *, required):
-    require(value is not None or not required, "a13_incidence_missing")
-    if value is None:
-        return
-    require(isinstance(value, dict) and set(value) == set(BRANCHES), "a13_incidence_branches")
+def validate(value):
+    """Section 4.3, case 1: the recorded record. A10.8 item 2: D:417-420 is the
+    complete list of tests; no test relates a numerator, or a denominator, to
+    the reason maps. The denominator self-check is in ``per_run``."""
+    require(isinstance(value, dict) and set(value) == set(BRANCHES), "a13 incidence branches")
     for b in BRANCHES:
         row = value[b]
+        require(isinstance(row, dict), "a13 incidence branches")
         n, d = row.get("numerator"), row.get("denominator")
         require(integer(n) and integer(d) and n <= d and row.get("assessed") is bool(d) and
-                row.get("rate") == (n / d if d else None), "a13_incidence_counts")
+                row.get("rate") == (n / d if d else None), "a13 incidence counts")
         for name in COUNTS:
             counts = row.get(name)
             require(isinstance(counts, dict) and all(isinstance(k, str) and integer(v) for k, v in counts.items()),
-                    "a13_incidence_separate_counts")
-        require(sum(row["balanced_fallbacks_by_reason"].values()) <= d and
-                sum(row["survival_first_unavailable_selections_by_reason"].values()) <= d, "a13_incidence_separate_counts")
-        affected_events = row["excluded_by_reason"].get("missing_or_not_estimable_row", 0)
-        if b == "survival_first":
-            affected_events += row["survival_first_unavailable_selections_by_reason"].get("missing_or_not_estimable_row", 0)
-        require((n == 0) == (affected_events == 0) and n <= affected_events, "a13_incidence_reasons")
+                    "a13 incidence separate counts")
```

Unified diff, `base.py:24-33 reader_identity` against stage 1 `reading.py:24-27 reader_identity` [M]:

```diff
--- stage1/B/reading_a10/reading.py:24-27 reader_identity
+++ stage2/reading_stage2_b/base.py:24-33 reader_identity
@@ -1,4 +1,10 @@
 def reader_identity():
-    """A hash of the reader's own files (LF-normalized, the instrument's convention)."""
-    files = {p.relative_to(PACKAGE.parent).as_posix(): lf_hash(p) for p in sorted(PACKAGE.glob("*.py"))}
-    return {"files": files, "sha256": digest(files)}
+    """D:529: a sha256 over the package's ``*.py`` files with their names.
+
+    Definition: ``digest({<file name relative to the package directory>:
+    sha256(file bytes with CRLF normalized to LF)})`` over every ``*.py`` file
+    directly in the package directory, where ``digest`` is the sha256 of the
+    canonical JSON. Names are relative to the package directory, so the identity
+    does not change when the package directory is renamed at commit (D:680)."""
+    files = {p.name: lf_hash(p) for p in sorted(PACKAGE.glob("*.py"))}
+    return {"files": files, "sha256": digest(files), "role": ROLE}
```

## 3. The registry as data

- **Reader A export:** `reading_stage2_a.registry.REGISTRY, imported from R`, 9926 canonical bytes, `v3.artifacts.digest` `d0e0570aa8e7ec02fe966201302b9ee9fb7993b7f51f0958b05fe4825b286abc` [M]. The reader's own `REGISTRY_DIGEST` is the same value [M].
- **Reader B export:** `reading_stage2_b.registry.REGISTRY, imported from R`, 11667 canonical bytes, `v3.artifacts.digest` `79a6d20c886a3732bf2578b7c8c0c455d6fc322381921b3c1d66c781ef13f94c` [M]. B's frozen literal `REGISTRY_DIGEST` is the same value, and `verify_formation()` returns: pass [M].
- **Field-by-field check:** 14 entries in each, identities only in A: none, only in B: none. Fields: identity, component, family, kind, arm, alpha, family_size, level_alpha, undefined_tail, seed, grid_values, arm_filters (key set and values), comparator_filters (key set and values), arm_seeds, comparator_seeds, resamples, quantile_method, sigma_variant, capstar_rr. **Content differences: none.** The two registries describe the same 14 comparisons, with equal identity and equal value in every compared parameter. No content difference [M].
- **Serialization differences (expected, not content):**
  - A holds the grid values in `grid`; B holds a grid name in `grid` (R1, SIGMA or CAPABILITIES) and the values in `grid_values`.
  - B holds `tuple`, `sigma_variant` and `capstar_rr` as data; A does not. A's sigma variant is implied by its grid choice (SIGMA_GRID exactly when kind is boundary and the arm starts with sigma) [R, reading_stage2_a/registry.py]; A's cap* rr is the literal 0.064 in registry.matches [R]. The implied values equal B's on all 14 [M].
  - A's boundary entries carry no `alpha` key (A's A6 entries come from v3.reading_a6.headline_comparisons()); B's carry alpha null. Compared as null [M].
  - Entry order: A sorts all 14 by identity; B sorts within A10arm and then within A6. The two orders are the same [M].

The 14 comparisons, equal in both readers [M]:

| Identity | Comp. | Family | Kind | Arm | alpha | Size | Level alpha | Undefined tail | Seed | Grid | Seeds arm/comp | Resamples | Quantile | sigma variant (B; A implied) | cap* rr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `A10arm.boundary.sqrt` | A10 | A10arm | boundary | sqrt | None | 18 | 0.002777777777777778 | 0.001388888888888889 | 20261011 | R1 `[0.055,0.056,0.057,0.058,0.059,0.06,0.062,0.064,0.066]` | 100/400 | 50000 | inverted_cdf | False; False | None |
| `A10arm.capstar.sqrt.0.5` | A10 | A10arm | cap_star | sqrt | 0.5 | 18 | 0.002777777777777778 | None | 20261011 | CAPABILITIES `[1.2,1.5,2.0,2.5,3.0,4.0,5.0]` | 100/75 | 50000 | inverted_cdf | False; False | 0.064 |
| `A10arm.capstar.sqrt.0.75` | A10 | A10arm | cap_star | sqrt | 0.75 | 18 | 0.002777777777777778 | None | 20261011 | CAPABILITIES `[1.2,1.5,2.0,2.5,3.0,4.0,5.0]` | 100/75 | 50000 | inverted_cdf | False; False | 0.064 |
| `A10arm.capstar.sqrt.1.0` | A10 | A10arm | cap_star | sqrt | 1.0 | 18 | 0.002777777777777778 | None | 20261011 | CAPABILITIES `[1.2,1.5,2.0,2.5,3.0,4.0,5.0]` | 100/75 | 50000 | inverted_cdf | False; False | 0.064 |
| `A10arm.capstar.sqrt.1.25` | A10 | A10arm | cap_star | sqrt | 1.25 | 18 | 0.002777777777777778 | None | 20261011 | CAPABILITIES `[1.2,1.5,2.0,2.5,3.0,4.0,5.0]` | 100/75 | 50000 | inverted_cdf | False; False | 0.064 |
| `A10arm.capstar.sqrt.1.5` | A10 | A10arm | cap_star | sqrt | 1.5 | 18 | 0.002777777777777778 | None | 20261011 | CAPABILITIES `[1.2,1.5,2.0,2.5,3.0,4.0,5.0]` | 100/75 | 50000 | inverted_cdf | False; False | 0.064 |
| `A6.boundary.crowding` | A6 | A6 | boundary | crowding | None | 33 | 0.0015151515151515152 | 0.0007575757575757576 | 20260929 | R1 `[0.055,0.056,0.057,0.058,0.059,0.06,0.062,0.064,0.066]` | 100/400 | 50000 | inverted_cdf | False; False | None |
| `A6.boundary.sigma_squared_x0.1` | A6 | A6 | boundary | sigma_squared_x0.1 | None | 33 | 0.0015151515151515152 | 0.0007575757575757576 | 20260929 | SIGMA `[0.059,0.06,0.062,0.064,0.066]` | 100/400 | 50000 | inverted_cdf | True; True | None |
| `A6.boundary.sigma_squared_x10` | A6 | A6 | boundary | sigma_squared_x10 | None | 33 | 0.0015151515151515152 | 0.0007575757575757576 | 20260929 | SIGMA `[0.059,0.06,0.062,0.064,0.066]` | 100/400 | 50000 | inverted_cdf | True; True | None |
| `A6.capstar.crowding.0.5` | A6 | A6 | cap_star | crowding | 0.5 | 33 | 0.0015151515151515152 | None | 20260929 | CAPABILITIES `[1.2,1.5,2.0,2.5,3.0,4.0,5.0]` | 100/75 | 50000 | inverted_cdf | False; False | 0.064 |
| `A6.capstar.crowding.0.75` | A6 | A6 | cap_star | crowding | 0.75 | 33 | 0.0015151515151515152 | None | 20260929 | CAPABILITIES `[1.2,1.5,2.0,2.5,3.0,4.0,5.0]` | 100/75 | 50000 | inverted_cdf | False; False | 0.064 |
| `A6.capstar.crowding.1.0` | A6 | A6 | cap_star | crowding | 1.0 | 33 | 0.0015151515151515152 | None | 20260929 | CAPABILITIES `[1.2,1.5,2.0,2.5,3.0,4.0,5.0]` | 100/75 | 50000 | inverted_cdf | False; False | 0.064 |
| `A6.capstar.crowding.1.25` | A6 | A6 | cap_star | crowding | 1.25 | 33 | 0.0015151515151515152 | None | 20260929 | CAPABILITIES `[1.2,1.5,2.0,2.5,3.0,4.0,5.0]` | 100/75 | 50000 | inverted_cdf | False; False | 0.064 |
| `A6.capstar.crowding.1.5` | A6 | A6 | cap_star | crowding | 1.5 | 33 | 0.0015151515151515152 | None | 20260929 | CAPABILITIES `[1.2,1.5,2.0,2.5,3.0,4.0,5.0]` | 100/75 | 50000 | inverted_cdf | False; False | 0.064 |

Filters per identity, equal key sets and values in both readers [M]:

| Identity | Arm filters | Comparator filters |
|---|---|---|
| `A10arm.boundary.sqrt` | `{"alpha":1.0,"capability":1.5,"category":"a10_arm","component":"sqrt","crowding":"total","g":"sqrt","grid":"R1","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` | `{"alpha":1.0,"capability":1.5,"category":"R1","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A10arm.capstar.sqrt.0.5` | `{"category":"a10_arm","component":"sqrt","crowding":"total","g":"sqrt","grid":"R2","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` | `{"category":"R2","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A10arm.capstar.sqrt.0.75` | `{"category":"a10_arm","component":"sqrt","crowding":"total","g":"sqrt","grid":"R2","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` | `{"category":"R2","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A10arm.capstar.sqrt.1.0` | `{"category":"a10_arm","component":"sqrt","crowding":"total","g":"sqrt","grid":"R2","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` | `{"category":"R2","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A10arm.capstar.sqrt.1.25` | `{"category":"a10_arm","component":"sqrt","crowding":"total","g":"sqrt","grid":"R2","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` | `{"category":"R2","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A10arm.capstar.sqrt.1.5` | `{"category":"a10_arm","component":"sqrt","crowding":"total","g":"sqrt","grid":"R2","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` | `{"category":"R2","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A6.boundary.crowding` | `{"alpha":1.0,"arm":"a6_crowding","capability":1.5,"category":"a6_crowding","component":"crowding","crowding":"reproductive","g":"linear","grid":"R1","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":"crowding_reproductive"}` | `{"alpha":1.0,"capability":1.5,"category":"R1","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A6.boundary.sigma_squared_x0.1` | `{"alpha":1.0,"arm":"a6_sigma_squared_x0.1","capability":1.5,"category":"a6_sigma_squared_x0.1","component":"sigma_squared_x0.1","crowding":"total","g":"linear","grid":"R1","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":"sigma_squared_x0.1"}` | `{"alpha":1.0,"capability":1.5,"category":"R1","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A6.boundary.sigma_squared_x10` | `{"alpha":1.0,"arm":"a6_sigma_squared_x10","capability":1.5,"category":"a6_sigma_squared_x10","component":"sigma_squared_x10","crowding":"total","g":"linear","grid":"R1","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":"sigma_squared_x10"}` | `{"alpha":1.0,"capability":1.5,"category":"R1","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A6.capstar.crowding.0.5` | `{"arm":"a6_crowding","category":"a6_crowding","component":"crowding","crowding":"reproductive","g":"linear","grid":"R2","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":"crowding_reproductive"}` | `{"category":"R2","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A6.capstar.crowding.0.75` | `{"arm":"a6_crowding","category":"a6_crowding","component":"crowding","crowding":"reproductive","g":"linear","grid":"R2","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":"crowding_reproductive"}` | `{"category":"R2","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A6.capstar.crowding.1.0` | `{"arm":"a6_crowding","category":"a6_crowding","component":"crowding","crowding":"reproductive","g":"linear","grid":"R2","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":"crowding_reproductive"}` | `{"category":"R2","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A6.capstar.crowding.1.25` | `{"arm":"a6_crowding","category":"a6_crowding","component":"crowding","crowding":"reproductive","g":"linear","grid":"R2","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":"crowding_reproductive"}` | `{"category":"R2","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |
| `A6.capstar.crowding.1.5` | `{"arm":"a6_crowding","category":"a6_crowding","component":"crowding","crowding":"reproductive","g":"linear","grid":"R2","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":"crowding_reproductive"}` | `{"category":"R2","component":"main","crowding":"total","g":"linear","k_star":1.8,"kappa":8.0,"steps":500,"theta":0.5,"variant":null}` |

Both exports are in the JSON in full, at `registry.A.export` and `registry.B.export`, exactly as each reader holds its `REGISTRY`; their content is the two tables above [M].

## 4. The normalization schema of section 4.3

[R] quoted verbatim from the cited files; excerpt and file sha256 [M].

Source: D:426-432 (D:428-432 is the record block), lines 426-432. File sha256 `3ac0f425cd2b1f27c31a6cf0b757a7ba9e62515ab128a85049f3c5a33d835822`; excerpt sha256 `2c40bdbe96b69afd3a21a0b6c9971f7a21ac9e1d731c0f3678860732ea51a721` [M].

> - The normalized record is, per branch with derived denominator `D`:
>
> ```
> {"numerator": 0, "denominator": D, "rate": 0.0 if D else None, "assessed": bool(D),
>  "provenance": {"numerator": "structural_zero_from_verified_family",
>                 "denominator": "derived_from_recorded_decisions"}}
> ```

Source: A10.1 The ruling, ADDENDUM_10.md:42-58, lines 42-58. File sha256 `132956131d2faf87db4f7a3132bd05f2c27497b37e5f950a12980fcd8ea237f5`; excerpt sha256 `429e4df8b208d64af3ae0f2b6df425c29ab686d4d68352bf75b5a6114c40e8fc` [M].

> **The ruling.** For a quantity whose arm ran, let its pool be the list `quantities[<quantity>]` of `contributing_runs.json`. Each run has the status of its family (D:467): `recorded` (case 1) or `no admitted rows` (case 2). Then `incidence_counts.<quantity>` is exactly:
>
> ```
> {"recorded_runs": <int>,
>  "not_recorded_runs": <int>,
>  "branches": {"ordinary_allocation": <C>, "survival_first": <C>, "yield_review": <C>}}
>
> <C> = {"excluded_by_reason": <V>,
>        "balanced_fallbacks_by_reason": <V>,
>        "survival_first_unavailable_selections_by_reason": <V>}
> ```
>
> 1. `recorded_runs` is the number of runs of the pool with status `recorded`. `not_recorded_runs` is the number with status `no admitted rows`. Both are JSON integers, and their sum is the length of the pool.
> 2. `branches` always holds the three branches, and each branch always holds the three count names.
> 3. **When `recorded_runs` is 0,** every `<V>`, all nine, is the JSON string `"not recorded"`.
> 4. **When `recorded_runs` is positive,** every `<V>` is a JSON object from reason to integer: for each reason that is a key of that map in at least one `recorded` run of the pool, the sum of that key's values over the `recorded` runs. A reason is kept whenever it appears, whatever its sum. A map with no reason in any `recorded` run is `{}`. Reason keys are the strings of the output file, copied and never interpreted. The case 2 runs of the pool add nothing to any map; `not_recorded_runs` states how many they are.
> 5. A not-run arm's quantities have no `incidence_counts` key (A8.5). A pool is never empty for an arm that ran, because G2 puts at least one job in every registry cell.

Source: A10.2 The ruling, ADDENDUM_10.md:86-102, lines 86-102. File sha256 `132956131d2faf87db4f7a3132bd05f2c27497b37e5f950a12980fcd8ea237f5`; excerpt sha256 `c996b1a89bc8396951f60155c342836ac80c481a7a59658571ec245db6bab5ba` [M].

> **The ruling.**
> 1. **Bytes.** `canonical(seal(payload)) + b"\n"`, with `v3.artifacts.canonical` and `seal` (`{"payload": payload, "sha256": digest(payload)}` [M, source read through the running code]).
> 2. **Payload.** Exactly two keys:
>
> ```
> {"schema": "a10-stage2-incidence-per-run-1",
>  "runs": {"<input component>/<job_id>": {"record": <record>, "status": <status>}}}
> ```
>
> 3. **Keys of `runs`.** Exactly the keys of `runs` in the same component's `contributing_runs.json`. The input component is one of `main`, `sqrt`, `crowding`, `sigma_squared_x10`, `sigma_squared_x0.1`.
> 4. **Entry.** Exactly two keys.
>    - `status` is `"recorded"` for a run of a case 1 family and `"no admitted rows"` for a run of a case 2 family.
>    - `record` is, for `recorded`, the output's `result["a13_decision_incidence"]` exactly as parsed: three branches, each with its seven native fields. For `no admitted rows` it is the object of the three branches, each the normalized record of D:428-432 with its `provenance`.
> 5. **No reason and no family per run.** A case 2 entry carries no `reason` key, and no entry carries a `family` key. The status literal `no admitted rows` is the per-run statement. D:467's reason text is a per-family coverage fact; where it is written is unchanged by this addendum.
> 6. **No `component` key.** The payload follows `contributing_runs.json` (D:488), whose `runs` map it mirrors key for key and which carries none.
> 7. **`per_run_sha256`** (D:523) is unchanged: sha256 of `canonical(m)` with no newline, `m` mapping each of the quantity's contributing keys to that run's `record` value. Both builds already agree on it [R, round 0].
> 8. **The comparison** of D:554 is of the file's sha256.

[R/M] No addendum rewrites D:428-432. A10.2 item 4 places that record, with its provenance, in incidence_per_run.json for status `no admitted rows`; A10.8 item 1 extends D:455's preconditions to every contributing run. A text search of Addenda 1 to 11 for D:42x/43x and the record's literals finds no other amending passage.

**The exact shapes, once:**

```
case 2 normalized record, per branch, derived denominator D (D:428-432):
{"numerator": 0, "denominator": D, "rate": 0.0 if D else None, "assessed": bool(D),
 "provenance": {"numerator": "structural_zero_from_verified_family",
                "denominator": "derived_from_recorded_decisions"}}

incidence_counts.<quantity> (A10.1):
{"recorded_runs": <int>, "not_recorded_runs": <int>,
 "branches": {"ordinary_allocation": <C>, "survival_first": <C>, "yield_review": <C>}}
<C> = {"excluded_by_reason": <V>, "balanced_fallbacks_by_reason": <V>,
       "survival_first_unavailable_selections_by_reason": <V>}
<V> = "not recorded" (all nine) when recorded_runs is 0; otherwise {reason: summed int} over the recorded runs

incidence_per_run.json (A10.2): canonical(seal(payload)) + "\n"
payload = {"schema": "a10-stage2-incidence-per-run-1",
           "runs": {"<input component>/<job_id>": {"record": <record>, "status": "recorded" | "no admitted rows"}}}
<record> = result["a13_decision_incidence"] as parsed (recorded), or the three branches of the case 2 record above (no admitted rows)
```

## 5. The fixtures

- **Manifest:** `S/fixtures/g2_regen/builder_package/fixture_manifest_g2r.json`, sha256 `1c82d28d012bf7253052b268265aabf7935c52d9e6ff269581abe670bf220c2b` [M].
- **`SHA256SUMS.txt`:** sha256 `2ea5a84395478bf358937d8555b9d088d869002ac06dea62ea6dd816ae5098e4` [M]; expected `2ea5a843...98e4`: matches.
- **File list hash, as the manifest defines it [R]:** A8.1, per fixture: v3.artifacts.digest of the sorted list of [tree, relative path, sha256] over every file of the fixture's three trees, except AUTHORIZED_HASHES_FIXTURE.json itself and the materialized inputs.json. It is the document's fixture_list_hash. Native lock files are in no list
- The manifest's top-level `fixture_list_hashes` agree with every `fixtures.<ID>.file_list_hash`: yes [M]. 50 fixtures, 38 refusing, 12 sealing [R].

| Fixture | `file_list_hash` [R] | Refuses | Phase | Label (quoted by the manifest) | Gate by the generator's reading |
|---|---|---|---|---|---|
| F06 | `b7dab5751c965ec2645f2664ec61b2bdcc4e8702bb9d0b4209eea64ff7c2d0d9` | no | - | - | - |
| F08a | `afb312921a287456a1f10a93a2f3e5351197acdfdce20fb15766c66f17cd4144` | no | - | - | - |
| F08b | `8054027f9c114cd7d2cb2c50076851642ee921bd72f4b54ad53b16be5fe1e8de` | no | - | - | - |
| F10 | `422df368f10c00d99a5191943508290c1e44c86dc9d716fea2dc4108ed35f0fd` | yes | input_verification | `a13 incidence missing on admitted family` | G8 |
| F10b | `d530fa62f873a473ab3a5e619acc49640e9df8c212b189c1ad22497cdff367aa` | yes | input_verification | `incidence denominators not derivable` | G8 |
| F11a | `a0b87d7d6325d8e07bb71ee644d0cc94ce5c12ba18731d56b39f10f0d4ed6d47` | yes | input_verification | - | G7 |
| F11b | `7a67940eb916533a1d34cb959d6ad39197b24b4e28a42c25ec31218a92af48db` | yes | input_verification | - | G7 |
| F11c | `536cc50598c4ff05dc98a5ca5244b1fc096639fe66238b4f22d983a4a15c890e` | yes | input_verification | - | G7 (or G1, on the absent published file) |
| F11d | `312a1e2bb746ef358a4518d86080ef823ca5286e3db2403ca1d74f08c620f051` | yes | input_verification | - | G7 |
| F11e | `0d40ed9da2c741a1d3875fb86711f5882162cb7737a1b26c137124485476bda7` | yes | input_verification | - | G7 |
| F11f | `30d1a6d40680df50c3b2f3b65dd84e14502cabeb9e0e1a38a034ce230797fb3d` | yes | input_verification | - | G7 |
| F11g | `b5857e04ebdacd4f2a5e71c3b6e3ad507ffade0869a402957a71bf778a9952e9` | yes | input_verification | - | G7 (inside require_a10) |
| F12a | `8875aefe7d862896e07b45ecc085839ba476dfda0621d41d90da5e88ac108424` | yes | input_verification | - | G4 |
| F12b | `d7945639a1023912dfc0874d914bd221269a3e7e119f276fae79e5067e58457f` | yes | input_verification | - | G4 |
| F12c | `34297e7192528740a594525202614778191cb7e24765f2cb3fe92270b422f5ae` | yes | input_verification | - | G4 |
| F12c2 | `d0bd4d24e8b2195a9d55b4e185153d6a732bc3db2ee797e90223a5050ade976c` | yes | input_verification | - | G4: output bytes against the verified_output_hashes.json entry |
| F12c3 | `9607f8a5cd125589cb811982a5b904836b3149631625d132729629644eb2ff4c` | yes | input_verification | - | G4: output bytes against the record's output_hash |
| F12d | `f918cc8b321c4d4be9736a285256a0c4c0d4b6accdd79ddf9063019ab0ecef76` | yes | input_verification | - | G2 |
| F12e | `df557243aac0e1c3a38ccd9904ef2584340db6a0485909cbc44de99aba66af11` | yes | input_verification | - | G2 |
| F12f | `bd955f14e9ec7bd66aa1c59074d7d239e4148ac376e67a935f917ef98362720e` | yes | input_verification | - | G2 |
| F12f2 | `d00ae67f2e47ab4179595df566b9533ca06ebef87d29545c45bdfe6344eefb6e` | yes | input_verification | - | G2: no job outside the registry cells, and job_count |
| F13a | `1c83c6634c39981df8e1a521d61023572067ebed1eab43a5ea7b08b54bbeccb4` | no | - | - | - |
| F13a2 | `ec7b823be43da7d01f7a2e861f7325ce7bbf2c5104d6eb5f399d685a6c282635` | no | - | - | - |
| F13b | `99a60e24667ea122bbf636281e8f3a9c4375d8dc514e4851ac87015efd9be07b` | yes | input_verification | - | G9 |
| F13c | `7d022011c9efda1679e73adb2fdaa51ef614278f6d0eca1a0ce8468a362cd75f` | yes | input_verification | - | G9 |
| F13d | `d504d96ee5151e1ea22d174e5f0db6712e8e2030a4b4ecc9c0f2995c54637f92` | no | - | - | - |
| F13d2 | `1fa6b7fb5344a9af6d62213e1f16726b129bf42795a5b5468da71020e701fd46` | no | - | - | - |
| F13e | `264025b258c0327ce391951266be03ab0ec8c47c61006adb2854064c2390433f` | no | - | - | - |
| F13e2 | `d6a94c6214fd31542ecf876b8967692e1c5f1447a94741cfa4c40644896666c7` | no | - | - | - |
| F13e3 | `116f95a367e310284dfa02e4244ae2065f327946efab08e0393517bbf949a770` | no | - | - | - |
| F13e4 | `fa4b3081d3a0b953820ffa5250b898bf744396dbd71ac7c1e9694e30eacd9ed7` | no | - | - | - |
| F13e5 | `fa4b3081d3a0b953820ffa5250b898bf744396dbd71ac7c1e9694e30eacd9ed7` | yes | input_verification | - | G1 (A8.4 binding) |
| F13e6 | `fa4b3081d3a0b953820ffa5250b898bf744396dbd71ac7c1e9694e30eacd9ed7` | yes | input_verification | - | G1 (A8.4 presence) |
| F13f | `b40618b999fbedc8d5d357288ef374888326207380b7e064d3dfaa1f39252485` | yes | input_verification | - | G9 |
| F13f2 | `3e0f005d8577c13146a2883f8fabab6d88bef793052ec7c1f0d48c3f3a789bba` | yes | input_verification | - | G9 |
| F13g | `d9c7ffe54a97dd7921f2d29672db4ea06efca5d35d9e727b23808274f95815b3` | yes | input_verification | - | G9: terminal latch |
| F13h | `1aeb208b785338eb9afd291cdf1524d1f5bc1b64cfa638cd559a16ec6c505179` | yes | input_verification | - | G9: table check and records check |
| F13i | `9f1bf69e4981fec46a7b0fcc757c01a66aee657d3c0a4745385cfc16de108585` | yes | input_verification | - | G9: no family record beside a closeout |
| F13j | `1ff854766fa99855101ad2689b504e9b76279d4aad74deff30f6513caef39e1e` | yes | input_verification | - | G9: a16_entered is False |
| F14a | `cdb54bcc983b3a584c5f276fabd0cc561fe997332f764d8c981d5f2053802936` | yes | input_verification | - | G6 |
| F14b | `f171903411e79203c46aad4e6e085b855927b9bb4079b7967d91d8885feeeba2` | yes | input_verification | - | G1 |
| F14c | `cbfa27b875f899ed660b8fa6c4bbd678fa5e6fcbe79fd7a54232de231428862a` | yes | input_verification | - | G6, case 2 condition 5 |
| F14d | `7d2089f1b71fdc716e69c83c37cfa84e30906e374b878f541723fcc912856b3f` | yes | input_verification | - | G6, A16 branch: record.plan_hash == manifest.a13_admission.a16.plan_hash |
| F14e | `34fdc6df3d78e0775d19e5c02487c9ac400245a3519765707796f68f47957d2c` | yes | input_verification | - | G6, nominal branch: A14 record plan_hash == receipt.a14_round.plan_hash |
| F14f | `a206e886533acfb95ab9867cbc43841397690dfb53870b06e8887f9406a1e0a4` | yes | input_verification | - | G6, nominal branch (or G1, on the bound hash) |
| F14f2 | `ab29c472c68c2903ccc28bac35db0e24a322f579a935743a72b8546df9000a9a` | yes | input_verification | - | G6, nominal branch: A13 refusal file sha256 against the receipt's two fields |
| F14g | `eb487b8762432ca596339ef5efafa978932b61719fef9e1ce68ccab499fd666c` | yes | input_verification | - | G6 |
| F15a | `9d5a6dd34d93b10c308df9e407ccab531a5b4972da3f8c82c17db5f9acb650fc` | yes | input_verification | - | G8 |
| F15b | `eae69b3bf9c760d3c89382bb4cdcd581d32c7463f6329079f641f76808297c2b` | yes | input_verification | - | G8 |
| MAIN | `eef696a3f1e9c33e2a3d6381da4ff6e9af3121d53af0c2cf44f1cfe0c7548a0a` | no | - | - | - |

**Expected outcomes, as the manifest gives them [R].** For refusing fixtures every entry also carries the note "the specification fixes the phase and the fact of refusal (D:658); the label is fixed only where one is quoted".

- **F10** refuses at `input_verification`; basis D:582, D:417; binder checks expected to fail ["g8.incidence_present_case1"]; isolation true; label "a13 incidence missing on admitted family".
- **F10b** refuses at `input_verification`; basis A6.1, A7.1; binder checks expected to fail ["g8.preconditions"]; isolation true; label "incidence denominators not derivable".
- **F11a** refuses at `input_verification`; basis D:583, D:371-372; binder checks expected to fail null; isolation null; label null.
- **F11b** refuses at `input_verification`; basis D:583, D:370; binder checks expected to fail null; isolation null; label null.
- **F11c** refuses at `input_verification`; basis D:583, D:372; binder checks expected to fail null; isolation null; label null.
- **F11d** refuses at `input_verification`; basis D:583; binder checks expected to fail null; isolation null; label null.
- **F11e** refuses at `input_verification`; basis D:583, D:368; binder checks expected to fail ["g7.spec_policy"]; isolation true; label null.
- **F11f** refuses at `input_verification`; basis D:583, D:371; binder checks expected to fail null; isolation null; label null.
- **F11g** refuses at `input_verification`; basis D:583; binder checks expected to fail null; isolation null; label null.
- **F12a** refuses at `input_verification`; basis D:584; binder checks expected to fail ["g4.output_exists"]; isolation true; label null.
- **F12b** refuses at `input_verification`; basis D:584; binder checks expected to fail ["g4.record_exists"]; isolation true; label null.
- **F12c** refuses at `input_verification`; basis D:584; binder checks expected to fail ["g4.output_hash_equals_hash_file","g4.output_hash_equals_record"]; isolation false; label null.
- **F12c2** refuses at `input_verification`; basis A8.6 item 1, D:354; binder checks expected to fail ["g4.output_hash_equals_hash_file"]; isolation true; label null.
- **F12c3** refuses at `input_verification`; basis A8.6 item 1, D:354; binder checks expected to fail ["g4.output_hash_equals_record"]; isolation true; label null.
- **F12d** refuses at `input_verification`; basis D:584, A3.5 rows 1 to 3, A8.1; binder checks expected to fail ["g2.job_count","g2.per_cell_count"]; isolation true; label null.
- **F12e** refuses at `input_verification`; basis D:584, A8.1; binder checks expected to fail ["g2.ids_distinct","g2.job_count","g2.per_cell_count","g2.seeds_distinct"]; isolation true; label null.
- **F12f** refuses at `input_verification`; basis D:584, A3.5 rows 1 to 3, A8.1; binder checks expected to fail ["g2.job_count","g2.per_cell_count"]; isolation true; label null.
- **F12f2** refuses at `input_verification`; basis A8.6 item 1, A8.1; binder checks expected to fail ["g2.job_count","g2.no_job_outside_cells"]; isolation true; label null.
- **F13b** refuses at `input_verification`; basis D:585, D:383; binder checks expected to fail ["g9.no_table"]; isolation true; label null.
- **F13c** refuses at `input_verification`; basis D:585, A8.3; binder checks expected to fail ["g9.evidence_set"]; isolation true; label null.
- **F13e5** refuses at `input_verification`; basis A8.4; binder checks expected to fail ["doc.supplementary_binding"]; isolation true; label null.
- **F13e6** refuses at `input_verification`; basis A8.4; binder checks expected to fail ["doc.supplementary_presence"]; isolation true; label null.
- **F13f** refuses at `input_verification`; basis A1.7, A2.9; binder checks expected to fail ["g9.no_records_runs"]; isolation true; label null.
- **F13f2** refuses at `input_verification`; basis A2.9; binder checks expected to fail ["g9.no_records_runs_run"]; isolation true; label null.
- **F13g** refuses at `input_verification`; basis A1.7(a), A2.9; binder checks expected to fail ["g9.terminal_latch"]; isolation true; label null.
- **F13h** refuses at `input_verification`; basis D:383, A1.7; binder checks expected to fail ["g9.no_records_runs","g9.no_table"]; isolation false; label null.
- **F13i** refuses at `input_verification`; basis A8.2; binder checks expected to fail ["g9.no_family_record"]; isolation true; label null.
- **F13j** refuses at `input_verification`; basis A8.2; binder checks expected to fail ["g9.closeout_a16_entered"]; isolation true; label null.
- **F14a** refuses at `input_verification`; basis D:586, D:361; binder checks expected to fail null; isolation null; label null.
- **F14b** refuses at `input_verification`; basis D:586; binder checks expected to fail ["g1.identity_binds_table"]; isolation true; label null.
- **F14c** refuses at `input_verification`; basis D:586, D:406; binder checks expected to fail ["g6.context_coverage"]; isolation true; label null.
- **F14d** refuses at `input_verification`; basis A1.3, A7.4; binder checks expected to fail ["g6.a16_plan_hash"]; isolation true; label null.
- **F14e** refuses at `input_verification`; basis A2.1 item 7; binder checks expected to fail ["g6.a14_plan_hash"]; isolation true; label null.
- **F14f** refuses at `input_verification`; basis A2.1 item 7; binder checks expected to fail ["g1.a13_refusal_bound","g1.published_hash_seal","g6.a13_refusal_receipt"]; isolation false; label null.
- **F14f2** refuses at `input_verification`; basis A8.6 item 1, A2.1 item 3; binder checks expected to fail ["g6.a13_refusal_receipt"]; isolation true; label null.
- **F14g** refuses at `input_verification`; basis A2.1; binder checks expected to fail ["g6.scope_allowed"]; isolation true; label null.
- **F15a** refuses at `input_verification`; basis D:587, D:425; binder checks expected to fail ["g8.no_missing_row"]; isolation true; label null.
- **F15b** refuses at `input_verification`; basis D:587, D:424; binder checks expected to fail ["g8.incidence_absent_case2"]; isolation true; label null.

#### F06 (seals)

- expects: derived equals recorded on every branch of every case 1 run, crowding included
- expects: crowding is case 1 here: status recorded
- reference: blocks `disclosure`, `incidence`, `quantity_keys`, `quantity_run_counts`, `violation_rows_by_family`; `v3.artifacts.digest` of the block `a89fbfee45c28fccb61255e4fde759926ce371a957619fe5ec67d46cb966c27c` [M]; full text in the JSON.
- screens: keys `family_case_from_outputs`, `flagged_quantities`, `quantities`, `quantities_with_an_unassessed_branch`; `v3.artifacts.digest` `4304954df41aff810dc968260268cd78f88d1bc39a522844d5646944e4ba7f20` [M]; full text in the JSON.

#### F08a (seals)

- expects: the zero-agent run: all three denominators 0, assessed false, rate null, reported unassessed
- expects: its cell's survival quantity still pools a positive denominator from the other run
- reference: blocks `disclosure`, `incidence`, `quantity_keys`, `quantity_run_counts`, `twin_denominators_of_the_zero_agent_runs`, `violation_rows_by_family`; `v3.artifacts.digest` of the block `e18d61e135797ee615f83901d416dc22c71c20e38c6c2c1ac648933efa70ce06` [M]; full text in the JSON.
- **A10.7 erratum applied:** `reference.twin_denominators_of_the_zero_agent_runs` = `{"rerun_8d5f08c6e4fcb99c4720c97a":{"ordinary_allocation":0,"survival_first":0,"yield_review":0}}`. A10.7 item 1: one entry. As packaged the block holds two entries, the second naming a job of F08b.
- screens: keys `family_case_from_outputs`, `flagged_quantities`, `quantities`, `quantities_with_an_unassessed_branch`; `v3.artifacts.digest` `2ec2e31c40d7b6aebfae6a22d1b2f3412bbe115c96d2a12e6adcc9e1e9905815` [M]; full text in the JSON.

#### F08b (seals)

- expects: A6.survival.crowding.0.057 pools to unassessed on all three branches, never to rate 0
- reference: blocks `disclosure`, `incidence`, `quantity_keys`, `quantity_run_counts`, `violation_rows_by_family`; `v3.artifacts.digest` of the block `3697e243a46bff15865596ddd0c728168be6a406bdda7bc81ad9af95859d8a08` [M]; full text in the JSON.
- **A10.7 erratum applied:** `reference.twin_denominators_of_the_zero_agent_runs` = `{"rerun_8d5f08c6e4fcb99c4720c97a":{"ordinary_allocation":0,"survival_first":0,"yield_review":0},"rerun_d368fdf0ce0bf1646a8cc510":{"ordinary_allocation":0,"survival_first":0,"yield_review":0}}`. A10.7 item 2: both entries, read from the block filed under F08a. The packaged F08b entry has no such block [M].
- screens: keys `family_case_from_outputs`, `flagged_quantities`, `quantities`, `quantities_with_an_unassessed_branch`; `v3.artifacts.digest` `95b6f346c78b39e363df638e399aa0768d478ca13b5fa74ce263d0165d992519` [M]; full text in the JSON.

#### F13a (seals)

- expects: A6 has eight entries; A6.boundary.sigma_squared_x10 has status 'not run', verdict 'undetermined', reason 'arm not run: <reason>' with the reason taken from the family record's terminal.reason, estimate, interval and undefined_share null, level_alpha 0.05/33 and undefined_tail 0.05/66
- expects: the other seven computed; family_size.A6 33; level and tail unchanged
- expects: its disclosure is computed from the comparator side alone (A3.7)
- expects: A8.5: the not-run arm's comparison entries, the keys each values.json must hold and each component's quantities lists are in reference.not_run
- reference: blocks `disclosure`, `incidence`, `not_run`, `not_run_reasons`, `quantity_keys`, `quantity_run_counts`, `violation_rows_by_family`; `v3.artifacts.digest` of the block `6cce35555369dbeae0433339d66a1f738af937ede896aa5d47ce8200b7606306` [M]; full text in the JSON.
- screens: none in the manifest

#### F13a2 (seals)

- expects: A6's six crowding comparisons read 'not run' with reason 'arm not run: round 2 Part 2 refused; no third round'; the two sigma boundaries are computed
- expects: A10 is computed
- expects: A8.5: the not-run arm's comparison entries, the keys each values.json must hold and each component's quantities lists are in reference.not_run
- reference: blocks `disclosure`, `incidence`, `not_run`, `not_run_reasons`, `quantity_keys`, `quantity_run_counts`, `violation_rows_by_family`; `v3.artifacts.digest` of the block `e894334136cb98b539a01ce5a7210d52c1e190c3b642a0a5024ca354d915854c` [M]; full text in the JSON.
- screens: none in the manifest

#### F13d (seals)

- expects: A6 seals with every one of its eight entries 'not run'; A10 is computed
- expects: each reason comes from that arm's evidence (reference.not_run.reasons)
- expects: A6's LADDER.json still has key/check and records/main (A8.5, A8.7)
- expects: A8.5: the not-run arm's comparison entries, the keys each values.json must hold and each component's quantities lists are in reference.not_run
- reference: blocks `disclosure`, `incidence`, `not_run`, `not_run_reasons`, `quantity_keys`, `quantity_run_counts`, `violation_rows_by_family`; `v3.artifacts.digest` of the block `43ab2e73cead594d17bdfed3e66565fc646b32777e2dec26706f673ce50c18da` [M]; full text in the JSON.
- screens: none in the manifest

#### F13d2 (seals)

- expects: A10 seals with its six entries 'not run'; family_size.A10arm stays 18; A6 is computed
- expects: sqrt_admission_check_sha256 is null in the fixture document (A8.1)
- expects: A8.5: the not-run arm's comparison entries, the keys each values.json must hold and each component's quantities lists are in reference.not_run
- reference: blocks `disclosure`, `incidence`, `not_run`, `not_run_reasons`, `quantity_keys`, `quantity_run_counts`, `violation_rows_by_family`; `v3.artifacts.digest` of the block `e6d0a6778c8c3f8ff93738b0027320fc75f8f0edde75efdd084b14d44ec1385a` [M]; full text in the JSON.
- screens: none in the manifest

#### F13e (seals)

- expects: G6's A16 branch passes; crowding is case 1
- expects: family.crowding.admission and family_error.crowding.* copy the values of reference.copied_values
- expects: schema 2 inventory: supplementary_records is {} (A8.4)
- reference: blocks `copied_values`, `disclosure`, `incidence`, `quantity_keys`, `quantity_run_counts`, `violation_rows_by_family`; `v3.artifacts.digest` of the block `a4ffc3e7c89d72add82f0c558525e7110e60de4fac8cd29608eb73482c5ac29a` [M]; full text in the JSON.
- screens: keys `family_case_from_outputs`, `flagged_quantities`, `quantities`, `quantities_with_an_unassessed_branch`; `v3.artifacts.digest` `2d832e3b6bd56a81b236bb482d114dc95b54d13aca947e5930ba3e9912817a95` [M]; full text in the JSON.

#### F13e2 (seals)

- expects: G6's A16 branch passes; two admitted rows
- reference: blocks `copied_values`, `disclosure`, `incidence`, `quantity_keys`, `quantity_run_counts`, `violation_rows_by_family`; `v3.artifacts.digest` of the block `43d8d6894d9cc7c791dd71c71a523d1fd6fc4193c0a97c369ef57b7fa1baf9ff` [M]; full text in the JSON.
- screens: keys `family_case_from_outputs`, `flagged_quantities`, `quantities`, `quantities_with_an_unassessed_branch`; `v3.artifacts.digest` `8cf27566324168b86c07c5baa4167b1b7dfbc3a5a61d441f4933c021fcd887d1` [M]; full text in the JSON.

#### F13e3 (seals)

- expects: G6's q = 2 branch passes: the round 1 admission record reads refused and its file hash equals refusals.round1_admission_record_sha256
- expects: rounds_used and family_error.crowding.* copy reference.copied_values; E2 and tests_round2 are non-null and distinct
- reference: blocks `copied_values`, `disclosure`, `incidence`, `quantity_keys`, `quantity_run_counts`, `violation_rows_by_family`; `v3.artifacts.digest` of the block `70d2f9c5ae41150d9d9ea4b1622fde5c5e00b9fa5db19c36ae0c5b8900cb5ddb` [M]; full text in the JSON.
- screens: keys `family_case_from_outputs`, `flagged_quantities`, `quantities`, `quantities_with_an_unassessed_branch`; `v3.artifacts.digest` `79196646d9f20cf00bcbf70fc12d55979e1b3eee21a7205792b164a6850f4240` [M]; full text in the JSON.

#### F13e4 (seals)

- expects: the inventory adapter selects INV-C by the schema string; supplementary_records.crowding binds the family record, the round record, the round admission record and the public record by sha256 and seal
- expects: every value equals F13e's: the arm's files and runs are the same
- reference: blocks `copied_values`, `disclosure`, `incidence`, `note`, `quantity_keys`, `quantity_run_counts`, `violation_rows_by_family`; `v3.artifacts.digest` of the block `6594ece743d23db2ff79e582aa03c7982baad7e25225791afead85fd072fe68f` [M]; full text in the JSON.
- screens: none in the manifest

#### MAIN (seals)

- expects: both components seal; 14 comparisons computed; family_size 18 and 33; 84 quantity keys, 30 in A10 and 54 in A6 (A8.5)
- expects: crowding and both sigma families: status 'no admitted rows', numerators 0 with provenance structural_zero_from_verified_family, denominators derived_from_recorded_decisions and equal to the twin's recorded denominators (reference.twin_denominators)
- expects: sqrt and nominal: status recorded; the denominator self-check passes on every case 1 run
- expects: F9: quantities whose comparator side has a nonzero pooled numerator are flagged; the others are not, and the output carries the 'not certified unaffected' sentence; families shows one recorded and one 'no admitted rows' side for the A6 quantities (reference.incidence, 84 keys)
- expects: F11(h): disclosure.<quantity> lists exactly the labelled violation rows a contributing run's configuration looks up (reference.disclosure, A8.9)
- expects: F16: byte-identical repeats; 'both' equals separate invocations
- reference: blocks `a8_9_comparison`, `disclosure`, `incidence`, `quantity_keys`, `quantity_run_counts`, `twin_denominators`, `twin_oracle_summary`, `violation_details`, `violation_row_names`, `violation_rows`, `violation_rows_by_family`; `v3.artifacts.digest` of the block `6057a8c436ce443c5199a2e938b3db1b4ce240e8206abd4e27c99742fa3254be` [M]; full text in the JSON.
- screens: keys `family_case_from_outputs`, `flagged_quantities`, `quantities`, `quantities_with_an_unassessed_branch`; `v3.artifacts.digest` `2ec2e31c40d7b6aebfae6a22d1b2f3412bbe115c96d2a12e6adcc9e1e9905815` [M]; full text in the JSON.

**The A10.7 erratum:**

Source: A10.7 The erratum, ADDENDUM_10.md:287-291, lines 287-291. File sha256 `132956131d2faf87db4f7a3132bd05f2c27497b37e5f950a12980fcd8ea237f5`; excerpt sha256 `c20b5e82366407e9694d4e6154f11b05d1bb5a1704f7168579e92cc4e291192a` [M].

> **The erratum.**
> 1. For F08a the block has one entry, `rerun_8d5f08c6e4fcb99c4720c97a`.
> 2. For F08b the block has both entries, `rerun_8d5f08c6e4fcb99c4720c97a` and `rerun_d368fdf0ce0bf1646a8cc510`.
> 3. **"Held" means:** for every entry of the fixture's block, the A6 `incidence_per_run.json` has the key `crowding/<job id>`, with status `no admitted rows` and a normalized record whose three denominators equal the entry's. An entry naming a job that is in none of the fixture's specs makes the block wrong, not "not checkable".
> 4. Until the manifest is regenerated (A10.9), a build checks F08a against item 1 and F08b against item 2, reading both from the block filed under F08a.

## 6. The fixture comparison results

[R] output hashes as reported in the two round 2 results files (files the assembler may not open; their hashes on disk were verified 864 of 864 by the round 2 comparison check, REPORT.md check 3); results-file sha256 and the per-fixture `identical` [M].

- **Results A:** `BA/reports/FIXTURE_RESULTS_A.json`, sha256 `2c51018ef81705177c39e89b4416955fe8f3888783aec19ac7a0e8be1f0fdf03` [M] (expected `2c51018e...df03`), 75827 bytes, schema `a10-stage2-fixture-results-3`, role A, reader identity `1c0fca4593af45918d405508cdab9ac01632bec50df97a762ae119f9adffea1d`.
- **Results B:** `BB/reports/FIXTURE_RESULTS_B.json`, sha256 `dfb3fe0c8a2e2c841be7f34fa408da98ded561d79b9099b1546ef24509c56823` [M] (expected `dfb3fe0c...6823`), 76225 bytes, schema `a10-stage2-fixture-results-3`, role B, reader identity `2ad63b7a9b07abb43309b656085890de32b752946be66ac5c2a7672f62bc72db`.
- **`identical`:** 50 of 50 fixtures [M]: 12 sealed in both builds, 38 refused in both. Each build's outcome agrees with the manifest's `refuses` on every fixture: yes [M].
- **Criterion:** D 8.3: values.json, contributing_runs.json, incidence_per_run.json and LADDER.json of run1 equal across builds on both components (sealed fixtures), or both builds refuse at the same phase (refusing fixtures).

### Refusing fixtures

In every refusal entry of both builds, the refusing command's folder holds exactly `["refusal.json"]` [R; confirmed on disk by the second check].

| Fixture | A: command, phase, label [R] | B: command, phase, label [R] | |
|---|---|---|---|
| F10 | verify, input_verification, `a13 incidence missing on admitted family` | verify, input_verification, `a13 incidence missing on admitted family` | identical |
| F10b | verify, input_verification, `incidence denominators not derivable` | verify, input_verification, `incidence denominators not derivable` | identical |
| F11a | verify, input_verification, `check failed` | verify, input_verification, `labels file supplied for a no-label family` | identical |
| F11b | verify, input_verification, `labels binding` | verify, input_verification, `A10 receipt does not bind the labels` | identical |
| F11c | collect, input_verification, `required file absent` | collect, input_verification, `input_missing` | identical |
| F11d | verify, input_verification, `A10 receipt chain` | verify, input_verification, `A10 receipt does not bind the family` | identical |
| F11e | verify, input_verification, `spec labels policy` | verify, input_verification, `spec labels policy differs` | identical |
| F11f | verify, input_verification, `check failed` | verify, input_verification, `family table refused by require_a10` | identical |
| F11g | verify, input_verification, `A6 variant FV row lacks its asymptotic label` | verify, input_verification, `family table refused by require_a10` | identical |
| F12a | verify, input_verification, `required file absent` | verify, input_verification, `input_missing` | identical |
| F12b | verify, input_verification, `required file absent` | verify, input_verification, `input_missing` | identical |
| F12c | verify, input_verification, `input hash` | verify, input_verification, `output hash differs from its completion record` | identical |
| F12c2 | verify, input_verification, `input hash` | verify, input_verification, `output hash differs from the verified hash file` | identical |
| F12c3 | verify, input_verification, `completion output hash` | verify, input_verification, `output hash differs from its completion record` | identical |
| F12d | verify, input_verification, `fixture job count` | verify, input_verification, `job count differs` | identical |
| F12e | verify, input_verification, `fixture job count` | verify, input_verification, `duplicate job id` | identical |
| F12f | verify, input_verification, `fixture job count` | verify, input_verification, `job count differs` | identical |
| F12f2 | verify, input_verification, `fixture job count` | verify, input_verification, `job count differs` | identical |
| F13b | verify, input_verification, `not-run published table` | verify, input_verification, `published table exists for a not-run arm` | identical |
| F13c | collect, input_verification, `not-run evidence set` | collect, input_verification, `not-run evidence set` | identical |
| F13e5 | verify, input_verification, `input hash` | verify, input_verification, `file hash differs from its inventory` | identical |
| F13e6 | verify, input_verification, `A16 supplementary block absent` | verify, input_verification, `supplementary records block missing or malformed` | identical |
| F13f | verify, input_verification, `not-run records present` | verify, input_verification, `run records exist for a not-run arm` | identical |
| F13f2 | verify, input_verification, `not-run records present` | verify, input_verification, `run records exist for a not-run arm` | identical |
| F13g | verify, input_verification, `not-run terminal latch` | verify, input_verification, `not-run family record is not terminal` | identical |
| F13h | verify, input_verification, `not-run published table` | verify, input_verification, `published table exists for a not-run arm` | identical |
| F13i | verify, input_verification, `closeout A16 family record exists` | verify, input_verification, `A16 family record exists beside a closeout` | identical |
| F13j | verify, input_verification, `closeout state` | verify, input_verification, `closeout record reads A16 entered` | identical |
| F14a | verify, input_verification, `admission binding absent` | verify, input_verification, `a13 admission binding absent` | identical |
| F14b | verify, input_verification, `family identity chain` | verify, input_verification, `identity record does not bind the table` | identical |
| F14c | verify, input_verification, `case two full context keys` | verify, input_verification, `no-admitted family lacks context coverage` | identical |
| F14d | verify, input_verification, `A16 round plan` | verify, input_verification, `A16 admission plan hash differs from the bound plan` | identical |
| F14e | verify, input_verification, `A14 plan binding` | verify, input_verification, `A14 admission plan hash differs from the receipt` | identical |
| F14f | verify, input_verification, `input hash` | verify, input_verification, `file hash differs from its inventory` | identical |
| F14f2 | verify, input_verification, `A13 refusal receipt binding` | verify, input_verification, `A13 refusal differs from the receipt` | identical |
| F14g | verify, input_verification, `family admission scope` | verify, input_verification, `admission scope not allowed for the family` | identical |
| F15a | verify, input_verification, `missing row contradicts empty admitted set` | verify, input_verification, `missing row recorded in a no-admitted family` | identical |
| F15b | verify, input_verification, `incidence contradicts empty admitted set` | verify, input_verification, `a13 incidence present on a no-admitted family` | identical |

### Sealed fixtures: six-file hashes of `run1`, per component [R]

For every row below, each build reports `run1_equals_run2` true and `both_equals_separate` true, and its `run2` hashes equal its `run1` hashes; these flags are listed per fixture [R].

#### F06: identical

| Component / file | sha256, A and B (one value where equal) |
|---|---|
| A10 `values.json` | A = B `ccc3e6b38308297b74f558be1c5431968884761ba9c4eefde7641d3b52e67665` |
| A10 `contributing_runs.json` | A = B `ca5ee6f5dbe5d38a74f76dcce682abdc6bdbe2c04bceef2d7e44a2466e8459bd` |
| A10 `incidence_per_run.json` | A = B `d9e587ca2b3cc608f46c42778bd355ccc599a468ac934ce42c5cd79ed44aece9` |
| A10 `LADDER.json` | A = B `11fdbcfb5658a015a324e1089c96de1b94d5d1b42ed906c773f9fbf0aa045214` |
| A10 `reading.json` | A `e4332e78632b9a5a6ea19c58965ec345251682720b405a87687ce3376382340c`; B `d4426b1af68f35f8c1c5605aca5c41e308a7336b690b56e3a33db572b036173a` (not compared) |
| A10 `SEAL.json` | A `acec0b1eae2917dc65becd7614b1ca6c77266afc7c0c0308d5c34b08a3c01ca1`; B `f34ccc2eb1fd99dbb3076f8624e7d84c0aefd25253a9e7b8e90a45d5aed99310` (not compared) |
| A10 `quantities_sha256` | A = B `e869cddcdb02a1684d34200273130c235e5f7a0591d292786339b9a525ab37ce` |
| A6 `values.json` | A = B `2fced132422baf7d5438a892b57cf055f77a328ec92ef68e40629a18337f7e39` |
| A6 `contributing_runs.json` | A = B `8eb4bf0aadbbd282ea8964906164b4fd5c2bccca6888c859f13a5a7b61ce057b` |
| A6 `incidence_per_run.json` | A = B `c3ce8a35b5a71e23e5376cbee572c068d136949f7943b91f9bbaae6da63d63b3` |
| A6 `LADDER.json` | A = B `f3ac8d81e6ed5c36ebee61e82a60ee667f8b30402f4672b5ac6ff9e95924decf` |
| A6 `reading.json` | A `c104ce4cec02c49946f97ed67a72f3b10a903819376b872499e211b47bcf5c2b`; B `92e05e118065e349da47de50d1a51c833bf6796127987f8d3e2294c19afff6d7` (not compared) |
| A6 `SEAL.json` | A `6031801ef3d1879974e98ad195d523214f707c947103bf9375ec44cf6b2c7169`; B `2869662a95db6f2e32ef4fd0f84cf988adb80a5a15409cf4c79bd4ab3abb1277` (not compared) |
| A6 `quantities_sha256` | A = B `b754f04298ffa2282d528a71bf47790b47667ce9f1210ab229b2f411c670a0eb` |

Flags (run1 = run2, both = separate, run2 hashes = run1 hashes) true in both builds and components: yes.

#### F08a: identical

| Component / file | sha256, A and B (one value where equal) |
|---|---|
| A10 `values.json` | A = B `ccc3e6b38308297b74f558be1c5431968884761ba9c4eefde7641d3b52e67665` |
| A10 `contributing_runs.json` | A = B `ca5ee6f5dbe5d38a74f76dcce682abdc6bdbe2c04bceef2d7e44a2466e8459bd` |
| A10 `incidence_per_run.json` | A = B `d9e587ca2b3cc608f46c42778bd355ccc599a468ac934ce42c5cd79ed44aece9` |
| A10 `LADDER.json` | A = B `11fdbcfb5658a015a324e1089c96de1b94d5d1b42ed906c773f9fbf0aa045214` |
| A10 `reading.json` | A `12ebfbbe8f11f1416211dab3547747b9a32ad4dd0fe41109ca668f9fadfa45cd`; B `0f63686c674a319788e9e9c826dcb2c7c5f595008585064156105b79036af9bc` (not compared) |
| A10 `SEAL.json` | A `e422072c76a66183631aeca933108a80129c3313c8c9f382bd9ee38b46a57fb9`; B `aabc54210ccffeea8d6dbcbe16aaa68f309da4702ee64d61bfc974b785012221` (not compared) |
| A10 `quantities_sha256` | A = B `e869cddcdb02a1684d34200273130c235e5f7a0591d292786339b9a525ab37ce` |
| A6 `values.json` | A = B `8346f2c816355c0f9e76f460b7f853a86602585e2e708251c7f2db8350160fe5` |
| A6 `contributing_runs.json` | A = B `cef41bd731ca3fd8c8bac474dc85e91eba21319245590687025352ffa564b67b` |
| A6 `incidence_per_run.json` | A = B `11daa8dd34db6d882c440b654f31747a6de68d616d37c700008ab0dee8cf6320` |
| A6 `LADDER.json` | A = B `66cd8b49eb510eb7950ae7c4321e862793fb0598ce434665ba69822a3a5f5086` |
| A6 `reading.json` | A `86a8a3cfb08f5677141766ada595e85a24a882739ddfc360c298b828731d2c25`; B `44b946c8c259f5de51779e4a276bf3d24fbfc503e7b2472585999484ec96d3a8` (not compared) |
| A6 `SEAL.json` | A `26aa3dbeec32e805ec338b8896a3cddb320f4e0419b45bc7fba63b68eae808d0`; B `39df6a04c2e8f3eb00a9c286aa3325508a8f013a1ccfd7614b9dc3b35f821d71` (not compared) |
| A6 `quantities_sha256` | A = B `847f0058432cb5874e2b63ca2d0f1616dfe280fff88812d979aeed6a546d428e` |

Flags (run1 = run2, both = separate, run2 hashes = run1 hashes) true in both builds and components: yes.

#### F08b: identical

| Component / file | sha256, A and B (one value where equal) |
|---|---|
| A10 `values.json` | A = B `ccc3e6b38308297b74f558be1c5431968884761ba9c4eefde7641d3b52e67665` |
| A10 `contributing_runs.json` | A = B `ca5ee6f5dbe5d38a74f76dcce682abdc6bdbe2c04bceef2d7e44a2466e8459bd` |
| A10 `incidence_per_run.json` | A = B `d9e587ca2b3cc608f46c42778bd355ccc599a468ac934ce42c5cd79ed44aece9` |
| A10 `LADDER.json` | A = B `11fdbcfb5658a015a324e1089c96de1b94d5d1b42ed906c773f9fbf0aa045214` |
| A10 `reading.json` | A `39f9c0102740a705cd781b5bda280974006e3fa129f8576535cdd06eec678ddd`; B `ad94e583f83066293cba4d22006f8371c4138de80c9b68acf9df18f6bdbc17cf` (not compared) |
| A10 `SEAL.json` | A `f8e2fc67818541c5d26b034d9984b0b50038592d3ff7cf1796d75822cd471cb7`; B `c5a3c3385b6ac11ac7f06e2c17d11b148dac99cddd6117b966abcb52886d02ea` (not compared) |
| A10 `quantities_sha256` | A = B `e869cddcdb02a1684d34200273130c235e5f7a0591d292786339b9a525ab37ce` |
| A6 `values.json` | A = B `cdda391241d095de069ded521a27166d6ee9bb93feccee064bb913d1562bc0cd` |
| A6 `contributing_runs.json` | A = B `fedf2d94d75da3307503308dbe1ad101882019dcf704c008503de075890c3d8a` |
| A6 `incidence_per_run.json` | A = B `91bab9ce7347c12eebf9fa7acf6af5e0a83397fef3c81ff3dba0ba2d8cb58653` |
| A6 `LADDER.json` | A = B `6eccafc3963c8a9584f4ccd8ba0b92b0a8e1845642d676b05bcc6fe18e3c2637` |
| A6 `reading.json` | A `8e25addc3f5f1ca9a6ee98eff60516e50d33fd3a8ec48f6436646fef2721b5d8`; B `c6af5820c2b7f702deddea8e232e654dd7a22852c823a7be959abb1dcae26a20` (not compared) |
| A6 `SEAL.json` | A `be01c9b3b6f6d1d3187f8cbfcc6e2c59796a6eccf3a9c0a1ac28c869b2815595`; B `b552b8b06f84262f154113e2b2f28a72b78685e6cc338573f46f75071c4078b4` (not compared) |
| A6 `quantities_sha256` | A = B `1e59aba828803e5be54794f823040987995fbc6e462ad224812e10ce93fe84ff` |

Flags (run1 = run2, both = separate, run2 hashes = run1 hashes) true in both builds and components: yes.

#### F13a: identical

| Component / file | sha256, A and B (one value where equal) |
|---|---|
| A10 `values.json` | A = B `ccc3e6b38308297b74f558be1c5431968884761ba9c4eefde7641d3b52e67665` |
| A10 `contributing_runs.json` | A = B `ca5ee6f5dbe5d38a74f76dcce682abdc6bdbe2c04bceef2d7e44a2466e8459bd` |
| A10 `incidence_per_run.json` | A = B `d9e587ca2b3cc608f46c42778bd355ccc599a468ac934ce42c5cd79ed44aece9` |
| A10 `LADDER.json` | A = B `11fdbcfb5658a015a324e1089c96de1b94d5d1b42ed906c773f9fbf0aa045214` |
| A10 `reading.json` | A `3e4813abce0e0202519d768964dc4cedcfff068aa59a8c2355cbb8f05cd95bc4`; B `adce1a7affb3858dcd97acef53175a89f0ef1d02bd30d9bada7046ba8306bdb2` (not compared) |
| A10 `SEAL.json` | A `2b4439a9266c212047cf2f465c7e84fda9688029d22c80875a996366702913ee`; B `4f69cc597fd1f16c83a60a3c52ad54a92f8b515fd10524db87fc199a90273ff7` (not compared) |
| A10 `quantities_sha256` | A = B `e869cddcdb02a1684d34200273130c235e5f7a0591d292786339b9a525ab37ce` |
| A6 `values.json` | A = B `64ea37f0487df28dc4f43ef33b6f27b8228bd4dbcd632a9ccaa8190e8fa5e747` |
| A6 `contributing_runs.json` | A = B `d5989a5bcb0cb9bca290f4a4018d98ff7e6e5796ccc609a2b9700cf00a0ebfff` |
| A6 `incidence_per_run.json` | A = B `2ab9cc10dd601f0aa5e7e28937d929673d87a45d1bd141c43d25514357724dd7` |
| A6 `LADDER.json` | A = B `e62bc3c0042d199294e898462306b9197f225b67f2ec33b04c698bfaf12577d3` |
| A6 `reading.json` | A `0e92e4eb32762f6bb0b91f486a934d54f25953bd5b8481e9c635bbf4270aa6ed`; B `2d9909324fb3c998c8efec4e078cfacb6714664b9ac0c70cc736327545ff8a3c` (not compared) |
| A6 `SEAL.json` | A `6c880a786041ea8ffc24ed0b333388b9faf8693097c07a9acd07adb1ed6e2aed`; B `97e158e6efa42b24fffe8f5cf28069fe3c6da331483bbab30ea9eb502311a212` (not compared) |
| A6 `quantities_sha256` | A = B `6dcaefe2e6327ecd110d1d871a971ff67c20d379ae30d6b916433d6f9e65d53b` |

Flags (run1 = run2, both = separate, run2 hashes = run1 hashes) true in both builds and components: yes.

#### F13a2: identical

| Component / file | sha256, A and B (one value where equal) |
|---|---|
| A10 `values.json` | A = B `ccc3e6b38308297b74f558be1c5431968884761ba9c4eefde7641d3b52e67665` |
| A10 `contributing_runs.json` | A = B `ca5ee6f5dbe5d38a74f76dcce682abdc6bdbe2c04bceef2d7e44a2466e8459bd` |
| A10 `incidence_per_run.json` | A = B `d9e587ca2b3cc608f46c42778bd355ccc599a468ac934ce42c5cd79ed44aece9` |
| A10 `LADDER.json` | A = B `11fdbcfb5658a015a324e1089c96de1b94d5d1b42ed906c773f9fbf0aa045214` |
| A10 `reading.json` | A `6b0a5ec597b8919162505b8765fcb051155165480103a012d9603ddf7cf98d22`; B `c32b3c15391d711299394efef98cc81373fcbe5ff1c648a5086d15fd10dfba1f` (not compared) |
| A10 `SEAL.json` | A `0e6bf0be70488cba7817ac895ba30285344ac60367df5ce2f852498de5f6c7a8`; B `7098f8d87544d612c736867779aedd9ce3fd9a3391741fba25b66a26892a3e4d` (not compared) |
| A10 `quantities_sha256` | A = B `e869cddcdb02a1684d34200273130c235e5f7a0591d292786339b9a525ab37ce` |
| A6 `values.json` | A = B `fdcfd14a9f9652ad23de4217fbe01e87e9dbe2d8ef351d31fd64db56e4501f48` |
| A6 `contributing_runs.json` | A = B `d0a22154d2620605d0469dbed2f0e3d91b80d2785e5ed14a2fc248cec757183a` |
| A6 `incidence_per_run.json` | A = B `bd92caceba27a8d51fe0ed364ee1d259be262581a9de5fae817d1686cc31b0b4` |
| A6 `LADDER.json` | A = B `11cd7d532e760176440ce319038c68fc413ebaa5d7dfcc4189948ca7a34208a2` |
| A6 `reading.json` | A `d5815cde33034c6dd0f3ad7c4b608480cfa8c1cd995f24230d6239de42a21da7`; B `dff4182d1dc919db98b08155e6f0a7939ed9cf999aa87ca2a07c33b6695c59b9` (not compared) |
| A6 `SEAL.json` | A `f9dc4b3741914aca7e4ebd5e0f35a4d1ff5115f1dba4514c7e5f8a54fe7ffd01`; B `b832b27df4970b0885525484e62444e5333b51a54c89c9e2e71486824d9ad541` (not compared) |
| A6 `quantities_sha256` | A = B `4977d9395860209e58a988c74bc3505e8050b7d607fa4590fc99efaa37b98d32` |

Flags (run1 = run2, both = separate, run2 hashes = run1 hashes) true in both builds and components: yes.

#### F13d: identical

| Component / file | sha256, A and B (one value where equal) |
|---|---|
| A10 `values.json` | A = B `ccc3e6b38308297b74f558be1c5431968884761ba9c4eefde7641d3b52e67665` |
| A10 `contributing_runs.json` | A = B `ca5ee6f5dbe5d38a74f76dcce682abdc6bdbe2c04bceef2d7e44a2466e8459bd` |
| A10 `incidence_per_run.json` | A = B `d9e587ca2b3cc608f46c42778bd355ccc599a468ac934ce42c5cd79ed44aece9` |
| A10 `LADDER.json` | A = B `11fdbcfb5658a015a324e1089c96de1b94d5d1b42ed906c773f9fbf0aa045214` |
| A10 `reading.json` | A `62c23787ef511311e4209e3dcd0c9bc09b8a7ce11e2a44775b2d962e20346185`; B `45c75e5fddbc85fd212c10367406054afca139b75029a08b4c9ce187a361f086` (not compared) |
| A10 `SEAL.json` | A `6fab0d0a73df0cf9f3a765301f9e6a0772b788222ea0ee85bedf5c13aa1aaa03`; B `91a1c501ee9dcf83c034a2bf111c01b29c04059709702d6b09d2e8e200abe9f4` (not compared) |
| A10 `quantities_sha256` | A = B `e869cddcdb02a1684d34200273130c235e5f7a0591d292786339b9a525ab37ce` |
| A6 `values.json` | A = B `2e299c078608b971cefb18b3556a77326d83ff46a40fd5b1d304e8b0fd8314c6` |
| A6 `contributing_runs.json` | A = B `194d4876945b1ccf2c837a2e6f251a9137769f916a8a6c493c187cf51d2778d9` |
| A6 `incidence_per_run.json` | A = B `dbe73e6ebbfb2c35e896876348b1c7e4f3687ba4bab6f24aaa78a52692eb3fc0` |
| A6 `LADDER.json` | A = B `45f8896becefe5a0b170ecac74d4263864fa202e946fb0687c21feed5f13aa62` |
| A6 `reading.json` | A `24d2cbe6e9490377b5d2ffbddef925d5ce59726a37bd389bafc5ace0a69725f8`; B `dd372368dc3c011402168d291a38f0fa51696745fe85cade3ae44bf4839515f4` (not compared) |
| A6 `SEAL.json` | A `54aa94585baac06fa7cc77e3ac69b1d90fa819776db7eb7d9c0ab4c5d6fd09d0`; B `be8f5a1a0e548de05fe3f24c770965bdfbdd701c9d1a62aa1cd42b45c185a4ad` (not compared) |
| A6 `quantities_sha256` | A = B `0957b40e190132151f175f2489a3780184cd99a07c7d294add0ccdfcf515d1e9` |

Flags (run1 = run2, both = separate, run2 hashes = run1 hashes) true in both builds and components: yes.

#### F13d2: identical

| Component / file | sha256, A and B (one value where equal) |
|---|---|
| A10 `values.json` | A = B `bf9fb04ecd388e6ca9ffdc18b66e393e7ad1f0783d74c2181f1cff61ca50d495` |
| A10 `contributing_runs.json` | A = B `1273f4c53fb39f10e9bce60c57be960dff3d89c2eefb8788938e5866264f2cf3` |
| A10 `incidence_per_run.json` | A = B `dbe73e6ebbfb2c35e896876348b1c7e4f3687ba4bab6f24aaa78a52692eb3fc0` |
| A10 `LADDER.json` | A = B `732d74f39b8271d1bd4bb68773036c41c8c7f17c8ecc805ae3205ce4f3f07003` |
| A10 `reading.json` | A `e8f154a0491b2a5c772323ab705aeeb3ad9ee88871f5574871d8be1267c95119`; B `8dc0af889c2613ad727ba2f7708f31bcb8ca96cc750711b6e0b4814d430e1875` (not compared) |
| A10 `SEAL.json` | A `67ac50868d2c5d9ba6f9b7e62f2878f8dff808297304560adba6fbe82a948198`; B `15d583a9378b4ef59029769afb2b548423e92e84e65b64042aa4f2a8b9393934` (not compared) |
| A10 `quantities_sha256` | A = B `d9435195cb21d154a4ed37234a20989c601d4029bccd9de1eb9ef429eb316dbc` |
| A6 `values.json` | A = B `c0ffb5918d45d316a0ad60f413f2de94e812bbe404c6b08618d3e6760851dfb8` |
| A6 `contributing_runs.json` | A = B `b1572ef254d12311f96ce050b72e8e6625b90519a46e8cb94a886fcc5cab4299` |
| A6 `incidence_per_run.json` | A = B `199194d879ecbdf2a07f8b56199d0c43a0725c36390746e3bdd8a27bc06d7cd3` |
| A6 `LADDER.json` | A = B `a4bccad814834ba89e09c965eaa939d76ca54a8f239fab55be1587edfa30bc65` |
| A6 `reading.json` | A `2021a27e9a5e62751383a491b0a05dc1ace38f0fd0dd100e4e77c7993f93d842`; B `62b246698231ff66235dc15d8528ee53e9dd2e5f157973c3e8bf17436e9245fc` (not compared) |
| A6 `SEAL.json` | A `7051b9bad135aec4fc2992ec80492d30cca166fcfa56f8f038859170e5644a0f`; B `6d8f05744fd02014db77fa42b3b8b182eca1bc7adf2d9ddfe6a85b83879db61f` (not compared) |
| A6 `quantities_sha256` | A = B `35267be9a781cb94caecb0ff84b661d78a22164fbcfffa46419d1a7827549abb` |

Flags (run1 = run2, both = separate, run2 hashes = run1 hashes) true in both builds and components: yes.

#### F13e: identical

| Component / file | sha256, A and B (one value where equal) |
|---|---|
| A10 `values.json` | A = B `ccc3e6b38308297b74f558be1c5431968884761ba9c4eefde7641d3b52e67665` |
| A10 `contributing_runs.json` | A = B `ca5ee6f5dbe5d38a74f76dcce682abdc6bdbe2c04bceef2d7e44a2466e8459bd` |
| A10 `incidence_per_run.json` | A = B `d9e587ca2b3cc608f46c42778bd355ccc599a468ac934ce42c5cd79ed44aece9` |
| A10 `LADDER.json` | A = B `11fdbcfb5658a015a324e1089c96de1b94d5d1b42ed906c773f9fbf0aa045214` |
| A10 `reading.json` | A `92d72471b11070192ee1e56f4cf637d2d4739a29460135c6e8e2bc1c400d8efc`; B `cac6051c4db8a20b0e8300dc9d3a3ef0d2359d361e103f2f1ca09754605b004d` (not compared) |
| A10 `SEAL.json` | A `b84ea6dd9a5f76fcb7307f611ba9443028e5b40022b037ab1aa06f9e049f804f`; B `2e646c958c57a358d0cc0521c2b54cb57c4bb606a53be7536446e842912b4d15` (not compared) |
| A10 `quantities_sha256` | A = B `e869cddcdb02a1684d34200273130c235e5f7a0591d292786339b9a525ab37ce` |
| A6 `values.json` | A = B `c96238382bc576988cf23f72c19dde0b411fbb91470e20ec26f98e38a68bb32c` |
| A6 `contributing_runs.json` | A = B `8eb4bf0aadbbd282ea8964906164b4fd5c2bccca6888c859f13a5a7b61ce057b` |
| A6 `incidence_per_run.json` | A = B `0c081cb028420e5977934a983b9af289acd69000a7601ea712f7a9cbca5edca6` |
| A6 `LADDER.json` | A = B `5eadd8311211ca3e7d5ad836584c969626d6b46cf7adac5efadde89fb0b87184` |
| A6 `reading.json` | A `944b7ec4ffe149cce1b611239e38f35122a8d143ff82c7a514d2ba0e665baca9`; B `e1b7c7b6067fe6bfe1697537ab0474e860e82973250d32fc28665a4186e139f5` (not compared) |
| A6 `SEAL.json` | A `cff30dcac92689d32ecdf3ae1c715457085ecc592923828321d8b764b961e84e`; B `057bbcdd447ce2bf297c54ccb0821fc6aa3f09a3696f9eb5fe1564e5ba049beb` (not compared) |
| A6 `quantities_sha256` | A = B `b754f04298ffa2282d528a71bf47790b47667ce9f1210ab229b2f411c670a0eb` |

Flags (run1 = run2, both = separate, run2 hashes = run1 hashes) true in both builds and components: yes.

#### F13e2: identical

| Component / file | sha256, A and B (one value where equal) |
|---|---|
| A10 `values.json` | A = B `ccc3e6b38308297b74f558be1c5431968884761ba9c4eefde7641d3b52e67665` |
| A10 `contributing_runs.json` | A = B `ca5ee6f5dbe5d38a74f76dcce682abdc6bdbe2c04bceef2d7e44a2466e8459bd` |
| A10 `incidence_per_run.json` | A = B `d9e587ca2b3cc608f46c42778bd355ccc599a468ac934ce42c5cd79ed44aece9` |
| A10 `LADDER.json` | A = B `11fdbcfb5658a015a324e1089c96de1b94d5d1b42ed906c773f9fbf0aa045214` |
| A10 `reading.json` | A `dcc55109066551c09e1e0106ceebf550f052595b1fe1940e3973cefd3b4ec0d7`; B `215321c8509ef563b212683d1bfd137fba6f818e3f794d865082c29be2f3b933` (not compared) |
| A10 `SEAL.json` | A `011d4130f5e2d0138daed1abf290a6bb3d6dcbc7603502d5e518d2eb60628141`; B `ba33ae4dfafcafb79ecce7653033dd632978829b6f036fe4585a4eb6b10d1126` (not compared) |
| A10 `quantities_sha256` | A = B `e869cddcdb02a1684d34200273130c235e5f7a0591d292786339b9a525ab37ce` |
| A6 `values.json` | A = B `19e6165bdc7713aca7fc643b2c4e65bf652d8dd95f401b3f7332e7cbf337a64b` |
| A6 `contributing_runs.json` | A = B `8eb4bf0aadbbd282ea8964906164b4fd5c2bccca6888c859f13a5a7b61ce057b` |
| A6 `incidence_per_run.json` | A = B `704624ca6a34e47518ef50db1e37da59dbf3b9080692df549a61b158f7ec5b07` |
| A6 `LADDER.json` | A = B `f2e076f4ad01054b4294178227a12ae4e0b14e4ca82d1a53aec27e7682d06cb6` |
| A6 `reading.json` | A `b65d1231c0b11a22e8d29dcb292c887981fced19255f9fe97bc797d0e51c2204`; B `83f1410648ceee4a99f7a7145b8301368ee01f6e14fa63ba3beeb741f965ca50` (not compared) |
| A6 `SEAL.json` | A `6a4c5931d7d642f7ea671bb144911580cc5614fed469bfc608ff8617230a5e10`; B `a68abbd59535f64df871a65f6a900c15560e1f5215f91a31bfe375ceb604383c` (not compared) |
| A6 `quantities_sha256` | A = B `b754f04298ffa2282d528a71bf47790b47667ce9f1210ab229b2f411c670a0eb` |

Flags (run1 = run2, both = separate, run2 hashes = run1 hashes) true in both builds and components: yes.

#### F13e3: identical

| Component / file | sha256, A and B (one value where equal) |
|---|---|
| A10 `values.json` | A = B `ccc3e6b38308297b74f558be1c5431968884761ba9c4eefde7641d3b52e67665` |
| A10 `contributing_runs.json` | A = B `ca5ee6f5dbe5d38a74f76dcce682abdc6bdbe2c04bceef2d7e44a2466e8459bd` |
| A10 `incidence_per_run.json` | A = B `d9e587ca2b3cc608f46c42778bd355ccc599a468ac934ce42c5cd79ed44aece9` |
| A10 `LADDER.json` | A = B `11fdbcfb5658a015a324e1089c96de1b94d5d1b42ed906c773f9fbf0aa045214` |
| A10 `reading.json` | A `66ee9cd4d9e8beb9a02966aec3c2d7a2451bbbd6d1a5038026a37a5cae7405a6`; B `9b727a65468a9b597fe48870611fd8202340318891ea6d7b2e56f19cbd9afc7f` (not compared) |
| A10 `SEAL.json` | A `2abacf40e251a35da1a90bb6f39bae64fc9b60ead43d003ed4feb92f4f7038fa`; B `3c4e191b1c6030172e075d65dfe4326afb824d0e356ae1e9961f672e6584a364` (not compared) |
| A10 `quantities_sha256` | A = B `e869cddcdb02a1684d34200273130c235e5f7a0591d292786339b9a525ab37ce` |
| A6 `values.json` | A = B `b29bb3eed3bf3c10c823e2ea18ab69efc5e60f234c83639c929aee2cc8a0b6b8` |
| A6 `contributing_runs.json` | A = B `8eb4bf0aadbbd282ea8964906164b4fd5c2bccca6888c859f13a5a7b61ce057b` |
| A6 `incidence_per_run.json` | A = B `24c3ffbf25a06c2ee908d147e9b5a3eedd0187221fe7fb3c9d658abc4a6d2c8c` |
| A6 `LADDER.json` | A = B `840bb962def3f260bf03797cf9b32790b546f12e928631bb92bfe6b550720190` |
| A6 `reading.json` | A `402c977639085c0227a5a2e36828713d6949f7194a771affc9c1f50629ec9792`; B `5e178536ede00157974f958423b4b417eda5f89d8f94814d094e655b07e89b93` (not compared) |
| A6 `SEAL.json` | A `322bf95af0eb145eb7ffa05235d4168f3d785ba38e557ed2baeefd65139c4651`; B `93bd51d4b01cf1e8b70dd064e2a70ae41b6ec8dc93150288c5a3b836bc735eaa` (not compared) |
| A6 `quantities_sha256` | A = B `b754f04298ffa2282d528a71bf47790b47667ce9f1210ab229b2f411c670a0eb` |

Flags (run1 = run2, both = separate, run2 hashes = run1 hashes) true in both builds and components: yes.

#### F13e4: identical

| Component / file | sha256, A and B (one value where equal) |
|---|---|
| A10 `values.json` | A = B `ccc3e6b38308297b74f558be1c5431968884761ba9c4eefde7641d3b52e67665` |
| A10 `contributing_runs.json` | A = B `ca5ee6f5dbe5d38a74f76dcce682abdc6bdbe2c04bceef2d7e44a2466e8459bd` |
| A10 `incidence_per_run.json` | A = B `d9e587ca2b3cc608f46c42778bd355ccc599a468ac934ce42c5cd79ed44aece9` |
| A10 `LADDER.json` | A = B `11fdbcfb5658a015a324e1089c96de1b94d5d1b42ed906c773f9fbf0aa045214` |
| A10 `reading.json` | A `6628d8de6568722a3c655ce0b2d5c3a118292dcd8434e003c71938fd160faeb8`; B `50fb50ddd294c6a43ce79fadcc9883ebdf91fce9d967779edba1e0ba48cf276e` (not compared) |
| A10 `SEAL.json` | A `bf3dbbeb06048f915bc56d603da5d2dc0674ff7fa73e839d06adf001c7f499c8`; B `510234c37905c244b04b54c06b662a9b504dcf18326ee32a7dd45f45893de663` (not compared) |
| A10 `quantities_sha256` | A = B `e869cddcdb02a1684d34200273130c235e5f7a0591d292786339b9a525ab37ce` |
| A6 `values.json` | A = B `c96238382bc576988cf23f72c19dde0b411fbb91470e20ec26f98e38a68bb32c` |
| A6 `contributing_runs.json` | A = B `8eb4bf0aadbbd282ea8964906164b4fd5c2bccca6888c859f13a5a7b61ce057b` |
| A6 `incidence_per_run.json` | A = B `0c081cb028420e5977934a983b9af289acd69000a7601ea712f7a9cbca5edca6` |
| A6 `LADDER.json` | A = B `5eadd8311211ca3e7d5ad836584c969626d6b46cf7adac5efadde89fb0b87184` |
| A6 `reading.json` | A `fecfef42521216b7a86d96f0f32b4aa171b112b94491f34be8d520ce068bb11b`; B `e1760c489e5dcba17bbfcf1c6cadc1a6b4899ca46d883f2e99a1e313daa30e1c` (not compared) |
| A6 `SEAL.json` | A `b8643183a9dced1fd1daf3f6a2f8e5bbb3ea9539781a0044da1ece2521a7eecc`; B `19e4acc7dc40dfbe9778a719bb6ee25fc27cfc921017a67051ae37c872719b3e` (not compared) |
| A6 `quantities_sha256` | A = B `b754f04298ffa2282d528a71bf47790b47667ce9f1210ab229b2f411c670a0eb` |

Flags (run1 = run2, both = separate, run2 hashes = run1 hashes) true in both builds and components: yes.

#### MAIN: identical

| Component / file | sha256, A and B (one value where equal) |
|---|---|
| A10 `values.json` | A = B `ccc3e6b38308297b74f558be1c5431968884761ba9c4eefde7641d3b52e67665` |
| A10 `contributing_runs.json` | A = B `ca5ee6f5dbe5d38a74f76dcce682abdc6bdbe2c04bceef2d7e44a2466e8459bd` |
| A10 `incidence_per_run.json` | A = B `d9e587ca2b3cc608f46c42778bd355ccc599a468ac934ce42c5cd79ed44aece9` |
| A10 `LADDER.json` | A = B `11fdbcfb5658a015a324e1089c96de1b94d5d1b42ed906c773f9fbf0aa045214` |
| A10 `reading.json` | A `8ead72abe2739cda86fe9b9906adae0d1d38e2bb0c56060a7b8c8c13e35e36ef`; B `65c89bf7edbfaa22677602a5842e6a4509004f4bc157a5f3eabc7952e86961ec` (not compared) |
| A10 `SEAL.json` | A `4a6ec4771b881533840767f9ae1d2ff538ef2f0fa07607dade48118da386e8ac`; B `aaf44d7bc082b80c32fc26a35e30e4fbcca961f4aabcfdb903fae50089f3ffaa` (not compared) |
| A10 `quantities_sha256` | A = B `e869cddcdb02a1684d34200273130c235e5f7a0591d292786339b9a525ab37ce` |
| A6 `values.json` | A = B `c0ffb5918d45d316a0ad60f413f2de94e812bbe404c6b08618d3e6760851dfb8` |
| A6 `contributing_runs.json` | A = B `b1572ef254d12311f96ce050b72e8e6625b90519a46e8cb94a886fcc5cab4299` |
| A6 `incidence_per_run.json` | A = B `199194d879ecbdf2a07f8b56199d0c43a0725c36390746e3bdd8a27bc06d7cd3` |
| A6 `LADDER.json` | A = B `a4bccad814834ba89e09c965eaa939d76ca54a8f239fab55be1587edfa30bc65` |
| A6 `reading.json` | A `6b87fc0f4d173f33376bd6dbfbade4e4f04aa291f32da0c5552bc8214fd3a63a`; B `aad55087a29f07ede40fa6c835fa31c308d6ef070c461a5139d8c208c6831ff0` (not compared) |
| A6 `SEAL.json` | A `ec9792e03c06e189414f6b002c91c383fe05a145f0abc3a96a0580c3ea7bf8d5`; B `559aca15dffb11707fe4c40e76cfa2336d39a7157dc6032be601efcaccfe035a` (not compared) |
| A6 `quantities_sha256` | A = B `35267be9a781cb94caecb0ff84b661d78a22164fbcfffa46419d1a7827549abb` |

Flags (run1 = run2, both = separate, run2 hashes = run1 hashes) true in both builds and components: yes.

`reading.json` and `SEAL.json` differ between builds on every sealed component and are not D 8.3 compared files. The second check found `SEAL.json` differing only at `collection_sha256`, `reader_identity`, the `reading.json` hash and its own seal [R].

### The verdict

- **`S/builds_checks/interpreter/compare_ab_round2_v2.txt`** (sha256 `f3a4e8facca7978487daee13728dcd2832942b2b0b5ef1f46eff7e414cfd098f` [M]): [R] counts {'both sealed': 12, 'both collected': 48, 'both refused': 38, 'manifest fixtures checked': 50}; the only findings listed are 2 'C5 not checkable' (MAIN reference.twin_oracle_summary, both builds) and 35 'obs label wording' lines, which D 8.3 item 4 permits; no differing criterion is listed. Produced by the repaired compare_ab.py (fe04710c...b8c6, DECISIONS s15).
- **`S/builds_checks/round2_comparison_check/REPORT.md`** (sha256 `c4a4541dcc8cf26bcc0effec593fb6b0bc8022456ae8ae8e755d47b5552720cc` [M]): [R] Verdict CONFIRMED WITH FINDINGS. Independent code agrees with the interpreter on every criterion; 864 of 864 reported output hashes match the files on disk; the four compared files are byte-identical across builds on all 12 sealed fixtures; every expectation name matches the manifest; `not checkable` appears only for MAIN reference.twin_oracle_summary in both builds. Its findings were gaps in compare_ab.py, repaired per DECISIONS s15.

## 7. The comparison tools

- **`S/builds_checks/interpreter/compare_ab.py`:** sha256 `fe04710ce3a0e4b7dcfd35aaa3b3f9996d27f34f48c7d2028ae933671ff7b8c6` [M]; equals the repaired script fe04710c...b8c6 named in DECISIONS s15 [M against R].
- **Build A `values_compare`:** `BA/repo/simulation/reading_stage2_tools/values_compare.py`, sha256 `1bbd6a8f304589a251677843be88decc65893b1c971ff8af5c0807fdaace605d` [M].
- **Build B `values_compare`:** `BB/repo/simulation/reading_stage2_tools/values_compare.py`, sha256 `1851add7c9db093800ad18aa2ef3f0af0bb4c685f8dd72ed901e7867fcec4264` [M].

## 8. Parse rate and memory peak: measurements on synthetic data

These are measurements on synthetic data, not on registered inputs [R]. Conditions: fixture MAIN, 284 run outputs (701.1 MB), 634 files and 939.8 MB per pass, warm page cache; WSL Ubuntu-20.04, phaseb Python 3.13.12, NumPy 2.4.4; one process, one numerical thread.

| Reader | `verify` whole-pass rate | `read --component both` whole-pass rate | s per output (verify, read) | Strict-parse rate of run outputs | Peak RSS |
|---|---|---|---|---|---|
| A | 16.3 MB/s (42.90 s, range 42.56 to 43.76, n = 3) | 15.9 MB/s (43.97 s, range 43.74 to 45.06) | 0.151, 0.155 | 171.5 MB/s | 1,126,472 kB (1.07 GiB) |
| B | 16.4 MB/s (42.68 s, range 41.85 to 42.94) | 16.1 MB/s (43.51 s, range 43.39 to 43.97) | 0.150, 0.153 | 170.7 MB/s | 1,029,268 kB (0.98 GiB) |

**Projection [I]:** Reader A retains about 0.37 MiB per contributing output until G7 ends (synthetic replay, 16,025 outputs); projected peak about 7 GiB at registered scale [I]. Reader B about 1.4 GiB [I].

The whole-pass rate, not the strict-parse rate, is the figure that replaces D 9.2's assumed parse rate. [R]

Verbatim source:

Source: S/probe/check/REPORT.md section 4, lines 172-180, lines 172-180. File sha256 `20be22b2a20912b46f4c1e532156b8790ae966fab4e39a1318157b80e9d1a922`; excerpt sha256 `35ea6d1e9e590074ca37be453465316bb1714829da0b4b36f506dbf28e13c6d2` [M].

> ## 4. What the freeze record can state (D 8.4)
>
> These are measurements on synthetic data: fixture MAIN, 284 run outputs (701.1 MB), 634 files and 939.8 MB per pass, warm page cache. They were taken on this workstation (WSL `Ubuntu-20.04`, phaseb Python 3.13.12, NumPy 2.4.4), with one process and one numerical thread.
>
> - **Reader A.** The whole-pass rate is 16.3 MB/s of output bytes for `verify` (median 42.90 s, range 42.56 to 43.76, n = 3) and 15.9 MB/s for `read --component both` (43.97 s, range 43.74 to 45.06). That is 0.151 and 0.155 s per output. Strict parsing of run outputs alone, with A's own `loads`, runs at 171.5 MB/s. Peak RSS is 1,126,472 kB (1.07 GiB).
> - **Reader B.** The whole-pass rate is 16.4 MB/s for `verify` (42.68 s, range 41.85 to 42.94) and 16.1 MB/s for `read --component both` (43.51 s, range 43.39 to 43.97). That is 0.150 and 0.153 s per output. Strict parsing of run outputs alone runs at 170.7 MB/s. Peak RSS is 1,029,268 kB (0.98 GiB).
> - **A recommended addition, labelled as a projection.** "Reader A retains about 0.37 MiB per contributing output until G7 ends (synthetic replay, 16,025 outputs); projected peak about 7 GiB at registered scale [I]. Reader B about 1.4 GiB [I]."
>
>   The whole-pass rate, not the strict-parse rate, is the figure that replaces D 9.2's assumed "parse rate".

## 9. Also recorded

### Open literal readings no addendum settles [R]

Build B:

Source: S/builds/B/executor_final_message_r2.txt section 4, lines 83-92: RQ-3, RQ-8 (type part), RQ-11 (first part), RQ-15, RQ-17, RQ-19, lines 83-92. File sha256 `6bddfa728a647db0d5f4b7ffcf249fef0bfe913a28514d65cf354899d0f6dcfe`; excerpt sha256 `fd29e5041d2e22c58af12c86b90492df948708691336b33c64d6c20f6a1b3ee4` [M].

> | # | Question | Reading | Where |
> |---|---|---|---|
> | RQ-3 | `path_map`'s form | accepted as a key in fixture mode, refused in registered mode, maps nothing | `inputs.py:66` |
> | RQ-8, type part | G5's native types against D:455's bool precondition | G5 tests the two flags' presence; D:455's precondition tests their type, under A6.1's label | `gates.py:273` |
> | RQ-11, first part | the sqrt admission record | the authorized hash always binds it; an inventory entry too when there is one | `gates.py:422` |
> | RQ-15 | `n_agents` in fixture mode | allowed only with value 0 | `gates.py:216` |
> | RQ-17 | sources of `family.<name>.admission` | counts from the binding admission record; `admitted_rows` from the loaded binding | `gates.py:855` |
> | RQ-19, new | A11.2 says `collect` tests none of the four structures beyond the leaf rule. A10.3b's form includes "the value types in those places" | `collect` refuses a `registration` that is not an object (a top-level value type) and an arm `family` that is not an object (a value type of the arm's key set). It tests nothing inside either. Under the leaf rule alone, a `family` that is a string would instead be one leaf | `inputs.py:67`, `:91` |
>
> RQ-19 cannot change a collection's bytes or a refusal's phase. It can move which command first refuses a document whose `registration` or `family` is not an object.

Build A:

Source: builder A's round 2 final message in S/builds/A/ line 140: Q1 and Q2, lines 140-140. File sha256 `fae77c3a09a5e9b3641e406d0f22db146c1dd777cf25e11692892f82f02c9767`; excerpt sha256 `4f413a589a512e7a9cfb5f9629bad40bcd2e531993b36d8a5970be076a9a1f62` [M].

> [R/M] Q1 and Q2 remain unruled. contracts.py:36 permits fixture-only integer n_agents=0 structurally, without fixture IDs. contracts.py:43 retains an inert optional fixture path_map object and rejects it in registered mode; explicit operator paths are used. Q3-Q6 remain resolved by Addendum 10. No new rule question was needed.

[R] No addendum settles these. DECISIONS s15 records them as affecting no criterion.

### Operator decisions the record rests on [R]

Section 14 is the only operator decision of the two. Section 15 is the interpreter's record of rounds 1 and 2 and Addendum 11, on which this record also rests.

Source: DECISIONS_2026-11-22.md section 14, lines 411-423; operator's words recorded at transcript 2026-11-23T10:40:33Z, lines 411-423. File sha256 `f9eb399778bc9ef6cbdcac5deb8b0d0d48788f531f92a855365205184d9e7849`; excerpt sha256 `313d5f323ceb2e3f22efc3c8bf110aa61871680a7b6d42c5353306c9b64385ef` [M].

> ## 14. "approve A6.2 addition, keep A6.4a, sigma inventories at 93a453b2"
>
> **The operator's words** (transcript 2026-11-23T10:40:33Z): "approve A6.2 addition, keep A6.4a, sigma inventories at 93a453b2"
>
> **Decision:**
> 1. **A6.2 item 1 is amended,** as Addendum 10's Events paragraph states. It now reads: "`verify` refuses, `collect` refuses, or the two collection folders of A10.3d differ;". Each takes the A6.3 route.
> 2. **A6.4a and A6.4 step 3 stay as adopted.** A refused pass writes only `refusal.json` and no ladder. Addendum 10's amendment of those two sentences is withdrawn: A10.3c's "a component folder sealed before the refusal stays" and the matching sentences of A10.3d's Events paragraph.
>    - Under `read --component both`, a reader computes and holds both components and writes no component file until both have passed every check. A refusal before publication then leaves `<out>` holding only `refusal.json`. An interruption during publication itself remains A6.4 step 1's partial-folder case.
>    - The interpreter will state this in Addendum 11, with its second check, repair round and final check. Both builders then apply it in round 2.
>    - No fixture reaches this path (refusing fixtures refuse at `verify`), so round 1's comparison is unaffected.
> 3. **Item 42 makes the two σ inventories from a checkout at code identity `93a453b2…`,** as the comparator inventory was made (A10.5 item 4). The inventories themselves still need their own go when item 42 comes up.
>
> **Not covered:** the freeze, any commit, and item 42's launch.

Source: DECISIONS_2026-11-22.md section 15, lines 425-456; an interpreter record, not an operator decision (its own heading). Recorded times: round 1 reports B 10:23Z and A 11:18Z; round 2 reports B 12:10Z and A 13:01Z (date 2026-11-23 [I], from section 14's transcript time and B's round 2 report heading; section 15 gives times only), lines 425-456. File sha256 `f9eb399778bc9ef6cbdcac5deb8b0d0d48788f531f92a855365205184d9e7849`; excerpt sha256 `1f945b6d958331202d11888000edc20922a2b011be89fbc0490901954b4d8bf0` [M].

> ## 15. Rounds 1 and 2, and Addendum 11 (interpreter record, not an operator decision)
>
> **Round 1** (Addendum 10).
> - **Reports:** B at 10:23Z and A at 11:18Z. Both BUILT WITH GAPS, all named tests pass, conduct clean.
> - **Comparison** (`builds_checks\interpreter\compare_ab_round1.txt`): every D 8.3 criterion and A10.9 item 5 pass on all 50 fixtures and 24 components. The refusing commands now agree too.
>
> **Addendum 11** (`S\spec\ADDENDUM_11.md`, `0389f2e9…e34d`).
> - **Content:**
>   - the operator's keep-A6.4a decision (s14): nothing is published until every gate, every requested component's computation and the D:275 re-hash have passed, and a refusal before publication leaves only `refusal.json`;
>   - the publication-fault exception, for the operator's acknowledgement;
>   - the exhaustive form list of `collect`;
>   - the recorded decisions.
> - **Checks:** drafted by the interpreter without attributions. Second check NOT READY on two highs, a leak and an overstatement of A6.4a. Final check READY WITH FINDINGS, seven low. All findings taken; dispositions in `spec\drafts\addendum11\INTERPRETER_REPAIR.md`. One adaptation, G3's temporary file outside `<out>`, was read by no check.
>
> **Round 2.**
> - **Reports:** B at 12:10Z and A at 13:01Z. Both BUILT WITH GAPS (registered integration untested), all tests pass including `a11_tests` 3/3, conduct clean. Final identities: A `1c0fca45…ea1d`, B `2ad63b7a…72db`. Results: A `2c51018e…df03`, B `dfb3fe0c…6823`.
> - **Comparison:** `compare_ab_round2.txt` passes every criterion.
> - **Second check of the comparison** (the second checker, `builds_checks\round2_comparison_check\REPORT.md`): CONFIRMED WITH FINDINGS.
>   - Its independent code agrees on every criterion.
>   - 864 of 864 reported output hashes match the files on disk.
>   - The four compared files are byte-identical across builds on all 12 sealed fixtures.
>   - Every expectation name matches the manifest.
>   - Its findings were gaps in `compare_ab.py`. They were repaired by adding manifest-derived expectation names, refusal phase and literal labels against the manifest, the collection tied to `collect`, F16 on all six files, and the briefs' required test names. The repaired script (`fe04710c…b8c6`) reproduces the result (`compare_ab_round2_v2.txt`) and catches all five damage cases of a negative control (`neg_control_compare.py`).
>
> **Open literal readings for the freeze record,** none affecting a criterion: B RQ-3, RQ-8 (type part), RQ-11 (first part), RQ-15, RQ-17 and RQ-19; A Q1 and Q2. Reader identity is defined differently by each build, and identities are never compared across builds.
>
> **Next:**
> 1. The throughput and memory probe (D 8.2 step 6). The interpreter's estimate from round 0 timings puts the item 43 projection above D:724's 6-hour line, so the choice may return to the operator.
> 2. The freeze record (D 8.4).
> 3. The commit request (D 8.5, the operator's go).
>
> Fixture regeneration is not needed for the freeze: A10.9 item 1 and A11.4 apply "at the next regeneration", and the erratum is carried by A10.7.

*One edit to the quote: a model name in DECISIONS line 442 is replaced by 'the second checker'. excerpt_sha256 is of the unedited source lines 425-456.*

### Pending

**The operator's acknowledgement of A11.1 item 4, the publication-fault exception, is pending until he gives it.** The text:

Source: ADDENDUM_11.md A11.1 item 4, lines 36-36. File sha256 `0389f2e99b6211a9b4c1a92ed4f7cb1ed86f8752ae7df45f9a57c2cb244ae34d`; excerpt sha256 `cf70fe0dc2fc9e720e02e19cd52b4a3fc7405218e838f272d7f637b2e4909bff` [M].

> 4. **A failure during publication** is the one way a refused pass can leave more than `refusal.json`. It covers an exception raised while a file under `<out>` is written, fsynced or renamed. The reader deletes nothing under `<out>`, temporary files included [I, from D:474's "written once and never replaced"]. Whatever folder the failure leaves, partial or complete, is hashed, locked and listed at A6.4 step 1, and a partial folder's unlisted files are not compared (A6.4 step 9). The reader writes `refusal.json`, with phase `after_computation_started`, and prints its refusal line (A1.4, A10.3c).

### Gaps in this record

- The R copies of the tools, R/simulation/reading_stage2_tools_a/ and _b/, hold byte_identity.py only. ladder, stream checker and values_compare are hashed in the builders' clones only; they match the builders' round 2 reports and the results files' `tools` blocks [M].
- The fixture outputs' six-file hashes are the builders' reported values [R]; the assembler may not open the outputs. The round 2 comparison check verified them on disk.

