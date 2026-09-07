# Minimized Pre-Defense Slide Content

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
* **Heading:** Current Research Landscape
* **Supporting:** Survey of 40 peer-reviewed defenses spanning 2021–2026.
* **Key Info:**
  * **Clean Trade-Off:** ~2%–6% accuracy drop when hardening unpruned models.
  * **Tree Vulnerability:** Ensembles fail heavily (>80% ASR) under iterative gradient attacks.
  * **Static Staleness:** Pre-generated adversarial samples show 16%–20% evasion rates.
  * **Latency Overhead:** Runtime XAI/Graph models incur 85–220ms delays, failing line-rate constraints.

---

### Slide 6: Literature Review (Part 2)
* **Heading:** Landmark Peer Defenses
* **Supporting:** Analysis of recent state-of-the-art architectures and their limitations.
* **Key Info:**
  * **Holla et al. (Base):** Restores accuracy to 88%. *Limit:* Retains ports & suffers static staleness.
  * **Olukola & Rahimi (AMDS):** 89.4% robust accuracy. *Limit:* Full 78-dimension burden (+140% overhead).
  * **Güvenç Paltun et al.:** Runtime SHAP verification. *Limit:* 85-220 ms inference (too slow).
  * **Zeng et al. (CSAGC):** Graph attention. *Limit:* >2.4 ms batch delay & topology spoofing risk.

---

### Slide 7: Comparative Analysis
* **Heading:** Comparative Analysis
* **Supporting:** Empirical benchmarks across 40 surveyed papers: Every best result has a limitation.
* **Key Info:**
  * **Best Clean Acc:** 98.2% (Roshan et al.) — *Limitation:* Zero defense (<32% under attack).
  * **Best White-Box Robustness:** 89.4% (Olukola & Rahimi) — *Limitation:* 2.1% clean drop, 78 dimensions (+140% GPU cost).
  * **Best Static Defense:** 88.0% (Holla et al. - Base) — *Limitation:* Static attack staleness & port shortcuts.
  * **Best Black-Box Robustness:** 88.6% (Ennaji et al.) — *Limitation:* Complex stateful query tracking.
  * **Best Certified Defense:** Provable L2 radius (Zhou et al.) — *Limitation:* Clean accuracy crashed by 18.3% (to 76.2%).

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
  * **Dataset:** 6,320,003 valid flows.
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
* **Supporting:** Comprehensive multi-threat evaluation protocol.
* **Key Info:**
  * **Clean Accuracy:** ≥ 95.5% (mitigating the standard AT penalty).
  * **Robust Accuracy:** 88.0%–90.5% against PGD-100 (ε=0.05).
  * **Attack Success Rate:** < 12.0% under white-box iterative attacks.
  * **Inference Speed:** < 0.05 ms per-flow (line-rate capability).
  * **Verification:** Check against gradient obfuscation via black-box transferability.

---

### Slide 14: Conclusion & Next Steps
* **Heading:** Core Contributions & Roadmap
* **Supporting:** A dynamic, lightweight pipeline robust against adaptive evasion.
* **Key Info:**
  * **Theoretical:** 80% stability-mass rule isolates invariant subspace (27 features).
  * **Architectural:** Two-phase dynamic PGD reduces staleness.
  * **Methodological:** Strict zero-leakage and port-shortcut removal.
  * **Immediate Next Step:** Execute 3-seed evaluation across 9 threat models for the final defense.
