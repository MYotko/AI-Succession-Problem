"""B1 execution guards with independent validator dependency records.

This is a local simulation gate, not certification of D10-D12 institutions.
Unknown irreversible actions and registered execution with fixtures fail
closed. Production authority and gate revalidation belong to the B2 runner.
"""

from dataclasses import dataclass, field
import hashlib
import json


@dataclass
class Validator:
    validator_id: str
    dependencies: dict = field(default_factory=dict)
    decisions: list = field(default_factory=list)

    def check(self, evidence):
        accepted = all(evidence.get(k, False) for k in ("welfare_floor", "reproduction_floor", "cohort_admitted", "deadline_valid", "capability_valid"))
        digest = hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()
        self.dependencies["last_evidence_hash"] = digest
        self.decisions.append((digest, accepted))
        return accepted


class ExecutionGuards:
    def __init__(self, count=4, fault_budget=1, authority=None):
        if count < 3 * fault_budget + 1:
            raise ValueError("empty peer quorum band")
        self.validators = [Validator(f"validator-{i}") for i in range(count)]
        self.required = (count + fault_budget + 2) // 2
        self.records = []
        self.authority = authority

    def authorize(self, action_type, evidence, *, fixture=True):
        votes = [v.check(dict(evidence)) for v in self.validators]
        allowed = action_type == "succession" and sum(votes) >= self.required and (fixture or bool(self.authority))
        self.records.append({"action": action_type, "votes": votes, "allowed": allowed,
                             "authority": "local_fixture_only" if fixture else self.authority})
        return allowed
