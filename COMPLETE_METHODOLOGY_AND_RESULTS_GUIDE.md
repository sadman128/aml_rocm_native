# Phase2Net: The Definitive Beginner-to-Expert Master Guide
## An Exhaustive, Pedagogical Breakdown of Methodology, Mathematical Foundations, Concrete Numerical Walkthroughs, and 3-Seed Experimental Results

---

> **Executive Note for Non-Computer Science Readers:**  
> This guide is specifically written so that someone with **zero prior knowledge** of computer science, programming, or advanced calculus can read it from start to finish and fully understand:
> 1. Exactly what a cyberattack looks like at the mathematical level.
> 2. Why traditional Artificial Intelligence (AI) fails when hackers tamper with network data.
> 3. How Phase2Net's mathematical innovations (Adversarial Stability SHAP and Dynamic Online PGD) solve these problems.
> 4. Every single formula, parameter, metric, and experimental outcome, demonstrated with concrete numbers and step-by-step arithmetic.

---

# Table of Contents
1. [The Unified Running Metaphor: The High-Tech Airport Scanner](#1-the-unified-running-metaphor-the-high-tech-airport-scanner)
2. [The "Zero-to-Hero" Comprehensive Glossary](#2-the-zero-to-hero-comprehensive-glossary)
3. [Real-World Anatomy: What Does a Network Flow Actually Look Like?](#3-real-world-anatomy-what-does-a-network-flow-actually-look-like)
4. [The Core Scientific Dilemma: Adversarial Attacks & Why Defenses Fail](#4-the-core-scientific-dilemma-adversarial-attacks--why-defenses-fail)
5. [System Architecture Flowchart](#5-system-architecture-flowchart)
6. [Stage 1: Raw Dataset Ingestion, Cleaning & Zero-Leakage Splitting](#6-stage-1-raw-dataset-ingestion-cleaning--zero-leakage-splitting)
7. [Stage 2: Candidate Feature Filtering via Mutual Information (MI)](#7-stage-2-candidate-feature-filtering-via-mutual-information-mi)
8. [Stage 3: Resilient Class Balancing via SMOTE](#8-stage-3-resilient-class-balancing-via-smote)
9. [Stage 4: Adversarial Stability SHAP Feature Selection (Core Novelty 1)](#9-stage-4-adversarial-stability-shap-feature-selection-core-novelty-1)
10. [Stage 5: Target Neural Network Architecture & Internal Mechanics](#10-stage-5-target-neural-network-architecture--internal-mechanics)
11. [Stage 6: Two-Phase Dynamic Online Adversarial Training (Core Novelty 2)](#11-stage-6-two-phase-dynamic-online-adversarial-training-core-novelty-2)
12. [Stage 7: Multi-Threat Evaluation Suite & The 9 Attack Formulations](#12-stage-7-multi-threat-evaluation-suite--the-9-attack-formulations)
13. [Evaluation Metrics & Step-by-Step Arithmetic Walkthroughs](#13-evaluation-metrics--step-by-step-arithmetic-walkthroughs)
14. [Complete Experimental Results Across 3 Random Seeds](#14-complete-experimental-results-across-3-random-seeds)
15. [Diagnostic Sweeps & Rigorous Scientific Proof Against Gradient Masking](#15-diagnostic-sweeps--rigorous-scientific-proof-against-gradient-masking)
16. [Computational Hardware Budget, Execution Times & Real-Time Latency](#16-computational-hardware-budget-execution-times--real-time-latency)
17. [Practitioner Guide to Reading the Output CSV & JSON Files](#17-practitioner-guide-to-reading-the-output-csv--json-files)
18. [Frequently Asked Questions (FAQ) for General Readers](#18-frequently-asked-questions-faq-for-general-readers)

---

# 1. The Unified Running Metaphor: The High-Tech Airport Scanner

Throughout this document, we will anchor every computer science concept to a single, intuitive real-world story: **An Automated Airport Luggage Security Scanner**.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   THE AIRPORT SCANNER METAPHOR                                   │
├───────────────────────────────┬──────────────────────────────────────────────────────────────────┤
│ Computer Science Concept      │ Real-World Airport Metaphor                                      │
├───────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ Network Traffic               │ Millions of passengers walking through an international terminal.│
│ Network Packets               │ Individual items inside a suitcase (shoes, shirts, bottles).     │
│ Network Flow                  │ The summarized baggage tag & X-ray scan report (total weight,    │
│                               │ bag dimensions, number of metal zippers, density).               │
│ Benign Flow (Class 0)         │ An innocent traveler's suitcase containing clothes and books.    │
│ Attack Flow (Class 1)         │ A smuggler's suitcase carrying dangerous contraband (a weapon).   │
│ NIDS Classifier (AI Model)    │ The automated software analyzing the X-ray scan to sound alarms. │
│ Adversarial Evasion Attack    │ A smuggler coating the contraband with a special thin foil so the│
│                               │ X-ray sensor misinterprets its shape as a harmless shampoo bottle.│
│ Perturbation Budget (ε)       │ The maximum allowable thickness of the foil before airport       │
│                               │ physical inspectors notice that the bag looks visibly deformed.  │
│ False Alarm (False Positive)  │ The alarm rings on an innocent tourist, causing airport delays.  │
│ Missed Attack (False Negative)│ The weapon slips past the scanner into the secure terminal!      │
└───────────────────────────────┴──────────────────────────────────────────────────────────────────┘
```

---

# 2. The "Zero-to-Hero" Comprehensive Glossary

Every technical term used in AI and cybersecurity is defined below in plain English:

### 💡 What is a Bit and a Byte?
* A **bit** is the smallest unit of digital information (a single electrical switch: $0$ or $1$).
* A **byte** is a group of 8 bits. One byte can store a single letter (e.g., `"A"`).
* **Kilobyte (KB):** ~1,000 bytes; **Megabyte (MB):** ~1,000,000 bytes.

### 💡 What is Float32?
Computers store integers (whole numbers like $1, 2, 3$) and floating-point numbers (decimals like $3.14159$). `Float32` means the computer allocates exactly 32 bits of memory to store a decimal number with high precision.

### 💡 What is a Network Protocol (TCP, UDP, ICMP)?
A **protocol** is an agreed-upon set of rules for communication, like international diplomacy etiquette:
* **TCP (Transmission Control Protocol):** Like certified registered mail with a return receipt. The sender and receiver shake hands; every packet is tracked, and if one is lost, it is re-sent.
* **UDP (User Datagram Protocol):** Like shouting out a window or sending a postcard. It is super-fast because there is no handshake or receipt (used for live video streaming or gaming).
* **ICMP (Internet Control Message Protocol):** Diagnostic messages (like pinging a server to see if it is alive).

### 💡 What is a Feature (Dimension / Attribute)?
A measurable numerical characteristic of an event. If we were predicting a person's health, features would be: `Heart Rate`, `Blood Pressure`, `Age`, and `Weight`. In network security, features are statistical properties of the connection, such as `Flow Duration` or `Total Forward Packets`.

### 💡 What is a Label (Target / Ground Truth)?
The true answer that the AI is trying to guess. In our binary classification problem:
* **$Y = 0$ (Benign):** Safe, legitimate user activity.
* **$Y = 1$ (Attack):** Malicious intrusion attempt.

### 💡 What is a Weight ($w$) and a Bias ($b$)?
Inside a neural network, a mathematical formula decides the outcome:
$$\text{Score} = (w_1 \cdot x_1) + (w_2 \cdot x_2) + \dots + b$$
* **Weights ($w$):** Dials that control how much importance the AI gives to each feature. If $w_1$ is large and positive, feature $x_1$ strongly screams "Attack!"
* **Bias ($b$):** An internal offset dial that shifts the prediction baseline.
* **Training an AI** simply means using calculus to turn all these millions of dials until the AI rarely makes mistakes.

### 💡 What is an Activation Function (ReLU)?
Without activation functions, a neural network is just a giant linear equation (it can only draw straight lines or flat planes). The **ReLU (Rectified Linear Unit)** function introduces a simple non-linear rule:
$$\text{ReLU}(z) = \max(0, z)$$
* If the number is negative, reset it to $0$.
* If positive, let it pass through unchanged.
* *Analogy:* A one-way electrical check-valve.

### 💡 What is a Loss Function (Binary Cross-Entropy)?
The AI's grading rubric. If an attack occurs ($y=1$) and the model predicts an attack probability $\hat{y} = 0.99$, the penalty is near zero:
$$\mathcal{L}_{\text{CE}} = - \left[ y \log(\hat{y}) + (1 - y) \log(1 - \hat{y}) \right]$$
* **Toy Math Check:**
  * If actual $y = 1$ and model predicts $\hat{y} = 0.99$: $\mathcal{L} = -\log(0.99) = \mathbf{0.01}$ (Minimal penalty!).
  * If actual $y = 1$ and model mistakenly predicts $\hat{y} = 0.01$: $\mathcal{L} = -\log(0.01) = \mathbf{4.60}$ (Huge penalty!).

### 💡 What is a Gradient ($\nabla$)?
In multi-dimensional calculus, the gradient is an arrow pointing in the direction of steepest uphill ascent.
* **Gradient Descent (Defenders):** The AI calculates the gradient of its mistakes and steps **downhill** to minimize errors.
* **Gradient Ascent (Hackers):** The attacker calculates the gradient of the AI's loss and steps **uphill** to maximize the AI's confusion!

### 💡 What is an Epoch?
* **Analogy:** Imagine reading a 500-page textbook from page 1 to page 500. Doing that once is **1 Epoch**.
* Training for **50 Epochs** means the AI has reviewed the entire 7-million-flow dataset 50 complete times.

### 💡 What is a Mini-Batch?
Attempting to feed 7 million records into a computer's memory at once causes an immediate system crash. We break the data into manageable groups called **mini-batches**. In Phase2Net, our batch size is **2,048 flows**. The model examines 2,048 flows, updates its dials, and moves to the next batch.

### 💡 What is Learning Rate ($\eta$ or $\alpha$)?
The step size the algorithm takes when adjusting its dials.
* If too large ($\eta = 1.0$), the model overshoots and destroys its learned knowledge.
* If too small ($\eta = 0.000001$), training takes months.
* We use the industry gold-standard: $\eta = 0.001$.

### 💡 What is an Optimizer (Adam)?
**Adam (Adaptive Moment Estimation)** is the automatic navigator. Instead of taking rigid step sizes, Adam tracks the moving average of past gradients and automatically slows down when approaching optimal solutions, preventing wild oscillations.

### 💡 What is Stratified Splitting?
* **Analogy:** Imagine a bowl with 80 green apples and 20 red apples. If you blindly grab a handful, you might get 15 red apples and 5 green ones, distorting the proportion.
* **Stratified Splitting** guarantees that every slice of data (Training, Validation, and Testing) has the exact same ratio: exactly $79.02\%$ Benign and $20.98\%$ Attack flows.

### 💡 What is the $L_\infty$ Norm and Epsilon ($\epsilon$)?
The **$L_\infty$ (L-infinity) norm** measures the **single largest absolute change** made to any individual feature:
$$\|\delta\|_\infty = \max\left( |\delta_1|, |\delta_2|, \dots, |\delta_M| \right)$$
* When we specify an **attack budget of $\epsilon = 0.05$**, it means: *The hacker is strictly forbidden from changing ANY individual standardized feature by more than $\pm 0.05$.* This guarantees the attack remains stealthy and realistic.

---

# 3. Real-World Anatomy: What Does a Network Flow Actually Look Like?

To demystify "network flows," here is an excerpt of what actual records from the **CSE-CIC-IDS2018** benchmark look like before mathematical processing:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            SAMPLE RAW NETWORK FLOW TELEMETRY RECORD                              │
├──────────────────────────────────────┬────────────────────────┬──────────────────────────────────┤
│ Feature Name                         │ Typical Benign Flow    │ Typical DDoS Attack Flow         │
├──────────────────────────────────────┼────────────────────────┼──────────────────────────────────┤
│ Protocol                             │ TCP (6)                │ TCP (6)                          │
│ Flow Duration                        │ 4,521,032 μs (4.5 sec) │ 120 μs (Super-fast burst!)       │
│ Total Forward Packets                │ 12 packets             │ 2 packets                        │
│ Total Backward Packets               │ 10 packets             │ 0 packets (Never waits for reply)│
│ Total Length of Fwd Packets          │ 840 bytes              │ 0 bytes (Empty probe)            │
│ Flow Bytes/s                         │ 185.8 bytes/s          │ 0.0 bytes/s                      │
│ Flow Packets/s                       │ 4.86 pkts/s            │ 16,666.6 pkts/s (Violent flood!) │
│ Flow Inter-Arrival Time (IAT) Mean   │ 410,993 μs             │ 60 μs                            │
│ SYN Flag Count                       │ 1                      │ 1                                │
│ ACK Flag Count                       │ 1                      │ 0                                │
│ Average Packet Size                  │ 76.36 bytes            │ 0.0 bytes                        │
│ Init Win Bytes Forward               │ 29,200 bytes           │ 1,024 bytes                      │
│ True Class Label                     │ 0 (BENIGN)             │ 1 (MALICIOUS ATTACK)             │
└──────────────────────────────────────┴────────────────────────┴──────────────────────────────────┘
```

Notice how distinct the numbers look to a human! A benign web-browsing session lasts several seconds and exchanges data back and forth. A DDoS attack fires millions of tiny, empty connection requests per second to overwhelm the server.

---

# 4. The Core Scientific Dilemma: Adversarial Attacks & Why Defenses Fail

## 4.1 The Geometry of an Evasion Attack
In high-dimensional space, an AI model draws a multi-dimensional border called a **decision boundary** separating Benign from Attack traffic.

```
       ATTACK REGION                           BENIGN REGION
             ● (Attack Sample x)
              \
               \  Direction of Loss Gradient (∇_x L)
                ▼ 
                 ●────────────────────────────│──────────────● (Misclassified!)
                x + δ_small                   │            x_adv = x + δ_optimal
                                       DECISION BOUNDARY
```

1. The attacker stands at point $x$ (inside the Attack territory).
2. They calculate the gradient of the loss function $\nabla_x \mathcal{L}(f(x), y)$, which points directly toward the nearest exit door to the Benign region.
3. By adding a tiny, stealthy vector $\delta$ with magnitude $\|\delta\|_\infty \le 0.05$, the attacker nudges the point just across the decision boundary.
4. The server receives the attack, but the AI security alarm stays completely silent!

---

## 4.2 Why Prior Defenses Failed

### Failure 1: The "Clean Importance" Fallacy
* **What prior papers did:** They calculated feature importance (e.g., using Mutual Information or standard SHAP) only on clean, unattacked traffic, selecting the top 15 features.
* **Why it failed:** Features with high clean importance often have the steepest mathematical slopes. An attacker needs to nudge these features by only a fraction of a percent to cause a massive swing in the AI's internal neurons. Under attack, the perceived importance of these features collapses, blinding the model.

### Failure 2: Perturbation Staleness in Static Retraining
* **What prior papers did (e.g., Holla et al., 2025):** They generated a batch of adversarial examples on Monday, saved them to a hard drive, and trained the AI on those saved examples all week.
* **Why it failed:** As an AI learns over 50 epochs, its internal weights update millions of times. Its decision boundary moves! The pre-computed attacks generated on Monday fall far behind the moving boundary and become harmless. The AI memorizes those fixed old samples, but when an attacker launches a fresh attack on Friday, the AI fails completely (accuracy drops to $79.70\%$).

---

# 5. System Architecture Flowchart

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PHASE2NET COMPLETE 7-STAGE PIPELINE                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘

 ┌──────────────────────────────────────────────────┐
 │ STAGE 1: RAW DATASET & PREPROCESSING             │
 │ • Ingest CSE-CIC-IDS2018 (8.28M raw records)     │
 │ • Clean NaN, Inf, duplicates & drop 6 metadata ID│ ───> Valid Clean Pool: 6,320,003 flows
 │ • Stratified 80/20 Partition                     │      ├── 1,264,001 Frozen Test (Isolated!)
 │ • Fit OneHotEncoder & StandardScaler on Core     │      └── 4,550,401 Core Training Set
 └─────────────────────────┬────────────────────────┘
                           │ (Transforms into 69 Continuous Dimensions)
                           ▼
 ┌──────────────────────────────────────────────────┐
 │ STAGE 2: COARSE MUTUAL INFORMATION FILTERING     │
 │ • Sample 100,000 flows from Core Train           │
 │ • Calculate Mutual Information I(X; Y)           │ ───> Dimension Reduction: 69 ──> 40 Features
 └─────────────────────────┬────────────────────────┘
                           │ (40 Candidate Features)
                           ▼
 ┌──────────────────────────────────────────────────┐
 │ STAGE 3: RESILIENT CLASS BALANCING VIA SMOTE     │
 │ • 4:1 Imbalance: 3.60M Benign vs 0.95M Attack    │
 │ • Synthesize 2.64M realistic minority attacks    │ ───> Balanced Core Pool: 7,191,590 flows
 │ • Validation & Test partitions strictly UNTOUCHED│      (Exact 1:1 ratio: 3.595M per class)
 └─────────────────────────┬────────────────────────┘
                           │ (Balanced 40-Dimensional Training Pool)
                           ▼
 ┌──────────────────────────────────────────────────┐
 │ STAGE 4: ADVERSARIAL STABILITY SHAP (NOVELTY 1)  │
 │ • Train 40-dim calibration MLP for 20 epochs     │
 │ • Extract SHAP attributions: Clean (φ_clean)     │
 │ • Perturb same 500 flows with PGD: Attacked (φ_adv)│
 │ • Compute Stability Score:                       │
 │     S_j = 1 - |φ_clean - φ_adv| / (φ_clean + φ_adv)│ ───> Prunes 13 fragile, volatile features
 │ • Select 80% cumulative stability mass cutoff    │      Isolates 27 Ultra-Robust Features!
 └─────────────────────────┬────────────────────────┘
                           │ (27 Robust Features Isolated)
                           ▼
 ┌──────────────────────────────────────────────────┐
 │ STAGE 5: TARGET NEURAL NETWORK ARCHITECTURE      │
 │ • Fresh Target MLP initialized (Zero prior weights)
 │ • 27 ──> Dense(128) ──> Dense(64) ──> Dense(32)   │ ───> Fully connected architecture with
 │ • Output Projection: Dense(32 ──> 2 Logits)      │      BatchNorm1d + ReLU + 30% Dropout
 └─────────────────────────┬────────────────────────┘
                           │ (Fresh Neural Network Weights θ)
                           ▼
 ┌──────────────────────────────────────────────────┐
 │ STAGE 6: TWO-PHASE DYNAMIC ONLINE PGD (NOVELTY 2)│
 │ • Phase 1 (Epochs 1-10): Clean Pretraining       │
 │ • Phase 2 (Epochs 11-50): Dynamic GPU PGD Loop   │ ───> Zero perturbation staleness!
 │     └── For EVERY batch: Generate fresh 5-step   │      L_total = 0.5 · L_clean + 0.5 · L_adv
 │         PGD using current weights θ_t            │
 └─────────────────────────┬────────────────────────┘
                           │ (Hardened, Robust Production Classifier)
                           ▼
 ┌──────────────────────────────────────────────────┐
 │ STAGE 7: COMPREHENSIVE MULTI-THREAT EVALUATION   │
 │ • 1,264,001 Frozen Test Flows (3 Seeds: 42,123,2024
 │ • White-Box: FGSM, PGD-100, BIM, MIM, APGD, CW   │ ───> 96.19% Clean Accuracy (+3.37 pp gain)
 │ • Black-Box: Score-based Square Attack (100 iter)│      90.13% PGD-100 Robustness (+10.43 pp gain)
 │ • Transfer: WiderNet surrogate transfer attack   │      < 0.02 ms/flow real-time inference speed
 └──────────────────────────────────────────────────┘
```

---

# 6. Stage 1: Raw Dataset Ingestion, Cleaning & Zero-Leakage Splitting

## 6.1 Data Cleaning Execution
The source dataset contains **8,284,871 raw flows** across 10 CSV files. We execute a 4-step sanitization protocol:

1. **Identifier Elimination:** Dropped `Source IP`, `Destination IP`, `Flow ID`, `Source Port`, `Destination Port`, and `Timestamp`.
   * *Why?* A neural network that memorizes that `IP 192.168.10.50` is an attacker will fail when the attacker changes their IP address tomorrow.
2. **Purging Corrupt Records:** Removed records containing `NaN`, `+Inf`, and `-Inf`.
3. **Removing Dead Dimensions:** Dropped zero-variance features where all 8 million rows contained the exact same constant value.
4. **Deduplication:** Dropped duplicate flow rows generated by sensor logging glitches.

**Post-Cleaning Result:** **6,320,003 valid flows** ($4,994,159$ Benign [$79.02\%$] and $1,325,844$ Attack [$20.98\%$]).

---

## 6.2 Zero-Leakage Stratified Splitting

```
Total Valid Records: 6,320,003
 ├── Frozen Test Partition (20%): 1,264,001 flows
 │    └── Locked away in cold isolation. Zero scalers or models touch this data!
 └── Training Pool (80%): 5,056,002 flows
      ├── Core Training Set (90% of pool): 4,550,401 flows (Fit all scalers & models)
      └── Validation Set (10% of pool):    505,601 flows (Epoch checkpoint monitoring)
```

---

## 6.3 Feature Normalization: The Mathematical Details
We apply **StandardScaler Normalization**:
$$z = \frac{x - \mu}{\sigma}$$

* $\mu$ (Mean): The mathematical average across all flows in Core Train.
* $\sigma$ (Standard Deviation): The spread or dispersion of the data.

### 🔢 Concrete Numerical Walkthrough:
Consider feature `Flow Duration`:
* Suppose across the 4.55 million Core Train flows, the average duration is $\mu = 5.0\text{ seconds}$, with a standard deviation $\sigma = 2.0\text{ seconds}$.

1. **Flow A** arrives with duration $x = 9.0\text{ seconds}$:
   $$z = \frac{9.0 - 5.0}{2.0} = \frac{4.0}{2.0} = \mathbf{+2.0}$$
   *(Interpretation: "This flow lasted 2 standard deviations longer than normal.")*

2. **Flow B** arrives with duration $x = 1.0\text{ second}$:
   $$z = \frac{1.0 - 5.0}{2.0} = \frac{-4.0}{2.0} = \mathbf{-2.0}$$
   *(Interpretation: "This flow lasted 2 standard deviations shorter than normal.")*

* **Output:** All 69 numeric features now share the exact same scale, centered around $0.0$.

---

# 7. Stage 2: Candidate Feature Filtering via Mutual Information (MI)

## 7.1 Mathematical Foundation
**Mutual Information (MI)** measures the reduction in uncertainty regarding the attack status $Y$ after observing feature $X$:

$$I(X; Y) = \sum_{y \in \{0, 1\}} \int_{-\infty}^{+\infty} p(x, y) \log_2 \left( \frac{p(x, y)}{p(x) \, p(y)} \right) dx$$

### 💡 Non-CS Breakdown of the Math:
* $p(x, y)$: How often does feature value $x$ appear together with label $y$?
* $p(x) \, p(y)$: How often would they appear together if they were completely independent random events?
* If knowing feature $x$ gives zero clues about whether an attack is happening, $\frac{p(x,y)}{p(x)p(y)} = 1$. Because $\log_2(1) = 0$, $I(X; Y) = 0$.
* If knowing feature $x$ immediately reveals whether an attack is happening, $I(X; Y)$ is very large.

---

## 7.2 🔢 Concrete Numerical Walkthrough
Suppose we test two features on 10,000 flows:

```
FEATURE 1: "SYN Flag Count"                    FEATURE 2: "TCP Checksum Value"
┌──────────────┬───────────────┬─────────────┐ ┌──────────────┬───────────────┬─────────────┐
│ Category     │ Attack Flows  │ Benign Flows│ │ Category     │ Attack Flows  │ Benign Flows│
├──────────────┼───────────────┼─────────────┤ ├──────────────┼───────────────┼─────────────┤
│ Value = High │ 4,900 flows   │ 100 flows   │ │ Value = High │ 2,500 flows   │ 2,500 flows │
│ Value = Low  │ 100 flows     │ 4,900 flows │ │ Value = Low  │ 2,500 flows   │ 2,500 flows │
└──────────────┴───────────────┴─────────────┘ └──────────────┴───────────────┴─────────────┘
  Prediction Confidence: 98.0%!                  Prediction Confidence: Exactly 50% (A Coin Flip!)
  Mutual Information Score: I(X;Y) ≈ 0.85 bits    Mutual Information Score: I(X;Y) = 0.00 bits
```

* **Outcome:** We rank all 69 features by $I(X; Y)$ and keep only the **top 40 candidate features** ($69 \longrightarrow 40$).

---

# 8. Stage 3: Resilient Class Balancing via SMOTE

## 8.1 The Core Imbalance Problem
In the Core Training Set:
* **Benign flows:** 3,595,795 ($79.02\%$)
* **Attack flows:** 954,606 ($20.98\%$)

If trained directly on this unbalanced distribution, the model becomes biased toward assuming all flows are Benign.

---

## 8.2 SMOTE Formula & Geometric Walkthrough
Instead of simply copying existing attack samples (which leads to memorization and overfitting), **SMOTE (Synthetic Minority Over-sampling Technique)** synthesizes brand-new, realistic attack samples by drawing line segments between neighboring attack samples in 40-dimensional space:

$$x_{\text{new}} = x_i + \lambda \cdot (x_{zi} - x_i), \quad \text{where } \lambda \sim \text{Uniform}(0, 1)$$

---

## 8.3 🔢 Concrete Numerical Walkthrough
Let's examine two real attack samples across two normalized features: `[Packet Rate, Flow Duration]`:
* Attack Sample 1 ($x_i$): $[+1.20, \, -0.40]$
* Attack Sample 2 ($x_{zi}$): $[+1.80, \, +0.20]$

1. Compute the vector difference between the two attacks:
   $$x_{zi} - x_i = [1.80 - 1.20, \, 0.20 - (-0.40)] = [+0.60, \, +0.60]$$
2. The computer draws a random decimal $\lambda$ between $0.0$ and $1.0$. Let's say $\lambda = 0.50$:
   $$\lambda \cdot (x_{zi} - x_i) = 0.50 \cdot [+0.60, \, +0.60] = [+0.30, \, +0.30]$$
3. Add this vector to $x_i$ to produce the new synthetic attack flow:
   $$x_{\text{new}} = [+1.20, \, -0.40] + [+0.30, \, +0.30] = \mathbf{[+1.50, \, -0.10]}$$

* **Execution Outcome:** SMOTE balances the Core Training Set to **7,191,590 flows** (exactly 3,595,795 Benign and 3,595,795 Attack flows, a 1:1 ratio).
* **Zero Leakage Rule:** Validation and Test partitions are **never** oversampled, ensuring evaluation occurs strictly on real-world distributions.

---

# 9. Stage 4: Adversarial Stability SHAP Feature Selection (Core Novelty 1)

## 9.1 The Fragility of Clean Feature Attributions
Standard feature selection calculates SHAP values only on clean data.  
* **Our Discovery:** Features with the highest clean predictive power often exhibit steep loss gradients. When an adversary adds a small perturbation ($\epsilon = 0.05$), the feature's attribution collapses or reverses sign. The model relies heavily on a feature that has been neutralized!

---

## 9.2 The Adversarial Stability Score Formula ($S_j$)
Phase2Net evaluates features in both their **Clean state** ($\bar{\phi}_j^{\text{clean}}$) and their **20-step PGD Perturbed state** ($\bar{\phi}_j^{\text{adv}}$):

$$\boxed{S_j = 1 - \frac{\left| \bar{\phi}_j^{\text{clean}} - \bar{\phi}_j^{\text{adv}} \right|}{\max\left(\bar{\phi}_j^{\text{clean}} + \bar{\phi}_j^{\text{adv}}, \, 10^{-10}\right)}}$$

### Term-by-Term Anatomical Breakdown:
1. $\left| \bar{\phi}_j^{\text{clean}} - \bar{\phi}_j^{\text{adv}} \right|$: **Absolute Drift.** How much did the feature's importance change when attacked?
2. $\bar{\phi}_j^{\text{clean}} + \bar{\phi}_j^{\text{adv}}$: **Magnitude Normalizer.** Ensures a change of $0.05$ on a small feature is treated appropriately relative to a change of $0.05$ on a massive feature.
3. $10^{-10}$: **Epsilon Stabilizer.** Prevents division by zero if an inactive feature has zero attribution in both states.
4. $1 - (\dots)$: **Score Inversion.** Converts the relative instability into a clean score from $0.0$ to $1.0$:
   * $S_j \approx 1.0$: **Ultra-Robust Feature** (Immune to adversarial perturbation).
   * $S_j \approx 0.0$: **Extremely Fragile Feature** (Collapses under perturbation).

---

## 9.3 🔢 Concrete Numerical Walkthrough: Comparing Two Features

```
 FEATURE A: "Bwd Packet Length Std"              FEATURE B: "Fwd Header Length"
 (Selected by Phase2Net as Robust)               (Pruned by Phase2Net as Fragile)
 ─────────────────────────────────────────────   ─────────────────────────────────────────────
 Clean Attribution:    φ̄_clean = 0.450           Clean Attribution:    φ̄_clean = 0.700 (High!)
 Attacked Attribution: φ̄_adv   = 0.435           Attacked Attribution: φ̄_adv   = 0.050 (Collapsed!)
 
 1. Absolute Drift:                              1. Absolute Drift:
    |0.450 - 0.435| = 0.015                         |0.700 - 0.050| = 0.650
 
 2. Denominator:                                 2. Denominator:
    0.450 + 0.435 = 0.885                           0.700 + 0.050 = 0.750
 
 3. Instability Ratio:                           3. Instability Ratio:
    0.015 / 0.885 ≈ 0.0169                          0.650 / 0.750 ≈ 0.8667
 
 4. Stability Score:                             4. Stability Score:
    S_A = 1 - 0.0169 = 0.9831 (98.3% STABLE!)       S_B = 1 - 0.8667 = 0.1333 (13.3% - FRAGILE!)
 
 VERDICT: ✅ RETAINED IN PHASE2NET               VERDICT: ❌ PRUNED & DISCARDED
```

---

## 9.4 The 80% Cumulative Mass Selection Rule
1. Rank all 40 candidate features in descending order of $S_j$: $S_{(1)} \ge S_{(2)} \ge \dots \ge S_{(40)}$.
2. Calculate the cumulative stability sum: $S_{\text{total}} = \sum_{k=1}^{40} S_k$.
3. Pick the top $m$ features that account for $80\%$ of the total stability mass:
   $$\sum_{j=1}^{m} S_{(j)} \ge 0.80 \cdot S_{\text{total}}$$
4. **Outcome:** Exactly **27 features** are selected ($40 \longrightarrow 27$), pruning the 13 most volatile, gradient-sensitive features.

---

# 10. Stage 5: Target Neural Network Architecture & Internal Mechanics

Once the 27 robust features are isolated, the final Phase2Net classifier is initialized from scratch with **zero prior weights**.

```
                        Input Vector: x ∈ ℝ²⁷ (27 Robust Features)
                                       │
                                       ▼
       ┌───────────────────────────────────────────────────────────────┐
       │ DENSE HIDDEN BLOCK 1                                          │
       │ • Linear Projection:      27 Inputs ──> 128 Neurons           │
       │ • Batch Normalization:    BatchNorm1d(128)                    │
       │ • Non-Linear Activation:  ReLU (Rectified Linear Unit)        │
       │ • Regularization:         Dropout (p = 0.30)                  │
       └───────────────────────────────┬───────────────────────────────┘
                                       │ Tensor Dimensions: [Batch, 128]
                                       ▼
       ┌───────────────────────────────────────────────────────────────┐
       │ DENSE HIDDEN BLOCK 2                                          │
       │ • Linear Projection:      128 Neurons ──> 64 Neurons          │
       │ • Batch Normalization:    BatchNorm1d(64)                     │
       │ • Non-Linear Activation:  ReLU                                │
       │ • Regularization:         Dropout (p = 0.30)                  │
       └───────────────────────────────┬───────────────────────────────┘
                                       │ Tensor Dimensions: [Batch, 64]
                                       ▼
       ┌───────────────────────────────────────────────────────────────┐
       │ DENSE HIDDEN BLOCK 3                                          │
       │ • Linear Projection:      64 Neurons ──> 32 Neurons           │
       │ • Batch Normalization:    BatchNorm1d(32)                     │
       │ • Non-Linear Activation:  ReLU                                │
       │ • Regularization:         Dropout (p = 0.30)                  │
       └───────────────────────────────┬───────────────────────────────┘
                                       │ Tensor Dimensions: [Batch, 32]
                                       ▼
       ┌───────────────────────────────────────────────────────────────┐
       │ OUTPUT CLASSIFICATION HEAD                                    │
       │ • Linear Projection:      32 Neurons ──> 2 Output Logits [z0,z1│
       │ • Softmax Function:       P(Benign), P(Attack)                │
       │ • Decision Rule:          Class = argmax(Softmax(z))          │
       └───────────────────────────────────────────────────────────────┘
```

---

## 10.1 Mathematical Mechanics of Each Layer

### 1. Linear Transformation ($z = Wx + b$)
Multiplies the 27 inputs by a weight matrix $W$ of size $128 \times 27$ and adds 128 bias terms. This projects the flow into a 128-dimensional representation.

### 2. Batch Normalization (`BatchNorm1d`)
Normalizes the layer's inputs across the 2,048 flows in the batch:
$$\hat{x} = \frac{x - \mu_{\text{batch}}}{\sqrt{\sigma_{\text{batch}}^2 + \epsilon_{\text{BN}}}}, \quad y = \gamma \hat{x} + \beta$$
* Stabilizes internal layer dynamics when active adversarial perturbations are introduced during training.

### 3. ReLU Activation Function
$$\text{ReLU}(z) = \max(0, z)$$
* Zeroes out negative activations, introducing non-linear decision boundaries.

### 4. Dropout ($p = 0.30$)
During training, each of the 128 neurons has a $30\%$ probability of being temporarily deactivated. This prevents neurons from co-adapting and forces the network to learn redundant representations.

### 5. Softmax Classification Output
Converts the final two raw numbers (logits $z_0$ and $z_1$) into clean probabilities:
$$P(\text{Attack}) = \frac{e^{z_1}}{e^{z_0} + e^{z_1}}$$

---

# 11. Stage 6: Two-Phase Dynamic Online Adversarial Training (Core Novelty 2)

## 11.1 The Min-Max Formulation
Phase2Net formulates robust training as a game between the classifier's weights $\theta$ and an active adversary:

$$\min_{\theta} \mathbb{E}_{(x, y) \sim \mathcal{D}} \left[ \frac{1}{2} \mathcal{L}_{\text{CE}}(f_\theta(x), y) + \frac{1}{2} \max_{\|\delta\|_\infty \le \epsilon, \, x+\delta \in [l, u]} \mathcal{L}_{\text{CE}}(f_\theta(x + \delta), y) \right]$$

* **$\frac{1}{2} \mathcal{L}_{\text{CE}}(f_\theta(x), y)$:** Ensures the model stays highly accurate on normal clean traffic.
* **$\frac{1}{2} \max \mathcal{L}_{\text{CE}}(f_\theta(x + \delta), y)$:** Forces the model to withstand worst-case perturbations.

---

## 11.2 The Two Training Phases

```
TOTAL TRAINING: 50 EPOCHS (Mini-Batch Size = 2,048)
 ├── PHASE 1: Clean Pretraining (Epochs 1 to 10)
 │    └── Trains on clean balanced data.
 │        Purpose: Allows the model to find a stable initial decision boundary.
 │
 └── PHASE 2: Dynamic Online PGD Regularization (Epochs 11 to 50)
      └── For EVERY mini-batch (X_b, Y_b) on GPU:
           ├── Step 1: Initialize random noise: δ_0 ~ Uniform(-ε, +ε)
           ├── Step 2: Perform 5 steps of PGD gradient ascent:
           │           X_{t+1} = Clip( X_t + α · sign(∇_X L(f_θ(X_t), Y)) )
           ├── Step 3: Compute clean loss L_clean and adversarial loss L_adv
           └── Step 4: Backpropagate on L_total = 0.5 · L_clean + 0.5 · L_adv
```

---

## 11.3 🔢 Concrete Step-by-Step PGD Numerical Walkthrough
Let's follow a single feature value through an online PGD update:
* Normalized clean feature: $x = +0.800$
* Allowable noise budget: $\epsilon = 0.050$  
  *(The feature MUST stay within $[0.800 - 0.050, 0.800 + 0.050] = [+0.750, +0.850]$)*
* Attack step size: $\alpha = 0.010$

1. **Step 0 (Random Start):**
   Random noise $\delta_0 = +0.015$ is added:
   $$x^0 = 0.800 + 0.015 = \mathbf{0.815}$$
2. **Step 1 (Gradient Ascent):**
   The GPU computes the gradient: $\nabla_{x^0} \mathcal{L} = +0.512$ (positive slope).  
   Because the slope is positive, $\text{sign}(+0.512) = +1$:
   $$x^1 = x^0 + \alpha \cdot (+1) = 0.815 + 0.010 \cdot 1 = \mathbf{0.825}$$
3. **Step 2 (Gradient Ascent):**
   Suppose the gradient is still positive:
   $$x^2 = 0.825 + 0.010 \cdot 1 = \mathbf{0.835}$$
4. **Steps 3, 4, 5 (Reaching the Ceiling):**
   By step 5, suppose $x^{\text{raw}}$ attempts to reach $+0.865$.  
   The projection operator $\Pi$ clamps it to the maximum ceiling: $\min(0.865, +0.850) = \mathbf{+0.850}$.

* **Outcome:** The neural network is trained against real-time perturbations tailored to its exact current weights, eliminating perturbation staleness.

---

# 12. Stage 7: Multi-Threat Evaluation Suite & The 9 Attack Formulations

To ensure rigorous validation, Phase2Net is tested against **9 distinct attack formulations**:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   THE 9 EVALUATED ATTACK METHODS                                 │
├───────────────────────────────┬──────────────────┬───────────────────────────────────────────────┤
│ Attack Algorithm              │ Threat Category  │ Key Mathematical Optimization Trait           │
├───────────────────────────────┼──────────────────┼───────────────────────────────────────────────┤
│ 1. FGSM                       │ White-Box        │ 1-step fast sign gradient: x + ε · sign(∇L)   │
│ 2. PGD-100                    │ White-Box        │ 100-step iterative ascent with random restart │
│ 3. BIM (I-FGSM)               │ Unseen White-Box │ Multi-step iterative ascent without restart   │
│ 4. MIM (MI-FGSM)              │ Unseen White-Box │ Momentum memory vector (μ = 1.0)              │
│ 5. APGD-CE                    │ Unseen White-Box │ Adaptive step-size halving decay schedule     │
│ 6. CW-L∞                      │ Unseen White-Box │ Logit-margin loss targeting classification gap│
│ 7. Square Attack              │ Black-Box        │ Score-based random coordinate block search    │
│ 8. Transfer PGD (WiderNet)    │ Black-Box        │ Cross-model evasion from surrogate MLP        │
│ 9. DeepFool                   │ Diagnostic       │ Unconstrained minimum boundary distance       │
└───────────────────────────────┴──────────────────┴───────────────────────────────────────────────┘
```

### Key Mathematical Formulations:
* **FGSM:** $x_{\text{adv}} = x + \epsilon \cdot \text{sign}\left(\nabla_x \mathcal{L}(f_\theta(x), y)\right)$
* **PGD-100:** $x^{t+1} = \Pi_{x + \mathcal{B}_\epsilon} \left( x^t + \alpha \cdot \text{sign}\left(\nabla_{x^t} \mathcal{L}(f_\theta(x^t), y)\right) \right)$
* **MIM:** $g_{t+1} = \mu \cdot g_t + \frac{\nabla \mathcal{L}}{\|\nabla \mathcal{L}\|_1}, \quad x^{t+1} = \Pi \left( x^t + \alpha \cdot \text{sign}(g_{t+1}) \right)$
* **CW-$L_\infty$:** $\mathcal{L}_{\text{CW}} = \max\left( z_y(x) - \max_{i \ne y} z_i(x), \, -\kappa \right)$
* **DeepFool:** $r_t = - \frac{f(x_t)}{\|\nabla f(x_t)\|_2^2} \nabla f(x_t)$

---

# 13. Evaluation Metrics & Step-by-Step Arithmetic Walkthroughs

Every test flow falls into one of four categories:
* **$\text{TP}$ (True Positive):** An actual cyberattack is correctly caught.
* **$\text{TN}$ (True Negative):** Normal traffic is correctly allowed through.
* **$\text{FP}$ (False Positive):** Normal traffic is mistakenly flagged as an attack (False Alarm).
* **$\text{FN}$ (False Negative):** A cyberattack slips past the model (Evasion).

---

## 13.1 🔢 Concrete Numerical Walkthrough of All Metrics
Suppose we evaluate **10,000 test flows** containing **8,000 Benign** and **2,000 Attack** flows:
* $\text{TP} = 1,900$
* $\text{FN} = 100$
* $\text{TN} = 7,920$
* $\text{FP} = 80$

### 1. Accuracy (Overall Correctness):
$$\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{Total}} = \frac{1,900 + 7,920}{10,000} = \frac{9,820}{10,000} = \mathbf{98.20\%}$$

### 2. Balanced Accuracy (Fair Unweighted Accuracy):
$$\text{Balanced Acc} = \frac{1}{2} \left( \frac{\text{TP}}{\text{TP} + \text{FN}} + \frac{\text{TN}}{\text{TN} + \text{FP}} \right) = \frac{1}{2} \left( \frac{1,900}{2,000} + \frac{7,920}{8,000} \right) = \frac{0.9500 + 0.9900}{2} = \mathbf{97.00\%}$$

### 3. Precision (Alert Reliability):
$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}} = \frac{1,900}{1,900 + 80} = \frac{1,900}{1,980} = \mathbf{0.9596 \quad (95.96\%)}$$

### 4. Recall / True Positive Rate (Detection Coverage):
$$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}} = \frac{1,900}{1,900 + 100} = \frac{1,900}{2,000} = \mathbf{0.9500 \quad (95.00\%)}$$

### 5. F1-Score (Harmonic Balance of Precision & Recall):
$$\text{F1} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}} = 2 \cdot \frac{0.9596 \cdot 0.9500}{0.9596 + 0.9500} = \frac{1.8232}{1.9096} = \mathbf{0.9548}$$

### 6. Matthews Correlation Coefficient (MCC):
The gold standard for imbalanced data (ranges from $-1.0$ [total disagreement] to $+1.0$ [perfect prediction]):
$$\text{Numerator} = (1,900 \cdot 7,920) - (80 \cdot 100) = 15,048,000 - 8,000 = 15,040,000$$
$$\text{Denominator} = \sqrt{(1,980)(2,000)(8,000)(7,940)} = \sqrt{2.515008 \times 10^{14}} \approx 15,858,777$$
$$\text{MCC} = \frac{15,040,000}{15,858,777} = \mathbf{+0.9484} \quad (\text{Outstanding correlation!})$$

### 7. Attack Success Rate (ASR — The Attacker's Metric):
$$\text{ASR} = \frac{\text{Successful Evasions (FN)}}{\text{Total Attempted Attacks}} = \frac{100}{2,000} = \mathbf{0.0500 \quad (5.0\% \text{ Attack Success Rate})}$$

---

# 14. Complete Experimental Results Across 3 Random Seeds

All evaluations were executed on the **1,264,001 frozen test flows** across three independent random seeds (**42, 123, 2024**). Results are reported as $\text{Mean} \pm \text{Standard Deviation}$.

---

## 14.1 Clean Traffic Performance (Normal Day-to-Day Network Traffic)

| Model Configuration | Accuracy (%) | Weighted F1 | MCC | Balanced Acc (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Undefended Baseline** | $92.82\% \pm 0.07\%$ | $0.9303 \pm 0.0006$ | $0.8020 \pm 0.0013$ | $92.56\% \pm 0.03\%$ |
| **Static Defense (Holla et al., 2025)** | $93.97\% \pm 1.09\%$ | $0.9403 \pm 0.0092$ | $0.8257 \pm 0.0219$ | $91.81\% \pm 2.09\%$ |
| **Phase2Net (Proposed)** | $\mathbf{96.19\% \pm 0.03\%}$ | $\mathbf{0.9620 \pm 0.0003}$ | $\mathbf{0.8859 \pm 0.0007}$ | $\mathbf{94.54\% \pm 0.03\%}$ |
| **Improvement over Baseline** | **+3.37 pp** | **+0.0317** | **+0.0839** | **+1.98 pp** |

> **Key Takeaway:** Most robust defense models suffer from a "robustness tax" (their accuracy on normal traffic drops). Phase2Net **improves clean accuracy by +3.37 percentage points** over the baseline! By filtering out 13 volatile, noisy features, the classifier makes fewer false alarms on benign traffic.

---

## 14.2 Robustness Under Standard Threat Formulation ($\epsilon = 0.05$)

| Threat Model | Baseline Acc (ASR) | Static Defense Acc (ASR) | Phase2Net Acc (ASR) | Phase2Net Gain |
| :--- | :---: | :---: | :---: | :---: |
| **FGSM ($\epsilon=0.05$)** | $84.20\% \pm 3.30\%$ ($8.91\%$) | $84.32\% \pm 3.35\%$ ($9.91\%$) | $\mathbf{92.67\% \pm 1.56\%}$ ($\mathbf{3.62\%}$) | **+8.35 pp** |
| **PGD-100 ($\epsilon=0.05$)** | $73.90\% \pm 2.43\%$ ($20.14\%$) | $79.70\% \pm 5.45\%$ ($15.23\%$) | $\mathbf{90.13\% \pm 1.20\%}$ ($\mathbf{6.05\%}$) | **+10.43 pp** |
| **Square Attack (Black-Box)** | $82.00\% \pm 0.89\%$ ($18.08\%$) | $85.40\% \pm 4.16\%$ ($13.63\%$) | $\mathbf{91.83\% \pm 1.07\%}$ ($\mathbf{5.27\%}$) | **+6.43 pp** |
| **Transfer PGD (WiderNet)** | $79.23\%$ ($18.52\%$) | $86.73\%$ ($8.92\%$) | $\mathbf{94.13\% \pm 1.68\%}$ ($\mathbf{2.08\%}$) | **+7.40 pp** |

> **Key Takeaway:** Under the primary benchmark attack (**100-step PGD**), baseline accuracy collapses to $73.90\%$, and static defense achieves only $79.70\%$. Phase2Net achieves **$90.13\%$ accuracy**, slashing the Attack Success Rate from $20.14\%$ down to **$6.05\%$**!

---

## 14.3 Generalization Across Unseen White-Box Attacks ($\epsilon = 0.05$)
These attacks use completely different mathematical optimization strategies that the model **never experienced during training**:

| Unseen Attack | Mathematical Trait | Phase2Net Accuracy | Phase2Net ASR | Baseline Acc (ASR) |
| :--- | :--- | :---: | :---: | :---: |
| **BIM (I-FGSM)** | Multi-step sign gradient | $\mathbf{91.37\% \pm 0.43\%}$ | $\mathbf{4.76\% \pm 0.25\%}$ | $75.60\%$ ($18.15\%$) |
| **MIM (MI-FGSM)** | Momentum velocity vector | $\mathbf{91.05\% \pm 1.85\%}$ | $\mathbf{5.09\% \pm 1.77\%}$ | $77.43\%$ ($16.14\%$) |
| **APGD-CE** | Adaptive step-size decay | $\mathbf{88.55\% \pm 1.95\%}$ | $\mathbf{7.70\% \pm 1.88\%}$ | $71.33\%$ ($22.78\%$) |
| **CW-$L_\infty$** | Targeted logit-margin loss | $\mathbf{90.15\% \pm 1.21\%}$ | $\mathbf{6.03\% \pm 1.03\%}$ | $73.98\%$ ($20.05\%$) |

> **Key Takeaway:** Phase2Net retains between **$88.55\%$ and $91.37\%$ accuracy** across all unseen attacks. This proves the model has not simply memorized 5-step PGD; it has learned a genuinely robust geometric decision boundary!

---

# 15. Diagnostic Sweeps & Rigorous Scientific Proof Against Gradient Masking

## 15.1 What is Gradient Masking?
In 2018, machine learning researchers (Athalye et al., ICML) exposed that many proposed adversarial defenses were scientifically flawed. The models were not actually robust; they had simply created jagged or flat loss landscapes where gradients became zero ("obfuscated gradients"). When tested with gradient-free or adaptive attacks, their defenses collapsed.

To prove that Phase2Net provides **genuine empirical robustness**, we performed three diagnostic tests:

---

## 15.2 Test 1: Perturbation Budget ($\epsilon$) Sweep
* If a defense relies on masking, accuracy typically remains unchanged until a sudden cliff occurs.
* In Phase2Net, accuracy degrades smoothly and monotonically as the attack budget expands:
  * $\epsilon = 0.01$: **$94.47\%$** accuracy
  * $\epsilon = 0.03$: **$93.35\%$** accuracy
  * $\epsilon = 0.05$: **$90.13\%$** accuracy *(Standard operational budget)*
  * $\epsilon = 0.10$: **$75.25\%$** accuracy

```
 Accuracy (%)
  100% ──┐
   95%   └──● (94.47% at ε=0.01)
   90%      └───● (93.35% at ε=0.03)
   85%          └────● (90.13% at ε=0.05)
   80%               │
   75%               └────────● (75.25% at ε=0.10)
    0% ─────────────────────────────────────────
         ε=0.01   ε=0.03   ε=0.05   ε=0.10
        (Smooth, monotonic degradation proves genuine defense!)
```

---

## 15.3 Test 2: PGD Iteration Step Sweep
* If a defense relies on masking, increasing the number of attack iterations allows the optimizer to break through.
* In Phase2Net, attack effectiveness plateaus cleanly:
  * $k = 20$ steps: **$91.40\%$**
  * $k = 50$ steps: **$90.45\%$**
  * $k = 100$ steps: **$90.13\%$**
  * $k = 200$ steps: **$90.10\%$**
* Increasing attack effort tenfold ($20 \to 200$ steps) only decreases accuracy by **$1.30\%$**, proving the attack has reached full convergence.

---

## 15.4 Test 3: DeepFool Unconstrained Boundary Distance
DeepFool removes all $\epsilon$ constraints and measures the exact mathematical distance to the decision boundary:
* **Mean $L_\infty$ distance to flip prediction:** **$2.3238 \pm 0.8727$**  
  *(This is **$46.5\times$ larger** than the attacker's operational budget $\epsilon = 0.05$!)*
* **Median $L_\infty$ distance:** **$1.0064 \pm 0.1483$** ($20.1\times$ larger than $\epsilon = 0.05$).
* **Percentage of samples exceeding $\epsilon = 0.05$:** **$97.33\% \pm 1.42\%$**
* **Conclusion:** Over $97\%$ of flows are physically so far from the decision boundary that an attacker cannot cause evasion within the allowable noise budget!

---

# 16. Computational Hardware Budget, Execution Times & Real-Time Latency

## 16.1 Hardware Specifications
All training and evaluations were executed locally on a single consumer-grade desktop PC:
* **GPU:** AMD Radeon RX 7600 (8 GB GDDR6 VRAM)
* **Compute Platform:** PyTorch using native AMD ROCm 7.2.1
* **System RAM:** 32 GB DDR4
* **Host CPU:** AMD Ryzen 5 processor

---

## 16.2 Training Computational Budget

| Training Phase | Dataset Size | Batch Size | Time per Epoch | Total Phase Duration |
| :--- | :---: | :---: | :---: | :---: |
| **Phase 1: Clean Pretrain (10 Epochs)** | 7.19M flows | 2,048 | $\sim 13$ seconds | $\sim 2.2$ minutes |
| **Phase 2: Dynamic Online PGD (40 Epochs)** | 7.19M flows | 2,048 | $\sim 99$ seconds | $\sim 66.0$ minutes |
| **Total Model Training (Per Seed)** | **50 Epochs** | **2,048** | — | **$\sim 69.3$ minutes (4,160 s)** |
| **Total 3-Seed Replication** | **150 Epochs** | **2,048** | — | **$\sim 3.5$ hours** |

---

## 16.3 Real-Time Operational Latency
* **Amortized Inference Latency:** **$< 0.02$ milliseconds ($20 \, \mu\text{s}$) per flow** on a single consumer GPU.
* **Throughput:** Over **$50,000$ network flows classified per second**.
* **Verdict:** Easily satisfies real-time, line-rate monitoring requirements for high-speed cloud enterprise networks.

---

# 17. Practitioner Guide to Reading the Output CSV & JSON Files

When reviewing the experimental output files in `outputs/v9_final/`, use this reference guide to locate specific metrics:

```
 outputs/v9_final/
  ├── FINAL_RESULTS_MEAN_STD.csv        <── Primary benchmark results across 3 seeds
  ├── UNSEEN_ATTACKS_MEAN_STD.csv       <── Generalization results against unseen attacks
  ├── deepfoolbudget.csv                <── Decision boundary distance percentiles
  ├── epsilon_sweep_summary.csv         <── Accuracy across ε ∈ {0.01, 0.03, 0.05, 0.10}
  ├── pgd_step_sweep_summary.csv        <── Accuracy across steps k ∈ {20, 50, 100, 200}
  ├── training_budget.csv & .json       <── Exact epoch execution times and GPU steps
  └── analytics_ieee/                   <── High-resolution 300 DPI publication plots
       ├── 11_cm_proposed_pgd.png       <── Confusion Matrix plot
       ├── 15_attack_sweeps.png         <── Sensitivity sweep curves
       ├── 16_boundary_diagnostics.png  <── DeepFool boundary distribution
       └── 20_asr_all_models.png        <── Multi-threat ASR bar comparison
```

### 📋 Key Column Definitions in `FINAL_RESULTS_MEAN_STD.csv`:
* `accuracy_mean` / `accuracy_std`: Average accuracy and stability across the 3 seeds.
* `attack_success_rate_mean`: The fraction of previously correct flows that were fooled by the attack (lower is better!).
* `mcc_mean`: Matthews Correlation Coefficient (closer to $+1.0$ is better).
* `mean_Linf_mean`: The average maximum feature change introduced by the attack.

---

# 18. Frequently Asked Questions (FAQ) for General Readers

### Q1: Why not just use traditional firewalls with hardcoded rules?
**Answer:** Traditional firewalls use fixed rules (e.g., "Block port 80 if traffic exceeds 1,000 packets"). Sophisticated attackers bypass these rules by spreading their traffic across hundreds of IP addresses or slowing down their transmission rate. Machine Learning detects subtle, multi-dimensional behavioral patterns that static rules miss entirely.

### Q2: Why can't the attacker just add a massive perturbation ($\epsilon = 1.0$) instead of $\epsilon = 0.05$?
**Answer:** In network communications, packets must adhere to rigid protocol standards. If an attacker alters packet lengths or timing too drastically, the TCP connection breaks, routers drop the packets, or the target application crashes before the exploit payload is delivered. An attack must remain subtle ($\epsilon \le 0.05$) to remain functional and avoid basic anomaly detection.

### Q3: Why does Phase2Net improve clean accuracy while other defenses hurt it?
**Answer:** Traditional adversarial training forces the model to memorize noisy, distorted inputs, which degrades its performance on normal traffic. Phase2Net first filters out the 13 most volatile, noisy features using its Adversarial Stability metric ($S_j$). By training exclusively on the 27 most reliable features, the model makes fewer mistakes on both clean traffic ($96.19\%$) and attacked traffic ($90.13\%$).

---

### 🏁 Final Summary for Non-Technical Stakeholders
1. **The Threat:** Modern cyberattackers can make tiny adjustments to their network packets to sneak past standard AI security scanners.
2. **The Discovery:** Existing AI systems pick fragile features and train on obsolete attack samples.
3. **The Phase2Net Solution:**
   * It measures feature stability under attack and keeps the **27 most resilient features**.
   * It continuously crafts fresh, real-time attacks on the GPU during training, teaching the AI to defend against adaptive attackers.
4. **The Bottom Line:** Phase2Net **increases clean traffic accuracy to 96.19%**, **maintains 90.13% accuracy under severe 100-step PGD attacks**, cuts attack success rates to **6.05%**, and inspects flows in **less than 0.02 milliseconds**, all while running on standard, affordable computer hardware.
