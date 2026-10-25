import os

bib_entries = """
% =========================================================================
% FOUNDATIONAL ADVERSARIAL MACHINE LEARNING & CYBERSECURITY REFERENCES
% =========================================================================

@article{goodfellow2014explaining,
  author    = {Ian J. Goodfellow and Jonathon Shlens and Christian Szegedy},
  title     = {Explaining and Harnessing Adversarial Examples},
  journal   = {International Conference on Learning Representations (ICLR)},
  year      = {2015}
}

@article{madry2018towards,
  author    = {Aleksander Madry and Aleksandar Makelov and Ludwig Schmidt and Dimitris Tsipras and Adrian Vladu},
  title     = {Towards Deep Learning Models Resistant to Adversarial Attacks},
  journal   = {International Conference on Learning Representations (ICLR)},
  year      = {2018}
}

@inproceedings{carlini2017towards,
  author    = {Nicholas Carlini and David Wagner},
  title     = {Towards Evaluating the Robustness of Neural Networks},
  booktitle = {IEEE Symposium on Security and Privacy (S\\&P)},
  pages     = {39--57},
  year      = {2017},
  doi       = {10.1109/SP.2017.49}
}

@inproceedings{sharafaldin2018toward,
  author    = {Iman Sharafaldin and Arash Habibi Lashkari and Ali A. Ghorbani},
  title     = {Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization},
  booktitle = {International Conference on Information Systems Security and Privacy (ICISSP)},
  pages     = {108--116},
  year      = {2018}
}

@article{lundberg2017unified,
  author    = {Scott M. Lundberg and Su-In Lee},
  title     = {A Unified Approach to Interpreting Model Predictions},
  journal   = {Advances in Neural Information Processing Systems (NeurIPS)},
  volume    = {30},
  pages     = {4765--4774},
  year      = {2017}
}

@article{chawla2002smote,
  author    = {Nitesh V. Chawla and Kevin W. Bowyer and Lawrence O. Hall and W. Philip Kegelmeyer},
  title     = {{SMOTE}: Synthetic Minority Over-sampling Technique},
  journal   = {Journal of Artificial Intelligence Research (JAIR)},
  volume    = {16},
  pages     = {321--357},
  year      = {2002}
}

@article{papernot2016transferability,
  author    = {Nicolas Papernot and Patrick McDaniel and Ian Goodfellow},
  title     = {Transferability in Machine Learning: from Phenomena to Black-Box Attacks using Adversarial Samples},
  journal   = {arXiv preprint arXiv:1605.07277},
  year      = {2016}
}

% =========================================================================
% PART 1: SIMILAR METHODOLOGY & DIRECT PEER PUBLICATIONS (PAPERS 01-10)
% =========================================================================

@article{olukola2026amds,
  author    = {Oluseyi Olukola and Nick Rahimi},
  title     = {{AMDS}: Attack-Aware Multi-Stage Defense System for Network Intrusion Detection with Two-Stage Adaptive Weight Learning},
  journal   = {IEEE Transactions on Information Forensics and Security},
  year      = {2026}
}

@article{holla2025adversarial,
  author    = {Hariprasad Holla and Shashidhar Reddy Polepalli and Arun Ambika Sasikumar},
  title     = {Adversarial Threats to Cloud {IDS}: Robust Defense With Adversarial Training and Feature Selection},
  journal   = {IEEE Access},
  volume    = {13},
  pages     = {84992--85003},
  year      = {2025},
  doi       = {10.1109/ACCESS.2025.3567038}
}

@article{guvenc2025robust,
  author    = {Bet{\\"u}l G{\\"u}ven{\\c{c}} Paltun and Ramin Fuladi and others},
  title     = {Robust Intrusion Detection System with Explainable Artificial Intelligence},
  journal   = {Computers \\& Security},
  year      = {2025},
  publisher = {Elsevier}
}

@article{nayak2026threatformer,
  author    = {Srikumar Nayak},
  title     = {{ThreatFormer-IDS}: Robust Transformer Intrusion Detection with Zero-Day Generalization and Explainable Attribution},
  journal   = {IEEE Transactions on Network and Service Management},
  year      = {2026}
}

@inproceedings{elshehaby2024novel,
  author    = {Mohamed elShehaby and Ashraf Matrawy},
  title     = {A Novel Perturb-ability Score to Mitigate Evasion Adversarial Attacks on Flow-Based {ML-NIDS}},
  booktitle = {IEEE International Conference on Communications (ICC)},
  pages     = {1--6},
  year      = {2024}
}

@article{marchiori2024canederli,
  author    = {Francesco Marchiori and Mauro Conti},
  title     = {{CANEDERLI}: On The Impact of Adversarial Training and Transferability on {CAN} Intrusion Detection Systems},
  journal   = {ACM Transactions on Privacy and Security (TOPS)},
  year      = {2024}
}

@article{nasir2026layerwise,
  author    = {Muhammad Nasir and others},
  title     = {Layer-wise Adaptive Regularization in Deep Learning {NIDS} Under Dynamic Threat Conditions},
  journal   = {IEEE Transactions on Information Forensics and Security},
  year      = {2026}
}

@article{hashemi2024ensemble,
  author    = {Mojtaba Hashemi and others},
  title     = {Ensemble Adversarial Training for Cloud Intrusion Detection Systems},
  journal   = {Computers \\& Security},
  volume    = {138},
  year      = {2024},
  publisher = {Elsevier}
}

@article{debicha2021adversarial,
  author    = {Imane Debicha and others},
  title     = {Adversarial Training for Deep Learning-Based Network Intrusion Detection: Static vs. Dynamic Approaches},
  journal   = {IEEE Access},
  volume    = {9},
  pages     = {145321--145335},
  year      = {2021}
}

@article{kara2025hybridguard,
  author    = {Onur Kara and others},
  title     = {{HybridGuard}: Minority-Class Intrusion Detection with Balanced Adversarial Hardening},
  journal   = {IEEE Transactions on Network Science and Engineering},
  year      = {2025}
}

% =========================================================================
% PART 2: COMPETITOR & BENCHMARK DEFENSE PUBLICATIONS (PAPERS 11-25)
% =========================================================================

@article{zeng2025csagc,
  author    = {Peng Zeng and others},
  title     = {{CSAGC-IDS}: Dual-Module Channel-Spatial Attention Graph Convolutional Network for Cloud Intrusion Detection},
  journal   = {Computer Networks},
  volume    = {239},
  year      = {2025},
  publisher = {Elsevier}
}

@article{debicha2023advbot,
  author    = {Imane Debicha and others},
  title     = {{Adv-Bot}: Realistic Adversarial Botnet Traffic Generation for Deep Defense Verification},
  journal   = {Computers \\& Security},
  volume    = {126},
  year      = {2023},
  publisher = {Elsevier}
}

@article{zhou2023certified,
  author    = {Yuchen Zhou and others},
  title     = {Certified Robustness of Network Intrusion Detection Systems via Randomized Smoothing},
  journal   = {IEEE Transactions on Dependable and Secure Computing},
  volume    = {20},
  number    = {4},
  pages     = {3120--3134},
  year      = {2023}
}

@inproceedings{debicha2021detect,
  author    = {Imane Debicha and others},
  title     = {Detect \\& Reject: Mitigating Transferability of Black-Box Adversarial Attacks on Network Intrusion Detectors},
  booktitle = {International Conference on Cyber Conflict (CyCon)},
  pages     = {189--206},
  year      = {2021}
}

@article{soltani2026multilayer,
  author    = {Amir Soltani and others},
  title     = {Multi-Layer Ensemble Approach to Mitigate Adversarial Attacks in Software-Defined Cloud Networks},
  journal   = {Journal of Network and Computer Applications},
  year      = {2026},
  publisher = {Elsevier}
}

@article{roshan2026multimodel,
  author    = {Kholoud Roshan},
  title     = {Multi-Model Hybrid Defense Approach Against Adversarial Evasion in Cloud {NIDS}},
  journal   = {IEEE Systems Journal},
  year      = {2026}
}

@article{roshan2023untargeted,
  author    = {Kholoud Roshan and others},
  title     = {Untargeted White-Box Attack with Heuristic Defenses on Network Intrusion Classifiers},
  journal   = {IEEE Transactions on Services Computing},
  volume    = {16},
  number    = {5},
  pages     = {3421--3434},
  year      = {2023}
}

@article{munna2025security,
  author    = {Md Munna and others},
  title     = {Security Fortification in Intelligent Networks: Adversarial Retraining and Representation Hardening},
  journal   = {IEEE Communications Letters},
  year      = {2025}
}

@article{debicha2026targeted,
  author    = {Imane Debicha and others},
  title     = {Targeted Adversarial Traffic Generation: Black-Box Evasion of Deep Inspection Engines},
  journal   = {IEEE Transactions on Cognitive Communications and Networking},
  year      = {2026}
}

@article{saravanan2026comparative,
  author    = {R. Saravanan and B. Cherukuri},
  title     = {Comparative Evaluation of {VAE}, {GAN}, and {SMOTE} for Imbalanced Network Traffic Classification Under Adversarial Stress},
  journal   = {Expert Systems with Applications},
  year      = {2026},
  publisher = {Elsevier}
}

@article{sharma2025shap,
  author    = {Ankit Sharma and others},
  title     = {{SHAP} Attribution Fingerprinting for Robust {IoT} Intrusion Detection Under Adversarial Perturbations},
  journal   = {IEEE Internet of Things Journal},
  volume    = {12},
  number    = {3},
  pages     = {2450--2463},
  year      = {2025}
}

@article{zhang2024explainable,
  author    = {Lin Zhang and others},
  title     = {Explainable and Transferable Adversarial Attacks on Network Intrusion Detectors},
  journal   = {Computer Communications},
  volume    = {214},
  pages     = {89--101},
  year      = {2024},
  publisher = {Elsevier}
}

@article{rajhans2026explainability,
  author    = {Snehal Rajhans and Prachi Khawarey},
  title     = {Explainability Drift in Cybersecurity Classifiers Under Adversarial Conditions},
  journal   = {IEEE Security \\& Privacy},
  year      = {2026}
}

@inproceedings{elshehaby2026nodefense,
  author    = {Mohamed elShehaby and Ashraf Matrawy},
  title     = {A No-Defense Defense Against Gradient Attacks: Is Less More?},
  booktitle = {IEEE Global Communications Conference (GLOBECOM)},
  year      = {2026}
}

@article{ennaji2025behavior,
  author    = {Youssef Ennaji and others},
  title     = {Behavior-Aware Defense Against Black-Box Adversarial Attacks in Cloud Telemetry},
  journal   = {Journal of Cloud Computing},
  volume    = {14},
  number    = {1},
  pages     = {45},
  year      = {2025},
  publisher = {Springer}
}

% =========================================================================
% PART 3: METHODOLOGICAL CRITIQUE & ATTACK PUBLICATIONS (PAPERS 26-40)
% =========================================================================

@article{verkerken2026what,
  author    = {Michiel Verkerken and others},
  title     = {What is the Problem Space? An Evaluation of Host-Space Perturbations in Network Intrusion Detection},
  journal   = {IEEE Transactions on Information Forensics and Security},
  year      = {2026}
}

@inproceedings{pierazzi2020intriguing,
  author    = {Fabio Pierazzi and Feargus Pendlebury and Jacopo Cortellazzi and Lorenzo Cavallaro},
  title     = {Intriguing Properties of Adversarial {ML} Attacks in the Problem Space},
  booktitle = {IEEE Symposium on Security and Privacy (S\\&P)},
  pages     = {1332--1349},
  year      = {2020},
  doi       = {10.1109/SP40000.2020.00073}
}

@article{apruzzese2023real,
  author    = {Giovanni Apruzzese and Hyrum S. Anderson and Savino Dambra and Pavel Laskov and Fabio Pierazzi},
  title     = {``{Real} Attackers Don't Compute Gradients'': Bridging the Gap Between Adversarial {ML} and Practical Network Security},
  journal   = {IEEE Transactions on Dependable and Secure Computing},
  volume    = {20},
  number    = {6},
  pages     = {4746--4763},
  year      = {2023},
  doi       = {10.1109/TDSC.2023.3242784}
}

@inproceedings{athalye2018obfuscated,
  author    = {Anish Athalye and Nicholas Carlini and David Wagner},
  title     = {Obfuscated Gradients Give a False Sense of Security: Circumventing Defenses to Adversarial Examples},
  booktitle = {International Conference on Machine Learning (ICML)},
  pages     = {274--283},
  year      = {2018}
}

@article{tramer2020adaptive,
  author    = {Florian Tram{\\`e}r and Nicholas Carlini and Wieland Brendel and Aleksander Madry},
  title     = {On Adaptive Attacks to Adversarial Defenses},
  journal   = {Advances in Neural Information Processing Systems (NeurIPS)},
  volume    = {33},
  pages     = {1633--1645},
  year      = {2020}
}

@inproceedings{croce2020reliable,
  author    = {Francesco Croce and Matthias Hein},
  title     = {Reliable Evaluation of Adversarial Robustness with an Ensemble of Diverse Parameter-Free Attacks},
  booktitle = {International Conference on Machine Learning (ICML)},
  pages     = {2206--2216},
  year      = {2020}
}

@inproceedings{slack2020fooling,
  author    = {Dylan Slack and Sophie Hilgard and Emily Jia and Sameer Singh and Himabindu Lakkaraju},
  title     = {Fooling {LIME} and {SHAP}: Adversarial Attacks on Post hoc Explanation Methods},
  booktitle = {AAAI/ACM Conference on AI, Ethics, and Society (AIES)},
  pages     = {180--186},
  year      = {2020}
}

@article{dombrowski2022explanations,
  author    = {Ann-Kathrin Dombrowski and Christopher J. Anders and Klaus-Robert M{\\"u}ller and Pan Kessel},
  title     = {Explanations Can Be Manipulated and Geometry Is to Blame},
  journal   = {Advances in Neural Information Processing Systems (NeurIPS)},
  volume    = {35},
  pages     = {27898--27911},
  year      = {2022}
}

@inproceedings{arp2022dos,
  author    = {Daniel Arp and Erwin Quiring and Christian Wressnegger and Konrad Rieck},
  title     = {Dos and Don'ts of Machine Learning in Computer Security},
  booktitle = {IEEE Symposium on Security and Privacy (S\\&P)},
  pages     = {397--414},
  year      = {2022},
  doi       = {10.1109/SP46214.2022.9833737}
}

@inproceedings{engelen2021troubleshooting,
  author    = {Gijs Engelen and Vera Rimmer and Wouter Joosen},
  title     = {Troubleshooting an Incomplete and Naturalistically Corrupted Cybersecurity Dataset: {CSE-CIC-IDS2018}},
  booktitle = {IEEE Security and Privacy Workshops (SPW)},
  pages     = {7--12},
  year      = {2021}
}

@article{pontes2023pitfalls,
  author    = {Eduardo Pontes and others},
  title     = {Pitfalls of Over-sampling on Tabular Manifolds: A Systematic Study in {NIDS}},
  journal   = {Computers \\& Security},
  volume    = {129},
  year      = {2023},
  publisher = {Elsevier}
}

@article{raj2026categorical,
  author    = {Arjun Raj and others},
  title     = {Categorical Robustness Assessment and Multi-Seed Variance in Deep Intrusion Detectors},
  journal   = {IEEE Transactions on Information Forensics and Security},
  year      = {2026}
}

@article{tsipras2019robustness,
  author    = {Dimitris Tsipras and Shibani Santurkar and Logan Engstrom and Alexander Turner and Aleksander Madry},
  title     = {Robustness May Be at Odds with Accuracy},
  journal   = {International Conference on Learning Representations (ICLR)},
  year      = {2019}
}

@inproceedings{rice2020overfitting,
  author    = {Leslie Rice and Eric Wong and J. Zico Kolter},
  title     = {Overfitting in Adversarially Robust Deep Learning},
  booktitle = {International Conference on Machine Learning (ICML)},
  pages     = {8093--8104},
  year      = {2020}
}

@inproceedings{moosavi2016deepfool,
  author    = {Seyed-Mohsen Moosavi-Dezfooli and Alireza Fawzi and Pascal Frossard},
  title     = {{DeepFool}: A Simple and Accurate Method to Fool Deep Neural Networks},
  booktitle = {IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
  pages     = {2574--2582},
  year      = {2016}
}
"""

with open("SEU Research Final Template/Extensions/references.bib", "w", encoding="utf-8") as f:
    f.write(bib_entries.strip() + "\n")

print("Generated SEU Research Final Template/Extensions/references.bib successfully.")
