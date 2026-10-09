# Emergence Lab — Study 09: evolution of action-conditioned self/world representations

**Version:** 0.1 (9 October 2026) · **Status:** DEVELOPMENT DESIGN / EXTERNAL REVIEW REQUEST · **NOT PREREGISTERED, NOT EXECUTED**.

This document defines an implementable, falsifiable scientific study. Numerical sample size, minimum meaningful effect, statistical test, environment code and exact benchmarks are **deliberately not frozen**. The study does **not** measure subjective experience, phenomenology, or consciousness. Do not reuse any Experiment 01–08 seeds as confirmatory observations.

## 1. Narrow research question

In a population of agents with mutable recurrent controllers, does selection on task reward alone lead to **reusable action-conditioned latent state** that carries information about the agent's own changing action consequences *as distinct from exogenous changes*—without an engineered hidden-motor-state target, engineered prediction-error feature, explicit self/world factorization, or true-cause label?

The phrase **functional self/world representation** is operational, NOT an assertion about introspection, an autobiographical self, consciousness, or a uniquely identifiable factorization. A generic action-conditioned world model might suffice and should be called that if the evidence warrants it.

## 2. Reasons previous studies are insufficient

- Exp07 evolved weights in a supplied recurrent architecture with an engineered action-effect feature. Post-hoc Audit08A showed a simple comparator beating the evolved model on all 32 seeds.
- Exp08 early evolved networks failed against hand-coded estimators; fitness was sparse/noisy and training budgets small.
- Exp08C–08D supervised learners received hidden mapping labels (while strong geometric observers received an ontology).
- Exp08E–08J learned from unlabeled action outcomes, but the action channels, update rules, cause families, feature covariance and probing schedule were researcher-selected. Several sophisticated variants failed to beat simple cycles, Bayesian estimators or nearest-neighbor memory.
- The linear 08G/08H causal models are identifiable only under interventions/sensors made available by their designed physics; combined/unmodeled causes and high noise break identification.
- All existing simulations are authored by the same project; CI reproducibility is not independent replication.

**Therefore the prior datasets are DEVELOPMENT DATA ONLY.** Their scores must never be promoted to confirmatory support by changing wording.

## 3. Proposed task domains and observations

Two new environments (not reskins of existing 1D/2D worlds) must be implemented and audited independently before registration.

**Environment A (prospective):** embodied 2D navigation with sensory information through spatially distributed landmarks, collisions and delayed/noisy proprioception; environment-specific causal changes include actuator remapping, transient wind, moving landmarks, intermittent sensor bias, independent combined causes, delays and dropouts. No direct displacement oracle or exact cause flags.

**Environment B (prospective; outside author required):** contact-based object manipulation or a spring-coupled articulated simulated body whose action→observation dynamics are structurally different from A. Use different mechanics, observations and reward structure; include body-side changes and world-side changes. Its author should not tune it using candidate results.

The agent-facing packet can contain **anonymous sensor values and previous motor command only**; no ground-truth coordinates, cause class, motor rotation, simulator seed, intervention time or reset flag. Task rewards and episode termination may of course be available to evolutionary fitness; document separately whether the policy sees reward. Simulator truth is accessible to a separate evaluator only. All controls have the same agent-facing sensor streams.

Interventions must include: stable conditions, changes to the actuator/body, exogenous world forces, sensor-only corruption, simultaneous causes, unfamiliar parameter shifts, and at least one mathematically observationally equivalent case. In the equivalent case, success means *avoiding unjustified attribution*, not pretending identification is possible. **Identifiability must be audited before assessing learned self/world attribution.**

## 4. Candidate and precommitted competing models (details still to freeze)

**Candidate:** controller genotype encoded by a variable graph of generic recurrent units initialized without hand-named 'self', motor polarity, prediction-error or wind dimensions; mutations may add/delete edges, units and weights. Reward-only, heritable, per-population selection. Agent can observe motor-command efference copy, but never precomputed action-effect errors. Explicitly count input units, memory, parameters, synapses, and computation. This still builds in major inductive biases: actions, recurrence, reward, neural activations, evolution algorithm and sensors.

**Strong controls** (minimum): random policy; reactive policy; one-step comparator; Bayesian system identification; nearest-neighbor memory; action-history feedforward policy; fixed-topology recurrent network; topology-evolving recurrent network; random fitness; de-novo/no-inheritance population with the same allowed structural mutations. When controls have privileged structural priors, explain them and report **both** privileged and matched-prior comparisons rather than excluding strong methods.

Selection/optimization budgets and data exposure must be audited at multiple levels: number of episodes, total observation/action transitions, tuning runs, wall-clock/hardware, parameter count and inferential compute. Exact compute matching may not be possible; publish a Pareto frontier and sensitivity analysis rather than asserting fairness falsely. No reward shaping derived from simulator-hidden causal truth in the confirmatory study.

## 5. Operational evidence and falsifiers

A functional action-conditioned internal representation requires **three independent pillars**; reward alone is insufficient.

**Pillar A — Out-of-distribution control advantage:** on both unseen environment families, the evolved candidate beats the *strongest prespecified development-selected comparator*, with a meaningful improvement threshold set before preregistration. Report each environment independently; a good pooled average that hides failure in the other environment does not meet the target. The comparator must be selected on development data, not the future confirmatory data.

**Pillar B — Causal use of latent state:** in counterfactually paired evaluations, lesion or swap the learned recurrent state while controlling all observable inputs and random streams. Measure downstream navigation/control performance. A lesion is a functional intervention, **not proof of a 'self variable'**. Compare with compute-/information-matched memory/history controls and randomized lesions; avoid changing the RNG draw order after an ablation.

**Pillar C — Differentiation under valid interventions:** freeze the controller, collect independent diagnostic trajectories with body-side and external-side perturbations, and train a small *post-hoc* probe exclusively on DEVELOPMENT diagnostic data. Evaluate the probe on truly held-out interventions. Compare with probes over raw sensor/action histories and baseline latent states under matched capacity. In observationally equivalent environments, test calibrated abstention/rejection, not forced class identification. Probe labels are for scientific evaluation, not agent or evolutionary training. Ensure probe capacity cannot manufacture a separation already encoded trivially by known intervention timestamps or artifact flags.

**Null explanations and failure criteria:** elementary model-based inference or KNN solves it equally well; no real transfer; performance advantage due to extra compute, stronger input, hyperparameter search, or seed luck; lesions harm any generic memory similarly; probes reveal only task/time labels; the environment leaks cause identity; candidate collapses under combined causes, dropout or newly authored physics. If any required pillar fails, state that the study **did not establish** a functional self/world representation beyond the specified alternatives. Negative results are publishable as careful computational audits.

## 6. Unit of analysis and prospective statistical plan

Independently initialized **evolutionary populations**, not episodes, neural units, cause scenarios or rollout steps, are the independent units. Follow an independent agent from each population through development-selected and then fixed test conditions. Pair candidate/baseline scores at the population/seed cluster level as appropriate. Environment A and B must each clear its own threshold (conjunctive requirement); define a multiplicity-aware CI/test for any additional co-primary outcomes. The principal effect is the *population-paired difference in held-out transfer reward* on a predeclared reward scale across a predeclared intervention mixture, with no early stopping based on test results.

An additional effect-size gate for the three pillars must be locked after **development-only** pilots. Pilot-based variance, available compute, detectable effect, attrition and power analysis must justify final population count. Predeclare all exclusions and missing-run handling, outlier treatment, CIs, ablations, number of tests, alternative model tuning, outcome aggregation, and whether negative rewards/survival count. Do not specify or generate confirmatory random seeds in this draft. No arbitrary post-hoc p-values should be used as a replacement for registration.

## 7. Scientific quality gates — stop on any failure

1. Review the 01–08 exploratory source/data and explicit comparison against prior art.
2. An outside person implements Environment B and inspects A, including sensor-leakage, seed artifacts, paired counterfactual validity and independent RNG streams.
3. Implement and test all strong baselines; show adequate optimization budgets and developmental sample-size justification. Make task difficulty reasonable but not deliberately ideal for candidate.
4. Freeze code, software versions, training/evaluation distributions, primary estimand, meaningful effect, sampling and all analyses. Preserve a manifest of commit hashes and checksums.
5. Deposit a **third-party timestamped** immutable preregistration (AsPredicted or Registered Report) **before** generating or opening confirmatory seeds/results. A GitHub commit alone is *not* independent preregistration.
6. Obtain explicit study-owner authorization to execute final study. Run exactly once; never retune on the test. Preserve every failed seed and full logs.
7. Commission outside reproduction, literature/novelty and statistical-methods review before journal claims.

## 8. Publication language and stopping point

If the prerequisites are achieved, the permitted claim is task-specific evolutionary emergence of useful action-conditioned computation **relative to preregistered controls**. Whether that computation is novel relative to robotics and machine-learning literature requires expert judgment. **No experimental outcome is defined that could prove phenomenal consciousness or the existence of a subject of experience.**

**Current STOP:** no independently authored second world; no complete fair baselines; no registered analysis, sample size, external methods review or confirmatory dataset. Study 09 is a *proposed study only*, not a run.
