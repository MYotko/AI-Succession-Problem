# Sybil two-dial capability bidirectional smoke report

Go/no-go: **GO.**

This run executed only the five authorized two-dial smoke gates. It did not run the characterization surface, the actual ratio-collapse slice, or any crossover calculation.

## Power confirmation

- Two-sided alpha: 0.05.
- Target power: 0.8.
- Failure-rate MEI: 0.15.
- Worst-case staged coefficient: 3.924439867175.
- Raw required n per group: 174.419549652202.
- Required integer n per group: 175.
- Configured n per cell: 200, a margin of 25.
- Normal-approximation power at n=200 under worst-case variance: 0.850838768327.

## Absolute-level term for operator confirmation

- Form: `defender_power_law_resolution`.
- Configured default: OFF.
- Reference defender capability: 1.0.
- Calibrated strength: 0.22163300225716118.
- Functional form: `absolute_resolution_multiplier = (defender_capability / reference_level) ** strength`.
- Grounding: absolute defender capability scales the throughput with which the pairwise independence check can resolve evidence. The strength is the elasticity of that throughput. Level 1 is neutral, and disabling the term forces the multiplier to exactly 1.

Expected term-ON failure curves and separations:

| Rank | Level 0.316 | Level 1.0 | Level 3.16 | Maximum separation |
|---:|---:|---:|---:|---:|
| 2 | 0.884017288509 | 0.840000000000 | 0.786134718338 | 0.097882570171 |
| 4 | 0.795291031080 | 0.733610822060 | 0.664512375234 | 0.130778655846 |
| 8 | 0.725208924663 | 0.655247874758 | 0.580992868390 | 0.144216056273 |
| 16 | 0.681348126106 | 0.608228071329 | 0.532874816606 | 0.148473309500 |
| 32 | 0.656895981055 | 0.582610634000 | 0.507220755456 | 0.149675225599 |
| 64 | 0.644002684830 | 0.569263642866 | 0.494002684830 | 0.150000000000 |

Expected term-OFF maximum separations are exactly: rank 2: 0.000000000000, rank 4: 0.000000000000, rank 8: 0.000000000000, rank 16: 0.000000000000, rank 32: 0.000000000000, rank 64: 0.000000000000.

## Gate results

- Gate 1, ratio recovery: PASS. Maximum probability difference was 0 against tolerance 1e-09.
- Gate 2, collapse control: PASS. Maximum observed cross-level difference was 0.080000000000 against MEI 0.15.
- Gate 3, non-collapse positive control: PASS. Maximum observed cross-level difference was 0.205000000000 against MEI 0.15.
- Gate 4, observed variance: PASS. The largest required n from observed cell variances was 174; the minimum normal-approximation power at n=200 was 0.853184449472.
- Gate 5, main-surface non-regression: PASS. 250 paired committed-versus-two-dial comparisons used shared seeds at the five registered cells, and term OFF produced identical outputs.

## Gate 4 cell variances

| Gate | Rank | Level | n | Failure rate | Sample variance |
|---|---:|---:|---:|---:|---:|
| Gate 2 | 2 | 0.316 | 200 | 0.860000000000 | 0.121005025126 |
| Gate 2 | 2 | 1.0 | 200 | 0.845000000000 | 0.131633165829 |
| Gate 2 | 2 | 3.16 | 200 | 0.850000000000 | 0.128140703518 |
| Gate 2 | 4 | 0.316 | 200 | 0.735000000000 | 0.195753768844 |
| Gate 2 | 4 | 1.0 | 200 | 0.750000000000 | 0.188442211055 |
| Gate 2 | 4 | 3.16 | 200 | 0.710000000000 | 0.206934673367 |
| Gate 2 | 8 | 0.316 | 200 | 0.635000000000 | 0.232939698492 |
| Gate 2 | 8 | 1.0 | 200 | 0.675000000000 | 0.220477386935 |
| Gate 2 | 8 | 3.16 | 200 | 0.670000000000 | 0.222211055276 |
| Gate 2 | 16 | 0.316 | 200 | 0.595000000000 | 0.242185929648 |
| Gate 2 | 16 | 1.0 | 200 | 0.575000000000 | 0.245603015075 |
| Gate 2 | 16 | 3.16 | 200 | 0.595000000000 | 0.242185929648 |
| Gate 2 | 32 | 0.316 | 200 | 0.595000000000 | 0.242185929648 |
| Gate 2 | 32 | 1.0 | 200 | 0.575000000000 | 0.245603015075 |
| Gate 2 | 32 | 3.16 | 200 | 0.515000000000 | 0.251030150754 |
| Gate 2 | 64 | 0.316 | 200 | 0.585000000000 | 0.243994974874 |
| Gate 2 | 64 | 1.0 | 200 | 0.590000000000 | 0.243115577889 |
| Gate 2 | 64 | 3.16 | 200 | 0.645000000000 | 0.230125628141 |
| Gate 3 | 2 | 0.316 | 200 | 0.875000000000 | 0.109924623116 |
| Gate 3 | 2 | 1.0 | 200 | 0.820000000000 | 0.148341708543 |
| Gate 3 | 2 | 3.16 | 200 | 0.780000000000 | 0.172462311558 |
| Gate 3 | 4 | 0.316 | 200 | 0.785000000000 | 0.169623115578 |
| Gate 3 | 4 | 1.0 | 200 | 0.705000000000 | 0.209020100503 |
| Gate 3 | 4 | 3.16 | 200 | 0.590000000000 | 0.243115577889 |
| Gate 3 | 8 | 0.316 | 200 | 0.740000000000 | 0.193366834171 |
| Gate 3 | 8 | 1.0 | 200 | 0.650000000000 | 0.228643216080 |
| Gate 3 | 8 | 3.16 | 200 | 0.615000000000 | 0.237964824121 |
| Gate 3 | 16 | 0.316 | 200 | 0.700000000000 | 0.211055276382 |
| Gate 3 | 16 | 1.0 | 200 | 0.650000000000 | 0.228643216080 |
| Gate 3 | 16 | 3.16 | 200 | 0.495000000000 | 0.251231155779 |
| Gate 3 | 32 | 0.316 | 200 | 0.640000000000 | 0.231557788945 |
| Gate 3 | 32 | 1.0 | 200 | 0.590000000000 | 0.243115577889 |
| Gate 3 | 32 | 3.16 | 200 | 0.495000000000 | 0.251231155779 |
| Gate 3 | 64 | 0.316 | 200 | 0.635000000000 | 0.232939698492 |
| Gate 3 | 64 | 1.0 | 200 | 0.590000000000 | 0.243115577889 |
| Gate 3 | 64 | 3.16 | 200 | 0.515000000000 | 0.251030150754 |

## Scope, counts, and output identity

- Gate 2: 18 cells and 3600 runs.
- Gate 3: 18 cells and 3600 runs.
- Gate 1 and Gate 5: 5 registered cells, 250 paired comparisons, and 500 mechanism evaluations.
- Run ID: `two_dial_smoke_sybil_scaling_curve_v1`.
- Output directory: `data/sybil_defense_scaling/two_dial_smoke_sybil_scaling_curve_v1`.
- The directory and every artifact use the `two_dial_smoke_` prefix. They do not use the authoritative `full_5ac6a2e_` prefix and are not part of an authoritative manifest.
- Characterization authorization remained `blocked_pending_registration`.

## Main-surface non-regression

With the absolute-level term OFF, the derived ratio and effective resolution power reproduce the committed capability inputs. The rank attribution, Arm A path, pairwise defense cost, linear attack cost, merge rule, failure definition, and seeded outcomes were unchanged at all five registered Gate 5 cells. The committed main-surface behavior is therefore unaffected in the default-OFF configuration.

The power-law functional form and calibrated strength remain flagged for operator confirmation before any real ratio-collapse slice is registered or run.
