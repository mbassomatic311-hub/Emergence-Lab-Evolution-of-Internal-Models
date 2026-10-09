# External scientific review request — Study 09 design

**Status:** ready to *share* for feedback, but **no reviewer has been contacted or committed**. This is an invitation to critique, not a claim of independent review.

## What we are asking for

An evolutionary robotics / causal system identification researcher to critique the proposed design **before confirmatory data generation**, and ideally independently author or audit one environment. An additional quantitative reviewer should inspect inference, population-level independence and preregistration. Reviewers must be free to recommend abandoning the project or reframing it as negative-results/methods work.

## Context reviewers need

- Existing [research repo](https://github.com/mbassomatic311-hub/Emergence-Lab-Evolution-of-Internal-Models) with Experiments 01–08; [Experiment 08 exploratory PR](https://github.com/mbassomatic311-hub/Emergence-Lab-Evolution-of-Internal-Models/pull/2) and earlier [Experiment 07 audit PR](https://github.com/mbassomatic311-hub/Emergence-Lab-Evolution-of-Internal-Models/pull/1).
- Honest summary: a hand-designed 1D comparator bested the evolved recurrent network in all 32 seed comparisons; 2D evolved networks underperformed analytic controllers; several designed online learners used action history successfully but their causal ontologies were supplied; active uncertainty probing failed to beat balanced cyclic actions.
- No scientific paper, independent replication, registration, or subjective-consciousness finding exists.

## Specific review questions

1. Which published algorithms already study the proposed effects? What novelty claim (if any) remains defensible?
2. Is the word 'self-model' justified or should all claims be restricted to action-conditioned sensorimotor dynamics?
3. Are two planned domains sufficiently different, or is the setup artificially biased to favor action-conditioned models?
4. Do the proposed interventions make body effects versus environmental effects **identifiable**? When are they mathematically indistinguishable?
5. Are policy observations truly separated from oracle/simulator states in all code paths?
6. Are comparators given comparable training samples, sensor channels, compute, feature priors and optimization/tuning effort?
7. Does changing connection topology make a real difference versus fixed RNNs and history-fed predictors?
8. Is the action history ablation implemented with preserved RNG streams, preventing accidental change in stochastic worlds?
9. Are interventions on hidden state causal and not just destructive to arbitrary memory?
10. Does the analysis treat independent evolving populations as sampling units and account for multiple worlds/contrasts?
11. Is the proposed training environment too sparse for evolution to find any improvement? Is task tuning likely to select a favorable result?
12. What would a strong **negative** result look like, and what publication venue would fairly accept it?

## Proposed contact message — not sent

Subject: Request for methods critique: evolutionary sensorimotor self-modeling study (open-source exploratory results)

Hello,

I'm developing an open-source computational research project on whether evolutionary selection can produce reusable action-conditioned internal representations without preprogrammed causal labels. Our exploratory simulations have mostly highlighted limitations: simple analytical and memory-based baselines often outperform the evolved networks, and causal attribution can fail when observations do not identify a unique cause.

Before running any confirmatory work, I'm looking for candid methodological feedback on a proposed study using independently implemented sensorimotor environments, preregistered hypotheses, and strong model-based controls. I would especially value criticism of the novelty claim, identifiability, test-set design, and feasible baselines. The current results and negative findings are public, and I would not expect you to endorse any consciousness claim.

Would you be willing to review a short protocol, or suggest someone better placed to assess it? I can provide the code, protocol and reviewer checklist.

Thank you for considering it.

---

**Before sending:** secure user's approval of recipient and exact email text; ask the reviewer for consent before identifying them in any public report. Do not advertise affiliation, endorsement, peer review or a commitment that does not exist.
