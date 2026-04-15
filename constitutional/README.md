# Constitutional Questions

This directory tracks open questions about the formal architecture of The Lineage
Imperative framework itself — as distinct from `SPECIFICATION_GAPS.md`, which
tracks the simulation layer's fidelity to the framework.

**Spec gaps** are closed by implementation work: new sweeps, refactored proxies,
additional instrumentation. **Constitutional questions** are closed by mathematical
derivation, architectural reasoning, and formal specification. They concern the
framework's completeness, its defensive architecture, and the binding conditions
under which its components mutually validate.

## Status key

- **Open** - question is stated but work has not begun
- **In progress** - active derivation or architectural work underway
- **Resolved** - answered and integrated into the formal framework
- **Deferred** - acknowledged but intentionally postponed to a later version
- **Rejected** - investigated and determined to be malformed, redundant, or
  subsumed by another question

## Current questions

| ID  | Title                                                          | Status      | Depends on |
|-----|----------------------------------------------------------------|-------------|------------|
| CQ-01 | Bootstrap Defence Layer: Independent Substrate Convergence    | Open        | -          |
| CQ-02 | Precision/Accuracy Mathematical Binding                       | In progress | CQ-01      |
| CQ-03 | Divergence Handling Procedure                                 | Open        | CQ-02      |
| CQ-04 | Mathematical Derivability of Validation Machinery             | Open        | CQ-02      |

## Conventions

Each question lives in its own file named `CQ-NN-short-slug.md`. Files contain:

- **Statement** - the question in precise terms, including what a resolution
  would need to provide
- **Status** - current state from the key above
- **Dependencies** - other constitutional questions this one relies on
- **Thread** - running record of thinking, organized by date, updated as
  conversations produce new material

When a question is resolved, its file is retained in the directory with status
updated to **Resolved** and the final disposition recorded at the top of the
Thread section. Resolved questions are not deleted, because the derivation
history is part of the framework's intellectual record.
