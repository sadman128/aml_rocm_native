# 🎓 Master Viva Defense Rapid-Fire Cheat Sheet (56 Simple Q&As)
## Adversarial Robustness in NIDS via Attribution-Guided Feature Selection & Dynamic Multi-Stage Adversarial Training

> **Viva Rules:**
> 1. **No filler words:** Do not say "Sir", "Thank you", or "In our paper". Start directly with the answer.
> 2. **Super short & simple:** 1 to 2 plain sentences. Say the core fact and stop talking.
> 3. **Non-CS friendly:** Clear, intuitive logic that anyone on the committee can understand immediately.

---

# 🏛️ Theme 1: Architecture & Model Choices

#### 1. Why didn't you use CNNs, LSTMs, or Transformers instead of a 4-layer MLP?
Network traffic is simple tabular numbers, not images or text. Transformers and CNNs are too slow and drop packets, while an MLP classifies traffic in under 0.02 milliseconds.

#### 2. Why not XGBoost or Random Forest?
Tree models make sharp step-by-step decisions, so you cannot use gradients to train them against attacks. They crash under adversarial attacks, while neural networks have smooth math that we can harden with live PGD.

#### 3. Why only 4 layers in your MLP? Why not deeper?
Our dataset only has 27 features, so a deeper network would overfit and run slower. 4 layers is fast, lightweight, and takes only 70 minutes to train on our GPU.

#### 4. Why the funnel shape (27 -> 128 -> 64 -> 32 -> 2)?
Halving the layers step-by-step compresses the data, throwing away random attack noise while keeping the true pattern of normal and malicious traffic.

#### 5. Why use ReLU instead of Sigmoid or Tanh?
Network traffic like packet counts and duration can never be negative, which matches ReLU's 0 to positive range. Sigmoid and Tanh squash numbers and introduce negative values that don't fit traffic data.

#### 6. Why use Dropout (p=0.30) and Batch Normalization?
Dropout stops the model from relying on a single feature, so tweaking one clue won't fool it. Batch Normalization keeps the data steady when mixing clean and attacked traffic.

#### 7. Why binary classification (Benign vs. Malicious) instead of 14 attack classes?
A firewall's immediate job is binary: allow the packet or block it. Once we prove the firewall can block attacks at line-rate speed, classifying specific attack types can be added later.

---

# 🧬 Theme 2: Feature Selection & SHAP

#### 8. Why use SHAP?
SHAP is mathematically fair and consistent. It tells us exactly how much each feature's importance changes when an attacker starts manipulating traffic.

#### 9. Why use Mutual Information (MI)?
Mutual Information quickly checks which features actually share useful information with attack labels, catching complex non-linear patterns that simple correlation misses.

#### 10. Why use Mutual Information BEFORE SHAP?
Testing all combinations of 69 features with SHAP is too slow for 6.3 million rows. Mutual Information drops 29 useless features in seconds so SHAP can quickly focus on the top 40.

#### 11. Why threshold 0.85 in Mutual Information?
It keeps the top features holding 95% of the useful information, while cutting out the noisy bottom features that don't help detect attacks.

#### 12. Why not PCA for feature selection?
PCA mixes all features into messy math formulas, so we can no longer tell which real packet features are safe. It also ignores whether traffic is under attack.

#### 13. Why not LIME instead of SHAP?
LIME tests random guesses around each sample, giving different explanations every time you run it. SHAP gives exact, repeatable math every time.

#### 14. Why not Random Forest feature importance?
Random Forest only checks what features look good on normal, quiet traffic. It doesn't see that an attacker can easily fake those same features.

#### 15. Why not simple correlation (Pearson/Spearman)?
Correlation only spots simple straight-line trends. Hackers change packet timing in complex, non-linear ways that only Mutual Information and SHAP can catch.

#### 16. What is the Stability Score in simple words?
It compares a feature's importance on normal traffic versus attacked traffic. If the importance stays the same, the score is 1 (robust); if it swings wildly, the score is 0 (fragile).

#### 17. Why keep 80% stability mass (27 features)?
The 80/20 rule: the top 27 features hold 80% of all stable clues. The remaining 13 features are unstable traps that attackers easily manipulate, so we drop them.

#### 18. How does removing 13 unstable features protect normal accuracy?
Unstable features give conflicting signals during training, confusing the model. Dropping them removes the noise, so the model learns normal traffic cleanly without losing accuracy.

---

# ⚔️ Theme 3: Attacks & PGD Dynamics

#### 19. Why 20-step PGD for the canary SHAP test?
20 attack steps is thorough enough to see if a feature's importance breaks under pressure, without taking forever to compute.

#### 20. Why 5-step PGD during training instead of 20-step?
5 steps creates strong attack samples in just 2 milliseconds per batch. Using 20 steps per batch would quadruple training time from 70 minutes to 5 hours for almost no extra benefit.

#### 21. Why train with PGD instead of FGSM?
FGSM only takes one single blind guess, which makes the model falsely think it's safe. PGD takes multiple steps to find the worst-case attack, building real defense.

#### 22. Why not train with Carlini-Wagner (CW)?
Carlini-Wagner is an intense optimization attack that takes seconds per sample, which would take weeks to train on 4.5 million flows. We use it only as a benchmark test on the final model.

#### 23. Why not train with DeepFool?
DeepFool calculates how to cross the boundary with minimal effort, whereas PGD guarantees attacks stay within a realistic packet-size box (epsilon = 0.05).

#### 24. Why step size 0.005 with epsilon 0.05 in PGD?
Taking small steps of 0.005 ensures the attack moves smoothly toward the worst vulnerability without overshooting or bouncing around.

#### 25. What does epsilon = 0.05 mean physically in network traffic?
It means an attacker can alter packet timing or byte sizes by at most 5%. That is small enough to keep network connections working without corrupting the protocol.

#### 26. What is Attack Staleness?
If you generate fake attacks once before training, the model's brain shifts as it learns, making those old attacks useless and leaving a 20% security hole.

#### 27. How does live mini-batch PGD stop attack staleness?
We create brand-new attacks on the fly right before every training batch, so the attacks always match the model's newest decision boundary.

---

# 🔄 Theme 4: Training Curriculum & Two-Phase Hardening

#### 28. Why warm up for 10 epochs? Why not 20 or 5?
At the start, the model knows nothing. 10 epochs gives it enough time to learn normal traffic patterns first; 5 is too rushed, and 20 wastes time before hardening begins.

#### 29. Why not attack from Epoch 1?
If you attack on Day 1 while the model has random weights, it gets overwhelmed by chaos and never learns what normal traffic even looks like.

#### 30. Why 50 total epochs? Why not 100?
The model stops improving after epoch 45. Running 100 epochs would waste GPU time and risk memorizing attack noise.

#### 31. Why a 50-50 balance between clean and attack data?
It treats normal traffic and attack traffic with equal importance, preventing the model from becoming paranoid or overly lenient.

#### 32. Why use the Adam optimizer?
Adam automatically adjusts the learning speed for each feature, which keeps training smooth when dealing with both clean and attacked samples.

#### 33. Why batch size 2048?
2048 samples at once fully utilizes our AMD graphics card, speeding up training to just 70 minutes while keeping memory usage under 2.2 GB.

#### 34. What is the total loss function in Phase 2?
Half cross-entropy loss on clean traffic plus half cross-entropy loss on live PGD attacks.

---

# 📦 Theme 5: Dataset, Preprocessing & Leakage

#### 35. Why use CSE-CIC-IDS2018?
It is the most realistic modern benchmark, created on an enterprise AWS network across 500 servers with 6.3 million flows and 14 modern attacks.

#### 36. Why not KDD99 or NSL-KDD?
They are over 25 years old and use simulated 1990s traffic that has nothing in common with modern internet protocols or threats.

#### 37. Why not CIC-IDS2017?
The 2017 dataset has broken timestamps, missing traffic labels, and syntax errors. The 2018 version fixed these issues and is much larger.

#### 38. Why D'hooge's curation instead of raw UNB CSVs?
The raw university CSVs have broken headers on Day 4 and missing values that crash programs. D'hooge cleaned them into standardized Parquet files while keeping all 6.3 million flows.

#### 39. Why remove IP addresses and port numbers?
Attackers change IPs and ports in seconds. If we keep them, the AI simply memorizes 'Port 80 is good', which looks great on paper but fails against real hackers.

#### 40. Why SMOTE instead of simple undersampling?
Undersampling deletes 75% of our normal traffic data, throwing away valuable training. SMOTE creates synthetic attack examples so we keep all our normal data.

#### 41. Why SMOTE instead of class weights?
Class weights just multiply the loss number without creating new examples. SMOTE actually fills the empty space with synthetic attack points, drawing a better boundary.

#### 42. Why apply SMOTE only inside the training split?
If you use SMOTE before splitting, synthetic test data leaks into the training set, which is cheating. Applying it only inside training keeps the test set 100% honest and unseen.

#### 43. Why a 72-8-20 split?
On 6.3 million flows, 20% locks away 1.26 million real flows for a bulletproof final test, while 8% validation makes sure training doesn't overfit.

---

# 🔍 Theme 6: Verification Against Fake Defenses

#### 44. What is Gradient Masking?
A fake defense where a model hides or flattens its math gradients. It tricks basic gradient attacks into failing, but black-box attacks easily break it.

#### 45. How do you prove your model doesn't have gradient masking?
First, 100 attack steps must do more damage than 20 steps. Second, black-box attacks cannot be stronger than white-box attacks. If both hold, the defense is real.

#### 46. What is DeepFool and why test it?
DeepFool finds the shortest distance needed to push a packet across the border. It proves whether our training actually pushed the enemy boundary further away.

#### 47. What is Carlini-Wagner (CW) and why test it?
Carlini-Wagner is a famous attack built specifically to defeat fake, masked defenses. If our model resists CW on the test set, our robustness is genuine.

#### 48. What is Square Attack and why test it?
Square Attack is a blind black-box attack that uses zero gradients. If a model survives white-box attacks but fails Square Attack, its defense is fake.

#### 49. What is Auto-PGD (APGD) and why test it?
Auto-PGD automatically tunes its own step size to find the best attack path, ensuring our evaluation doesn't rely on poorly tuned attacks.

#### 50. Why test 9 different attack types?
Real attackers won't use the same attack we trained on. Testing 9 diverse attacks proves our defense works against unexpected threats, not just our own training method.

#### 51. What is surrogate model transferability?
An attacker trains their own clone model, creates attacks on it, and sends them to our model. Testing this proves we can block attacks even when the hacker doesn't have our code.

---

# 📊 Theme 7: Expected Results & Hardware Feasibility

#### 52. How did you come up with 95.5% clean and 88-90% robust accuracy?
Published peer papers reached 88% with static training and 89.4% with dynamic training. Because we eliminate attack staleness and prune 13 noisy features, we expect to match and beat that frontier without losing normal accuracy.

#### 53. What does Attack Success Rate <12% mean practically?
It means less than 12 out of 100 attacks manage to sneak past our firewall. Undefended models let 70 out of 100 attacks sneak through.

#### 54. Why is line-rate speed defined as <0.05 ms per flow?
Data center switches process millions of packets per second. If our AI takes more than 0.05 milliseconds per flow, network traffic backs up and drops packets.

#### 55. How can an 8 GB AMD GPU train 6.3 million flows in 70 minutes?
Our model has only 27 inputs and 14,000 parameters, which takes under 2.2 GB of VRAM. PyTorch ROCm runs large batches of 2048 flows completely in parallel.

#### 56. What if your final experiments get 84% instead of 88%?
84% is still a huge leap over the 30% undefended baseline. If needed, we can increase the attack loss weight or train with 7 PGD steps to strengthen the boundary.
