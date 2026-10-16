# Experiment 09 — Open-Ended Representation Invention (bounded grammar)

**Status: exploratory.** This experiment extends Exp08 by introducing true functions outside Exp08's original candidate model family and permitting a candidate model to add one term from a larger symbolic grammar.

This is not unrestricted invention, not a novelty claim, and not evidence of general intelligence. The grammar is explicitly authored by the researcher.

## Research question

Can a system recover a useful representation term absent from its original model family, and does disagreement-guided selection of observations improve discovery versus passive sampling under the same model-selection procedure?

## Arms

- `fixed_original`: uses only the original linear, interaction, quadratic and absolute-difference terms.
- `passive_expand`: collects random observations, then chooses among the original model and models augmented with one grammar term using a BIC-like score.
- `active_expand`: uses weighted predictive disagreement among those candidate models to choose observations, then uses the same final model selection as passive expansion.

## Run

```sh
python -m pip install numpy
python -m unittest -v
python engine09.py --worlds 200 --budget 40 --initial 10 --seed 20261016 --out exp09_results.json
```

## Important interpretation boundaries

- The true functions are outside Exp08's original candidate model family but are drawn from a finite, documented discovery grammar. The system does not invent arbitrary operators.
- The active query heuristic is a form of model-disagreement sampling, related to established active learning and Bayesian experimental design.
- The candidate models currently add only one new feature. Interactions among multiple invented features are not explored.
- The data-generating function is stationary and low-dimensional; real-world discovery is substantially harder.
- The test functions are known to the benchmark designer. A confirmatory evaluation must use held-out function families not used in development.
- Any initial results are exploratory. No confirmatory or novelty claim should be made without an independently frozen protocol and literature review.

## Next milestone

Add a staged feature-invention procedure that can propose combinations of discovered features, test whether it can recover functions from a held-out grammar, include adversarial distractor features, and compare against strong passive feature selection and an oracle. Freeze the evaluation protocol before examining confirmatory outcomes.
