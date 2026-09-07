# V9 Experimental Methodology & Architectural Specification

This document details the complete experimental methodology implemented in `adversarial_cloud_ids_defense_v9_final.ipynb` for evaluating adversarial defense mechanisms on the CSE-CIC-IDS2018 benchmark.

---

## 1. Dataset, Partitioning & Leakage Prevention
*   **Source Dataset:** Full CSE-CIC-IDS2018 network flow dataset (~4.5 million flows).
*   **Leakage-Free Splitting Pipeline:**
    1.  **Test Partition (20%):** Stratified and frozen immediately after cleaning. Test data remains 100% isolated until the final adversarial evaluation.
    2.  **Dev / Validation Partition (10% of training pool):** Kept strictly untouched for epoch-level validation F1 monitoring and early checkpoint selection.
    3.  **SHAP Calibration Pool:** Dedicated sample carved strictly from the *training pool* to compute SHAP values and stability scores, ensuring zero data leakage into the validation or test sets.
*   **Preprocessing Fit Scope:** `OneHotEncoder`, `StandardScaler`, `mutual_info_classif`, and `SMOTE` are fit strictly on the core training pool.
*   **SMOTE Categorical Handling:** SMOTE is applied post-encoding; synthetic samples may contain interpolated fractional values across one-hot feature dimensions.

---

## 2. Feature Selection Framework
*   **Mutual Information (MI) Stage:** Top 40 features selected from the training pool based on mutual information with the binary target.
*   **Paper Defense Features (Top 15 Clean SHAP):** Top 15 features selected by mean absolute SHAP values on clean samples.
*   **V9 Defense Features (Cumulative 80% Robust SHAP):**
    *   SHAP values computed under both clean and adversarial ($	ext{PGD}_{20}$) conditions on the training calibration pool.
    *   Stability Score: $	ext{Score}_j = 1.0 - rac{|	ext{SHAP}^{	ext{clean}}_j - 	ext{SHAP}^{	ext{adv}}_j|}{\max(	ext{SHAP}^{	ext{clean}}_j + 	ext{SHAP}^{	ext{adv}}_j, 10^{-10})}$.
    *   Features ranked by stability score and accumulated up to 80% of total robust score (yielding ~18–22 stable features).

---

## 3. Defense Implementations
*   **1. Baseline IDSNet:** Standard multi-layer perceptron (128-64-32 with Dropout 0.3) trained on the 15 Paper features using standard cross-entropy loss (50 epochs).
*   **2. Paper Defense (Static Adversarial Augmentation):**
    *   Faithful reproduction of static augmentation methodology (Holla et al., 2025).
    *   Warm-up model generates pre-computed static FGSM ($10,000$ samples) and static PGD ($10,000$ samples) perturbations.
    *   Augmented dataset ($	ext{Clean} + 	ext{FGSM} + 	ext{PGD}$) trains the model for 50 epochs.
*   **3. V9 Defense (Online Dynamic PGD Training):**
    *   Trained on the V9 robust SHAP feature subset.
    *   **Phase 1:** 10 epochs of clean pretraining.
    *   **Phase 2:** 40 epochs of pure-GPU online PGD adversarial training, dynamically generating fresh 5-step PGD perturbations per batch using current model weights ($\mathcal{L} = 0.5 \mathcal{L}_{	ext{clean}} + 0.5 \mathcal{L}_{	ext{adv}}$).

---

## 4. Adversarial Threat Models & Diagnostics
*   **Standard Robustness Benchmark:**
    *   **FGSM:** Single-step gradient attack ($\epsilon = 0.05$).
    *   **PGD:** 100-step multi-step projected gradient descent ($\epsilon = 0.05$, step size $lpha = 0.10 	imes \epsilon$, with rigorous $L_\infty$ assertion check).
    *   **Square-style Attack:** Fast GPU-vectorized score-based coordinate block search (100 iterations on 1,000 samples).
    *   **Transfer PGD Attack:** Black-box transferability against an independently trained WiderNet surrogate (256-128-64) with target feature alignment.
*   **Gradient-Masking Diagnostic Probes:**
    *   **Label-Only Boundary Search:** GPU-vectorized decision-based binary search probing boundary distance (heuristic diagnostic, not a defense benchmark).
    *   **PGD Iteration Sweep:** $20, 50, 100, 200$ steps to verify optimization plateaus.
    *   **Epsilon Sweep:** $\epsilon \in \{0.01, 0.03, 0.05, 0.10\}$ to test monotonic degradation.
    *   **Multi-Indicator Heuristic Verdict:** Aggregates transfer gap, iteration decay, and epsilon slope to detect potential gradient masking.
*   **DeepFool:** Reported strictly as an unconstrained minimum-perturbation distance metric.

---

## 5. Computational Fairness & Budget Tracking
V9 leverages a higher computational training budget due to online per-batch gradient optimization. To maintain academic fairness:
*   All training budgets, epoch durations, GPU forward/backward steps, and wall-clock times are explicitly exported to `training_budget.csv` and `training_budget.json`.
*   The thesis attributes V9's empirical robustness to the combination of adaptive feature selection and expanded online optimization budget.
