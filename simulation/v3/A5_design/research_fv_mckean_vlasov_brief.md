# Scoping Brief: Viability of a Certified FV Method via McKean-Vlasov Theory

## 1. The Exact Mapping
The committed offline estimator runs the Fleming-Viot (FV) route (`simulate` in `offline_estimator.py`) through the following discrete-time process:
*   At each step, the killing criterion is `reproductive_support(state)`.
*   Within each of the independent groups, killed particles are replaced by uniform resampling from the survivors in that same group.
*   If a group collapses entirely, the trajectory terminates.
*   After copying the state of the chosen survivors, the system advances with `independent=True`, providing each particle with independent environmental draws.
*   The transitions used to fit the continuation values (the `before` and `after` bins) are recorded pre-resampling.

Mathematically, this maps exactly to a discrete-time Feynman-Kac interacting particle system, specifically a Moran-type mean-field particle approximation. It approximates the non-linear Markov chain (the McKean-Vlasov limit) that describes the law of the underlying agent-based model conditioned on survival.

## 2. The Quantity We Must Certify
Amendment A4 evaluates the Bellman residual as a per-cell mean. In `continuation.py`, `fit_transitions` aggregates these residuals across all time steps and across all particles within the training groups.
Therefore, the quantity we must certify is not a single-time average but a time-occupation average along the paths of the interacting particle system. This distinction is critical because single-time error bounds typically grow exponentially with the time horizon. To certify an aggregate over hundreds of steps without exponential degradation, the chosen theorems must provide concentration or error bounds that are uniform in time.

## 3. Candidate Theorems
The following are candidate mathematical results for this analysis:

*   **Non-asymptotic concentration inequalities for mean-field particle models** (e.g., Del Moral, 2004, "Feynman-Kac Formulae", unverified (from memory)).
    *   *Statement:* The probability that the particle system's empirical measure deviates from the limiting McKean-Vlasov measure by more than a given margin is exponentially bounded in the number of particles.
    *   *Assumptions:* Uniform mixing of the underlying Markov transition kernel, and strict upper and lower bounds on the potential function (the survival probability).
    *   *Constants:* Without strong mixing, the constants scale exponentially with time.
    *   *Coverage:* It covers our time-occupation quantity if extended to path-space or historical measures.

*   **Propagation of chaos with explicit rates, uniform in time** (e.g., Del Moral and Miclo, 2000, "Branching and Interacting Particle Systems", unverified (from memory)).
    *   *Statement:* The total variation distance between the joint law of a fixed number of particles and the product law of independent conditioned processes is bounded by a constant divided by the total number of particles.
    *   *Assumptions:* Strong ergodicity, often requiring a strictly positive Dobrushin ergodic coefficient for the transition kernel.
    *   *Constants:* Explicitly depend on the mixing rates and the Dobrushin coefficient.
    *   *Coverage:* Useful for bounding the within-group particle covariance, which could establish an effective sample size.

*   **Bias bounds of order 1/N** (unverified (from memory)).
    *   *Statement:* The expected bias of the unnormalized particle measure is bounded by a constant over the number of particles.
    *   *Assumptions:* Regularity of the test functions and bounded transitions.
    *   *Constants:* Depend on the supremum of the test functions.
    *   *Coverage:* Covers the bias of the mean residual, but falls short of providing the concentration inequalities needed for a high-confidence certificate.

*   **FV results for quasi-stationary distributions on discrete or countable spaces** (e.g., Asselah, Ferrari, Groisman, 2011, "Quasi-stationary distributions and Fleming-Viot processes", unverified (from memory)).
    *   *Statement:* The empirical measure of the FV process converges to the quasi-stationary distribution (QSD) as the number of particles grows.
    *   *Assumptions:* Irreducibility and aperiodicity on the state space, ensuring a unique QSD.
    *   *Constants:* Asymptotic; finite-N rates are rarely explicit for complex state spaces.
    *   *Coverage:* Covers the invariant measure limit, but does not give a finite-sample bound for our specific time-averaged residuals.

*   **Covariance bounds between particles** (unverified (from memory)).
    *   *Statement:* The covariance between the histories of any two interacting particles scales as 1/N.
    *   *Assumptions:* Strong mixing.
    *   *Constants:* Depend on the spectral gap or mixing time.
    *   *Coverage:* Could theoretically bound the variance of the group-level residual estimates.

## 4. The Constants
To leverage uniform-in-time bounds, the theorems require specific stability and mixing quantities, such as the Dobrushin ergodic coefficient, a spectral gap, or bounded potential ratios (maximum versus minimum survival probability across states).
*   **(a) The full agent-based model:** These constants cannot be computed or bounded practically. The state space is immense, and the transition matrix is extremely sparse. Transitions between arbitrary states in a single step are impossible, meaning the Dobrushin coefficient is zero. Any theoretical lower bound on mixing over multiple steps would be so small that it would render the required particle count astronomically large.
*   **(b) The demographic core:** For the reduced demographic space, these quantities can be computed exactly. The project has already certified a QSD with a simple dominant Perron root (e.g., in `spectral.py` and the P5 and W1C certifications). The spectral gap exists and is bounded, meaning the constants are well-behaved, but this applies only to the core, not the full agent-based model evaluated by the instrument.

## 5. Designs to Compare
The following designs offer different paths forward:

*   **(a) A certificate from a particle concentration inequality with explicit constants.**
    *   *Viability:* Not viable.
    *   *Cost:* Infinite development and X2 hours. Bounding the required mixing constants for the full agent-based model is intractable.
    *   *Blind Certification:* Would require an algorithmic check of the full model's spectral gap, which cannot be executed blind or otherwise.

*   **(b) Independence across groups plus a certified bound on within-group dependence.**
    *   *Viability:* Not viable.
    *   *Cost:* Infinite development and X2 hours.
    *   *Blind Certification:* Deriving an effective sample size multiplier relies on the same intractable uniform mixing bounds to prove that the 256 particles do not fully correlate over the long measurement horizon.

*   **(c) A different validation design: independent single-particle conditioned sampling.**
    *   *Viability:* Viable only if the target survival events are not too rare over the 500-step horizon. Instead of FV resampling, we would run completely independent trajectories and compute the residuals strictly over the subset that survives.
    *   *Cost:* High X2 hours. If survival is rare, generating enough independent surviving paths to pass the Bernstein screen would require massive computational resources. Development cost is low.
    *   *Blind Certification:* Straightforward. It uses the existing empirical Bernstein tests over truly independent units.

*   **(d) Keeping the asymptotic label.**
    *   *Viability:* Highly viable.
    *   *Cost:* Zero X2 hours and zero development.
    *   *Blind Certification:* The current implementation properly bounds the sample variation of independent groups using delta-method and Fieller intervals with Student t critical values, explicitly declaring them as asymptotic diagnostics rather than strict finite-sample certificates.

## 6. Recommendation and Next Concrete Step
**Recommendation:** Abandon the McKean-Vlasov certification route and retain the asymptotic label for the FV tier.
The theoretical machinery required to establish a finite-sample certificate for a mean-field particle model demands uniform-in-time mixing constants. While these are computable for the demographic core, they are completely intractable for the full, high-dimensional agent-based model. Attempting to bound them would yield theoretical constants so small that the required particle count would be practically infinite.

**Next Concrete Step:** Accept the asymptotic status of the FV tier as currently designed in amendment A4. Do not alter the estimator or validation code. Proceed with the planned pre-registered runs using the existing blind diagnostics.
