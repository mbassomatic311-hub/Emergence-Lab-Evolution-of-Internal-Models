# Experiment 06: independent-style methodological audit and post-hoc sensitivity check

**Status: post-hoc audit of an exploratory computational study; not independent replication, not peer review, not evidence of consciousness.**

## Verified, narrowly framed finding

A deliberately engineered two-stage sensorimotor task favors neural controllers that combine an earlier motor-command signal with a subsequent ambiguous sensory event. Across 24 evolutionary seeds (300 generations each), the mean exact expected payoff of the best final-generation controller was 0.1705, versus 0.0833 for random-fitness selection. Mean paired difference was 0.0872 (95% bootstrap interval 0.0611–0.1130). Original 24-seed evolved-to-no-recurrence and evolved-to-same-genome-memory-disabled comparisons were positive in all runs; the latter reduction to zero also follows analytically from the task design. Mean causal-source ROC AUC of selected controllers was 0.631, versus chance 0.5.

These quantities concern **synthetic survival payoffs and action/event correlations**. They are not biological data and do not assess subjective experience.

## Important problems found in methods audit

1. **Confounded no-inheritance control:** In the frozen `engine.py`, `no_inheritance` regenerates each population with zero recurrence and immediately `continue`s, preventing any newly mutated recurrent link from appearing. It therefore tests the combined absence of inheritance *and* recurrent links, rather than loss of inheritance alone. Treat its zero payoff as a consequence of the imposed architecture, not an independently informative negative result.
2. **Only a narrow motor-command comparison is tested:** The motor-command signal is supplied by the environment, not chosen by the agent. The controller does not discover a body, a motor system, or first-person selfhood. Calling this a full *self-model* would overstate the implementation.
3. **Exact expected-payoff selection is an oracle:** Training fitness is evaluated on the analytically known true event probabilities (four possible cue/event pairs), not on uncertain individual lifetimes or locally experienced reproductive success. Accordingly, the simulated selection is a powerful engineered optimizer and is not a realistic ecological simulation.
4. **Post-hoc highest-score champion:** The reported agent for every condition is the best-performing controller in the final generation *using actual task payoff*, including the random-fitness group. This yields positive scores in the random-fitness group even though fitness did not drive its evolution. It is a valid descriptive best-of-population comparison, but not a comparison of typical individuals under random drift.
5. **Designed task and candidate components:** The world guarantees that remembering the command can help. Neural units, phase timing, sensor inputs, structural mutation and policy evaluation are specified. A useful connection does not appear ex nihilo.
6. **Neither prospective public preregistration nor independent replication:** The protocol was frozen locally after earlier exploratory work. Its statistical intervals measure variation across simulation seeds under one selected model, not uncertainty about real evolution.

## NEW post-hoc sensitivity control: de novo recurrence without inherited genotypes

To address (1) without modifying frozen source or replacing the original results, `audit_de_novo_control.py` independently regenerates 192 unrelated controllers for each of 300 generations, allowing recurrent links de novo (Bernoulli 0.045 per potential recurrent edge with fresh normally distributed weights). No genome is passed between generations. We evaluate the best final-generation controller using the same survival criterion and 24 original seed identifiers. This is a simple alternate baseline, **not** the original frozen mutation process, and its outcome is exploratory.

- New independent-generation baseline: mean payoff **0.02030** (95% bootstrap interval **0.01766–0.02323**), all 24 runs nonzero.
- Original evolving condition: mean payoff **0.17051**.
- Paired difference: mean **0.15022** (95% bootstrap interval **0.12943–0.16933**); evolved results higher in **24/24** paired seeds.

This does **not** fix all design limitations. It does show that the original zero-value no-inheritance baseline should not have been interpreted as a clean ablation and that the more appropriate new baseline is nonzero.

## Literature and novelty

The distinction between externally caused and self-caused sensory events is widely researched under *corollary discharge/efference copy*; see Crapse and Sommer (2008), DOI 10.1038/nrn2457. Robots already learn action-sensation relationships and adaptive body models; see Bongard, Zykov and Lipson (2006), DOI 10.1126/science.1133687. A 2025 human study investigated formation of action-outcome models and sense of agency; see Tanaka and Imamizu (2025), DOI 10.1038/s44271-025-00240-7. No comprehensive novelty claim is warranted on the current literature search.

## Responsible release and next test

Suitable for transparent sharing as an *exploratory computational teaching/methods demonstration*, provided this addendum is included and authorship/credit is settled. **Not yet a defensible original paper claiming a new mechanism for consciousness.** Next: preregister a separate study in advance, replace exact-payoff selection with stochastic lifetime survival/reproduction, allow agents to choose motor actions, separate mutation from inheritance controls cleanly, incorporate more than binary environmental states, test multiple controller topologies and cost assumptions, then ask an external evolutionary-computation or neuroscience researcher to independently replicate the model.

### Files

Original frozen: `engine.py`, `run_study.py`, `STUDY_PROTOCOL.md`, raw seed outputs and original research note. New post-hoc audit: `audit_de_novo_control.py`, `audit_de_novo_control.csv`, `audit_de_novo_metrics.json`, this addendum, and amended PDF. The frozen source was **not modified** to retrofit favorable results.
