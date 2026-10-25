# Academic Board Cross-Evaluation & Defense Interrogation (15-Slide Deck)
## Slide-by-Slide Defense Criticisms, Viva Traps, and Winning Spoken Rebuttals

> **How to Use This Document:**
> This guide prepares you for the **Master's Thesis Pre-Defense viva**. For each of the **14 slides** (featuring expanded focus on Literature Review and Proposed Methodology), a hypothetical adversarial committee member (e.g., ML Theorist, Systems Auditor, Security Chair) asks the hardest possible questions.
> 
> * **Response Target:** 15–30 Seconds in spoken viva format.
> * **Golden Rule:** Stay calm, maintain academic poise, cite established literature, and use intuitive analogies without colloquial slang.

---

### Slide 1: Title Page

* **🧐 The Critic Board Member's Interrogation:**  
  *"Your title is 'Adversarial Robustness in Network Intrusion Detection Systems via Attribution-Guided Feature Selection and Dynamic Multi-Stage Adversarial Training'. Why is this a Master's thesis topic rather than just a routine machine learning engineering project?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  Testing whether your work has genuine theoretical research substance rather than simply chaining together off-the-shelf Python libraries.
* **🛡️ Winning Board-Proof Spoken Rebuttal (15–30 Seconds):**  
  > *"Honorable committee, this is an foundational research problem at the intersection of game-theoretic explainability and non-convex robust optimization. Standard adversarial training suffers from Tsipras' accuracy-robustness trade-off and perturbation staleness. Our contribution is formulating a novel mathematical stability criterion derived from Shapley values that identifies an invariant 27-dimensional manifold, proving that targeted subspace reduction can resolve the clean accuracy penalty while providing empirical robustness under dynamic minimax optimization."*
* **📊 Board Readiness Score:** **9.8 / 10**  
  *Delivery Tip:* Use technical terms like *Shapley attribution invariance* and *minimax optimization* to immediately establish academic depth.

---

### Slide 2: Presentation Outline

* **🧐 The Critic Board Member's Interrogation:**  
  *"Your outline covers the 11 required presentation topics across 14 slides. How have you structured the time allocation across these sections?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  Testing presentation discipline and time management.
* **🛡️ Winning Board-Proof Spoken Rebuttal (15–30 Seconds):**  
  > *"The presentation is calibrated at approximately one minute per slide for a total of 12 to 14 minutes. Context and motivation take the first four minutes, our literature survey and 3-part methodology receive six dedicated minutes of technical focus, and the experimental setup, timeline, and hypotheses conclude the remaining three minutes, leaving ample time for your questions."*
* **📊 Board Readiness Score:** **9.9 / 10**  
  *Delivery Tip:* Speak with calm, structured confidence. Time discipline signals thorough preparation.

---

### Slide 3: Problem Statement

* **🧐 The Critic Board Member's Interrogation (Network Systems Prof):**  
  *"You define your threat model as an $\ell_\infty \le 0.05$ bounded perturbation on continuous features. But real network packets are discrete byte streams. If you add 0.05 to 'Flow Duration' or 'Packet Length', that might violate TCP checksums or produce fractional packet lengths that a physical NIC would instantly drop. Isn't this continuous feature-space attack completely artificial?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  The fundamental critique bridging tabular feature-space perturbations and physical problem-space constraints (Pierazzi et al., IEEE S&P 2020).
* **🛡️ Winning Board-Proof Spoken Rebuttal (15–30 Seconds):**  
  > *"That is a well-recognized constraint in network security research. As formalized by Pierazzi et al. at IEEE S&P, feature-space perturbations represent an **upper-bound threat model**. An attacker in the physical problem space can alter inter-arrival timing by delaying transmissions, or inflate packet lengths by adding dummy padding. If an intrusion detector fails against continuous bounded perturbations, it is fundamentally vulnerable. In this thesis, our scope is rigorously evaluating flow-level tabular representations, while physical packet re-assembly remains an exciting direction for future problem-space work."*
* **📊 Board Readiness Score:** **9.8 / 10**  
  *Delivery Tip:* Cite **Pierazzi et al. (IEEE S&P 2020)** and explicitly acknowledge that continuous perturbations represent an *upper-bound theoretical vulnerability*.

---

### Slide 4: Motivation & Research Objectives

* **🧐 The Critic Board Member's Interrogation (ML Theorist):**  
  *"Tsipras et al. (ICLR 2019) mathematically proved that adversarial robustness is fundamentally at odds with clean accuracy—that any robust classifier must suffer a drop in clean accuracy. On Slide 4, you state your objective is to investigate whether selecting stable features can improve both clean and robust performance. Are you suggesting an established ICLR theorem is incorrect?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  Appearing naive or claiming to violate fundamental statistical learning theorems.
* **🛡️ Winning Board-Proof Spoken Rebuttal (15–30 Seconds):**  
  > *"Not at all; Tsipras' mathematical proof is indisputable, but it relies on a strict foundational premise: that the input feature space $\mathcal{X}$ is **fixed and immutable**, as in standard image pixel grids. In tabular network flow engineering, the feature space is not fixed. Raw flow records contain noisy, gradient-volatile features and transient socket shortcuts that distort clean decision boundaries. By performing subspace reduction—pruning down to 27 perturbation-stable dimensions—we remove volatile dimensions. Adversarial training then acts as a regularizer over the remaining stable manifold, allowing us to maintain clean accuracy without contradicting Tsipras' theorem."*
* **📊 Board Readiness Score:** **9.9 / 10**  
  *Delivery Tip:* Emphasize: *Tsipras assumed a fixed feature space; we perform subspace dimensionality reduction to remove non-robust features.*

---

### Slide 5: Literature Review (Part 1): Current Research Landscape

* **🧐 The Critic Board Member's Interrogation:**  
  *"On Slide 5, you mention that studies frequently report a 2% to 6% clean accuracy penalty when applying adversarial training, and that tree ensembles frequently suffer degradation under iterative gradient attacks. Why do tree ensembles struggle if they achieve 98% clean accuracy?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  Testing theoretical understanding of tree ensemble decision boundaries versus gradient perturbations.
* **🛡️ Winning Board-Proof Spoken Rebuttal (15–30 Seconds):**  
  > *"Tree-based ensembles like Random Forest and XGBoost split feature space using axis-aligned orthogonal step functions with zero gradient everywhere. Because they have non-differentiable margins, they cannot be hardened via standard gradient-based minimax optimization. When attacked by transfer or query-based attacks, perturbations easily step across these brittle partitions into misclassified leaf regions, leading to substantial degradation despite high clean accuracy."*
* **📊 Board Readiness Score:** **9.9 / 10**  
  *Delivery Tip:* Explain the difference between *axis-aligned orthogonal splits* and *smooth, differentiable neural margins*.

---

### Slide 6: Literature Review (Part 2): Landmark Peer Benchmarks

* **🧐 The Critic Board Member's Interrogation:**  
  *"You criticize your base paper, Holla et al. (IEEE Access 2025), for using static adversarial training. But Holla reported 88% defended accuracy against gradient attacks and 84% against black-box Square Attack. If their IEEE Access paper published in 2025 already works, why is your dynamic training necessary?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  Challenging the necessity of your research when a peer publication already claims 88% defended accuracy.
* **🛡️ Winning Board-Proof Spoken Rebuttal (15–30 Seconds):**  
  > *"Holla's 88% defended accuracy relies on **static offline augmentation**—pre-generating 30,000 attack samples once before retraining. As weights update across 50 epochs, the decision boundary moves, and those static perturbations may lose efficacy against adaptive attacks. Furthermore, in Section V-B and Figure 3 of their paper, Holla et al. explicitly retained **Source Port and Destination Port** as top influential features. As Engelen et al. proved at ACM CCS, models on CSE-CIC-IDS2018 can achieve high accuracy simply by memorizing port numbers. Our research is essential because we permanently excise socket shortcuts and train against live, evolving attacks that continuously track the moving boundary."*
* **📊 Board Readiness Score:** **9.8 / 10**  
  *Delivery Tip:* Cite Holla's Section V-B (port retention) and Engelen et al. (port shortcut leakage) with absolute confidence.

---

### Slide 7: Comparative Analysis & Research Gaps

* **🧐 The Critic Board Member's Interrogation:**  
  *"Your comparison table summarizes Holla et al., Olukola & Rahimi, Zeng et al., and Güvenç Paltun et al. What is the single unifying research gap across all of these works that your thesis addresses?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  Testing whether you see the big picture or just get lost in individual paper details.
* **🛡️ Winning Board-Proof Spoken Rebuttal (15–30 Seconds):**  
  > *"The overarching research gap across all four works is an **unresolved trade-off between perturbation staleness, feature-space noise, and inference latency**. Holla et al. achieved line-rate speed but suffered static staleness and port leakage. Olukola & Rahimi addressed staleness with dynamic training but incurred heavy overhead by optimizing across all 78 noisy dimensions without feature selection. Güvenç Paltun et al. and Zeng et al. introduced defenses with prohibitive runtime latencies. Our pipeline bridges this exact gap: offline stability filtering removes noisy dimensions, dynamic PGD reduces staleness, and our compact MLP preserves line-rate throughput."*
* **📊 Board Readiness Score:** **10.0 / 10**  
  *Delivery Tip:* Frame your answer as the synthesis that unites the strengths of prior works while eliminating their operational drawbacks.

---

### Slide 8: Proposed Methodology (Part 1): Data Sanitization & Screening

* **🧐 The Critic Board Member's Interrogation (Data Science Auditor):**  
  *"On Slide 8, you partition 6,320,003 flows into 72% Core Training (4,550,401 flows), 8% Validation (505,601 flows), and 20% Test (1,264,001 flows). Why this exact structure, and why do you need Mutual Information to filter 69 features to 40 before SHAP?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  Testing understanding of data partitioning hygiene and two-tier feature engineering efficiency.
* **🛡️ Winning Board-Proof Spoken Rebuttal (30 Seconds):**  
  > *"First, an initial 80/20 train-test split is the standard benchmark protocol on CSE-CIC-IDS2018. To enforce strict zero-leakage, we freeze the 1.26 million flow test partition on Day 0. Within the 5.05 million development portion, an industry-standard 9-to-1 split yields exactly 72% for core training (4.55M flows) and 8% for validation (505K flows). All scalers are fitted strictly on the 72% split.
  > 
  > Second, computing Shapley values has combinatorial complexity $\mathcal{O}(2^D)$. Running SHAP across 69 dimensions on millions of flows is computationally prohibitive. Mutual Information acts as a rapid, coarse filter, eliminating 29 uninformative noise dimensions in seconds. This reduces downstream SHAP computation by over 60% while preserving physical feature semantics."*
* **📊 Board Readiness Score:** **10.0 / 10**  
  *Delivery Tip:* Clearly distinguish the two tiers: *coarse filtering for computational efficiency, stability auditing for adversarial robustness*.

---

### Slide 9: Proposed Methodology (Part 2): Pillar 1 — Adversarial Stability SHAP

* **🧐 The Critic Board Member's Interrogation (XAI Specialist):**  
  *"On Slide 9, how exactly does your 80% cumulative stability-mass criterion select the 27 features, and why is this mathematically superior to an arbitrary flat threshold?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  Testing the mathematical formulation of your stability metric.
* **🛡️ Winning Board-Proof Spoken Rebuttal (30 Seconds):**  
  > *"An arbitrary flat threshold (like $\tau = 0.50$) is rigid and does not adapt to the empirical distribution of feature stability across different datasets.
  > 
  > Instead, we compute the total stability mass across all 40 candidate features: $S_{\text{total}} = \sum_{k=1}^{40} S_k$. We rank features in descending order of $S_j$ and retain the minimal subset $m$ such that their cumulative stability sum accounts for at least 80% of the total mass: $\sum_{j=1}^m S_j \ge 0.80 \cdot S_{\text{total}}$.
  > 
  > This Pareto-optimal criterion systematically captures the vast majority of stable attribution energy, selecting exactly 27 features while filtering out the long tail of 13 volatile dimensions."*
* **📊 Board Readiness Score:** **10.0 / 10**  
  *Delivery Tip:* Emphasize that the **80% cumulative mass rule** is an adaptive Pareto criterion, not an arbitrary manual cutoff.

---

### Slide 10: Proposed Methodology (Part 3): Pillar 2 — Two-Phase Dynamic Hardening

* **🧐 The Critic Board Member's Interrogation (Optimization Theorist):**  
  *"On Slide 10, your dynamic PGD step size is $\alpha = 0.005$ with $\epsilon = 0.05$ across 5 steps. Why $\alpha = 0.005$ rather than $\epsilon / 4 = 0.0125$?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  Testing parameter calibration for inner gradient ascent.
* **🛡️ Winning Board-Proof Spoken Rebuttal (30 Seconds):**  
  > *"In non-convex continuous tabular manifolds, a smaller step size of $\alpha = 0.005$ ($\epsilon / 10$) prevents the inner optimization loop from overshooting the local loss maximum. Over 5 iterations, this provides controlled gradient ascent that explores the local $\ell_\infty$ ball without producing chaotic, oscillating perturbations.
  > 
  > Paired with our 10-epoch clean representation warmup, this controlled step size allows the network to gradually adapt its decision boundaries, maintaining benign traffic stability while building empirical adversarial robustness."*
* **📊 Board Readiness Score:** **10.0 / 10**  
  *Delivery Tip:* Explain that $\alpha = 0.005$ prevents **gradient oscillation and overshooting** in tabular feature space.

---

### Slide 11: Dataset, Environment & Target Architecture

* **🧐 The Critic Board Member's Interrogation (Systems Prof):**  
  *"You are evaluating 6.32 million flows on an AMD Radeon RX 7600 with 8 GB of VRAM. Can an 8 GB GPU really handle dynamic adversarial training on 6.32 million flows without running out of memory?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  Testing hardware feasibility and VRAM budgeting.
* **🛡️ Winning Board-Proof Spoken Rebuttal (15–30 Seconds):**  
  > *"Yes, Professor, easily. Because our feature selection prunes the input space to 27 compact numerical features, and our target architecture has fewer than 15,000 parameters, memory consumption is exceptionally low. With batch size 2048 and mixed precision under native ROCm PyTorch, the entire model, activations, and gradient tensors occupy less than 2.2 GB of VRAM—well within the RX 7600's 8 GB capacity. A full 50-epoch training run completes in approximately 70 minutes."*
* **📊 Board Readiness Score:** **10.0 / 10**  
  *Delivery Tip:* Cite the exact VRAM footprint: *less than 2.2 GB active VRAM out of 8 GB*.

---

### Slide 12: Weekly Research Timeline & Gantt Chart

* **🧐 The Critic Board Member's Interrogation (Defense Chair):**  
  *"Today is September 10th. You have roughly four weeks until October 11th to complete full multi-threat evaluation, run multi-seed tests, write the entire thesis manuscript, and defend. Is this timeline realistic?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  The primary concern of department chairs: project delay and unfinished manuscripts.
* **🛡️ Winning Board-Proof Spoken Rebuttal (15–30 Seconds):**  
  > *"The timeline is tightly structured and entirely feasible because all exploratory groundwork is already complete. Tasks 1 through 7 are finished: the data ingestion pipeline, theoretical formulations, and ROCm GPU environment are verified. Because our compact 27-feature MLP completes a 50-epoch training run in approximately 70 minutes on our RX 7600, all multi-seed and multi-threat evaluations will complete within Week 11. Weeks 12 and 13 are reserved exclusively for manuscript drafting and supervisor revisions ahead of our October 11 defense."*
* **📊 Board Readiness Score:** **9.9 / 10**  
  *Delivery Tip:* Reassure the committee by citing your actual training duration (~70 minutes per full 50-epoch run), proving computational tractability.

---

### Slide 13: Expected Results & Research Hypotheses

* **🧐 The Critic Board Member's Interrogation (Robust ML Specialist):**  
  *"You hypothesize achieving 88% to 90.5% robust accuracy under PGD-100. How will you prove that your model isn't just suffering from gradient masking or obfuscated gradients, as identified by Athalye et al. at ICML 2018?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  A classic defense board trap: claiming high robustness that is actually an artifact of broken optimization gradients.
* **🛡️ Winning Board-Proof Spoken Rebuttal (15–30 Seconds):**  
  > *"We follow the diagnostic verification suite established by Athalye et al. (ICML 2018):
  > 
  > First, we verify that 100-step PGD outperforms 20-step PGD, confirming that iterative search finds worse perturbations rather than hitting zero gradients.
  > 
  > Second, we evaluate parameter-free Auto-PGD (APGD-CE) and optimization-based Carlini-Wagner attacks, which do not rely on standard fixed-step gradients.
  > 
  > Third, we evaluate the gradient-free black-box Square Attack and surrogate transferability. If robust accuracy remains high across both gradient-free and black-box transfer attacks, it mathematically confirms genuine decision boundary regularization rather than gradient obfuscation."*
* **📊 Board Readiness Score:** **10.0 / 10**  
  *Delivery Tip:* Citing **Athalye et al. (ICML 2018)** and listing the three diagnostic checks (iterative convergence, APGD/CW, and gradient-free Square Attack) will instantly impress any machine learning specialist.

---

### Slide 14: Conclusion & Immediate Next Steps

* **🧐 The Critic Board Member's Interrogation:**  
  *"What is the primary ablation experiment you will run to prove that both of your pillars—Stability SHAP and Dynamic Training—are independently necessary?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  Testing your experimental design and ablation rigor.
* **🛡️ Winning Board-Proof Spoken Rebuttal (15–30 Seconds):**  
  > *"We will execute a 2x2 factorial ablation study:
  > 1. Baseline Model (Clean-only features + Standard Static Training);
  > 2. Stability SHAP only (27 stable features + Static Training);
  > 3. Dynamic Training only (Full 69 features + Two-Phase Dynamic PGD);
  > 4. Full Proposed Pipeline (27 stable features + Two-Phase Dynamic PGD).
  > This cleanly isolates the individual performance contribution of feature stability versus dynamic minimax optimization, proving that both pillars are essential to achieve Pareto-optimal accuracy and robustness."*
* **📊 Board Readiness Score:** **9.9 / 10**  
  *Delivery Tip:* Describing a clean **2x2 factorial ablation** proves you understand rigorous experimental scientific methodology.

---

### Slide 15: References (Academic Bibliography)

* **🧐 The Critic Board Member's Interrogation:**  
  *"You cite 18 references covering foundations from 2015 to direct 2025–2026 peers. Which single reference is your theoretical foundation, and which is your direct benchmark?"*
* **⚠️ Vulnerability / Ambiguity Exposed:**  
  Testing if you distinguish between foundational theory and empirical baselines.
* **🛡️ Winning Board-Proof Spoken Rebuttal (15–30 Seconds):**  
  > *"Our direct empirical baseline is Reference 1, Holla et al. (IEEE Access 2025), which established the Static Triad benchmark on cloud NIDS. Our theoretical foundations are Madry et al. (ICLR 2018) for minimax adversarial training and Lundberg & Lee (NeurIPS 2017) for cooperative game-theoretic Shapley attribution. We also build upon Tsipras et al. (ICLR 2019) to address the accuracy-robustness trade-off, and Engelen et al. (ACM CCS 2021) for dataset hygiene and shortcut removal."*
* **📊 Board Readiness Score:** **10.0 / 10**  
  *Delivery Tip:* Distinctly separating your empirical baseline (`[1]`) from your theoretical foundations (`[8]`, `[11]`, `[17]`, `[18]`) demonstrates mastery of the literature.
