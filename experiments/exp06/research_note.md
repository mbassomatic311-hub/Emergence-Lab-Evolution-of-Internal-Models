# Evolved Action-Outcome Comparison in Minimal Recurrent Agents: An Exploratory Simulation

**Status:** Open computational methods note, not a peer-reviewed paper or proof of consciousness. Prepared 8 October 2026. Authorship and affiliations to be confirmed prior to public distribution.

## Abstract
An elementary prerequisite for distinguishing self-generated from external sensory events is to combine an earlier motor command with a later sensory consequence. We tested whether structural mutation and Darwinian-style selection could produce that ability in agents initialized with no recurrent neural connections. Four-unit neural controllers faced a two-phase ecology in which the current sensory signal alone was uninformative about the hidden source. Recurrent connections were initially absent and could arise through inherited mutations. We analyzed 24 independent evolutionary runs per condition, 300 generations each, against no-recurrence, random-fitness, and no-inheritance controls. The primary outcome was expected survival payoff on a fully specified probability distribution, with additional interventions and independent held-out trials. The mean evolved payoff was 0.1705 (95% bootstrap interval 0.1487–0.1881), compared with 0.0833 under random fitness selection and an analytic ceiling of 0.2100. Mean post hoc source classification AUC was 0.631. These results provide a minimal demonstration of evolved sensorimotor comparison under engineered constraints, not evidence for subjective awareness. Direct conceptual antecedents include corollary discharge and robot self-modeling research.

## Research question and scope
Can inherited mutation and selection create a working action-outcome comparison circuit from initially absent recurrent connections when the organism benefits from distinguishing self-caused and external sensory consequences? The study is a model of evolved **causal sensorimotor integration**, not a measurement of conscious experience, not an origin-of-life simulation, and not an unrestricted open-ended artificial ecology.

## Methods (ADEMP)
**Aims.** Identify the minimal structural condition under which an agent can use its own preceding motor action to make an adaptive decision about an ambiguous event; quantify variance across independent evolutionary histories.

**Data generation.** Each episode samples balanced motor direction c in {−1,+1} and equally likely hidden source z∈{self,external}. Self-generated events agree with c with probability q=0.92; externally generated events are random. At the earlier phase the controller observes c, while at the later phase it observes only the binary sensory event y. The source itself is never an input. Entry earns +1 for self-caused events, −1 for externally caused events; declining earns 0. The design intentionally makes action–event contingency useful for survival.

**Controllers and evolution.** The controller has four nonlinear hidden units. Initial action-to-event recurrent weights are all zero and connection masks all false. Structural mutations can introduce or remove recurrent edges; continuous weights also mutate. Population size 192; 300 generations; 24 elites; 64 eligible parents; other hyperparameters and immutable pre-run checksums in STUDY_PROTOCOL.md and engine.py. Fitness is computed as the exact expected environmental payoff over the four possible (c,y) pairs. There is no backpropagation or explicit self/other classification training. The source enters only the environment/payoff computation.

**Estimands and analysis.** The primary estimand is the mean across 24 fresh, fixed simulation seeds of champion expected payoff, paired to the same genome with recurrence disabled. The analytic maximum is 0.2100 at q=0.92 and no measurement cost. 95% percentile bootstrap intervals resample independent evolutionary seeds 12,000 times. Negative controls separately disable recurrence, randomize fitness-based selection, or prevent genotype inheritance. Held-out Monte Carlo trials per champion: 25,000. Secondary interventions change event reliability to q=0.80, 0.50, and 0.08; shuffle the retained cue; measure post hoc ROC AUC of entry likelihood for latent causal source.

**Study status.** The analysis plan was frozen locally before the 24-seed runs, with SHA-256 hashes, but was NOT externally or prospectively preregistered. Some model choices were informed by pilot runs excluded from this set; findings remain exploratory.

## Results
- Evolved recurrence: mean payoff 0.1705; 95% bootstrap CI [0.1487,0.1881].
- No recurrence: mean payoff 0.0000; random fitness: 0.0833; no inheritance: 0.0000.
- Mean post-hoc hidden-source ROC AUC: 0.631 (chance is 0.5). This reflects information acquired about cause, **not** subjectivity.
- Held-out reliability q=0.80: mean exact payoff 0.1218; uninformative q=0.50: 0.0000; reversed q=0.08: -0.1705.
- When cue memory is shuffled on new episodes, average payoff is 0.0001. Cutting recurrence analytically yields 0.0000.
- Individual evolutionary runs varied; Figure 2 shows the full distribution rather than selecting only successful examples.

## Interpretation
The data support a narrow computational claim: an action-history link can be favored when survival requires integrating temporally separated sensory and motor information. The same controller loses that advantage when recurrence is removed, cues are scrambled, or the environment ceases to carry useful motor-contingent information. This is a minimal computational reenactment of an established concept: a corollary-discharge/efference-copy-like comparison. The model does not demonstrate a full body model, subjective feeling, personal identity, or an evolutionary origin of consciousness.

## Major limitations
1. The task was designed so the action–outcome comparison matters. Its evolution cannot establish that real ecology necessarily produces subjective awareness.
2. Even though recurrent links were initially absent, neural units, mutation operators, survival payoffs, timing and sensory representations were specified by the experimenter.
3. The controller has only two observations and a binary action. It has no metabolism, body morphology, changing physical world or genuinely self-directed sensor exploration.
4. Analytical selection fitness uses the full known environment distribution rather than individual noisy lifetime survival; stochastic uncertainty is added only in held-out evaluation.
5. The phenomenon overlaps extensively with existing corollary discharge, internal-model and evolutionary robotics literature. Original scientific novelty has not been established.
6. A linear or nonlinear readout decoding causal source from internal state cannot establish phenomenal consciousness.
7. The local protocol was not published before the run and does not have the status of external preregistration or independently verified replication.

## Publication assessment
Suitable for open sharing as an **exploratory computational note with code**, but not yet suitable to claim a new theory of consciousness or a peer-reviewed biological discovery. A stronger research submission would need external critique, replication by someone independent, ecologically richer simulations, independent controller architectures, comparison to published models, robustness to altered evolutionary parameters, and a demonstrably novel prediction.

## References
- Crapse, T.B. & Sommer, M.A. (2008). Corollary discharge across the animal kingdom. *Nature Reviews Neuroscience* 9, 587–600. doi:10.1038/nrn2457.
- Bongard, J., Zykov, V. & Lipson, H. (2006). Resilient machines through continuous self-modeling. *Science* 314, 1118–1121. doi:10.1126/science.1133687.
- Tanaka, T. & Imamizu, H. (2025). Sense of agency for a new motor skill emerges via the formation of a structural internal model. *Communications Psychology* 3, 70. doi:10.1038/s44271-025-00240-7.
- Morris, T.P., White, I.R. & Crowther, M.J. (2019). Using simulation studies to evaluate statistical methods. *Statistics in Medicine* 38, 2074–2102. doi:10.1002/sim.8086.
- Center for Open Science (2025). Simulation Studies Preregistration Template and OSF registration guidance. https://help.osf.io/article/330-welcome-to-registrations.
