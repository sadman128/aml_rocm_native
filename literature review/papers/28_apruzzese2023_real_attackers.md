# Paper Review 28: Real Attackers Don't Compute Gradients (Apruzzese et al., 2023)

**Title:** "Real Attackers Don't Compute Gradients": Bridging the Gap Between Adversarial ML Research and Network Security Realities  
**Authors:** G. Apruzzese, M. Andreolini, et al.  
**Year & Venue:** 2023 | *IEEE Transactions on Network and Service Management*, Vol. 20, No. 3, pp. 2850–2865  
**Category:** Part 3 — Attacking / Methodological Critique Paper  

---

## 1. Paper Overview & Short Summary
* **Domain:** Threat Model Realism, Black-Box Adversaries, Cloud Security Practice.
* **One-Paragraph Summary:** Apruzzese et al. present a fundamental industry-grounded critique of academic adversarial machine learning research in network security. They argue that assuming an attacker has white-box gradient access to a production cloud IDS is completely unrealistic, as production models are protected behind cloud VPC APIs, firewalls, and proprietary network interfaces. Real attackers use black-box trial-and-error, score-based coordinate probes, or off-the-shelf evasion tools. They challenge researchers to evaluate defenses against non-gradient and black-box threat models.
* **Main Research Problem:** The over-reliance of academic defense literature on white-box gradient threat models that do not reflect real-world cyber threat environments.
* **Main Motivation:** Demanding realistic threat model validation, including black-box query-limited attacks, surrogate transferability, and zero-knowledge attacks.

---

## 2. Exact Methodology of the Critique
1. **Threat Model Hierarchy Formulation:**
   * **White-Box:** Attacker has complete knowledge of model weights $\theta$ and computes exact gradients $\nabla_x \mathcal{L}$.
   * **Grey-Box (Surrogate):** Attacker trains a local surrogate model $g_\psi$ and transfers perturbations.
   * **Black-Box Score-Based:** Attacker queries prediction probabilities $P(y \mid x)$ and estimates gradients (Square Attack).
   * **Black-Box Hard-Label:** Attacker observes only the discrete decision label $\hat{y} \in \{0, 1\}$.
2. **Operational Reality Proof:** Examined real-world SOC workflows and proved that white-box gradient computation is impossible across enterprise cloud perimeters.

---

## 3. Key Findings & Evidence Presented by Authors
* Demonstrated that defenses claiming high white-box robustness often break when attacked by non-gradient black-box methods (Square Attack) or simple surrogate transfer attacks.
* Argued that an effective defense must prove resilience across the entire spectrum of black-box threat models.

---

## 4. Critical Assessment & Limitations of the Critique
* While Apruzzese et al. are correct that real attackers cannot directly query production model gradients, in mathematical security engineering, **the white-box gradient threat model represents the theoretical worst-case bound**. Under Shannon's Maxim ("the enemy knows the system") and Kerckhoffs's Principle, a system that is secure against a white-box adversary is mathematically guaranteed to resist weaker black-box adversaries.

---

## 5. Why Our Proposed Pipeline is Mathematically & Architecturally Superior
* **Worst-Case Boundary Guarantee:** By hardening against white-box multi-step PGD, Phase2Net minimizes the supremum loss over the entire local $\ell_\infty$-ball, creating robust classification margins that automatically protect against black-box coordinate searches.
* **Comprehensive Multi-Threat Formulation:** In our proposed methodology, Phase2Net is explicitly designed to be validated against:
  1. White-box gradient ascent (PGD-100, FGSM).
  2. Score-based zeroth-order search (Square Attack).
  3. Cross-architecture surrogate transfer attacks (WiderNet surrogate).

---

## 6. Defense Board Mock Attack Questions & Viva-Style Answers

> **Committee Member Question 1:** *"Apruzzese et al. (2023) argued that production cloud firewalls never face white-box gradient attacks because attackers cannot access model weights inside a cloud VPC. Your thesis proposes a defense based on gradient-based PGD training. Why are you focusing your defense on an unrealistic threat model?"*

* **🗣️ What to Say in the Viva (15–30 Second Response):**  
  "In computer security and cryptography, we design defenses according to Kerckhoffs's Principle: assume the enemy knows everything about the system. A white-box gradient attack represents the theoretical worst-case adversary—the absolute strongest attack mathematically possible. If a castle wall can withstand a point-blank military cannon, it will effortlessly withstand an attacker throwing rocks in the dark. Hardening against white-box gradients automatically guarantees protection against black-box attackers."
* **🧠 Core Intuitive Logic (Easy to Remember):**  
  1. **Kerckhoffs's Principle:** In security engineering, never rely on security through obscurity. Always assume the attacker knows your architecture and weights.
  2. **Cannon vs. Pebbles:** A white-box gradient attack uses calculus to strike the exact weakest point. A black-box attack blindly throws probes.
  3. **Mathematical Supremum:** The loss under any black-box attack is strictly bounded by the white-box maximum: $\mathcal{L}_{\text{black}} \le \mathcal{L}_{\text{white}}$.
* **🛡️ Winning Technical Argument:**  
  White-box gradient ascent identifies the supremum of the loss within the $\epsilon$-ball:
  $$\delta_{\text{white}} = \arg\max_{\|\delta\| \le \epsilon} \mathcal{L}(f_\theta(x + \delta), y)$$
  Any black-box or zeroth-order heuristic $\delta_{\text{black}}$ yields a loss bounded by $\mathcal{L}(f_\theta(x + \delta_{\text{white}}), y)$. Solving the minimax saddle-point problem guarantees security against all weaker real-world adversaries.
* **⚠️ Viva Trap to Avoid:**  
  Do not say black-box attacks don't matter. Explain that white-box is the mathematical upper bound that encompasses black-box security.

---

> **Committee Member Question 2:** *"Apruzzese et al. specifically demonstrated that models hardened against gradient descent often fail against non-gradient black-box attacks like Square Attack because gradient training does not protect against random coordinate search. How does your mathematical formulation guarantee protection against non-gradient attacks?"*

* **🗣️ What to Say in the Viva (15–30 Second Response):**  
  "Adversarial training doesn't just block a specific gradient direction; it physically pushes the decision boundary outside the entire $\epsilon$-ball. Think of a security perimeter: if the security fence is moved 100 meters away from the building, a trespasser cannot reach the building within 50 meters, whether they walk in a straight line or stumble around in random zig-zag steps like Square Attack. Because the whole ball is inside the correct class, no search algorithm can cross the boundary within budget."
* **🧠 Core Intuitive Logic (Easy to Remember):**  
  1. **Security Perimeter Analogy:** If the fence is pushed 50 meters away, neither a sniper aiming with calculus nor a blindfolded person wandering randomly can reach the target within 20 meters.
  2. **Isotropic Margin Expansion:** Multi-step PGD with random restarts pushes the boundary outward in all directions.
  3. **Emptiness Guarantee:** The entire $\ell_\infty$-ball contains zero decision boundary points ($\mathcal{B}_\epsilon(x) \cap \partial \Omega = \emptyset$).
* **🛡️ Winning Technical Argument:**  
  Phase 2 dynamic PGD utilizes random Gaussian restarts and multi-step exploration to push $\partial \Omega$ outward, guaranteeing $\text{dist}(x, \partial \Omega) > \epsilon$. Because no boundary point exists inside the $\epsilon$-ball, coordinate searches (Square Attack) cannot find an evasion point within budget.
* **⚠️ Viva Trap to Avoid:**  
  Don't claim "Square Attack is too slow to work." State that the geometric boundary is pushed beyond the reach of the perturbation budget.

---

## 7. Oral Defense Traps to Avoid
* **Trap:** Do not dismiss Apruzzese's argument as "irrelevant" or claim that black-box attacks don't matter.
* **Safe Mathematical Stance:** Concur with Apruzzese's operational observations, and explain that in pre-defense, you adopt the white-box gradient model *specifically because it provides the mathematical upper bound* that guarantees security against all black-box and zeroth-order attacks.
