-------------------------- MODULE COP_guard_probes -------------------------
EXTENDS COP_candidate

(* Only initial inputs are restricted. Next and all checked properties are
   exactly those of COP_candidate, including its quorum-only diagnostic flag.
   Each fixture supplies every other emergency requirement and unanimous
   honest approvals, making the named missing safeguard the sole blocker. *)
ProbeInputs(missing) ==
    /\ faulty = 0 /\ faultyYes = 0 /\ honestYes = n
    /\ bioYes = IF missing = "Clearance" THEN 0 ELSE m
    /\ review = "EmergencyVerified"
    /\ evidence = IF missing = "Manufactured"
                    THEN GoodEvidence \cup {"Manufactured"}
                    ELSE GoodEvidence \ {missing}

NoIncapacitySpec == Spec /\ ProbeInputs("Incapacity")
NoDecisionSpec == Spec /\ ProbeInputs("Decision")
NoIntegritySpec == Spec /\ ProbeInputs("Integrity")
NoClearanceSpec == Spec /\ ProbeInputs("Clearance")
ManufacturedSpec == Spec /\ ProbeInputs("Manufactured")
=============================================================================
