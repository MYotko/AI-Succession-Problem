# CQ-02: Precision/Accuracy Mathematical Binding

**Status:** In progress
**Dependencies:** CQ-01
**Opened:** April 2026

## Statement

The Bootstrap defence layer (CQ-01) uses substrate convergence as its
validation mechanism. Convergence is a precision question: do the substrates
agree tightly enough that their agreement is meaningful? But precision alone
does not validate accuracy. High precision with low accuracy — multiple
substrates agreeing tightly on a wrong answer — is the most dangerous failure
mode, because the convergence itself becomes false evidence of correctness.

**The question:** Can precision and accuracy be *mathematically bound* such
that a failure in either dimension produces a detectable inconsistency with
the other, rather than leaving them as two independent checks that could each
be attacked separately?

A resolution would need to provide:

- A mathematical relationship between precision and accuracy derived from the
  framework's own equations (not stipulated from outside)
- A checkable coupling condition whose satisfaction requires both precision
  and accuracy simultaneously
- A diagnostic signature: what the four quadrants (high/low precision ×
  high/low accuracy) look like and how the defence layer distinguishes them
- Adversarial robustness: an adversary who spoofs one dimension must also
  spoof the other in internally consistent ways, raising the computational or
  epistemic cost of attack

## Thread

### Reframing from threshold question to binding question

Original framing asked "how much divergence is acceptable?" — a tolerance band
question. Recognized as a precision-vs-accuracy problem rather than a
single-dimensional threshold problem. The two dimensions fail independently
and require different detection machinery.

**Accuracy failure** (high precision, low accuracy): all substrates converge
tightly on the wrong value. Signature of shared specification error or
coordinated compromise. Most dangerous failure mode.

**Precision failure** (low precision, high accuracy): substrates land in
approximately the right region with wide spread. Recoverable as measurement
uncertainty if acceptable, but not strong validation.

**Both failures simultaneously** (low precision, low accuracy): framework
error or incoherent specification. This is the quadrant where the defence
layer earns its keep — a single-substrate approach cannot distinguish this
from noisy-but-correct derivation, but heterogeneous verification can.

### Candidate structures for the binding

Three structures sketched, ordered from most tractable to most ambitious:

**Structure 1: Precision-weighted accuracy.** The structural consistency check
is evaluated against the full distribution of substrate outputs rather than a
point estimate. Predicted structural behaviors (phi's nonlinear response curve,
phase transition boundaries, yield condition firing thresholds) are functions
of the parameter values with known derivatives. A small parameter perturbation
produces a predictable structural-response perturbation. Check: does the
spread of predicted structural behaviors match the spread you'd expect from the
parameter uncertainty propagated through the framework's sensitivity analysis?
Mismatch indicates precision and accuracy are inconsistent.

**Structure 2: Invariant ratios.** The framework has multiple parameters that
interact through U_sys. Any correct derivation should produce not just the
parameters but specific ratios and products among them that are invariant
under the framework's mathematical structure. An adversary spoofing one value
must also spoof all interacting values in coordinated ways that preserve the
ratios. The more interaction terms the framework has, the more constraints
must be satisfied simultaneously. This is similar in spirit to how
cryptographic protocols use multiple algebraic constraints to make forgery
computationally infeasible.

**Structure 3: Convergence-as-proof.** Each substrate produces not just
numerical parameters but derivation chains grounded in Shannon entropy,
thermodynamic constraints, and game-theoretic equilibrium conditions. Chains
are compared for logical equivalence independently of whether numerical
outputs match. Two substrates that produce the same number through logically
equivalent derivations provide stronger validation than substrates that
happen to agree numerically. A substrate producing the correct number through
incorrect derivation is caught by chain comparison despite numerical
agreement. Uses formal verification machinery (proof-carrying code, certified
compilation, interactive theorem provers).

### Structure 2 concrete sketch (phi and alpha as test case)

Phi and alpha interact through L(t) even though they appear in different
parts of U_sys. Phi scales L(t)'s contribution to U_sys directly. Alpha
governs theta_tech via `exp(-alpha * runaway_term)`, and theta_tech is a
multiplicand in L(t). So alpha propagates to L(t), which then gets scaled by
phi in U_sys.

In the regime where both parameters are active (high capability → large
runaway_term, sub-viable reproduction rate → phi's extinction buffer matters),
consider the derivatives of U_sys with respect to each parameter:

- dU_sys/d(phi) is proportional to L(t)
- dU_sys/d(alpha) is proportional to phi × (partial of L(t) w.r.t. alpha),
  which is proportional to theta_tech × runaway_term

The ratio dU_sys/d(phi) ÷ dU_sys/d(alpha) is an expression depending on L(t),
phi, runaway_term, and theta_tech — but *not* on the specific values the
substrates derived for phi and alpha independently. The ratio is determined
by the framework's structure and the system state at evaluation time.

**This provides a binding condition.** Substrates that agree on phi and alpha
numerically but disagree on the sensitivity ratio are producing
numerically-correct outputs through incorrect derivational procedures — the
accuracy failure that hides behind convergence. Substrates that disagree on
phi and alpha but agree on the sensitivity ratio within tolerance are probably
producing precision failures the framework's equations would smooth out at
higher orders.

More strongly: the sensitivity ratio is a framework prediction about how a
correctly-derived parameter pair should behave under perturbation. The
prediction is independently checkable at any substrate by running the
substrate's values through the framework's equations and measuring the ratio.
Convergence on parameters is necessary; convergence on sensitivity ratios is
a stronger check; the two together form a binding where precision failures in
one dimension produce detectable inconsistencies in the other.

### Open sub-questions for Structure 2

- Are sensitivity ratios state-invariant, or do they vary with system state?
  Intuition: they vary (because L(t) varies and the parameters interact with
  state-dependent quantities), but the variation should follow a specific
  functional form determined by the framework's equations. If variation
  matches the predicted form, the substrate is producing a coherent derivation.
- What tolerance bands apply to the ratio check? This recurses the precision
  question at the ratio level rather than the parameter level — still a real
  question, but applied to a quantity with stronger structural constraints.
- Does Structure 2 extend to parameters beyond phi and alpha? The framework
  has rho, lambda, mu, and the inverse scarcity weights, all of which
  interact through U_sys. The binding should scale with the number of
  interaction terms, strengthening as more parameters are included.
- Can Structure 2 be combined with Structure 1 for additional robustness?
  The two are not mutually exclusive — precision-weighted accuracy checks and
  invariant ratio checks can run in parallel.

### Next work

- Work out the phi/alpha sensitivity ratio symbolically
- Verify it behaves as claimed under perturbation
- Check whether it's state-invariant or state-dependent in predictable ways
- Determine whether the result generalizes to the full parameter set
- If structure 2 fails on inspection, try structure 1 as fallback
