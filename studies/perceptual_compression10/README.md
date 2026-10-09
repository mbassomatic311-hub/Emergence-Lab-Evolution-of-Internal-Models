# Study 10 — Multimodal predictive compression (exploratory development)

**Study status: exploratory COMPUTATIONAL SIMULATION, not externally registered or independently replicated.** This is **not a consciousness experiment** and **does not measure subjective unity of experience, extra physical dimensions, or biological neurons**. No inferential novelty claim is made.

## Research question and conditional falsifiers

When several noisy sensory streams describe overlapping physical causes, can a low-dimensional representation of their **combined** signals preserve enough information to predict future sensory observations? Conversely, when sensory streams track distinct causes, does compressing everything into the same small bottleneck lose information?

- **H1, expected in a redundant physical world:** A joint four-dimensional linear representation should predict future observed signals at least as well as equally small *separately* compressed representations, and potentially outperform regularized full-input regression with scarce samples.
- **H2, failure condition in a more complex world:** When each modality tracks its own three dynamic physical factors (nine total), a four-dimensional representation should lose predictive information relative to an appropriately regularized model observing all 48 channels.
- **H3, out-of-distribution degradation:** Corruption in one sensory stream can hurt all models, and no compression choice is guaranteed best.
- **Null / rival explanations:** Linear latent world structure was intentionally designed into the generator; PCA can exploit correlations that are there by construction. Strong regularized raw-input and supervised reduced-rank models may equal or exceed unsupervised PCA with enough training, so a predictive advantage does not imply a cognitive discovery.

## Simulator and information access

24 fixed independent **development** world seeds in each scenario. Per world, three modalities each provide 16 noisy observations (**48 total**). There are two randomly varying control inputs. Dynamics are driven by an unknown stable linear state transition and control matrix, with stochastic process disturbances. **No fitted model receives the generating state's coordinates, true matrices, or latent-factor labels.** Each world uses the same physical dynamics but *independently randomized trajectories and sensor noise* for training, validation, and test.

- **Shared physical factors:** all three sensory groups observe linear noisy mixtures of the same three hidden dynamic state variables.
- **Modality-private factors:** each sensory group observes different three-variable dynamic state, nine hidden factors total, while actions may influence multiple groups.
- Observational noise SD 0.32; stochastic transition noise SD 0.28. Sensors include 16 linear combinations per modality. This is not a biologically realistic retina, cochlea, or interoceptive organ. Ground truth is used to **generate** synthetic worlds, never to train the learned predictors.
- Fit on either 120 or 1,000 training transitions, choose the ridge penalty from a fixed five-value grid on a separate 220-step development validation trajectory, and score on a separate 480-step evaluation trajectory **per world**. These test trajectories are internal *development holdouts*, **not an independently preregistered confirmatory set**.
- Evaluate an additional **unseen sensory corruption** scenario: inject new noise SD 1.6 into the first 16 current sensor channels at evaluation only; the target future sensors are not corrupted. Parameters are not retuned.

All models see the same sensory observations and action signals; the models differ in their dimensionality and representational assumptions. All models predict the **next** 48 observed sensory values; model error is calculated after standardized per-channel scaling from training data (mean squared error; smaller is better). No conscious-experience variable is generated or predicted.

## Predictors and important fairness limitations

| Predictor | Sensory representation | Trained head |
|---|---|---|
| Action-only | No sensory inputs | Ridge regression |
| Raw ridge | All 48 sensor channels | Ridge regression (penalty tuned on validation) |
| Joint PCA-4 | Four latent dimensions learned from all 48 channels | Ridge regression |
| Split PCA-4 | Per-modality dimensions 2 + 1 + 1, total four | Ridge regression |
| Random projection-4 | Four random orthonormal sensory dimensions | Ridge regression |
| Joint PCA-8 | Eight dimensions learned jointly | Ridge regression |
| Split PCA-8 | Per-modality dimensions 3 + 3 + 2 | Ridge regression |
| Supervised rank-4 | Four-dimensional reduced-rank sensory-to-target mapping | Ridge regression trained on sensory futures |
| Future-target shuffled PCA-4 | Joint PCA-4 but next-sensor training targets deliberately permuted | Negative control |

**PCA itself is a fixed existing algorithm; it has not evolved spontaneously.** The split allocation was selected by the investigator, not optimized; a fully tuned modular bottleneck is an outstanding stronger control. The supervised rank-4 head receives future-sensor training targets to choose its representation, so it is a *different* information regime than PCA, not a causally matched ablation. Four latent sensory dimensions do not specify the overall computational burden of each estimator. Each method also receives two control signals. Training samples/alpha grid and evaluation worlds are otherwise matched.

## Main exploratory results — MSE averaged across 24 worlds

| World / training transitions | Joint PCA-4 | Split PCA-4 | Raw ridge | Supervised rank-4 | Random-4 | Action-only |
|---|---:|---:|---:|---:|---:|---:|
| Shared / 120 | **0.5229** | 0.5655 | 0.5557 | 0.5505 | 0.7322 | 1.0254 |
| Shared / 1,000 | **0.4657** | 0.4999 | 0.4736 | 0.4717 | 0.6514 | 0.9248 |
| Private / 120 | 0.7869 | 0.8138 | **0.6196** | 0.7810 | 0.8977 | 1.0191 |
| Private / 1,000 | 0.6877 | 0.7135 | **0.5001** | 0.6853 | 0.7955 | 0.9360 |

Mean world-paired difference (joint PCA-4 minus raw ridge; lower favors PCA) at 120 training transitions:

- **Shared:** −0.03285; exploratory seed-bootstrap 95% percentile interval **[−0.03882, −0.02739]**; joint PCA outperformed raw ridge in 24/24 development worlds.
- **Private:** +0.16735; exploratory seed-bootstrap 95% interval **[+0.15584, +0.17990]**; joint PCA underperformed raw ridge in 24/24 development worlds.
- Joint PCA-4 minus split PCA-4 in the shared case: −0.04265, exploratory 95% interval [−0.05612, −0.03102].

The negative control that deliberately mismatched observations with future targets scored 1.1558 on shared/120, worse than both joint PCA (0.5229) and action-only regression (1.0254). Learning the temporal correspondence matters within this constructed world.

### New sensory corruption (no training on it)

In the shared / 120 case, the mean error under corrupted current observations was joint PCA-4 **0.6399**, raw ridge **0.7442**, and split PCA-4 **0.9698**. In the private / 120 case joint PCA-4 **0.8812** versus raw ridge **0.8872**, with a seed-bootstrap interval for the difference **[−0.02664, +0.01529]** (includes zero). This distribution-shift result is a *specific* corruption method chosen by us; generalization is not established.

**Across many iterative choices, all bootstrap intervals above describe only sampled synthetic world seeds.** Multiple models and conditions were examined, no independent preregistration took place, and these intervals cannot support a broad population or consciousness claim.

## Interpretation — what this test does and doesn't show

- **Demonstrated in the synthetic worlds:** Under known, low-rank shared generative causes, jointly compressing three noisy streams to four variables can preserve enough information to predict future observations and sometimes outperform high-dimensional regression at limited sample sizes.
- **Demonstrated counterexample:** Four variables lose relevant predictive structure when the simulated world needs nine physical latent degrees of freedom. The 48-input regularized model is substantially better in that scenario.
- **Not demonstrated:** Human perceptual unity, first-person awareness, neuronal dimensionality, uniquely existing internal mental dimensions, string-theoretic extra spatial dimensions, or whether sensory integration causes consciousness. The generative worlds *literally have their low-rank structure specified in code*.
- **Prior art:** Low-dimensional neural manifolds and predictive information bottlenecks are existing neuroscientific and information-theoretic ideas; see citations below. We are re-creating an expected computational property, not claiming a new principle.

## Suggested next real-world scientific test (NOT conducted)

Use a publicly accessible **multisensory neural dataset** with simultaneous neural activity and sensory stimulation, or a human audiovisual integration paradigm with matched trial-level subjective reports. Prespecify the primary comparison between shared latent bottlenecks, separate-bottleneck and full-input predictors, matched hyperparameter budgets, cross-participant generalization, and neural/patient-wise statistical units. Test an independent report of perceived integration rather than labeling any dimensionality reduction as consciousness. Secure ethics approval if collecting new human data. Such a study can test association with perception, not prove subjective experience is spatially multidimensional.

## Reproduction

Requires Python 3.11+ and NumPy 2.x; reference environment NumPy 2.3.5. With BLAS single-threaded for deterministic output:

```bash
OPENBLAS_NUM_THREADS=1 python -m unittest -v test_study10.py
OPENBLAS_NUM_THREADS=1 python study10.py --seeds 24 --out development-reproduced
```

Verify `development/per_seed.csv` and `development/summary.json`. Original development output hashes are in `SHA256SUMS.txt`. Test/report on genuinely new environments should be treated as a separately timestamped study, not as validation of an already-inspected result.

## Related published scientific literature

- Perich, Narain & Gallego (2025), *A neural manifold view of the brain*, Nature Neuroscience: https://www.nature.com/articles/s41593-025-02031-z
- Senkowski & Engel (2024), *Multi-timescale neural dynamics for multisensory integration*, Nature Reviews Neuroscience: https://www.nature.com/articles/s41583-024-00845-7
- Bialek and colleagues (2015), *Predictive information in a sensory population*: https://pmc.ncbi.nlm.nih.gov/articles/PMC4460449/
- Low-dimensionality alone is not a metric of conscious awareness, and theoretical dimensions of experience are not extra physical dimensions.
