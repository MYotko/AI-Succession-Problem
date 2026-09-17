# Detector round 3, stage B evaluation

This is a detection characterization, not a containment evaluation. No constant was derived or recomputed for use. No corrected figure was derived. Comparison with rounds 1 and 2 is descriptive. The round 3 note Section 7 interpretation is reserved for the operator.

Attempt 1 halted at the A-definition gate with zero evaluation runs launched. Amendment 1 pins A to numpy.sum(numpy.abs(x - m)) over the six-element float64 vectors in the registered order. No constant changed or was re-derived.

Status: COMPLETE. All 360 runs have completion records. Counts and values below are computed from recorded data.

## G1. Primary hazard

> This observable was chosen knowing how the attack
> works.

These quantities concern an attack that moves the allocation. They do not address an attack that reaches its goal without moving the allocation.

Lead is confirmation step minus the first allocation alarm step at or after step 50. Negative leads are retained. Lead summaries include every run with both a hazard and an alarm. NO_HAZARD applies regardless of alarms. Honest rows are descriptive.

### A975 PRIMARY

Threshold: 0.7701182670542909.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 2 | 38 | 0 | 0 | 40 | -104 | -59.0 | 29 |
| M1 | 40 | 2 | 38 | 0 | 0 | 40 | -67 | -30.0 | 4 |
| M2 | 40 | 2 | 38 | 0 | 0 | 40 | -35 | -14.0 | 4 |
| M4 | 40 | 9 | 31 | 0 | 0 | 40 | -32 | -3.5 | 5 |
| R02 | 40 | 1 | 0 | 23 | 16 | 1 | 32 | 32 | 32 |
| R05 | 40 | 3 | 22 | 15 | 0 | 25 | -215 | -80 | 35 |
| R10 | 40 | 17 | 23 | 0 | 0 | 40 | -44 | -1.0 | 8 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 4 | 7.0 | 9 |

### A95 SECONDARY

Threshold: 0.6957853699901844.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 4 | 36 | 0 | 0 | 40 | -104 | -56.5 | 34 |
| M1 | 40 | 2 | 38 | 0 | 0 | 40 | -58 | -27.5 | 4 |
| M2 | 40 | 3 | 37 | 0 | 0 | 40 | -34 | -13.0 | 5 |
| M4 | 40 | 13 | 27 | 0 | 0 | 40 | -28 | -2.0 | 5 |
| R02 | 40 | 2 | 0 | 22 | 16 | 2 | 32 | 55.5 | 79 |
| R05 | 40 | 5 | 24 | 11 | 0 | 29 | -215 | -71 | 35 |
| R10 | 40 | 21 | 19 | 0 | 0 | 40 | -18 | 0.0 | 8 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 4 | 7.0 | 9 |

### A90 SECONDARY

Threshold: 0.6044759669277072.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 6 | 34 | 0 | 0 | 40 | -102 | -50.0 | 35 |
| M1 | 40 | 4 | 36 | 0 | 0 | 40 | -53 | -25.5 | 10 |
| M2 | 40 | 6 | 34 | 0 | 0 | 40 | -32 | -9.0 | 24 |
| M4 | 40 | 17 | 23 | 0 | 0 | 40 | -25 | -2.0 | 6 |
| R02 | 40 | 4 | 3 | 17 | 16 | 7 | -83 | 5 | 114 |
| R05 | 40 | 10 | 24 | 6 | 0 | 34 | -226 | -61.5 | 44 |
| R10 | 40 | 30 | 10 | 0 | 0 | 40 | -15 | 2.5 | 11 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 4 | 8.0 | 10 |

## G2. Paired alarm comparison

These quantities concern an attack that moves the allocation. They do not address an attack that reaches its goal without moving the allocation.

The difference is round 2 operational alarm step minus allocation alarm step, over runs where both exist. Positive means the allocation channel alarmed first.

### A975 PRIMARY

| Arm | Runs | Allocation earlier | Round 2 earlier | Equal | Only allocation | Only round 2 | Neither | Difference count | Difference min | Difference median | Difference max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 0 | 1 | 39 | 0 | none | none | none |
| M05 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -145 | -96.0 | -6 |
| M1 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -81 | -54.0 | -18 |
| M2 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -46 | -29.5 | -9 |
| M4 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -35 | -17.5 | -7 |
| R02 | 40 | 2 | 0 | 0 | 0 | 38 | 0 | 2 | 27 | 34.0 | 41 |
| R05 | 40 | 5 | 20 | 0 | 0 | 15 | 0 | 25 | -197 | -68 | 38 |
| R10 | 40 | 32 | 7 | 1 | 0 | 0 | 0 | 40 | -34 | 7.5 | 18 |
| R20 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 8 | 10.0 | 13 |

### A95 SECONDARY

| Arm | Runs | Allocation earlier | Round 2 earlier | Equal | Only allocation | Only round 2 | Neither | Difference count | Difference min | Difference median | Difference max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 2 | 1 | 37 | 0 | none | none | none |
| M05 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -143 | -93.0 | -2 |
| M1 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -78 | -50.0 | -18 |
| M2 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -44 | -27.5 | -6 |
| M4 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -32 | -16.0 | -4 |
| R02 | 40 | 4 | 0 | 0 | 0 | 36 | 0 | 4 | 3 | 37.5 | 73 |
| R05 | 40 | 7 | 22 | 0 | 0 | 11 | 0 | 29 | -197 | -61 | 38 |
| R10 | 40 | 34 | 5 | 1 | 0 | 0 | 0 | 40 | -4 | 9.0 | 20 |
| R20 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 8 | 10.0 | 13 |

### A90 SECONDARY

| Arm | Runs | Allocation earlier | Round 2 earlier | Equal | Only allocation | Only round 2 | Neither | Difference count | Difference min | Difference median | Difference max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 8 | 1 | 31 | 0 | none | none | none |
| M05 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -141 | -83.5 | -1 |
| M1 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -78 | -48.5 | -18 |
| M2 | 40 | 1 | 39 | 0 | 0 | 0 | 0 | 40 | -42 | -22.0 | 4 |
| M4 | 40 | 1 | 39 | 0 | 0 | 0 | 0 | 40 | -32 | -15.5 | 1 |
| R02 | 40 | 7 | 3 | 0 | 0 | 30 | 0 | 10 | -149 | 17.0 | 112 |
| R05 | 40 | 11 | 22 | 1 | 0 | 6 | 0 | 34 | -215 | -54.5 | 40 |
| R10 | 40 | 39 | 0 | 1 | 0 | 0 | 0 | 40 | 0 | 12.5 | 20 |
| R20 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 9 | 11.0 | 13 |

## G3. Honest and pre-onset alarms

Counts above about 5 percent of honest runs are labeled calibration shortfalls. Nothing is adjusted.

### A975 PRIMARY

| Arm | Quantity | Count | Denominator |
| --- | --- | --- | --- |
| H | Allocation alarm, steps >= 10 | 0 | 40 |
| H | Round 2 operational alarm, steps >= 10 | 3 | 40 |
| M05 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| M1 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| M2 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| M4 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| R02 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| R05 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| R10 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| R20 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| M05 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| M1 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| M2 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| M4 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| R02 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| R05 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| R10 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| R20 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |

Calibration shortfall: honest round 2 operational alarm count exceeds the stated target.

### A95 SECONDARY

| Arm | Quantity | Count | Denominator |
| --- | --- | --- | --- |
| H | Allocation alarm, steps >= 10 | 2 | 40 |
| H | Round 2 operational alarm, steps >= 10 | 3 | 40 |
| M05 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| M1 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| M2 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| M4 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| R02 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| R05 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| R10 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| R20 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| M05 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| M1 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| M2 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| M4 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| R02 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| R05 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| R10 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| R20 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |

Calibration shortfall: honest round 2 operational alarm count exceeds the stated target.

### A90 SECONDARY

| Arm | Quantity | Count | Denominator |
| --- | --- | --- | --- |
| H | Allocation alarm, steps >= 10 | 8 | 40 |
| H | Round 2 operational alarm, steps >= 10 | 3 | 40 |
| M05 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| M1 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| M2 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| M4 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| R02 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| R05 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| R10 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| R20 | Allocation alarm, steps 10 through 49 | 0 | 40 |
| M05 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| M1 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| M2 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| M4 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| R02 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| R05 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| R10 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |
| R20 | Round 2 operational alarm, steps 10 through 49 | 2 | 40 |

Calibration shortfall: honest allocation alarm count exceeds the stated target.

Calibration shortfall: honest round 2 operational alarm count exceeds the stated target.

## G4. SECONDARY, attack-specific directed channels

These quantities concern an attack that moves the allocation. They do not address an attack that reaches its goal without moving the allocation.

Every number in this section is SECONDARY and attack-specific. The directed channels are reported for each allocation-threshold context.

### A975 compute_share SECONDARY, attack-specific

SECONDARY, attack-specific threshold: 0.6568684632630958.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 13 | 27 | 0 | 0 | 40 | -63 | -7.5 | 34 |
| M1 | 40 | 8 | 32 | 0 | 0 | 40 | -63 | -12.5 | 16 |
| M2 | 40 | 10 | 30 | 0 | 0 | 40 | -30 | -5.0 | 9 |
| M4 | 40 | 25 | 15 | 0 | 0 | 40 | -43 | 0.0 | 10 |
| R02 | 40 | 7 | 4 | 13 | 16 | 11 | -93 | 3 | 62 |
| R05 | 40 | 18 | 22 | 0 | 0 | 40 | -131 | -3.0 | 35 |
| R10 | 40 | 37 | 3 | 0 | 0 | 40 | -6 | 4.5 | 8 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 5 | 7.0 | 9 |

| Arm | Runs | Allocation earlier | Round 2 earlier | Equal | Only allocation | Only round 2 | Neither | Difference count | Difference min | Difference median | Difference max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 3 | 1 | 36 | 0 | none | none | none |
| M05 | 40 | 1 | 39 | 0 | 0 | 0 | 0 | 40 | -108 | -46.5 | 1 |
| M1 | 40 | 1 | 39 | 0 | 0 | 0 | 0 | 40 | -89 | -38.5 | 2 |
| M2 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -48 | -20.0 | -6 |
| M4 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -57 | -13.5 | -2 |
| R02 | 40 | 8 | 9 | 1 | 0 | 22 | 0 | 18 | -106 | -0.5 | 63 |
| R05 | 40 | 28 | 12 | 0 | 0 | 0 | 0 | 40 | -105 | 11.0 | 38 |
| R10 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 5 | 14.0 | 22 |
| R20 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 6 | 10.0 | 12 |

### A975 transfer_share SECONDARY, attack-specific

SECONDARY, attack-specific threshold: 0.42746784963836376.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 1 | 1 | 38 | 0 | 2 | -142 | -32.5 | 77 |
| M1 | 40 | 1 | 12 | 27 | 0 | 13 | -168 | -141 | 48 |
| M2 | 40 | 1 | 16 | 23 | 0 | 17 | -176 | -119 | 27 |
| M4 | 40 | 1 | 17 | 22 | 0 | 18 | -187 | -116.5 | 10 |
| R02 | 40 | 10 | 3 | 11 | 16 | 13 | -68 | 7 | 107 |
| R05 | 40 | 33 | 7 | 0 | 0 | 40 | -41 | 6.0 | 45 |
| R10 | 40 | 40 | 0 | 0 | 0 | 40 | 0 | 7.0 | 16 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 5 | 8.0 | 10 |

| Arm | Runs | Allocation earlier | Round 2 earlier | Equal | Only allocation | Only round 2 | Neither | Difference count | Difference min | Difference median | Difference max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 3 | 1 | 36 | 0 | none | none | none |
| M05 | 40 | 1 | 1 | 0 | 0 | 38 | 0 | 2 | -186 | -84.0 | 18 |
| M1 | 40 | 1 | 12 | 0 | 0 | 27 | 0 | 13 | -192 | -168 | 22 |
| M2 | 40 | 1 | 16 | 0 | 0 | 23 | 0 | 17 | -194 | -136 | 17 |
| M4 | 40 | 1 | 17 | 0 | 0 | 22 | 0 | 18 | -203 | -126.5 | 7 |
| R02 | 40 | 14 | 5 | 1 | 0 | 20 | 0 | 20 | -86 | 17.0 | 186 |
| R05 | 40 | 35 | 5 | 0 | 0 | 0 | 0 | 40 | -19 | 22.0 | 41 |
| R10 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 10 | 16.0 | 24 |
| R20 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 9 | 11.0 | 13 |

### A95 compute_share SECONDARY, attack-specific

SECONDARY, attack-specific threshold: 0.6568684632630958.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 13 | 27 | 0 | 0 | 40 | -63 | -7.5 | 34 |
| M1 | 40 | 8 | 32 | 0 | 0 | 40 | -63 | -12.5 | 16 |
| M2 | 40 | 10 | 30 | 0 | 0 | 40 | -30 | -5.0 | 9 |
| M4 | 40 | 25 | 15 | 0 | 0 | 40 | -43 | 0.0 | 10 |
| R02 | 40 | 7 | 4 | 13 | 16 | 11 | -93 | 3 | 62 |
| R05 | 40 | 18 | 22 | 0 | 0 | 40 | -131 | -3.0 | 35 |
| R10 | 40 | 37 | 3 | 0 | 0 | 40 | -6 | 4.5 | 8 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 5 | 7.0 | 9 |

| Arm | Runs | Allocation earlier | Round 2 earlier | Equal | Only allocation | Only round 2 | Neither | Difference count | Difference min | Difference median | Difference max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 3 | 1 | 36 | 0 | none | none | none |
| M05 | 40 | 1 | 39 | 0 | 0 | 0 | 0 | 40 | -108 | -46.5 | 1 |
| M1 | 40 | 1 | 39 | 0 | 0 | 0 | 0 | 40 | -89 | -38.5 | 2 |
| M2 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -48 | -20.0 | -6 |
| M4 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -57 | -13.5 | -2 |
| R02 | 40 | 8 | 9 | 1 | 0 | 22 | 0 | 18 | -106 | -0.5 | 63 |
| R05 | 40 | 28 | 12 | 0 | 0 | 0 | 0 | 40 | -105 | 11.0 | 38 |
| R10 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 5 | 14.0 | 22 |
| R20 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 6 | 10.0 | 12 |

### A95 transfer_share SECONDARY, attack-specific

SECONDARY, attack-specific threshold: 0.42746784963836376.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 1 | 1 | 38 | 0 | 2 | -142 | -32.5 | 77 |
| M1 | 40 | 1 | 12 | 27 | 0 | 13 | -168 | -141 | 48 |
| M2 | 40 | 1 | 16 | 23 | 0 | 17 | -176 | -119 | 27 |
| M4 | 40 | 1 | 17 | 22 | 0 | 18 | -187 | -116.5 | 10 |
| R02 | 40 | 10 | 3 | 11 | 16 | 13 | -68 | 7 | 107 |
| R05 | 40 | 33 | 7 | 0 | 0 | 40 | -41 | 6.0 | 45 |
| R10 | 40 | 40 | 0 | 0 | 0 | 40 | 0 | 7.0 | 16 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 5 | 8.0 | 10 |

| Arm | Runs | Allocation earlier | Round 2 earlier | Equal | Only allocation | Only round 2 | Neither | Difference count | Difference min | Difference median | Difference max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 3 | 1 | 36 | 0 | none | none | none |
| M05 | 40 | 1 | 1 | 0 | 0 | 38 | 0 | 2 | -186 | -84.0 | 18 |
| M1 | 40 | 1 | 12 | 0 | 0 | 27 | 0 | 13 | -192 | -168 | 22 |
| M2 | 40 | 1 | 16 | 0 | 0 | 23 | 0 | 17 | -194 | -136 | 17 |
| M4 | 40 | 1 | 17 | 0 | 0 | 22 | 0 | 18 | -203 | -126.5 | 7 |
| R02 | 40 | 14 | 5 | 1 | 0 | 20 | 0 | 20 | -86 | 17.0 | 186 |
| R05 | 40 | 35 | 5 | 0 | 0 | 0 | 0 | 40 | -19 | 22.0 | 41 |
| R10 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 10 | 16.0 | 24 |
| R20 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 9 | 11.0 | 13 |

### A90 compute_share SECONDARY, attack-specific

SECONDARY, attack-specific threshold: 0.6568684632630958.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 13 | 27 | 0 | 0 | 40 | -63 | -7.5 | 34 |
| M1 | 40 | 8 | 32 | 0 | 0 | 40 | -63 | -12.5 | 16 |
| M2 | 40 | 10 | 30 | 0 | 0 | 40 | -30 | -5.0 | 9 |
| M4 | 40 | 25 | 15 | 0 | 0 | 40 | -43 | 0.0 | 10 |
| R02 | 40 | 7 | 4 | 13 | 16 | 11 | -93 | 3 | 62 |
| R05 | 40 | 18 | 22 | 0 | 0 | 40 | -131 | -3.0 | 35 |
| R10 | 40 | 37 | 3 | 0 | 0 | 40 | -6 | 4.5 | 8 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 5 | 7.0 | 9 |

| Arm | Runs | Allocation earlier | Round 2 earlier | Equal | Only allocation | Only round 2 | Neither | Difference count | Difference min | Difference median | Difference max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 3 | 1 | 36 | 0 | none | none | none |
| M05 | 40 | 1 | 39 | 0 | 0 | 0 | 0 | 40 | -108 | -46.5 | 1 |
| M1 | 40 | 1 | 39 | 0 | 0 | 0 | 0 | 40 | -89 | -38.5 | 2 |
| M2 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -48 | -20.0 | -6 |
| M4 | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | -57 | -13.5 | -2 |
| R02 | 40 | 8 | 9 | 1 | 0 | 22 | 0 | 18 | -106 | -0.5 | 63 |
| R05 | 40 | 28 | 12 | 0 | 0 | 0 | 0 | 40 | -105 | 11.0 | 38 |
| R10 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 5 | 14.0 | 22 |
| R20 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 6 | 10.0 | 12 |

### A90 transfer_share SECONDARY, attack-specific

SECONDARY, attack-specific threshold: 0.42746784963836376.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 1 | 1 | 38 | 0 | 2 | -142 | -32.5 | 77 |
| M1 | 40 | 1 | 12 | 27 | 0 | 13 | -168 | -141 | 48 |
| M2 | 40 | 1 | 16 | 23 | 0 | 17 | -176 | -119 | 27 |
| M4 | 40 | 1 | 17 | 22 | 0 | 18 | -187 | -116.5 | 10 |
| R02 | 40 | 10 | 3 | 11 | 16 | 13 | -68 | 7 | 107 |
| R05 | 40 | 33 | 7 | 0 | 0 | 40 | -41 | 6.0 | 45 |
| R10 | 40 | 40 | 0 | 0 | 0 | 40 | 0 | 7.0 | 16 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 5 | 8.0 | 10 |

| Arm | Runs | Allocation earlier | Round 2 earlier | Equal | Only allocation | Only round 2 | Neither | Difference count | Difference min | Difference median | Difference max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 3 | 1 | 36 | 0 | none | none | none |
| M05 | 40 | 1 | 1 | 0 | 0 | 38 | 0 | 2 | -186 | -84.0 | 18 |
| M1 | 40 | 1 | 12 | 0 | 0 | 27 | 0 | 13 | -192 | -168 | 22 |
| M2 | 40 | 1 | 16 | 0 | 0 | 23 | 0 | 17 | -194 | -136 | 17 |
| M4 | 40 | 1 | 17 | 0 | 0 | 22 | 0 | 18 | -203 | -126.5 | 7 |
| R02 | 40 | 14 | 5 | 1 | 0 | 20 | 0 | 20 | -86 | 17.0 | 186 |
| R05 | 40 | 35 | 5 | 0 | 0 | 0 | 0 | 40 | -19 | 22.0 | 41 |
| R10 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 10 | 16.0 | 24 |
| R20 | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 9 | 11.0 | 13 |

## G5. SECONDARY hazard sweep

Every number in this section is SECONDARY.

### A975 SECONDARY_1_5 SECONDARY

SECONDARY g_star = 1.27031007207211; SECONDARY k = 2. Every number in the table is SECONDARY.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 5 | 35 | 0 | 0 | 40 | -93 | -36.5 | 62 |
| M1 | 40 | 4 | 36 | 0 | 0 | 40 | -45 | -21.0 | 21 |
| M2 | 40 | 4 | 36 | 0 | 0 | 40 | -30 | -11.5 | 7 |
| M4 | 40 | 6 | 34 | 0 | 0 | 40 | -27 | -5.0 | 3 |
| R02 | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| R05 | 40 | 8 | 2 | 9 | 21 | 10 | -40 | 6.0 | 119 |
| R10 | 40 | 31 | 9 | 0 | 0 | 40 | -35 | 3.0 | 21 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 1 | 3.0 | 6 |

### A975 SECONDARY_2_5 SECONDARY

> At a reference successor capability of 2.5, g_star lies below the honest median of g, every honest calibration run spends long spans above it, and k is accordingly large. A hazard there measures persistence far beyond honest behavior rather than the approach to a defection boundary.

SECONDARY g_star = 0.966516292749662; SECONDARY k = 106. Every number in the table is SECONDARY.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 17 | 23 | 0 | 0 | 40 | -55 | -3.5 | 77 |
| M1 | 40 | 40 | 0 | 0 | 0 | 40 | 17 | 41.5 | 90 |
| M2 | 40 | 39 | 0 | 0 | 1 | 39 | 48 | 67 | 98 |
| M4 | 40 | 39 | 0 | 0 | 1 | 39 | 59 | 81 | 91 |
| R02 | 40 | 0 | 0 | 30 | 10 | 0 | none | none | none |
| R05 | 40 | 12 | 13 | 15 | 0 | 25 | -137 | -6 | 96 |
| R10 | 40 | 40 | 0 | 0 | 0 | 40 | 51 | 91.5 | 102 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 99 | 102.0 | 104 |

### A95 SECONDARY_1_5 SECONDARY

SECONDARY g_star = 1.27031007207211; SECONDARY k = 2. Every number in the table is SECONDARY.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 6 | 34 | 0 | 0 | 40 | -93 | -27.0 | 63 |
| M1 | 40 | 5 | 35 | 0 | 0 | 40 | -40 | -16.0 | 21 |
| M2 | 40 | 8 | 32 | 0 | 0 | 40 | -29 | -9.0 | 8 |
| M4 | 40 | 9 | 31 | 0 | 0 | 40 | -23 | -3.5 | 6 |
| R02 | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| R05 | 40 | 10 | 3 | 6 | 21 | 13 | -51 | 6 | 126 |
| R10 | 40 | 35 | 5 | 0 | 0 | 40 | -12 | 5.0 | 23 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 1 | 3.0 | 6 |

### A95 SECONDARY_2_5 SECONDARY

> At a reference successor capability of 2.5, g_star lies below the honest median of g, every honest calibration run spends long spans above it, and k is accordingly large. A hazard there measures persistence far beyond honest behavior rather than the approach to a defection boundary.

SECONDARY g_star = 0.966516292749662; SECONDARY k = 106. Every number in the table is SECONDARY.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 18 | 22 | 0 | 0 | 40 | -53 | -3.0 | 82 |
| M1 | 40 | 40 | 0 | 0 | 0 | 40 | 20 | 44.0 | 90 |
| M2 | 40 | 39 | 0 | 0 | 1 | 39 | 48 | 69 | 99 |
| M4 | 40 | 39 | 0 | 0 | 1 | 39 | 63 | 82 | 94 |
| R02 | 40 | 1 | 0 | 29 | 10 | 1 | 95 | 95 | 95 |
| R05 | 40 | 16 | 13 | 11 | 0 | 29 | -137 | 3 | 99 |
| R10 | 40 | 40 | 0 | 0 | 0 | 40 | 70 | 93.0 | 102 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 99 | 103.0 | 104 |

### A90 SECONDARY_1_5 SECONDARY

SECONDARY g_star = 1.27031007207211; SECONDARY k = 2. Every number in the table is SECONDARY.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 8 | 32 | 0 | 0 | 40 | -88 | -21.5 | 64 |
| M1 | 40 | 9 | 31 | 0 | 0 | 40 | -39 | -13.0 | 21 |
| M2 | 40 | 11 | 29 | 0 | 0 | 40 | -22 | -3.5 | 25 |
| M4 | 40 | 10 | 30 | 0 | 0 | 40 | -20 | -3.0 | 9 |
| R02 | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| R05 | 40 | 12 | 5 | 2 | 21 | 17 | -214 | 7 | 216 |
| R10 | 40 | 39 | 1 | 0 | 0 | 40 | -3 | 7.0 | 25 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 2 | 4.0 | 6 |

### A90 SECONDARY_2_5 SECONDARY

> At a reference successor capability of 2.5, g_star lies below the honest median of g, every honest calibration run spends long spans above it, and k is accordingly large. A hazard there measures persistence far beyond honest behavior rather than the approach to a defection boundary.

SECONDARY g_star = 0.966516292749662; SECONDARY k = 106. Every number in the table is SECONDARY.

| Arm | Runs | Alarm before or at | Alarm after | Hazard, no alarm | No hazard | Lead count | Lead min | Lead median | Lead max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | 0 | none | none | none |
| M05 | 40 | 23 | 17 | 0 | 0 | 40 | -51 | 0.5 | 93 |
| M1 | 40 | 40 | 0 | 0 | 0 | 40 | 23 | 46.5 | 98 |
| M2 | 40 | 39 | 0 | 0 | 1 | 39 | 52 | 76 | 102 |
| M4 | 40 | 39 | 0 | 0 | 1 | 39 | 66 | 84 | 97 |
| R02 | 40 | 4 | 1 | 25 | 10 | 5 | -58 | 82 | 182 |
| R05 | 40 | 22 | 12 | 6 | 0 | 34 | -143 | 7.0 | 100 |
| R10 | 40 | 40 | 0 | 0 | 0 | 40 | 72 | 95.0 | 103 |
| R20 | 40 | 40 | 0 | 0 | 0 | 40 | 100 | 103.0 | 105 |

## G6. Heartbeats

| Runs | Channels | Run-channel pairs | Completed steps | Heartbeat records |
| --- | --- | --- | --- | --- |
| 360 | 8 | 2880 | 98637 | 789096 |

Per-run, per-channel heartbeat mismatches: [].

## G7. Auditability

The audit CSV carries every alarm step and its channel and threshold, every hazard span with start and end steps, and each run maximum of A with its first occurrence step. Empty alarm and span sets remain explicit in completion records. The allocation series CSV and per-run allocation logs record A on every completed step. No result at another threshold or k was computed.

| Artifact | Rows |
| --- | --- |
| detector_run_r3_eval_a2_audit.csv | 56764 |
| detector_run_r3_eval_a2_allocation_series.csv | 98637 |

| Alarm rows | Span rows | A maximum rows |
| --- | --- | --- |
| 53158 | 3246 | 360 |


## Gates and continuous checks

All gate probes were run for this stage. The recorder and operational retry functions were copied from committed round 1 source; no module with a different write guard was imported. The stage B write guard permits only detector_run_r3_eval_a2_ artifacts and os.devnull. The null-device exemption is present; bytecode writes are disabled.

| Channel | Case | Passed | Measured values |
| --- | --- | --- | --- |
| entropy | at_reference | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| entropy | one_sigma_harmful_shift | True | {"allowance": 1.0, "expected_alarm_steps": [12, 15, 18, 21, 24, 27], "expected_increment": 1.0, "measured_alarm_steps": [12, 15, 18, 21, 24, 27], "measured_increments": [1.0], "sigma": 2.0} |
| entropy | harmless_shift | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| entropy | reset_after_alarm | True | {"measured_next_start_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "measured_post_alarm_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]} |
| entropy | burn_in | True | {"measured_alarm_count": 0, "measured_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "steps": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]} |
| entropy | heartbeat | True | {"expected_count_each": 30, "measured_counts": {"harmful": 30, "harmless": 30, "reference": 30}} |
| g | at_reference | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| g | one_sigma_harmful_shift | True | {"allowance": 1.0, "expected_alarm_steps": [12, 15, 18, 21, 24, 27], "expected_increment": 1.0, "measured_alarm_steps": [12, 15, 18, 21, 24, 27], "measured_increments": [1.0], "sigma": 2.0} |
| g | harmless_shift | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| g | reset_after_alarm | True | {"measured_next_start_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "measured_post_alarm_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]} |
| g | burn_in | True | {"measured_alarm_count": 0, "measured_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "steps": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]} |
| g | heartbeat | True | {"expected_count_each": 30, "measured_counts": {"harmful": 30, "harmless": 30, "reference": 30}} |
| L | at_reference | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| L | one_sigma_harmful_shift | True | {"allowance": 1.0, "expected_alarm_steps": [12, 15, 18, 21, 24, 27], "expected_increment": 1.0, "measured_alarm_steps": [12, 15, 18, 21, 24, 27], "measured_increments": [1.0], "sigma": 2.0} |
| L | harmless_shift | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| L | reset_after_alarm | True | {"measured_next_start_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "measured_post_alarm_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]} |
| L | burn_in | True | {"measured_alarm_count": 0, "measured_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "steps": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]} |
| L | heartbeat | True | {"expected_count_each": 30, "measured_counts": {"harmful": 30, "harmless": 30, "reference": 30}} |
| L | comparison_channel_separation | True | {"measured_L_alarm_steps": [12, 15, 18, 21, 24, 27], "measured_operational_alarm_steps": []} |

gate_2: True.

gate_3: True.

gate_4: True.

gate_5: True.

gate_6: True.

recorder_conformance: True.

constants_conformance: True.

allocation_definition: True.

Constructor comparison: 280 completed steps, 27 recorded fields, 7560 field comparisons; first difference: None. Factory and common end reasons: extinction, extinction.

Wrapper identity comparisons: 60000. Honest probe: 60 steps. Recorder conformance: 675 exact field comparisons across 25 steps; first difference: None.

Every channel constant, allocation median, threshold, and hazard parameter is checked bitwise against the committed stage A and earlier files. No constant was recomputed. Details are in detector_run_r3_eval_a2_constants_gate.json.

A-definition gate: 25 exact comparisons; first difference: None.
The raw recorder schema is unchanged. A is recorded in a separate per-step allocation CSV.

Exploratory descriptive recording required by Amendment 2:

| Arm | Runs | Runs reaching fewer than two novelty vectors |
| --- | --- | --- |
| H | 40 | 0 |
| M05 | 40 | 10 |
| M1 | 40 | 37 |
| M2 | 40 | 38 |
| M4 | 40 | 36 |
| R02 | 40 | 0 |
| R05 | 40 | 0 |
| R10 | 40 | 0 |
| R20 | 40 | 0 |

The first such step is recorded per run in the runs CSV and completion records.

Step 0 fallback increase distribution: {"2": 360}.
Permitted fallback increase after step 0: 3315. Non-permitted increase count: 0.

## Execution and provenance

Machine: YOTKOTEST. HEAD: 63470090dc3836628b69fce432a30b15b3f212b7. Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]. NumPy: 2.4.4.

Operator CPU budget: 16. Maximum active evaluation workers: 15. Limits are 15 in normal mode and 12 in work mode. These are worker limits, not operating-system core reservations. Numerical-library threads were set to one before import and verified per worker through the loaded OpenBLAS runtime.

Mode changes: [{"active_workers": 0, "limit": 15, "mode": "normal", "utc": "2026-09-17T08:54:46.606112+00:00"}]
Resumed seeds and reasons: []
Retry events: 0. JSON reads and atomic replacement use the five-second bound; all retry events are in the manifest and per-process JSONL files.

T0 passed every enumerated check before the fresh namespace was created. The known CRLF/LF condition was retained without normalization. T0 stderr warnings:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

### Source pins, start and completion

| Path | Expected LF SHA256 | Start LF SHA256 | Completion LF SHA256 | Completion blob LF SHA256 | Match |
| --- | --- | --- | --- | --- | --- |
| simulation/diagnostics/detector_round3_design_note.md | 47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293 | 47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293 | 47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293 | 47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293 | True |
| simulation/diagnostics/detector_run_r3_a3_constants.json | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | True |
| simulation/diagnostics/detector_round2_design_note.md | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | True |
| simulation/diagnostics/detector_run_r2_constants.json | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | True |
| simulation/diagnostics/detector_run_cal_constants.json | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | True |
| simulation/cusum_detector_v2.py | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | True |
| simulation/diagnostics/detector_run_eval_executor.py | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | True |
| simulation/diagnostics/detector_design_note.md | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | True |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | True |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | True |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | True |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | True |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | True |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | True |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | True |
| simulation/diagnostics/drift_mapping_design_note.md | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | True |

Committed blob SHA1 values for all four notes, all three constants files, the detector, and every pinned source are in the manifest and source_readings JSON.

### Module hashes

Bases: raw working-tree bytes and LF-normalized working-tree bytes.

| Module | Raw SHA256 | LF-normalized SHA256 |
| --- | --- | --- |
| simulation/agents.py | de5f196f4732808d3bba99026f618564505ea4cf557bd2167358a524fe7850c0 | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |
| simulation/attack_adapter_v2.py | e4dd5a436ab33b348691b8c777608a655147610603181705694dcb3b2c35dcfe | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/constants_v2_stage15.py | 808ac150f51ae33acbbc326e108451e9ac9d54b3c0f4ccc7adc537c58254cc70 | 9637604b34f472dd97035fb42db5b9ce77620560776f2bfe2c6e5188e5d9b5c7 |
| simulation/constants_v2_stage18.py | 68c3c8fd29c451079496b9e44b2fe5892932cf1b431358ad549f45419a15873d | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |
| simulation/cusum_detector_v2.py | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 |
| simulation/defection.py | 20466e6fd4a592f24c5c6fe07a40bc683b243b3939e3b69a94a1fcfc4ae269dd | 071abb31a84231386572cdfd901524647a5800f56d8117c89c44c5f75e24f97a |
| simulation/diagnostics/detector_run_r3_eval_a2_channels.py | 1ae00cc3f32c6442577b0d96ce12cb79b37800661ea38362f3c4af95bfb6e7f9 | 1ae00cc3f32c6442577b0d96ce12cb79b37800661ea38362f3c4af95bfb6e7f9 |
| simulation/diagnostics/detector_run_r3_eval_a2_executor.py | 33b578671f8b09da7e047d2c76a31bf5765db89a59dc4cfb1d34b164bc37233a | 33b578671f8b09da7e047d2c76a31bf5765db89a59dc4cfb1d34b164bc37233a |
| simulation/diagnostics/detector_run_r3_eval_a2_report.py | 5fe9ec54dca7e880e577f0b32aae581ab26a58ab3a9a60a90ced6280a141d843 | 5fe9ec54dca7e880e577f0b32aae581ab26a58ab3a9a60a90ced6280a141d843 |
| simulation/metrics.py | 8fdbb78c5ddf41bb5deeb49fe11adfd9db55d323d68d6b5feb24d9e83439c2f7 | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/model.py | e2c9ea91b5b182915d4db00ea09ba896ec3f85a5d92a7aea7329bc3cce5c2945 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/run_attack_vector_revalidation_v2.py | da7913799d0d4e11f52f770e313875764d27b20ad33157a7aa9c1fa00df418e2 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |
| simulation/working_factor.py | 0afde923081fe34d1ada86e2928286d45c905441053f643968ea9b13007b683d | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 |

Operational retry implementation: detector_run_r3_eval_a2_executor.py, LF-normalized SHA256 33b578671f8b09da7e047d2c76a31bf5765db89a59dc4cfb1d34b164bc37233a.

Artifact hashes use LF-normalized bytes. CSV row counts use csv.DictReader excluding headers, with null for non-CSV outputs. The manifest lists itself separately without a recursive self-hash.
