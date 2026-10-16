# Experiment 10 — Residual-Guided Compositional Discovery

**Status: exploratory prototype.** Exp10 moves beyond Exp09's one-added-term selection by screening a finite feature grammar against baseline residuals and evaluating one- and two-feature additions. It tests whether a residual pattern can guide the construction of a better representation.

## Research question

Can residual-guided composition recover nonlinear structure that is not represented by any single candidate term, and does disagreement-guided sampling help relative to passive sampling under equal observation budgets?

## Arms

- \`fixed\`: fit only the baseline linear, interaction, and quadratic representation.
- \`passive\`: randomly sample inputs, then residual-screen the documented grammar and select among baseline, single-addition, and pair-addition models using a BIC-like score.
- \`active\`: choose each additional input by weighted disagreement among the same screened candidate models, then use the same final selection procedure.

## Run

From this directory:

\`\`\`sh
python -m pip install numpy
python -m unittest -v
python engine10.py --worlds 100 --budget 48 --initial 12 --seed 20261017 --out exp10_results.json
\`\`\`

## What this does—and does not—establish

- The feature library is finite, human-authored, and includes selected products of primitive expressions. This is bounded compositional search, not unrestricted source-code invention.
- Residual screening can overfit noisy data; active query selection can exploit the same misspecification. Stronger baselines and held-out grammars are essential.
- Benchmark truths are sampled from a known composition family. This is not an independent generalization test and not evidence of scientific novelty.
- Report all arms, paired uncertainty, recovery rate, and error-world counts; do not report only the best aggregate metric.
- A confirmatory study should freeze this code and protocol, use new target families and noise regimes, and compare against regularized regression, exhaustive feature selection with the same grammar, and an oracle.

## Planned falsification tests

1. Increase noise and reduce the observation budget.
2. Add many irrelevant but correlated distractor features.
3. Test target compositions absent from the candidate library.
4. Compare active sampling to passive sampling with matched seeds and budgets.
5. Check whether improved prediction actually coincides with recovery of the true term.


## Automated check
The repository's research-experiment workflow runs the unit tests and a 20-world smoke benchmark for pull requests touching Exp09/Exp10. This smoke run checks execution and output shape; it is not a confirmatory statistical result. The workflow checks out the pull-request merge ref by default so it can test the submitted branch without a manually constructed ref.
