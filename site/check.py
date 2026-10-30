"""Check the site's text before a commit: python site/check.py

Refuses, in site/*.md, README.md and the dated site updates (essays/site-update-*.md):
- withdrawn claims stated as findings (a sentence that reports the claim as withdrawn or superseded passes);
- em and en dashes;
- the author's employer, and private details (addresses, paths, machine names);
- words the blind rules keep out of public text (survival or extinction rates, rule rankings).

A dated site update is kept as published. A withdrawn claim in one passes only when the update carries a dated
correction note at its top ("> **Correction, YYYY-MM-DD.**") that quotes the withdrawn wording.

Exits 1 and lists every hit with its file and line.
"""
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
REPO = SITE.parent

# Claims withdrawn on 25 September 2026 (README status notice). A sentence matching one of these passes only when it
# also says the claim is withdrawn, superseded or no longer held.
WITHDRAWN = [
    (r"(?i)\bis (derived as )?the unique (nash )?equilibrium", "the uniqueness claim"),
    (r"(?i)\bderived as the unique\b", "the uniqueness claim"),
    (r"(?i)\bdominant strategy\b", "the dominant-strategy claim"),
    (r"(?i)\b150,000\b", "the withdrawn simulation total"),
    (r"(?i)computationally prov", "a proof claimed for simulation results"),
    (r"(?i)mathematical consequence, not a moral", "the scarcity-weighting claim"),
    (r"(?i)framework is at v1\.", "a superseded version"),
    (r"(?i)(?<!not )guarantees? (cooperation|mutual cultivation)", "a guarantee of cooperation"),
    # Corrected 29 October 2026 (Audit B). Records: v3_rerun_design_note.md amendments A10 and A12, the v2.0
    # instrument validation record, SPECIFICATION_GAPS.md GAP-05, defense_heldout_design_note.md section 11.
    (r"(?i)\b(stays?|are|is|remain)\s+sealed until", "the sealed-results claim (readings opened 5 October 2026)"),
    (r"(?i)before any (table, )?run(,| or| under)", "a registration claim without its qualifier (registered)"),
    (r"(?i)before any stage 1 output existed", "the A12 timing claim (estimation existed, unread)"),
    (r"(?i)each test was registered before the defen[cs]e", "the universal pre-registration claim"),
    (r"(?i)written before the result was known", "the gate 2 validity-gate timing claim"),
    (r"(?i)every claim in that record cites", "the citation claim about the validation record"),
    (r"(?i)reading is (running|under way) now|runs are now being read", "the reading-in-progress claim (sealed 29 October)"),
    (r"(?i)more than 32 scenarios", "the scenario count"),
    (r"(?i)\b24 adversarial attack scenarios", "the scenario count"),
    (r"(?i)\b11/13\b|\b11 of 13\b", "the 11-of-13 coverage count"),
    (r"(?i)amendments A1 to A7\b", "a superseded amendment range"),
    (r"(?i)published paper is v1\.|\*\*status:\*\* version 1\.x|v1\.x\.2[^\n]{0,60}\bcurrent version|"
     r"v2\.0 paper update is pending", "a superseded version"),
    (r"(?i)essays predate September 2026", "the essay-date claim"),
    (r"(?i)roughly twice that floor", "the floor ratio (about 1.55 like for like)"),
    (r"(?i)seven of the ten adversarial scenarios", "the uncontaminated-vector count (eight)"),
    (r"(?i)no threat is needed|with no threat behind it", "the model-collapse claim (corrected 2 October)"),
]
REPORTED = re.compile(r"(?i)used to be|did not survive|failed|withdrawn|not unique|is not the only|no longer|"
                      r"superseded|showed that it is not|the claim that|does not guarantee|later corrected|corrected this|"
                      r"previous version|claimed that|it said that|that update said|none of them now says")
ALWAYS = [
    ("—", "an em dash"),
    ("–", "an en dash"),
    (r"(?i)bessemer", "the author's employer"),
    (r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "an IP address"),
    (r"/home/|/Users/|/root/|~/|[A-Za-z]:\\", "a local path"),
    (r"(?i)yotko-evo|yotko-legion|YOTKOTEST|yotkolaptop|tailnet|tailscale", "a machine name"),
    (r"(?i)\b(survival|extinction|fire) rates?\b|\brule rankings?\b", "a blind-rule phrase"),
]
NOTE_START = re.compile(r"^> \*\*Correction, \d{4}-\d{2}-\d{2}\.\*\*")


def sentences(text):
    return re.split(r"(?<=[.!?])\s+|\n{2,}", text)


def correction_notes(text):
    """The text of every dated correction note: a blockquote that opens with '> **Correction, YYYY-MM-DD.**'."""
    notes, inside = [], False
    for line in text.splitlines():
        if NOTE_START.match(line):
            inside = True
        elif inside and not line.startswith(">"):
            inside = False
        if inside:
            notes.append(line.lstrip("> "))
    return " ".join(" ".join(notes).split()).lower()


def check(path, dated=False):
    hits = []
    text = path.read_text(encoding="utf-8")
    name = path.relative_to(REPO).as_posix()
    for n, line in enumerate(text.splitlines(), 1):
        for pat, why in ALWAYS:
            if re.search(pat, line):
                hits.append(f"{name}:{n}: {why}: {line.strip()[:120]}")
    notes = correction_notes(text) if dated else ""
    for raw in sentences(text):
        s = " ".join(raw.split())  # updates are hard-wrapped; match across line breaks
        for pat, why in WITHDRAWN:
            m = re.search(pat, s)
            if not m or REPORTED.search(s):
                continue
            if dated and " ".join(m.group(0).split()).lower() in notes:
                continue
            n = text[:text.find(raw)].count("\n") + 1
            hits.append(f"{name}:{n}: {why} stated as a finding: {s.strip()[:160]}")
    return hits


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    living = sorted(SITE.glob("*.md")) + [REPO / "README.md"]
    dated = sorted((REPO / "essays").glob("site-update-*.md"))
    hits = [h for f in living for h in check(f)] + [h for f in dated for h in check(f, dated=True)]
    for h in hits:
        print(h)
    print(f"{len(living) + len(dated)} files, {len(hits)} problems")
    sys.exit(1 if hits else 0)
