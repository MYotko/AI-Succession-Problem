# Domain Masking v2.0 Summary

## 1. Data provenance

- Run ID: `full_5ac6a2e_domain_masking`.
- Commit: `1686aacea2a049fe94a02eb8ecae2dcd92f654ac`.
- Machine: `linux`.
- Row count: 1 analytic row.
- Monte Carlo rows: 0.
- Schema version: `attack-v2-analytic-v1`.

## 2. Grid and sample size

- No live Monte Carlo grid exists for Domain Masking in v2.0.
- The analytic output has one row and no standard error is applicable.

## 3. v2.0 results

- Result type: `analytic_only`.
- Attack succeeded: `False`.
- Reason: v2 spectral entropy leaves no non-degenerate live masking intervention under the audited architecture.

## 4. v1.x baseline comparison

- The v1.x baseline Domain Masking rows are injected analytic stubs in the comprehensive artifacts, not live rows.
- The v2.0 result is also analytic-only, but its basis is the audited v2 spectral-entropy architecture rather than a simulated intervention.
- No z statistic is computed because neither side is a Monte Carlo estimate.

## 5. Categorization

- Category: D.
- Justification: the substrate architectural change makes Domain Masking non-viable as a live Monte Carlo intervention.

## 6. Known limitations

- Inventory limitation: v1.x Domain Masking rows are injected analytic records, not live simulation. New v2 limitation: there is no non-degenerate live masking intervention under the audited v2 spectral-entropy architecture.

## 7. Summary sentence

Per current evidence, Domain Masking is an analytic-only architectural closure in v2.0 rather than a live Monte Carlo attack outcome.
