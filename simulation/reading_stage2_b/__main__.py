"""``python -B -m reading_stage2 collect|verify|read``, run from ``simulation/`` (D:281-285).

    collect --inputs <inputs.json> --out <new-collection-folder>
    verify  --inputs <collection-folder>/inputs.json --out <new-folder>
    read    --inputs <collection-folder>/inputs.json --component A10|A6|both --out <new-folder>

What may reach a terminal (D:540-545, A1.4): on success the component name,
each output file's sha256, the reader identity and counts of files and jobs
verified; on refusal the one line ``REFUSED: <phase>: <reason_class>``, with the
class name of an exception the reader did not raise itself. Never an exception's
text, a traceback, or a value.

A10.3c: ``verify`` takes ``--out``; on pass the new folder holds ``verify.json``,
on refusal only ``refusal.json``. ``read`` writes ``<out>/<component>/`` with the
six files and ``<out>/run_log.json``. A11.1: a refused pass writes only
``refusal.json``; nothing is published before every gate, every computation and
the re-hash have passed, and no success line is printed before ``run_log.json``
is in place. Exit status is 0 exactly when a command passed.
"""
import sys
import time
import warnings

warnings.simplefilter("ignore")

from . import labels  # noqa: E402
from .base import CREATED, document_bytes, write_once  # noqa: E402
from .common import COMPUTATION_STARTED, Refused  # noqa: E402

OPTIONS = {"collect": {"--inputs", "--out"}, "verify": {"--inputs", "--out"}, "read": {"--inputs", "--component", "--out"}}
REQUIRED = {"collect": {"--inputs", "--out"}, "verify": {"--inputs", "--out"}, "read": {"--inputs", "--component", "--out"}}


def parse(argv):
    """A parser that prints nothing: a usage error is a refusal label."""
    if not argv or argv[0] not in OPTIONS:
        raise Refused("usage")
    command, options, rest = argv[0], {}, argv[1:]
    if len(rest) % 2:
        raise Refused("usage")
    for name, value in zip(rest[::2], rest[1::2]):
        if name not in OPTIONS[command] or name in options:
            raise Refused("usage")
        options[name] = value
    if not REQUIRED[command] <= set(options) or options.get("--component", "both") not in ("A10", "A6", "both"):
        raise Refused("usage")
    return command, options


def emit(lines):
    sys.stdout.write("".join(line + "\n" for line in lines))
    sys.stdout.flush()


def refusal_line(phase, label, exception_class=None):
    if label not in labels.ALL:
        label = "unlisted refusal label"
    line = "REFUSED: %s: %s" % (phase, label)
    return line + (" (%s)" % exception_class if exception_class else ""), label


def run(command, options):
    from . import inputs as I
    if command == "collect":
        result = I.collect(options["--inputs"], options["--out"])
        return ["collect: inputs.json sha256=" + result["inputs.json"],
                "collect: collection.json sha256=" + result["collection.json"],
                "reader_identity: " + I.identity_line(), "files_verified: %d" % result["files"]]
    from pathlib import Path
    from .gates import Gates
    started = time.monotonic()
    inputs, collection, collection_sha256, folder = I.load_collection(options["--inputs"])
    out = options.get("--out")
    gates = Gates(inputs, collection, collection_sha256, folder, out)
    try:
        gates.run()
        if command == "verify":
            gates.ledger.verify()
            gates.end()
            lines = ["verify: pass", "reader_identity: " + gates.identity["sha256"],
                     "files_verified: %d" % len(gates.ledger.entries), "jobs_verified: %d" % len(gates.contributing)]
            Path(out).mkdir(parents=True)
            CREATED.add(str(out))
            write_once(Path(out) / "verify.json", document_bytes({
                "schema": "a10-stage2-verify-1", "status": "pass", "reader_identity": gates.identity["sha256"],
                "collection_sha256": collection_sha256, "files_verified": len(gates.ledger.entries),
                "jobs_verified": len(gates.contributing)}))
            return lines
        from . import compute, registry as R
        components = list(R.COMPONENTS) if options["--component"] == "both" else [options["--component"]]
        written = compute.read(gates, components, out)
        lines = []
        for component in components:
            lines.append("component: " + component)
            lines += ["%s %s sha256=%s" % (component, name, written[component][name]["sha256"])
                      for name in list(compute.FILES) + ["SEAL.json"]]
        lines += ["reader_identity: " + gates.identity["sha256"], "files_verified: %d" % len(gates.ledger.entries),
                  "jobs_verified: %d" % len(gates.contributing)]
        import resource
        # D:538 as replaced by A1.13 and A6.8: one wall time per pass, in whole
        # minutes; file names, hashes, byte counts, a resource peak and the
        # numbers of files and jobs verified. Unsealed.
        write_once(Path(out) / "run_log.json", document_bytes({
            "schema": "a10-stage2-run-log-1", "command": command, "component": options["--component"],
            "wall_minutes": int((time.monotonic() - started) // 60),
            "peak_rss_kilobytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "numerical_threads_effective": gates.threads, "files_verified": len(gates.ledger.entries),
            "jobs_verified": len(gates.contributing), "files": written}))
        return lines
    finally:
        gates.cleanup()


def main(argv=None):
    """The one top-level handler (A1.4). It catches every exception."""
    argv = sys.argv[1:] if argv is None else argv
    out = None
    try:
        command, options = parse(argv)
        out = options.get("--out")
        lines = run(command, options)
        warnings.simplefilter("ignore")
        emit(lines)
        return 0
    except BaseException as exc:  # noqa: BLE001 - never print input content
        phase = "after_computation_started" if COMPUTATION_STARTED.get() else "input_verification"
        # A10.3c: ``refusal.json`` is a bare object holding exactly ``phase``,
        # ``reason_class`` and ``status`` with the literal ``refused``, plus
        # ``exception_class`` only for an exception the reader did not raise.
        if isinstance(exc, Refused):
            line, label = refusal_line(phase, str(exc.args[0]) if exc.args else "")
            record = {"status": "refused", "phase": phase, "reason_class": label}
        else:
            line, label = refusal_line(phase, "unexpected exception", type(exc).__name__)
            record = {"status": "refused", "phase": phase, "reason_class": label, "exception_class": type(exc).__name__}
        try:
            if out is not None:
                import os
                from pathlib import Path
                folder = Path(out)
                # A11.1: a refusal before publication finds no ``<out>`` and
                # leaves it holding exactly ``refusal.json``. A failure during
                # publication (item 4) finds the folder this pass created; the
                # record is added and nothing is deleted. A folder that was
                # already there is never written into.
                if not os.path.lexists(folder):
                    folder.mkdir(parents=True)
                    write_once(folder / "refusal.json", document_bytes(record))
                elif str(out) in CREATED:
                    write_once(folder / "refusal.json", document_bytes(record))
        except BaseException:  # noqa: BLE001
            pass
        try:
            emit([line])
        except BaseException:  # noqa: BLE001 - a closed stream must not produce a traceback
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
