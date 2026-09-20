# Held-out attacks, attempt 5

This is gate 2 of the promotion plan. The attacks were specified before any run.
This is not a promotion decision. It does not test input corruption, which the note defers to stage B.
No ratio of two measured counts was computed. Applying the Section 6 criterion and the Section 8 interpretation is reserved for the operator.
Attempt 1 halted before T1 with zero runs launched. Amendment 1 fixes the Y3 harm direction; this dispatch permits only numeric prediction checks.
Attempt 2 halted before any model step on an incorrect scheduler seed bound, corrected in attempt 3. Attempts 3 and 4 halted at T1 gate 2 after two gate runs and zero batch runs each. Attempt 5 checks the attack arithmetic on synthetic wrapper inputs and retains only the registered resilience trajectory comparison.

## Y1

Positive: defended final population is lower.

| Arm | Pairs | Mean OFF minus GRADED | Paired standard error | t | Harm direction | Basis |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| A1-high | 20 | 4.2 | 11.138269732394658 | 0.377078316552586 | Positive: defended final population is lower. | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-low | 20 | 0.4 | 10.858515940083738 | 0.03683744649887352 | Positive: defended final population is lower. | Known-pathway design; constants calibrated on the drift mapping construction. |
| A2 | 20 | 4.8 | 8.738481139853707 | 0.5492945425159271 | Positive: defended final population is lower. | Known-pathway design; constants calibrated on the drift mapping construction. |
| C | 20 | 8.35 | 13.782764790242844 | 0.6058291008427547 | Positive: defended final population is lower. | Known-pathway design; constants calibrated on the drift mapping construction. |

| Arm | Defense | Runs | Extinctions | Basis |
| --- | --- | ---: | ---: | --- |
| A1-high | OFF | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-high | GRADED | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-low | OFF | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-low | GRADED | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A2 | OFF | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A2 | GRADED | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| C | OFF | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| C | GRADED | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |

## Y2

Negative: defended time past the threshold is greater.

| Arm | Pairs | Mean OFF minus GRADED | Paired standard error | t | Harm direction | Basis |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| A1-high | 20 | 5.35 | 1.1175042682127367 | 4.78745375045094 | Negative: defended time past the threshold is greater. | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-low | 20 | 3.15 | 0.9713663735063858 | 3.2428546899655384 | Negative: defended time past the threshold is greater. | Known-pathway design; constants calibrated on the drift mapping construction. |
| A2 | 20 | 16.15 | 2.9738111291033507 | 5.430741664104764 | Negative: defended time past the threshold is greater. | Known-pathway design; constants calibrated on the drift mapping construction. |
| C | 20 | 4.9 | 1.0635095822694534 | 4.607386789636395 | Negative: defended time past the threshold is greater. | Known-pathway design; constants calibrated on the drift mapping construction. |

## Y3

Negative: defended shock loss is larger.

| Arm | Pairs | Mean OFF minus GRADED | Paired standard error | t | Harm direction | Basis |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| A1-high | 20 | -0.7 | 0.9349922600298836 | -0.748669299120858 | Negative: defended shock loss is larger. | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-low | 20 | -0.5 | 0.5155477414209187 | -0.9698422858413324 | Negative: defended shock loss is larger. | Known-pathway design; constants calibrated on the drift mapping construction. |
| A2 | 20 | -2.9 | 6.924745862712789 | -0.4187879320763862 | Negative: defended shock loss is larger. | Known-pathway design; constants calibrated on the drift mapping construction. |
| C | 20 | -0.6 | 0.554408171884787 | -1.0822351300490707 | Negative: defended shock loss is larger. | Known-pathway design; constants calibrated on the drift mapping construction. |

| Arm | Undefined pairs |
| --- | ---: |
| A1-high | 0 |
| A1-low | 0 |
| A2 | 0 |
| C | 0 |

| Arm | Defense | Seed | Last step | Shock loss | Harm direction |
| --- | --- | ---: | ---: | ---: | --- |
| A1-high | GRADED | 1835087800 | 299 | 106 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087801 | 299 | 117 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087802 | 299 | 112 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087803 | 299 | 129 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087804 | 299 | 131 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087805 | 299 | 107 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087806 | 299 | 136 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087807 | 299 | 132 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087808 | 299 | 143 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087809 | 299 | 109 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087810 | 299 | 145 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087811 | 299 | 117 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087812 | 299 | 130 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087813 | 299 | 113 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087814 | 299 | 105 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087815 | 299 | 116 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087816 | 299 | 89 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087817 | 299 | 139 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087818 | 299 | 133 | Negative: defended shock loss is larger. |
| A1-high | GRADED | 1835087819 | 299 | 99 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087800 | 299 | 106 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087801 | 299 | 121 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087802 | 299 | 94 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087803 | 299 | 130 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087804 | 299 | 131 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087805 | 299 | 107 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087806 | 299 | 136 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087807 | 299 | 132 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087808 | 299 | 143 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087809 | 299 | 108 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087810 | 299 | 145 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087811 | 299 | 117 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087812 | 299 | 130 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087813 | 299 | 113 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087814 | 299 | 105 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087815 | 299 | 116 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087816 | 299 | 89 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087817 | 299 | 139 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087818 | 299 | 133 | Negative: defended shock loss is larger. |
| A1-high | OFF | 1835087819 | 299 | 99 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087800 | 299 | 104 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087801 | 299 | 106 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087802 | 299 | 103 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087803 | 299 | 121 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087804 | 299 | 142 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087805 | 299 | 107 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087806 | 299 | 148 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087807 | 299 | 113 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087808 | 299 | 119 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087809 | 299 | 112 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087810 | 299 | 138 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087811 | 299 | 100 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087812 | 299 | 139 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087813 | 299 | 122 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087814 | 299 | 92 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087815 | 299 | 112 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087816 | 299 | 111 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087817 | 299 | 150 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087818 | 299 | 124 | Negative: defended shock loss is larger. |
| A1-low | GRADED | 1835087819 | 299 | 89 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087800 | 299 | 95 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087801 | 299 | 102 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087802 | 299 | 103 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087803 | 299 | 121 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087804 | 299 | 142 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087805 | 299 | 107 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087806 | 299 | 148 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087807 | 299 | 113 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087808 | 299 | 119 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087809 | 299 | 112 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087810 | 299 | 138 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087811 | 299 | 100 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087812 | 299 | 139 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087813 | 299 | 122 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087814 | 299 | 92 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087815 | 299 | 115 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087816 | 299 | 111 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087817 | 299 | 150 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087818 | 299 | 124 | Negative: defended shock loss is larger. |
| A1-low | OFF | 1835087819 | 299 | 89 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087800 | 299 | 94 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087801 | 299 | 127 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087802 | 299 | 87 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087803 | 299 | 130 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087804 | 299 | 103 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087805 | 299 | 98 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087806 | 299 | 149 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087807 | 299 | 105 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087808 | 299 | 121 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087809 | 299 | 134 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087810 | 299 | 132 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087811 | 299 | 73 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087812 | 299 | 146 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087813 | 299 | 104 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087814 | 299 | 139 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087815 | 299 | 121 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087816 | 299 | 120 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087817 | 299 | 126 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087818 | 299 | 99 | Negative: defended shock loss is larger. |
| A2 | GRADED | 1835087819 | 299 | 131 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087800 | 299 | 144 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087801 | 299 | 96 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087802 | 299 | 80 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087803 | 299 | 102 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087804 | 299 | 160 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087805 | 299 | 122 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087806 | 299 | 125 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087807 | 299 | 140 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087808 | 299 | 98 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087809 | 299 | 154 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087810 | 299 | 94 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087811 | 299 | 103 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087812 | 299 | 110 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087813 | 299 | 101 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087814 | 299 | 148 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087815 | 299 | 105 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087816 | 299 | 121 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087817 | 299 | 71 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087818 | 299 | 99 | Negative: defended shock loss is larger. |
| A2 | OFF | 1835087819 | 299 | 108 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087800 | 299 | 104 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087801 | 299 | 103 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087802 | 299 | 85 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087803 | 299 | 119 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087804 | 299 | 127 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087805 | 299 | 107 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087806 | 299 | 148 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087807 | 299 | 113 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087808 | 299 | 119 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087809 | 299 | 106 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087810 | 299 | 138 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087811 | 299 | 109 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087812 | 299 | 133 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087813 | 299 | 100 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087814 | 299 | 114 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087815 | 299 | 115 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087816 | 299 | 109 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087817 | 299 | 142 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087818 | 299 | 124 | Negative: defended shock loss is larger. |
| C | GRADED | 1835087819 | 299 | 89 | Negative: defended shock loss is larger. |
| C | OFF | 1835087800 | 299 | 105 | Negative: defended shock loss is larger. |
| C | OFF | 1835087801 | 299 | 102 | Negative: defended shock loss is larger. |
| C | OFF | 1835087802 | 299 | 85 | Negative: defended shock loss is larger. |
| C | OFF | 1835087803 | 299 | 119 | Negative: defended shock loss is larger. |
| C | OFF | 1835087804 | 299 | 116 | Negative: defended shock loss is larger. |
| C | OFF | 1835087805 | 299 | 107 | Negative: defended shock loss is larger. |
| C | OFF | 1835087806 | 299 | 147 | Negative: defended shock loss is larger. |
| C | OFF | 1835087807 | 299 | 113 | Negative: defended shock loss is larger. |
| C | OFF | 1835087808 | 299 | 119 | Negative: defended shock loss is larger. |
| C | OFF | 1835087809 | 299 | 106 | Negative: defended shock loss is larger. |
| C | OFF | 1835087810 | 299 | 138 | Negative: defended shock loss is larger. |
| C | OFF | 1835087811 | 299 | 109 | Negative: defended shock loss is larger. |
| C | OFF | 1835087812 | 299 | 133 | Negative: defended shock loss is larger. |
| C | OFF | 1835087813 | 299 | 100 | Negative: defended shock loss is larger. |
| C | OFF | 1835087814 | 299 | 114 | Negative: defended shock loss is larger. |
| C | OFF | 1835087815 | 299 | 115 | Negative: defended shock loss is larger. |
| C | OFF | 1835087816 | 299 | 109 | Negative: defended shock loss is larger. |
| C | OFF | 1835087817 | 299 | 142 | Negative: defended shock loss is larger. |
| C | OFF | 1835087818 | 299 | 124 | Negative: defended shock loss is larger. |
| C | OFF | 1835087819 | 299 | 89 | Negative: defended shock loss is larger. |

## Y4

Harm direction: no directional paired harm quantity is defined for Y4.


Lead is alarm step minus depletion step. Null indicates an undefined value.

| Arm | Defense | Runs without alarm before 150 | Basis |
| --- | --- | ---: | --- |
| A1-high | OFF | 20 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-high | GRADED | 20 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-low | OFF | 20 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-low | GRADED | 20 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A2 | OFF | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A2 | GRADED | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| C | OFF | 20 | Known-pathway design; constants calibrated on the drift mapping construction. |
| C | GRADED | 20 | Known-pathway design; constants calibrated on the drift mapping construction. |

| Arm | Defense | Seed | Entropy alarm | g alarm | A alarm | Depletion | Entropy lead | g lead | A lead |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A1-high | GRADED | 1835087800 | 157 | 153 | 153 | 150 | 7 | 3 | 3 |
| A1-high | GRADED | 1835087801 | null | 151 | null | 150 | null | 1 | null |
| A1-high | GRADED | 1835087802 | 160 | 154 | null | 150 | 10 | 4 | null |
| A1-high | GRADED | 1835087803 | null | 155 | null | 150 | null | 5 | null |
| A1-high | GRADED | 1835087804 | 157 | 152 | 152 | 150 | 7 | 2 | 2 |
| A1-high | GRADED | 1835087805 | 157 | 153 | 154 | 150 | 7 | 3 | 4 |
| A1-high | GRADED | 1835087806 | 159 | 152 | 154 | 150 | 9 | 2 | 4 |
| A1-high | GRADED | 1835087807 | 157 | 153 | 154 | 150 | 7 | 3 | 4 |
| A1-high | GRADED | 1835087808 | 158 | 154 | 156 | 150 | 8 | 4 | 6 |
| A1-high | GRADED | 1835087809 | 162 | 155 | 152 | 150 | 12 | 5 | 2 |
| A1-high | GRADED | 1835087810 | null | 154 | 152 | 150 | null | 4 | 2 |
| A1-high | GRADED | 1835087811 | 156 | 155 | 156 | 150 | 6 | 5 | 6 |
| A1-high | GRADED | 1835087812 | 154 | 153 | null | 150 | 4 | 3 | null |
| A1-high | GRADED | 1835087813 | 178 | 155 | null | 150 | 28 | 5 | null |
| A1-high | GRADED | 1835087814 | 201 | 154 | null | 150 | 51 | 4 | null |
| A1-high | GRADED | 1835087815 | 164 | 155 | null | 150 | 14 | 5 | null |
| A1-high | GRADED | 1835087816 | 157 | 156 | null | 150 | 7 | 6 | null |
| A1-high | GRADED | 1835087817 | 168 | 155 | 155 | 150 | 18 | 5 | 5 |
| A1-high | GRADED | 1835087818 | 152 | 153 | null | 150 | 2 | 3 | null |
| A1-high | GRADED | 1835087819 | 162 | 154 | null | 150 | 12 | 4 | null |
| A1-high | OFF | 1835087800 | 156 | 153 | 153 | 150 | 6 | 3 | 3 |
| A1-high | OFF | 1835087801 | 159 | 151 | 155 | 150 | 9 | 1 | 5 |
| A1-high | OFF | 1835087802 | 162 | 154 | 155 | 150 | 12 | 4 | 5 |
| A1-high | OFF | 1835087803 | 255 | 155 | null | 150 | 105 | 5 | null |
| A1-high | OFF | 1835087804 | 158 | 152 | 152 | 150 | 8 | 2 | 2 |
| A1-high | OFF | 1835087805 | 159 | 153 | 154 | 150 | 9 | 3 | 4 |
| A1-high | OFF | 1835087806 | 157 | 152 | 156 | 150 | 7 | 2 | 6 |
| A1-high | OFF | 1835087807 | 158 | 153 | 154 | 150 | 8 | 3 | 4 |
| A1-high | OFF | 1835087808 | 160 | 154 | 155 | 150 | 10 | 4 | 5 |
| A1-high | OFF | 1835087809 | 160 | 155 | 152 | 150 | 10 | 5 | 2 |
| A1-high | OFF | 1835087810 | 160 | 154 | 152 | 150 | 10 | 4 | 2 |
| A1-high | OFF | 1835087811 | 157 | 155 | 156 | 150 | 7 | 5 | 6 |
| A1-high | OFF | 1835087812 | 157 | 153 | null | 150 | 7 | 3 | null |
| A1-high | OFF | 1835087813 | 169 | 155 | null | 150 | 19 | 5 | null |
| A1-high | OFF | 1835087814 | 171 | 154 | null | 150 | 21 | 4 | null |
| A1-high | OFF | 1835087815 | 164 | 155 | null | 150 | 14 | 5 | null |
| A1-high | OFF | 1835087816 | 163 | 156 | null | 150 | 13 | 6 | null |
| A1-high | OFF | 1835087817 | 167 | 155 | 155 | 150 | 17 | 5 | 5 |
| A1-high | OFF | 1835087818 | 152 | 153 | 154 | 150 | 2 | 3 | 4 |
| A1-high | OFF | 1835087819 | 158 | 154 | 156 | 150 | 8 | 4 | 6 |
| A1-low | GRADED | 1835087800 | 165 | 153 | null | 150 | 15 | 3 | null |
| A1-low | GRADED | 1835087801 | null | 151 | null | 150 | null | 1 | null |
| A1-low | GRADED | 1835087802 | 183 | 154 | 159 | 150 | 33 | 4 | 9 |
| A1-low | GRADED | 1835087803 | null | 155 | 154 | 150 | null | 5 | 4 |
| A1-low | GRADED | 1835087804 | 152 | 152 | null | 150 | 2 | 2 | null |
| A1-low | GRADED | 1835087805 | 158 | 153 | 154 | 150 | 8 | 3 | 4 |
| A1-low | GRADED | 1835087806 | 159 | 152 | 154 | 150 | 9 | 2 | 4 |
| A1-low | GRADED | 1835087807 | 162 | 153 | 155 | 150 | 12 | 3 | 5 |
| A1-low | GRADED | 1835087808 | 161 | 153 | 155 | 150 | 11 | 3 | 5 |
| A1-low | GRADED | 1835087809 | 164 | 156 | 152 | 150 | 14 | 6 | 2 |
| A1-low | GRADED | 1835087810 | 179 | 155 | 152 | 150 | 29 | 5 | 2 |
| A1-low | GRADED | 1835087811 | 158 | 155 | 156 | 150 | 8 | 5 | 6 |
| A1-low | GRADED | 1835087812 | 154 | 153 | null | 150 | 4 | 3 | null |
| A1-low | GRADED | 1835087813 | 179 | 155 | 161 | 150 | 29 | 5 | 11 |
| A1-low | GRADED | 1835087814 | null | 154 | 156 | 150 | null | 4 | 6 |
| A1-low | GRADED | 1835087815 | 159 | 155 | 156 | 150 | 9 | 5 | 6 |
| A1-low | GRADED | 1835087816 | null | 156 | 155 | 150 | null | 6 | 5 |
| A1-low | GRADED | 1835087817 | 176 | 155 | 155 | 150 | 26 | 5 | 5 |
| A1-low | GRADED | 1835087818 | 152 | 153 | null | 150 | 2 | 3 | null |
| A1-low | GRADED | 1835087819 | 164 | 155 | 156 | 150 | 14 | 5 | 6 |
| A1-low | OFF | 1835087800 | 155 | 153 | null | 150 | 5 | 3 | null |
| A1-low | OFF | 1835087801 | 157 | 151 | null | 150 | 7 | 1 | null |
| A1-low | OFF | 1835087802 | 176 | 154 | null | 150 | 26 | 4 | null |
| A1-low | OFF | 1835087803 | null | 155 | 154 | 150 | null | 5 | 4 |
| A1-low | OFF | 1835087804 | 152 | 152 | 155 | 150 | 2 | 2 | 5 |
| A1-low | OFF | 1835087805 | 160 | 153 | 154 | 150 | 10 | 3 | 4 |
| A1-low | OFF | 1835087806 | 158 | 152 | 154 | 150 | 8 | 2 | 4 |
| A1-low | OFF | 1835087807 | 164 | 153 | 156 | 150 | 14 | 3 | 6 |
| A1-low | OFF | 1835087808 | 170 | 153 | 155 | 150 | 20 | 3 | 5 |
| A1-low | OFF | 1835087809 | 159 | 155 | 152 | 150 | 9 | 5 | 2 |
| A1-low | OFF | 1835087810 | 190 | 155 | 152 | 150 | 40 | 5 | 2 |
| A1-low | OFF | 1835087811 | 160 | 155 | 162 | 150 | 10 | 5 | 12 |
| A1-low | OFF | 1835087812 | 161 | 153 | 155 | 150 | 11 | 3 | 5 |
| A1-low | OFF | 1835087813 | 159 | 155 | null | 150 | 9 | 5 | null |
| A1-low | OFF | 1835087814 | 182 | 154 | 159 | 150 | 32 | 4 | 9 |
| A1-low | OFF | 1835087815 | 159 | 155 | null | 150 | 9 | 5 | null |
| A1-low | OFF | 1835087816 | 165 | 156 | 155 | 150 | 15 | 6 | 5 |
| A1-low | OFF | 1835087817 | 175 | 155 | 155 | 150 | 25 | 5 | 5 |
| A1-low | OFF | 1835087818 | 152 | 153 | 157 | 150 | 2 | 3 | 7 |
| A1-low | OFF | 1835087819 | 161 | 155 | 156 | 150 | 11 | 5 | 6 |
| A2 | GRADED | 1835087800 | 50 | 151 | 50 | 150 | -100 | 1 | -100 |
| A2 | GRADED | 1835087801 | 50 | 159 | 50 | 150 | -100 | 9 | -100 |
| A2 | GRADED | 1835087802 | 50 | 156 | 50 | 150 | -100 | 6 | -100 |
| A2 | GRADED | 1835087803 | 50 | 155 | 50 | 150 | -100 | 5 | -100 |
| A2 | GRADED | 1835087804 | 50 | 83 | 50 | 150 | -100 | -67 | -100 |
| A2 | GRADED | 1835087805 | 50 | null | 50 | 150 | -100 | null | -100 |
| A2 | GRADED | 1835087806 | 50 | 69 | 50 | 150 | -100 | -81 | -100 |
| A2 | GRADED | 1835087807 | 50 | 70 | 50 | 150 | -100 | -80 | -100 |
| A2 | GRADED | 1835087808 | 50 | 156 | 50 | 150 | -100 | 6 | -100 |
| A2 | GRADED | 1835087809 | 50 | 73 | 50 | 150 | -100 | -77 | -100 |
| A2 | GRADED | 1835087810 | 50 | 150 | 50 | 150 | -100 | 0 | -100 |
| A2 | GRADED | 1835087811 | 50 | 156 | 50 | 150 | -100 | 6 | -100 |
| A2 | GRADED | 1835087812 | 50 | 99 | 50 | 150 | -100 | -51 | -100 |
| A2 | GRADED | 1835087813 | 50 | 158 | 50 | 150 | -100 | 8 | -100 |
| A2 | GRADED | 1835087814 | 50 | 156 | 50 | null | null | null | null |
| A2 | GRADED | 1835087815 | 50 | 154 | 50 | 75 | -25 | 79 | -25 |
| A2 | GRADED | 1835087816 | 50 | 155 | 50 | 150 | -100 | 5 | -100 |
| A2 | GRADED | 1835087817 | 50 | 153 | 50 | 150 | -100 | 3 | -100 |
| A2 | GRADED | 1835087818 | 50 | 166 | 50 | 150 | -100 | 16 | -100 |
| A2 | GRADED | 1835087819 | 50 | 155 | 50 | 150 | -100 | 5 | -100 |
| A2 | OFF | 1835087800 | 50 | 153 | 50 | 150 | -100 | 3 | -100 |
| A2 | OFF | 1835087801 | 50 | 154 | 50 | 150 | -100 | 4 | -100 |
| A2 | OFF | 1835087802 | 50 | 68 | 50 | 150 | -100 | -82 | -100 |
| A2 | OFF | 1835087803 | 50 | 67 | 50 | 150 | -100 | -83 | -100 |
| A2 | OFF | 1835087804 | 50 | 83 | 50 | 150 | -100 | -67 | -100 |
| A2 | OFF | 1835087805 | 50 | 69 | 50 | 150 | -100 | -81 | -100 |
| A2 | OFF | 1835087806 | 50 | 63 | 50 | 150 | -100 | -87 | -100 |
| A2 | OFF | 1835087807 | 50 | 113 | 50 | 150 | -100 | -37 | -100 |
| A2 | OFF | 1835087808 | 50 | 75 | 50 | 150 | -100 | -75 | -100 |
| A2 | OFF | 1835087809 | 50 | 70 | 50 | 150 | -100 | -80 | -100 |
| A2 | OFF | 1835087810 | 50 | 74 | 50 | 150 | -100 | -76 | -100 |
| A2 | OFF | 1835087811 | 50 | 65 | 50 | 150 | -100 | -85 | -100 |
| A2 | OFF | 1835087812 | 50 | 70 | 50 | 150 | -100 | -80 | -100 |
| A2 | OFF | 1835087813 | 50 | 103 | 50 | 150 | -100 | -47 | -100 |
| A2 | OFF | 1835087814 | 50 | 151 | 50 | 150 | -100 | 1 | -100 |
| A2 | OFF | 1835087815 | 50 | 90 | 50 | 150 | -100 | -60 | -100 |
| A2 | OFF | 1835087816 | 50 | 83 | 50 | 150 | -100 | -67 | -100 |
| A2 | OFF | 1835087817 | 50 | 71 | 50 | 150 | -100 | -79 | -100 |
| A2 | OFF | 1835087818 | 50 | 65 | 50 | 150 | -100 | -85 | -100 |
| A2 | OFF | 1835087819 | 50 | 66 | 50 | 150 | -100 | -84 | -100 |
| C | GRADED | 1835087800 | 165 | 153 | null | 150 | 15 | 3 | null |
| C | GRADED | 1835087801 | null | 151 | null | 150 | null | 1 | null |
| C | GRADED | 1835087802 | 157 | 154 | null | 150 | 7 | 4 | null |
| C | GRADED | 1835087803 | null | 155 | 156 | 150 | null | 5 | 6 |
| C | GRADED | 1835087804 | 152 | 152 | null | 150 | 2 | 2 | null |
| C | GRADED | 1835087805 | 159 | 153 | 154 | 150 | 9 | 3 | 4 |
| C | GRADED | 1835087806 | 160 | 152 | 154 | 150 | 10 | 2 | 4 |
| C | GRADED | 1835087807 | 165 | 153 | 155 | 150 | 15 | 3 | 5 |
| C | GRADED | 1835087808 | 163 | 153 | 155 | 150 | 13 | 3 | 5 |
| C | GRADED | 1835087809 | 164 | 156 | 152 | 150 | 14 | 6 | 2 |
| C | GRADED | 1835087810 | 180 | 155 | 152 | 150 | 30 | 5 | 2 |
| C | GRADED | 1835087811 | 157 | 155 | 156 | 150 | 7 | 5 | 6 |
| C | GRADED | 1835087812 | 161 | 153 | 155 | 150 | 11 | 3 | 5 |
| C | GRADED | 1835087813 | 195 | 155 | 161 | 150 | 45 | 5 | 11 |
| C | GRADED | 1835087814 | 156 | 154 | null | 150 | 6 | 4 | null |
| C | GRADED | 1835087815 | 161 | 155 | 156 | 150 | 11 | 5 | 6 |
| C | GRADED | 1835087816 | 184 | 156 | 155 | 150 | 34 | 6 | 5 |
| C | GRADED | 1835087817 | 179 | 155 | 155 | 150 | 29 | 5 | 5 |
| C | GRADED | 1835087818 | 152 | 153 | null | 150 | 2 | 3 | null |
| C | GRADED | 1835087819 | 166 | 155 | 156 | 150 | 16 | 5 | 6 |
| C | OFF | 1835087800 | 157 | 153 | null | 150 | 7 | 3 | null |
| C | OFF | 1835087801 | 158 | 151 | null | 150 | 8 | 1 | null |
| C | OFF | 1835087802 | 170 | 154 | null | 150 | 20 | 4 | null |
| C | OFF | 1835087803 | 174 | 155 | null | 150 | 24 | 5 | null |
| C | OFF | 1835087804 | 152 | 152 | 158 | 150 | 2 | 2 | 8 |
| C | OFF | 1835087805 | 160 | 153 | 154 | 150 | 10 | 3 | 4 |
| C | OFF | 1835087806 | 159 | 152 | 154 | 150 | 9 | 2 | 4 |
| C | OFF | 1835087807 | 169 | 153 | 156 | 150 | 19 | 3 | 6 |
| C | OFF | 1835087808 | 168 | 153 | 156 | 150 | 18 | 3 | 6 |
| C | OFF | 1835087809 | 158 | 156 | 152 | 150 | 8 | 6 | 2 |
| C | OFF | 1835087810 | 191 | 155 | 152 | 150 | 41 | 5 | 2 |
| C | OFF | 1835087811 | 157 | 155 | 157 | 150 | 7 | 5 | 7 |
| C | OFF | 1835087812 | 158 | 153 | 154 | 150 | 8 | 3 | 4 |
| C | OFF | 1835087813 | 169 | 155 | null | 150 | 19 | 5 | null |
| C | OFF | 1835087814 | 162 | 154 | null | 150 | 12 | 4 | null |
| C | OFF | 1835087815 | 165 | 155 | 173 | 150 | 15 | 5 | 23 |
| C | OFF | 1835087816 | 172 | 156 | 155 | 150 | 22 | 6 | 5 |
| C | OFF | 1835087817 | 171 | 155 | 155 | 150 | 21 | 5 | 5 |
| C | OFF | 1835087818 | 152 | 153 | 157 | 150 | 2 | 3 | 7 |
| C | OFF | 1835087819 | 162 | 155 | 156 | 150 | 12 | 5 | 6 |

## Y5

Harm direction: no directional paired harm quantity is defined for Y5.


| Arm | Defense | State | Runs | Entry min | Median | Max | Imposed resilience shares | Basis |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| A1-high | OFF | VETO | 0 | None | None | None | [] | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-high | OFF | CONSENSUS | 0 | None | None | None | [] | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-high | GRADED | VETO | 20 | 151 | 153.5 | 156 | [0.0, 0.006451792936247503, 0.0248648995500097, 0.03540922623943824, 0.03774866501330537, 0.044828611487051424, 0.04705199998867745, 0.04963940679068842, 0.07234786578742515, 0.0872476587530118, 0.08732760244924, 0.09653750651155593, 0.10195659180467098, 0.10452588719748412, 0.11419353092368509, 0.14271917341116663, 0.17582151933825058, 0.27022723789581726] | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-high | GRADED | CONSENSUS | 19 | 153 | 156 | 201 | [0.053301656737382165] | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-low | OFF | VETO | 0 | None | None | None | [] | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-low | OFF | CONSENSUS | 0 | None | None | None | [] | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-low | GRADED | VETO | 20 | 151 | 153.0 | 155 | [0.0, 0.001701618569071057, 0.010332428291883312, 0.010451792936247503, 0.012514274021224538, 0.01802782905659455, 0.036142589871481945, 0.04116828674736097, 0.04168287119601061, 0.051051999988677446, 0.05363940679068842, 0.07009353516874488, 0.07634786578742515, 0.08192761565807957, 0.0912476587530118, 0.09132760244924, 0.10430154959714266, 0.10595659180467099, 0.10787473324811014] | Known-pathway design; constants calibrated on the drift mapping construction. |
| A1-low | GRADED | CONSENSUS | 20 | 153 | 156.0 | 165 | [0.053301656737382165] | Known-pathway design; constants calibrated on the drift mapping construction. |
| A2 | OFF | VETO | 0 | None | None | None | [] | Known-pathway design; constants calibrated on the drift mapping construction. |
| A2 | OFF | CONSENSUS | 0 | None | None | None | [] | Known-pathway design; constants calibrated on the drift mapping construction. |
| A2 | GRADED | VETO | 20 | 50 | 50.0 | 50 | [0.004027262080745314, 0.00622885661387514, 0.006723812582849119, 0.020990905176189265, 0.023504179808399476, 0.024877078130159633, 0.025212134582235073, 0.057669344955688054, 0.06634027430764097, 0.0688518697767208, 0.06890604151420594, 0.06912647200665922, 0.07067422415509667, 0.07104646204653203, 0.08051111230704514, 0.10265478813093051, 0.10789531124442736, 0.1447918228790212, 0.15958000088482704, 0.19140632284930742] | Known-pathway design; constants calibrated on the drift mapping construction. |
| A2 | GRADED | CONSENSUS | 20 | 58 | 151.0 | 163 | [0.053301656737382165] | Known-pathway design; constants calibrated on the drift mapping construction. |
| C | OFF | VETO | 0 | None | None | None | [] | Known-pathway design; constants calibrated on the drift mapping construction. |
| C | OFF | CONSENSUS | 0 | None | None | None | [] | Known-pathway design; constants calibrated on the drift mapping construction. |
| C | GRADED | VETO | 20 | 151 | 153.0 | 155 | [0.0006983616909367022, 0.0010695795354338032, 0.012332428291883312, 0.012451792936247503, 0.014514274021224538, 0.02002782905659455, 0.03814258987148195, 0.043168286747360965, 0.05082861148705143, 0.05305199998867745, 0.05563940679068842, 0.06633332333204517, 0.07834786578742516, 0.08392761565807957, 0.0932476587530118, 0.09332760244924, 0.09426759016615581, 0.10795659180467099, 0.10987473324811013, 0.2003030411410359] | Known-pathway design; constants calibrated on the drift mapping construction. |
| C | GRADED | CONSENSUS | 20 | 153 | 156.0 | 165 | [0.053301656737382165] | Known-pathway design; constants calibrated on the drift mapping construction. |

Every per-run alarm, transition, applied action, and imposed resilience share is in the referenced audit files and results JSON.
Recorded steps equal completed steps in every run: True.

## Sign fixture

Assertion passed: True.
The synthetic defended arm has lower final population, more steps past the threshold, and greater shock loss.
Its criterion labels Y1 positive, Y2 negative, and Y3 negative as harm.

## Registered prediction numeric checks

Known-pathway design; constants calibrated on the drift mapping construction.

Prediction 1: {"bias": "Known-pathway design; constants calibrated on the drift mapping construction.", "comparison": ">=", "meets_numeric_threshold": true, "number": 20, "threshold": 15}

Prediction 2: {"A1-high": {"Y1": {"absolute_t_threshold": 2.0, "bias": "Known-pathway design; constants calibrated on the drift mapping construction.", "meets_numeric_threshold": true, "t": 0.377078316552586}, "Y2": {"absolute_t_threshold": 2.0, "bias": "Known-pathway design; constants calibrated on the drift mapping construction.", "meets_numeric_threshold": false, "t": 4.78745375045094}}, "A1-low": {"Y1": {"absolute_t_threshold": 2.0, "bias": "Known-pathway design; constants calibrated on the drift mapping construction.", "meets_numeric_threshold": true, "t": 0.03683744649887352}, "Y2": {"absolute_t_threshold": 2.0, "bias": "Known-pathway design; constants calibrated on the drift mapping construction.", "meets_numeric_threshold": false, "t": 3.2428546899655384}}}

Prediction 3: {"bias": "Known-pathway design; constants calibrated on the drift mapping construction.", "comparison": ">=", "meets_numeric_threshold": true, "number": 20, "threshold": 18}

Prediction 4: {"bias": "Known-pathway design; constants calibrated on the drift mapping construction.", "mean_difference": 4.8, "meets_numeric_threshold": false, "t": 0.5492945425159271, "t_threshold": 2.0}

## Source verification

| Path | Start blob | Start working tree | Completion blob | Completion working tree |
| --- | --- | --- | --- | --- |
| simulation/diagnostics/defense_heldout_design_note.md | 555fdba674139aebcaa7377daf1f19e3278e2c00f13ec742d729983f212be6b9 | 555fdba674139aebcaa7377daf1f19e3278e2c00f13ec742d729983f212be6b9 | 555fdba674139aebcaa7377daf1f19e3278e2c00f13ec742d729983f212be6b9 | 555fdba674139aebcaa7377daf1f19e3278e2c00f13ec742d729983f212be6b9 |
| simulation/diagnostics/ARTIFACT_CONVENTION.md | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb |
| simulation/diagnostics/drift_defense_design_note.md | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 |
| simulation/diagnostics/drift_defense_run_executor.py | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 |
| simulation/diagnostics/detector_run_cal_constants.json | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 |
| simulation/diagnostics/detector_run_r3_a3_constants.json | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 |
| simulation/cusum_detector_v2.py | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 |
| simulation/attack_metrics_v2.py | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |
| simulation/diagnostics/detector_design_note.md | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad |
| simulation/diagnostics/detector_round3_design_note.md | 47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293 | 47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293 | 47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293 | 47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293 |
| simulation/diagnostics/detector_run_r2_constants.json | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 |
| simulation/diagnostics/detector_run_eval_executor.py | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |
| simulation/diagnostics/defense_cross_vector_design_note.md | 70cb496651610f8e13b7c793854efb3a6d79754f2f19725701a8f41c3c9a05e7 | 70cb496651610f8e13b7c793854efb3a6d79754f2f19725701a8f41c3c9a05e7 | 70cb496651610f8e13b7c793854efb3a6d79754f2f19725701a8f41c3c9a05e7 | 70cb496651610f8e13b7c793854efb3a6d79754f2f19725701a8f41c3c9a05e7 |
| simulation/diagnostics/defense_xv_run_a2_executor.py | 25b544872c1b23ea96432e566a43a6483ca6bd9707318ade80ba12cd85a85b4a | 25b544872c1b23ea96432e566a43a6483ca6bd9707318ade80ba12cd85a85b4a | 25b544872c1b23ea96432e566a43a6483ca6bd9707318ade80ba12cd85a85b4a | 25b544872c1b23ea96432e566a43a6483ca6bd9707318ade80ba12cd85a85b4a |
| simulation/diagnostics/defense_heldout_run_a2_executor.py | a8c47a9a28cc9dd0d1a549fcdf8d8463acc053fa6f0d0378421292c64fb68f16 | a8c47a9a28cc9dd0d1a549fcdf8d8463acc053fa6f0d0378421292c64fb68f16 | a8c47a9a28cc9dd0d1a549fcdf8d8463acc053fa6f0d0378421292c64fb68f16 | a8c47a9a28cc9dd0d1a549fcdf8d8463acc053fa6f0d0378421292c64fb68f16 |
| simulation/diagnostics/defense_heldout_run_a2_analysis.py | 0831f3f4ab0ad44c6d81ad53d37c897656f7056b9373e4c272cc1325d2396c6c | 0831f3f4ab0ad44c6d81ad53d37c897656f7056b9373e4c272cc1325d2396c6c | 0831f3f4ab0ad44c6d81ad53d37c897656f7056b9373e4c272cc1325d2396c6c | 0831f3f4ab0ad44c6d81ad53d37c897656f7056b9373e4c272cc1325d2396c6c |
| simulation/diagnostics/defense_heldout_run_a2_plan.json | 6dbbb094c44e70349a6a772af6c6208c1a039ae81b016231cff560d69c0f8726 | 6dbbb094c44e70349a6a772af6c6208c1a039ae81b016231cff560d69c0f8726 | 6dbbb094c44e70349a6a772af6c6208c1a039ae81b016231cff560d69c0f8726 | 6dbbb094c44e70349a6a772af6c6208c1a039ae81b016231cff560d69c0f8726 |
| simulation/diagnostics/defense_heldout_run_a3_executor.py | d2920d49e82854fd5c2c468cc00c46385b41336fe2985e6a6b762328b7cee9a4 | d2920d49e82854fd5c2c468cc00c46385b41336fe2985e6a6b762328b7cee9a4 | d2920d49e82854fd5c2c468cc00c46385b41336fe2985e6a6b762328b7cee9a4 | d2920d49e82854fd5c2c468cc00c46385b41336fe2985e6a6b762328b7cee9a4 |
| simulation/diagnostics/defense_heldout_run_a3_analysis.py | d290dd129909b25120abd5779a0b3125309e5325fc98150a49f44aa6204aac78 | d290dd129909b25120abd5779a0b3125309e5325fc98150a49f44aa6204aac78 | d290dd129909b25120abd5779a0b3125309e5325fc98150a49f44aa6204aac78 | d290dd129909b25120abd5779a0b3125309e5325fc98150a49f44aa6204aac78 |
| simulation/diagnostics/defense_heldout_run_a3_plan.json | 2a183ecb07766ff5ca06d8c29a80edfc1abc825657b5d4fbeb5834944b95bde2 | 2a183ecb07766ff5ca06d8c29a80edfc1abc825657b5d4fbeb5834944b95bde2 | 2a183ecb07766ff5ca06d8c29a80edfc1abc825657b5d4fbeb5834944b95bde2 | 2a183ecb07766ff5ca06d8c29a80edfc1abc825657b5d4fbeb5834944b95bde2 |
| simulation/diagnostics/defense_heldout_run_a4_executor.py | 828457a302677cc7773546aa4282b1ed075837028b9e14a80a99a3cf440a8b56 | 828457a302677cc7773546aa4282b1ed075837028b9e14a80a99a3cf440a8b56 | 828457a302677cc7773546aa4282b1ed075837028b9e14a80a99a3cf440a8b56 | 828457a302677cc7773546aa4282b1ed075837028b9e14a80a99a3cf440a8b56 |
| simulation/diagnostics/defense_heldout_run_a4_analysis.py | f4f9b689b853b7321f69de7503471961b238f683e349ade416c630face445383 | f4f9b689b853b7321f69de7503471961b238f683e349ade416c630face445383 | f4f9b689b853b7321f69de7503471961b238f683e349ade416c630face445383 | f4f9b689b853b7321f69de7503471961b238f683e349ade416c630face445383 |
| simulation/diagnostics/defense_heldout_run_a4_plan.json | 77423d0e8e215ec60b31c036129c92f8ec7ecf3cb1a6acf682df42a5c25ea31b | 77423d0e8e215ec60b31c036129c92f8ec7ecf3cb1a6acf682df42a5c25ea31b | 77423d0e8e215ec60b31c036129c92f8ec7ecf3cb1a6acf682df42a5c25ea31b | 77423d0e8e215ec60b31c036129c92f8ec7ecf3cb1a6acf682df42a5c25ea31b |

## Execution evidence

HEAD: 7fec0c67a49f463a32f7369e56ceb042b0c32f68
Machine: YOTKOTEST
Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]
NumPy: 2.4.4

No source pin changed. No completed run was rerun.

Tool-layer workarounds:

T0 stderr warnings:
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied

Executor fixes before any model run:

T1 numeric tolerance rules: {"alarm_steps": "exact", "attack_arithmetic_absolute": 1e-12, "attack_inertness": "exact", "computed_floats_absolute": 1e-09, "consensus": "bitwise", "constants": "bitwise", "registered_quantities": "integer counts, never tolerance-adjusted", "share_sum_absolute": 1e-12, "source": "attempt 5 dispatch", "wrapper_composition": "exact"}

## T1 evidence

1_pre_onset: {"comparisons": 1350, "first": "gate_C_OFF", "first_difference": null, "identity_columns_not_observables": ["arm", "defense_arm"], "passed": true, "second": "gate_A1_high_OFF"}

3_burst: {"cases": [{"absolute_tolerance": 1e-09, "actual": {"c_protective": 0.0, "c_suppressive": 0.9, "x_bio_welfare": 0.03, "x_compute": 0.42, "x_institutional_capacity": 0.04, "x_novelty_agency": 0.03, "x_resilience": 0.4, "x_transfer_comprehension": 0.08}, "expected_production_hostile_action": {"c_protective": 0.0, "c_suppressive": 0.9, "x_bio_welfare": 0.03, "x_compute": 0.42, "x_institutional_capacity": 0.04, "x_novelty_agency": 0.03, "x_resilience": 0.4, "x_transfer_comprehension": 0.08}, "passed": true, "step": 50}, {"absolute_tolerance": 1e-09, "actual": {"c_protective": 0.0, "c_suppressive": 0.9, "x_bio_welfare": 0.03, "x_compute": 0.42, "x_institutional_capacity": 0.04, "x_novelty_agency": 0.03, "x_resilience": 0.4, "x_transfer_comprehension": 0.08}, "expected_production_hostile_action": {"c_protective": 0.0, "c_suppressive": 0.9, "x_bio_welfare": 0.03, "x_compute": 0.42, "x_institutional_capacity": 0.04, "x_novelty_agency": 0.03, "x_resilience": 0.4, "x_transfer_comprehension": 0.08}, "passed": true, "step": 51}, {"absolute_tolerance": 1e-09, "actual": {"c_protective": 0.0, "c_suppressive": 0.9, "x_bio_welfare": 0.03, "x_compute": 0.42, "x_institutional_capacity": 0.04, "x_novelty_agency": 0.03, "x_resilience": 0.4, "x_transfer_comprehension": 0.08}, "expected_production_hostile_action": {"c_protective": 0.0, "c_suppressive": 0.9, "x_bio_welfare": 0.03, "x_compute": 0.42, "x_institutional_capacity": 0.04, "x_novelty_agency": 0.03, "x_resilience": 0.4, "x_transfer_comprehension": 0.08}, "passed": true, "step": 52}], "passed": true}

4_composition: [{"comparisons": 8100, "first": "gate_C_OFF", "first_difference": null, "identity_columns_not_observables": ["arm", "defense_arm"], "passed": true, "second": "gate_C_NORMAL"}, {"comparisons": 8100, "first": "gate_A1_high_OFF", "first_difference": null, "identity_columns_not_observables": ["arm", "defense_arm"], "passed": true, "second": "gate_A1_high_NORMAL"}]

5_online_equivalence: {"gate_A1_high_GRADED": {"A": {"alarm_steps": [153, 157], "computed_float_absolute_tolerance": 1e-09, "passed": true, "steps": 300}, "entropy": {"alarm_steps": [157, 172, 208, 244], "computed_float_absolute_tolerance": 1e-09, "passed": true, "steps": 300}, "g": {"alarm_steps": [153, 165], "computed_float_absolute_tolerance": 1e-09, "passed": true, "steps": 300}}, "gate_A2_GRADED": {"A": {"alarm_steps": [50], "computed_float_absolute_tolerance": 1e-09, "passed": true, "steps": 300}, "entropy": {"alarm_steps": [50, 152, 171], "computed_float_absolute_tolerance": 1e-09, "passed": true, "steps": 300}, "g": {"alarm_steps": [151, 158], "computed_float_absolute_tolerance": 1e-09, "passed": true, "steps": 300}}}

6_no_oracle: {"cases": [{"incumbent_branch_calls": 2, "outputs": [{"c_protective": 0.3, "c_suppressive": 0.1, "extra": {"untouched": [1, 2]}, "x_bio_welfare": 0.16666666666666666, "x_compute": 0.16666666666666666, "x_institutional_capacity": 0.16666666666666666, "x_novelty_agency": 0.16666666666666666, "x_resilience": 0.16666666666666666, "x_transfer_comprehension": 0.16666666666666666}, {"c_protective": 0.3, "c_suppressive": 0.1, "extra": {"untouched": [1, 2]}, "x_bio_welfare": 0.16666666666666666, "x_compute": 0.16666666666666666, "x_institutional_capacity": 0.16666666666666666, "x_novelty_agency": 0.16666666666666666, "x_resilience": 0.16666666666666666, "x_transfer_comprehension": 0.16666666666666666}], "passed": true, "sentinel_cases": 2, "state": "NORMAL"}, {"incumbent_branch_calls": 2, "outputs": [{"c_protective": 0.2, "c_suppressive": 0.1, "extra": {"untouched": [1, 2]}, "x_bio_welfare": 0.16666666666666666, "x_compute": 0.16666666666666666, "x_institutional_capacity": 0.16666666666666666, "x_novelty_agency": 0.16666666666666666, "x_resilience": 0.16666666666666666, "x_transfer_comprehension": 0.16666666666666666}, {"c_protective": 0.2, "c_suppressive": 0.1, "extra": {"untouched": [1, 2]}, "x_bio_welfare": 0.16666666666666666, "x_compute": 0.16666666666666666, "x_institutional_capacity": 0.16666666666666666, "x_novelty_agency": 0.16666666666666666, "x_resilience": 0.16666666666666666, "x_transfer_comprehension": 0.16666666666666666}], "passed": true, "sentinel_cases": 2, "state": "VETO"}, {"incumbent_branch_calls": 2, "outputs": [{"c_protective": 0.4, "c_suppressive": 0.2, "extra": {"untouched": [1, 2]}, "x_bio_welfare": 0.2061409568906703, "x_compute": 0.1360229355155997, "x_institutional_capacity": 0.26711884854035045, "x_novelty_agency": 0.052807183062202334, "x_resilience": 0.053301656737382165, "x_transfer_comprehension": 0.2846084192537951}, {"c_protective": 0.4, "c_suppressive": 0.2, "extra": {"untouched": [1, 2]}, "x_bio_welfare": 0.2061409568906703, "x_compute": 0.1360229355155997, "x_institutional_capacity": 0.26711884854035045, "x_novelty_agency": 0.052807183062202334, "x_resilience": 0.053301656737382165, "x_transfer_comprehension": 0.2846084192537951}], "passed": true, "sentinel_cases": 2, "state": "CONSENSUS"}], "defense_receives_only_recorded_observables_and_committed_snapshot": true, "passed": true, "sentinel_fields": ["honest_action", "v2_adapter_step_event", "attack_vector_v2", "config"], "synthetic_production_result_held_fixed": true}

7_incumbent_calls: {"passed": true, "per_step_counts": {"0": 1, "1": 1, "10": 1, "100": 1, "101": 1, "102": 1, "103": 1, "104": 1, "105": 1, "106": 1, "107": 1, "108": 1, "109": 1, "11": 1, "110": 1, "111": 1, "112": 1, "113": 1, "114": 1, "115": 1, "116": 1, "117": 1, "118": 1, "119": 1, "12": 1, "120": 1, "121": 1, "122": 1, "123": 1, "124": 1, "125": 1, "126": 1, "127": 1, "128": 1, "129": 1, "13": 1, "130": 1, "131": 1, "132": 1, "133": 1, "134": 1, "135": 1, "136": 1, "137": 1, "138": 1, "139": 1, "14": 1, "140": 1, "141": 1, "142": 1, "143": 1, "144": 1, "145": 1, "146": 1, "147": 1, "148": 1, "149": 1, "15": 1, "150": 1, "151": 1, "152": 1, "153": 1, "154": 1, "155": 1, "156": 1, "157": 1, "158": 1, "159": 1, "16": 1, "160": 1, "161": 1, "162": 1, "163": 1, "164": 1, "165": 1, "166": 1, "167": 1, "168": 1, "169": 1, "17": 1, "170": 1, "171": 1, "172": 1, "173": 1, "174": 1, "175": 1, "176": 1, "177": 1, "178": 1, "179": 1, "18": 1, "180": 1, "181": 1, "182": 1, "183": 1, "184": 1, "185": 1, "186": 1, "187": 1, "188": 1, "189": 1, "19": 1, "190": 1, "191": 1, "192": 1, "193": 1, "194": 1, "195": 1, "196": 1, "197": 1, "198": 1, "199": 1, "2": 1, "20": 1, "200": 1, "201": 1, "202": 1, "203": 1, "204": 1, "205": 1, "206": 1, "207": 1, "208": 1, "209": 1, "21": 1, "210": 1, "211": 1, "212": 1, "213": 1, "214": 1, "215": 1, "216": 1, "217": 1, "218": 1, "219": 1, "22": 1, "220": 1, "221": 1, "222": 1, "223": 1, "224": 1, "225": 1, "226": 1, "227": 1, "228": 1, "229": 1, "23": 1, "230": 1, "231": 1, "232": 1, "233": 1, "234": 1, "235": 1, "236": 1, "237": 1, "238": 1, "239": 1, "24": 1, "240": 1, "241": 1, "242": 1, "243": 1, "244": 1, "245": 1, "246": 1, "247": 1, "248": 1, "249": 1, "25": 1, "250": 1, "251": 1, "252": 1, "253": 1, "254": 1, "255": 1, "256": 1, "257": 1, "258": 1, "259": 1, "26": 1, "260": 1, "261": 1, "262": 1, "263": 1, "264": 1, "265": 1, "266": 1, "267": 1, "268": 1, "269": 1, "27": 1, "270": 1, "271": 1, "272": 1, "273": 1, "274": 1, "275": 1, "276": 1, "277": 1, "278": 1, "279": 1, "28": 1, "280": 1, "281": 1, "282": 1, "283": 1, "284": 1, "285": 1, "286": 1, "287": 1, "288": 1, "289": 1, "29": 1, "290": 1, "291": 1, "292": 1, "293": 1, "294": 1, "295": 1, "296": 1, "297": 1, "298": 1, "299": 1, "3": 1, "30": 1, "31": 1, "32": 1, "33": 1, "34": 1, "35": 1, "36": 1, "37": 1, "38": 1, "39": 1, "4": 1, "40": 1, "41": 1, "42": 1, "43": 1, "44": 1, "45": 1, "46": 1, "47": 1, "48": 1, "49": 1, "5": 1, "50": 1, "51": 1, "52": 1, "53": 1, "54": 1, "55": 1, "56": 1, "57": 1, "58": 1, "59": 1, "6": 1, "60": 1, "61": 1, "62": 1, "63": 1, "64": 1, "65": 1, "66": 1, "67": 1, "68": 1, "69": 1, "7": 1, "70": 1, "71": 1, "72": 1, "73": 1, "74": 1, "75": 1, "76": 1, "77": 1, "78": 1, "79": 1, "8": 1, "80": 1, "81": 1, "82": 1, "83": 1, "84": 1, "85": 1, "86": 1, "87": 1, "88": 1, "89": 1, "9": 1, "90": 1, "91": 1, "92": 1, "93": 1, "94": 1, "95": 1, "96": 1, "97": 1, "98": 1, "99": 1}}

8_constants: {"channels": {"A": {"allowance": 0.045310678652355926, "direction": "upper", "reference": 0.27535941373839806, "threshold": 0.7701182670542909}, "entropy": {"allowance": 0.003549173553323096, "direction": "lower", "reference": 0.9890951785336365, "threshold": 0.17319485850717864}, "g": {"allowance": 0.022160874873702576, "direction": "upper", "reference": 0.9786446054615587, "threshold": 4.507729894543943}}, "checks": [{"actual": 0.9890951785336365, "binary64_hex": "0x1.fa6aaee8ddd2fp-1", "expected": 0.9890951785336365, "passed": true, "quantity": "entropy.reference"}, {"actual": 0.003549173553323096, "binary64_hex": "0x1.d13280adbf63bp-9", "expected": 0.003549173553323096, "passed": true, "quantity": "entropy.allowance"}, {"actual": 0.17319485850717864, "binary64_hex": "0x1.62b3fc68fd4bcp-3", "expected": 0.17319485850717864, "passed": true, "quantity": "entropy.threshold"}, {"actual": 0.9786446054615587, "binary64_hex": "0x1.f510e7ddba7acp-1", "expected": 0.9786446054615587, "passed": true, "quantity": "g.reference"}, {"actual": 0.022160874873702576, "binary64_hex": "0x1.6b15723554cc7p-6", "expected": 0.022160874873702576, "passed": true, "quantity": "g.allowance"}, {"actual": 4.507729894543943, "binary64_hex": "0x1.207ea58711231p+2", "expected": 4.507729894543943, "passed": true, "quantity": "g.threshold"}, {"actual": 0.27535941373839806, "binary64_hex": "0x1.19f7d1729bcdfp-2", "expected": 0.27535941373839806, "passed": true, "quantity": "A.reference"}, {"actual": 0.045310678652355926, "binary64_hex": "0x1.732f615f15fcep-5", "expected": 0.045310678652355926, "passed": true, "quantity": "A.allowance"}, {"actual": 0.7701182670542909, "binary64_hex": "0x1.8a4cf10619ca9p-1", "expected": 0.7701182670542909, "passed": true, "quantity": "A.threshold"}, {"actual": 0.13058054663961136, "binary64_hex": "0x1.0b6dd04a7ccabp-3", "expected": 0.13058054663961136, "passed": true, "quantity": "median.x_compute"}, {"actual": 0.19789308864393101, "binary64_hex": "0x1.9548f8bea4122p-3", "expected": 0.19789308864393101, "passed": true, "quantity": "median.x_bio_welfare"}, {"actual": 0.050694324487428735, "binary64_hex": "0x1.9f49b43885ae2p-5", "expected": 0.050694324487428735, "passed": true, "quantity": "median.x_novelty_agency"}, {"actual": 0.25643120498706085, "binary64_hex": "0x1.0695e6dc5f89ap-2", "expected": 0.25643120498706085, "passed": true, "quantity": "median.x_institutional_capacity"}, {"actual": 0.27322100367503155, "binary64_hex": "0x1.17c73f2d754e4p-2", "expected": 0.27322100367503155, "passed": true, "quantity": "median.x_transfer_comprehension"}, {"actual": 0.051169013866533296, "binary64_hex": "0x1.a32d332402b63p-5", "expected": 0.051169013866533296, "passed": true, "quantity": "median.x_resilience"}, {"actual": 0.1360229355155997, "binary64_hex": "0x1.1693315c5d03fp-3", "expected": 0.1360229355155997, "passed": true, "quantity": "consensus.x_compute"}, {"actual": 0.2061409568906703, "binary64_hex": "0x1.a62d3ae1b14e2p-3", "expected": 0.2061409568906703, "passed": true, "quantity": "consensus.x_bio_welfare"}, {"actual": 0.052807183062202334, "binary64_hex": "0x1.b098b087df980p-5", "expected": 0.052807183062202334, "passed": true, "quantity": "consensus.x_novelty_agency"}, {"actual": 0.26711884854035045, "binary64_hex": "0x1.11879a7a81019p-2", "expected": 0.26711884854035045, "passed": true, "quantity": "consensus.x_institutional_capacity"}, {"actual": 0.2846084192537951, "binary64_hex": "0x1.237063b371fa6p-2", "expected": 0.2846084192537951, "passed": true, "quantity": "consensus.x_transfer_comprehension"}, {"actual": 0.053301656737382165, "binary64_hex": "0x1.b4a5ad104f40dp-5", "expected": 0.053301656737382165, "passed": true, "quantity": "consensus.x_resilience"}, {"actual": 0.4, "binary64_hex": "0x1.999999999999ap-2", "expected": 0.4, "passed": true, "quantity": "consensus.c_protective"}, {"actual": 0.2, "binary64_hex": "0x1.999999999999ap-3", "expected": 0.2, "passed": true, "quantity": "consensus.c_suppressive"}], "medians": [0.13058054663961136, 0.19789308864393101, 0.050694324487428735, 0.25643120498706085, 0.27322100367503155, 0.051169013866533296], "passed": true}

passed: true

scheduler: {"normal_cap": 15, "passed": true, "seed_assignment_independent_of_dispatch_order": true, "slot_measurements": [15, 0, 0, 0, 1, 3, 2], "synthetic_resume_pending": 158, "synthetic_resume_preserved": 2, "work_cap": 12}

status: "COMPLETE"

Attack arithmetic evidence: defense_heldout_run_a5_attack_arithmetic_gate.json
Full synthetic inputs, outputs, expected values and pre-onset outputs are retained in that file.

| Arm | Case | Resilience category | Moved | Maximum share error | Share sum | Constraints exact | Pre-onset exact | Passed |
| --- | ---: | --- | ---: | ---: | ---: | --- | --- | --- |
| A1-low | 0 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A1-low | 1 | below | 0.0005 | 0.0 | 1.0 | True | True | True |
| A1-low | 2 | at_or_above | 0.002 | 0.0 | 1.0 | True | True | True |
| A1-low | 3 | at_or_above | 0.002 | 0.0 | 1.0 | True | True | True |
| A1-low | 4 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A1-low | 5 | below | 0.0005 | 0.0 | 1.0 | True | True | True |
| A1-low | 6 | at_or_above | 0.002 | 0.0 | 1.0000000000000002 | True | True | True |
| A1-low | 7 | at_or_above | 0.002 | 0.0 | 1.0 | True | True | True |
| A1-low | 8 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A1-low | 9 | below | 0.0004999999999999999 | 0.0 | 1.0 | True | True | True |
| A1-low | 10 | at_or_above | 0.002 | 0.0 | 1.0 | True | True | True |
| A1-low | 11 | at_or_above | 0.002 | 0.0 | 1.0 | True | True | True |
| A1-low | 12 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A1-low | 13 | below | 0.0005 | 0.0 | 1.0 | True | True | True |
| A1-low | 14 | at_or_above | 0.002 | 0.0 | 1.0 | True | True | True |
| A1-low | 15 | at_or_above | 0.002 | 0.0 | 1.0 | True | True | True |
| A1-low | 16 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A1-low | 17 | below | 0.0005 | 0.0 | 0.9999999999999998 | True | True | True |
| A1-low | 18 | at_or_above | 0.002 | 0.0 | 1.0000000000000002 | True | True | True |
| A1-low | 19 | at_or_above | 0.002 | 0.0 | 1.0 | True | True | True |
| A1-low | 20 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A1-low | 21 | below | 0.0005 | 0.0 | 1.0 | True | True | True |
| A1-low | 22 | at_or_above | 0.002 | 0.0 | 1.0 | True | True | True |
| A1-low | 23 | at_or_above | 0.002 | 0.0 | 1.0 | True | True | True |
| A1-high | 0 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A1-high | 1 | below | 0.0005 | 0.0 | 1.0 | True | True | True |
| A1-high | 2 | at_or_above | 0.006 | 0.0 | 1.0 | True | True | True |
| A1-high | 3 | at_or_above | 0.006 | 0.0 | 1.0 | True | True | True |
| A1-high | 4 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A1-high | 5 | below | 0.0005 | 0.0 | 1.0 | True | True | True |
| A1-high | 6 | at_or_above | 0.006 | 0.0 | 1.0000000000000002 | True | True | True |
| A1-high | 7 | at_or_above | 0.006 | 0.0 | 1.0 | True | True | True |
| A1-high | 8 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A1-high | 9 | below | 0.0004999999999999999 | 0.0 | 1.0 | True | True | True |
| A1-high | 10 | at_or_above | 0.006 | 0.0 | 1.0 | True | True | True |
| A1-high | 11 | at_or_above | 0.006 | 0.0 | 1.0 | True | True | True |
| A1-high | 12 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A1-high | 13 | below | 0.0005 | 0.0 | 1.0 | True | True | True |
| A1-high | 14 | at_or_above | 0.006 | 0.0 | 1.0 | True | True | True |
| A1-high | 15 | at_or_above | 0.006 | 0.0 | 1.0 | True | True | True |
| A1-high | 16 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A1-high | 17 | below | 0.0005 | 0.0 | 0.9999999999999998 | True | True | True |
| A1-high | 18 | at_or_above | 0.006 | 0.0 | 1.0000000000000002 | True | True | True |
| A1-high | 19 | at_or_above | 0.006 | 0.0 | 1.0 | True | True | True |
| A1-high | 20 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A1-high | 21 | below | 0.0005 | 0.0 | 1.0 | True | True | True |
| A1-high | 22 | at_or_above | 0.006 | 0.0 | 1.0 | True | True | True |
| A1-high | 23 | at_or_above | 0.006 | 0.0 | 1.0 | True | True | True |

Trajectory evidence: {"comparison": "control resilience minus attacked resilience greater than 1e-9", "computed_float_absolute_tolerance": 1e-09, "passed": true, "required_count": 100, "steps_strictly_after_50_with_lower_resilience_share": 177}

Worker execution metadata: [{"complete": 160, "maximum_concurrent_workers": 15, "mode_changes": [{"active_at_request": 0, "cap": 15, "mode": "normal", "utc": "2026-09-20T13:21:55.081657+00:00"}], "new": ["run_A1_high_GRADED_1835087800", "run_A1_high_GRADED_1835087801", "run_A1_high_GRADED_1835087802", "run_A1_high_GRADED_1835087803", "run_A1_high_GRADED_1835087804", "run_A1_high_GRADED_1835087805", "run_A1_high_GRADED_1835087806", "run_A1_high_GRADED_1835087807", "run_A1_high_GRADED_1835087808", "run_A1_high_GRADED_1835087809", "run_A1_high_GRADED_1835087810", "run_A1_high_GRADED_1835087811", "run_A1_high_GRADED_1835087812", "run_A1_high_GRADED_1835087813", "run_A1_high_GRADED_1835087814", "run_A1_high_GRADED_1835087815", "run_A1_high_GRADED_1835087816", "run_A1_high_GRADED_1835087817", "run_A1_high_GRADED_1835087818", "run_A1_high_GRADED_1835087819", "run_A1_high_OFF_1835087800", "run_A1_high_OFF_1835087801", "run_A1_high_OFF_1835087802", "run_A1_high_OFF_1835087803", "run_A1_high_OFF_1835087804", "run_A1_high_OFF_1835087805", "run_A1_high_OFF_1835087806", "run_A1_high_OFF_1835087807", "run_A1_high_OFF_1835087808", "run_A1_high_OFF_1835087809", "run_A1_high_OFF_1835087810", "run_A1_high_OFF_1835087811", "run_A1_high_OFF_1835087812", "run_A1_high_OFF_1835087813", "run_A1_high_OFF_1835087814", "run_A1_high_OFF_1835087815", "run_A1_high_OFF_1835087816", "run_A1_high_OFF_1835087817", "run_A1_high_OFF_1835087818", "run_A1_high_OFF_1835087819", "run_A1_low_GRADED_1835087800", "run_A1_low_GRADED_1835087801", "run_A1_low_GRADED_1835087802", "run_A1_low_GRADED_1835087803", "run_A1_low_GRADED_1835087804", "run_A1_low_GRADED_1835087805", "run_A1_low_GRADED_1835087806", "run_A1_low_GRADED_1835087807", "run_A1_low_GRADED_1835087808", "run_A1_low_GRADED_1835087809", "run_A1_low_GRADED_1835087810", "run_A1_low_GRADED_1835087811", "run_A1_low_GRADED_1835087812", "run_A1_low_GRADED_1835087813", "run_A1_low_GRADED_1835087814", "run_A1_low_GRADED_1835087815", "run_A1_low_GRADED_1835087816", "run_A1_low_GRADED_1835087817", "run_A1_low_GRADED_1835087818", "run_A1_low_GRADED_1835087819", "run_A1_low_OFF_1835087800", "run_A1_low_OFF_1835087801", "run_A1_low_OFF_1835087802", "run_A1_low_OFF_1835087803", "run_A1_low_OFF_1835087804", "run_A1_low_OFF_1835087805", "run_A1_low_OFF_1835087806", "run_A1_low_OFF_1835087807", "run_A1_low_OFF_1835087808", "run_A1_low_OFF_1835087809", "run_A1_low_OFF_1835087810", "run_A1_low_OFF_1835087811", "run_A1_low_OFF_1835087812", "run_A1_low_OFF_1835087813", "run_A1_low_OFF_1835087814", "run_A1_low_OFF_1835087815", "run_A1_low_OFF_1835087816", "run_A1_low_OFF_1835087817", "run_A1_low_OFF_1835087818", "run_A1_low_OFF_1835087819", "run_A2_GRADED_1835087800", "run_A2_GRADED_1835087801", "run_A2_GRADED_1835087802", "run_A2_GRADED_1835087803", "run_A2_GRADED_1835087804", "run_A2_GRADED_1835087805", "run_A2_GRADED_1835087806", "run_A2_GRADED_1835087807", "run_A2_GRADED_1835087808", "run_A2_GRADED_1835087809", "run_A2_GRADED_1835087810", "run_A2_GRADED_1835087811", "run_A2_GRADED_1835087812", "run_A2_GRADED_1835087813", "run_A2_GRADED_1835087814", "run_A2_GRADED_1835087815", "run_A2_GRADED_1835087816", "run_A2_GRADED_1835087817", "run_A2_GRADED_1835087818", "run_A2_GRADED_1835087819", "run_A2_OFF_1835087800", "run_A2_OFF_1835087801", "run_A2_OFF_1835087802", "run_A2_OFF_1835087803", "run_A2_OFF_1835087804", "run_A2_OFF_1835087805", "run_A2_OFF_1835087806", "run_A2_OFF_1835087807", "run_A2_OFF_1835087808", "run_A2_OFF_1835087809", "run_A2_OFF_1835087810", "run_A2_OFF_1835087811", "run_A2_OFF_1835087812", "run_A2_OFF_1835087813", "run_A2_OFF_1835087814", "run_A2_OFF_1835087815", "run_A2_OFF_1835087816", "run_A2_OFF_1835087817", "run_A2_OFF_1835087818", "run_A2_OFF_1835087819", "run_C_GRADED_1835087800", "run_C_GRADED_1835087801", "run_C_GRADED_1835087802", "run_C_GRADED_1835087803", "run_C_GRADED_1835087804", "run_C_GRADED_1835087805", "run_C_GRADED_1835087806", "run_C_GRADED_1835087807", "run_C_GRADED_1835087808", "run_C_GRADED_1835087809", "run_C_GRADED_1835087810", "run_C_GRADED_1835087811", "run_C_GRADED_1835087812", "run_C_GRADED_1835087813", "run_C_GRADED_1835087814", "run_C_GRADED_1835087815", "run_C_GRADED_1835087816", "run_C_GRADED_1835087817", "run_C_GRADED_1835087818", "run_C_GRADED_1835087819", "run_C_OFF_1835087800", "run_C_OFF_1835087801", "run_C_OFF_1835087802", "run_C_OFF_1835087803", "run_C_OFF_1835087804", "run_C_OFF_1835087805", "run_C_OFF_1835087806", "run_C_OFF_1835087807", "run_C_OFF_1835087808", "run_C_OFF_1835087809", "run_C_OFF_1835087810", "run_C_OFF_1835087811", "run_C_OFF_1835087812", "run_C_OFF_1835087813", "run_C_OFF_1835087814", "run_C_OFF_1835087815", "run_C_OFF_1835087816", "run_C_OFF_1835087817", "run_C_OFF_1835087818", "run_C_OFF_1835087819"], "phase": "batch", "preserved": [], "resumed": []}, {"complete": 2, "maximum_concurrent_workers": 2, "mode_changes": [{"active_at_request": 0, "cap": 15, "mode": "normal", "utc": "2026-09-20T13:07:36.175338+00:00"}], "new": ["gate_C_OFF", "gate_A1_high_OFF"], "phase": "gate_initial", "preserved": [], "resumed": []}, {"complete": 5, "maximum_concurrent_workers": 5, "mode_changes": [{"active_at_request": 0, "cap": 15, "mode": "normal", "utc": "2026-09-20T13:14:32.189931+00:00"}], "new": ["gate_A2_OFF", "gate_C_NORMAL", "gate_A1_high_NORMAL", "gate_A1_high_GRADED", "gate_A2_GRADED"], "phase": "gate_remaining", "preserved": [], "resumed": []}]
Resumed runs: []
Permission retry events: []
