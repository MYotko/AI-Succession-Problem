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

# MiKTeX font tree, used for the path-based font selection below.
$MiktexFontRoot = "$env:LOCALAPPDATA\Programs\MiKTeX\fonts"

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

# Font selection, appended to the preamble. See the note above the pandoc
# arguments for why DejaVu was chosen and by what measurement.
if ($Engine -in @("xelatex", "lualatex")) {
    $dv = ($MiktexFontRoot + "\truetype\public\dejavu") -replace "\\", "/"
    $dvMath = ($MiktexFontRoot + "\opentype\public\dejavu-math") -replace "\\", "/"
    foreach ($p in @("$dv/DejaVuSerif.ttf", "$dvMath/dejavu-math.otf")) {
        if (-not (Test-Path $p)) {
            throw "required font missing: $p. Install with: mpm --install=dejavu; mpm --install=dejavu-math"
        }
    }
    $header += @"

\usepackage{fontspec}
\setmainfont{DejaVuSerif}[
  Path = $dv/ ,
  Extension = .ttf,
  UprightFont = *,
  BoldFont = *-Bold,
  ItalicFont = *-Italic,
  BoldItalicFont = *-BoldItalic ]
\setmonofont{DejaVuSansMono}[
  Path = $dv/ ,
  Extension = .ttf,
  Scale = MatchLowercase ]
\usepackage{unicode-math}
\setmathfont{dejavu-math.otf}[ Path = $dvMath/ ]
% Route \mathbf through the math font.
%
% Two headings use \mathbf{\Psi} and \mathbf{\Theta}. Under legacy semantics
% \mathbf selects the upright bold TEXT font even inside math, so those
% requested U+1D6F9 and U+1D6E9 from DejaVuSerif-Bold, which has neither, and
% the glyphs were dropped: four notdef marks, in the table of contents on page
% 3 and in the body headings on pages 82 and 83.
%
% A math-font range fallback cannot fix this, and was tried and reverted: the
% request never reaches the math font. \symbf is unicode-math's math-font
% equivalent, and it maps Greek capitals to the bold block at U+1D6A8, which
% dejavu-math does provide.
%
% AtBeginDocument is required. unicode-math redefines \mathbf itself at
% begin-document, so a bare \let in the preamble is overwritten and the
% glyphs stay missing. That was measured, not assumed.
\AtBeginDocument{\let\mathbf\symbf}
"@
}
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

# Fonts are selected in the preamble by explicit path rather than by family
# name, because these come from MiKTeX packages and are not registered as
# system fonts. Family-name lookup fails for them.
#
# DejaVu Serif was chosen by measurement against two gates. Gate one, all twelve
# non-ASCII characters the paper uses must render: DejaVu Serif covers them all.
# Gate two, hyphens must extract as U+002D: DejaVu produces zero U+2011 in the
# ToUnicode CMap.
#
# The candidates that lost. Cambria passes gate one but fails gate two: it maps
# its hyphen glyph to U+2011, which put 1,277 non-breaking hyphens into the
# extracted text and broke in-reader search. STIX Two Text passes gate two
# cleanly but fails gate one, missing the arrow and the relations
# less-than-or-equal, greater-than-or-equal, element-of, and approximately-equal,
# because those live in STIX Two Math rather than the text face. Latin Modern,
# the engine default, passes gate two but drops nine of the twelve characters.

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
