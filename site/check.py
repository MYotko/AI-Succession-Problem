"""Check the site's text before a commit: python site/check.py

Refuses, in site/*.md:
- withdrawn claims stated as findings (a sentence that reports the claim as withdrawn or superseded passes);
- em and en dashes;
- the author's employer, and private details (addresses, paths, machine names);
- words the blind rules keep out of public text (survival or extinction rates, rule rankings).

Exits 1 and lists every hit with its file and line.
"""
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent

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
]
REPORTED = re.compile(r"(?i)used to be|did not survive|failed|withdrawn|not unique|is not the only|no longer|"
                      r"superseded|showed that it is not|the claim that|does not guarantee")
ALWAYS = [
    ("—", "an em dash"),
    ("–", "an en dash"),
    (r"(?i)bessemer", "the author's employer"),
    (r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "an IP address"),
    (r"/home/|~/|[A-Za-z]:\\", "a local path"),
    (r"(?i)yotko-evo|YOTKOTEST|tailnet|tailscale", "a machine name"),
    (r"(?i)\b(survival|extinction|fire) rates?\b|\brule rankings?\b", "a blind-rule phrase"),
]


def sentences(text):
    return re.split(r"(?<=[.!?])\s+|\n{2,}", text)


def check(path):
    hits = []
    text = path.read_text(encoding="utf-8")
    for n, line in enumerate(text.splitlines(), 1):
        for pat, why in ALWAYS:
            if re.search(pat, line):
                hits.append(f"{path.name}:{n}: {why}: {line.strip()[:120]}")
    for s in sentences(text):
        for pat, why in WITHDRAWN:
            if re.search(pat, s) and not REPORTED.search(s):
                n = text[:text.find(s)].count("\n") + 1
                hits.append(f"{path.name}:{n}: {why} stated as a finding: {s.strip()[:160]}")
    return hits


if __name__ == "__main__":
    files = sorted(SITE.glob("*.md"))
    hits = [h for f in files for h in check(f)]
    for h in hits:
        print(h)
    print(f"{len(files)} files, {len(hits)} problems")
    sys.exit(1 if hits else 0)
