param([switch]$Smoke, [switch]$BuildOnly, [string]$Only = '*')
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath($PSScriptRoot)
$javaPath = 'C:/Users/matty/Dev/tools/jre/bin/java.exe'
$jarPath = 'C:/Users/matty/Dev/tools/tla/tla2tools.jar'
if (!(Test-Path -LiteralPath $javaPath) -or !(Test-Path -LiteralPath $jarPath)) {
    throw 'HALT: missing prerequisite; downloads are prohibited.'
}
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Write-Text([string]$path, [string]$value) {
    $resolved = [IO.Path]::GetFullPath($path)
    if (!$resolved.StartsWith($root + [IO.Path]::DirectorySeparatorChar)) {
        throw "Write outside verification/tla: $resolved"
    }
    [IO.File]::WriteAllText($resolved, $value, $utf8)
}
foreach ($sub in @('configs', 'logs', 'meta', 'records', 'tmp')) {
    [IO.Directory]::CreateDirectory((Join-Path $root $sub)) | Out-Null
}
$defaults = [ordered]@{
    ApplySafeguards = $true; MinBio = 1; MaxBio = 4; MinPeer = 1; MaxPeer = 4; f = 4
    Mode = 'Safety'; EvidenceMode = 'All'; GateReading = 'Equations'
    BioReading = 'Cached'; AttributionReading = 'Independent'; ReviewReading = 'Exclusive'
    TrustReading = 'Graduated'; ResetReading = 'Consecutive'; EnvironmentReading = 'Stable'
    QuorumReading = 'Fraction'; TauNum = 2; TauDen = 3; BioTauNum = 2; BioTauDen = 3
    ByzantineReading = 'PeerQuorum'; TransitionKind = 'Succession'; LiveTarget = 'Normal'
}
$jobs = New-Object System.Collections.Generic.List[object]
function Add-Job([string]$id, [string]$spec, [string]$property, [hashtable]$overrides = @{}, [bool]$temporal = $false, [string]$definition = 'Spec') {
    $settings = [ordered]@{}
    foreach ($key in $defaults.Keys) { $settings[$key] = $defaults[$key] }
    foreach ($key in $overrides.Keys) { $settings[$key] = $overrides[$key] }
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("SPECIFICATION $definition")
    $lines.Add('CHECK_DEADLOCK FALSE')
    $lines.Add('CONSTANTS')
    foreach ($key in $settings.Keys) {
        $v = $settings[$key]
        if ($v -is [bool]) { $v = $v.ToString().ToUpperInvariant() }
        elseif ($v -is [string]) { $v = '"' + $v + '"' }
        $lines.Add("  $key = $v")
    }
    $lines.Add('INVARIANT TypeOK')
    $lines.Add($(if ($temporal) { "PROPERTY $property" } else { "INVARIANT $property" }))
    $configText = ($lines -join "`n") + "`n"
    Write-Text (Join-Path $root "configs/$id.cfg") $configText
    $jobs.Add([pscustomobject]@{id=$id;spec=$spec;specDefinition=$definition;property=$property;temporal=$temporal;settings=$settings;config="configs/$id.cfg"})
}

foreach ($spec in @('COP_as_written', 'COP_candidate')) {
    $short = $(if ($spec -eq 'COP_as_written') { 'written' } else { 'candidate' })
    if ($Smoke) {
        Add-Job "$short-smoke2-safety" $spec 'TwoKeySafety' @{MaxBio=1;MaxPeer=1;f=0;EvidenceMode='Good'}
        Add-Job "$short-smoke2-emergency" $spec 'EmergencyReachable' @{MaxBio=1;MaxPeer=1;f=0;Mode='Emergency';EvidenceMode='Good'}
        Add-Job "$short-smoke2-live" $spec 'Liveness' @{MaxBio=1;MaxPeer=1;f=0;Mode='Liveness';EvidenceMode='Good'} $true
        continue
    }
    foreach ($prop in @('TwoKeySafety', 'NoSingleClass', 'DecisionSafety', 'SignatureSafety', 'EmergencySafeguards')) {
        Add-Job "$short-base-$prop" $spec $prop
    }
    Add-Job "$short-base-EmergencyReachable" $spec 'EmergencyReachable' @{Mode='Emergency';EvidenceMode='Good';f=0}
    Add-Job "$short-base-NeverEmergency" $spec 'NeverEmergency' @{Mode='Emergency';EvidenceMode='Good';f=0}
    foreach ($target in @('Normal', 'Emergency')) {
        Add-Job "$short-base-Liveness-$target" $spec 'Liveness' @{Mode='Liveness';EvidenceMode='Good';LiveTarget=$target} $true
        Add-Job "$short-anomalies-Liveness-$target" $spec 'Liveness' @{Mode='Liveness';EvidenceMode='Good';LiveTarget=$target;EnvironmentReading='Anomalies'} $true
    }
    foreach ($reset in @('Consecutive', 'Cumulative')) {
        foreach ($prop in @('TrustResetSafety', 'FreshPanelSafety', 'NeverReset')) {
            Add-Job "$short-reset-$reset-$prop" $spec $prop @{Mode='Reset';EvidenceMode='Good';ResetReading=$reset}
        }
        Add-Job "$short-reset-$reset-TrustDoesNotRiseOnAnomaly" $spec 'TrustDoesNotRiseOnAnomaly' @{Mode='Reset';EvidenceMode='Good';ResetReading=$reset} $true
    }
    foreach ($peers in 1..4) {
        foreach ($budget in 0..$peers) {
            Add-Job "$short-byz-n$peers-f$budget" $spec 'ByzantineSafety' @{MinPeer=$peers;MaxPeer=$peers;f=$budget;EvidenceMode='Good'}
        }
    }
    Add-Job "$short-byz-entire" $spec 'ByzantineSafety' @{ByzantineReading='EntireTransition'}
    foreach ($gate in @('Textual', 'Probability')) {
        foreach ($prop in @('TwoKeySafety', 'NoSingleClass', 'DecisionSafety', 'EmergencyReachable')) {
            $overrides = @{GateReading=$gate;EvidenceMode='Good'}
            if ($prop -eq 'EmergencyReachable') { $overrides.Mode='Emergency';$overrides.f=0 }
            if ($prop -eq 'DecisionSafety') { $overrides.EvidenceMode='Decision' }
            Add-Job "$short-gate-$gate-$prop" $spec $prop $overrides
        }
    }
    foreach ($bio in @('Fresh', 'NoObjection')) {
        foreach ($prop in @('TwoKeySafety', 'NoSingleClass', 'EmergencyReachable')) {
            $overrides = @{BioReading=$bio;EvidenceMode='Good'}
            if ($prop -eq 'EmergencyReachable') { $overrides.Mode='Emergency';$overrides.f=0 }
            Add-Job "$short-bio-$bio-$prop" $spec $prop $overrides
        }
        Add-Job "$short-bio-$bio-Liveness" $spec 'Liveness' @{BioReading=$bio;Mode='Liveness';EvidenceMode='Good';LiveTarget='Emergency'} $true
    }
    Add-Job "$short-bio-Fresh-NeverEmergency" $spec 'NeverEmergency' @{BioReading='Fresh';EvidenceMode='All'}
    foreach ($attrib in @('Independent', 'NonManufactured')) {
        Add-Job "$short-attribution-$attrib" $spec 'EmergencyReachable' @{AttributionReading=$attrib;Mode='Emergency';EvidenceMode='Good';f=0}
    }
    foreach ($prop in @('TwoKeySafety', 'NoSingleClass', 'EmergencyReachable')) {
        $ov = @{ReviewReading='Cumulative';EvidenceMode='Good'}
        if ($prop -eq 'EmergencyReachable') { $ov.Mode='Emergency';$ov.f=0 }
        Add-Job "$short-review-cumulative-$prop" $spec $prop $ov
    }
    Add-Job "$short-review-cumulative-Liveness" $spec 'Liveness' @{ReviewReading='Cumulative';Mode='Liveness';EvidenceMode='Good';LiveTarget='Emergency'} $true
    Add-Job "$short-trust-fixed" $spec 'TwoKeySafety' @{TrustReading='Fixed';EvidenceMode='Good'}
    foreach ($kind in @('Reallocation', 'Modification')) {
        Add-Job "$short-kind-$kind" $spec 'DecisionSafety' @{TransitionKind=$kind;EvidenceMode='Decision'}
    }
    foreach ($q in @(@(3,4), @(1,1))) {
        foreach ($peers in 1..4) {
            $required = [int][Math]::Ceiling($peers * $q[0] / $q[1])
            foreach ($budget in @(($required-1), $required)) {
                Add-Job "$short-tau-$($q[0])of$($q[1])-n$peers-f$budget" $spec 'ByzantineSafety' @{MinPeer=$peers;MaxPeer=$peers;f=$budget;EvidenceMode='Good';TauNum=$q[0];TauDen=$q[1]}
            }
        }
    }
    foreach ($q in @('Majority', 'Fraction')) {
        Add-Job "$short-quorum-$q" $spec 'EmergencyReachable' @{QuorumReading=$q;Mode='Emergency';EvidenceMode='Good';f=0}
    }
}
if (!$Smoke) {
    foreach ($prop in @('TwoKeySafety', 'NoSingleClass', 'DecisionSafety', 'SignatureSafety', 'EmergencySafeguards', 'EmergencyReachable')) {
        $ov = @{ApplySafeguards=$false}
        if ($prop -eq 'EmergencyReachable') { $ov.Mode='Emergency';$ov.EvidenceMode='Good';$ov.f=0 }
        Add-Job "candidate-quorum-only-$prop" 'COP_candidate' $prop $ov
    }
    foreach ($missing in @('Incapacity','Decision','Integrity')) {
        Add-Job "candidate-missing-$missing" 'COP_candidate' 'EmergencySafeguards' @{EvidenceMode=$missing}
        Add-Job "candidate-quorum-only-missing-$missing" 'COP_candidate' 'EmergencySafeguards' @{EvidenceMode=$missing;ApplySafeguards=$false}
    }
    foreach ($spec in @('COP_as_written','COP_candidate')) {
        $short = $(if ($spec -eq 'COP_as_written') { 'written' } else { 'candidate' })
        Add-Job "$short-isolated-no-decision" $spec 'DecisionSafety' @{EvidenceMode='Decision'}
        Add-Job "$short-isolated-no-signature" $spec 'SignatureSafety' @{EvidenceMode='Signature'}
        foreach ($attrib in @('Independent','NonManufactured')) {
            Add-Job "$short-no-independence-$attrib" $spec 'NeverEmergency' @{EvidenceMode='Independent';AttributionReading=$attrib;f=0}
        }
    }
    foreach ($attrib in @('Independent','NonManufactured')) {
        Add-Job "candidate-quorum-only-no-independence-$attrib" 'COP_candidate' 'NeverEmergency' @{EvidenceMode='Independent';AttributionReading=$attrib;ApplySafeguards=$false;f=0}
    }
    . (Join-Path $root 'guard-probe-jobs.ps1')
    foreach ($spec in @('COP_as_written','COP_candidate')) {
        $src = Join-Path $root "configs/$(if($spec -eq 'COP_as_written'){'written'}else{'candidate'})-base-TwoKeySafety.cfg"
        Write-Text (Join-Path $root "$spec.cfg") ([IO.File]::ReadAllText($src))
    }
}
Write-Text (Join-Path $root "$(if($Smoke){'smoke'}else{'run'})-manifest.json") (($jobs | ConvertTo-Json -Depth 8) + "`n")
if ($BuildOnly) { Write-Output "Built $($jobs.Count) configurations."; exit 0 }

function Hash([string]$path) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash }
$codeHashes = [ordered]@{}
foreach ($file in @('COP_core.tla','COP_as_written.tla','COP_candidate.tla')) {
    $codeHashes[$file] = Hash (Join-Path $root $file)
}
$selected = @($jobs | Where-Object { $_.id -like $Only })
$complete = 0
foreach ($job in $selected) {
    $controlPath = Join-Path $root 'control.json'
    if (Test-Path -LiteralPath $controlPath) {
        $control = Get-Content -LiteralPath $controlPath -Raw | ConvertFrom-Json
        if ($control.stopAfterCurrent) {
            Write-Output "Stopped between checks with $complete complete and $($selected.Count-$complete) pending."
            break
        }
    }
    foreach ($key in $codeHashes.Keys) {
        if ((Hash (Join-Path $root $key)) -ne $codeHashes[$key]) { throw "Model changed during execution: $key" }
    }
    $jobCodeHashes = [ordered]@{}
    foreach ($key in $codeHashes.Keys) { $jobCodeHashes[$key] = $codeHashes[$key] }
    $jobModule = "$($job.spec).tla"
    $jobCodeHashes[$jobModule] = Hash (Join-Path $root $jobModule)
    $recordPath = Join-Path $root "records/$($job.id).json"
    $configHash = Hash (Join-Path $root $job.config)
    if (Test-Path -LiteralPath $recordPath) {
        $previous = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
        $matches = $previous.configHash -eq $configHash
        foreach ($key in $jobCodeHashes.Keys) { $matches = $matches -and ($previous.codeHashes.$key -eq $jobCodeHashes[$key]) }
        if ($matches -and (Test-Path -LiteralPath (Join-Path $root $previous.log)) -and
            (Hash (Join-Path $root $previous.log)) -eq $previous.logHash) { $complete++; continue }
        throw "Existing result $($job.id) has incompatible identity. Preserve it and use a new run id."
    }
    $metaPath = Join-Path $root "meta/$($job.id)"
    [IO.Directory]::CreateDirectory($metaPath) | Out-Null
    $logRelative = "logs/$($job.id).log"
    $logPath = Join-Path $root $logRelative
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $javaPath
    $psi.WorkingDirectory = $root
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.Arguments = '-XX:+UseParallelGC -XX:ActiveProcessorCount=2 -XX:ParallelGCThreads=2 -Xmx768m ' +
        '"-Djava.io.tmpdir=' + (Join-Path $root 'tmp') + '" -cp "' + $jarPath +
        '" tlc2.TLC -workers 2 -seed 0 -fp 0 -metadir "' + $metaPath +
        '" -config "' + (Join-Path $root $job.config) + '" ' + $job.spec
    $started = [DateTime]::UtcNow.ToString('o')
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()
    Write-Text (Join-Path $root 'current-run.json') (([ordered]@{
        id=$job.id;pid=$process.Id;startedUTC=$started;completed=$complete;
        running=1;pending=$selected.Count-$complete-1;workers=2;status='running'
    } | ConvertTo-Json) + "`n")
    $stdout = $process.StandardOutput.ReadToEndAsync()
    $stderr = $process.StandardError.ReadToEndAsync()
    $process.WaitForExit()
    $output = $stdout.Result + $stderr.Result
    Write-Text $logPath $output
    $status = 'ERROR'
    if ($output -match 'Model checking completed. No error has been found.') { $status = 'HOLDS' }
    elseif ($output -match ('Invariant ' + [regex]::Escape($job.property) + ' is violated') -or
            ($job.temporal -and $output -match 'Temporal properties were violated')) { $status = 'VIOLATED' }
    $counts = [regex]::Match($output, '([\d,]+) states generated, ([\d,]+) distinct states found, ([\d,]+) states left on queue')
    $generated = $null; $distinct = $null; $queue = $null
    if ($counts.Success) {
        $generated = [long]$counts.Groups[1].Value.Replace(',','')
        $distinct = [long]$counts.Groups[2].Value.Replace(',','')
        $queue = [long]$counts.Groups[3].Value.Replace(',','')
    }
    $record = [ordered]@{id=$job.id;spec=$job.spec;property=$job.property;status=$status;
        generated=$generated;distinct=$distinct;queue=$queue;exitCode=$process.ExitCode;
        settings=$job.settings;config=$job.config;configHash=$configHash;codeHashes=$jobCodeHashes;
        log=$logRelative;logHash=(Hash $logPath);startedUTC=$started;finishedUTC=[DateTime]::UtcNow.ToString('o');
        machine=$env:COMPUTERNAME;workers=2;jvmActiveProcessors=2;parallelGCThreads=2;
        runnerHash=(Hash (Join-Path $root 'RunChecks.ps1'));
        command=$psi.FileName + ' ' + $psi.Arguments}
    if ($status -eq 'ERROR') {
        Write-Text (Join-Path $root "records/$($job.id).error.json") (($record | ConvertTo-Json -Depth 8) + "`n")
        Write-Output $output
        throw "TLC evaluation or tool error for $($job.id); inspect and fix before resumption."
    }
    if ($null -eq $generated) { throw "Cannot parse state counts for $($job.id)" }
    $temporaryRecord = "$recordPath.partial"
    Write-Text $temporaryRecord (($record | ConvertTo-Json -Depth 8) + "`n")
    [IO.File]::Move($temporaryRecord, $recordPath)
    $complete++
    Write-Text (Join-Path $root 'current-run.json') (([ordered]@{
        id=$job.id;pid=$null;completed=$complete;running=0;
        pending=$selected.Count-$complete;workers=2;status='completed'
    } | ConvertTo-Json) + "`n")
    Write-Output "$complete/$($selected.Count) $($job.id): $status ($generated generated, $distinct distinct)"
}
