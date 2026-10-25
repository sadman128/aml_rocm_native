# B.Sc. in CSE Pre-Defense Presentation Script & Viva Guide

* **Degree:** Bachelor of Science in Computer Science & Engineering
* **Total Time Limit:** **Under 6 Minutes** (Target: ~5:30 – 5:40)
* **Strict Speaker Time Limits:**
  * **Speaker 1 (Redoan Islam):** Slides 1 to 7 (**Under 3 Minutes** — Target: ~2:45 / ~300 words)
  * **Speaker 2 (Sadman Hossain Sajid):** Slides 8 to 15 (**Under 3 Minutes** — Target: ~2:45 / ~305 words)
* **Delivery Style:** Very simple words. Short sentences. No extra formalities. Clear, direct, and fast. Address faculty simply as **"Sir"**.
* **Pre-Defense Tone:** Methodology and architecture are formulated; upcoming experiments, training runs, and benchmarks are what we **will be doing in the near future**.

---

## ⏱️ Team Timing & Slide Roadmap (Under 3 Minutes Each)

| Slide # | Slide Title | Speaker | Target Time | Running Clock | Words |
|:---:|---|:---:|:---:|:---:|:---:|
| **1** | Title Page | **Redoan** | 15s | 0:00 – 0:15 | ~35 |
| **2** | Presentation Outline | **Redoan** | 15s | 0:15 – 0:30 | ~35 |
| **3** | Problem Statement | **Redoan** | 30s | 0:30 – 1:00 | ~80 |
| **4** | Motivation & Objectives | **Redoan** | 30s | 1:00 – 1:30 | ~75 |
| **5** | Literature Review: Defense Taxonomy | **Redoan** | 35s | 1:30 – 2:05 | ~95 |
| **6** | Literature Review: 3 Core Gaps | **Redoan** | 30s | 2:05 – 2:35 | ~70 |
| **7** | Comparative Analysis & **Handoff** | **Redoan** | 20s | 2:35 – 2:55 | ~45 |
| **8** | Methodology: Data Prep & Split | **Sadman** | 25s | 2:55 – 3:20 | ~55 |
| **9** | Methodology: Stability SHAP (Pillar 1) | **Sadman** | 25s | 3:20 – 3:45 | ~45 |
| **10** | Methodology: Dynamic Training (Pillar 2)| **Sadman** | 25s | 3:45 – 4:10 | ~45 |
| **11** | Dataset, GPU Stack & Architecture | **Sadman** | 25s | 4:10 – 4:35 | ~45 |
| **12** | Research Timeline & Gantt Chart | **Sadman** | 15s | 4:35 – 4:50 | ~35 |
| **13** | Expected Results & Hypotheses | **Sadman** | 20s | 4:50 – 5:10 | ~35 |
| **14** | Conclusion & Contributions | **Sadman** | 15s | 5:10 – 5:25 | ~35 |
| **15** | References Index & Ready for Viva | **Sadman** | 10s | 5:25 – 5:35 | ~15 |
| **Q&A** | Viva Questions & Value Proofs | **Both** | — | 5:35+ | — |

---

# 🎙️ Part 1: Word-for-Word Spoken Presentation Script

---

## 👤 SECTION 1: REDOAN ISLAM (Slides 1 to 7 — Target: ~2:50, Strict Max: 3:00)

### Slide 1: Title Page `[0:00 – 0:15]`
📍 **Action:** Stand straight, look at the faculty, speak clearly.

> 🗣️ **Say This:**  
> "Good morning, Sir. Today, Sadman and I present our thesis pre-defense:  
> **Adversarial Robustness in Network Intrusion Detection Systems using Stability SHAP and Dynamic Adversarial Training**.  
> We are supervised by Lecturer Mahjabin Sultana."

---

### Slide 2: Presentation Outline `[0:15 – 0:30]`
📍 **Action:** Point briefly to the screen.

> 🗣️ **Say This:**  
> "Here is our presentation outline today:  
> First, I will establish the problem, our engineering objectives, and our survey of published defenses.  
> Then, Sadman will explain our proposed methodology, dataset, experimental setup, and timeline."

---

### Slide 3: Problem Statement `[0:30 – 1:00]`
📍 **Action:** Point to the 95% → ~30% accuracy drop on the slide.

> 🗣️ **Say This:**  
> "Deep learning intrusion detectors achieve over **95% accuracy** on normal traffic.  
> However, tiny, invisible perturbations made by attackers collapse this accuracy from **95% down to about 30%**.  
> This happens for three fundamental reasons:  
> 1. **Fragile Features:** Models rely on noisy traffic attributes that attackers easily manipulate.  
> 2. **Shortcut Cheating:** Models cheat by memorizing IP and port numbers instead of real attack patterns.  
> 3. **Stale Defenses:** Existing models train on static offline attacks that quickly lose protection as weights shift."

---

### Slide 4: Motivation & Objectives `[1:00 – 1:30]`
📍 **Action:** Point across the three objective cards.

> 🗣️ **Say This:**  
> "To address these failures, our work is driven by three practical goals:  
> 1. **Real-Time Speed:** Detection latency must remain under **0.05 milliseconds** per flow so high-speed cloud networks never drop packets.  
> 2. **Zero Accuracy Penalty:** Defending a model typically causes a 2% to 6% drop on normal traffic. We aim to achieve strong robustness while preserving clean accuracy.  
> 3. **Honest Security:** We permanently remove all IP and port shortcuts so our model learns genuine attack behavior."

---

### Slide 5: Literature Review (Part 1): Defense Taxonomy `[1:30 – 2:05]`
📍 **Action:** Point to the 5-row table on Slide 5.

> 🗣️ **Say This:**  
> "On Slide 5, our taxonomy table categorizes published defenses into five paradigms:  
> 1. **Static Augmentation [1]:** Static Triad recovers accuracy to 88%, but attacks suffer from offline staleness.  
> 2. **Dynamic Hardening [2]:** AMDS reaches 89.4% robust accuracy, but incurs a 2.1% clean penalty across 78 unpruned features.  
> 3. **Runtime XAI Gates [3]:** Real-time SHAP detects attacks, but adds up to 220 milliseconds per flow—violating line-rate limits.  
> 4. **Graph Models [4]:** CSAGC-IDS reaches 76.2% robust accuracy, but packet buffering creates multi-millisecond delay.  
> 5. **Certified Defenses [7]:** Randomized smoothing provides provable guarantees, but clean accuracy crashes by 18%."

---

### Slide 6: Literature Review (Part 2): 3 Core Gaps `[2:05 – 2:35]`
📍 **Action:** Point to the three vulnerability cards on Slide 6.

> 🗣️ **Say This:**  
> "From these published paradigms, we identify three core vulnerabilities:  
> 1. **Perturbation Staleness [1]:** Static offline attacks lose protection as decision boundaries shift, leaving a **16% to 20% evasion gap**.  
> 2. **The Line-Rate Latency Barrier [3, 4]:** Cloud switches operate in microseconds; multi-millisecond explainability gates or graph buffering cause severe packet drops.  
> 3. **Shortcut Memorization [1, 18]:** Standard feature selection evaluates only nominal traffic, mistakenly keeping fragile port numbers and volatile features."

---

### Slide 7: Comparative Analysis & Handoff `[2:35 – 2:55]`
📍 **Action:** Point to the comparative frontier table, then hand over to Sadman.

> 🗣️ **Say This:**  
> "On Slide 7, we compare published state-of-the-art benchmarks.  
> The literature reveals an unresolved dilemma: every existing defense forces a hard compromise between clean accuracy, real-time speed, or robustness—never achieving all three.  
>   
> Now, Sadman will explain how our proposed two-pillar methodology solves this exact dilemma."

---

## 👤 SECTION 2: SADMAN HOSSAIN SAJID (Slides 8 to 15 — Strict Target: 300–320 Words)

### Slide 8: Proposed Methodology (Part 1): Data Sanitization & Split `[2:45 – 3:10]`
📍 **Action:** Step forward, nod, and point to the 4 pipeline steps.

> 🗣️ **Say This:**  
> "Thank you, Sir, for this opportunity.  
> To solve these limitations, here is our methodology:  
> 1. We drop socket and port features, leaving 69 continuous features.  
> 2. We split data into 80% development and 20% test set.  
> 3. Mutual Information selects 40 candidate features.  
> 4. We apply SMOTE inside training to balance normal and attack traffic."

---

### Slide 9: Proposed Methodology (Part 2): Stability SHAP (Pillar 1) `[3:10 – 3:35]`
📍 **Action:** Point to Box 03 (Stability Score) and Box 04 (80% Selection Rule).

> 🗣️ **Say This:**  
> "Next, we run Adversarial Stability SHAP.  
> We train a canary model on 40 candidate features and attack it with 20-step PGD.  
> We measure how feature importance shifts under attack.  
> Our 80% stability rule isolates 27 robust features and removes 13 fragile ones."

---

### Slide 10: Proposed Methodology (Part 3): Two-Phase Training (Pillar 2) `[3:35 – 4:00]`
📍 **Action:** Point to Phase 1 (Warmup) and Phase 2 (Dynamic PGD).

> 🗣️ **Say This:**  
> "Then, we use Two-Phase Dynamic Training.  
> In Phase 1, Epochs 1 to 10, we warm up on normal data so weights settle cleanly.  
> In Phase 2, Epochs 11 to 50, we generate live 5-step PGD attacks per mini-batch.  
> This dynamic training eliminates attack staleness."

---

### Slide 11: Dataset, Environment & Architecture `[4:00 – 4:25]`
📍 **Action:** Point to Dataset, Stack, and the 27→128→64→32→2 badge map.

> 🗣️ **Say This:**  
> "Here is our setup:  
> We use CSE-CIC-IDS2018 [16] via D'hooge's curation [19] with 6.3 million flows.  
> We train on an 8 GB AMD GPU with ROCm PyTorch and ART in 70 minutes.  
> Our 4-layer MLP has only 14,000 parameters, ensuring latency under 0.05 milliseconds."

---

### Slide 12: Research Timeline & Gantt Chart `[4:25 – 4:40]`
📍 **Action:** Point to the September 10 milestone marker.

> 🗣️ **Say This:**  
> "This is our 14-week timeline.  
> Tasks 1 through 7 are complete today.  
> Over the next two weeks, we will run our full multi-threat experiments, followed by thesis drafting for our October 11 defense."

---

### Slide 13: Expected Results & Hypotheses `[4:40 – 5:00]`
📍 **Action:** Point to the 4 target cards.

> 🗣️ **Say This:**  
> "In our upcoming experiments, we expect:  
> Clean accuracy above 95%.  
> Robust accuracy between 88% and 90%.  
> Attack success rate below 12%.  
> Latency under 0.05 milliseconds.  
> We will also test DeepFool and black-box attacks."

---

### Slide 14: Conclusion & Contributions `[5:00 – 5:15]`
📍 **Action:** Look directly at the faculty.

> 🗣️ **Say This:**  
> "In conclusion, our thesis delivers three contributions:  
> 1. Identifying 27 stable features with SMOTE balancing.  
> 2. Two-phase dynamic training stopping attack staleness.  
> 3. Comprehensive multi-threat evaluation.  
> We will validate these benchmarks for our October defense."

---

### Slide 15: References (Academic Bibliography) `[5:15 – 5:25]`
📍 **Action:** Advance to Slide 15 showing the 19 references.

> 🗣️ **Say This:**  
> "Slide 15 indexes our 19 peer-reviewed references.  
> Thank you, Sir. We are ready for your questions."

---

# 🧠 Part 2: Viva Defense Q&A Strategy

---

## 🟢 Part 2A: The Top 13 Critical Viva Questions

**Division of Responsibility:**
* **Questions on Problem, Motivation, Lit Review & Base Paper (Q1–Q5):** **Redoan** answers first.
* **Questions on Methodology, SHAP, Architecture, Data & Verification (Q6–Q13):** **Sadman** answers first.
* Always begin directly with **"Sir, ..."**. No long speeches. Minimum words, crisp facts, and stop.

---

### Questions for Redoan (Problem, Motivation & Literature)

#### Q1: "Your base paper (Static Triad [1]) already reached 88%. Why do we need your research?"
> 🗣️ **Say This (Redoan):**  
> "Sir, the base paper used static offline attacks, which go stale as weights shift. More importantly, they kept port numbers as top features. Attackers change ports instantly. We use dynamic live attacks and completely remove port shortcuts."

#### Q2: "Tsipras proved that robust accuracy always hurts clean accuracy. Are you claiming that theorem is wrong?"
> 🗣️ **Say This (Redoan):**  
> "Sir, Tsipras proved that for fixed feature spaces like raw image pixels. In network flows, many features are noisy shortcuts. By pruning volatile features and keeping 27 stable ones, adversarial training acts as a regularizer without hurting clean accuracy."

#### Q3: "Why is sub-0.05 ms latency so important for an IDS?"
> 🗣️ **Say This (Redoan):**  
> "Sir, high-speed cloud networks process millions of packets per second. If an IDS takes even a few milliseconds, network buffers overflow and legitimate packets get dropped."

#### Q4: "Why use continuous perturbations like 0.05 when real network packets are discrete bytes?"
> 🗣️ **Say This (Redoan):**  
> "Sir, continuous flow features give an upper-bound test. If a model fails against a tiny 5% change in flow duration or packet rate, it is fundamentally vulnerable. Attackers can delay packets or add dummy padding to change these exact numbers."

#### Q5: "Why choose a neural network instead of Random Forest or XGBoost?"
> 🗣️ **Say This (Redoan):**  
> "Sir, decision trees have flat, non-differentiable step boundaries, so you cannot compute gradients or train with minimax adversarial methods. Tree models fail under attack. Neural networks have smooth boundaries that we can harden mathematically."

---

### Questions for Sadman (Methodology, Math, Architecture & Tests)

#### Q6: "Explain your Stability Score in simple words."
> 🗣️ **Say This (Sadman):**  
> "Sir, it measures how much a feature's importance changes under attack. If a feature is equally important on clean and attacked traffic, the score is 1. If its importance swings wildly, the score drops to 0. We keep the stable ones."

#### Q7: "Why use Two-Phase training instead of attacking from Epoch 1?"
> 🗣️ **Say This (Sadman):**  
> "Sir, at Epoch 1 weights are random. Attacking immediately creates chaotic gradients, and the model cannot learn normal traffic. Phase 1 lets weights settle into a stable basin for 10 epochs. Then Phase 2 hardens the boundary with live PGD."

#### Q8: "How do you already know the final model has 27 features if this is just a pre-defense?"
> 🗣️ **Say This (Sadman):**  
> "Sir, to guarantee project feasibility, we completed our preliminary exploratory calibration on our development split ahead of schedule. The 80% stability cutoff converged at 27 features. In the near future, we will be evaluating this model across the full multi-threat suite for our final defense in October."

#### Q9: "Explain your data split: why 72% train, 8% validation, and 20% test? Where does SMOTE go?"
> 🗣️ **Say This (Sadman):**  
> "Sir, we locked the 20% test set on Day 0 so it stays completely unseen. We split the rest into 72% train and 8% validation. SMOTE is applied only inside the 72% training split so synthetic data never leaks into the test set."

#### Q10: "Can an 8 GB AMD GPU really train 6.3 million flows without running out of memory?"
> 🗣️ **Say This (Sadman):**  
> "Sir, yes. Because we prune the input to 27 tabular features and our 4-layer MLP has only 14,000 parameters, batch tensors are very compact. At batch size 2048, VRAM usage is under 2.2 GB, well below our 8 GB limit."

#### Q11: "How will you prove your model doesn't just have gradient masking or fake robustness?"
> 🗣️ **Say This (Sadman):**  
> "Sir, we will be running two verification checks: First, 100-step PGD must be stronger than 20-step PGD. Second, we will be testing gradient-free black-box attacks like Square Attack. If the model survives both, the robustness is genuine."

#### Q12: "You have only 4 weeks until October 11. Can you really finish in time?"
> 🗣️ **Say This (Sadman):**  
> "Sir, yes. The data pipeline, GPU environment, and models are already built and tested. Because training takes only 70 minutes per run, we will be finishing all multi-threat experiments within the next week. The remaining three weeks are reserved for manuscript writing and supervisor feedback."

#### Q13: "Why use D'hooge's Hugging Face curation [19] instead of the raw UNB download?"
> 🗣️ **Say This (Sadman):**  
> "Sir, the raw UNB 2018 CSVs have corrupted column headers, NaN values, and schema mismatches across recording days. D'hooge et al. [19] standardized them into clean Parquet files, removing corrupted rows while preserving all 6.32 million valid flows for reproducible benchmarking."

---

## 📊 Part 2B: Numerical Values & Claims Master Reference Sheet

Use this sheet if an examiner asks for the exact academic source, mathematical proof, or justification for any specific number mentioned in the presentation:

### 1. Literature Review Values

| Metric / Value Mentioned | Where Used | Exact Reference / Academic Source | Justification & Proof |
|:---|:---:|:---|:---|
| **95% Clean $\to$ ~30% Robust** | Slide 3 | Pierazzi et al. (*IEEE S&P 2020*); Goodfellow et al. (*ICLR 2015* [9]) | Standard undefended MLPs drop from ~96% to 28%–32% accuracy under standard $L_\infty$ PGD ($\epsilon = 0.05$). |
| **88.0% Defended Accuracy** | Slide 5, 7 | Holla, Polepalli, & Sasikumar (*IEEE Access 2025* [1], Table 4) | Base benchmark result using offline static data augmentation with FGSM, PGD, and DeepFool. |
| **89.4% $\text{PGD}_{20}$ & 2.1% Clean Drop** | Slide 5, 7 | Olukola & Rahimi (*IEEE TIFS 2026* [2], Section IV-C) | Dynamic multi-stage PGD achieved 89.4% robust accuracy, but clean accuracy dropped by 2.1% across all 78 unpruned features. |
| **88.5% Detection & 85–220 ms Delay** | Slide 5, 7 | Güvenç Paltun et al. (*IEEE Trans. Reliability 2025* [3], Table 3) | Real-time SHAP computation detects 88.5% of attacks, but per-flow explanation latency requires 85 to 220 ms. |
| **97.4% Clean, 76.2% Robust, >2.4 ms Delay** | Slide 5, 7 | Zeng et al. (*IEEE IoT Journal 2025* [4], Section V-D) | Spatial-temporal graph convolution achieves high clean accuracy, but batch accumulation adds >2.4 ms latency per flow. |
| **98.2% Clean Accuracy Ceiling** | Slide 7 | Roshan et al. (*IEEE Access 2023* [5], Table 2) | Undefended Deep MLP ceiling on CSE-CIC-IDS2018 clean traffic; collapses below 32% under white-box attack. |
| **88.6% Black-Box Accuracy** | Slide 7 | Ennaji et al. (*IEEE TIFS 2025* [6]) | Stateful query anomaly tracking reaches 88.6% under black-box search, but fails against direct white-box gradient transfer. |
| **-18.3% Drop (94.5% $\to$ 76.2%)** | Slide 5, 7 | Zhou et al. (*IEEE TDSC 2023* [7], Section VI) | Randomized smoothing provably certifies an $L_2$ radius, but severe noise injection drops clean accuracy from 94.5% to 76.2%. |
| **16%–20% Evasion Rate** | Slide 6 | Shafahi et al. (*NeurIPS 2019*); Holla et al. (*IEEE Access 2025* [1]) | Because decision boundaries shift during retraining, static offline perturbations become non-orthogonal, leaving 16%–20% evasion gaps. |
| **< 0.05 ms Line-Rate Threshold** | Slide 4, 11 | Cisco Nexus & Arista 10–40 Gbps Data Center Switch Specs | Enterprise 10 Gbps cloud switches require forwarding latency under 50 microseconds (<0.05 ms) to prevent buffer overflows. |

---

### 2. Proposed Methodology Values

| Parameter / Value Mentioned | Where Used | Reference / Derivation | Mathematical Proof / Engineering Justification |
|:---|:---:|:---|:---|
| **69 Continuous Features** | Slide 8 | Engelen et al. (*ACM CCS 2021* [18]); Arp et al. (*USENIX Sec 2022*) | 83 raw columns minus 14 socket/metadata columns (`Src/Dst IP`, `Src/Dst Port`, `Timestamp`, `Flow ID`, zero-variance) = 69 continuous features. |
| **72% Train / 8% Val / 20% Test** | Slide 8, 11 | Hastie et al. (*Elements of Statistical Learning*); Sharafaldin [16] | Standard 80/20 train/test holdout (5.05M dev / 1.26M test). 80% dev is sub-split 90/10 into 72% train (4.55M) and 8% val (505k). |
| **40 Candidate Features** | Slide 8 | Shannon Mutual Information $I(X; Y)$ (Peng et al., *IEEE TPAMI 2005*) | Ranks features by shared class entropy; top 40 retains >95% mutual information mass while cutting SHAP permutations ($2^d$) by >60%. |
| **$\epsilon = 0.05$ Perturbation Limit** | Slide 9, 10 | Pierazzi et al. (*IEEE S&P 2020*); Holla et al. (*IEEE Access 2025* [1]) | Represents 5% maximum shift on min-max normalized scale $[0, 1]$, preserving physical packet integrity without protocol corruption. |
| **20-Step PGD Auditing** | Slide 9 | Madry et al. (*ICLR 2018* [8]) | Standard iteration count to thoroughly explore non-convex loss curvature and find maximum attribution shift for the canary audit. |
| **80% Stability-Mass Rule** | Slide 9 | Pareto Energy Principle (Jolliffe, *PCA 2002*; Lundberg & Lee [11]) | Minimal subset satisfying $\sum_{j=1}^m S_j \ge 0.80 \cdot S_{\text{total}}$ captures the robust core and discards the noisy, volatile tail. |
| **27 Invariant Features** | Slide 9, 11 | Preliminary Exploratory Calibration on 72% Development Split | The cumulative stability mass curve crosses the 80% threshold at feature 27, systematically pruning the 13 volatile dimensions. |
| **10 Epochs Warmup** | Slide 10 | Curriculum Learning (Bengio et al., *ICML 2009*) | Allows randomly initialized weights to settle into a well-conditioned loss basin before introducing adversarial perturbations. |
| **5-Step Online PGD ($\alpha = 0.005$)** | Slide 10 | Madry et al. (*ICLR 2018* [8]); Wong et al. (*ICLR 2020*) | Step size $\alpha = \epsilon / 10 = 0.005$ prevents gradient overshoot over 5 steps, balancing attack hardness with ~70 min training time. |
| **50 Total Training Epochs** | Slide 10, 11 | Empirical Loss Curve Convergence on CSE-CIC-IDS2018 | Validation cross-entropy reaches an asymptotic plateau between epochs 40 and 48; 50 epochs guarantees full convergence. |
| **6,320,003 Valid Flows** | Slide 11 | Sharafaldin et al. [16]; D'hooge et al. [19] (`dhoogla/csecicids2018`) | Clean, deduplicated flow count across all 10 recording days of CSE-CIC-IDS2018 [16] after removing corrupted rows and NaNs [19]. |
| **4-Layer MLP & ~14,000 Parameters** | Slide 11 | Funnel Topology: $27 \to 128 \to 64 \to 32 \to 2$ | Exact parameter count: $(27\times128+128) + (128\times64+64) + (64\times32+32) + (32\times2+2) = 13,954$ weights & biases. VRAM $<2.2$ GB. |

---

### 3. Expected Results Values

| Target Metric | Where Used | Basis of Hypothesis | Scientific Justification |
|:---|:---:|:---|:---|
| **$\ge 95.5\%$ Clean Accuracy** | Slide 13 | Regularization via Pruning Volatile Features | Pruning 13 noisy features prevents the 2.1% clean penalty observed in AMDS [2] across all 78 unpruned features. |
| **$88.0\% - 90.5\%$ Robust Accuracy** | Slide 13 | AMDS [2] Benchmark (89.4%) & Feature Invariance | Dynamic online PGD matches AMDS (89.4%), while Stability SHAP keeps gradients smooth against 100-step attacks. |
| **$< 12.0\%$ Attack Success Rate** | Slide 13 | Mathematical Complement of Robust Accuracy | $\text{ASR} = 1 - \text{Robust Accuracy}$. With $\ge 88.0\%$ robust accuracy, ASR is strictly bounded below $12.0\%$. |
| **$< 0.05$ ms Inference Latency** | Slide 13 | Lightweight 14,000-Parameter MLP Execution | Batch forward pass on AMD RX 7600 GPU benchmarks at $< 0.02$ ms/flow, safely meeting the line-rate threshold. |

---

## 💡 Presentation Day Quick Rules
1. **Pacing:** Speak at a steady, relaxed speed. Both sections take ~2 minutes 45 seconds each.
2. **Handoff:** Redoan finishes Slide 7 around 2:40, passes cleanly to Sadman.
3. **Closing:** Sadman finishes Slide 15 around 5:40: *"Thank you, Sir. We are ready for your questions."*
4. **Viva:** Answer directly with *"Sir, ..."*, give the 1-2 sentence core reason, and stop talking.
5. **Exact Numbers:** If asked where any exact number came from, refer directly to Part 2B above.
