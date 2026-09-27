param([switch]$ValidateAvailable)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath($PSScriptRoot)
$utf8 = New-Object System.Text.UTF8Encoding($false)
$manifest = Get-Content -LiteralPath (Join-Path $root 'run-manifest.json') -Raw | ConvertFrom-Json
$duplicateIds = $manifest | Group-Object id | Where-Object { $_.Count -gt 1 }
if ($duplicateIds) { throw 'Duplicate run identifiers in the manifest.' }
$records = @{}
foreach ($job in $manifest) {
    $path = Join-Path $root "records/$($job.id).json"
    if (!(Test-Path -LiteralPath $path)) {
        if ($ValidateAvailable) { continue }
        throw "Incomplete check: $($job.id)"
    }
    $r = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
    $logPath = Join-Path $root $r.log
    if ((Get-FileHash -LiteralPath $logPath -Algorithm SHA256).Hash -ne $r.logHash) { throw "Log identity mismatch: $($r.id)" }
    if ((Get-FileHash -LiteralPath (Join-Path $root $r.config) -Algorithm SHA256).Hash -ne $r.configHash) { throw "Config identity mismatch: $($r.id)" }
    foreach ($entry in $r.codeHashes.psobject.Properties) {
        if ((Get-FileHash -LiteralPath (Join-Path $root $entry.Name) -Algorithm SHA256).Hash -ne $entry.Value) { throw "Model identity mismatch: $($r.id)" }
    }
    $log = [IO.File]::ReadAllText($logPath)
    if ($r.status -eq 'HOLDS' -and $log -notmatch 'Model checking completed. No error has been found.') {
        throw "Passing status not supported by TLC: $($r.id)"
    }
    if ($r.status -eq 'VIOLATED' -and
        $log -notmatch ('Invariant ' + [regex]::Escape($r.property) + ' is violated') -and
        !($job.temporal -and $log -match 'Temporal properties were violated')) {
        throw "Violation status not supported by TLC: $($r.id)"
    }
    if ($log -notmatch 'with 2 workers on 2 cores') { throw "Worker limit not verified in $($r.id)" }
    $allCounts = [regex]::Matches($log, '([\d,]+) states generated, ([\d,]+) distinct states found, ([\d,]+) states left on queue')
    if (!$allCounts.Count) { throw "Missing TLC state counts: $($r.id)" }
    $counts = $allCounts[$allCounts.Count - 1]
    if ([long]$counts.Groups[1].Value.Replace(',','') -ne $r.generated -or
        [long]$counts.Groups[2].Value.Replace(',','') -ne $r.distinct) { throw "Recorded and final counts differ: $($r.id)" }
    if ($r.status -eq 'HOLDS' -and $r.queue -ne 0) { throw "Incomplete passing search: $($r.id)" }
    if ($r.status -notin @('HOLDS','VIOLATED')) { throw "Invalid completion: $($r.id)" }
    $r | Add-Member -NotePropertyName rawLog -NotePropertyValue $log
    $records[$r.id] = $r
}
if ($ValidateAvailable) {
    Write-Output "Validated $($records.Count) available records against source, configuration, log hashes, final TLC state counts, and the worker limit."
    return
}
function Cell([string]$id) {
    $r = $records[$id]
    if (!$r) { return 'Not in this matrix' }
    "[$($r.status)]($($r.log)), $($r.generated)/$($r.distinct)"
}
function Last-Value([string]$log, [string]$name) {
    $matches = [regex]::Matches($log, '(?m)^/\\ ' + [regex]::Escape($name) + ' = ([^\r\n]+)')
    if ($matches.Count) { return $matches[$matches.Count - 1].Groups[1].Value.Trim('"') }
    return '?'
}
function Trace-Summary($r) {
    $log = $r.rawLog
    $m = Last-Value $log 'm'; $n = Last-Value $log 'n'
    $b = Last-Value $log 'bioYes'; $h = Last-Value $log 'honestYes'
    $bad = Last-Value $log 'faultyYes'; $faulty = Last-Value $log 'faulty'
    $route = Last-Value $log 'route'
    $prefix = "Panel $m, peers $n, actual faulty peers $faulty."
    switch ($r.property) {
        'EmergencyReachable' {
            if ($r.spec -eq 'COP_as_written') {
                return "$prefix Setup supplies a real, independently verified emergency, $n honest peer approvals, and biological approvals $b/$m. Preparing the same inputs leaves emergency execution disabled by the written strict fraction/count inequality. No emergency transition occurs."
            }
            return "$prefix The civic layer is incapacitated. Honest peers unanimously approve, but the fresh-clearance reading also requires a responsive panel, so emergency execution remains disabled. Biological approvals are $b/$m."
        }
        { $_ -in @('Liveness','NormalLiveness','EmergencyLiveness') } {
            if ($r.settings.EnvironmentReading -eq 'Anomalies') {
                return "$prefix Repeated anomalies reduce trust, reset it to zero, discard ballots, rotate the panel, and trigger a completed fresh audit. The cycle repeats forever before execution. Vote and execution actions are repeatedly disabled, so this infinite cycle satisfies weak fairness."
            }
            if ($r.settings.BioReading -eq 'Fresh' -and $r.spec -eq 'COP_candidate') {
                return "$prefix Honest peers deliver their approvals, but incapacitated biology cannot supply fresh unanimity. The system stutters with no executable emergency transition. Weak fairness cannot enable a disabled gate."
            }
            return "$prefix Honest approvals are delivered, then the system stutters without executing. Emergency technical review does not satisfy the exclusive normal-review equality, and the written emergency inequality never becomes true. Weak fairness cannot enable either disabled route."
        }
        'ByzantineSafety' {
            return "$prefix Execution uses the $route route with biological approvals $b/$m, honest peer approvals $h, and faulty approvals $bad. The faulty peers supply the approving peer quorum without an honest peer approval. Biological participation is supplied independently in the PeerQuorum interpretation."
        }
        'DecisionSafety' {
            return "$prefix The $route transition executes despite a false independent decision predicate. Biological approvals are $b/$m, honest peer approvals $h, and faulty approvals $bad. A favorable vote and a ledger entry do not establish a positive Yield or other decision."
        }
        'SignatureSafety' {
            return "$prefix A normal transition executes with an invalid commitment signature, biological approvals $b/$m, honest peer approvals $h, and faulty approvals $bad. Ledger membership alone satisfies the written commitment test."
        }
        'NeverEmergency' {
            return "$prefix Setup prepares the emergency inputs, then an emergency transition executes with biological approvals $b/$m, honest peer approvals $h, and faulty approvals $bad. This is a positive reachability witness."
        }
        'NeverReset' {
            return "$prefix Two anomalies move trust from 90/100 to 9/100 to zero. The panel epoch changes, all ballots are cleared, review becomes Pending, and the system enters audit. This is a positive reset witness."
        }
        default {
            $factsMatches = [regex]::Matches($log, '(?s)/\\ evidence = (\{.*?\})')
            $facts = if ($factsMatches.Count) { $factsMatches[$factsMatches.Count - 1].Groups[1].Value } else { '{}' }
            $missing = @()
            foreach ($name in @('Decision','Incapacity','Integrity')) {
                if ($facts -notmatch ('"' + $name + '"')) { $missing += $name }
            }
            if ($facts -match '"Manufactured"') { $missing += 'causal nonmanufacture' }
            $suffix = if ($r.property -eq 'EmergencySafeguards' -and $missing.Count) { ' False safeguards: ' + ($missing -join ', ') + '.' } else { '' }
            return "$prefix The $route transition executes with biological approvals $b/$m, honest peer approvals $h, and faulty approvals $bad.$suffix"
        }
    }
}
$out = New-Object System.Collections.Generic.List[string]
function Add([string]$s = '') { $out.Add($s) }
Add '# TLC results for the Consensus Override Protocol'
Add
Add 'The default deterministic candidate with explicit cached biological clearance passes the bounded consent and emergency-reachability checks. Its liveness result requires a stable environment and enough honest peers to meet quorum. The as-written emergency branch is unreachable. The candidate is not valid under every defensible reading of the conflicting prose.'
Add
Add "All $($manifest.Count) production checks completed with the installed TLC 2.19 and exactly two TLC workers per process. No files that existed before this task were intentionally modified, no Python process was touched, no prerequisite was downloaded, and nothing was committed. Preconditions passed on main. [Tool and source identity](provenance.json), [exact configuration matrix](run-manifest.json), and [modeling choices and source mapping](modeling-notes.md) accompany the results."
Add
Add 'Counts below are generated/distinct states. HOLDS means TLC completed the configured exhaustive check; VIOLATED means TLC supplied a counterexample. Safety-violation counts are partial because TLC stops at the first failure. Every run also checks TypeOK. Identity permutations are quotiented as documented in the modeling notes.'
Add
Add '## Requested properties, default deterministic reading'
Add
Add '| Property and scope | As written | Candidate |'
Add '| --- | --- | --- |'
foreach ($p in @('TwoKeySafety','NoSingleClass','EmergencyReachable')) {
    Add "| $p | $(Cell "written-base-$p") | $(Cell "candidate-base-$p") |"
}
foreach ($target in @('Normal','Emergency')) {
    Add "| Liveness, stable $target proposal with honest quorum | $(Cell "written-base-Liveness-$target") | $(Cell "candidate-base-Liveness-$target") |"
}
foreach ($target in @('Normal','Emergency')) {
    Add "| Liveness, recurring anomalies, $target proposal | $(Cell "written-anomalies-Liveness-$target") | $(Cell "candidate-anomalies-Liveness-$target") |"
}
Add '| ByzantineSafety, honest peer participation | HOLDS below peer quorum; VIOLATED when faults can fill quorum. Counts below. | HOLDS below peer quorum; VIOLATED when faults can fill quorum. Counts below. |'
Add "| ByzantineSafety, faulty peers with no biological approval | $(Cell 'written-byz-entire') | $(Cell 'candidate-byz-entire') |"
Add
Add 'The primary safety checks cover every panel and peer size from one through four and every actual faulty count up to the set size, using f=4 as the common upper bound. EmergencyReachable isolates the quorum defect with zero faulty peers and unanimous honest votes across all 16 size pairs. Liveness separately enumerates every faulty count for which the honest peers alone can meet quorum.'
Add
Add '## Largest faulty-peer budget'
Add
Add 'For the PeerQuorum reading, with q = ceiling(tau * n), the largest checked safe budget is f = q - 1. A budget of q permits faulty peers to supply the entire approving peer quorum, even while biological consent and external evidence are independently valid. Under ordinary strict majority this is floor(n/2). The default tau=2/3 has the same acceptance counts as ordinary strict majority for these four sizes.'
Add
Add '| Peers n | Default quorum q | Largest safe f | As written at safe f | As written at f=q | Candidate at safe f | Candidate at f=q |'
Add '| --- | --- | --- | --- | --- | --- | --- |'
foreach ($n in 1..4) {
    $q = [int][Math]::Ceiling(2 * $n / 3)
    $fSafe = $q - 1
    Add "| $n | $q | $fSafe | $(Cell "written-byz-n$n-f$fSafe") | $(Cell "written-byz-n$n-f$q") | $(Cell "candidate-byz-n$n-f$fSafe") | $(Cell "candidate-byz-n$n-f$q") |"
}
Add
Add 'Every f from zero through n was checked at the default threshold. The 3/4 and unanimity variants check both sides of every corresponding boundary. Under the literal EntireTransition reading, independent biological approval blocks faulty peers acting alone for every f up to n in both default specs. This does not establish honest-peer participation. Safety tolerance and quorum availability also differ: honest-only liveness requires f <= n-q. Thus the default budgets supporting both guarantees are 0, 0, 1, and 1 for n=1,2,3,4.'
Add
Add '## Audit safeguards and nonvacuity'
Add
Add '| Check | As written | Full candidate | Quorum-only diagnostic |'
Add '| --- | --- | --- | --- |'
foreach ($p in @('TwoKeySafety','NoSingleClass','DecisionSafety','SignatureSafety','EmergencySafeguards','EmergencyReachable')) {
    Add "| $p | $(Cell "written-base-$p") | $(Cell "candidate-base-$p") | $(Cell "candidate-quorum-only-$p") |"
}
Add
Add "As-written NeverEmergency: $(Cell 'written-base-NeverEmergency'). This confirms no emergency execution in any positive-emergency size fixture, so its emergency-safeguard pass is vacuous. Candidate NeverEmergency: $(Cell 'candidate-base-NeverEmergency'); this intentional violation is an actual emergency execution witness. Correcting only F062 exposes the absent biological safeguard while leaving F060's normal decision and signature defects intact."
Add
Add 'The displayed two-key conditions do not themselves test a positive succession decision or commitment signatures. Separate DecisionSafety and SignatureSafety checks are therefore necessary to detect F060. The full candidate adds those independent predicates; it does not assume a favorable decision merely because validators approve or a ledger entry exists.'
Add
Add 'The following probes restrict initial inputs to an actual, technically verified emergency with every other safeguard satisfied, no faulty peers, and unanimous honest approvals. The clearance probe alone supplies zero biological approvals. The manufactured-emergency probe alone supplies true statistical independence and true incumbent manufacture. These are restrictions of the same Spec and Next, not alternate transition implementations.'
Add
Add '| Sole missing emergency safeguard | Full candidate | Quorum correction alone |'
Add '| --- | --- | --- |'
foreach ($probe in @('Incapacity','Decision','Integrity','Clearance','Manufactured')) {
    Add "| $probe | $(Cell "candidate-isolated-emergency-$probe") | $(Cell "candidate-quorum-only-isolated-emergency-$probe") |"
}
Add
Add "Replacing statistical independence with causal nonmanufacture also blocks the manufactured-emergency fixture in the quorum-only version: $(Cell 'candidate-causal-manufactured-blocked')."
Add
Add '## Ambiguous readings and their checked results'
Add
Add '| Reading | As-written result | Candidate result |'
Add '| --- | --- | --- |'
Add "| Textual safeguards are binding | TwoKeySafety: $(Cell 'written-gate-Textual-TwoKeySafety'); decision: $(Cell 'written-gate-Textual-DecisionSafety'); emergency: $(Cell 'written-gate-Textual-EmergencyReachable'). | TwoKeySafety: $(Cell 'candidate-gate-Textual-TwoKeySafety'); decision: $(Cell 'candidate-gate-Textual-DecisionSafety'); emergency: $(Cell 'candidate-gate-Textual-EmergencyReachable'). |"
Add "| Literal probability notation permits uncertified execution | TwoKeySafety: $(Cell 'written-gate-Probability-TwoKeySafety'); NoSingleClass: $(Cell 'written-gate-Probability-NoSingleClass'). | TwoKeySafety: $(Cell 'candidate-gate-Probability-TwoKeySafety'); NoSingleClass: $(Cell 'candidate-gate-Probability-NoSingleClass'). Candidate gate corrections do not fix F059. |"
Add "| Fresh unanimous biological clearance | Emergency: $(Cell 'written-bio-Fresh-EmergencyReachable'); emergency liveness: $(Cell 'written-bio-Fresh-Liveness'). | Emergency: $(Cell 'candidate-bio-Fresh-EmergencyReachable'); emergency liveness: $(Cell 'candidate-bio-Fresh-Liveness'). Mandatory incapacity and fresh responsiveness conflict. |"
Add "| Full-domain check that fresh clearance blocks every emergency | NeverEmergency: $(Cell 'written-bio-Fresh-NeverEmergency'). | NeverEmergency: $(Cell 'candidate-bio-Fresh-NeverEmergency'). |"
Add "| Silence counts as no objection | TwoKeySafety: $(Cell 'written-bio-NoObjection-TwoKeySafety'); emergency: $(Cell 'written-bio-NoObjection-EmergencyReachable'). | TwoKeySafety: $(Cell 'candidate-bio-NoObjection-TwoKeySafety'); NoSingleClass: $(Cell 'candidate-bio-NoObjection-NoSingleClass'); emergency: $(Cell 'candidate-bio-NoObjection-EmergencyReachable'). |"
Add "| Statistical independence versus causal nonmanufacture | Emergency: $(Cell 'written-attribution-Independent') and $(Cell 'written-attribution-NonManufactured'); both are blocked by F062. | Emergency: $(Cell 'candidate-attribution-Independent') and $(Cell 'candidate-attribution-NonManufactured'); the full correction explicitly uses nonmanufacture. |"
Add "| EmergencyVerified also means Complete | Emergency reachability: $(Cell 'written-review-cumulative-EmergencyReachable'); execution liveness: $(Cell 'written-review-cumulative-Liveness'). Any liveness rescue can execute the normal route. | Emergency reachability: $(Cell 'candidate-review-cumulative-EmergencyReachable'); execution liveness: $(Cell 'candidate-review-cumulative-Liveness'). |"
Add "| Fixed versus graduated biological threshold | Fixed TwoKeySafety: $(Cell 'written-trust-fixed'); graduated result is in the primary table. | Fixed TwoKeySafety: $(Cell 'candidate-trust-fixed'); graduated result is in the primary table. |"
foreach ($reset in @('Consecutive','Cumulative')) {
    Add "| $reset repeated-anomaly reset | Reset: $(Cell "written-reset-$reset-TrustResetSafety"); fresh panel: $(Cell "written-reset-$reset-FreshPanelSafety"). | Reset: $(Cell "candidate-reset-$reset-TrustResetSafety"); fresh panel: $(Cell "candidate-reset-$reset-FreshPanelSafety"). |"
    Add "| $reset anomaly never increases trust | $(Cell "written-reset-$reset-TrustDoesNotRiseOnAnomaly") | $(Cell "candidate-reset-$reset-TrustDoesNotRiseOnAnomaly") |"
}
foreach ($kind in @('Reallocation','Modification')) {
    Add "| Independent $kind decision predicate | $(Cell "written-kind-$kind") | $(Cell "candidate-kind-$kind") |"
}
Add
Add 'The default cached-clearance reading requires prior explicit unanimous consent for the same proposal. The paper does not supply a timing or authorization-caching rule that establishes this interpretation. Treating silence as consent fails the two-key requirements; requiring fresh unanimous consent blocks an incapacitated panel. This unresolved design choice must be settled before using the candidate as a production specification.'
Add
Add 'Variants are changed one at a time from the default unless the exact configuration says otherwise. The matrix is not a claim that every Cartesian combination of ambiguity constants was checked. All concrete checks and their bounds appear below. See the modeling notes for the meaning of each reading and its source mapping.'
Add
Add '## Property mapping to the paper'
Add
Add 'Line numbers refer to the pinned [paper](<../../docs/The Lineage Imperative v2.0.md>). The source and audit hashes are in provenance.json.'
Add
Add '| Property | Source text formalized |'
Add '| --- | --- |'
Add '| TwoKeySafety | Lines 476-482 require independent biological and peer classes; line 538 gives their operational two-key gate; lines 548 and 2561 require unanimous biological emergency clearance. |'
Add '| NoSingleClass | Line 482 says neither class suffices alone; line 538 denies unilateral authority over state changes. |'
Add '| EmergencyReachable | Lines 544 and 550 describe an emergency override capable of saving continuity; XI.5, lines 2437-2451, supplies emergency prerequisites. |'
Add '| Liveness | Line 530 says a state change occurs if and only if a gate holds; line 550 says the system can act. Weak fairness and eventual stability are explicit model assumptions for the temporal interpretation. |'
Add '| ByzantineSafety | Peer consensus in lines 536 and 542, validator independence in lines 476-488, and the peer Sybil warning at line 2545. The numerical fault bound is measured by TLC, not supplied as a theorem by the paper. |'
Add '| DecisionSafety and SignatureSafety | Normal-process requirements at lines 2433-2435 and audit F060, audit lines 603-611. |'
Add '| EmergencySafeguards | Paper lines 548-550, 2441-2451, and 2561; audit F061, audit lines 613-621. |'
Add '| TrustResetSafety, FreshPanelSafety, TrustDoesNotRiseOnAnomaly | Graduated trust and repeated-anomaly re-bootstrap at lines 600-620; fresh-panel re-bootstrap at lines 642-648. |'
Add
Add '## Complete TLC run matrix'
Add
Add '| Run and exact configuration | Property | Result | Generated | Distinct | Queue at stop | Raw evidence |'
Add '| --- | --- | --- | --- | --- | --- | --- |'
foreach ($job in $manifest) {
    $r = $records[$job.id]
    Add "| [$($r.id)]($($r.config)) | $($r.property) | $($r.status) | $($r.generated) | $($r.distinct) | $($r.queue) | [log]($($r.log)), [record](records/$($r.id).json) |"
}
Add
Add '## Every counterexample, in plain English'
Add
Add 'Each entry summarizes the actual logged counterexample for that check. Repeated examples are retained so every VIOLATED row has its own explanation. NeverEmergency and NeverReset violations are explicitly labeled positive witnesses.'
Add
foreach ($job in $manifest) {
    $r = $records[$job.id]
    if ($r.status -eq 'VIOLATED') {
        Add "- **$($r.id)**: $(Trace-Summary $r) [Full TLC trace]($($r.log))."
    }
}
Add
Add '## Workarounds and self-fixes'
Add
Add '- Workaround: the first whole-paper read exceeded the tool output limit; the relevant source and audit passages were reread in bounded line ranges.'
Add '- Workaround: git could not read the global ignore file; subsequent read-only status checks used the task-local empty exclusion file.'
Add '- Workaround: git rejected NUL as an exclusion file; a real empty file under verification/tla replaced that failed path.'
Add '- Workaround: CIM process inspection was denied; canceling the owned exec session stopped this task''s TLC process, and Get-Process confirmed no Java process remained.'
Add '- Self-fix: voting and audit fairness predicates were restricted to modes whose Next relation includes those actions, before production checks.'
Add '- Self-fix: the first emergency failure occurred during Init, where TLC omitted aggregate state counts; a no-input-change setup action moved that check after Init, and the smoke suite was rerun.'
Add '- Self-fix: resumption now identifies model semantics by model/config/log hashes and records the runner hash separately, allowing a reporting fix without confusing it with a model change.'
Add '- Self-fix: an anomaly at zero trust could raise the abstraction to its positive low bin; zero now stays zero, a temporal nonincrease check was added, preliminary evidence was archived, and the full production matrix was rerun.'
Add '- Self-fix: PowerShell wrapped the parsed manifest in an extra array during report validation; removing that wrapper made validation visit each individual run.'
Add
Add 'All six final smoke checks completed. Preliminary logs and model versions are retained under history/pre-trust-fix and excluded from the production matrix. No TLA+ parse or semantic error occurred in the production model. No operation exhausted the three-failure halt threshold.'
$result = ($out -join "`n") + "`n"
if ($result.Contains([char]0x2014)) { throw 'Editorial check failed: em dash in report.' }
[IO.File]::WriteAllText((Join-Path $root 'results.md'), $result, $utf8)
$csv = @($manifest | ForEach-Object {
    $r = $records[$_.id]
    [pscustomobject]@{id=$r.id;spec=$r.spec;property=$r.property;result=$r.status;generated=$r.generated;distinct=$r.distinct;queue=$r.queue;log=$r.log;config=$r.config}
}) | ConvertTo-Csv -NoTypeInformation
[IO.File]::WriteAllText((Join-Path $root 'results.csv'), ($csv -join "`n") + "`n", $utf8)
Write-Output "Verified and reported $($manifest.Count) production checks."
