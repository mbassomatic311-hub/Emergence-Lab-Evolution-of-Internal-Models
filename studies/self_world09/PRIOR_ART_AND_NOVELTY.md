# Literature and novelty screen — initial review (not a systematic review)

**Date:** 9 Oct 2026 · **Status:** initial source-checked screen; requires external expert critique and broader searching before a novelty claim.

| Prior work | Why it directly constrains our claims |
|---|---|
| Bongard, Zykov & Lipson (2006), *Resilient Machines Through Continuous Self-Modeling*, *Science*. DOI [10.1126/science.1133687](https://doi.org/10.1126/science.1133687) | Robots have already inferred body dynamics from action–sensation feedback and adapted after damage. Action-conditioned self-models are not new. |
| Kwiatkowski & Lipson (2019), *Task-Agnostic Self-Modeling Machines*, *Science Robotics*. DOI [10.1126/scirobotics.aau9354](https://doi.org/10.1126/scirobotics.aau9354) | Data-driven task-agnostic self-modeling from robot experience already demonstrated. 'Without explicit body geometry' is not by itself novel. |
| Chen, Kwiatkowski, Vondrick & Lipson (2022), *Fully Body Visual Self-Modeling of Robot Morphologies*, *Science Robotics*. DOI [10.1126/scirobotics.abn1944](https://doi.org/10.1126/scirobotics.abn1944) | Learned internal morphological representations from visual experience likewise preexist. |
| Klyubin, Polani & Nehaniv (2005), *Empowerment: A Universal Agent-Centric Measure of Control*. DOI [10.1109/CEC.2005.1554676](https://doi.org/10.1109/CEC.2005.1554676) | Information-theoretic action/sensor controllability is established; we cannot claim discovery of action agency from feedback. |
| Hauser & Bühlmann (2014), *Two Optimal Strategies for Active Learning of Causal Models from Interventional Data*. DOI [10.1016/j.ijar.2013.11.007](https://doi.org/10.1016/j.ijar.2013.11.007) | Experimental interventions improving causal identifiability are known. The 08G/08H controls are demonstrations, not novel principle. |
| Locatello et al. (2019), *Challenging Common Assumptions in the Unsupervised Learning of Disentangled Representations*, ICML. [PMLR publication](https://proceedings.mlr.press/v97/locatello19a.html) | Unsupervised factorization generally requires inductive bias/assumptions; 'from nowhere' is untenable. Our proposal must inventory supplied biases. |
| Hafner et al. (2023), *Mastering Diverse Domains through World Models*, [arXiv:2301.04104](https://arxiv.org/abs/2301.04104) | Model-based RL/world-model adaptation is a strong modern algorithmic comparison; the proposal must not compare only against weak toy reactive agents. |

## Provisional novelty assessment

**Known:** forward models, active sensing, sensorimotor calibration, evolving neural controllers, body-schema learning and latent-world modeling. Our 01–08 results have not established an original method or an empirically unreported phenomenon.

**Potential and unproven angle:** selection-driven acquisition of a *transferable*, action-conditioned latent representation, without a hand-coded causal ontology, tested under intentionally paired body/world perturbations in **independently implemented**, physically distinct domains against modern matched-compute baselines. Whether this combination is novel remains an open literature question, not an assertion.

## Reviewer actions

- Search conferences/journals: ALIFE, GECCO, Artificial Life, Evolutionary Computation, IEEE Transactions on Evolutionary Computation, CoRL, ICRA, IROS, NeurIPS, ICML, Science Robotics.
- Search by **combinations**, not only the word 'consciousness': evolved body schema + internal models + causal intervention; action-conditioned state, developmental robotics, morphological adaptation, disentangled controllable latent, intrinsic motivation, dual control, active system identification, predictive processing.
- Find published open-code baselines with comparable training budgets. Determine whether a replication of an established result, rather than a novelty claim, is the right publication path.
- Do not frame this as proving a theory of consciousness, holographic reality or simulation theory.
