#!/usr/bin/env python3
"""Fail if advisor-document content reaches a generated snapshot.

This repository is public. LINEAGE_IMPERATIVE_ADVISOR.md is deliberately
untracked and carries strategy, so its content must never enter the repository
indirectly through a generated artifact. The generator itself refuses to read
the file (see the never-ingest list in generate_project_knowledge_snapshots.py).
This checker is the independent backstop that verifies the outcome rather than
trusting the mechanism.

Two classes of needle, deliberately treated differently.

Content needles are strings that can only appear if the document's text was
actually ingested. A hit is a failure anywhere, with no exceptions, because
there is no legitimate reason for this repository to contain them.

Name needles are the document's filename. The filename legitimately appears in
the small number of tracked files whose job is to document or enforce the rule,
and those files are themselves ingested into snapshots. A bare filename search
therefore cannot distinguish "the advisor document leaked" from "something
correctly documents that the advisor document must not leak." Rather than drop
the filename tripwire, which would weaken detection of a real ingestion whose
body text is not enumerated below, a hit is a failure unless it is attributed
to an allowlisted source file.

Attribution uses the snapshot's own per-file markers, written by the generator
as "FILE: <relpath>". A name hit before the first marker lands in the snapshot
header, which lists ingested filenames, and is always a failure: it would mean
a file with that name was ingested.

Exit code 0 means clean, 1 means a violation was found.
"""

from __future__ import annotations

import argparse
import base64
import pathlib
import sys
from typing import List, Tuple

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
SNAPSHOT_DIR = REPO_ROOT / "snapshots"

# Strings that can only appear if the document body was ingested.
# A hit is a failure anywhere, unconditionally.
#
# These are stored base64 encoded rather than as plaintext literals, for two
# reasons. First, correctness: this file is itself ingested into the code
# snapshot, so plaintext needles here would trip the very check they implement.
# Second, and more importantly, this repository is public. The needles are
# fingerprints of a private document, so publishing them in plaintext would
# disclose part of what that document contains and would be trivially
# discoverable through code search. Encoding is obfuscation, not secrecy:
# anyone who runs this tool can recover the values. It prevents casual
# disclosure and indexing, nothing stronger, and it is not a place to put a
# secret that actually needs protecting.
_ENCODED_CONTENT_NEEDLES = (
    "QWxsYW4gRGFmb2U=",
    "WWFyaW4gR2Fs",
    "ZmluZ2VycHJpbnRpbmcgcmlzaw==",
)

CONTENT_NEEDLES = tuple(
    base64.b64decode(s).decode("utf-8") for s in _ENCODED_CONTENT_NEEDLES
)

# The document filename. A hit is a failure unless attributed to a source in
# NAME_NEEDLE_ALLOWLIST below.
NAME_NEEDLES = ("LINEAGE_IMPERATIVE_ADVISOR",)

# Source files permitted to mention the filename. Keep this list minimal, and
# only add a file whose purpose is to document or enforce the never-ingest rule.
# Anything else naming the document should be reworded instead of allowlisted.
NAME_NEEDLE_ALLOWLIST = frozenset({
    # Declares the never-ingest deny-list.
    "scripts/generate_project_knowledge_snapshots.py",
    # This checker, once it is itself ingested into the code snapshot.
    "scripts/check_snapshot_leak.py",
    # Records anomaly B4 and the advisor-document collision note.
    "simulation/diagnostics/defended_collapse_discrepancy_report.md",
})

HEADER_SOURCE = "<snapshot header>"


def attributed_lines(text: str) -> List[Tuple[int, str, str]]:
    """Yield (line_number, source_relpath, line) for every line in a snapshot."""
    out = []
    current = HEADER_SOURCE
    for i, line in enumerate(text.splitlines(), 1):
        if line.startswith("FILE: "):
            current = line[len("FILE: "):].strip().replace("\\", "/")
        out.append((i, current, line))
    return out


def scan(snapshot_dir: pathlib.Path) -> Tuple[List[str], List[str]]:
    """Return (violations, allowed_notes)."""
    violations: List[str] = []
    allowed: List[str] = []

    files = sorted(snapshot_dir.glob("*.md"))
    if not files:
        violations.append(f"no snapshot files found under {snapshot_dir}")
        return violations, allowed

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, source, line in attributed_lines(text):
            low = line.lower()

            for needle in CONTENT_NEEDLES:
                if needle.lower() in low:
                    violations.append(
                        f"{path.name}:{lineno}: content needle {needle!r} "
                        f"(source {source}). Content needles are never allowlisted."
                    )

            for needle in NAME_NEEDLES:
                if needle.lower() in low:
                    if source in NAME_NEEDLE_ALLOWLIST:
                        allowed.append(f"{path.name}:{lineno} from {source}")
                    else:
                        violations.append(
                            f"{path.name}:{lineno}: name needle {needle!r} "
                            f"from non-allowlisted source {source}"
                        )
    return violations, allowed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot-dir",
        type=pathlib.Path,
        default=SNAPSHOT_DIR,
        help="directory of generated snapshots to scan",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="print only violations",
    )
    args = parser.parse_args()

    violations, allowed = scan(args.snapshot_dir)

    if not args.quiet:
        print(f"scanned {args.snapshot_dir}")
        print(f"  content needles: {len(CONTENT_NEEDLES)}, never allowlisted")
        print(f"  name needles   : {len(NAME_NEEDLES)}, "
              f"allowlisted for {len(NAME_NEEDLE_ALLOWLIST)} sources")
        if allowed:
            print(f"\nallowed name-needle mentions ({len(allowed)}):")
            for note in allowed:
                print(f"  ok  {note}")

    if violations:
        print(f"\nHALT: {len(violations)} violation(s):")
        for v in violations:
            print(f"  {v}")
        return 1

    print("\nCLEAN: no advisor content in any snapshot.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
