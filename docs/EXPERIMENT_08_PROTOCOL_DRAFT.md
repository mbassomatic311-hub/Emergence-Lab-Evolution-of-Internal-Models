# Experiment 08 — Proposed confirmatory design (DRAFT)

> **NOT PREREGISTERED. NOT EXECUTED.** This is a living study design for external criticism. Do not call it a frozen protocol or count any exploratory data as confirmatory. An immutable externally timestamped plan, code and hash must be deposited **before** opening the eventual held-out seed set.

## Research objective
Test whether evolutionary search over **mutable controller architectures** can discover action-conditioned internal representations that *generalize across changes in actuator dynamics* better than computation-matched nonrecurrent controllers **and** simple hand-designed model-based estimators.

This is a question about sensorimotor control and evolutionary computation. **There is no consciousness test or measurement.** Successful prediction, learning, and a self/body model do not entail first-person experience.

## Motivation and falsifiable alternatives
Experiment 07 provided a memory unit and engineered action-effect input and then selected neural weights. Audit 08A found a post-hoc hand-coded comparator that surpassed evolved recurrent controllers in the same simulator. Thus the candidate mechanisms are not novel, and any next result must survive this and stronger baselines.

- **H1 (narrow, provisional)**: Under a prespecified computational/energy budget, evolved modular recurrent controllers achieve a nonzero out-of-distribution gain over the **best of multiple prespecified, cost-matched baseline classes**, averaged across multiple independently implemented worlds.
- **H0**: Any gain vanishes against elementary action-effect estimators, well-tuned recurrent policies, or other complexity-matched baselines.
- **Falsifier**: If the best engineered benchmark ties or wins on the preregistered primary transfer metric, H1 is unsupported, even if evolved networks beat reactive agents.

## Simulation families (at least two independently written implementations)
A. **1D actuator world**: noisy target bearing, hidden action sign, unannounced reversals, longer sensor delays, random external impulses, and sensor dropouts. Include training task distributions and qualitatively different held-out interventions; robustly distinguish self-motion from external world changes.

B. **2D resource world**: turning, translation, moving obstacles, food depletion, variable action lag, changing body mechanics, resource uncertainty and explicit per-step compute/energy costs. This world must NOT be a trivial translation of the 1D rules and must be reviewed by a separate developer.

Agents do not observe privileged hidden states (true actuator sign, exact target coordinates, future hazards, reversal schedule). Both worlds require validation that trivial policies cannot win by exploiting seeded reset artifacts.

## Controller classes and fair comparison
1. Random and reactive (minimum baselines).
2. Hand-coded one-step sign estimator (Audit 08A).
3. Analytic Bayesian hidden-state estimator, parameter tuned exclusively on development seeds.
4. Nonrecurrent policy with explicit recent observation/action history (controls for availability of history).
5. Fixed-topology recurrent policy with evolved weights (controls for the contribution of topology search).
6. Evolved topology (candidate): connections and recurrence may be absent at initialization and introduced/removed by heritable structural mutation, with costs.
7. Random-fitness and de-novo/no-inheritance controls.

To avoid misleading claims, benchmark models should be compared at matched **sensor access, training episodes, lifetime steps, approximate compute budget and controller complexity**. Report unmatched comparisons clearly as supplemental. Control adaptive hyperparameter optimization and baseline search effort.

## Outcomes and analysis (must be finalized before registration)
- **Primary:** average transfer score normalized within each world relative to a prespecified baseline and task upper bound, under held-out distribution shift. Independently evolved populations, not individual test episodes, are units of analysis.
- **Secondary:** survival, food per unit energy, predictions of the sensory consequences of the agent's own actions, calibration, adaptation speed following reversal, controller size and energy cost.
- Assess explicit **causal information use**: scramble the motor-command copy while preserving available observation history; test matched controllers with action history but no recurrent state; test predictions on novel interventions.
- Acknowledge correlation between performance and a post-hoc "self model": prediction accuracy is not subjective experience.

## Registration and sampling gates
1. Build validated independent implementations and strong baseline benchmarks, run **development/pilot seeds only**.
2. Use pilot variability to choose an attainable per-family sample size, a primary contrast, minimum practically relevant effect, confidence interval method, and correction for any co-primary tests.
3. Freeze code, environment distributions, hyperparameters, seed generation algorithm, inclusion/exclusion rules, statistical plan, and expected compute expenditure.
4. Deposit immutable preregistration with an independent timestamp (e.g., AsPredicted or a registered report / public archival record). Obtain reviewer feedback where possible.
5. Only then generate and evaluate untouched confirmatory seeds. Preserve all failures, intermediate logs, and raw data; compare results without retuning.
6. Get an independent scientist to rerun the code and check analysis before presenting confirmatory evidence.

## Publication and novelty gate
This is not a new consciousness theory. A contribution would require **an improvement over strong known methods**, reproducibility in at least two independent environments, an explicit relation to existing literature, and an expert opinion on whether the specific method or result adds knowledge. A peer-reviewed Registered Report is preferable if feasible. A GitHub repository or Zenodo DOI is an archive, not peer review.

## Foundational literature
- Bongard et al. (2006), resilient robots: https://doi.org/10.1126/science.1133687
- Imamizu (2010), efference copy: https://doi.org/10.1111/j.1468-5884.2010.00428.x
- Shadmehr et al. (2010), sensorimotor prediction: https://doi.org/10.1146/annurev-neuro-060909-153135
- Contemporary overview of embodied sensorimotor control: https://pmc.ncbi.nlm.nih.gov/articles/PMC12458597/

**Transparency:** Experiment 08 has no confirmatory results and has not yet been publicly preregistered.
