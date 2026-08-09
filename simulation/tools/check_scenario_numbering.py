#!/usr/bin/env python3
"""Validate scenario-number citations against the scenario catalog.

docs/Simulation_Scenarios.md is canon. Every other file that cites a scenario
number must agree with it. This checker exists because the comprehension gap
sweep carried two wrong citations for months without anyone noticing: it
attributed an Opaque Reasoning finding to Scenarios 25-26, which are Evaluator
Collusion and Methodological Diversity, and titled itself Scenarios 31-32,
which belong to Engineered Fragility and Resilience Monitoring.

How validation works
--------------------
A bare number cannot be validated, because a citation like "Scenarios 31-32"
is only wrong relative to what it claims to be about. So the checker pairs each
citation with any scenario name it recognizes from the catalog within a small
context window, then verifies the two agree. The window matters: in the sweep
script the subject ("opaque-reasoning") sits on the line above its citation, so
single-line matching would have missed the very defect that motivated this
tool. Citations with no recognizable name anywhere in the window are reported
separately as unverifiable rather than silently passed, so a human can review
them.

A name is only considered present if every distinctive word of the catalog
title appears, so "Opaque Reasoning" matches but a stray "reasoning" does not.

Some files legitimately quote a wrong citation while documenting that it is
wrong. Those are allowlisted by path; keep the list minimal.

Exit code 0 means no mismatches, 1 means at least one mismatch.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Dict, List, Set, Tuple

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent.resolve()
CANON = REPO_ROOT / "docs" / "Simulation_Scenarios.md"

SCAN_DIRS = ("simulation", "docs")
SCAN_SUFFIXES = (".py", ".md")

# Files that discuss mis-citations and must be allowed to quote wrong numbers.
ALLOWLIST = frozenset({
    "docs/Simulation_Scenarios.md",
    "simulation/diagnostics/defended_collapse_discrepancy_report.md",
    "simulation/tools/check_scenario_numbering.py",
})

# Heading forms in the catalog, covering the implemented and the not-yet forms:
#   ### Scenario 21: Opaque Reasoning (Attack Succeeds)
#   ### [NOT IMPLEMENTED] Scenario 33-34: Biological Validator Obsolescence
# The dash between paired numbers may be a hyphen or an en dash.
HEADING = re.compile(
    r"^#{2,4}\s*(?:\[NOT IMPLEMENTED\]\s*)?Scenario\s+(\d+)(?:\s*[-–]\s*(\d+))?\s*:\s*(.+?)\s*$"
)

# A citation: "Scenario 21", "Scenarios 31-32", "Scenario 33-34".
CITATION = re.compile(r"Scenarios?\s+(\d+)(?:\s*[-–]\s*(\d+))?")

# A markdown list item, used to keep tight bullet lists from merging.
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")

# Words too generic to identify a scenario by name.
STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "of", "for", "in", "to", "is", "attack",
    "attacks", "defeated", "succeeds", "defense", "layer", "v1", "v2", "not",
    "implemented", "through", "by", "with", "on", "at", "as", "full", "cop",
})


def parse_canon(path: pathlib.Path) -> Dict[int, str]:
    """Return {scenario_number: title}."""
    canon: Dict[int, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = HEADING.match(line.strip())
        if not m:
            continue
        lo, hi, title = m.group(1), m.group(2), m.group(3)
        title = re.sub(r"\(.*?\)", "", title).strip()
        lo_i = int(lo)
        canon[lo_i] = title
        if hi:
            canon[int(hi)] = title
    return canon


def title_keywords(title: str) -> Set[str]:
    words = re.findall(r"[A-Za-z_]+", title.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def build_name_index(canon: Dict[int, str]) -> Dict[str, Set[int]]:
    """Map a distinctive multi-word scenario phrase to the numbers it covers."""
    index: Dict[str, Set[int]] = {}
    for num, title in canon.items():
        kws = title_keywords(title)
        if not kws:
            continue
        phrase = " ".join(sorted(kws))
        index.setdefault(phrase, set()).add(num)
    return index


def names_in_line(line: str, canon: Dict[int, str]) -> Dict[str, Set[int]]:
    """Which catalog scenario titles are named on this line."""
    low = line.lower()
    found: Dict[str, Set[int]] = {}
    for num, title in canon.items():
        kws = title_keywords(title)
        # A title reducing to a single distinctive word is too weak to match on.
        # "The Runaway AI" reduces to {runaway}, which matches any paragraph
        # mentioning runaway_threshold and produced a false failure. Requiring
        # two words costs a little recall and buys a lot of precision.
        if len(kws) < 2:
            continue
        # Require every distinctive keyword of the title to be present, so
        # "Opaque Reasoning" matches but a stray "reasoning" alone does not.
        if all(k in low for k in kws):
            found.setdefault(title, set()).add(num)
    return found


def paragraph_span(lines: List[str], idx: int) -> Tuple[int, int]:
    """The blank-line-delimited block containing lines[idx].

    The paragraph is the right unit rather than a fixed line window. A fixed
    window bleeds across neighboring bullets in a dense list and produces false
    mismatches, while a paragraph keeps a citation with the sentence that
    actually makes the claim. This works for markdown prose and for Python
    docstrings alike, since both separate ideas with blank lines.

    In a tight markdown bullet list there are no blank lines between items, so
    a plain blank-line paragraph would span every bullet and attribute one
    bullet's scenario name to another bullet's citation. Each list item is
    therefore treated as its own unit, with its wrapped continuation lines.
    """
    start = idx
    while start > 0 and lines[start - 1].strip() and not LIST_ITEM.match(lines[start]):
        start -= 1
    end = idx
    while (
        end + 1 < len(lines)
        and lines[end + 1].strip()
        and not LIST_ITEM.match(lines[end + 1])
    ):
        end += 1
    return start, end


def iter_files() -> List[pathlib.Path]:
    out = []
    for d in SCAN_DIRS:
        base = REPO_ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix in SCAN_SUFFIXES:
                if "__pycache__" in p.parts:
                    continue
                out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--show-unverifiable", action="store_true",
                    help="also list citations with no recognizable scenario name")
    ap.add_argument("--window", type=int, default=3,
                    help="lines of context each side searched for a scenario name")
    args = ap.parse_args()

    if not CANON.exists():
        print(f"FATAL: canon not found at {CANON}", file=sys.stderr)
        return 1

    canon = parse_canon(CANON)
    print(f"canon: {CANON.relative_to(REPO_ROOT)}, {len(canon)} numbered scenarios")

    mismatches: List[str] = []
    unverifiable: List[str] = []
    checked = 0

    for path in iter_files():
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        if rel in ALLOWLIST:
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        seen_paragraphs: Set[Tuple[int, int]] = set()
        for lineno, line in enumerate(lines, 1):
            if not CITATION.search(line):
                continue
            span = paragraph_span(lines, lineno - 1)
            if span in seen_paragraphs:
                continue
            seen_paragraphs.add(span)
            context = "\n".join(lines[span[0]:span[1] + 1])

            # Citations and names are both gathered at paragraph scope. Mixing
            # scopes was a bug: a paragraph that names a scenario on one line
            # and cites its number on another looked like a mismatch, which
            # wrongly flagged prose that explains a mis-citation by quoting the
            # wrong number next to the right name.
            cited: Set[int] = set()
            for lo, hi in CITATION.findall(context):
                cited.add(int(lo))
                if hi:
                    cited.add(int(hi))

            named = names_in_line(context, canon)
            if not named:
                unverifiable.append(
                    f"{rel}:{span[0] + 1}: cites {sorted(cited)}, no catalog name in paragraph"
                )
                continue
            if len(named) > 1:
                # A paragraph naming several scenarios while citing one number
                # is normal prose, for example a survey listing attack vectors.
                # There is no sound way to decide which name the number belongs
                # to, so report for review rather than guess. Precision matters
                # more than recall here: a checker that cries wolf on ordinary
                # prose gets switched off, and then it catches nothing.
                titles = ", ".join(sorted(named))
                unverifiable.append(
                    f"{rel}:{span[0] + 1}: cites {sorted(cited)}, paragraph names "
                    f"several scenarios [{titles}], ambiguous"
                )
                continue
            checked += 1
            title, nums = next(iter(named.items()))
            if not (nums & cited):
                mismatches.append(
                    f"{rel}:{span[0] + 1}: paragraph names [{title}] "
                    f"({sorted(nums)}) but cites {sorted(cited)}"
                )

    print(f"validated {checked} citation(s) that name a scenario")
    print(f"unverifiable (number cited, no name on line): {len(unverifiable)}")
    if args.show_unverifiable:
        for u in unverifiable:
            print(f"  ?  {u}")

    if mismatches:
        print(f"\nFAIL: {len(mismatches)} mismatch(es):")
        for m in mismatches:
            print(f"  {m}")
        return 1

    print("\nOK: every validated citation agrees with the catalog.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
