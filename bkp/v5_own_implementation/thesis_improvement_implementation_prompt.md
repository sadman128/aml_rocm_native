# Implementation Prompt: Addressing Gradient Masking & Feature Selection Findings

## Context

I have a PyTorch/ROCm reimplementation of "Adversarial Threats to Cloud IDS: Robust
Defense With Adversarial Training and Feature Selection" (Holla, Polepalli &
Sasikumar, IEEE Access 2025), running on CSE-CIC-IDS2018. The notebook
(`adversarial_cloud_ids_defense_rocm_v4_final.ipynb`) implements:

- Adaptive mutual-information feature selection (cumulative-importance threshold,
  not the paper's fixed T)
- A baseline IDSNet (configurable 3-hidden-layer MLP with BatchNorm+Dropout)
- A dual-layer defended model: Stage 1 (clean training on SHAP-robust features) +
  Stage 2 (Madry-style on-the-fly PGD adversarial training)
- A paper-comparable fixed-budget attack evaluation track (FGSM/PGD/DeepFool via
  ART, eps=0.05) plus a black-box Square Attack
- A raw-coded (no ART) zero-day/unseen-attack suite: MI-FGSM, pure random noise,
  a sparse high-magnitude attack, and a gradient-free Boundary-Walk attack — none
  of these attack types are ever used during training
- An automated gradient-masking detector comparing defended-model accuracy on
  gradient-based zero-day attacks vs. the gradient-free Boundary-Walk attack

## What the last full run found

1. **Gradient masking suspected.** Defended model accuracy: 92-95% against every
   gradient-based attack (known FGSM/PGD/DeepFool AND unseen MI-FGSM/Sparse), but
   only **34.5%** against the gradient-free Boundary-Walk attack — a 59.15
   percentage-point gap, ~4x the notebook's own 15pp alert threshold. This is the
   classic signature described in Athalye et al., "Obfuscated Gradients Give a
   False Sense of Security" (ICML 2018): a model whose apparent robustness comes
   partly from distorting/flattening gradients near the decision boundary rather
   than a genuinely hardened boundary.
2. **Adaptive MI feature selection selected 42 of 44 candidate features** at a
   90% cumulative-importance threshold — essentially no dimensionality reduction
   happened, unlike the paper's implied ~25 features. SHAP-robust selection then
   picked 24 features from those 42.
3. **Baseline model is comparatively fragile** this run (Square Attack success
   rate 75.3%, DeepFool crashes baseline to 16.25% accuracy) — plausibly
   downstream of point 2's much larger feature/attack surface than earlier
   fixed-T=25 runs.
4. Known-attack-track results otherwise look strong and directionally consistent
   with the paper (defended model beats baseline under every known attack).

## Task list, in priority order

### Priority 1 — Investigate and address gradient masking directly

**1a. Add a gradient-free attack into Stage 2 training itself, not just evaluation.**
Currently Stage 2 (`adversarial_train_model`) only ever generates PGD-style
examples via `native_pgd`. Add an option to mix in gradient-free adversarial
examples during training — e.g., a lightweight per-batch random-search attack
(similar in spirit to `tabular_square_attack` but cheap enough to run every
batch) or an abbreviated Boundary-Walk with a small step budget. Make the mix
ratio configurable (e.g. `CONFIG["adv_train_gradfree_ratio"]`, default something
modest like 0.15-0.25 of the adversarial portion of each batch). Re-run the full
pipeline and check whether the Boundary-Walk gap in Table 9 shrinks. Report
before/after numbers explicitly.

**1b. Implement and run an adaptive attack against the defended model**, per
Athalye et al.'s own recommended verification method: an attack designed with
knowledge of the specific defense mechanism, not a generic off-the-shelf one.
Concretely: run PGD with substantially more steps (e.g. 100-200, vs. the current
eval budget of 20) and multiple random restarts (e.g. 5-10) specifically against
the defended model, and check whether success rate increases substantially with
more optimization budget — if it does, that's further evidence of masking rather
than genuine robustness, since a truly hardened model's robustness shouldn't
collapse just from giving the attacker more compute.

**1c. Repeat the full zero-day suite across all 3 seeds (42, 123, 2024)**, using
the existing `DATA_SEED`/`SEED` isolation already in the pipeline, to confirm the
59pp masking gap is a consistent finding and not a single-seed artifact. Report
mean/std of the Boundary-Walk gap across seeds.

**1d. Add TRADES-style robust loss as an alternative Stage 2 training option**
(configurable, alongside the current pure-PGD-augmentation approach) —
implement the TRADES loss (Zhang et al., "Theoretically Principled Trade-off
between Robustness and Accuracy," ICML 2019): a KL-divergence term between clean
and adversarial predictions added to standard cross-entropy, rather than training
directly on adversarial-labeled examples. This is known in the literature to
produce less gradient-masking-prone models than pure adversarial-example
augmentation. Compare its Table 9 gradient-masking gap against the current
approach's.

### Priority 2 — Feature selection sensitivity

**2a. Sweep `mi_cumulative_threshold` and `shap_cumulative_threshold`** across a
small grid (e.g. 0.70, 0.80, 0.90 — current default) and report, for each: number
of features selected, baseline clean/attacked accuracy, defended clean/attacked
accuracy, and the Boundary-Walk masking gap from Table 9. The goal is to
determine whether a smaller, more paper-comparable feature count (a) improves
baseline attack robustness on its own, and (b) changes the masking gap.

**2b. Add an elbow-detection alternative to cumulative-threshold selection** —
e.g., select the feature count at the point of maximum second-derivative drop in
the sorted MI/SHAP curve — as a second adaptive method to compare against the
cumulative-threshold approach, since 90% cumulative mass turned out to be an
unexpectedly weak filter on this dataset.

### Priority 3 — Verification and reporting infrastructure

**3a. Add TABLE 9's masking-gap check to the multi-seed aggregation workflow**
(the existing 3-seed stability study), so gradient-masking-gap mean/std is
reported alongside the existing accuracy/F1 stability metrics.

**3b. Add a "TABLE 10 — Adaptive Attack Verification" section** presenting the
Priority 1b results (success rate vs. PGD iteration count / restart count) as a
short curve, directly supporting or refuting the masking hypothesis with a
second independent line of evidence beyond the single-attack-type comparison in
Table 9.

**3c. Update the notebook's markdown/comments** to describe the masking finding,
the TRADES alternative (if implemented), and the feature-selection sensitivity
results as an explicit "Limitations and Findings Beyond the Paper" section —
this is the strongest original-contribution material for the thesis and should
be easy for a reader/examiner to find, not buried in console output.

## Constraints and conventions to preserve

- Keep `DATA_SEED`/`SEED` isolation exactly as-is (train/test split, SMOTE, and
  feature selection stay fixed across seed-stability runs; only weight init and
  training stochasticity vary).
- Keep the existing paper-comparable fixed-budget attack track (ART, eps=0.05,
  FGSM/PGD/DeepFool) unchanged — new work should be additive, not replace it,
  since it's still needed for the paper cross-check table.
- Keep Madry-style multi-step PGD as the primary Stage 2 training method (per
  earlier explicit decision) — TRADES should be an additional configurable mode,
  not a replacement, so both can be compared directly.
- No ART dependency for any of the new zero-day/adaptive-attack/masking-check
  code — stay consistent with the existing raw-coded native PyTorch approach for
  everything in this task list.
- Every new hyperparameter goes into `CONFIG`, none hardcoded, consistent with
  the rest of the notebook's existing convention.
- Validate the final notebook the same way as before: concatenate all code cells
  in execution order (skipping the `!pip install` magic cell), run `py_compile`
  and `pyflakes` on the result, and confirm zero errors/warnings before treating
  it as done.

## Deliverable

A complete, updated `.ipynb` file (not a diff or partial patch instructions),
fully validated per the constraints above, plus a short written summary
covering: (1) whether the gradient-masking gap shrank after 1a/1b/1d, (2) the
feature-selection sensitivity sweep results from 2a/2b, and (3) whether the
finding held consistently across all 3 seeds per 1c.
