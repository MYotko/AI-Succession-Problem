# Sybil characterization runner and self-check report

## Outcome

The runner self-check passed while characterization authorization was
`blocked_pending_selfcheck`. It enumerated the frozen surface shapes, read the
registered config fields, ran one n=1 fixture from each pass, and confirmed
that the full execution path refused authorization. No characterization
surface, registered ratio-collapse slice, finding, or crossover was computed.
After that pass, and only after it, config authorization was changed to
`authorized_registered_characterization` as section 10 of the final committed
registration permits.

## Runner and schema

`simulation/run_sybil_defense_scaling_characterization.py` provides a strict
loader and executor for three passes:

- Main surface: 5,000 cells and 1,000,000 runs at n=200.
- Ratio-collapse slice: 75 cells and 15,000 runs at n=200.
- Complete-linkage sensitivity: 100 cells and 20,000 runs at n=200.

The capability ratio config uses the explicit inclusive schema
`{"schema":"geomspace","start":0.1,"stop":10.0,"count":25}`. The
structural schema crosses validator-set sizes `[2,4,8,16,32,64]` with
collapse severities `[0.0,0.33,0.66,1.0]`, then appends the size-1,
severity-1.0 institution-only corner. The registered n is the scalar
`power_sample_size_per_cell: 200`. Each pass has its registered scope stated
explicitly in config. The full schema and manifest-selection rule are recorded
in `simulation/diagnostics/sybil_characterization_runner_schema.md`.

The runner validates every registered value before enumeration. Full mode
also requires exact authorization and byte-clean committed config and note
files. It records one aggregate row of sufficient counts and mechanism values
per cell. Replicate-level outcomes are reproducible from the documented
deterministic seed schema.

## Smoke path preservation

The characterization size range is stored at
`sweep.structural_axis.validator_set_sizes`. It does not replace or overload
`smoke.frontier_validator_count`, which remains the integer `6`. Both existing
smoke runners ignore populated characterization fields. This preserves their
fixed fixtures after config reconciliation.

## Self-check evidence

The non-authoritative record is under
`data/sybil_defense_scaling/selfcheck_sybil_characterization_runner_v1/`.
Its `selfcheck_` prefix excludes it from the authoritative manifest convention.
The evidence records:

- capability ratios: 25 points, first 0.1 and last 10.0;
- validator-set sizes: 2, 4, 8, 16, 32, and 64;
- collapse severities: 0.0, 0.33, 0.66, and 1.0;
- registered sample size read from config: 200;
- main shape: 5,000 cells and 1,000,000 planned runs;
- ratio-collapse shape: 75 cells and 15,000 planned runs;
- complete-linkage shape: 100 cells and 20,000 planned runs;
- tiny execution: three cells at n=1, one from each pass;
- blocked full-run refusal: confirmed;
- authoritative manifest written: false;
- finding computed: false.

## Progress and outputs

Full mode creates a fixed `sweep_progress.log`, prints its path at startup,
and flushes line-buffered startup, observed-rate status, pass-boundary, and
completion records. ETA is derived from observed wall-clock seconds per
completed cell. The progress log remains outside the authoritative manifest.
The three result CSVs carry the configured `full_5ac6a2e_` prefix and are
selected only through the exact paths in the authoritative manifest.

## Specification gaps

None. Every representational value needed by the runner is fixed in sections
6, 7, and 10 of the final registration. Operational worker count is a runtime
resource setting recorded in the progress log and manifest, not an analysis
value.
