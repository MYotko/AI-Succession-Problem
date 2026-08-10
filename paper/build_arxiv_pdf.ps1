# Build the arXiv PDF from the assembled paper.
#
# Toolchain installed 2026-08-09:
#   pandoc 3.10.1
#   MiKTeX 25.12, providing MiKTeX-XeTeX 4.16
#
# Tectonic was the first choice but is not in the winget catalog under any id,
# so MiKTeX was installed instead. MiKTeX uses the same on-demand package model
# ("just enough TeX"), and unlike typst it honors the LaTeX header-includes this
# build needs for table layout. Typst is available in winget but pandoc's typst
# writer ignores LaTeX preamble injection, so it cannot satisfy the longtable
# requirement.
#
# Why a real typesetting engine rather than a lighter converter: the source
# carries 456 inline and 75 display math expressions across 68 distinct LaTeX
# commands, 107 headings that must become PDF bookmarks, and a seven-column
# table with rows up to 136 characters.
#
# Smart typography is disabled with -f markdown-smart so no quotes, ellipses, or
# dashes are substituted during conversion. The paper contains zero em-dashes
# and that property must survive the build.

param(
    [string]$Source = "docs/The Lineage Imperative v2.0.md",
    [string]$OutDir = "$env:USERPROFILE\Documents\arxiv-build",
    [ValidateSet("xelatex", "lualatex", "pdflatex", "tectonic")]
    [string]$Engine = "xelatex",
    # Rotate the widest table onto its own landscape page. Off by default;
    # turn on only if VIII.9-1 is measured to overflow.
    [switch]$LandscapeWideTable
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

# MiKTeX and pandoc land in per-user paths that a non-login shell may not have.
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")

if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    throw "pandoc not found on PATH."
}
if (-not (Get-Command $Engine -ErrorAction SilentlyContinue)) {
    throw "PDF engine '$Engine' not found on PATH."
}

if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force $OutDir | Out-Null }
$stamp = Get-Date -Format "yyyyMMdd"
$out = Join-Path $OutDir "lineage_imperative_v2_$stamp.pdf"

# LaTeX preamble additions, written to a file and passed with -H so the
# directives stay readable and ordered.
$headerPath = Join-Path $OutDir "arxiv_header.tex"
$header = @'
% Tables: pandoc emits longtable for multi-page tables. Shrink the font so the
% seven-column Table VIII.9-1 fits the text block without overflowing.
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{etoolbox}
\AtBeginEnvironment{longtable}{\small}
\setlength{\LTleft}{0pt}
\setlength{\LTright}{0pt}
% Allow long table cells to wrap rather than run into the margin.
\usepackage{array}
\usepackage{ragged2e}
% Bookmarks: the source has 14 level-4 headings, which pandoc maps to
% \paragraph. LaTeX omits \paragraph from the bookmark tree by default, which
% left 93 bookmarks against 107 headings on the first build. Raising the
% bookmark depth brings them into the outline.
%
% This must be PassOptionsToPackage, not \hypersetup. Pandoc's template loads
% hyperref after header-includes, so \hypersetup here is an undefined control
% sequence and the build fails with pandoc exit 43.
\PassOptionsToPackage{bookmarksdepth=4}{hyperref}
'@
if ($LandscapeWideTable) {
    $header += @'

% Landscape for wide tables, applied only when measurement shows overflow.
\usepackage{pdflscape}
'@
}
Set-Content -Path $headerPath -Value $header -Encoding utf8

$pandocArgs = @(
    $Source,
    "-o", $out,
    "-f", "markdown-smart",          # no typographic substitution
    "--pdf-engine=$Engine",
    "-H", $headerPath,
    "--toc",
    "--toc-depth=4",
    "-V", "documentclass=article",
    "-V", "geometry:margin=1in",
    "-V", "fontsize=11pt",
    "-V", "colorlinks=true",
    "-V", "linkcolor=black",
    "-V", "urlcolor=blue",
    "-M", "title=The Lineage Imperative: A Constitutional Architecture for Post-AGI Succession, Legitimacy, and Civilizational Continuity",
    "-M", "author=Matthew Yotko"
)

# Unicode engines need a font covering the twelve non-ASCII characters the
# source uses, including the arrow and the set and order relations.
#
# Cambria was chosen by measurement, not preference. Coverage was tested
# character by character against the installed fonts: Cambria and Segoe UI
# Symbol are the only ones with full coverage. Times, Georgia, Segoe UI,
# Calibri, and Consolas all lack U+2208 element-of, and Arial additionally
# lacks the subscript digits. DejaVu, the first choice, is not installed on
# this machine at all. Cambria Math is the matching OpenType math font.
if ($Engine -in @("xelatex", "lualatex")) {
    $pandocArgs += @("-V", "mainfont=Cambria",
                     "-V", "mathfont=Cambria Math",
                     "-V", "monofont=Consolas")
}

Write-Host "building with $Engine ..."
# Remove any prior artifact first. Without this a failed build leaves the
# previous PDF in place and the existence check below passes on a stale file,
# which is how a failing build once reported success.
if (Test-Path $out) { Remove-Item $out -Force }
& pandoc @pandocArgs
$pandocExit = $LASTEXITCODE

if ($pandocExit -ne 0) { throw "pandoc exited $pandocExit" }
if (-not (Test-Path $out)) { throw "build produced no output at $out" }
Write-Host ("built: {0}" -f $out)
Write-Host ("size : {0:N0} bytes" -f (Get-Item $out).Length)
Write-Host ("run QA with: python paper/qa_arxiv_pdf.py `"{0}`"" -f $out)
