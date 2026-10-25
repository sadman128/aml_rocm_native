# Minimized Pre-Defense Slide Content (15 Slides)

---

### Slide 1: Title Page
* **Title:** Adversarial Robustness in Network Intrusion Detection Systems
* **Subtitle:** via Attribution-Guided Feature Selection and Dynamic Multi-Stage Adversarial Training
* **Candidate:** Sadman Hossain Sajid & Redoan Islam
* **Supervisor:** Mahjabin Sultana | Lecturer, CSE
* **Date:** September 10, 2026

---

### Slide 2: Presentation Outline
* **Heading:** Presentation Outline
* **Supporting:** Overview of the research structure and milestones.
* **Key Info:**
  * 1. Problem Statement
  * 2. Motivation & Objectives
  * 3. Literature Review
  * 4. Comparative Analysis
  * 5. Proposed Methodology
  * 6. Dataset & Environment
  * 7. Target Architecture
  * 8. Research Timeline
  * 9. Expected Results
  * 10. Conclusion

---

### Slide 3: Problem Statement
* **Heading:** AI Firewalls Fail Under Tiny Attacks
* **Supporting:** Modern deep learning reaches >95% accuracy on normal traffic, but drops to ~30% when attackers make tiny, undetectable tweaks to packets.
* **Key Info:**
  * **Performance Drop:** 95% Clean Accuracy → ~30% Robust Accuracy under attack.
  * **Fragile Features:** Classifiers rely on weak traffic clues that attackers can easily disguise.
  * **Shortcut Cheating:** Models memorize IP addresses and port numbers instead of learning real attack behavior.
  * **Stale Defenses:** Existing defenses train once on old attacks, making them helpless against adaptive attackers.

---

### Slide 4: Motivation & Research Objectives
* **Heading:** Motivation & Objectives
* **Supporting:** Building fast, accurate, and honest AI defense for live enterprise networks.
* **Key Info:**
  * **Real-Time Speed:** Detection must take less than 0.05 ms per flow to avoid network delays or dropped packets.
  * **No Accuracy Penalty:** Stop adversarial attacks without sacrificing normal traffic accuracy by filtering out noisy features.
  * **Honest Security:** Completely remove all port and IP shortcuts so the AI learns real attack behavior, with strict zero-leakage testing.

---

### Slide 5: Literature Review (Part 1)
* **Heading:** Literature Review
* **Supporting:** Taxonomy of published defense paradigms and operational trade-offs.
* **Core Defense Paradigms:**
  | Ref | Published Method | Defense Paradigm | Robust Result | Critical Bottleneck |
  | :---: | :--- | :--- | :---: | :--- |
  | **[1]** | **Static Triad Augmentation** | Offline Static Augmentation | 88.0% Defended | Offline staleness; port shortcuts retained |
  | **[2]** | **AMDS (Adaptive Multi-Stage)** | Dynamic Minimax PGD Hardening | 89.4% $\text{PGD}_{20}$ | 2.1% clean drop; unpruned 78-dim overhead |
  | **[3]** | **XAI-Centroid Gate** | Runtime Attribution (SHAP) | 88.5% Detection | Severe latency (85–220 ms); violates line rate |
  | **[4]** | **CSAGC-IDS** | Channel-Spatial Graph Attention | 76.2% Robust | Buffering delay (>2.4 ms); topology spoofing |
  | **[7]** | **Randomized Smoothing** | Certified Provable $L_2$ Radius | Provable Guarantees | Clean accuracy crash: 94.5% → 76.2% (-18.3%) |
* **Key Literature Finding:** Existing defenses force a harsh trade-off between clean accuracy, real-time speed, and compute cost.

---

### Slide 6: Literature Review (Part 2)
* **Heading:** Literature Review
* **Supporting:** Three core structural vulnerabilities identified across existing NIDS defenses.
* **Key Vulnerabilities:**
  * **1. Perturbation Staleness [1]:** Static offline attacks lose defense efficacy as model weights shift during training (16%–20% evasion rate).
  * **2. Line-Rate Latency Barrier [3, 4]:** Runtime XAI (85–220 ms) and graph buffering (>2.4 ms) cause buffer overflow on microsecond cloud switches.
  * **3. Shortcut Memorization & Nominal Bias [1, 18]:** Nominal-only feature selection retains volatile features and ephemeral port shortcuts.


---

### Slide 7: Comparative Analysis
* **Heading:** Comparative Analysis
* **Supporting:** State-of-the-art benchmark frontiers: Every published defense faces a critical trade-off.
* **Benchmark Frontier:**
  | Benchmark Frontier | Published Method & Ref | Best Result | Defense Mechanism | Limitation |
  | :--- | :--- | :---: | :--- | :--- |
  | **Best Clean Accuracy** | **Deep MLP [5] / CSAGC-IDS [4]** | **98.2%** Clean | Standard Deep MLP / Graph Attention | **Zero Defense:** Collapses to **<32%** under white-box PGD; or 2.4 ms delay. |
  | **Best White-Box Robustness** | **AMDS [2]** | **89.4%** $\text{PGD}_{20}$ | Multi-Stage Dynamic PGD | **Clean Drop & Overhead:** 2.1% clean penalty; keeps 78 dimensions (+140% GPU). |
  | **Best Static Defense** | **Static Triad [1]** | **88.0%** Defended | Static Triad Augmentation | **Staleness & Shortcuts:** Offline attacks go stale (16–20% evasion); retained ports. |
  | **Best Black-Box Robustness** | **Query Anomaly Tracker [6]** | **88.6%** Black-Box | Query Anomaly Tracking | **High Complexity:** Stateful memory tracking; vulnerable to adaptive transfer. |
  | **Best Certified Defense** | **Randomized Smoothing [7]** | **Provable $L_2$ Radius** | Randomized Smoothing | **Severe Accuracy Crash:** Clean accuracy dropped from 94.5% → 76.2% (-18.3%). |
* **Key Takeaway:** Across published literature, no existing defense achieves high robustness without sacrificing clean accuracy, line-rate speed, or computational efficiency.

---

### Slide 8: Proposed Methodology (Part 1)
* **Heading:** Data Sanitization & Screening
* **Supporting:** Strict zero-leakage protocol and coarse dimensionality reduction.
* **Key Info:**
  * **Sanitization:** Remove IPs, Ports, Timestamp, Flow ID → 69 continuous features remain.
  * **Strict Partitioning:** 80% Dev (72% Train / 8% Val) | 20% Test (Locked Day 0).
  * **MI Screening:** Shannon Mutual Information filters 69 down to top 40 candidates.
  * **SMOTE Balancing:** Applied exclusively within the 72% training partition.

---

### Slide 9: Proposed Methodology (Part 2)
* **Heading:** Pillar 1 — Adversarial Stability SHAP
* **Supporting:** Isolating the 27 perturbation-invariant features.
* **Key Info:**
  * **Step 1:** Train canary MLP on clean data (40 features).
  * **Step 2:** Dual-state audit via PGD-20 (measure clean vs. adversarial SHAP).
  * **Step 3:** Calculate exact Stability Score ($S_j$).
  * **Step 4:** Apply 80% cumulative stability-mass rule.
  * **Result:** 27 stable features selected; 13 volatile features permanently pruned.

---

### Slide 10: Proposed Methodology (Part 3)
* **Heading:** Pillar 2 — Two-Phase Dynamic Hardening
* **Supporting:** Curriculum training to mitigate static attack staleness.
* **Key Info:**
  * **Phase 1 (Epochs 1-10):** Clean warmup. Weights settle in a stable geometric basin.
  * **Phase 2 (Epochs 11-50):** 5-step online PGD generated fresh per mini-batch.
  * **Joint Objective:** Balances clean and adversarial loss (0.5/0.5).
  * **Outcome:** Tracks shifting decision boundaries while preserving benign accuracy.

---

### Slide 11: Dataset & Environment
* **Heading:** Dataset & Environment
* **Supporting:** Large-scale evaluation on the CSE-CIC-IDS2018 benchmark.
* **Key Info:**
  * **Dataset:** 6,320,003 valid flows from CSE-CIC-IDS2018 [16] (Curated Benchmark [19]: `dhoogla/csecicids2018`).
  * **Hardware/Software:** AMD Radeon RX 7600 (8 GB), native ROCm PyTorch (Windows).
  * **Topology:** 4-Layer MLP (27 → 128 → 64 → 32 → 2).
  * **Layer Design:** Linear → BatchNorm → ReLU → Dropout(0.30).
  * **Speed:** Highly optimized batch operations (~70 min train time).

---

### Slide 12: Research Timeline
* **Heading:** Weekly Gantt Chart
* **Supporting:** 14-week schedule from July 4 to October 11, 2026.
* **Key Info:**
  * **Weeks 1-7 (Completed):** Literature review, methodology formulation, and environment setup.
  * **Sep 10 (Current Milestone):** Pre-Defense Presentation.
  * **Weeks 11-12 (Upcoming):** Multi-threat empirical evaluation.
  * **Weeks 13-14 (Upcoming):** Result analysis & manuscript drafting.
  * **Oct 11 (Final Milestone):** Thesis Defense.

---

### Slide 13: Expected Results
* **Heading:** Performance Targets
* **Supporting:** Comprehensive multi-threat evaluation protocol (FGSM, DeepFool, PGD, CW, Square Attack).
* **Key Info:**
  * **Clean Accuracy:** ≥ 95.5% (mitigating the standard AT penalty).
  * **Robust Accuracy:** 88.0%–90.5% against PGD-100 (ε=0.05).
  * **Attack Success Rate:** < 12.0% under white-box iterative attacks.
  * **Inference Speed:** < 0.05 ms per-flow (line-rate capability).
  * **Verification:** Check against gradient obfuscation via DeepFool and black-box transferability.

---

### Slide 14: Conclusion & Next Steps
* **Heading:** Core Contributions & Roadmap
* **Supporting:** A dynamic, lightweight pipeline robust against adaptive evasion.
* **Key Info:**
  * **Feature Selection & Balancing:** Adversarial Stability SHAP (27 features) with leak-free SMOTE.
  * **Two-Phase Training:** Clean warmup + live online PGD eliminating attack staleness.
  * **Multi-Threat Evaluation:** Rigorous benchmarking across white-box (FGSM, DeepFool, PGD, CW) and black-box threats.
  * **Immediate Next Step:** Complete full empirical runs and manuscript drafting for the October defense.

---

### Slide 15: References (Academic Bibliography)
* **Heading:** References
* **Supporting:** Comprehensive bibliography of foundational papers, peer defense frameworks, and benchmark datasets.
* **Key Citations:**
  * **[1] Static Triad Augmentation:** Holla et al., *IEEE Access*, 2025.
  * **[2] AMDS Dynamic Hardening:** Olukola & Rahimi, *IEEE TIFS*, 2026.
  * **[3] XAI-Centroid Gate:** Güvenç Paltun et al., *IEEE Trans. Rel.*, 2025.
  * **[4] CSAGC-IDS Graph Attention:** Zeng et al., *IEEE IoTJ*, 2025.
  * **[5] Deep Feedforward MLP:** Roshan et al., *IEEE Access*, 2023.
  * **[6] Query Anomaly Tracking:** Ennaji et al., *IEEE TIFS*, 2025.
  * **[7] Provable Certified Robustness:** Zhou et al., *IEEE TDSC*, 2023.
  * **[8] PGD Minimax Hardening:** Madry et al., *ICLR*, 2018.
  * **[9] FGSM Baseline:** Goodfellow et al., *ICLR*, 2015.
  * **[10] TRADES Regularization:** Zhang et al., *ICML*, 2019.
  * **[11] SHAP Attribution:** Lundberg & Lee, *NeurIPS*, 2017.
  * **[12] Obfuscated Gradients Diagnostic:** Athalye et al., *ICML*, 2018.
  * **[13] Square Attack:** Andriushchenko et al., *ECCV*, 2020.
  * **[14] Boundary Attack:** Brendel et al., *ICLR*, 2018.
  * **[15] SMOTE Oversampling:** Chawla et al., *JAIR*, 2002.
  * **[16] CSE-CIC-IDS2018 Benchmark:** Sharafaldin et al., *Proc. ICISSP*, 2018.
  * **[17] Trade-Off Theorem:** Tsipras et al., *ICLR*, 2019.
  * **[18] Shortcut & Port Leakage:** Engelen et al., *ACM CCS*, 2021.
  * **[19] Curated Benchmark Dataset:** D'hooge et al., Hugging Face (`dhoogla/csecicids2018`), 2020/2023.
