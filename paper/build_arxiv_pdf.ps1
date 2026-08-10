# Build the arXiv PDF from the assembled paper.
#
# STATUS: prepared, NOT YET RUN. As of 2026-08-09 this machine has neither
# pandoc nor any LaTeX engine, so no PDF has been produced. The script fails
# loudly rather than emitting a degraded artifact.
#
# Why a real typesetting engine is required rather than a lighter converter:
# the source carries 456 inline and 75 display math expressions using 68
# distinct LaTeX commands, 107 headings that must become PDF bookmarks, and a
# seven-column table whose rows run to 136 characters. A converter that cannot
# typeset math would emit raw markup such as $\mathcal{U}_{sys}$ into the body
# text, which is a degraded artifact, not a stylistic variation.
#
# Prerequisites, one of:
#   A. pandoc plus tectonic     (recommended: tectonic self-fetches packages)
#        winget install JohnMacFarlane.Pandoc
#        winget install TectonicTypesetting.Tectonic
#   B. pandoc plus MiKTeX       (largest download, most complete)
#        winget install JohnMacFarlane.Pandoc
#        winget install MiKTeX.MiKTeX
#   C. pandoc plus typst        (fastest, smallest; pandoc 3.x required)
#        winget install JohnMacFarlane.Pandoc
#        winget install Typst.Typst
#
# Smart typography is disabled with -f markdown-smart so that no quotes,
# ellipses, or dashes are substituted during conversion. The paper contains
# zero em-dashes and that must survive the build.

param(
    [string]$Source = "docs/The Lineage Imperative v2.0.md",
    [string]$OutDir = "$env:USERPROFILE\Documents\arxiv-build",
    [ValidateSet("tectonic", "xelatex", "lualatex", "pdflatex", "typst")]
    [string]$Engine = "tectonic"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    throw "pandoc not found. Install it first; see the header of this script."
}
if ($Engine -ne "typst" -and -not (Get-Command $Engine -ErrorAction SilentlyContinue)) {
    throw "PDF engine '$Engine' not found. Install it first, or pass -Engine."
}

if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force $OutDir | Out-Null }
$stamp = Get-Date -Format "yyyyMMdd"
$out = Join-Path $OutDir "lineage_imperative_v2_$stamp.pdf"

$args = @(
    $Source,
    "-o", $out,
    "-f", "markdown-smart",          # no typographic substitution
    "--pdf-engine=$Engine",
    "--toc",
    "--toc-depth=3",
    "--number-sections",
    "-V", "documentclass=article",
    "-V", "geometry:margin=1in",
    "-V", "fontsize=11pt",
    "-V", "colorlinks=true",
    "-V", "linkcolor=black",
    "-V", "urlcolor=blue",
    "-M", "title=The Lineage Imperative: A Constitutional Architecture for Post-AGI Succession, Legitimacy, and Civilizational Continuity",
    "-M", "author=Matthew Yotko"
)

# XeLaTeX and LuaLaTeX need a Unicode font with coverage for the twelve
# non-ASCII characters the source uses, including the arrow and the relations.
if ($Engine -in @("xelatex", "lualatex")) {
    $args += @("-V", "mainfont=DejaVu Serif", "-V", "mathfont=DejaVu Math TeX Gyre")
}

Write-Host "pandoc $($args -join ' ')"
& pandoc @args

if (-not (Test-Path $out)) { throw "build produced no output at $out" }
Write-Host "built: $out"
Write-Host ("size: {0:N0} bytes" -f (Get-Item $out).Length)

# Post-build QA. Requires: pip install pypdf
python - @"
import sys, pathlib
try:
    from pypdf import PdfReader
except ImportError:
    print('pypdf not installed; skipping QA. pip install pypdf')
    sys.exit(0)
r = PdfReader(r'$out')
print(f'pages: {len(r.pages)}')
text = chr(10).join((p.extract_text() or '') for p in r.pages)
print(f'replacement chars U+FFFD: {text.count(chr(0xFFFD))}')
print(f'em-dashes U+2014: {text.count(chr(0x2014))}')
print(f'raw math markup leaked into text: {text.count(chr(92) + "mathcal")}')
try:
    print(f'bookmarks: {len(r.outline)}')
except Exception as e:
    print(f'bookmarks: could not read ({e})')
"@
