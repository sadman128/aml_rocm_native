# Pre-Defense Presentation & Viva Defense Kit (September 10, 2026)

This directory contains the master slide materials, viva scripts, and defense Q&A for your Master's Thesis Proposal / Pre-Defense presentation:  
**"Adversarial Robustness in Network Intrusion Detection Systems via Attribution-Guided Feature Selection and Dynamic Multi-Stage Adversarial Training"**

---

## 🎯 Topic Distribution & Slide Structure (14 Slides Total)

The presentation maps your required 11 core sections across **15 dedicated slides**, allocating deep focus to **Literature Review (2 slides)** and **Proposed Methodology (3 slides)**:

| Required Topic | Slide Number & Title | Focus & Core Contents |
| :--- | :--- | :--- |
| **1. Title Page** | **Slide 1:** Title Page | Thesis title, candidate credentials, supervisor, department, date. |
| **2. Outline** | **Slide 2:** Presentation Outline | Numbered roadmap through the 11 presentation topics. |
| **3. Problem Statement** | **Slide 3:** Problem Statement | NIDS vulnerability, bounded perturbation threat model ($\ell_\infty \le 0.05$), continuous feature scope. |
| **4. Motivation** | **Slide 4:** Motivation & Objectives | Line-rate cloud requirements, Tsipras' dilemma, testable research objective, zero-leakage hygiene. |
| **5. Literature Review (Part 1)** | **Slide 5:** Taxonomy of Published Defenses | **Paradigms & Trade-offs:** Offline augmentation [1], dynamic PGD [2], runtime XAI [3], and graph attention [4]; clean trade-off and latency dilemmas. |
| **5. Literature Review (Part 2)** | **Slide 6:** Landmark Peer Benchmarks | **Deep dive on direct peers:** Static Triad [1] (base benchmark), AMDS [2], XAI Gate [3], CSAGC-IDS [4] (methods, results, bottlenecks). |
| **6. Comparison** | **Slide 7:** Comparative Analysis & Gaps | 5-row frontier benchmark table directly connecting published limits to what our pipeline addresses. |
| **7. Proposed Methodology (Part 1)** | **Slide 8:** Sanitization & Screening | Purging socket shortcuts (69 continuous dims), strict zero-leakage 72/8/20 split on 6.32M flows, Mutual Information screening (69 $\to$ 40), continuous SMOTE. |
| **7. Proposed Methodology (Part 2)** | **Slide 9:** Pillar 1 — Stability SHAP | Canary model auditing under $\text{PGD}_{20}$, exact normalized formula $S_j$, **80% cumulative stability-mass selection rule** isolating **27 stable features**. |
| **7. Proposed Methodology (Part 3)** | **Slide 10:** Pillar 2 — Dynamic Hardening | Phase 1 clean warmup (epochs 1–10) + Phase 2 live online 5-step PGD (epochs 11–50, $\alpha = 0.005$) with balanced 50/50 clean/adversarial loss. |
| **8. Dataset and Environment** | **Slide 11:** Dataset, Environment & Arch | CSE-CIC-IDS2018 (**6,320,003 valid flows**), **AMD Radeon RX 7600 (8 GB VRAM)** + ROCm PyTorch stack, 4-layer MLP topology ($27 \to 128 \to 64 \to 32 \to 2$). |
| **9. Gantt Chart** | **Slide 12:** Weekly Timeline & Gantt Chart | Weekly schedule July 4 to Oct 11, pre-defense milestone (Sep 10), execution milestones. |
| **10. Expected Result** | **Slide 13:** Expected Results & Hypotheses | Target clean ($\ge 95.5\%$) and robust ($88.0\% - 90.5\%$) hypotheses, 9-threat evaluation suite, diagnostic checks against gradient masking, sub-0.05 ms latency target. |
| **11. Conclusion** | **Slide 14:** Conclusion & Next Milestones | Summary of 3 core contributions, 2x2 factorial ablation study design, immediate timeline toward final defense. |
| **References** | **Slide 15:** References (Academic Bibliography) | Comprehensive bibliography indexing all 18 cited foundation papers, peer defenses, and benchmark hygiene standards. |

---

## 📁 Package Contents & File Guide

| File | Purpose | How to Use |
| :--- | :--- | :--- |
| **[SLIDES_ONLY.md](file:///f:/PythonProjects/aml_rocm_native/docs/pre_defense/SLIDES_ONLY.md)** | **Raw Slide Content (14 Slides)** | Copy-paste clean bullet points, tables, ASCII Gantt chart, and formulas directly into your slide deck. Contains zero speaker notes. |
| **[PRE_DEFENSE_SLIDES.md](file:///f:/PythonProjects/aml_rocm_native/docs/pre_defense/PRE_DEFENSE_SLIDES.md)** | **Master Presentation Guide** | Practice your oral delivery. Contains layout suggestions, on-slide content, and timed viva-style speaker notes (~1 minute per slide). |
| **[BOARD_CROSS_EVALUATION.md](file:///f:/PythonProjects/aml_rocm_native/docs/pre_defense/BOARD_CROSS_EVALUATION.md)** | **Defense Interrogation & Rebuttals** | Rehearse committee Q&A. Covers the most critical attack angles (Systems, ML Theory, Data Science, and Chair) with 15–30 second bullet-proof viva answers. |

---

## 🎯 Key Methodological Quick Recall Sheet (Exact Experimental Settings)

* **Data Partitioning (Strict Zero-Leakage on 6,320,003 Valid Flows):**
  * Initial split: **80% Development (5,056,002 flows) / 20% Held-Out Test (1,264,001 flows)** (locked on Day 0)
  * Development sub-partition (90/10): **72% Core Training (4,550,401 flows)** / **8% Validation (505,601 flows)** / **20% Test (1,264,001 flows)**
  * Scalers fitted strictly on the 72% Core Training partition.
* **Feature Dimensionality Reduction:**
  * **69 continuous numerical features** (IPs, Ports, Flow IDs purged)
  * $\to$ **40 candidate features** (Mutual Information coarse filter)
  * $\to$ **27 stable features** (**80% cumulative stability-mass selection rule**):
    $$\min m \quad \text{s.t.} \quad \sum_{j=1}^m S_j \ge 0.80 \cdot S_{\text{total}}, \quad S_j = 1 - \frac{|\bar{\phi}^{\text{clean}}_j - \bar{\phi}^{\text{adv}}_j|}{\max(\bar{\phi}^{\text{clean}}_j + \bar{\phi}^{\text{adv}}_j, 10^{-10})}$$
* **PGD Step Allocation:**
  * **Training (Phase 2):** 5-step online PGD ($\text{PGD}_5, \epsilon=0.05, \mathbf{\alpha=0.005}$)
  * **Stability Auditing (Pillar 1):** 20-step PGD ($\text{PGD}_{20}, \epsilon=0.05$)
  * **Final Evaluation Suite:** 100-step PGD ($\text{PGD}_{100}, \epsilon=0.05$) + Auto-PGD, CW, FGSM, Square Attack
* **Hardware & Target Architecture:**
  * Hardware: **AMD Radeon RX 7600 (8 GB VRAM)**, native ROCm PyTorch
  * 4-Layer MLP: $\mathbf{27} \to \mathbf{128} \to \mathbf{64} \to \mathbf{32} \to \mathbf{2}$ (BatchNorm, ReLU, Dropout 0.30, ~14,000 parameters)
  * Inference latency: Sub-0.05 ms amortized target ($<0.02$ ms preliminary benchmark).
