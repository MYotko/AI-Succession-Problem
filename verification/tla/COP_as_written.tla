-------------------------- MODULE COP_as_written --------------------------
EXTENDS Integers, FiniteSets, TLC
CONSTANTS ApplySafeguards, MinBio, MaxBio, MinPeer, MaxPeer, f,
          Mode, EvidenceMode, GateReading, BioReading, AttributionReading,
          ReviewReading, TrustReading, ResetReading, EnvironmentReading,
          QuorumReading, TauNum, TauDen, BioTauNum, BioTauDen,
          ByzantineReading, TransitionKind, LiveTarget
VARIABLES m, n, faulty, bioYes, honestYes, faultyYes, evidence, review,
          phase, route, trust, anomalies, panelEpoch, certificateEpoch, sawReset
INSTANCE COP_core WITH Corrected <- FALSE
=============================================================================
