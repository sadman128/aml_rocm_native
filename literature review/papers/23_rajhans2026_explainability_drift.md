# Paper Review 23: Explainability Drift in Cybersecurity (Rajhans & Khawarey, 2026)

**Title:** Explainability Drift in Cybersecurity Classifiers: Quantifying Attribution Divergence Under Distribution Shift  
**Authors:** A. Rajhans and S. Khawarey  
**Year & Venue:** 2026 | *IEEE Security & Privacy* / arXiv:2601.xxxxx  
**Category:** Part 2 — Competitor & Alternative Benchmark Defense  

---

## 1. Paper Overview & Short Summary
* **Domain:** Explainability Drift, Concept Drift, Model Degradation in NIDS.
* **One-Paragraph Summary:** Rajhans and Khawarey investigate the phenomenon of "explainability drift" in machine learning security models. They prove that as network traffic undergoes natural temporal distribution shift or adversarial manipulation, the model's feature attributions diverge significantly *before* a drop in raw classification accuracy is observed. They propose monitoring attribution drift as an early warning indicator for model degradation.
* **Main Research Problem:** Traditional NIDS monitoring detects model degradation only after classification error rates spike, causing delayed incident response.
* **Main Motivation:** Using attribution drift metrics as proactive telemetry to detect concept drift and stealthy adversarial campaigns.

---

## 2. Exact Methodology
1. **Attribution Drift Formulation:** Measures divergence between baseline training attribution distribution and operational attribution distribution using Kullback-Leibler (KL) divergence.
2. **Early Warning Trigger:** Alerts administrators when drift exceeds a threshold, prompting retraining.

---

## 3. Key Results & Empirical Findings
* **Dataset:** CSE-CIC-IDS2018.
* **Early Detection:** Identifies distribution drift and stealthy evasion attacks up to 48 hours before overall classification accuracy drops by > 5%.
* **Finding:** 68% of features in standard NIDS models exhibit severe explainability drift under minor traffic distribution changes.

---

## 4. Critical Limitations & Flaws
1. **Computational Cost of Continuous Auditing:** Calculating daily SHAP distributions across millions of operational flows imposes heavy computational overhead on logging infrastructure.
2. **Passive Detection:** The method is purely diagnostic; it detects drift but does not actively prevent the model from misclassifying drifted flows.

---

## 5. Why Our Proposed Pipeline is Mathematically & Architecturally Superior
* **Proactive Invariance Engineering:** Instead of monitoring drift passively after deployment, Phase2Net eliminates drift-prone features **before deployment** by discarding features with $S(f_j) < \tau$.
* **Mathematically Bounded Attribution Manifold:** By training strictly on the 27 stable features under dynamic min-max PGD, Phase2Net's representations are intrinsically regularized against attribution drift.

---

## 6. Defense Board Mock Attack Questions & Viva-Style Answers

> **Committee Member Question 1:** *"Rajhans & Khawarey show that 68% of features exhibit severe explainability drift over time. How can you guarantee that your 27 chosen features won't suffer from explainability drift in production?"*

### **Our Bullet-Proof Defense Rebuttal (Viva-Style):**

* **🗣️ What to Say in the Viva (15–30 Second Response):**  
  *"Professor, Rajhans found that 68% of features drift because standard models rely heavily on transient network artifacts—like IP addresses, dynamic port numbers, and temporary window sizes—which change every day. Our 27 features deliberately exclude all ephemeral socket identifiers. Instead, we select fundamental physical traffic dynamics: packet length distributions and inter-arrival time statistics. These transport behaviors are governed by network protocol physics, which remain stable over time. Furthermore, our stability metric $S_j$ explicitly measures and weeds out any feature that drifts under perturbation."*

* **🧠 Core Intuitive Logic (Easy to Remember):**
  1. **Weather vs. Climate:** Transient socket fields (ports, IPs) are like daily weather—they change constantly. Behavioral packet distributions are like climate—they represent stable, long-term physical laws.
  2. **Drift Filtering Built-In:** If a feature drifts under attack, its stability score drops, and our offline selector discards it.
  3. **Proactive vs. Reactive:** Rajhans watches the car engine overheat; we remove the bad engine parts before driving.

* **🛡️ Winning Technical Argument:**  
  Our dual-state stability metric $S(f_j)$ directly optimizes for low attribution divergence: $|\phi_j(\mathcal{D}) - \phi_j(\mathcal{D}_{\text{adv}})| \to 0$. Features that survive filtering lie on an invariant sub-manifold.

* **⚠️ Viva Trap to Avoid:**  
  *Never say:* "Network drift doesn't exist."  
  *Safe stance:* "Network concept drift is real, which is why eliminating socket identifiers and selecting physically grounded transport statistics is necessary to maintain long-term model reliability."
