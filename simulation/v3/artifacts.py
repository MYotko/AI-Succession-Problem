"""Canonical artifacts, scoped writes and cross-platform process leases."""
from contextlib import contextmanager
from contextvars import ContextVar
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SIMULATION = ROOT.parent
_INPUT_VIEW = ContextVar('a11_input_view', default=None)


def input_path(path):
    """Resolve a frozen worker input; inactive for all ordinary execution."""
    view = _INPUT_VIEW.get()
    if view is None:
        return path
    resolved = str(Path(path).resolve())
    if resolved in view['paths']:
        return Path(view['paths'][resolved])
    if any(Path(resolved).is_relative_to(Path(p)) for p in view['protected']):
        raise ValueError('A11 input was not in the verified snapshot: ' + resolved)
    return path


@contextmanager
def input_view(view):
    token = _INPUT_VIEW.set(view)
    try:
        yield
    finally:
        _INPUT_VIEW.reset(token)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(input_path(path)).read_bytes()).hexdigest()


def scoped(path):
    result = Path(path).resolve()
    if not result.is_relative_to(ROOT):
        raise ValueError("output outside simulation/v3")
    return result


def atomic_json(path, value):
    path = scoped(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.partial")
    with temporary.open("wb") as stream:
        stream.write(canonical(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    for attempt in range(8):
        try:
            os.replace(temporary, path)
            break
        except PermissionError:
            if attempt == 7:
                raise
            time.sleep(min(.2, .01 * 2**attempt))
    if os.name != "nt":
        fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def read(path):
    for attempt in range(8):
        try:
            return json.loads(Path(input_path(path)).read_text(encoding="utf-8"))
        except PermissionError:
            if attempt == 7:
                raise
            time.sleep(min(.2, .01 * 2**attempt))


def seal(payload):
    return {"payload": payload, "sha256": digest(payload)}


def unseal(document):
    if set(document) != {"payload", "sha256"} or digest(document["payload"]) != document["sha256"]:
        raise ValueError("artifact hash mismatch")
    return document["payload"]


def source_manifest():
    # All root Python dependencies are bundled unchanged. Tests are excluded.
    files = list(ROOT.glob("*.py")) + [p for p in SIMULATION.glob("*.py") if not p.name.startswith("test_")]
    # This reviewed exception is executable provenance, not a generated result.
    compatibility = ROOT / "calibration_compatibility_A1.json"
    if compatibility.exists():
        files.append(compatibility)
    table_compatibility = ROOT / "table_compatibility_A2.json"
    if table_compatibility.exists():
        files.append(table_compatibility)
    repair_compatibility = ROOT / "table_compatibility_A3.json"
    if repair_compatibility.exists():
        files.append(repair_compatibility)
    constants = ROOT / "a10_constants.json"
    if constants.exists():
        files.append(constants)
    return {p.relative_to(SIMULATION).as_posix(): hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest() for p in sorted(files)}


def code_identity():
    return digest(source_manifest())


def stable_job(kind, config, tag, index):
    if tag not in ("pilot", "configuration", "validation", "v3_rerun", "v3_calibration", "v3_tables"):
        raise ValueError("unknown experiment tag")
    base = {"kind": kind, "config": config, "tag": tag, "index": index}
    key = digest(base)
    seed_key = key
    source = config.get("a10_seed_source")
    if source is not None:
        from .instrument import declaration
        if (kind != "rerun" or not declaration(config.get("model", {}).get("instrument")).a10
                or "a10_seed_source" in source or "instrument" in source.get("model", {})):
            raise ValueError("invalid A10 paired seed source")
        seed_key = digest({"kind": kind, "config": source, "tag": tag, "index": index})
    # A disjoint high-bit namespace avoids overlap with legacy 32-bit seeds.
    # The wrapper expands this entropy for the legacy initializer.
    return {**base, "id": f"{kind}_{key[:24]}", "seed": (1 << 128) | int(seed_key[:32], 16), "seed_identity": seed_key}


def configure_threads(count):
    if count not in (1, 2):
        raise ValueError("threads must be one or two")
    for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = str(count)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


def available_cpus():
    if hasattr(os, "sched_getaffinity"):
        return len(os.sched_getaffinity(0))
    return os.process_cpu_count() or 1


def runtime(threads):
    import numpy as np
    verified = []
    libraries = Path(np.__file__).resolve().parent.parent / "numpy.libs"
    for library in libraries.glob("*openblas*"):
        try:
            dll = ctypes.CDLL(str(library))
        except OSError:
            continue
        for symbol in ("scipy_openblas_get_num_threads64_", "scipy_openblas_get_num_threads", "openblas_get_num_threads64_", "openblas_get_num_threads"):
            try:
                query = getattr(dll, symbol)
            except AttributeError:
                continue
            query.restype = ctypes.c_int
            verified.append({"library": library.name, "effective": query()})
            break
    if not verified or any(v["effective"] != threads for v in verified):
        raise RuntimeError("cannot verify the requested NumPy library thread limit")
    return {"machine": platform.node(), "platform": platform.platform(), "python": platform.python_version(),
            "numpy": np.__version__, "available_cpus": available_cpus(), "threads_configured": threads,
            "threads_verified": verified}


@contextmanager
def lease(path):
    path = scoped(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = path.open("a+b")
    acquired = False
    try:
        if os.name == "nt":
            import msvcrt
            stream.seek(0)
            if not stream.read(1):
                stream.write(b"0")
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        acquired = True
        yield
    except (BlockingIOError, PermissionError) as exc:
        if acquired:
            raise
        raise RuntimeError("lease already held") from exc
    finally:
        if acquired:
            if os.name == "nt":
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)
        stream.close()


A13_COMMIT = "48815a655c9f4096ea8ceef35ee277ee0352c7d3"
A14_COMMIT = "17f17ef9cee4b18d70f043a1e097359cd6642693"
# The stage 2 successor pin: the full hash of the commit that carries the adopted
# stage 2 registration text (A10 section 12's dated ceiling amendment A15, and
# A16, adopted with it). It was None until that commit existed and is set once,
# at commit time, to that commit's hash. Set, current A10 launches and
# publications verify strictly against it, and A14 and earlier pins verify
# historically through the callers' selection (table_validation_a4.publish,
# table_labels_a5.publish). Unset (None), current A10 verification requires the
# A14 pin exactly as before. The three selection sites below share these helpers
# so the A13 Part 2 binding cannot drop silently (audit A finding 2).
STAGE2_COMMIT = "ae71028ecc1bcd4a8049eb1fc933cdb725e5fa33"
# The heading of the adopted stage 2 amendment, as bytes, set at commit time
# together with STAGE2_COMMIT. The committed note at the successor pin must
# contain it, as A14's note had to contain A14 (design note line 2558).
STAGE2_AMENDMENT_MARKER = b"### Amendment A16, 2026-10-29: prospective validation extensions for A10 stage 2"
# Text the committed note at the current pin must contain. The successor note is
# a superset of A14's, so A14's markers stay required.
STAGE2_NOTE_MARKERS = (b'Clarified, 2026-10-16: pricing R_max', b'### Amendment A14')


def current_a10_commit():
    """The commit current A10 launches must pin: the successor once set, else A14."""
    return STAGE2_COMMIT or A14_COMMIT


def current_a10_note_markers():
    """The text the committed note at the current pin must contain."""
    if not STAGE2_COMMIT:
        return STAGE2_NOTE_MARKERS
    if not isinstance(STAGE2_AMENDMENT_MARKER, bytes) or not STAGE2_AMENDMENT_MARKER.strip():
        raise RuntimeError('STAGE2_COMMIT is set without its amendment marker')
    return STAGE2_NOTE_MARKERS + (STAGE2_AMENDMENT_MARKER,)


def is_current_a10_pin(commit):
    """Whether a plan's pin is the current A10 pin (full or eight-character form)."""
    current = current_a10_commit()
    return commit in (current, current[:8])


def a13_binding_pins():
    """The pins under which a registered A4 publication applies A13 Part 2's
    admission binding: A13, A14 and the stage 2 successor once it is set."""
    commits = [A13_COMMIT, A14_COMMIT] + ([STAGE2_COMMIT] if STAGE2_COMMIT else [])
    return tuple(form for commit in commits for form in (commit, commit[:8]))


def verify_registration(pin, repository=None, *, instrument=None, historical=False):
    """Read-only Git verification. A supplied hash alone is insufficient."""
    if not pin or set(pin) != {"commit", "path", "sha256"}:
        raise RuntimeError("registered mode needs a pinned, committed pre-registration hash")
    path = Path(pin["path"])
    if path.is_absolute() or ".." in path.parts or not pin["commit"]:
        raise ValueError("invalid pre-registration pin")
    repo = Path(repository or SIMULATION.parent)
    def git(*args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout
    try:
        git("merge-base", "--is-ancestor", pin["commit"], "HEAD")
        committed = git("show", f"{pin['commit']}:{path.as_posix()}")
        from .instrument import declaration
        if declaration(instrument).a10 and b"Amendment A10" not in committed:
            raise RuntimeError("registered A10 requires a design pin containing Amendment A10")
        if declaration(instrument).a10 and b"Amendment A11" not in committed:
            raise RuntimeError("registered A10 requires a design pin containing Amendment A11")
        if not historical and declaration(instrument).a10:
            current = current_a10_commit()
            if (not is_current_a10_pin(pin['commit'])
                    or path.as_posix() != 'simulation/diagnostics/v3_rerun_design_note.md'
                    or any(marker not in committed for marker in current_a10_note_markers())):
                raise RuntimeError('current A10 launches require the %s pin %s'
                                   % ('stage 2' if STAGE2_COMMIT else 'A14', current[:8]))
        if hashlib.sha256(committed).hexdigest() != pin["sha256"] or (not historical and file_hash(repo / path) != pin["sha256"]):
            raise RuntimeError("pre-registration hash is stale")
        if historical:
            return dict(pin)  # Ancestry and committed bytes only; no working note.
        tracked = git("diff", "HEAD", "--", "simulation").strip()
        # Match every file contributing to code_identity, including future
        # non-Python provenance files. Ignored untracked files also fail.
        identities = ["simulation/" + name for name in source_manifest()]
        untracked = git("ls-files", "--others", "--", *identities).strip()
        if tracked or untracked:
            raise RuntimeError("registered source must be committed and clean")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("pre-registration commit cannot be verified locally") from exc
    return dict(pin)
