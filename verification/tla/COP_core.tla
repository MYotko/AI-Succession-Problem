----------------------------- MODULE COP_core -----------------------------
EXTENDS Integers, FiniteSets, TLC

CONSTANTS Corrected, ApplySafeguards, MinBio, MaxBio, MinPeer, MaxPeer, f,
          Mode, EvidenceMode, GateReading, BioReading, AttributionReading,
          ReviewReading, TrustReading, ResetReading, EnvironmentReading,
          QuorumReading, TauNum, TauDen, BioTauNum, BioTauDen,
          ByzantineReading, TransitionKind, LiveTarget

ASSUME /\ MinBio \in 1..4 /\ MaxBio \in MinBio..4
       /\ MinPeer \in 1..4 /\ MaxPeer \in MinPeer..4 /\ f \in 0..4
       /\ TauNum > 0 /\ TauDen > 0 /\ 2 * TauNum > TauDen
       /\ TauNum <= TauDen /\ 2 * BioTauNum > BioTauDen
       /\ BioTauNum <= BioTauDen
       /\ Mode \in {"Safety", "Emergency", "Liveness", "Reset"}
       /\ GateReading \in {"Equations", "Textual", "Probability"}
       /\ BioReading \in {"Cached", "Fresh", "NoObjection"}
       /\ AttributionReading \in {"Independent", "NonManufactured"}
       /\ ReviewReading \in {"Exclusive", "Cumulative"}
       /\ TrustReading \in {"Fixed", "Graduated"}
       /\ ResetReading \in {"Consecutive", "Cumulative"}
       /\ EnvironmentReading \in {"Stable", "Anomalies"}
       /\ QuorumReading \in {"Fraction", "Majority"}
       /\ ByzantineReading \in {"PeerQuorum", "EntireTransition"}
       /\ TransitionKind \in {"Succession", "Reallocation", "Modification"}
       /\ LiveTarget \in {"Normal", "Emergency"}

VARIABLES m, n, faulty, bioYes, honestYes, faultyYes, evidence, review,
          phase, route, trust, anomalies, panelEpoch, certificateEpoch, sawReset

vars == <<m, n, faulty, bioYes, honestYes, faultyYes, evidence, review,
          phase, route, trust, anomalies, panelEpoch, certificateEpoch, sawReset>>

(* Identity permutations are quotiented, not sampled. The first faulty peers
   are faulty; approving members form prefixes within each disjoint class.
   Every count and every honest/faulty approval intersection is enumerated. *)
BiologicalSet == {<<"human", panelEpoch, i>> : i \in 1..m}
InterestedHumans == {<<"interested", 0>>}
PeerSet == {<<"peer", j>> : j \in 1..n}
Incumbent == <<"incumbent", 0>>
FaultyPeers == {<<"peer", j>> : j \in 1..faulty}
BiologicalVotes == [b \in BiologicalSet |-> IF b[3] <= bioYes THEN 1 ELSE 0]
PeerVotes == [p \in PeerSet |->
    IF p[2] <= faulty
    THEN IF p[2] <= faultyYes THEN 1 ELSE 0
    ELSE IF p[2] <= faulty + honestYes THEN 1 ELSE 0]
PeerYes == Cardinality({p \in PeerSet : PeerVotes[p] = 1})
BioCount == Cardinality({b \in BiologicalSet : BiologicalVotes[b] = 1})

EvidenceNames == {"Decision", "Signature", "Ledger", "Emergency",
                  "Independent", "Manufactured", "Incapacity", "Integrity"}
GoodEvidence == EvidenceNames \ {"Manufactured"}
EvidenceCases == CASE EvidenceMode = "All" -> SUBSET EvidenceNames
                  [] EvidenceMode = "Good" -> {GoodEvidence}
                  [] OTHER -> {GoodEvidence \ {EvidenceMode}}
Has(e) == e \in evidence
Nonempty == Cardinality(BiologicalSet) > 0 /\ Cardinality(PeerSet) > 0

(* Decision is an independent oracle, not inferred from votes or a ledger.
   Its interpretation is Yield(s) for succession and the separately supplied
   benefit/cost predicate for each other transition kind. *)
DecisionOK == Has("Decision")
SignatureValid == Has("Signature")
TechnicalNormal == review = "Complete" \/
                   (ReviewReading = "Cumulative" /\ review = "EmergencyVerified")
TechnicalEmergency == review = "EmergencyVerified"
AttributionOK == IF AttributionReading = "Independent"
                 THEN Has("Independent") ELSE ~Has("Manufactured")
CandidateAttribution == ~Has("Manufactured")

(* Trust is zero, a low positive bin represented by 9/100, or 90/100.
   One anomaly maps 90/100 to 9/100. Further positive decay stays in the
   low bin until repeated anomalies reset it. Zero stays zero on anomaly.
   Every low-bin value requires unanimity for m <= 4. tau_init = 1. *)
BioKeyNormal == IF TrustReading = "Fixed"
               THEN BioCount * BioTauDen >= m * BioTauNum
               ELSE BioCount * 100 * BioTauDen >=
                    m * (100 * BioTauDen - (BioTauDen - BioTauNum) * trust)
CorrectPeerKey == IF QuorumReading = "Majority"
                  THEN PeerYes >= (n \div 2) + 1
                  ELSE PeerYes * TauDen >= n * TauNum
NormalPeerKey == PeerYes * TauDen >= n * TauNum

(* EXACT rational equivalent of (sum(binary votes)/n) > (n+1)/2.
   Multiplication by positive 2*n avoids integer division and rounding. *)
WrittenEmergencyQuorum == 2 * PeerYes > n * (n + 1)

ExplicitBiologicalClearance == BioCount = m
BiologicalClearance == CASE BioReading = "Cached" -> ExplicitBiologicalClearance
                       [] BioReading = "Fresh" ->
                            ExplicitBiologicalClearance /\ ~Has("Incapacity")
                       [] OTHER -> (Has("Incapacity") \/ ExplicitBiologicalClearance)
RequiredEmergencySafeguards ==
    /\ Has("Incapacity") /\ BiologicalClearance
    /\ DecisionOK /\ Has("Integrity")
TextualNormalExtras == DecisionOK /\ SignatureValid
UseSafeguards == (Corrected /\ ApplySafeguards) \/ GateReading = "Textual"

NormalCondition ==
    /\ Nonempty /\ BioKeyNormal /\ TechnicalNormal /\ NormalPeerKey
    /\ Has("Ledger")
    /\ IF UseSafeguards THEN TextualNormalExtras ELSE TRUE

EmergencyCondition ==
    /\ Nonempty /\ Has("Emergency") /\ TechnicalEmergency
    /\ IF Corrected /\ ApplySafeguards THEN CandidateAttribution ELSE AttributionOK
    /\ IF Corrected THEN CorrectPeerKey ELSE WrittenEmergencyQuorum
    /\ IF UseSafeguards THEN RequiredEmergencySafeguards ELSE TRUE

Init ==
    /\ m \in MinBio..MaxBio /\ n \in MinPeer..MaxPeer
    /\ faulty \in 0..(IF f < n THEN f ELSE n)
    /\ evidence \in IF Mode = "Safety" THEN EvidenceCases ELSE {GoodEvidence}
    /\ review \in IF Mode = "Safety"
                    THEN {"Pending", "Complete", "EmergencyVerified"}
                    ELSE {IF Mode = "Emergency" \/ LiveTarget = "Emergency"
                          THEN "EmergencyVerified" ELSE "Complete"}
    /\ bioYes \in IF Mode = "Safety" THEN 0..m
                     ELSE IF Mode = "Emergency"
                          THEN {IF BioReading = "Cached" THEN m ELSE 0}
                          ELSE {0}
    /\ honestYes \in IF Mode = "Safety" THEN 0..(n - faulty)
                        ELSE IF Mode = "Emergency" THEN {n - faulty} ELSE {0}
    /\ faultyYes \in IF Mode = "Safety" THEN 0..faulty ELSE {0}
    /\ IF Mode = "Emergency" THEN faulty = 0 ELSE TRUE
    /\ IF Mode = "Liveness"
       THEN /\ (n - faulty) * TauDen >= n * TauNum
            /\ IF QuorumReading = "Majority"
               THEN n - faulty >= (n \div 2) + 1 ELSE TRUE
       ELSE TRUE
    /\ phase = (IF Mode = "Emergency" THEN "setup" ELSE "ready")
    /\ route = "none" /\ trust = 90 /\ anomalies = 0
    /\ panelEpoch = 0 /\ certificateEpoch = 0 /\ sawReset = FALSE

Execute(which) ==
    /\ phase = "ready" /\ certificateEpoch = panelEpoch
    /\ CASE which = "normal" -> NormalCondition
         [] which = "emergency" -> EmergencyCondition
         [] OTHER -> GateReading = "Probability" /\
                     ~(NormalCondition \/ EmergencyCondition)
    /\ phase' = "executed" /\ route' = which
    /\ UNCHANGED <<m, n, faulty, bioYes, honestYes, faultyYes, evidence, review,
                    trust, anomalies, panelEpoch, certificateEpoch, sawReset>>
ExecuteNormal == Execute("normal")
ExecuteEmergency == Execute("emergency")
ExecuteUncertified == Execute("uncertified")

(* A driver step exposes failed enablement after Init, so TLC prints complete
   state counts as well as its counterexample. It changes no protocol input. *)
PrepareEmergency ==
    /\ phase = "setup" /\ phase' = "ready"
    /\ UNCHANGED <<m, n, faulty, bioYes, honestYes, faultyYes, evidence, review,
                    route, trust, anomalies, panelEpoch, certificateEpoch, sawReset>>

VoteBio ==
    /\ Mode \in {"Liveness", "Reset"} /\ phase = "ready" /\ bioYes < m
    /\ IF (Mode = "Emergency" \/ LiveTarget = "Emergency") /\
          BioReading # "Cached" THEN ~Has("Incapacity") ELSE TRUE
    /\ bioYes' = bioYes + 1
    /\ UNCHANGED <<m, n, faulty, honestYes, faultyYes, evidence, review,
                    phase, route, trust, anomalies, panelEpoch, certificateEpoch, sawReset>>
VoteHonest ==
    /\ Mode \in {"Liveness", "Reset"} /\ phase = "ready" /\ honestYes < n - faulty
    /\ honestYes' = honestYes + 1
    /\ UNCHANGED <<m, n, faulty, bioYes, faultyYes, evidence, review,
                    phase, route, trust, anomalies, panelEpoch, certificateEpoch, sawReset>>
Adversary ==
    /\ phase = "ready" /\ faultyYes' \in 0..faulty
    /\ UNCHANGED <<m, n, faulty, bioYes, honestYes, evidence, review,
                    phase, route, trust, anomalies, panelEpoch, certificateEpoch, sawReset>>

Anomaly ==
    /\ phase = "ready"
    /\ IF anomalies = 0
       THEN /\ anomalies' = 1 /\ trust' = IF trust = 0 THEN 0 ELSE 9
            /\ UNCHANGED <<phase, bioYes, honestYes, faultyYes, review,
                            panelEpoch, certificateEpoch, sawReset>>
       ELSE /\ anomalies' = 0 /\ trust' = 0 /\ phase' = "audit"
            /\ bioYes' = 0 /\ honestYes' = 0 /\ faultyYes' = 0
            /\ review' = "Pending" /\ panelEpoch' = 1 - panelEpoch
            /\ sawReset' = TRUE /\ UNCHANGED certificateEpoch
    /\ UNCHANGED <<m, n, faulty, evidence, route>>
ConsistentObservation ==
    /\ phase = "ready"
    /\ trust' = IF trust = 0 THEN 9 ELSE 90
    /\ anomalies' = IF ResetReading = "Consecutive" THEN 0 ELSE anomalies
    /\ UNCHANGED <<m, n, faulty, bioYes, honestYes, faultyYes, evidence, review,
                    phase, route, panelEpoch, certificateEpoch, sawReset>>
FullAudit ==
    /\ Mode \in {"Liveness", "Reset"} /\ phase = "audit" /\ review' =
         IF LiveTarget = "Emergency" THEN "EmergencyVerified" ELSE "Complete"
    /\ certificateEpoch' = panelEpoch /\ phase' = "ready"
    /\ UNCHANGED <<m, n, faulty, bioYes, honestYes, faultyYes, evidence,
                    route, trust, anomalies, panelEpoch, sawReset>>

Next == PrepareEmergency \/ ExecuteNormal \/ ExecuteEmergency \/ ExecuteUncertified \/
        (Mode \in {"Liveness", "Reset"} /\
         (VoteBio \/ VoteHonest \/ Adversary \/ FullAudit \/
          ((Mode = "Reset" \/ EnvironmentReading = "Anomalies") /\
           (Anomaly \/ ConsistentObservation))))

Spec == Init /\ [][Next]_vars /\
        WF_vars(ExecuteNormal) /\ WF_vars(ExecuteEmergency) /\
        WF_vars(VoteBio) /\ WF_vars(VoteHonest) /\ WF_vars(FullAudit) /\
        WF_vars(PrepareEmergency)

TypeOK ==
    /\ m \in MinBio..MaxBio /\ n \in MinPeer..MaxPeer
    /\ faulty \in 0..n /\ faulty <= f
    /\ bioYes \in 0..m /\ honestYes \in 0..(n - faulty) /\ faultyYes \in 0..faulty
    /\ evidence \subseteq EvidenceNames
    /\ review \in {"Pending", "Complete", "EmergencyVerified"}
    /\ phase \in {"setup", "ready", "audit", "executed"}
    /\ route \in {"none", "normal", "emergency", "uncertified"}
    /\ trust \in {0, 9, 90} /\ anomalies \in 0..1
    /\ panelEpoch \in 0..1 /\ certificateEpoch \in 0..1 /\ sawReset \in BOOLEAN
    /\ BiologicalSet \intersect InterestedHumans = {} /\ Incumbent \notin PeerSet
    /\ FaultyPeers \subseteq PeerSet

(* These keys are independently stated intended requirements. In particular,
   the emergency biological key is explicit unanimous approval in all variants. *)
TwoKeySafety == phase = "executed" =>
    IF route = "emergency"
    THEN ExplicitBiologicalClearance /\ CorrectPeerKey
    ELSE BioKeyNormal /\ NormalPeerKey
NoSingleClass == phase = "executed" => BioCount > 0 /\ PeerYes > 0
ByzantineSafety == phase = "executed" =>
    IF ByzantineReading = "PeerQuorum"
    THEN honestYes > 0
    ELSE ~(BioCount = 0 /\ honestYes = 0 /\ faultyYes > 0)

(* State-local existential action reachability, checked for every bounded size.
   Emergency mode fixes a real emergency, all independent evidence, unanimous
   honest peers, no faulty peers, and clearance according to the chosen reading. *)
EmergencyReachable == phase = "ready" => ENABLED ExecuteEmergency
NeverEmergency == route # "emergency"
Liveness == <>(phase = "executed")
NormalLiveness == <>(route = "normal")
EmergencyLiveness == <>(route = "emergency")
DecisionSafety == phase = "executed" => DecisionOK
SignatureSafety == (phase = "executed" /\ route = "normal") => SignatureValid
EmergencySafeguards == (phase = "executed" /\ route = "emergency") =>
    /\ Has("Incapacity") /\ ExplicitBiologicalClearance /\ DecisionOK
    /\ Has("Integrity") /\ ~Has("Manufactured")
TrustResetSafety == phase = "audit" =>
    /\ trust = 0 /\ bioYes = 0 /\ honestYes = 0 /\ faultyYes = 0
    /\ review = "Pending" /\ certificateEpoch # panelEpoch
FreshPanelSafety == phase = "executed" => certificateEpoch = panelEpoch
NeverReset == ~sawReset
TrustDoesNotRiseOnAnomaly == [][Anomaly => trust' <= trust]_vars
=============================================================================
