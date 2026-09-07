# Master Study Index: 40 Individual Paper Reviews

This directory contains **40 individual, paper-by-paper research guides and critiques** prepared for thesis study, literature review chapter writing, and pre-defense / final defense preparation. 

Every paper is kept in its own dedicated Markdown file so you can study each work independently without confusion.

---

## Directory Organization & Reading Roadmap

### Part 1: Papers with Similar Methodology (Direct Peers & Predecessors)
*Studies employing multi-stage training, attribution-informed feature selection, or dynamic adversarial hardening.*

1. [**01. AMDS: Attack-Aware Multi-Stage Defense System (Olukola & Rahimi, 2026)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/01_olukola2026_amds.md)
   * *Focus:* Two-stage training with adaptive clean/adversarial loss scheduling.
2. [**02. Adversarial Threats to Cloud IDS (Holla et al., 2025)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/02_holla2025_adversarial_threats.md)
   * *Focus:* Direct foundational baseline on CSE-CIC-IDS2018; offline static data augmentation + SHAP selection.
3. [**03. Robust Intrusion Detection System with Explainable AI (Güvenç Paltun et al., 2025)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/03_guvenc2025_robust_xai.md)
   * *Focus:* Attribution Alignment Loss penalizing SHAP drift during training.
4. [**04. ThreatFormer-IDS: Robust Transformer IDS (Nayak, 2026)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/04_nayak2026_threatformer.md)
   * *Focus:* Attention-attribution stability pruning with lightweight Transformer architecture.
5. [**05. A Novel Perturb-ability Score for ML-NIDS (elShehaby & Matrawy, 2024)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/05_elshehaby2024_perturbability.md)
   * *Focus:* Heuristic feature sensitivity ranking to prune vulnerable flow features.
6. [**06. CANEDERLI: Adversarial Training and Transferability (Marchiori & Conti, 2024)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/06_marchiori2024_canederli.md)
   * *Focus:* Clean warmup followed by online PGD; surrogate transferability analysis.
7. [**07. Layer-wise Adaptive Regularization in NIDS (Nasir et al., 2026)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/07_nasir2026_layerwise_reg.md)
   * *Focus:* Internal hidden-layer Lipschitz regularization to prevent gradient shattering.
8. [**08. Ensemble Adversarial Training for Cloud IDS (Hashemi et al., 2024)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/08_hashemi2024_ensemble_at.md)
   * *Focus:* Mutual Information reduction followed by multi-model adversarial ensemble.
9. [**09. Adversarial Training for DL-NIDS: Static vs Dynamic (Debicha et al., 2021)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/09_debicha2021_at_nids.md)
   * *Focus:* Empirical proof that static offline augmentation suffers from perturbation staleness.
10. [**10. HybridGuard: Minority-Class Intrusion Detection (Kara et al., 2025)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/10_kara2025_hybridguard.md)
   * *Focus:* Stage 1 & 2 preprocessing engine: Mutual Information (40 features) + continuous SMOTE.

---

### Part 2: Competitor & Alternative Benchmark Defenses
*Contemporary alternative architectures and baseline comparisons.*

11. [**11. CSAGC-IDS: Dual-Module Channel-Spatial Attention GCN (Zeng et al., 2025)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/11_zeng2025_csagc_ids.md)
12. [**12. Adv-Bot: Realistic Adversarial Botnet Attacks (Debicha et al., 2023)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/12_debicha2023_advbot.md)
13. [**13. Certified Robustness via Randomized Smoothing (Zhou et al., 2023)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/13_zhou2023_randomized_smoothing.md)
14. [**14. Detect & Reject for Transferability of Black-Box Attacks (Debicha et al., 2021)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/14_debicha2021_detect_reject.md)
15. [**15. Multi-Layer Ensemble Approach to Mitigate Attacks (Soltani et al., 2026)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/15_soltani2026_multilayer_ensemble.md)
16. [**16. Multi-Model Hybrid Defense Approach (Roshan, 2026)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/16_roshan2026_hybrid_defense.md)
17. [**17. Untargeted White-Box Attack with Heuristic Defenses (Roshan et al., 2023)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/17_roshan2023_heuristic_defenses.md)
18. [**18. Security Fortification in Intelligent Networks (Munna et al., 2025)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/18_munna2025_intelligent_networks.md)
19. [**19. Targeted Adversarial Traffic Generation: Black-Box Evasion (Debicha et al., 2026)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/19_debicha2026_blackbox_evasion.md)
20. [**20. Comparative Evaluation of VAE, GAN, and SMOTE (Saravanan & Cherukuri, 2026)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/20_saravanan2026_smote_evaluation.md)
21. [**21. SHAP Attribution Fingerprinting for IoT Detection (Sharma et al., 2025)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/21_sharma2025_shap_fingerprinting.md)
22. [**22. Explainable and Transferable Adversarial Attacks (Zhang et al., 2024)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/22_zhang2024_xai_transfer_attacks.md)
23. [**23. Explainability Drift in Cybersecurity Classifiers (Rajhans & Khawarey, 2026)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/23_rajhans2026_explainability_drift.md)
24. [**24. A No-Defense Defense Against Gradient Attacks: Is Less More? (elShehaby & Matrawy, 2026)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/24_elshehaby2026_is_less_more.md)
25. [**25. Behavior-Aware Defense Against Black-Box Attacks (Ennaji et al., 2025)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/25_ennaji2025_behavior_aware.md)

---

### Part 3: Attacking / Methodological Critique Papers (With Defense Board Mock Q&A)
*Critical papers board members will use to challenge your work, with detailed, bullet-proof counter-arguments and numbers from our V9 methodology.*

26. [**26. "What is the Problem Space?" Host-Space Perturbations (Verkerken et al., 2026)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/26_verkerken2026_problem_space.md)
    * *Critique:* 60% of continuous feature perturbations cannot be reconstructed into valid TCP/IP packets.
    * *Our Defense:* Continuous envelope as mathematical upper bound + empirical feature clamping `[lo, hi]` + structural mask.
27. [**27. Intriguing Properties of Adversarial ML in the Problem Space (Pierazzi et al., 2020)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/27_pierazzi2020_intriguing_properties.md)
    * *Critique:* Inverse mapping problem; non-invertible feature spaces create synthetic illusions.
    * *Our Defense:* Focus on packet length/timing dynamics that directly map to available problem-space transformations (padding & delay).
28. [**28. Real Attackers Don't Compute Gradients (Apruzzese et al., 2023)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/28_apruzzese2023_real_attackers.md)
    * *Critique:* White-box gradient threat models are unrealistic in operational network environments.
    * *Our Defense:* Gradient training creates broad decision margins; verified on zero-gradient Square Attack (**91.83% Acc**, 5.27% ASR) and surrogate transfer (**94.13% Acc**, 2.08% ASR).
29. [**29. Obfuscated Gradients Give a False Sense of Security (Athalye et al., 2018)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/29_athalye2018_obfuscated_gradients.md)
    * *Critique:* Low ASR is often caused by gradient masking, shattered gradients, or vanishing gradients.
    * *Our Defense:* Passed all 5 Athalye diagnostics: Iterative PGD > FGSM, APGD-CE (88.55%), CW-Linf (90.15%), Square Attack (91.83%), and surrogate transfer (94.13%).
30. [**30. On Adaptive Attacks to Adversarial Defenses (Tramèr et al., 2020)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/30_tramer2020_adaptive_attacks.md)
    * *Critique:* Defenses trained on cross-entropy collapse under adaptive loss objectives.
    * *Our Defense:* Evaluated against 4 unseen adaptive objectives (CW margin loss, APGD-CE, MIM, BIM), maintaining 88.55% to 91.37% accuracy.
31. [**31. Reliable Evaluation via AutoAttack / APGD (Croce & Hein, 2020)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/31_croce2020_autoattack.md)
    * *Critique:* Fixed-step PGD gets trapped on local loss plateaus; attacks are under-optimized.
    * *Our Defense:* APGD-CE with adaptive step-size decay executed across all 3 seeds; maintained **88.55% ± 1.95% accuracy**.
32. [**32. Fooling LIME and SHAP: Adversarial Scaffolding (Slack et al., 2020)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/32_slack2020_fooling_shap.md)
    * *Critique:* SHAP explanations can be tricked by scaffolding adversaries.
    * *Our Defense:* SHAP is computed strictly offline during training on trusted calibration data; 27-feature mask is frozen into the model, leaving zero runtime attack surface.
33. [**33. Explanations Can Be Manipulated & Geometry Is to Blame (Dombrowski et al., 2022)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/33_dombrowski2022_explanations_geometry.md)
    * *Critique:* Gradient attributions reflect local manifold curvature noise rather than feature importance.
    * *Our Defense:* Curvature noise is precisely what $S(f)$ penalizes; high-divergence features are discarded ($S_f \to 0$), leaving only flat, stable dimensions.
34. [**34. Dos and Don'ts of Machine Learning in Security (Arp et al., 2022)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/34_arp2022_dos_and_donts.md)
    * *Critique:* 70%+ of NIDS papers suffer from data snooping, preprocessing leakage, and test contamination.
    * *Our Defense:* Strict 5-point zero-leakage protocol: pre-transformation 80/10/20 splitting, train-only StandardScaler and SMOTE, sequestered calibration pool, and frozen test partition.
35. [**35. Troubleshooting CSE-CIC-IDS2018 (Engelen et al., 2021)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/35_engelen2021_troubleshooting_cicids.md)
    * *Critique:* CSE-CIC-IDS2018 is corrupted with socket metadata leakage (IPs/ports enabling fake 99% accuracy).
    * *Our Defense:* Systematically stripped all socket identifiers (`Flow ID`, `Src/Dst IP`, `Src/Dst Port`, `Timestamp`); model learns strictly from bidirectional flow dynamics.
36. [**36. Pitfalls of Over-sampling on Tabular Manifolds (Pontes et al., 2023)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/36_pontes2023_oversampling_pitfalls.md)
    * *Critique:* SMOTE creates synthetic anomalies between non-convex clusters.
    * *Our Defense:* Applied SMOTE strictly to the 40 continuous numeric MI features on training data only; test set evaluated in natural class imbalance (96.19% Acc, 0.9620 F1).
37. [**37. Categorical Robustness Assessment & Seed Variance (Raj et al., 2026)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/37_raj2026_categorical_robustness.md)
    * *Critique:* Single-seed evaluations exhibit up to ±15% variance under PGD; results are unreliable.
    * *Our Defense:* Full 3-seed protocol (`seeds = [42, 123, 2024]`); all numbers reported as Mean ± Std; standard deviations $\le 1.95\%$ across all 11 attacks.
38. [**38. Robustness May Be at Odds with Accuracy (Tsipras et al., 2019)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/38_tsipras2019_robustness_vs_accuracy.md)
    * *Critique:* Adversarial robustness fundamentally reduces clean accuracy.
    * *Our Defense:* Tsipras assumes a fixed feature space. Phase2Net replaces noisy baseline features with a 27-dimensional stable subspace; online PGD acts as a regularizer, boosting clean accuracy by **+3.37%** (to 96.19%).
39. [**39. Overfitting in Adversarially Robust Deep Learning (Rice et al., 2020)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/39_rice2020_robust_overfitting.md)
    * *Critique:* Robust test accuracy collapses late in adversarial training.
    * *Our Defense:* Phase 1 clean warmup prevents early collapse; 10% dev-set checkpointing captures weights at peak validation performance; balanced $0.5 \mathcal{L}_{\text{clean}} + 0.5 \mathcal{L}_{\text{adv}}$ loss prevents over-indexing.
40. [**40. The DeepFool Dilemma: Geometric Margin Probing (Moosavi-Dezfooli et al., 2016)**](file:///f:/PythonProjects/aml_rocm_native/literature%20review/papers/40_moosavi2016_deepfool_dilemma.md)
    * *Critique:* DeepFool achieves 94% flip rate on robust models.
    * *Our Defense:* DeepFool is an unconstrained minimum-distance attack. Phase2Net pushed the mean $L_2$ boundary distance to **4.1502** (+103% over baseline). Within the valid threat budget ($\epsilon \le 0.05$), DeepFool flips **only 2.67% of samples**.
