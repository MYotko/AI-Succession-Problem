# Reviewer assessment of the FV and McKean–Vlasov scoping brief

**By:** Claude Code, 2026-09-29. **Brief reviewed:** `FV_MKV_SCOPING_BRIEF.md`, by Gemini. **Status:** exploratory research, not registered.

## Verdict on the brief

**Sound on its main point.**
- The mapping is right. The FV route is a discrete-time Feynman–Kac mean-field particle system of Moran type: only killed particles are replaced, by copies of survivors. Its limit is the McKean–Vlasov process conditioned on survival.
- The quantity is right. It is a time-occupation average along the particle system, so any certificate needs concentration bounds that are uniform in time.
- **The main obstacle is right.** Uniform-in-time bounds need mixing or stability constants for the full agent-based model, and those cannot credibly be computed or bounded. A certificate for the FV tier along this line is not viable for the full model.

**Three corrections:**
1. **"The Dobrushin coefficient is zero" does not settle the question by itself.** That is true of the one-step coefficient for sparse transitions. But the theory works with multi-step minorization conditions, and the brief asserts rather than shows that those are hopeless. The conclusion probably holds; the argument is incomplete.
2. **"Constants computable exactly for the demographic core" overstates it.** The project certified a simple dominant Perron root. A spectral-gap or mixing bound also needs control of the rest of the spectrum, which has not been established.
3. **Design (c) conditions on the wrong event.** Conditioning each trajectory on survival over the whole horizon is not needed. That leads to the design below.

## A design the brief missed: validate FV-route tables on independent plain trajectories

The Bellman residual at a living state does not depend on how that state was reached (the Markov property). A4's plain tier already validates on living sources only. So an FV-route table can be validated on independent plain trajectories, restricted to living sources, with the same certified empirical Bernstein test and table-conditional width as the plain tier. Every trajectory is an independent unit, so no particle dependence arises.

**What it certifies:** the mean residual per cell under the plain occupancy law. That is a different law from the FV conditioned law, not a weaker version of it.

**Why that law may be the better one:**
- The reruns run plain dynamics with allocation, not FV, and look tables up at the states they actually reach.
- A4's census floor already uses the plain law, even for FV rows.

So certifying under the plain law may match how the tables are used better than the FV law does.

**The limit:** FV-route kernels are the ones where fewer than half of the plain paths survive the full window. Cells that only the conditioned regime populates would stay uncertified. Those would either stay under the asymptotic label or be unpublished, and the availability floor would show what that costs.

**Cheap to test,** as a planning study like P3 on the 15 FV jobs of P1: plain trajectories, fresh planning seeds, living sources, table-conditional width, global family. Measure the share of cells and visits certified, and the floor. Plain tasks take about 15 minutes per 32 groups. That is about 1 to 2 X2 hours after the A4 run, or a few hours on the workstation.

**If it works,** it would become a new amendment, probably with a two-tier rule for FV rows: certified where plain paths reach, asymptotic elsewhere. That needs its own blind certification and the operator's approval. Nothing changes for the A4 run in progress.

## Verified references

- P. Del Moral, *Feynman–Kac Formulae: Genealogical and Interacting Particle Systems with Applications*, Springer, 2004.
- P. Del Moral and L. Miclo, "Branching and interacting particle systems approximations of Feynman–Kac formulae with applications to non-linear filtering", *Séminaire de Probabilités XXXIV*, Lecture Notes in Mathematics 1729, 2000, 1–145. [Springer](https://link.springer.com/chapter/10.1007/BFb0103798)
- P. Del Moral and E. Rio, "Concentration inequalities for mean field particle models", *Annals of Applied Probability* 21(3), 2011, 1017–1052. It generalizes Hoeffding, Bernstein and Bennett inequalities to interacting particle systems, which is the tool a certificate would need; the constants depend on stability. [Project Euclid](https://projecteuclid.org/euclid.aoap/1307020390)
- A. Asselah, P. A. Ferrari and P. Groisman, "Quasistationary distributions and Fleming–Viot processes in finite spaces", *Journal of Applied Probability* 48(2), 2011, 322–332. The brief gave the title without "in finite spaces". [Project Euclid](https://projecteuclid.org/euclid.jap/1308662630)
- B. Cloez and M.-N. Thai, "Quantitative results for the Fleming–Viot particle system and quasi-stationary distributions in discrete space", *Stochastic Processes and their Applications* 126(3), 2016, 680–702. It gives uniform-in-time convergence with explicit rates, from two-particle correlation estimates. [arXiv 1312.2444](https://arxiv.org/abs/1312.2444)
- **Relevant, and not cited by the brief:** "The particle approximation of quasi-stationary distributions: concentration bounds in the uniform case", arXiv 2412.15820 (2024). Worth reading if the particle route is ever reopened, for example for the demographic core. [arXiv](https://arxiv.org/pdf/2412.15820)

## Recommendation

1. Keep the FV tier's asymptotic label for A4, as the brief says.
2. Do not pursue a particle-concentration certificate for the full model.
3. **Next, after the A4 run:** a small non-registered planning study of plain-trajectory validation for FV-route tables. It is cheap, and if it works it could certify much of the FV tier under the law the reruns actually use.
