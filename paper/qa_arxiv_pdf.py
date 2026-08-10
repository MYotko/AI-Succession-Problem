#!/usr/bin/env python3
"""QA gates for the arXiv PDF build.

Usage:
    python paper/qa_arxiv_pdf.py <path-to-pdf>

Gates, each pass or fail:
  1. zero replacement characters in extracted text
  2. zero em-dashes in extracted text
  3. zero leaked math markup, meaning no literal dollar sign and no backslash
     command such as mathcal surviving into the body text
  4. bookmark count close to the source heading count
  5. every cell of every source table present in the extracted text, with the
     widest table checked cell by cell
  6. page count recorded

Exit code 0 if every gate passes, 1 otherwise.
"""

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).parent.parent
SOURCE = REPO / "docs" / "The Lineage Imperative v2.0.md"


def extract(pdf_path):
    from pypdf import PdfReader
    reader = PdfReader(str(pdf_path))
    pages = [(p.extract_text() or "") for p in reader.pages]
    try:
        outline = reader.outline
    except Exception:
        outline = []

    def count_outline(node):
        n = 0
        for item in node:
            if isinstance(item, list):
                n += count_outline(item)
            else:
                n += 1
        return n

    return pages, count_outline(outline) if outline else 0


def source_tables(text):
    """Return [(heading, [rows-of-cells])] for every markdown table."""
    lines = text.split("\n")
    tables = []
    i = 0
    while i < len(lines):
        if (lines[i].startswith("|") and i + 1 < len(lines)
                and re.match(r"^\|[\s:\-|]+\|\s*$", lines[i + 1])):
            heading = next((lines[k] for k in range(i, -1, -1)
                            if lines[k].startswith("#")), "?")
            rows = []
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                if not re.match(r"^\|[\s:\-|]+\|\s*$", lines[j]):
                    rows.append([c.strip() for c in
                                 lines[j].strip().strip("|").split("|")])
                j += 1
            tables.append((heading.strip(), rows))
            i = j
        else:
            i += 1
    return tables


#/ Cambria's ToUnicode CMap maps its hyphen glyph to U+2011 rather than U+002D,
#/ so extracted text carries non-breaking hyphens wherever the source has plain
#/ ones. That is a text-layer property, not a rendering fault: the page looks
#/ correct. Content-presence comparisons therefore fold the dash variants
#/ together, while the dash census below reports the raw codepoints so the
#/ property stays visible rather than being smoothed away.
DASHES = dict.fromkeys(
    [0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2015, 0x2212, 0x00AD], "-")


def norm(s):
    return re.sub(r"\s+", " ", s.translate(DASHES)).strip()


def main():
    if len(sys.argv) < 2:
        print("usage: python paper/qa_arxiv_pdf.py <path-to-pdf>")
        return 2
    pdf = pathlib.Path(sys.argv[1])
    if not pdf.exists():
        print(f"FATAL: no such file: {pdf}")
        return 2

    pages, n_bookmarks = extract(pdf)
    text = "\n".join(pages)
    flat = norm(text)
    src = SOURCE.read_text(encoding="utf-8")

    results = []
    print(f"pdf   : {pdf}")
    print(f"pages : {len(pages)}")
    print(f"size  : {pdf.stat().st_size:,} bytes")
    print(f"text  : {len(text):,} extracted characters")
    print()

    # Gate 1
    n = text.count("\ufffd")
    results.append(("1 replacement characters", n == 0, f"{n} found"))

    # Gate 2
    n = text.count("\u2014")
    results.append(("2 em-dashes", n == 0, f"{n} found"))

    # Gate 3
    dollars = text.count("$")
    cmds = re.findall(r"\\(mathcal|frac|cdot|Delta|Theta|sigma|text|left|right)\b", text)
    ok3 = dollars == 0 and len(cmds) == 0
    results.append(("3 leaked math markup", ok3,
                    f"{dollars} literal dollar signs, {len(cmds)} backslash commands"))

    # Gate 4
    n_head = len([l for l in src.split("\n") if re.match(r"^#{1,6} ", l)])
    ok4 = abs(n_bookmarks - n_head) <= 10
    results.append(("4 bookmarks", ok4,
                    f"{n_bookmarks} bookmarks against {n_head} source headings"))

    # Gate 5
    tables = source_tables(src)
    #/ A narrow table column wraps long cells across lines, so "Sub-Threshold
    #/ Drift" can arrive as "Sub-" plus "Threshold Drift". The gate asks whether
    #/ the content is present, not how it was laid out, so a whitespace-squashed
    #/ comparison is checked as well as the space-normalized one.
    squashed = re.sub(r"\s+", "", text.translate(DASHES))
    missing_total = 0
    detail = []
    for heading, rows in tables:
        miss = []
        for row in rows:
            for cell in row:
                c = norm(re.sub(r"[`*]", "", cell))
                if not c or c in {"---"}:
                    continue
                if c not in flat and re.sub(r"\s+", "", c) not in squashed:
                    miss.append(c)
        missing_total += len(miss)
        detail.append((heading, len(rows), len(miss), miss[:6]))
    results.append(("5 table cells present", missing_total == 0,
                    f"{missing_total} missing across {len(tables)} tables"))

    # Gate 6
    results.append(("6 page count recorded", True, f"{len(pages)} pages"))

    print("GATES")
    for name, ok, note in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:28} {note}")

    print("\nTABLE DETAIL")
    for heading, nrows, nmiss, sample in detail:
        print(f"  {nrows:2} rows, {nmiss:2} missing  {heading[:66]}")
        for s in sample:
            print(f"      missing: {s[:70]}")

    print("\nDASH CENSUS, raw codepoints in extracted text")
    for cp, label in ((0x002D, "ASCII hyphen"), (0x2010, "hyphen"),
                      (0x2011, "non-breaking hyphen"), (0x2013, "en dash"),
                      (0x2014, "em dash"), (0x2212, "minus sign")):
        print(f"  U+{cp:04X} {label:22} {text.count(chr(cp)):>6}")
    print("  note: Cambria maps its hyphen glyph to U+2011, so search and")
    print("  copy-paste return non-breaking hyphens. Rendering is unaffected.")

    # Glyph spot-check: characters known to be at risk in bold contexts.
    print("\nGLYPH SPOT-CHECK")
    for ch, label in (("\u03a8", "Psi U+03A8"), ("\u0398", "Theta U+0398"),
                      ("\u2192", "arrow U+2192"), ("\u2208", "element-of U+2208"),
                      ("\u00d7", "times U+00D7"), ("\u2264", "leq U+2264")):
        print(f"  {label:22} source {src.count(ch):>4}   pdf text {text.count(ch):>4}")

    failed = [r for r in results if not r[1]]
    print(f"\n{'ALL GATES PASS' if not failed else str(len(failed)) + ' GATE(S) FAILED'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
