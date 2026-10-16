# Experiment 08 — Protocol and Claim Boundaries

**Version:** 0.1 exploratory protocol, written after initial development runs. This document is not a preregistration. The existing 500-world run is exploratory and must remain labeled as such.

## Primary question

Does active selection of observations using disagreement among candidate models improve held-out prediction over passive observation when both arms share the same model family and final model-selection criterion?

## Current operational design

- World family: one of four supplied symbolic forms: linear, interaction, quadratic, or absolute difference.
- Inputs: two continuous variables sampled in [-1, 1].
- Measurement noise SD: 0.05.
- Data budget: 32 observations, including 8 initial random observations.
- Arms: fixed linear; passive observation plus BIC-like candidate selection; active disagreement-guided observation plus the same selection.
- Evaluation: 512 fresh noiseless held-out inputs per world.
- Outcomes: held-out mean squared prediction error and exact candidate-family identification.
- Independent unit: generated world.
- Uncertainty: paired bootstrap over worlds, 10,000 resamples, fixed bootstrap seed 71823.

## Interpretation

This is a controlled toy benchmark of active model selection. The true family is selected from the same finite library given to the algorithm. Therefore, successful identification is not open-ended scientific discovery. No claim is made about consciousness, human-level reasoning, or a new general-purpose intelligence.

## Development and confirmatory separation

The initial 500-world run was examined before this protocol was committed to the repository. It cannot serve as confirmatory evidence for this protocol. Before a confirmatory run, publish an independently timestamped preregistration that specifies:
- untouched seed range and sample size;
- a held-out generator family not used for development;
- misspecified worlds where no candidate family is correct;
- primary metric and one primary contrast;
- all baselines, exclusions, and analysis code;
- criteria for failure and for advancing to the next research stage.

## Required next comparison

The next substantive step is not merely to increase the number of runs. It is to add environments where the true rule lies outside the supplied model library, then test whether a representation-expansion mechanism can propose a useful new feature. Compare it against passive selection, fixed-library active selection, and a strong oracle upper bound. Preserve negative results and report computational costs.
