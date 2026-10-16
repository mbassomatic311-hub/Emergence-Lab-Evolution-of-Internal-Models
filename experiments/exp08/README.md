# Experiment 08 — Active Representation Discovery

**Status: exploratory computational benchmark.** This is a new track in Emergence Lab, separate from the website. It is not a claim of novelty, general intelligence, or scientific discovery.

## Question

When a system is uncertain which of several candidate mathematical representations describes an unfamiliar environment, does choosing observations where the candidate models disagree improve rule identification and out-of-sample prediction compared with collecting observations passively?

## What is implemented

- Four candidate representation families: linear, interaction, quadratic, and absolute-difference.
- Synthetic worlds generated from one of those families with randomized coefficients and measurement noise.
- A fixed-linear baseline that never revises its representation.
- A passive model-selection baseline that gathers random observations and selects by a BIC-like score.
- An active arm that uses weighted disagreement among candidate models to choose informative inputs, then uses the same model-selection rule as the passive arm.
- Fresh held-out inputs, per-world paired comparisons, and a bootstrap interval for mean MSE differences.

The candidate families are explicitly provided. The active system does **not** invent arbitrary mathematical languages or operators. Query-by-committee, information-seeking, model selection, and related ideas have substantial prior art; a literature review is required before any novelty claim.

## Run

Python 3.10+ and NumPy are required.

```sh
python -m pip install numpy
python -m unittest -v
python engine08.py --worlds 500 --budget 32 --initial 8 --seed 20261015 --out results.json
```

The JSON output contains configuration, arm summaries, per-world rows, and paired bootstrap contrasts. The primary independent unit is the generated world, not each held-out point.

## Exploratory run (not confirmatory)

On 500 generated worlds, 32 total observations per world (8 initial + 24 chosen/collected), and noise SD 0.05:

| Arm | Mean held-out MSE | Median held-out MSE | Representation accuracy |
|---|---:|---:|---:|
| Fixed linear | 0.12047 | 0.09990 | 24.6% |
| Passive model selection | 0.000372 | 0.000288 | 96.6% |
| Active model selection | 0.000295 | 0.000240 | 98.0% |

Active minus passive comparison, expressed as passive MSE minus active MSE: mean difference **0.0000766**, 95% paired world-bootstrap interval **[0.0000433, 0.0001124]**; active had lower MSE in 285/500 worlds and higher MSE in 215/500. This suggests a small advantage in this deliberately favorable, low-dimensional setup. The large gain over fixed-linear is primarily evidence that representation flexibility matters; it is not evidence that the active strategy is broadly superior.

These results were inspected during development and are therefore exploratory. They must not be relabeled as preregistered or confirmatory.

## Limitations and next tests

1. The true representation is always among four supplied candidates; real problems may require a representation outside the candidate set.
2. Candidate model scores use a BIC-like approximation; correlated model families and small samples can make scores unreliable.
3. Active queries are selected from a finite random grid, not optimized continuously.
4. The current worlds are two-dimensional, stationary, and noisily observed. There is no hidden regime shift yet.
5. The benchmark does not establish that this method is new relative to active learning, Bayesian experimental design, optimal design, or automated scientific discovery.

Next milestone: freeze a protocol for untouched seeds; add misspecified worlds whose true rule is not in the candidate library; add a model-expansion arm that proposes new terms; and compare against a stronger passive baseline and an oracle selector. Require gains on held-out world families, not just this generator, before advancing the claim.
