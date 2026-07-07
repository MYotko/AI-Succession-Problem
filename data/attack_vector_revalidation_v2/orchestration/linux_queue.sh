#!/usr/bin/env bash
set -euo pipefail

repo=/home/yotko/projects/AI-Succession-Problem-attack-v2
python="$repo/.venv/bin/python"
branch=attack-v2-linux
commit=5ac6a2e
parent_pid=2743952
log="$repo/data/attack_vector_revalidation_v2/linux/logs/queue.log"

write_log() {
    printf '%s %s\n' "$(date --utc --iso-8601=seconds)" "$1" >> "$log"
}

assert_protected_files() {
    git -C "$repo" diff --quiet pre-attack-vector-revalidation -- \
        data/comprehensive_adversarial_sweeps.csv \
        data/comprehensive_adversarial_sweeps_v1x2_phi.csv \
        data/veto_capture_sweep_v1.csv \
        data/veto_capture_sweep_v2.csv
}

commit_and_push() {
    message=$1
    shift
    assert_protected_files
    git -C "$repo" add -- "$@"
    git -C "$repo" commit -m "$message"
    git -C "$repo" push origin "$branch"
}

write_log 'Waiting for Linux Biological Veto shard.'
while kill -0 "$parent_pid" 2>/dev/null; do
    sleep 60
done

veto_status=simulation/diagnostics/attack_vector_revalidation_status_linux_shard_3_of_4.md
grep -Fq 'State: `completed`' "$repo/$veto_status"
commit_and_push \
    'Add Linux Biological Veto v2 shard' \
    data/attack_vector_revalidation_v2/linux/biological_veto_capture/full_5ac6a2e_veto_shard3of4 \
    "$veto_status"
write_log 'Committed Linux Biological Veto shard.'

vectors=(
    ledger_compromise
    domain_masking
    opaque_reasoning
    bootstrap_subversion
    sub_threshold_drift
    engineered_fragility
)

cd "$repo"
for vector in "${vectors[@]}"; do
    run_id="full_${commit}_${vector}"
    write_log "Starting $vector."
    "$python" simulation/run_attack_vector_revalidation_v2.py \
        --vector "$vector" \
        --mode full \
        --machine linux \
        --workers 11 \
        --run-id "$run_id"
    commit_and_push \
        "Add Linux $vector v2 results" \
        "data/attack_vector_revalidation_v2/linux/$vector/$run_id" \
        simulation/diagnostics/attack_vector_revalidation_status_linux.md
    write_log "Committed $vector."
done

write_log 'Linux queue completed.'
