# Paper Review 37: Categorical Robustness & Seed Variance (Raj et al., 2026)

**Title:** Categorical Robustness Assessment for Machine Learning based Network Intrusion Detection Systems  
**Authors:** A. Raj, S. Mohan, et al.  
**Year & Venue:** 2026 | *IEEE Transactions on Information Forensics and Security* / arXiv:2602.xxxxx  
**Category:** Part 3 — Attacking / Methodological Critique Paper  

---

## 1. Paper Overview & Short Summary
* **Domain:** Evaluation Reproducibility, Random Seed Variance, Statistical Robustness Auditing.
* **One-Paragraph Summary:** Raj et al. conduct an extensive reproducibility audit across published AML-NIDS literature, revealing that adversarial evaluations reported on a single random seed are statistically unreliable. They demonstrate that identical neural network architectures trained with different random initialization seeds exhibit performance swings of up to $\pm 15\%$ in robust accuracy under PGD attacks. They prove that defenses claiming slight accuracy improvements often fall within random seed variance.
* **Main Research Problem:** The prevalence of single-seed evaluations in cybersecurity literature that report cherry-picked or statistically insignificant results.
* **Main Motivation:** Demanding multi-seed statistical confidence intervals as a mandatory requirement for valid adversarial evaluation.

---

## 2. Exact Methodology of the Critique
1. **Seed Variance Experimentation:** Trains identical deep models across 20 distinct random seeds: $\text{seeds} \in \{1, \dots, 20\}$.
2. **Variance Quantification:** Evaluates clean accuracy and PGD robust accuracy, computing standard deviations $\sigma_{\text{robust}}$.
3. **Finding:** While clean accuracy showed low variance ($\sigma \approx 0.3\%$), adversarial robust accuracy exhibited extreme variance ($\sigma = 4.8\% \text{ to } 7.2\%$).

---

## 3. Key Findings & Evidence Presented by Authors
* Demonstrated that over 85% of published AML-NIDS papers report only a single seed.
* Proved that claimed defense improvements under 5% are frequently statistical artifacts of lucky seed selection.

---

## 4. Critical Assessment & Limitations of the Critique
* Raj et al.'s critique establishes the necessity of multi-seed reporting ($\mu \pm \sigma$). Any valid thesis must report metrics averaged across multiple independent runs with explicit standard deviations.

---

## 5. Why Our Proposed Pipeline is Mathematically & Architecturally Superior
* **Multi-Seed Protocol in Methodology Design:** Phase2Net is explicitly designed to be evaluated across multiple independent seeds (e.g., `seeds = [42, 123, 2024]`), reporting Mean $\pm$ Standard Deviation.
* **Mathematical Variance Reduction:** Phase2Net's architectural stability stems from the low condition number of the SHAP-selected feature covariance matrix $\kappa(\mathbf{\Sigma}_{27}) \ll \kappa(\mathbf{\Sigma}_{78})$, which mathematically suppresses parameter sensitivity to weight initialization.

---

## 6. Defense Board Mock Attack Questions & Viva-Style Answers

> **Committee Member Question 1:** *"Raj et al. (2026) proved that adversarial evaluations evaluated on a single seed exhibit up to $\pm 15\%$ variance under PGD. How does your proposed evaluation methodology ensure that your reported results will be statistically valid rather than an artifact of seed selection?"*

* **🗣️ What to Say in the Viva (15–30 Second Response):**  
  "We explicitly reject single-seed reporting. Our methodology specifies running all experiments across multiple independent random seeds (seeds 42, 123, and 2024), reporting results as Mean $\pm$ Standard Deviation with confidence intervals. Furthermore, by reducing the input space from 78 noisy features to 27 stable features, we remove the ill-conditioned gradient directions that cause high seed variance in the first place."
* **🧠 Core Intuitive Logic (Easy to Remember):**  
  1. **Multi-Seed Standard:** Never trust a single roll of the dice; we run multiple independent seeds for data splitting, initialization, and attacks.
  2. **Tightly Bounded Results:** We report Mean $\pm$ Standard Deviation to prove statistical significance.
  3. **Mathematical Stability:** Eliminating noisy features flattens the optimization landscape, preventing random initializations from landing in wildly different local minima.
* **🛡️ Winning Technical Argument:**  
  We report $\bar{\mu} \pm \hat{\sigma}$ across independent seeds. Projecting into the 27-dimensional stable subspace $\mathbf{P}$ eliminates ill-conditioned Hessian directions. Under random initialization, gradient variance scales with dimension: $\text{Var}(\nabla_x \mathcal{L}) \propto \mathcal{O}(D)$. Reducing dimensions from 78 to 27 mathematically constrains gradient update variance across seeds.
* **⚠️ Viva Trap to Avoid:**  
  Never report a single number without variance or standard deviation when asked about evaluation reliability.

---

## 7. Oral Defense Traps to Avoid
* **Trap:** Never claim that your model is deterministic and only needs one run.
* **Safe Mathematical Stance:** State that you evaluate across multiple random seeds and report confidence intervals to ensure statistical reproducibility.
