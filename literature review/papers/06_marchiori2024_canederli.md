# Paper Review 06: CANEDERLI (Marchiori & Conti, 2024)

**Title:** CANEDERLI: Adversarial Training and Transferability in Network Intrusion Detection  
**Authors:** F. Marchiori and M. Conti  
**Year & Venue:** 2024 | *IEEE Transactions on Dependable and Secure Computing*, Vol. 21, No. 4, pp. 3105–3120  
**Category:** Part 1 — Similar Methodology / Direct Peer  

---

## 1. Paper Overview & Short Summary
* **Domain:** Black-Box Transferability, Surrogate Architectures, Adversarial Training Benchmark.
* **One-Paragraph Summary:** Marchiori and Conti conduct a systematic empirical investigation into the cross-architecture transferability of adversarial perturbations in tabular NIDS. They demonstrate that adversarial samples generated on deep surrogate neural networks transfer with alarming success rates (>75% ASR) to undefended target classifiers including Random Forests, Support Vector Machines, and Gradient Boosted Trees. They propose CANEDERLI, an ensemble adversarial training regimen that aggregates adversarial gradients from multiple surrogate architectures during training.
* **Main Research Problem:** Defenses trained against white-box attacks often remain vulnerable to black-box transfer attacks crafted on surrogate models with different inductive biases.
* **Main Motivation:** Understanding the mathematical mechanisms that enable adversarial transferability across tabular classifiers and designing transfer-resistant defenses.

---

## 2. Exact Methodology
1. **Cross-Architecture Transferability Matrix:** Evaluates adversarial transfer across five heterogeneous model families: MLP, Random Forest, XGBoost, CNN-1D, and Decision Trees.
2. **CANEDERLI Multi-Surrogate Defense Pipeline:**
   * Employs an ensemble of $M$ surrogate networks with diverse layer depths and activation functions.
   * Generates adversarial perturbations by maximizing the joint multi-surrogate loss.
   * Retrains the target detector on the multi-surrogate perturbed samples.

---

## 3. Key Results & Empirical Findings
* **Datasets:** CSE-CIC-IDS2018 and UNSW-NB15.
* **Baseline Transfer Vulnerability:** Undefended models exhibit 72% to 84% ASR when attacked by surrogate-generated PGD samples.
* **CANEDERLI Robustness:** Reduces black-box surrogate transfer ASR to 14.5% across heterogeneous targets.
* **Operational Overhead:** Training time scales linearly with the number of surrogates ($M \times \text{training time}$), requiring multiple concurrent forward/backward passes per iteration.

---

## 4. Critical Limitations & Flaws
1. **Ensemble Scalability Bottleneck:** Maintaining and optimizing $M$ diverse surrogate models during training creates substantial GPU memory and compute overhead.
2. **Full-Feature Alignment:** CANEDERLI trains across all raw features without dimensionality reduction. Because raw feature spaces share common collinearities across models, surrogate gradients readily align along shared feature dimensions.

---

## 5. Why Our Proposed Pipeline is Mathematically & Architecturally Superior
* **Subspace Orthogonalization Breaks Transferability:** Marchiori & Conti observed high transferability because surrogate models trained on identical 78-dimensional features learn aligned gradient directions. Phase2Net projects data into the **27-dimensional SHAP-stable subspace**. When an external attacker trains a black-box surrogate on raw traffic in $\mathbb{R}^{78}$, the surrogate's gradient distributes energy across all 78 dimensions. By eliminating the 51 non-stable dimensions, Phase2Net mechanically shatters gradient alignment.
* **Single-Model Compactness:** Phase2Net achieves transfer resistance using a **single compact 3-layer MLP** without training multi-model ensembles.

---

## 6. Defense Board Mock Attack Questions & Viva-Style Answers

> **Committee Member Question 1:** *"Marchiori & Conti (2024) showed that defending against transfer attacks requires training against a whole ensemble of surrogate models. Your proposed methodology trains against perturbations generated only by your own model. Why won't your defense fail against black-box transfer attacks from an independently trained surrogate?"*

### **Our Bullet-Proof Defense Rebuttal (Viva-Style):**

* **🗣️ What to Say in the Viva (15–30 Second Response):**  
  *"Professor, transfer attacks only succeed when the surrogate and target model share the exact same brittle feature dependencies. Marchiori & Conti trained their models on all 78 raw features, so every model learned the same vulnerable shortcuts. In Phase2Net, we project the data into a private, 27-dimensional stable subspace. An external attacker training a surrogate model on raw traffic is optimizing in a 78-dimensional world. When their attack hits our model, 51 of their dimensions hit a brick wall of zero weights, completely shattering gradient alignment. We don't need a heavy ensemble because our feature subspace breaks transferability by design."*

* **🧠 Core Intuitive Logic (Easy to Remember):**
  1. **The Shared Language Analogy:** Transfer attacks work because both models speak the same flawed language (78 unpruned features). We changed the dialect to 27 stable features, so the attacker's instructions get lost in translation.
  2. **Worst-Case Superiority:** Our internal white-box PGD attack is mathematically the strongest possible attack. If the model can survive its own worst-case white-box attack, it will easily survive weaker attacks transferred from an external surrogate.
  3. **Resource Efficiency:** Avoids the 5x training overhead of maintaining multiple surrogate models.

* **🛡️ Winning Technical Argument:**  
  Adversarial transferability is proportional to gradient cosine similarity. Projecting into a 27-dimensional subspace where non-robust shared features are eliminated drives cross-model gradient similarity toward zero.

* **⚠️ Viva Trap to Avoid:**  
  *Never say:* "Transfer attacks are impossible."  
  *Safe stance:* "Transfer attacks are dangerous on shared unpruned feature spaces, but projecting into a verified stable subspace breaks the cross-model alignment that enables transferability."
