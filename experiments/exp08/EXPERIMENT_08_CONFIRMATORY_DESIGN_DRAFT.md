# Experiment 08 confirmatory design — pre-registration DRAFT ONLY

**Status: Not frozen, not externally registered, no confirmatory seeds evaluated.** Do not label this as an independently preregistered study.

## Proposed falsifiable hypothesis
Under equal data and compute budgets, topologically evolvable recurrent controllers will outperform the strongest preregistered nonrecurrent and model-based baselines on adaptation to unseen changes of action dynamics in at least two independently engineered environment families. This is a claim about performance and transfer, **not about consciousness**.

## Critical null alternatives
- A one-step motor-effect comparator or a Bayesian state estimator matches or exceeds performance.
- Apparent benefits are driven by extra parameter count, privileged sensors, or unequal tuning budgets.
- Gain occurs only in the training world; performance collapses under sensor loss, delayed actions, and action-independent environmental changes.
- Mutation of recurrent topology itself adds nothing beyond fixed recurrence or explicit recent history.

## Needed controls
Random, greedy, one-step comparator, Bayesian filter, explicitly history-equipped nonrecurrent controller, fixed-topology recurrent network, topology-mutating recurrent network, random-selection evolutionary search, and no-inheritance control with de novo topology allowed. Use comparable information and compute budgets; disclose any mismatch. Independently inspect environmental randomization and accidental leakage.

## Design locks (to complete before registration)
- Fully specified primary endpoint (mean held-out food per step adjusted for cost, or normalized transfer score) and clinically/physically meaningful threshold.
- Independent population as analysis unit; uncertainty across independent evolution runs, never episodes as independent samples.
- Predefined 1D and separately authored 2D families including explicit positive and negative transfer interventions.
- Clearly separated development seeds from **as-yet-ungenerated** confirmatory seeds.
- Training regime, number of generations/population size, computation per candidate, tuning allowances, seeds, stopping, missing outputs and correction for multiple primary comparisons.
- Independent replication, reproducible environment and full citations to foundational evolutionary robotics and internal forward model research.

## Recommended sequence
1. Share draft and this negative pilot with an evolutionary robotics researcher for critique.
2. Implement matched nonrecurrent history, Bayesian and evolved architectures with a common evaluation harness.
3. Conduct pilot/power study on development seeds only.
4. Register protocol with an independently timestamped service (AsPredicted or journal Registered Report) BEFORE any confirmatory test run.
5. Run confirmatory seeds once without tuning; publish favorable and unfavorable findings equally.

No hypothesis about first-person subjective experience is tested with these simulations.
