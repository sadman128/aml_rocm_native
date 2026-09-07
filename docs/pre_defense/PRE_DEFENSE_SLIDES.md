# Undergraduate B.Sc. Pre-Defense Presentation: 14-Slide Complete Guide
## "Adversarial Robustness in Network Intrusion Detection Systems via Attribution-Guided Feature Selection and Dynamic Multi-Stage Adversarial Training"

> **Pre-Defense Presentation Instructions:**
> * **Target Duration:** 6–7 Minutes total (Redoan: Slides 1–7, Sadman: Slides 8–14).
> * **Degree:** Bachelor of Science (B.Sc.) in Computer Science & Engineering.
> * **Structure:** 11 core sections, with expanded focus on **Literature Review (2 slides)** and **Proposed Methodology (3 slides)**.
> * **Audience:** Academic Defense Committee / Research Supervisors.
> * **Key Pre-Defense Rule:** The board evaluates the **soundness of your proposal, research gaps, methodology, and feasibility**. All results are framed as **hypothesized targets and theoretical expectations**; do not state that the code has already been fully executed.
> * **Every slide below includes:**
>   1. **Slide Metadata & Visual Layout Advice** (How to format the slide visually).
>   2. **On-Slide Content** (Bullet points, tables, diagrams simplified for maximum clarity).
>   3. **🗣️ Speaker Notes / Spoken Script** (Conversational, viva-ready explanation).

---

## Slide 1: Title Page

### 📐 Layout & Visual Suggestion
* Clean, professional academic template (navy blue `#0f2440` and royal blue `#2563eb` accents).
* University logo top-left; Date and Candidate/Supervisor credentials bottom-center.

### 📄 On-Slide Content
* **Title:**  
  # Adversarial Robustness in Network Intrusion Detection Systems via Attribution-Guided Feature Selection and Dynamic Multi-Stage Adversarial Training
* **Subtitle:** Pre-Defense Presentation / Undergraduate B.Sc. Thesis Proposal
* **Candidate Name:** [Your Name / Student ID]
* **Supervisor:** [Supervisor Name & Title]
* **Department:** Department of Computer Science & Engineering
* **Date:** September 10, 2026

### 🗣️ Speaker Notes (Spoken Script — 30 seconds)
> "Honorable members of the defense committee and respected supervisors, good morning. Today, I am presenting my pre-defense thesis proposal entitled: *'Adversarial Robustness in Network Intrusion Detection Systems via Attribution-Guided Feature Selection and Dynamic Multi-Stage Adversarial Training'*.
> 
> Over the past ten weeks, I have investigated why modern deep learning intrusion detection systems exhibit vulnerability to bounded adversarial perturbations, audited critical structural gaps across peer-reviewed literature, and formulated a novel two-pillar defense pipeline. Today, I will walk you through the research problem, our methodology, our experimental environment, and our timeline toward the final thesis defense in October."

---

## Slide 2: Presentation Outline

### 📐 Layout & Visual Suggestion
* 2-column agenda list with sequential numbered milestone badges matching the 11 required presentation topics.

### 📄 On-Slide Content
1. **Research Context & Problem Statement** — Vulnerability of deep NIDS to bounded perturbations
2. **Motivation & Research Objectives** — Addressing the accuracy vs. robustness trade-off
3. **Literature Review** — Current research findings & landmark peer defenses (2021–2026)
4. **Comparative Analysis & Research Gaps** — Structural limitations & what our work addresses
5. **Proposed Methodology** —
   * *Data Sanitization & Strict Zero-Leakage Partitioning (72/8/20 Split)*
   * *Pillar 1: Adversarial Stability SHAP (80% Cumulative Stability Mass)*
   * *Pillar 2: Two-Phase Dynamic Adversarial Training (Warmup + 5-step Online PGD)*
6. **Dataset & Computing Environment** — CSE-CIC-IDS2018 (6.32M flows) & AMD RX 7600 ROCm stack
7. **Target Model Architecture** — 4-layer MLP topology & design parameters
8. **Weekly Research Timeline & Gantt Chart** — Progress from July 4 to October 11
9. **Expected Results & Research Hypotheses** — Performance targets & multi-threat evaluation protocol
10. **Conclusion & Immediate Next Steps** — Core contributions & execution roadmap

### 🗣️ Speaker Notes (Spoken Script — 30 seconds)
> "Here is an outline of today's presentation. We begin with the security challenge in network intrusion detection and formulate our research objectives.
> 
> Next, we review the literature landscape and our direct peers, clearly identifying the research gaps.
> 
> I then dedicate deep technical focus to our proposed methodology: data sanitization, our game-theoretic Adversarial Stability SHAP pillar, and our two-phase dynamic hardening curriculum. Finally, I detail our experimental setup, timeline, and hypothesized outcomes."

---

## Slide 3: Problem Statement

### 📐 Layout & Visual Suggestion
* 2-column layout:
  * Left: Performance graphic (95% Clean Acc → ~30% Robust Acc) & Evasion description.
  * Right: 3 root cause cards (Fragile Features, Shortcut Cheating, Stale Defenses).

### 📄 On-Slide Content
* **The Problem: AI Firewalls Fail Under Tiny Cyber Attacks**
  * Modern Deep Neural Networks achieve **$> 95\%$ accuracy** on normal network traffic.
  * However, detection collapses down to **$\sim 30\%$** when attackers make tiny, undetectable packet tweaks.
* **How the Attack Works (Evasion):**
  * Attackers slightly alter packet timing, flow duration, or byte sizes.
  * **Consequence:** The AI is tricked into classifying dangerous cyber attacks as harmless normal traffic.
* **Three Root Causes in Current Systems:**
  * **1. Fragile Features:** Classifiers rely on weak traffic clues that attackers can easily disguise.
  * **2. Shortcut Cheating:** Models cheat by memorizing port numbers and IP addresses instead of learning real attack behavior.
  * **3. Stale Defenses:** Existing defenses train only once on old attacks, making them helpless against adaptive, modern attackers.

### 🗣️ Speaker Notes (Spoken Script — 35 seconds)
> "Deep learning intrusion detection systems look great on paper, achieving over **95% accuracy** on normal traffic.  
> But in reality, they have a fatal flaw: when an attacker makes tiny, invisible tweaks to network packets, accuracy collapses from **95% down to about 30%**.  
> Why does this happen? Three main reasons:  
> **1. Fragile Features:** The AI relies on weak traffic clues that attackers can easily disguise.  
> **2. Shortcut Cheating:** Models cheat by memorizing port numbers and IP addresses instead of learning real attack patterns.  
> **3. Stale Defenses:** Existing defenses train only once on old attacks, making them helpless against adaptive, modern attackers."

---

## Slide 4: Motivation & Research Objectives

### 📐 Layout & Visual Suggestion
* 3 highlight cards emphasizing Line-Rate Feasibility, Zero Accuracy Penalty, and Honest Security.

### 📄 On-Slide Content
* **Building Fast, Accurate, and Honest AI Defense**
  * Why this research matters and what engineering goals we must achieve.
* **1. Real-Time Line-Rate Speed (< 0.05 ms):**
  * High-speed networks cannot wait: slow detection creates bottlenecks and drops valid packets.
  * **Goal:** Maintain sub-0.05 ms per-flow inference so network traffic moves at full line-rate speed.
* **2. No Accuracy Penalty:**
  * Defending models against attacks usually causes a **2% to 6% drop** on normal traffic accuracy.
  * **Goal:** Stop adversarial attacks without sacrificing normal classification performance by filtering out noisy features.
* **3. Honest Security (No Shortcuts):**
  * Real attackers switch ports and spoof IP addresses in seconds.
  * **Goal:** Permanently remove all IP and port shortcuts so the AI learns real attack behavior, with strict zero-leakage testing.

### 🗣️ Speaker Notes (Spoken Script — 25 seconds)
> "To solve these three problems, our research is driven by three practical goals:  
> **1. Real-Time Speed:** In high-speed cloud networks, detection must take less than **0.05 milliseconds** per flow so we never delay or drop valid packets.  
> **2. No Accuracy Penalty:** Usually, defending a model against attacks causes a **2% to 6% drop** on normal traffic. Our goal is to defend against attacks *without* sacrificing normal performance by filtering out noisy features.  
> **3. Honest Security:** Real attackers switch ports and spoof IPs constantly. We permanently remove all port and IP shortcuts so our model learns genuine, reliable attack behavior."

---

## Slide 5: Literature Review (Part 1): Current Research Landscape & Empirical Findings

### 📐 Layout & Visual Suggestion
* 5 structured highlight boxes detailing macro findings across the 40 surveyed papers (2021–2026), giving the board a high-level panoramic view of the state of the art.

### 📄 On-Slide Content
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

### 🗣️ Speaker Notes (Spoken Script — 60 seconds)
> "Before examining individual architectures, Slide 5 summarizes what the broader research community has discovered across 40 recent publications between 2021 and 2026.
> 
> Several empirical patterns emerge consistently across the published literature:
> First, multiple studies report that applying adversarial training to unpruned data incurs an accuracy penalty between 2% and 6%, showing that naive hardening distorts decision boundaries on unpruned data.
> 
> Second, tree-based models like Random Forest and XGBoost achieve high clean scores but often show substantial accuracy degradation under iterative PGD because they lack smooth, differentiable margins.
> 
> Third, static offline augmentation frequently suffers from perturbation staleness: fixed attack vectors may lose effectiveness as model weights shift during training.
> 
> Fourth, runtime defenses like on-the-fly SHAP computation or Graph Neural Networks introduce significant latency overhead—taking from 2.4 to 220 milliseconds per flow—which is impractical for high-speed cloud networks.
> 
> Finally, current feature selection methods evaluate only clean traffic, frequently retaining port shortcuts."

---

## Slide 6: Literature Review (Part 2): Landmark Peer Benchmarks & Defense Paradigms

### 📐 Layout & Visual Suggestion
* 4 distinct benchmark cards detailing the exact methodology, results, and critical limitations of direct peer papers.

### 📄 On-Slide Content
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

### 🗣️ Speaker Notes (Spoken Script — 60 seconds)
> "Slide 6 examines the four landmark peer models that directly shape our proposal.
> 
> Our foundational base paper is Holla et al., published in IEEE Access 2025. In their paper, baseline accuracy collapsed from 85% down to 55% under PGD. While their static triad defense recovered accuracy to 88%, they noted static attack staleness, retained source and destination ports, and reported 11 milliseconds of inference latency.
> 
> Olukola & Rahimi, in their 2026 IEEE TIFS paper, introduced AMDS. They showed that a two-stage training schedule—clean warmup followed by dynamic PGD—preserves clean accuracy (achieving 94.8% clean and 89.4% robust). However, they optimize over all 78 raw dimensions without feature pruning, inflating training compute by 140% and offering limited explainability.
> 
> Güvenç Paltun et al. evaluated real-time SHAP gates, but computing explanations on-the-fly takes 85 to 220 milliseconds per flow.
> 
> Finally, Zeng et al. built Graph Neural Networks, but window accumulation creates high latency, and graph structures can be fooled by dummy packets. Our methodology directly unifies the strengths of these works while eliminating their vulnerabilities."

---

## Slide 7: Comparative Analysis

### 📐 Layout & Visual Suggestion
* 5-row comparative benchmark table synthesizing the empirical ceilings and critical bottlenecks across the 40 surveyed papers.

### 📄 On-Slide Content
* **Header Title:** Comparative Analysis
* **Subtitle:** Empirical ceilings in published literature: Every best result has a limitation.

| Benchmark Frontier | Published Paper | Best Result | Defense Mechanism | Limitation |
| :--- | :--- | :---: | :--- | :--- |
| **Best Clean Accuracy** | *Roshan et al. (2023) / Zeng et al. (2025)* | **98.2%** Clean | Standard Deep MLP / Graph Attention | **Zero Defense:** Collapses to **<32%** under white-box PGD attacks; or incurs 2.4 ms graph delay. |
| **Best White-Box Robustness** | *Olukola & Rahimi (IEEE TIFS 2026)* | **89.4%** PGD₂₀ | Multi-Stage Dynamic PGD | **Clean Drop & Overhead:** Suffers **2.1% clean penalty**; keeps all 78 dimensions (+140% GPU cost). |
| **Best Static Defense (Base Paper)** | *Holla et al. (IEEE Access 2025)* | **88.0%** Defended | Static Triad Augmentation | **Staleness & Shortcuts:** Offline attacks go stale (16–20% evasion); retained port shortcuts. |
| **Best Black-Box Robustness** | *Ennaji et al. (IEEE TIFS 2025)* | **88.6%** Black-Box | Query Perturbation & Anomaly Tracking | **High Complexity:** Requires stateful query tracking; vulnerable to adaptive white-box transfer. |
| **Best Certified Defense** | *Zhou et al. (IEEE TDSC 2023)* | **Provable $L_2$ Radius** | Randomized Smoothing | **Severe Accuracy Crash:** Clean accuracy dropped from **94.5% → 76.2%** (-18.3% penalty). |

* **The Literature Dilemma:** Across 40 surveyed papers, no existing system achieves high robustness without suffering a severe penalty in clean accuracy, latency, or computational complexity.

### 🗣️ Speaker Notes (Spoken Script — 30 seconds)
> "When we analyze all 40 papers in the literature, a clear pattern emerges: every best result comes with a serious limitation:  
> 1. Best Clean Accuracy reaches 98.2%, but has zero defense—collapsing to under 32% under attack.  
> 2. Best White-Box Robustness reaches 89.4% under PGD, but causes a 2.1% clean accuracy penalty across 78 dimensions.  
> 3. Our Base Paper achieves 88%, but relies on static offline attacks and keeps port shortcuts.  
> 4. Best Black-Box Robustness reaches 88.6%, but requires heavy stateful query tracking.  
> 5. Certified Defense provably bounds attacks, but clean accuracy crashes by 18% down to 76%.  
>   
> Across the entire literature, no defense achieves high robustness without sacrificing either clean accuracy or real-time speed.  
> Now, Sadman will present how our Proposed Methodology solves this exact dilemma."

---

## Slide 8: Proposed Methodology (Part 1): Data Sanitization & Screening

### 📐 Layout & Visual Suggestion
* 3 sequential process cards: Data Sanitization (Purging Ports) $\to$ Zero-Leakage Split (72/8/20) $\to$ Mutual Information Coarse Filter (69 $\to$ 40).

### 📄 On-Slide Content
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

### 🗣️ Speaker Notes (Spoken Script — 60 seconds)
> "Here is Part 1 of our proposed methodology: data sanitization, zero-leakage splitting, and candidate screening.
> 
> First, following USENIX Security guidelines by Arp et al., we permanently purge non-generalizable socket identifiers—source and destination IPs, timestamps, flow IDs, and port numbers. This leaves 69 continuous numerical features representing true transport behavior, such as packet lengths and inter-arrival times.
> 
> Second, to guarantee zero data leakage, we perform an initial 80/20 train-test split, locking the 1.26 million flow test set on Day 0. The remaining 5.05 million development flows are partitioned 90/10 into 4.55 million core training flows (72%) and 505,000 validation flows (8%). All scalers are fitted strictly on the 72% core training split.
> 
> Third, computing Shapley values across 69 dimensions is computationally heavy. Mutual Information acts as a fast, coarse filter, selecting the top 40 candidate features in seconds while preserving interpretable feature names. Finally, continuous-only SMOTE balances minority attack classes strictly within the training set."

---

## Slide 9: Proposed Methodology (Part 2): Pillar 1 — Adversarial Stability SHAP

### 📐 Layout & Visual Suggestion
* Visual comparison showing Clean SHAP vs. Adversarial Stability SHAP, highlighting the mathematical formula and the 80% cumulative stability-mass selection rule that isolates the 27 stable features.

### 📄 On-Slide Content
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

### 🗣️ Speaker Notes (Spoken Script — 60 seconds)
> "Slide 9 introduces Pillar 1 of our methodology: Adversarial Stability SHAP, which we describe as the 'Earthquake Test'.
> 
> Standard feature selection evaluates importance only on clean data. That can be problematic: a feature might look highly predictive under normal traffic, but if a tiny gradient nudge completely flips its attribution, it serves as an open backdoor for an attacker.
> 
> To detect this vulnerability, we train an unhardened canary model on the 40 candidate features and attack it with 20-step PGD. We compute Shapley attributions on both clean and perturbed traffic, and evaluate their stability using our normalized criterion $S_j$.
> 
> Rather than using an arbitrary flat threshold, we apply the 80% cumulative stability-mass selection rule: we rank candidate features by stability score and retain the minimal subset that captures 80% of the total stability mass. This systematically isolates the 27 most perturbation-stable features while pruning the 13 volatile dimensions."

---

## Slide 10: Proposed Methodology (Part 3): Pillar 2 — Two-Phase Dynamic Hardening

### 📐 Layout & Visual Suggestion
* 2-stage visual timeline:
  * Stage 1: Representation Warmup (Epochs 1–10) with clean cross-entropy.
  * Stage 2: Dynamic Online Hardening (Epochs 11–50) with live 5-step PGD ($\alpha = 0.005$) and joint clean/adversarial loss.

### 📄 On-Slide Content
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

### 🗣️ Speaker Notes (Spoken Script — 60 seconds)
> "Slide 10 details Pillar 2: Two-Phase Dynamic Adversarial Training.
> 
> Naive adversarial training can fail because introducing aggressive perturbations at epoch 1 into randomly initialized weights disrupts representation learning, leading to clean accuracy drops.
> 
> We address this using a structured two-phase curriculum. In Phase 1—warmup for epochs 1 to 10—we train exclusively on clean data. This allows the model to settle into a well-conditioned loss basin where benign and attack classes form separated clusters.
> 
> Then, in Phase 2—epochs 11 to 50—we introduce dynamic online PGD. For every mini-batch, we generate fresh 5-step PGD perturbations on the GPU using current weights, with a calibrated step size of $\alpha = 0.005$. By training with a balanced 50/50 clean and adversarial loss, perturbations actively track the moving decision boundary, reducing static staleness while anchoring clean accuracy."

---

## Slide 11: Dataset, Experimental Environment & Target Architecture

### 📐 Layout & Visual Suggestion
* 3 distinct specification cards: Dataset Statistics, Hardware/Software Stack, and Target Neural Topology.

### 📄 On-Slide Content
* **1. Benchmark Dataset (CSE-CIC-IDS2018):**
  * Industry-standard collaborative benchmark: **14 attacks across 7 threat profiles** (evaluated as binary classification: Benign vs. Malicious).
  * **Curated Source:** Utilizes the standardized `dhoogla/csecicids2018` benchmark curation (D'hooge et al., Hugging Face) instead of the raw ~250 GB uncurated UNB dump, resolving corrupted headers, schema inconsistencies across the 10 recording days, and NaN/Inf values while preserving all 6.32M valid flows.
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

### 🗣️ Speaker Notes (Spoken Script — 45 seconds)
> "Slide 11 details our benchmark dataset, hardware environment, and target architecture.
> 
> We evaluate on CSE-CIC-IDS2018, containing 6.32 million valid flows capturing 14 distinct attack types across 7 threat profiles in a binary classification setup. We specifically use the standardized `dhoogla/csecicids2018` benchmark curation from Hugging Face rather than the raw 250 GB dump to eliminate corrupted headers and schema flaws while guaranteeing 100% reproducibility.
> 
> Our strict zero-leakage partition allocates 4.55 million flows to core training, 505,000 to validation, and 1.26 million to the locked test set.
> 
> All experiments run on an AMD Radeon RX 7600 GPU with 8 GB of VRAM using PyTorch and native ROCm acceleration on Windows. With vectorized batch operations of size 2048, forward and backward passes execute with high efficiency, completing 50 epochs in approximately 70 minutes.
> 
> Our classifier is an ultra-compact 4-layer MLP: 27 inputs, hidden layers of 128, 64, and 32 units with Batch Normalization, ReLU activations, and 30% dropout. With fewer than 15,000 parameters, it delivers high computational efficiency."

---

## Slide 12: Weekly Research Timeline & Gantt Chart

### 📐 Layout & Visual Suggestion
* Clean visual ASCII Gantt chart showing weekly progress from July 4 to October 11, with the current pre-defense milestone clearly highlighted.

### 📄 On-Slide Content

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

### 🗣️ Speaker Notes (Spoken Script — 30 seconds)
> "This Gantt chart shows our weekly timeline from July 4 through to final defense on October 11.
> 
> Today, September 10th, marks our pre-defense milestone at the end of Week 10. Tasks 1 through 7—including topic selection, literature survey, base paper analysis, mathematical formulation, and environment setup—are completed.
> 
> Over the next two weeks, we execute our multi-threat evaluations and ablation studies, leaving Weeks 13 and 14 for manuscript finalization and supervisor review ahead of our October 11 defense."

---

## Slide 13: Expected Results & Research Hypotheses

### 📐 Layout & Visual Suggestion
* 4 structured hypothesis cards: Target Metrics, Multi-Threat Suite, Gradient Obfuscation Checks, and Inference Latency Target.

### 📄 On-Slide Content
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

### 🗣️ Speaker Notes (Spoken Script — 45 seconds)
> "Slide 13 outlines our research hypotheses and evaluation protocol.
> 
> Because this is a proposal defense, our metrics represent testable research hypotheses. We hypothesize a target clean accuracy above 95.5% and a PGD-100 robust accuracy between 88% and 90.5%, cutting attack success rates below 12%.
> 
> To ensure scientific rigor, we will evaluate across 9 distinct adversarial threats, including parameter-free Auto-PGD, Carlini-Wagner, and gradient-free Square Attack.
> 
> Crucially, following Athalye et al., we will conduct diagnostic checks to verify that robustness is not an artifact of gradient masking. Finally, we target sub-0.05 ms inference latency to ensure cloud viability."

---

## Slide 14: Conclusion & Immediate Next Steps

### 📐 Layout & Visual Suggestion
* 2-column closing slide: Summary of Core Contributions on the left, Immediate Execution Milestones on the right.

### 📄 On-Slide Content
* **Summary of Proposed Contributions:**
  * **Theoretical Contribution:** Formulates Adversarial Stability SHAP with an 80% cumulative stability-mass selection rule, isolating a 27-dimensional perturbation-invariant subspace.
  * **Architectural Contribution:** Proposes a two-phase dynamic training curriculum (clean warmup + 5-step online PGD, $\alpha = 0.005$) to reduce the effect of static attack staleness while preserving benign representation geometry.
  * **Methodological Hygiene:** Permanently removes socket shortcut leakage and enforces strict zero-leakage 72/8/20 partitioning on 6.32M valid flows.
* **Immediate Next Milestones (Sept 11 – Oct 11):**
  * Execute 3-seed experimental runs across all 9 adversarial threat models.
  * Conduct ablation studies: (1) Full 69D vs. 40D MI vs. 27D Stable; (2) Static Triad vs. Dynamic PGD.
  * Complete and submit the final undergraduate B.Sc. thesis manuscript for October defense.

### 🗣️ Speaker Notes (Spoken Script — 30 seconds)
> "To conclude, our undergraduate B.Sc. thesis proposal introduces two complementary pillars: Adversarial Stability SHAP to isolate an invariant 27-dimensional feature space, and two-phase dynamic adversarial training to harden decision boundaries while reducing static attack staleness.
> 
> Our immediate next steps are executing multi-seed experiments across all 9 attack vectors, performing ablation studies, and completing the thesis book for our October defense.
> 
> Thank you, honorable committee members. We are now ready to take your questions."




