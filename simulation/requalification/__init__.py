"""Post-update requalification harness (REQUALIFICATION_PLAN.md, 2026-10-29).

Operational tooling, deliberately outside ``v3.artifacts.source_manifest``: that
manifest covers ``simulation/v3/*.py``, the non-test ``simulation/*.py`` and four
reviewed JSON records, so nothing in this package enters any code identity.

The harness replays a frozen, deterministically selected sample of completed
jobs at each job's original producing code identity (X), in an isolated scratch
checkout of that identity, under the post-update runtime (E), and compares the
scientific bytes of each fresh result with the archived durable output. It
calls the original producers' unchanged functions from outside their manifests.
It re-simulates every job and every extension replicate from its original seed
into empty scratch, never installs an archived checkpoint or output as completed
work, compares only, and publishes or latches nothing.
"""
