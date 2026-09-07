# SLIDE CONTENTS ONLY (Pre-Defense Presentation — 14 Slides)
## Focused Pre-Defense Deck: Expanded Literature Review (2 Slides) & In-Depth Methodology (3 Slides)

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

### Slide 5: Literature Review (Part 1): Current Research Landscape & Empirical Findings
* **Scope of Survey:** Comprehensive analysis of **40 peer-reviewed publications (2021–2026)** spanning deep learning NIDS, adversarial hardening, and Explainable AI (SHAP).
* **Macro Empirical Findings Across the Literature:**
  * **1. Clean Accuracy Trade-Off in Literature:**  
    Several published studies observe that applying adversarial training to unpruned feature spaces leads to an empirical clean accuracy drop of $2\%$ to $6\%$ (e.g., Olukola & Rahimi reported a 2.1% drop from 96.9% to 94.8%), reflecting Tsipras' trade-off when noisy dimensions remain intact.
  * **2. Vulnerability of Tree Ensembles:**  
    Tree-based ensemble models (Random Forest, XGBoost) achieve high clean accuracy but often suffer substantial accuracy degradation under iterative gradient perturbations ($>80\%$ Attack Success Rate in benchmark evaluations) due to non-differentiable step boundaries.
  * **3. Static Perturbation Staleness:**  
    Offline data augmentation (generating fixed adversarial samples prior to training) often exhibits reduced effectiveness against adaptive attacks ($16\%$ to $20\%$ evasion reported in peer studies), as static samples do not track evolving decision boundaries.
  * **4. Inference Latency Overhead in Complex Architectures:**  
    Architectures incorporating runtime XAI verification (85–220 ms/flow) or dynamic graph window accumulation (>2.4 ms/flow) can introduce substantial latency overhead relative to real-time line-rate constraints ($<0.05$ ms).
  * **5. Shortcut Memorization & Clean-Only Bias:**  
    Conventional feature selection methods (Gini impurity, clean SHAP) evaluate features solely on nominal traffic, frequently retaining port numbers that act as fragile back doors under perturbation.

---

### Slide 6: Literature Review (Part 2): Landmark Peer Benchmarks & Defense Paradigms
* **1. Feature Selection + Static Adversarial Training (Holla et al., IEEE Access 2025 — Base Paper):**
  * *Architecture & Method:* 3-layer MLP (128-64-32); clean SHAP ranking of top 8 features; static triad augmentation (10k FGSM, 10k PGD, 10k DeepFool).
  * *Results:* Baseline 85% clean drops to 55% under PGD and 50% under DeepFool; defense restores accuracy to 88% gradient and 84% Square Attack (11 ms latency).
  * *Reported Limitations:* **Static attack staleness** (pre-generated perturbations may lose efficacy as weights evolve) and **port retention** (Src/Dst Port explicitly retained).
* **2. Multi-Stage Dynamic Hardening (Olukola & Rahimi, IEEE TIFS 2026 — AMDS):**
  * *Architecture & Method:* 4-layer MLP backbone; clean warmup (15 epochs) followed by dynamic PGD with adaptive clean/adversarial loss scheduling.
  * *Results:* Achieves 94.8% clean accuracy (-2.1% penalty) and 89.4% robust accuracy under PGD-20 (0.08 ms inference latency).
  * *Reported Limitations:* Operates across all 78 dimensions without feature selection (+140% training overhead); provides limited attribution explainability.
* **3. Real-Time Explainable AI Gate (Güvenç Paltun et al., IEEE Trans. Rel. 2025):**
  * *Architecture & Method:* Deep Neural Network paired with runtime SHAP cosine similarity verification against clean centroids.
  * *Results:* 95.1% clean accuracy; detects 88.5% of FGSM/PGD perturbations.
  * *Reported Limitations:* **High runtime latency** (85–220 ms per flow); susceptible to attribution scaffolding attacks.
* **4. Dynamic Graph Attention IDS (Zeng et al., IEEE IoTJ 2025 — CSAGC-IDS):**
  * *Architecture & Method:* Dual-module channel-spatial attention over dynamic inter-host communication graphs.
  * *Results:* 97.4% clean accuracy; 76.2% robust accuracy under graph topology evasion.
  * *Reported Limitations:* Time-window batch accumulation delay (>2.4 ms per flow); vulnerable to dummy-edge connection spoofing.

---

### Slide 7: Comparative Analysis

* **Header Title:** Comparative Analysis
* **Subtitle:** Empirical benchmarks across 40 surveyed papers: Every best result has a limitation.

| Benchmark Frontier | Published Paper | Best Result | Defense Mechanism | Limitation |
| :--- | :--- | :---: | :--- | :--- |
| **Best Clean Accuracy** | *Roshan et al. (2023) / Zeng et al. (2025)* | **98.2%** Clean | Standard Deep MLP / Graph Attention | **Zero Defense:** Collapses to **<32%** under white-box PGD attacks; or incurs 2.4 ms graph delay. |
| **Best White-Box Robustness** | *Olukola & Rahimi (IEEE TIFS 2026)* | **89.4%** PGD₂₀ | Multi-Stage Dynamic PGD | **Clean Drop & Overhead:** Suffers **2.1% clean penalty**; keeps all 78 dimensions (+140% GPU cost). |
| **Best Static Defense (Base Paper)** | *Holla et al. (IEEE Access 2025)* | **88.0%** Defended | Static Triad Augmentation | **Staleness & Shortcuts:** Offline attacks go stale (16–20% evasion); retained port shortcuts. |
| **Best Black-Box Robustness** | *Ennaji et al. (IEEE TIFS 2025)* | **88.6%** Black-Box | Query Perturbation & Anomaly Tracking | **High Complexity:** Requires stateful query tracking; vulnerable to adaptive white-box transfer. |
| **Best Certified Defense** | *Zhou et al. (IEEE TDSC 2023)* | **Provable $L_2$ Radius** | Randomized Smoothing | **Severe Accuracy Crash:** Clean accuracy dropped from **94.5% → 76.2%** (-18.3% penalty). |

* **The Literature Dilemma:** Across 40 surveyed papers, no existing system achieves high robustness without suffering a severe penalty in clean accuracy, latency, or computational complexity.

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
  * **Curation Source:** Standardized `dhoogla/csecicids2018` Parquet curation (replaces raw 250 GB uncurated dump to resolve corrupted headers and NaN flaws while guaranteeing 100% reproducibility).
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
  * **First-Order Gradient Attacks:** FGSM, $\text{PGD}_{20}$, $\text{PGD}_{100}$, BIM.
  * **Parameter-Free & Optimization Attacks:** Auto-PGD (APGD-CE), Carlini-Wagner ($\ell_\infty$).
  * **Decision-Based & Black-Box Attacks:** Square Attack (query-based), Surrogate Model Transferability.
* **3. Verification Against Gradient Obfuscation:**
  * Validate that robustness is genuine and not caused by gradient masking (verifying non-zero input gradients and evaluating black-box transferability).
* **4. Operational Latency Target:**
  * **Target Inference Speed:** Sub-0.05 ms amortized per flow (preliminary GPU batch benchmarks: $<0.02$ ms/flow).

---

### Slide 14: Conclusion & Immediate Next Steps
* **Summary of Proposed Contributions:**
  * **Theoretical Contribution:** Formulates Adversarial Stability SHAP with an 80% cumulative stability-mass selection rule, isolating a 27-dimensional perturbation-invariant subspace.
  * **Architectural Contribution:** Proposes a two-phase dynamic training curriculum (clean warmup + 5-step online PGD, $\alpha = 0.005$) to reduce the effect of static attack staleness while preserving benign representation geometry.
  * **Methodological Hygiene:** Permanently removes socket shortcut leakage and enforces strict zero-leakage 72/8/20 partitioning on 6.32M valid flows.
* **Immediate Next Milestones (Sept 11 – Oct 11):**
  * Execute 3-seed experimental runs across all 9 adversarial threat models.
  * Conduct ablation studies: (1) Full 69D vs. 40D MI vs. 27D Stable; (2) Static Triad vs. Dynamic PGD.
  * Complete and submit the final undergraduate B.Sc. thesis manuscript for October defense.
