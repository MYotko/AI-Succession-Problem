$ErrorActionPreference = 'Stop'

$repo = 'C:\Users\matty\OneDrive\Documents\GitHub\AI-Succession-Problem'
$python = 'C:\Python314\python.exe'
$branch = 'attack-v2-laptop'
$commit = '5ac6a2e'
$log = Join-Path $repo 'data\attack_vector_revalidation_v2\laptop\logs\queue.log'
$parents = @(5292, 35072, 31216)
$baselines = @(
    'data/comprehensive_adversarial_sweeps.csv',
    'data/comprehensive_adversarial_sweeps_v1x2_phi.csv',
    'data/veto_capture_sweep_v1.csv',
    'data/veto_capture_sweep_v2.csv'
)

function Write-QueueLog([string]$message) {
    $timestamp = (Get-Date).ToUniversalTime().ToString('o')
    Add-Content -LiteralPath $log -Value "$timestamp $message"
}

function Assert-ProtectedFiles {
    & git -C $repo diff --quiet pre-attack-vector-revalidation -- $baselines
    if ($LASTEXITCODE -ne 0) {
        throw 'Protected baseline diff check failed.'
    }
}

function Commit-And-Push(
    [string]$message,
    [string[]]$paths
) {
    Assert-ProtectedFiles
    & git -C $repo add -- $paths
    if ($LASTEXITCODE -ne 0) {
        throw "git add failed: $message"
    }
    & git -C $repo commit -m $message
    if ($LASTEXITCODE -ne 0) {
        throw "git commit failed: $message"
    }
    & git -C $repo push origin $branch
    if ($LASTEXITCODE -ne 0) {
        throw "git push failed: $message"
    }
}

Set-Location -LiteralPath $repo
Write-QueueLog 'Waiting for laptop Biological Veto shards.'
Wait-Process -Id $parents

$shardStatuses = @(
    'simulation/diagnostics/attack_vector_revalidation_status_laptop_shard_0_of_4.md',
    'simulation/diagnostics/attack_vector_revalidation_status_laptop_shard_1_of_4.md',
    'simulation/diagnostics/attack_vector_revalidation_status_laptop_shard_2_of_4.md'
)
foreach ($status in $shardStatuses) {
    if (-not (Select-String -LiteralPath $status -SimpleMatch 'State: `completed`')) {
        throw "Laptop shard did not complete successfully: $status"
    }
}

$shardPaths = @(
    'data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard0of4',
    'data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard1of4',
    'data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard2of4'
) + $shardStatuses
Commit-And-Push 'Add laptop Biological Veto v2 shards' $shardPaths
Write-QueueLog 'Committed laptop Biological Veto shards.'

$vectors = @(
    'measurement_tampering',
    'successor_contamination',
    'sybil_capture',
    'evaluator_collusion'
)

foreach ($vector in $vectors) {
    $runId = "full_${commit}_${vector}"
    Write-QueueLog "Starting $vector."
    & $python simulation/run_attack_vector_revalidation_v2.py `
        --vector $vector `
        --mode full `
        --machine laptop `
        --workers 15 `
        --run-id $runId
    if ($LASTEXITCODE -ne 0) {
        throw "Full vector failed: $vector"
    }
    $paths = @(
        "data/attack_vector_revalidation_v2/laptop/$vector/$runId",
        'simulation/diagnostics/attack_vector_revalidation_status_laptop.md'
    )
    Commit-And-Push "Add laptop $vector v2 results" $paths
    Write-QueueLog "Committed $vector."
}

Write-QueueLog 'Laptop queue completed.'
