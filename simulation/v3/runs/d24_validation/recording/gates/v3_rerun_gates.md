# v3 rerun gates

Phase: all. Fixtures: False. No missing check counts as a pass.

| Check | Status | Cases | Failures | Nominal zero-failure bound (95%) |
|---|---|---:|---:|---:|
| G1.1 | passed | 12 | 0 | 0.22092219194555587 |
| G1.2 | passed | 256 | 0 | 0.011633876163163285 |
| G1.3 | passed | 326 | 0 | 0.009147269643070288 |
| G1.4 | passed | 15 | 0 | 0.18103627252208465 |
| G1.5 | passed | 34 | 0 | 0.0843396433506254 |
| G3.1.scenarios | passed | 5 | 0 | 0.45071972834694113 |
| G3.1.sample | passed | 200 | 0 | 0.014867039231272059 |
| G3.2 | passed | 3 | 0 | 0.6315968501359612 |
| G2.2 | failed | 0 | 1 | not applicable |
| G4.2 | failed | 0 | 1 | not applicable |
| G3.3 | not_testable | 0 | 0 | not applicable |
| G4.1 | failed | 1000 | 1 | not applicable |
| G4.3 | passed | 120 | 0 | 0.024655401055656383 |
| G2.1 | not_applicable | 0 | 0 | not applicable |
| G2.4 | not_applicable | 0 | 0 | not applicable |
| G2.3 | not_applicable | 0 | 0 | not applicable |
| G5.1 | not_applicable | 0 | 0 | not applicable |
| G5.2 | not_applicable | 0 | 0 | not applicable |

Cleared through: 1.
Citable results: {'R1': False, 'R2': False, 'R2_cliff': False}.

The nominal bound is 1 - 0.05^(1/n). Chosen scenarios and dependent/stratified records do not support an unrestricted iid failure-rate claim.

- G2.2: ['incomplete R2 seed/grid evidence']
- G4.2: ['incomplete R2 seed/grid evidence']
- G3.3: D23: no R2 succession fired anywhere in the verified family
- G4.1: ['fewer than 10000 living-start R2 steps']
- G2.1: D10: phi study
- G2.4: D10: phi study
- G2.3: D12/W2 deviation-set game deferred to W3; no game in these reruns
- G5.1: D10: waits for P4
- G5.2: D10: waits for P4
