"""The A1.4 stream checker.

Usage: python -B stream_check.py <captured stdout or stderr file>

Reads one captured stream and prints only the count of lines outside the
patterns D:540-545 and A1.4 allow. It never prints a line. The allowed lines
are exactly those the reader's top-level module can emit:

    component: A10|A6
    <A10|A6> <one of the six file names> sha256=<64 hex>
    reader_identity: <64 hex>
    files_verified: <count>
    jobs_verified: <count>
    verify: pass
    collect: inputs.json|collection.json sha256=<64 hex>
    REFUSED: input_verification|after_computation_started: <label>
    REFUSED: <phase>: unexpected exception (<exception class name>)

where <label> is one of the literal labels below, the reader's own complete
list (``reading_stage2/labels.py``). An empty line, a line with a carriage
return, and undecodable bytes are outside the patterns. Standard library only.
"""
import re
import sys

LABELS = (
    'A10 receipt does not bind the family',
    'A10 receipt does not bind the labels',
    'A13 refusal differs from its authorized hash',
    'A13 refusal differs from its registered constant',
    'A13 refusal differs from the receipt',
    'A13 refusal does not read refused',
    'A14 admission plan hash differs from the receipt',
    'A14 publication plan hashes differ',
    'A14 receipt does not bind the admission record',
    'A14 receipt does not bind the public records',
    'A14 receipt malformed',
    'A16 admission plan hash differs from the bound plan',
    'A16 family record exists beside a closeout',
    'A16 family record is not published at the bound round',
    'A16 provenance differs from the on-disk records',
    'A16 provenance misplaced',
    'A16 receipt does not bind the round records',
    'A16 receipt malformed',
    'A16 records differ from the bound list',
    'A16 records differ from the bound round',
    'PYTHONINTMAXSTRDIGITS is not 0',
    'a13 admission binding absent',
    'a13 incidence branches',
    'a13 incidence counts',
    'a13 incidence missing on admitted family',
    'a13 incidence present on a no-admitted family',
    'a13 incidence separate counts',
    'accepted identities not computable',
    'admission plan hash differs from the receipt',
    'admission record admitted set differs from the binding',
    'admission record disagrees with the loaded table',
    'admission record schema or scope differs',
    'admission scope not allowed for the family',
    'arm spec was not made at the running identity',
    'authorized-hash document entries',
    'authorized-hash document schema or keys',
    'authorized-hash document seal',
    'authorized-hash document specification set',
    'binding admission record did not pass',
    'calibration differs from its frozen pin',
    'calibration refused by the native loader',
    'capability path invalid',
    'cell job count differs',
    'closeout record does not bind the refused record',
    'closeout record does not exclude other run roots',
    'closeout record names another arm or status',
    'closeout record reads A16 entered',
    'closeout record schema or keys',
    'collection file inventory',
    'collection schema',
    'collection seal',
    'committed record not readable at HEAD',
    'comparator contributing run count differs',
    'comparator registration pin differs',
    'comparator registration pin not verified',
    'completion record does not match its job',
    'contributing-run map changed after it was sealed',
    'derived incidence denominators differ from recorded',
    'disclosure rows not computable',
    'duplicate job id',
    'duplicate job seed',
    'excluded root not named by its inventory',
    'family incidence status inconsistent',
    'family size differs',
    'family table refused by require_a10',
    'family table refused by the native loader',
    'file differs from the sealed collection',
    'file hash differs from its inventory',
    'file_hash',
    'final population inconsistent',
    'fixture table in registered mode',
    'fixture table lacks its marker',
    'fixture-only model key',
    'identity record differs from its authorized hash',
    'identity record differs from the committed record',
    'identity record does not bind the receipt or sidecar',
    'identity record does not bind the table',
    'identity record malformed',
    'incidence denominators not derivable',
    'input changed during reading',
    'input_missing',
    'inputs a16 keys',
    'inputs arm keys',
    'inputs arm names',
    'inputs arm status',
    'inputs comparator family keys',
    'inputs comparator keys',
    'inputs differ from the sealed collection',
    'inputs excluded roots',
    'inputs family keys',
    'inputs fixture flag',
    'inputs keys',
    'inputs leaf type',
    'inputs path',
    'inputs path is not absolute',
    'inputs registration pin',
    'inputs schema',
    'inventory differs from its authorized hash',
    'inventory identity differs from the running identity',
    'inventory keys',
    'inventory schema',
    'inventory seal',
    'inventory verdict or checks',
    'job count differs',
    'job definition malformed',
    'job outside the registry cells',
    'job path strings differ from the registered paths',
    'json_duplicate_key',
    'json_malformed',
    'json_nonfinite',
    'key_number',
    'label record malformed',
    'labels file supplied for a no-label family',
    'missing row recorded in a no-admitted family',
    'mode mixture',
    'nan_result',
    'native cell selection refused',
    'native comparison helper refused',
    'native context builder refused',
    'native job builder refused',
    'native modules not importable',
    'no-admitted family condition failed',
    'no-admitted family job instrument differs',
    'no-admitted family lacks context coverage',
    'no-label receipt differs',
    'nominal table is not the file at its registered path',
    'not-run arm keys',
    'not-run evidence does not read refused',
    'not-run evidence not bound',
    'not-run evidence set',
    'not-run family record is not terminal',
    'not-run family record names another family',
    'not-run reason missing',
    'numerical thread limit not verified as one',
    'original refusal not preserved',
    'output destination exists',
    'output destination inside an input root',
    'output does not match its job',
    'output file exists',
    'output hash differs from its completion record',
    'output hash differs from the verified hash file',
    'path_map in registered mode',
    'population path differs',
    'pre-dispatch spec differs from the final spec',
    'pre-dispatch spec listed but not supplied',
    'primary row count differs',
    'producer identity not accepted',
    'published file not listed in its inventory',
    'published table exists for a not-run arm',
    'python or numpy version differs from the frozen environment',
    'quantity key collision',
    'registration pin differs from the authorized pin',
    'registration pin not verified',
    'registry digest differs from its frozen literal',
    'registry formation differs from the native registry',
    'root manifest differs from the spec',
    'round 1 refusal not preserved',
    'run path length differs',
    'run records exist for a not-run arm',
    'run result malformed',
    'run used fixture tables',
    'running identity differs',
    'running identity not computable',
    'seal',
    'seal differs from its inventory',
    'sealed collection missing',
    'seed registry differs from the committed record',
    'seed registry digest differs from the specs',
    'spec differs from its inventory',
    'spec family or stage differs',
    'spec family paths differ from the registered paths',
    'spec jobs differ from the registered jobs',
    'spec labels policy differs',
    'spec registration differs from the pin',
    'spec schema',
    'spec seal',
    'specification set digest',
    'sqrt admission record differs from its authorized hash',
    'step field type',
    'step times differ',
    'strict receipt or labels binding differs',
    'supplementary records block missing or malformed',
    'survival differences need a boundary comparison',
    'table calibration differs from the calibration',
    'table family differs',
    'unexpected exception',
    'unlisted refusal label',
    'unserializable value',
    'usage',
    'validation receipt does not bind the family',
    'verified hash file differs from its inventory',
    "verified hash file does not cover exactly the spec's outputs",
    'verified hash file malformed',
)
FILES = ("reading.json", "values.json", "contributing_runs.json", "incidence_per_run.json", "LADDER.json", "SEAL.json")
HEX = "[0-9a-f]{64}"
PATTERNS = [re.compile(p) for p in (
    r"component: (A10|A6)",
    r"(A10|A6) (%s) sha256=%s" % ("|".join(re.escape(f) for f in FILES), HEX),
    r"reader_identity: %s" % HEX,
    r"files_verified: (0|[1-9][0-9]*)",
    r"jobs_verified: (0|[1-9][0-9]*)",
    r"verify: pass",
    r"collect: (inputs\.json|collection\.json) sha256=%s" % HEX,
    r"REFUSED: (input_verification|after_computation_started): (%s)" % "|".join(re.escape(s) for s in LABELS),
    r"REFUSED: (input_verification|after_computation_started): unexpected exception \([A-Za-z_][A-Za-z0-9_]*\)",
)]


def outside(data):
    """The number of lines of ``data`` (bytes) outside the allowed patterns."""
    if not data:
        return 0
    lines = data.split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    count = 0
    for raw in lines:
        try:
            line = raw.decode("ascii")
        except UnicodeDecodeError:
            count += 1
            continue
        if not any(p.fullmatch(line) for p in PATTERNS):
            count += 1
    return count


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage")
        return 2
    try:
        with open(argv[0], "rb") as stream:
            data = stream.read()
    except OSError:
        print("unreadable")
        return 2
    count = outside(data)
    print(count)
    return int(count > 0)


if __name__ == "__main__":
    raise SystemExit(main())
