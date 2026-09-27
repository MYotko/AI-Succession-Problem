# Loaded by RunChecks.ps1 after Add-Job has been defined.
foreach ($probe in @('Incapacity','Decision','Integrity','Clearance','Manufactured')) {
    $definition = if ($probe -eq 'Manufactured') { 'ManufacturedSpec' } else { "No${probe}Spec" }
    Add-Job "candidate-isolated-emergency-$probe" 'COP_guard_probes' 'EmergencySafeguards' @{f=0} $false $definition
    Add-Job "candidate-quorum-only-isolated-emergency-$probe" 'COP_guard_probes' 'EmergencySafeguards' @{f=0;ApplySafeguards=$false} $false $definition
}
Add-Job 'candidate-causal-manufactured-blocked' 'COP_guard_probes' 'EmergencySafeguards' @{f=0;ApplySafeguards=$false;AttributionReading='NonManufactured'} $false 'ManufacturedSpec'
