# Paper Review 21: SHAP Attribution Fingerprinting (Sharma et al., 2025)

**Title:** Forensic Attribution Fingerprinting: Using SHAP for Explainable Adversarial Detection in IoT Networks  
**Authors:** P. Sharma, V. Kumar, et al.  
**Year & Venue:** 2025 | *IEEE Transactions on Information Forensics and Security*, Vol. 20, pp. 1120–1134  
**Category:** Part 2 — Competitor & Alternative Benchmark Defense  

---

## 1. Paper Overview & Short Summary
* **Domain:** Attribution Fingerprinting, Explainable Forensics, IoT Threat Detection.
* **One-Paragraph Summary:** Sharma et al. develop an explainable forensic attribution framework for IoT networks. The system computes SHAP attribution signatures for distinct attack classes, constructing baseline "attribution fingerprints." During inference, the system checks whether incoming flows produce attribution profiles that match known attack signatures or exhibit anomalous attribution drift indicative of adversarial evasion.
* **Main Research Problem:** Black-box classifiers provide classification labels without forensic attribution evidence, preventing incident response teams from diagnosing attack mechanics.
* **Main Motivation:** Using explainable AI attribution vectors as forensic fingerprints to detect and categorize zero-day and adversarial attacks.

---

## 2. Exact Methodology
1. **Fingerprint Database:** Precomputes mean SHAP attribution vectors for each attack class across training data.
2. **Attribution Drift Metric:** For an incoming flow, computes runtime SHAP vector and measures Wasserstein distance to class fingerprints.
3. **Forensic Gate:** Flags flows as adversarial if minimum distance exceeds a threshold.

---

## 3. Key Results & Empirical Findings
* **Dataset:** BoT-IoT and CSE-CIC-IDS2018.
* **Forensic Attribution:** 92.4% attribution accuracy on clean known attack categories.
* **Operational Latency:** Inference latency reaches **140 ms per flow** due to real-time KernelSHAP computation.

---

## 4. Critical Limitations & Flaws
1. **Unusable in Line-Rate Networks:** 140 ms per flow is completely incompatible with high-speed cloud throughput requirements.
2. **Sensitivity to Attribution Perturbation:** Minor input jitter that shifts feature attributions triggers false forensic alarms.

---

## 5. Why Our Proposed Pipeline is Mathematically & Architecturally Superior
* **Offline Attribution Use ($O(1)$ Inference Complexity):** Phase2Net uses SHAP stability **strictly offline** to identify the 27-dimensional invariant subspace, entirely avoiding inference-time explanation computation.
* **Sub-Millisecond Execution:** Phase2Net achieves **< 0.02 ms inference latency**, providing 7,000x faster throughput while delivering robust defense against adversarial evasion.

---

## 6. Defense Board Mock Attack Questions & Viva-Style Answers

> **Committee Member Question 1:** *"Sharma et al. show that computing attribution fingerprints provides forensic explainability for every classified flow. If your proposed methodology eliminates runtime SHAP computation, aren't you sacrificing forensic explainability?"*

### **Our Bullet-Proof Defense Rebuttal (Viva-Style):**

* **🗣️ What to Say in the Viva (15–30 Second Response):**  
  *"Professor, in a live network, you must separate **instant packet blocking** from **offline forensic investigation**. Sharma's method takes 140 milliseconds per packet to calculate an explanation. If an edge firewall waited 140 milliseconds per packet, the entire enterprise network would freeze! Our model blocks the attack instantly in less than 0.02 milliseconds. If a security analyst later needs a detailed forensic report on flagged packets, they can run SHAP asynchronously in an offline sandbox without stopping live traffic."*

* **🧠 Core Intuitive Logic (Easy to Remember):**
  1. **The Fire Alarm Analogy:** When a smoke detector goes off, you don't wait for a chemical laboratory analysis of the smoke particles before sounding the alarm. You sound the alarm instantly (< 0.02 ms), and analyze the soot later in the lab.
  2. **Global Structural Explainability:** We already provide global transparency: operators know *in advance* that the model makes decisions strictly on 27 verified behavioral features.
  3. **Line-Rate Viability:** Microsecond inline forwarding is non-negotiable in cloud engineering.

* **🛡️ Winning Technical Argument:**  
  Inline classification requires $O(1)$ time complexity. Running KernelSHAP on the critical forwarding path introduces unacceptable $O(N \cdot D)$ delays. Forensic explainability should be decoupled from the inline classification engine.

* **⚠️ Viva Trap to Avoid:**  
  *Never say:* "Security analysts don't need explanations."  
  *Safe stance:* "Forensics are vital for post-incident audits, but inline firewalls must make microsecond pass/drop decisions. We decouple real-time enforcement from offline forensic auditing."
