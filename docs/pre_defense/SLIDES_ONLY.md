# SLIDE CONTENTS ONLY (Pre-Defense Presentation — 15 Slides)
## Focused Pre-Defense Deck: Expanded Literature Review (2 Slides), In-Depth Methodology (3 Slides) & References (1 Slide)

---

### Slide 1: Title Page
* **Title:** Adversarial Robustness in Network Intrusion Detection Systems via Attribution-Guided Feature Selection and Dynamic Multi-Stage Adversarial Training
* **Subtitle:** Pre-Defense Presentation
* **Candidate:** [Your Name / Student ID]
* **Supervisor:** [Supervisor Name & Title]
* **Department:** Department of Computer Science & Engineering
* **Date:** September 10, 2026

---

### Slide 2: Presentation Outline
* **1. Research Context & Problem Statement** — Vulnerability of deep NIDS to bounded perturbations
* **2. Motivation & Research Objectives** — Addressing the accuracy vs. robustness trade-off
* **3. Literature Review** — Current research findings & landmark peer defenses (2021–2026)
* **4. Comparative Analysis & Research Gaps** — Structural limitations & what our work addresses
* **5. Proposed Methodology** —
  * *Data Sanitization & Strict Zero-Leakage Partitioning (72/8/20 Split)*
  * *Pillar 1: Adversarial Stability SHAP (80% Cumulative Stability Mass)*
  * *Pillar 2: Two-Phase Dynamic Adversarial Training (Warmup + 5-step Online PGD)*
* **6. Dataset & Environment** — CSE-CIC-IDS2018 (6.32M flows) & AMD RX 7600 ROCm stack
* **7. Target Model Architecture** — 4-layer MLP topology & design parameters
* **8. Weekly Research Timeline & Gantt Chart** — Progress from July 4 to October 11
* **9. Expected Results & Research Hypotheses** — Performance targets & multi-threat evaluation protocol
* **10. Conclusion & Immediate Next Steps** — Core contributions & execution roadmap

---

### Slide 3: Problem Statement
* **The Vulnerability of Machine Learning NIDS:**
  * Modern Deep Neural Networks achieve **$> 95\%$ accuracy** on normal traffic.
  * However, detection collapses down to **$\sim 30\%$** when attackers make tiny, undetectable packet tweaks.
* **How the Attack Works (Evasion):**
  * Attackers slightly alter flow timing, byte counts, and packet sizes.
  * **Consequence:** The AI is tricked into classifying dangerous cyber attacks as harmless normal traffic.
* **Root Causes in Current Systems:**
  * **Fragile Features:** Classifiers rely on weak traffic clues that attackers can easily disguise.
  * **Shortcut Cheating:** Models memorize IP addresses and port numbers instead of learning real attack behavior.
  * **Stale Defenses:** Existing defenses train once on old attacks, making them helpless against adaptive, modern attackers.

---

### Slide 4: Motivation & Research Objectives
* **1. Real-Time Line-Rate Speed (< 0.05 ms):**
  * High-speed networks cannot wait: slow detection creates bottlenecks and drops valid packets.
  * **Goal:** Maintain sub-0.05 ms per-flow inference so network traffic moves at full line-rate speed.
* **2. No Accuracy Penalty:**
  * Defending models against attacks usually causes a 2% to 6% drop in normal traffic accuracy.
  * **Goal:** Stop adversarial attacks without sacrificing normal classification performance by filtering out noisy features.
* **3. Honest Security (No Shortcuts):**
  * Real attackers switch ports and spoof IP addresses in seconds.
  * **Goal:** Permanently remove all IP and port shortcuts so the AI learns real attack behavior, with strict zero-leakage testing.

---

### Slide 5: Literature Review (Part 1): Taxonomy of Published Defenses

* **Header Title:** Literature Review
* **Subtitle:** Published defense paradigms, benchmark methods, and operational trade-offs.

| Ref | Published Method | Defense Paradigm | Benchmark Result | Critical Bottleneck |
| :---: | :--- | :--- | :---: | :--- |
| **[1]** | **Static Triad Augmentation** | Offline Static Augmentation | 88.0% Defended | Offline attack staleness; retained port shortcuts |
| **[2]** | **AMDS (Adaptive Multi-Stage)** | Dynamic Minimax PGD Hardening | 89.4% $\text{PGD}_{20}$ | 2.1% clean drop; unpruned 78-dim overhead (+140% GPU) |
| **[3]** | **XAI-Centroid Gate** | Runtime Attribution (SHAP) | 88.5% Detection | Severe latency (85–220 ms/flow); violates line-rate |
| **[4]** | **CSAGC-IDS** | Channel-Spatial Graph Attention | 76.2% Robust | Buffering delay (>2.4 ms); graph topology spoofing |
| **[7]** | **Randomized Smoothing** | Certified Provable $L_2$ Radius | Provable Guarantees | Clean accuracy crash: 94.5% → 76.2% (-18.3% drop) |

* **Key Literature Finding:** Existing defenses force an unresolved trade-off: offline methods suffer attack staleness, runtime defenses violate line-rate throughput, and certified methods severely penalize clean traffic.

---

### Slide 6: Literature Review (Part 2): Core Research Gaps & Structural Vulnerabilities

* **Header Title:** Literature Review
* **Subtitle:** Three structural vulnerabilities identified across existing NIDS defenses.

* **1. Perturbation Staleness (Offline Augmentation Vulnerability) `[1]`:**
  * *Mechanism:* Defenses like Static Triad inject pre-computed static attack samples once before retraining.
  * *Vulnerability:* As neural weights evolve during training, the decision boundary shifts away from static samples, allowing dynamic adaptive attacks to easily evade the model (16%–20% evasion rate).
* **2. The Line-Rate Latency Barrier (Runtime Defense Vulnerability) `[3, 4]`:**
  * *Mechanism:* Complex runtime verifications like real-time SHAP gates (85–220 ms) `[3]` and graph batch buffering (>2.4 ms) `[4]` introduce heavy computational overhead.
  * *Vulnerability:* High-speed cloud switches operate on microsecond scales (<0.05 ms); multi-millisecond per-flow processing causes buffer overflow and packet drops.
* **3. Shortcut Learning & Nominal Attribution Bias (Feature Selection Vulnerability) `[1, 18]`:**
  * *Mechanism:* Conventional feature selection evaluates feature importance exclusively on benign, nominal traffic.
  * *Vulnerability:* Models retain ephemeral socket shortcuts (`Src/Dst Port`, `IP`) and gradient-volatile features that attackers trivially manipulate to bypass detection.

---

### Slide 7: Comparative Analysis

* **Header Title:** Comparative Analysis
* **Subtitle:** State-of-the-art benchmark frontiers: Every published defense faces a critical trade-off.

| Benchmark Frontier | Published Method & Ref | Best Result | Defense Mechanism | Limitation |
| :--- | :--- | :---: | :--- | :--- |
| **Best Clean Accuracy** | **Deep MLP [5] / CSAGC-IDS [4]** | **98.2%** Clean | Standard Deep MLP / Graph Attention | **Zero Defense:** Collapses to **<32%** under white-box PGD attacks; or incurs 2.4 ms graph delay. |
| **Best White-Box Robustness** | **AMDS [2]** | **89.4%** $\text{PGD}_{20}$ | Multi-Stage Dynamic PGD | **Clean Drop & Overhead:** Suffers **2.1% clean penalty**; keeps all 78 dimensions (+140% GPU cost). |
| **Best Static Defense (Base Paper)** | **Static Triad [1]** | **88.0%** Defended | Static Triad Augmentation | **Staleness & Shortcuts:** Offline attacks go stale (16–20% evasion); retained port shortcuts. |
| **Best Black-Box Robustness** | **Query Anomaly Tracker [6]** | **88.6%** Black-Box | Query Perturbation & Anomaly Tracking | **High Complexity:** Requires stateful query tracking; vulnerable to adaptive white-box transfer. |
| **Best Certified Defense** | **Randomized Smoothing [7]** | **Provable $L_2$ Radius** | Randomized Smoothing | **Severe Accuracy Crash:** Clean accuracy dropped from **94.5% → 76.2%** (-18.3% penalty). |

* **The Literature Dilemma:** Across published literature, no existing system achieves high robustness without suffering a severe penalty in clean accuracy, latency, or computational complexity.

---

### Slide 8: Proposed Methodology (Part 1): Data Sanitization & Screening
* **1. Data Sanitization (Engelen 2021 & Arp 2022 Guidelines):**
  * Permanently remove non-generalizable socket shortcuts: `Src IP`, `Dst IP`, `Src Port`, `Dst Port`, `Timestamp`, `Flow ID`.
  * **Result:** **69 continuous numerical features** capturing intrinsic flow dynamics (packet lengths, inter-arrival times, byte rates).
* **2. Strict Zero-Leakage Partitioning:**
  * Initial split: **80% Development Partition** (5,056,002 flows) and **20% Held-Out Test Set** (1,264,001 flows) locked on Day 0.
  * Sub-partition Development set (90/10): **72% Core Training** (4,550,401 flows) and **8% Validation** (505,601 flows).
  * *Zero Leakage Protocol:* Normalization parameters ($\mu, \sigma$) are fitted strictly on the 72% Core Training split; test data is never observed.
* **3. Coarse Candidate Screening (Mutual Information):**
  * Shannon Mutual Information filters uninformative noise from 69 dimensions to **top 40 candidate features**:
    $$I(X_j; Y) = H(Y) - H(Y \mid X_j)$$
  * Preserves physical feature semantics (unlike PCA) and accelerates downstream Shapley computation by over 60%.
* **4. Continuous-Only SMOTE Balancing:**
  * Applied strictly within $\mathcal{D}_{\text{train}}$ to continuous numerical features to balance minority attacks without interpolating discrete flags.

---

### Slide 9: Proposed Methodology (Part 2): Pillar 1 — Adversarial Stability SHAP
* **The Vulnerability of Clean-Only Feature Selection:**
  * Clean-only feature selection evaluates importance solely on nominal data.
  * **Vulnerability:** Features with high clean attribution may have steep local gradient slopes, allowing attackers to manipulate them with minimal perturbation.
* **The Dual-State Attribution Auditing Procedure:**
  * Train an unhardened baseline canary model on clean training data across the 40 candidate features.
  * Subject the model to 20-step PGD perturbations ($\text{PGD}_{20}, \epsilon = 0.05$).
  * Compute mean absolute Shapley values on clean flows ($\bar{\phi}^{\text{clean}}_j$) and perturbed flows ($\bar{\phi}^{\text{adv}}_j$).
* **The Exact Mathematical Stability Score ($S_j$):**
  $$S_j = 1 - \frac{|\bar{\phi}^{\text{clean}}_j - \bar{\phi}^{\text{adv}}_j|}{\max(\bar{\phi}^{\text{clean}}_j + \bar{\phi}^{\text{adv}}_j, 10^{-10})}$$
* **The 80% Cumulative Stability-Mass Selection Rule:**
  * Compute total stability mass: $S_{\text{total}} = \sum_{k=1}^{40} S_k$.
  * Rank candidate features in descending order of $S_j$ and select the minimal subset $m$ satisfying:
    $$\min m \quad \text{s.t.} \quad \sum_{j=1}^m S_j \ge 0.80 \cdot S_{\text{total}}$$
  * **Outcome:** Exactly **27 stable features** are selected, pruning the 13 most gradient-volatile dimensions to form $\mathbf{P} \in \mathbb{R}^{27 \times 69}$.

---

### Slide 10: Proposed Methodology (Part 3): Pillar 2 — Two-Phase Dynamic Hardening
* **Curriculum Optimization Rationale:**
  * Injecting strong perturbations from Epoch 1 into randomly initialized weights creates chaotic loss gradients, destabilizing representation formation and leading to clean accuracy degradation.
* **Phase 1: Representation Warmup (Epochs 1 to 10):**
  * Train exclusively on clean data using standard cross-entropy loss:
    $$\mathcal{L}_{\text{clean}} = -\sum y_c \log f_\theta(x)_c$$
  * Settle network weights into a well-conditioned local loss basin where benign and attack classes form distinct geometric clusters.
* **Phase 2: Dynamic Online Hardening (Epochs 11 to 50):**
  * For every mini-batch, generate fresh **5-step online PGD perturbations** on the GPU using current weights:
    $$x^{t+1} = \Pi_{x + \mathcal{S}} \left( x^t + \alpha \cdot \text{sign}\left(\nabla_x \mathcal{L}(f_\theta(x^t), y)\right) \right), \quad \epsilon = 0.05, \; \alpha = 0.005$$
  * Updates model parameters via a balanced joint objective:
    $$\mathcal{L}_{\text{total}} = 0.5 \cdot \mathcal{L}_{\text{clean}}(f_\theta(x), y) + 0.5 \cdot \mathcal{L}_{\text{adv}}(f_\theta(x_{\text{adv}}), y)$$
  * **Result:** Mitigates static attack staleness while preserving benign representation anchors.

---

### Slide 11: Dataset & Environment
* **1. Benchmark Dataset (CSE-CIC-IDS2018):**
  * Industry-standard collaborative benchmark: **14 attacks across 7 threat profiles** (evaluated as binary classification).
  * **Curation Source:** Standardized `dhoogla/csecicids2018` Parquet curation [19] (replaces raw 250 GB uncurated dump to resolve corrupted headers and NaN flaws while guaranteeing 100% reproducibility).
  * Total valid flow volume: **6,320,003 flows** (post-sanitization & invalid row removal).
  * Partition breakdown:
    * **72% Core Train:** **4,550,401 flows**
    * **8% Validation:** **505,601 flows**
    * **20% Frozen Test:** **1,264,001 flows**
* **2. Hardware & Software Platform:**
  * **GPU Platform:** AMD Radeon RX 7600 (8 GB VRAM, RDNA 3 architecture).
  * **Software Stack:** Python 3.10, PyTorch with native ROCm acceleration on Windows, Adversarial Robustness Toolbox (ART).
  * **Batch Optimization:** Vectorized GPU tensor operations ($B = 2048$), mixed-precision execution (~70 min for 50 epochs).
* **3. Target Model Architecture:**
  * **Topology:** 4-Layer Multi-Layer Perceptron: $\mathbf{27} \to \mathbf{128} \to \mathbf{64} \to \mathbf{32} \to \mathbf{2}$.
  * **Layer Design:** Linear $\to$ Batch Normalization $\to$ ReLU Activation $\to$ Dropout ($p = 0.30$).
  * **Complexity:** Compact feed-forward pass (~14,000 parameters) ensuring high GPU throughput.

---

### Slide 12: Weekly Research Timeline & Gantt Chart

```
Task Name / Week          W1   W2   W3   W4   W5   W6   W7   W8   W9   W10  W11  W12  W13  W14
------------------------------------------------------------------------------------------------
1. Topic Selection       [====]
2. Literature Review          [=========]
3. Base Paper Selection            [====]
4. Methodology Study                    [=========]
5. Limitation Identification                 [====]
6. Environment Setup                              [====]
7. Pre-Defense Prep                                    [=========] (★ Sep 10 - Milestone)
8. Implementation                                                [====]
9. Empirical Evaluation                                               [====]
10. Result Analysis & Comparison                                           [====]
11. Thesis Manuscript Drafting                                                  [=========]
12. Supervisor Review & Revisions                                                    [====]
13. Final Thesis Defense                                                                  [★ Oct 11]
```

* **Current Status (September 10, 2026):**
  * Tasks 1 through 7 are complete (Theoretical formulation, literature audit, data ingestion pipeline, and GPU environment verified).
  * Pre-defense milestone achieved; immediately transitioning to multi-threat evaluation (Weeks 11–12) and final manuscript submission (Weeks 13–14).

---

### Slide 13: Expected Results & Research Hypotheses
* **1. Classification Performance Targets (Hypotheses):**
  * **Target Clean Accuracy:** $\ge 95.5\%$ (Hypothesizing that pruning 13 unstable features mitigates clean accuracy degradation).
  * **Target Robust Accuracy ($\text{PGD}_{100}, \epsilon = 0.05$):** $88.0\% - 90.5\%$ (vs. undefended baselines expected to exhibit severe degradation).
  * **Target Attack Success Rate (ASR):** $< 12.0\%$ under iterative white-box gradient attacks.
* **2. Comprehensive Multi-Threat Evaluation Suite:**
  * **First-Order Gradient & Boundary Attacks:** FGSM, DeepFool (minimum-distance boundary perturbation), $\text{PGD}_{20}$, $\text{PGD}_{100}$, BIM.
  * **Optimization & Parameter-Free Attacks:** Auto-PGD (APGD-CE), Carlini-Wagner ($\ell_\infty$).
  * **Decision-Based & Black-Box Attacks:** Square Attack (query-based), Surrogate Model Transferability.
* **3. Verification Against Gradient Obfuscation:**
  * Validate that robustness is genuine and not caused by gradient masking (verifying non-zero input gradients and evaluating black-box transferability).
* **4. Operational Latency Target:**
  * **Target Inference Speed:** Sub-0.05 ms amortized per flow (preliminary GPU batch benchmarks: $<0.02$ ms/flow).

---

### Slide 14: Conclusion & Immediate Next Steps
* **Summary of Proposed Contributions:**
  * **Robust Feature Selection & SMOTE Balancing:** Formulates Adversarial Stability SHAP (80% stability rule isolating 27 invariant features) combined with leak-free SMOTE class balancing strictly inside the training split.
  * **Two-Phase Dynamic Adversarial Training:** Proposes representation warmup (Epochs 1–10) followed by live 5-step online PGD mini-batch hardening (Epochs 11–50) to track moving decision boundaries and eliminate attack staleness.
  * **Comprehensive Multi-Threat Evaluation:** Rigorous robustness verification across diverse attack modalities (FGSM, DeepFool, PGD, CW, Square Attack) with zero socket-shortcut leakage.
* **Immediate Next Milestones (Sept 11 – Oct 11):**
  * Execute 3-seed experimental runs across all 9 adversarial threat models.
  * Conduct ablation studies: (1) Full 69D vs. 40D MI vs. 27D Stable; (2) Static Triad vs. Dynamic PGD.
  * Complete and submit the final undergraduate B.Sc. thesis manuscript for October defense.

---

### Slide 15: References (Academic Bibliography)

* **[1]** Holla, Polepalli, & Sasikumar, "Adversarial Threats to Cloud IDS: Robust Defense With Adversarial Training and Feature Selection," *IEEE Access*, vol. 13, 2025.
* **[2]** Olukola & Rahimi, "Adversarial Hardening of Deep Neural Network-Based Network Intrusion Detection Systems," *IEEE Transactions on Information Forensics and Security*, vol. 21, 2026.
* **[3]** Güvenç Paltun et al., "Real-Time Explainable AI Gate for Detecting Adversarial Perturbations in Network Intrusion Detection," *IEEE Transactions on Reliability*, 2025.
* **[4]** Zeng et al., "CSAGC-IDS: Channel-Spatial Attention Graph Convolutional Network for Intrusion Detection," *IEEE Internet of Things Journal*, 2025.
* **[5]** Roshan et al., "Empirical Robustness Limits of Deep Learning Network Intrusion Detection Systems," *IEEE Access*, 2023.
* **[6]** Ennaji et al., "Black-Box Adversarial Detection via Stateful Query Profiling in Deep IDS," *IEEE Transactions on Information Forensics and Security*, 2025.
* **[7]** Zhou et al., "Provable Certified Robustness Guarantees for Deep Tabular Anomaly Detectors," *IEEE Transactions on Dependable and Secure Computing*, 2023.
* **[8]** Madry, Makelov, Schmidt, Tsipras, & Vladu, "Towards Deep Learning Models Resistant to Adversarial Attacks," in *International Conference on Learning Representations (ICLR)*, 2018.
* **[9]** Goodfellow, Shlens, & Szegedy, "Explaining and Harnessing Adversarial Examples," in *International Conference on Learning Representations (ICLR)*, 2015.
* **[10]** Zhang, Yu, Jiao, Xing, El Ghaoui, & Jordan, "Theoretically Principled Trade-off between Robustness and Accuracy (TRADES)," in *International Conference on Machine Learning (ICML)*, 2019.
* **[11]** Lundberg & Lee, "A Unified Approach to Interpreting Model Predictions (SHAP)," in *Advances in Neural Information Processing Systems (NeurIPS)*, 2017.
* **[12]** Athalye, Carlini, & Wagner, "Obfuscated Gradients Give a False Sense of Security: Circumventing Defenses to Adversarial Examples," in *International Conference on Machine Learning (ICML)*, 2018.
* **[13]** Andriushchenko, Croce, Flammarion, & Hein, "Square Attack: A Query-Efficient Black-Box Adversarial Attack via Random Search," in *European Conference on Computer Vision (ECCV)*, 2020.
* **[14]** Brendel, Rauber, & Bethge, "Decision-Based Adversarial Attacks: Reliable Attacks Against Black-Box Models," in *International Conference on Learning Representations (ICLR)*, 2018.
* **[15]** Chawla, Bowyer, Hall, & Kegelmeyer, "SMOTE: Synthetic Minority Over-Sampling Technique," *Journal of Artificial Intelligence Research*, vol. 16, 2002.
* **[16]** Sharafaldin, Lashkari, & Ghorbani, "Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization (CSE-CIC-IDS2018)," in *Proc. ICISSP*, 2018.
* **[17]** Tsipras, Santurkar, Engstrom, Turner, & Madry, "Robustness May Be at Odds with Accuracy," in *International Conference on Learning Representations (ICLR)*, 2019.
* **[18]** Engelen et al., "Troubleshooting the Flaws of Machine Learning in Network Intrusion Detection," in *ACM Conference on Computer and Communications Security (CCS)*, 2021.
* **[19]** D'hooge, Wauters, Volckaert, & De Turck, "CSE-CIC-IDS2018 on AWS (Standardized Parquet Curation)," Hugging Face Dataset (dhoogla/csecicids2018), 2020/2023.

