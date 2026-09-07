# B.Sc. in CSE Pre-Defense Presentation Script & Viva Guide

* **Degree:** Bachelor of Science (B.Sc.) in Computer Science & Engineering
* **Total Time Limit:** **6 to 7 Minutes** (~360 – 420 seconds)
* **Speaker Split:**
  * **Speaker 1 (Redoan Islam):** Slides 1 to 7 (~3 minutes / ~350 words)
  * **Speaker 2 (Sadman Hossain Sajid):** Slides 8 to 14 (~3 to 3.5 minutes / ~380 words)
* **Delivery Style:** Simple, short sentences. Natural conversational pace (~115 words/minute). Memorizable without getting stuck on complex academic tongue-twisters.

---

## ⏱️ Team Timing & Slide Roadmap

| Slide # | Slide Title | Speaker | Target Time | Running Clock | Word Count |
|:---:|---|:---:|:---:|:---:|:---:|
| **1** | Title Page | **Redoan** | 18s | 0:00 – 0:18 | ~35 words |
| **2** | Presentation Outline | **Redoan** | 12s | 0:18 – 0:30 | ~25 words |
| **3** | Problem Statement | **Redoan** | 35s | 0:30 – 1:05 | ~70 words |
| **4** | Motivation & Objectives | **Redoan** | 25s | 1:05 – 1:30 | ~50 words |
| **5** | Literature Review: Macro Findings | **Redoan** | 30s | 1:30 – 2:00 | ~60 words |
| **6** | Literature Review: Landmark Defenses | **Redoan** | 35s | 2:00 – 2:35 | ~70 words |
| **7** | Comparative Analysis & **Handoff** | **Redoan** | 30s | 2:35 – 3:05 | ~75 words |
| **8** | Methodology 1: Data Sanitization | **Sadman** | 35s | 3:05 – 3:40 | ~70 words |
| **9** | Methodology 2: Stability SHAP | **Sadman** | 45s | 3:40 – 4:25 | ~90 words |
| **10** | Methodology 3: Two-Phase Dynamic PGD | **Sadman** | 35s | 4:25 – 5:00 | ~70 words |
| **11** | Dataset, Environment & Architecture | **Sadman** | 30s | 5:00 – 5:30 | ~60 words |
| **12** | Research Timeline & Gantt Chart | **Sadman** | 20s | 5:30 – 5:50 | ~40 words |
| **13** | Expected Results & Targets | **Sadman** | 25s | 5:50 – 6:15 | ~50 words |
| **14** | Conclusion & Closing | **Sadman** | 20s | 6:15 – 6:35 | ~40 words |
| **BUFFER**| Transition to Viva Committee Questions | **Both** | 25s | 6:35 – 7:00 | — |

---

# 🎙️ Part 1: Word-for-Word Spoken Script

---

## 👤 SECTION 1: REDOAN ISLAM (Slides 1 to 7)

### Slide 1: Title Page `[0:00 – 0:18]`
📍 **Action:** Smile, make eye contact with the board, speak calmly.

> 🗣️ **Say This (Word-for-Word):**  
> "Good morning, respected committee members and supervisor.  
> Today, my co-author Sadman Hossain Sajid and I present our undergraduate B.Sc. thesis pre-defense:  
> **Adversarial Robustness in Network Intrusion Detection Systems via Attribution-Guided Feature Selection and Dynamic Multi-Stage Adversarial Training**.  
> We are supervised by Lecturer Mahjabin Sultana."

---

### Slide 2: Presentation Outline `[0:18 – 0:30]`
📍 **Action:** Point at the screen and state the exact headings directly.

> 🗣️ **Say This (Word-for-Word):**  
> "Here is our presentation outline:  
> I will present the **Problem Statement**, **Motivation**, **Literature Review**, and **Research Gap**.  
> Then, Sadman will present our **Proposed Methodology**, **Dataset & Environment**, **Research Timeline**, and **Expected Results**."

---

### Slide 3: Problem Statement `[0:30 – 1:05]`
📍 **Action:** Point to the big '95% → ~30%' graphic on the left.

> 🗣️ **Say This (Word-for-Word — Natural & Conversational):**  
> "Deep learning intrusion detection systems look great on paper, achieving over **95% accuracy** on normal traffic.  
> But in reality, they have a fatal flaw: when an attacker makes tiny, invisible tweaks to network packets, accuracy collapses from **95% down to about 30%**.  
> Why does this happen? Three main reasons:  
> **1. Fragile Features:** The AI relies on weak traffic clues that attackers can easily disguise.  
> **2. Shortcut Cheating:** Models cheat by memorizing port numbers and IP addresses instead of learning real attack patterns.  
> **3. Stale Defenses:** Existing defenses train only once on old attacks, making them helpless against adaptive, modern attackers."

📚 **Key References & Citations (if asked by evaluators):**
* **Evasion Collapse:** *Pierazzi et al., "Intriguing Properties of Adversarial ML Attacks in Problem Space", IEEE S&P 2020*
* **Fragile Features:** *Goodfellow et al., "Explaining and Harnessing Adversarial Examples", ICLR 2015*
* **Shortcut Learning (Ports & IPs):** *Arp et al., "Dos and Don'ts of Machine Learning in Computer Security", USENIX Security 2022; Engelen et al., "Troubleshooting an Intrusion Detection Dataset", ACM CCS 2021*
* **Static Defense Staleness:** *Shafahi et al., "Adversarial Training for Free!", NeurIPS 2019*

---

### Slide 4: Motivation & Objectives `[1:05 – 1:30]`
📍 **Action:** Point across the three objective cards on the screen.

> 🗣️ **Say This (Word-for-Word — Natural & Conversational):**  
> "To solve these three problems, our research is driven by three practical goals:  
> **1. Real-Time Speed:** In high-speed cloud networks, detection must take less than **0.05 milliseconds** per flow so we never delay or drop valid packets.  
> **2. No Accuracy Penalty:** Usually, defending a model against attacks causes a **2% to 6% drop** on normal traffic. Our goal is to defend against attacks *without* sacrificing normal performance by filtering out noisy features.  
> **3. Honest Security:** Real attackers switch ports and spoof IPs constantly. We permanently remove all port and IP shortcuts so our model learns genuine, reliable attack behavior."

📚 **Key References & Citations (if asked by evaluators):**
* **Accuracy vs. Robustness Trade-off:** *Tsipras et al., "Robustness May Be at Odds with Accuracy", ICLR 2019*
* **Benchmark Hygiene & Shortcut Elimination:** *Arp et al., "Dos and Don'ts of Machine Learning in Computer Security", USENIX Security 2022; Engelen et al., ACM CCS 2021*

---

### Slide 5: Literature Review (Part 1): Current Landscape `[1:30 – 2:00]`
📍 **Action:** Point to the '40 Publications' badge.  
💡 *Tip for Redoan: Paper titles are shown right before each citation if asked directly.*

> 🗣️ **Say This (Word-for-Word):**  
> "From surveying **40 recent peer-reviewed publications** (2021–2026), we found 5 key facts:  
> **1. Clean Accuracy Drop:** Defenses cause a **2% to 6% drop** on clean data [*"Robustness May Be at Odds with Accuracy"* — Tsipras et al., ICLR 2019; *"Theoretically Principled Trade-off Between Robustness and Accuracy" (TRADES)* — Zhang et al., ICML 2019].  
> **2. Tree Ensembles Fail:** Random Forest and XGBoost collapse under gradient attacks, suffering **over 80% evasion** [*"Real Attackers Don't Compute Gradients"* — Apruzzese et al., IEEE TIFS 2023].  
> **3. Static Staleness:** Offline attack samples lose effectiveness over time (**16% to 20% evasion**) [*"Adversarial Training for Free!"* — Shafahi et al., NeurIPS 2019; *"Adversarial Threats to Cloud IDS"* — Holla et al., IEEE Access 2025].  
> **4. Runtime XAI is Too Slow:** Runtime SHAP adds **85 to 220 milliseconds** of delay, which is too slow for real networks [*"Robust Intrusion Detection System with Explainable AI"* — Güvenç Paltun et al., Computers & Security 2025].  
> **5. Clean-Only Bias:** Selecting features only on normal traffic accidentally keeps fragile port shortcuts [*"Dos and Don'ts of Machine Learning in Computer Security"* — Arp et al., USENIX Security 2022; *"Troubleshooting an Intrusion Detection Dataset"* — Engelen et al., ACM CCS 2021]."

---

### Slide 6: Literature Review (Part 2): Landmark Defenses `[2:00 – 2:35]`
📍 **Action:** Point across the 4 defense cards.

> 🗣️ **Say This (Word-for-Word):**  
> "We studied four landmark peer defenses:  
> **1. Static Adversarial — Holla et al. [*"Adversarial Threats to Cloud IDS"*, IEEE Access 2025] (Base Paper):** Used static adversarial training. Defended accuracy reached 88%, but attacks become stale and it keeps port shortcuts [*"Troubleshooting an Intrusion Detection Dataset"* — Engelen et al., 2021].  
> **2. Dynamic Hardening — Olukola & Rahimi [*"AMDS: Attack-Aware Multi-Stage Defense System"*, IEEE TIFS 2026]:** Used dynamic training, but kept all 78 dimensions with a heavy 140% computational overhead.  
> **3. Explainable AI Gate — Güvenç Paltun et al. [*"Robust Intrusion Detection System with Explainable AI"*, Elsevier 2025]:** Used runtime SHAP, but its 85 ms delay is too slow for real-time networks [*"Fooling LIME and SHAP"* — Slack et al., AIES 2020].  
> **4. Graph Attention IDS — Zeng et al. [*"CSAGC-IDS: Dual-Module Network Intrusion Detection"*, IEEE IoTJ 2025]:** Used graph attention, but packet buffering adds 2.4 ms delay."

---

### Slide 7: Comparative Analysis `[2:35 – 3:05]`
📍 **Action:** Point across the 5 benchmark rows on the table, then turn toward Sadman for the handoff.

> 🗣️ **Say This (Word-for-Word — Natural & Conversational):**  
> "When we analyze all 40 papers in the literature, a clear pattern emerges: every best result comes with a serious limitation:  
> **1. Best Clean Accuracy:** Reaches **98.2%** (Roshan et al.), but has zero defense—collapsing to **under 32%** when attacked.  
> **2. Best White-Box Robustness:** Reaches **89.4%** under PGD (Olukola & Rahimi), but causes a **2.1% clean accuracy penalty** across 78 dimensions.  
> **3. Best Static Defense:** Our base paper (Holla et al.) achieves **88%**, but relies on static offline attacks and keeps port shortcuts.  
> **4. Best Black-Box Robustness:** Reaches **88.6%** (Ennaji et al.), but requires heavy stateful query tracking.  
> **5. Best Certified Defense:** Zhou et al. provably bounds attacks, but clean accuracy crashes by **18% down to 76%**.  
>   
> Across the entire literature, no defense achieves high robustness without sacrificing either clean accuracy or real-time speed.  
>   
> **Now, Sadman will present how our Proposed Methodology solves this exact dilemma.**"

📚 **Key References & Citations (if asked by evaluators):**
* **Clean Ceiling:** *Roshan et al., "Untargeted White-box Adversarial Attack with Heuristic Defence Methods in Real-time Deep Learning based Network Intrusion Detection System", J. Ambient Intell. Humaniz. Comput., Springer 2023*
* **White-Box PGD Ceiling:** *Olukola & Rahimi, "AMDS: Attack-Aware Multi-Stage Defense System for Network Intrusion Detection", IEEE TIFS 2026*
* **Static Defense (Base Paper):** *Holla et al., "Adversarial Threats to Cloud IDS: Robust Defense With Adversarial Training and Feature Selection", IEEE Access 2025*
* **Black-Box Defense:** *Ennaji et al., "Behavior-Aware and Generalizable Defense Against Black-Box Adversarial Attacks", IEEE TIFS 2025*
* **Certified Defense:** *Zhou et al., "Certified Robustness for Network Intrusion Detection Systems via Randomized Smoothing", IEEE TDSC 2023*

---

## 👤 SECTION 2: SADMAN HOSSAIN SAJID (Slides 8 to 14)

### Slide 8: Proposed Methodology (Part 1): Data Sanitization `[3:05 – 3:40]`
📍 **Action:** Step forward, nod to Redoan, and walk through the 4 numbered steps.

> 🗣️ **Say This (Word-for-Word):**  
> "Thank you, Redoan.  
> Respected committee, our Proposed Methodology begins with data sanitization and partitioning:  
> **Step 1 (Sanitization):** We permanently remove all IPs, ports, and timestamps, leaving **69 continuous numerical features** [*"Dos and Don'ts"* — Arp et al., 2022; *"Troubleshooting CICIDS"* — Engelen et al., 2021].  
> **Step 2 (Partitioning):** We lock our 20% test set on Day 0. The rest is strictly split into **72% core training and 8% validation** [*"Toward Generating a New Dataset for Intrusion Detection"* — Sharafaldin et al., ICISSP 2018].  
> **Step 3 (Coarse Screening):** Mutual Information rapidly filters 69 features down to the **top 40 candidates**, cutting downstream computation by over 60%.  
> **Step 4 (SMOTE Balancing):** Continuous-only SMOTE is applied **strictly inside the 72% training partition** to prevent any data leakage [*"SMOTE"* — Chawla et al., JAIR 2002; Arp et al., 2022]."

---

### Slide 9: Proposed Methodology (Part 2): Stability SHAP `[3:40 – 4:25]`
📍 **Action:** Point directly to the two equation images in Box 03 and Box 04.  
💡 *Tip for Sadman: Paper titles are shown right before each citation if asked directly.*

> 🗣️ **Say This (Word-for-Word):**  
> "Pillar 1 of our methodology is **Adversarial Stability SHAP**:  
> Selecting features only on clean data is dangerous.  
> We train a canary baseline model and attack it with 20-step PGD [*"Towards Deep Learning Models Resistant to Adversarial Attacks"* — Madry et al., ICLR 2018].  
> We calculate Shapley attributions on both clean and adversarial flows [*"A Unified Approach to Interpreting Model Predictions"* (SHAP) — Lundberg & Lee, NeurIPS 2017].  
> Using our **Stability Score formula (Box 03)**, we measure how resistant each feature is to perturbation.  
> Then, using our **80% cumulative stability-mass rule (Box 04)**, our **preliminary calibration systematically isolates the 27 most invariant features**, permanently pruning 13 volatile dimensions."

---

### Slide 10: Proposed Methodology (Part 3): Two-Phase Dynamic Training `[4:25 – 5:00]`
📍 **Action:** Point to Phase 1 (Warmup) and Phase 2 (Dynamic PGD).

> 🗣️ **Say This (Word-for-Word):**  
> "Pillar 2 is our **Two-Phase Dynamic Training Curriculum**:  
> Attacking randomly initialized weights at Epoch 1 causes chaotic loss gradients.  
> **Phase 1 (Epochs 1 to 10):** We warm up exclusively on clean data so weights settle into a stable geometric basin [*"Curriculum Learning"* — Bengio et al., ICML 2009].  
> **Phase 2 (Epochs 11 to 50):** For every mini-batch, we generate fresh 5-step online PGD attacks using current weights [*"Towards Deep Learning Models Resistant to Adversarial Attacks"* — Madry et al., ICLR 2018].  
> We optimize a balanced **50-50 joint loss** on clean and adversarial samples, continuously tracking the moving boundary."

---

### Slide 11: Dataset, Environment & Architecture `[5:00 – 5:30]`
📍 **Action:** Point to the 3 panels: Dataset, Stack, and the 27→128→64→32→2 badge map.

> 🗣️ **Say This (Word-for-Word):**  
> "Here is our Dataset & Environment setup:  
> **Dataset:** 6.32 million valid flows from CSE-CIC-IDS2018 [*"Toward Generating a New Dataset for Intrusion Detection"* — Sharafaldin et al., 2018], capturing 14 distinct attack types across 7 threat profiles in a binary classification setup. We use the standardized `dhoogla/csecicids2018` benchmark curation [*"CSE-CIC-IDS2018 Parquet Curation"* — D'hooge et al., Hugging Face 2023] instead of the raw 250 GB dump because it consolidates all 10 recording days, removes corrupt rows and schema discrepancies, and guarantees full scientific reproducibility.  
> **Environment:** An AMD Radeon RX 7600 GPU (8 GB VRAM) running native ROCm PyTorch on Windows with ART [*"Adversarial Robustness Toolbox"* — Nicolae et al., IBM ART 2018]. Training completes in **70 minutes**.  
> **Target Architecture:** A 4-layer MLP: **27 to 128, 64, 32, and 2 outputs** with Batch Normalization and Dropout. It has only 14,000 parameters, ensuring line-rate throughput."

---

### Slide 12: Research Timeline & Gantt Chart `[5:30 – 5:50]`
📍 **Action:** Point to the dashed milestone line at September 10.

> 🗣️ **Say This (Word-for-Word):**  
> "This is our 14-week Research Timeline:  
> Tasks 1 through 7 are **complete**, successfully reaching today's September 10 Pre-Defense milestone.  
> Over the next two weeks, we complete our multi-threat evaluation, followed by thesis drafting for our **final defense on October 11**."

---

### Slide 13: Expected Results & Hypotheses `[5:50 – 6:15]`
📍 **Action:** Point to the 4 metric cards.

> 🗣️ **Say This (Word-for-Word):**  
> "Our Expected Results targets are:  
> **Clean accuracy:** at least 95.5%.  
> **Robust accuracy:** 88% to 90.5% against 100-step PGD attacks [*"Towards Deep Learning Models Resistant to Adversarial Attacks"* — Madry et al., 2018].  
> **Attack success rate:** under 12%.  
> **Inference latency:** under 0.05 milliseconds per flow.  
> We also evaluate black-box query attacks [*"Square Attack: A Query-Efficient Black-Box Attack"* — Andriushchenko et al., ECCV 2020] and Auto-PGD [*"Reliable Evaluation of Adversarial Robustness"* (AutoAttack) — Croce & Hein, ICML 2020] to verify there is no gradient masking [*"Obfuscated Gradients Give a False Sense of Security"* — Athalye et al., ICML 2018]."

---

### Slide 14: Conclusion & Closing `[6:15 – 6:35]`
📍 **Action:** Look at both the supervisor and the committee members.

> 🗣️ **Say This (Word-for-Word):**  
> "In Conclusion, our undergraduate thesis delivers three contributions:  
> **1. Theoretical:** Stability SHAP isolating 27 perturbation-stable features.  
> **2. Architectural:** Two-phase dynamic training that eliminates attack staleness.  
> **3. Methodological:** Strict zero-leakage 72/8/20 split and socket shortcut removal.  
>   
> Thank you. We are now ready for your questions."

---

# 🧠 Part 2: Viva Defense Q&A Strategy (Who Answers What)

To avoid talking over each other or looking unprepared, divide the questions based on who presented the section:
* **Questions on Problem, Motivation, Lit Review & Base Paper (Q1–Q7):** **Redoan** answers first.
* **Questions on Methodology, SHAP, Training, Math, Architecture & Tests (Q8–Q20):** **Sadman** answers first.
* If either of you finishes early, the other can add one quick sentence: *"To add to that, Professor..."*

---

### 🟢 Questions for Redoan (Problem, Motivation & Literature)

#### Q1: "Why use continuous perturbations with a 0.05 limit when real network packets are discrete byte streams?"

> 🗣️ **Say This (Redoan):**  
> "Continuous tabular features act as an upper-bound test. If an intrusion detector fails against small numerical perturbations in flow duration or packet size, it is fundamentally vulnerable. In the real world, attackers can delay packets or add dummy padding to manipulate these exact values. We study the tabular representation first; physical packet reconstruction is future work."

* **Keywords:** *Upper-bound threat model, Pierazzi et al. (IEEE S&P 2020), continuous flow features.*

#### Q2: "Tsipras et al. proved that robust accuracy always hurts clean accuracy. Are you claiming that theorem is wrong?"

> 🗣️ **Say This (Redoan):**  
> "Not at all, Professor. Tsipras' proof assumes the feature space is fixed and cannot be changed, like raw image pixels. But in network flows, many features are noisy, volatile, or transient shortcuts. By removing those noisy features and keeping only 27 stable dimensions, adversarial training acts as a regularizer without hurting clean accuracy."

* **Keywords:** *Tsipras et al. (ICLR 2019), fixed feature space assumption, subspace regularization.*

#### Q3: "Why is sub-0.05 ms latency so important for an IDS?"

> 🗣️ **Say This (Redoan):**  
> "High-speed enterprise networks process millions of flows every minute. If an IDS takes 50 or 100 milliseconds per flow, network buffers will fill up and drop legitimate packets. A practical intrusion detector must provide fast, feed-forward inference."

* **Keywords:** *Line-rate throughput, buffer overflow, feed-forward latency.*

#### Q4: "Your base paper (Holla et al., 2025) reported 88% defended accuracy. Why do we need your research?"

> 🗣️ **Say This (Redoan):**  
> "Holla et al. used static offline training—they created attack samples once before retraining. As network weights update, the decision boundary moves, and those static samples lose effectiveness. More importantly, Section V-B of their paper shows they kept Source and Destination Ports as top features. Attackers change ports trivially. We use live dynamic attacks and completely remove port shortcuts."

* **Keywords:** *Static attack staleness, Section V-B port retention, Engelen et al. (ACM CCS).*

#### Q5: "Why did you use an MLP instead of Random Forest or XGBoost, which are popular for tabular data?"

> 🗣️ **Say This (Redoan):**  
> "Tree ensembles use rigid, step-like splits with zero gradient. Because they are not differentiable, you cannot directly apply gradient-based adversarial training. When attacked, tree models degrade severely. Neural networks have smooth, differentiable boundaries that we can harden mathematically."

* **Keywords:** *Non-differentiable step boundaries, minimax optimization, differentiable margins.*

#### Q6: "Why not use runtime Explainable AI like Güvenç Paltun et al.?"

> 🗣️ **Say This (Redoan):**  
> "Computing Shapley values at runtime takes 85 to 220 milliseconds per flow. That is thousands of times too slow for live networks. We use SHAP offline during feature selection, keeping runtime inference under 0.02 milliseconds."

* **Keywords:** *Combinatorial Shapley complexity, offline auditing vs runtime latency.*

#### Q7: "Why did you remove IP addresses and Port numbers?"

> 🗣️ **Say This (Redoan):**  
> "In a specific dataset, attacks might come from Port 8080 or one specific IP. But in real life, attackers change ports and spoof IPs instantly. If a model relies on ports, it learns a transient shortcut, not real traffic behavior. Removing socket features forces the model to learn true behavioral dynamics like flow duration and packet length distributions."

* **Keywords:** *Shortcut learning, Arp et al. (Dos and Don'ts of ML in Security), Engelen et al.*

---

### 🔵 Questions for Sadman (Methodology, Math, Architecture & Tests)

#### Q8: "Explain your data split: why 72% train, 8% validation, and 20% test?"

> 🗣️ **Say This (Sadman):**  
> "We started with the standard 80-20 train-test split on CSE-CIC-IDS2018. We locked the 20% test set—1.26 million flows—on Day 0 so no tuning ever touches it. Inside the 80% development set, we used a standard 9-to-1 split: 90% for core training (72% overall, 4.55M flows) and 10% for validation (8% overall, 505k flows). All scalers are fitted strictly on the 72% training partition."

* **Keywords:** *Strict zero-leakage, frozen holdout test set, pre-scaling isolation.*

#### Q8B: "Why did you use the `dhoogla/csecicids2018` release instead of downloading the raw 250 GB dataset directly from UNB?"

> 🗣️ **Say This (Sadman):**  
> "The official UNB distribution is an uncurated ~250 GB archive of raw PCAP captures and uncleaned CSVs with severe formatting issues: inconsistent column headers across the 10 recording days, corrupted rows, and thousands of NaN and infinity values. Laurens D'hooge's published benchmark curation (`dhoogla/csecicids2018` on Hugging Face) standardizes the schema across all 10 days, cleans corrupted rows, and converts them into optimized Parquet flows while preserving all 6.32 million valid network records. Using this peer-accepted benchmark guarantees 100% scientific reproducibility and eliminates hundreds of gigabytes of raw PCAP redundancy."

* **Keywords:** *D'hooge et al. benchmark curation, schema standardization, Parquet compression, 100% reproducibility.*

#### Q9: "Why apply SMOTE only inside the 72% training partition?"

> 🗣️ **Say This (Sadman):**  
> "If you apply SMOTE before splitting, synthetic samples created from test flows will leak into the training set, causing artificial high accuracy. Applying SMOTE strictly inside the training set guarantees that our validation and test sets remain completely pure real-world traffic."

* **Keywords:** *Data leakage prevention, continuous-only interpolation, class balance.*

#### Q10: "Why use Mutual Information first before SHAP?"

> 🗣️ **Say This (Sadman):**  
> "Computing Shapley values has exponential complexity. Running SHAP directly on 69 features across millions of flows would take days. Mutual Information is a fast statistical filter that eliminates 29 uninformative features in seconds. This reduces downstream SHAP computation by over 60% while preserving physical feature semantics."

* **Keywords:** *Shannon Mutual Information, coarse-to-fine filtering, computational tractability.*

#### Q11: "Explain your Stability Score concept in simple words."

> 🗣️ **Say This (Sadman):**  
> "This score measures how much a feature's importance shifts under attack. If a feature has the exact same importance on both clean and attacked flows, the score is 1; if its importance swings wildly, the score drops toward 0."

* **Keywords:** *Attribution shift, normalized stability index, perturbation invariance.*

#### Q12: "Why use the 80% cumulative stability-mass rule instead of a flat cutoff like 0.5?"

> 🗣️ **Say This (Sadman):**  
> "A flat cutoff like 0.5 is an arbitrary guess that doesn't adapt to different datasets. Our 80% rule acts like a Pareto principle: we rank features by stability and select the minimal subset that contains 80% of the total stability energy. On our dataset, this systematically captures the 27 most stable features and discards the 13 volatile ones."

* **Keywords:** *Pareto-optimal thresholding, adaptive stability mass, elbow-point selection.*

#### Q12B: "How do you already know it is 27 features if this is just a pre-defense?"

> 🗣️ **Say This (Sadman):**  
> "To guarantee project feasibility, we completed our preliminary data pipeline and canary model audit ahead of schedule—as shown in Tasks 1 through 7 of our Gantt chart. When we ran the 80% stability selection on our 72% development set, it empirically converged on exactly 27 features. What remains for our October final defense is the extensive multi-threat evaluation across 9 attack models."

* **Keywords:** *Preliminary exploratory calibration, Task 1–7 milestone completion, empirical convergence.*

#### Q13: "Why use Two-Phase training instead of training with PGD from Epoch 1?"

> 🗣️ **Say This (Sadman):**  
> "At Epoch 1, neural network weights are randomly initialized. If you inject strong adversarial attacks immediately, loss gradients become chaotic and the model cannot learn basic benign traffic patterns. In Phase 1, we warm up on clean data for 10 epochs so weights settle into a stable basin. Then in Phase 2, we introduce live PGD attacks to harden decision boundaries."

* **Keywords:** *Curriculum learning, non-convex loss surface, representation warmup.*

#### Q14: "Why use 5-step PGD during training instead of 20-step or 100-step?"

> 🗣️ **Say This (Sadman):**  
> "During training, PGD runs inside every single mini-batch across 40 epochs. 5-step PGD gives an optimal balance between attack strength and training speed, completing in 70 minutes. We reserve 20-step PGD for offline stability auditing, and 100-step PGD for final evaluation. This guarantees that evaluation is much stronger than training."

* **Keywords:** *Training budget optimization, multi-scale PGD auditing, evaluation asymmetry.*

#### Q15: "Why choose a step size of 0.005 when the perturbation limit is 0.05?"

> 🗣️ **Say This (Sadman):**  
> "Taking large steps can overshoot the loss peak and cause training instability. Setting the step size to 0.005—which is one-tenth of the perturbation limit—ensures smooth, controlled gradient ascent over the 5 steps."

* **Keywords:** *Gradient ascent stability, overshoot prevention, local perturbation exploration.*

#### Q16: "Can an 8 GB AMD RX 7600 really train 6.32 million flows without running out of VRAM?"

> 🗣️ **Say This (Sadman):**  
> "Yes, easily. Because our input is reduced to 27 tabular features and our 4-layer MLP has only 14,000 parameters, memory usage is very small. With a batch size of 2048 in mixed precision, the entire model, tensors, and gradients take less than 2.2 GB of VRAM. That is well within the 8 GB capacity."

* **Keywords:** *2.2 GB active VRAM footprint, vectorized batch tensors, native ROCm acceleration.*

#### Q17: "Why did you choose a 4-layer architecture with 128, 64, 32, and 2 neurons?"

> 🗣️ **Say This (Sadman):**  
> "It follows a classic funnel topology that progressively compresses 27 input features into higher-level representations. Batch Normalization stabilizes training across features with different scales, and 30% Dropout prevents overfitting on dominant flow classes."

* **Keywords:** *Funnel dimensional reduction, internal covariate shift, regularization via Dropout(0.30).*

#### Q18: "How will you prove your model doesn't just suffer from gradient masking or obfuscated gradients?"

> 🗣️ **Say This (Sadman):**  
> "We follow the three verification checks from Athalye's ICML 2018 paper:  
> First, 100-step PGD must achieve a higher attack success rate than 20-step PGD, confirming that iterative search finds worse perturbations.  
> Second, we evaluate gradient-free attacks like Square Attack and surrogate transferability.  
> If the model resists both gradient-based and gradient-free attacks, robustness is genuine, not masked."

* **Keywords:** *Athalye et al. (ICML 2018), gradient masking diagnostics, black-box transferability.*

#### Q19: "You have 4 weeks until October 11. Is this realistic for an undergraduate thesis?"

> 🗣️ **Say This (Sadman):**  
> "Yes, completely realistic. The pipeline, data preprocessing, and GPU environment are already finished and tested. Because our 50-epoch training takes only 70 minutes, all multi-threat experiments will finish within one week. The remaining three weeks are reserved exclusively for manuscript writing and supervisor feedback."

* **Keywords:** *70-minute training turnaround, pre-validated pipeline, milestone schedule adherence.*

#### Q20: "What is your main ablation study to prove both pillars are necessary?"

> 🗣️ **Say This (Sadman):**  
> "We run a 2-by-2 factorial ablation:  
> 1. Baseline: 69 features with standard training.  
> 2. Stability only: 27 stable features with static training.  
> 3. Dynamic only: 69 features with two-phase dynamic training.  
> 4. Full proposed model: 27 stable features with two-phase dynamic training.  
> This cleanly isolates how much robustness comes from feature stability versus dynamic optimization."

* **Keywords:** *2x2 factorial ablation, orthogonal performance attribution.*

---

#### ⚡ Rapid-Fire Viva: Core Fundamentals (1–2 Line Oral Answers)

#### 🛡️ Group A: Network Security & Attack Types (CSE-CIC-IDS2018)

#### Q21: "What is a DoS (Denial of Service) attack?"

> 🗣️ **Say This:**  
> "A DoS attack floods a server with bogus traffic or exhausts its CPU and memory from a single source, making the service unavailable to legitimate users."

#### Q22: "What is a DDoS (Distributed Denial of Service) attack, and how is it different from DoS?"

> 🗣️ **Say This:**  
> "A DDoS attack achieves the same goal as a DoS, but traffic comes simultaneously from thousands of distributed botnet machines, so you cannot stop it by simply blocking a single IP address."

#### Q23: "What are Slowloris and SlowHTTPTest, and how do they differ from volumetric floods?"

> 🗣️ **Say This:**  
> "Volumetric floods clog network bandwidth with huge traffic volumes, whereas Slowloris stealthily opens connections and sends headers very slowly, starving server connection slots using almost zero bandwidth."

#### Q24: "What are LOIC and HOIC?"

> 🗣️ **Say This:**  
> "They are open-source flooding tools used in DoS attacks: LOIC blasts targets with raw UDP or HTTP packets, while HOIC sends randomized HTTP requests across multiple URLs simultaneously."

#### Q25: "What is a Brute Force attack?"

> 🗣️ **Say This:**  
> "An automated trial-and-error attack that repeatedly guesses thousands of username and password combinations until finding the right one, such as attacks on FTP or SSH ports."

#### Q26: "What is a Web Attack? Explain SQL Injection vs. Cross-Site Scripting (XSS)."

> 🗣️ **Say This:**  
> "Web attacks exploit website vulnerabilities. SQL Injection injects database commands to steal backend data, while XSS injects malicious JavaScript into web pages to steal user session cookies."

#### Q27: "What is a Botnet and an Infiltration attack?"

> 🗣️ **Say This:**  
> "A botnet is a network of compromised machines controlled remotely by an attacker. Infiltration is a stealthy attack where an intruder breaches an internal PC—like via an infected download—and pivots deeper into the network."

#### Q28: "What is Heartbleed?"

> 🗣️ **Say This:**  
> "A famous OpenSSL vulnerability where an attacker sends a malformed TLS heartbeat request, tricking the server into leaking 64 kilobytes of secret memory containing private keys and passwords."

#### Q29: "What is a Network Flow vs. a Raw Packet? Why use flows for an IDS?"

> 🗣️ **Say This:**  
> "A packet is a single transmission chunk on the wire, while a flow is a statistical summary of all packets sharing the same IP and port. We use flows because inspecting raw packet payloads is too slow at line rate and blocked by modern HTTPS encryption."

#### Q30: "What is the difference between an IDS, an IPS, and a Firewall?"

> 🗣️ **Say This:**  
> "A firewall blocks traffic based on static IP and port rules; an IDS passively monitors traffic to raise alerts; and an IPS sits directly inline to actively drop malicious connections in real time."

---

#### 🧠 Group B: Explainable AI (XAI) & SHAP

#### Q31: "What is SHAP (SHapley Additive exPlanations)?"

> 🗣️ **Say This:**  
> "SHAP is an Explainable AI method based on cooperative game theory that calculates the fair individual contribution of each feature to a model's final prediction."

#### Q32: "What is a Shapley value intuitively?"

> 🗣️ **Say This:**  
> "Think of a sports team winning a match: the Shapley value measures how much each individual player contributed to the victory by testing team performance across all possible player combinations."

#### Q33: "What is the difference between Clean and Adversarial Attribution in your Stability Score?"

> 🗣️ **Say This:**  
> "Clean attribution measures a feature's importance during normal traffic, while adversarial attribution measures its importance under attack. We compare them to identify which features stay stable and which ones collapse under perturbation."

#### Q34: "What is Mutual Information, and why use it before SHAP?"

> 🗣️ **Say This:**  
> "Mutual Information measures how much information a feature shares with the attack class. We use it first as a fast filter in seconds to remove 29 useless features, cutting downstream SHAP computation by over 60%."

---

#### ⚔️ Group C: Adversarial Machine Learning & Threat Models

#### Q35: "What is an Adversarial Attack in machine learning?"

> 🗣️ **Say This:**  
> "An attacker adds tiny, mathematically calculated noise to the input that is imperceptible or within a strict budget, but tricks the machine learning model into predicting the wrong class with high confidence."

#### Q36: "What does the perturbation bound of 0.05 mean practically?"

> 🗣️ **Say This:**  
> "It means no single feature can be modified by more than 5% of its normalized range, keeping the perturbation realistic without altering the core physical nature of the flow."

#### Q37: "What is the difference between FGSM and PGD?"

> 🗣️ **Say This:**  
> "FGSM is a quick, one-step attack that takes a single step along the gradient. PGD is an iterative attack that takes multiple small steps, making it much stronger and the universal benchmark for adversarial testing."

#### Q38: "What is the difference between White-Box and Black-Box attacks?"

> 🗣️ **Say This:**  
> "In a white-box attack, the attacker has full access to the model's weights and gradients. In a black-box attack, the attacker can only query the model with inputs and observe the output predictions without seeing internal weights."

#### Q39: "What is Gradient Masking (Obfuscated Gradients)?"

> 🗣️ **Say This:**  
> "It is a false sense of security where a model breaks or flattens gradients to deceive basic gradient attacks, but remains completely vulnerable to iterative or black-box attacks. We verify our defense is genuine using 100-step PGD and black-box tests."

---

#### 🧪 Group D: Machine Learning & Pipeline Hygiene

#### Q40: "What is SMOTE and what is your strict anti-leakage rule?"

> 🗣️ **Say This:**  
> "SMOTE generates synthetic data along line segments between neighbor points to balance minority classes. We apply SMOTE strictly inside the 72% training partition after splitting, so synthetic samples never leak into test sets."

#### Q41: "Why use Batch Normalization and Dropout in your neural network?"

> 🗣️ **Say This:**  
> "Batch Normalization stabilizes training across features with very different numerical scales, while Dropout deactivates 30% of neurons during training to prevent the network from overfitting on dominant flow classes."

---

## 💡 Quick Presentation Day Checklist
1. **Redoan starts:** Introduces the project, covers Problem, Motivation, Lit Review, and passes the mic smoothly at Slide 7.
2. **Sadman takes over at Slide 8:** Covers Methodology, Math, Architecture, Timeline, Expected Results, and Conclusion.
3. **Practice with a timer:** Aim for Redoan finishing Slide 7 around **3:00**, and Sadman finishing Slide 14 around **6:20–6:35**.
4. **Slide 14 Updated in PowerPoint:** Slide 14 verified and calibrated to undergraduate B.Sc. thesis.



