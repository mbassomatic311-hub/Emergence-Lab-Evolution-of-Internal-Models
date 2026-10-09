# Experiment 06 — analysis plan frozen before held-out simulations

Date written: 2026-10-08 (system date; machine timestamps may differ). Version 1.
**Status: internal prospective analysis plan, NOT publicly preregistered.**

## Claim being examined
Whether an inherited artificial neural controller initially without recurrent links can evolve an action-outcome comparator when differential survival favors interpreting event origins.

NO claim is made that agents possess consciousness, selfhood, beliefs, or subjective experience.

## Aims and data-generating mechanism (ADEMP)
- Each episode first provides a balanced binary motor command `c` (+1/-1). The agent's movement produces a sensory consequence `y` with probability q=.92 of agreeing with c. Alternatively, an external event produces y independent of c. Hidden source z is balanced 50:50 and **never passed to the controller**.
- The controller receives c at t=0 and y at t=1, never simultaneously. It chooses a risky resource: entry yields +1 survival payoff for a self-produced event and −1 for an external event; avoiding yields 0. The objective does not explicitly reward identity/source classification.
- A 4-unit nonlinear recurrent controller passes t=0 hidden activity to t=1 through an evolving matrix. All 16 recurrent connections are *absent initially* and can emerge by mutation. No hard-coded action-outcome match comparison is supplied. Input, bias, and readout weights are also inherited/mutated.
- Tournament-like truncation selection, genome cloning, small independent structural mutations, no gradient fitting, no target labels. This is a deliberately minimal, artificial ecology, not a biological evolutionary reconstruction.

## Primary tests
1. 24 fixed held-out independent evolution seeds: 100003 + 101*i, i=0..23; 300 generations, 192 controllers/generation.
2. Primary estimand: mean across seeds of **exact expected survival payoff** of each champion on the original generative distribution, compared with the *same champion* with evolved recurrence clamped to zero.
3. Secondary: mean champion payoff under q=.80 (same causal relationship), q=.50 (uninformative), q=.08 (reversed contingency), and after independently shuffling the cue retained in memory at testing.
4. Negative controls: populations with recurrence forbidden throughout evolution; populations undergoing random fitness selection; and populations whose descendants do not inherit their parents' genotype. Same seeds and generation budgets. Report distributions for all, including failure cases.
5. Neural measurement: post-hoc ROC AUC of the agents' entry propensity for the hidden source on independent trials. No source supervision during evolution. This is only a proxy for **information about causal origins**, NOT awareness.
6. 95% bootstrap intervals over **independent evolution seeds**, with seed 58333. Report effect sizes. Exploratory p-values, if any, described as simulation comparisons rather than population inference about biology.

## Analytical sanity checks and performance measures
- Source identity is independent of a single instantaneous cue or event individually. If recurrence is absent, expected net survival payoff is exactly zero; with an ideal match detector and q=.92, bound is .21.
- Monte Carlo held-out evaluation: 25,000 fresh trials/champion, independent random streams. Recheck numerical payoff against analytically computed expectation; allow <= .04 deviation because source sampling introduces noise.
- Use nonzero recurrence as a structural measure, not evidence of self-awareness. Inspect evolved responses to all 4 cue/event pairs.
- Test deterministic reproduction, source randomization, unchanged negative controls, input isolation, and artifacts before reporting.

## Publication standard
Any write-up must declare this a **minimal computational demonstration of evolved sensorimotor comparison**, not a theory proven or the origin of consciousness. The design is not externally preregistered and is based on discussion/pilot work; negative results remain reportable. Materially overlapping studies: Crapse & Sommer (2008) corollary discharge; Bongard et al. (2006) self-modeling; Tanaka & Imamizu (2025) agency/internal-model learning. Any academic publication requires novel question, literature review, independent audit, robustness over varied worlds, public code and data, and expert review.

## Frozen configuration
- Population 192; 300 generations; elite count 24; parent pool 64; hidden nodes 4.
- Training q=.92; structural mutation probability .045 and removal .008 per connection/child; connection cost .0008 per active link/fitness evaluation.
- Input weight mutation probability .23, SD .32; initial weight SD .8.
- Confirmatory label is inappropriate absent independent public preregistration; call tests **held-out within-session**.
