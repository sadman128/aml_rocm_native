import os

chapter2_latex = r"""\chapter{Literature Review and Theoretical Foundations}\label{chap:lit_review}

\section{Introduction and Taxonomy of Adversarial Threats in Cloud NIDS}\label{sec:lit_intro}

Cloud-native computing environments increasingly rely on Network Intrusion Detection Systems (NIDS) powered by Deep Neural Networks (DNNs) to process multi-gigabit traffic streams and detect sophisticated zero-day incursions. While deep learning architectures deliver exceptional classification accuracy on clean, identically and independently distributed (i.i.d.) network telemetry, they remain fundamentally brittle when subjected to test-time evasion attacks generated via Adversarial Machine Learning (AML)~\cite{goodfellow2014explaining,madry2018towards}. 

In the tabular cloud NIDS domain, an adversary aims to craft an evasion flow vector $x_{\text{adv}} \in \mathbb{R}^d$ from a true malicious traffic vector $x_0 \in \mathbb{R}^d$ such that a trained neural detector $f: \mathbb{R}^d \to \mathcal{Y}$ misclassifies the malicious transmission as benign ($f(x_{\text{adv}}) = 0$ where $f(x_0) = 1$). To maintain network protocol semantics and evasion imperceptibility, the adversarial perturbation is bounded within an $L_\infty$-norm budget $\epsilon$:
\begin{equation}\label{eq:threat_model_norm}
    \|x_{\text{adv}} - x_0\|_\infty = \max_{j \in \{1,\dots,d\}} |x_{\text{adv},j} - x_{0,j}| \le \epsilon
\end{equation}
subject to valid feature domain constraints $x_{\text{adv}} \in [x_{\min}, x_{\max}]^d$ and structural invariance masks $m \in \{0,1\}^d$ ensuring immutable traffic characteristics remain unaltered.

\begin{figure}[!htp]
\centering
\begin{minipage}{0.95\textwidth}
\small
\textbf{Taxonomy of Adversarial Threats in Cloud NIDS:}
\begin{itemize}
    \item \textbf{White-Box Gradient Attacks:} Adversary possesses full knowledge of network topology, weights $\theta$, and loss function $\mathcal{L}$. Includes single-step Fast Gradient Sign Method (FGSM)~\cite{goodfellow2014explaining}, multi-step Projected Gradient Descent (PGD)~\cite{madry2018towards}, Basic Iterative Method (BIM), Momentum Iterative Method (MIM), and adaptive Auto-PGD (APGD-CE)~\cite{croce2020reliable}.
    \item \textbf{Black-Box Query Attacks:} Adversary queries the target model as an oracle without gradient access. Evaluated via score-based coordinate perturbation search (Square Attack) and decision-based boundary searches~\cite{apruzzese2023real}.
    \item \textbf{Surrogate Transfer Attacks:} Adversary trains an independent surrogate model $\hat{f}$, crafts adversarial samples against $\hat{f}$, and transfers them against the target cloud NIDS~\cite{papernot2016transferability,marchiori2024canederli}.
    \item \textbf{Unconstrained Geometric Probing:} Iterative minimum-distance optimization (DeepFool)~\cite{moosavi2016deepfool} used to quantify orthogonal decision boundary margins.
\end{itemize}
\end{minipage}
\caption{Taxonomy of adversarial threat vectors evaluated in modern cloud NIDS literature.}\label{fig:threat_taxonomy}
\end{figure}

The existing literature on adversarial defenses in cloud NIDS can be systematically partitioned into three categories: (1) multi-stage architectures and attribution-informed feature selection methods, (2) contemporary alternative benchmark defenses (certified smoothing, graph neural networks, and ensembles), and (3) foundational critique studies addressing problem-space realization, gradient masking, and evaluation pitfalls. The following sections provide a rigorous analysis of each domain.

\section{Directly Related Methodological Peers}\label{sec:peer_review}

A distinct group of recent studies shares our foundational philosophy: combining multi-stage training schedules, feature-space pruning, and adversarial hardening. Analyzing these works reveals both their merits and their critical architectural limitations.

\subsection{Static Offline Augmentation vs. Dynamic Perturbation}
The direct foundational baseline for our research is the cloud intrusion defense proposed by Holla et al.~\cite{holla2025adversarial}. Their pipeline evaluates deep learning models on the CSE-CIC-IDS2018 benchmark dataset. Holla et al. apply Mutual Information (MI) to select an initial 40-feature subset, compute clean Shapley Additive Explanations (SHAP)~\cite{lundberg2017unified} attributions to isolate the top 15 features, and train a 3-layer Multi-Layer Perceptron (MLP) with dimensions $128 \to 64 \to 32$. To confer robustness, they introduce a static triad data augmentation strategy: pre-generating 10,000 FGSM, 10,000 PGD, and 10,000 DeepFool samples offline using an initial undefended baseline model, concatenating these static samples into the training pool, and retraining across 50 epochs.

While Holla et al.~\cite{holla2025adversarial} demonstrate improved resistance against weak single-step perturbations, their approach exhibits three fatal vulnerabilities:
\begin{enumerate}
    \item \textbf{Perturbation Staleness:} Static adversarial samples are generated once with respect to the initial model weights $\theta_0$. As the neural network updates during retraining, the model's loss landscape shifts, rendering the static samples obsolete. The model easily minimizes empirical loss on the static augmented samples while remaining critically exposed to fresh, dynamic adversarial vectors generated against updated weights $\theta_t$.
    \item \textbf{Gradient-Fragile Feature Selection:} Selecting features purely based on clean SHAP attributions favors features with large initial gradient norms. As proved by Dombrowski et al.~\cite{dombrowski2022explanations}, clean gradient attributions frequently reflect local manifold curvature rather than true invariant importance, making these dimensions easily manipulable by gradient ascent.
    \item \textbf{Robustness Ceiling:} Under standard iterative white-box attacks (PGD-100 at $\epsilon = 0.05$), the defense achieved only $79.70\%$ accuracy, with an Attack Success Rate (ASR) of $14.65\%$.
\end{enumerate}

Debicha et al.~\cite{debicha2021adversarial} conduct a focused comparative study contrasting static offline adversarial augmentation with dynamic online adversarial training in network anomaly detection. Their empirical findings confirm that static augmentation provides a false sense of security; models trained on fixed offline perturbations collapse when challenged by iterative attacks, whereas dynamic batch-level adversarial generation maintains active boundary regularization throughout convergence.

\subsection{Two-Stage Training and Adaptive Weighting}
Olukola and Rahimi~\cite{olukola2026amds} propose AMDS, an attack-aware multi-stage defense system for network intrusion detection. AMDS establishes a two-stage training protocol: Stage 1 trains an initial neural backbone exclusively on clean network flows to establish well-clustered latent representations, while Stage 2 injects dynamic 20-step PGD perturbations with an adaptive loss-weighting mechanism driven by batch-level gradient magnitudes. While AMDS successfully mitigates catastrophic clean accuracy collapse, it operates across the complete raw feature space without attribution filtering. This incurs excessive gradient computation latency and produces a $2.1\%$ penalty on clean network traffic.

Marchiori and Conti~\cite{marchiori2024canederli} present CANEDERLI, evaluating two-phase adversarial training for vehicle CAN-bus and telemetry intrusion systems. Their architecture utilizes clean warm-up epochs followed by iterative PGD perturbation injection, coupled with an evaluation of cross-model surrogate transferability. Their findings demonstrate that clean pretraining stabilizes batch normalization running statistics, preventing the erratic gradient oscillations that occur when random adversarial vectors are injected from epoch zero.

\subsection{Attribution Alignment and Feature Stability}
G{\"{u}}ven{\c{c}} Paltun et al.~\cite{guvenc2025robust} investigate explainability drift in cybersecurity classifiers, noting that feature attributions fluctuate widely under adversarial attacks. To counteract this, they propose an Attribution Alignment Loss that penalizes discrepancies between clean and adversarial SHAP explanations during model training. While mathematically elegant, calculating SHAP explanations inside every training batch requires second-order Hessian calculations, multiplying wall-clock training time by over $400\%$ and making the approach intractable for enterprise cloud datasets containing millions of flow records.

Nayak~\cite{nayak2026threatformer} introduces ThreatFormer-IDS, combining attention-attribution stability pruning with a Transformer encoder. However, Nayak evaluates attribution stability solely against random Gaussian noise rather than directed gradient ascent, leaving the identified features vulnerable to worst-case adversarial perturbation. Similarly, elShehaby and Matrawy~\cite{elshehaby2024novel} formulate a heuristic ``Perturb-ability Score'' (PS) based on feature variance to discard sensitive dimensions. However, their heuristic ignores non-linear cooperative feature interactions, which cooperative game-theoretic metrics like SHAP capture rigorously.

In tabular cloud NIDS preprocessing, Kara et al.~\cite{kara2025hybridguard} propose HybridGuard, establishing the efficacy of combining initial Mutual Information feature reduction (top 40 features) with synthetic minority oversampling (SMOTE) to stabilize minority attack representation. Nasir et al.~\cite{nasir2026layerwise} introduce layer-wise adaptive regularization, enforcing Lipschitz continuity across hidden representations to prevent gradient shattering. Hashemi et al.~\cite{hashemi2024ensemble} explore ensemble adversarial training across multiple disparate architectures, highlighting that diversity in feature sub-spaces reduces transferability across models.

\section{Contemporary Alternative and Benchmark Defenses}\label{sec:alternative_defenses}

Beyond multi-stage adversarial training, several alternative defensive paradigms have been advanced in contemporary intrusion detection literature.

\subsection{Graph Neural Networks and Topology Defense}
Zeng et al.~\cite{zeng2025csagc} propose CSAGC-IDS, a Dual-Module Channel-Spatial Attention Graph Convolutional Network designed to capture topological dependencies among interconnected cloud hosts. By modeling network traffic as communication graphs, CSAGC-IDS exploits spatial correlation to detect coordinated distributed denial-of-service (DDoS) and botnet campaigns. However, graph-based architectures exhibit high computational complexity ($O(|V|^2)$ in dense graphs) and introduce latency overheads that impede wire-speed line-rate inspection in 100~Gbps enterprise backbones. Furthermore, adversarial graph perturbations (e.g., topology poisoning) present an emerging attack surface.

\subsection{Certified Defenses via Randomized Smoothing}
Zhou et al.~\cite{zhou2023certified} adapt Randomized Smoothing to network intrusion detection, establishing mathematically certified robustness guarantees within an $L_2$-norm radius $R$. By adding isotropic Gaussian noise $\epsilon \sim \mathcal{N}(0, \sigma^2 I)$ to input flow vectors and taking the majority vote over Monte Carlo samples, the classifier guarantees invariant predictions within the certified radius. Nevertheless, certified smoothing incurs severe operational penalties in cloud NIDS: evaluating $N = 100,000$ Monte Carlo samples per flow vector inflates inference latency from microseconds to hundreds of milliseconds, creating unacceptable packet queuing delays in real-time firewall deployments. Moreover, randomized smoothing provides spherical $L_2$ guarantees, which fail to bound coordinate-wise $L_\infty$ box perturbations effectively in tabular domains.

\subsection{Reject-Option and Filter Classifiers}
Debicha et al.~\cite{debicha2021detect} formulate Detect \& Reject, an architecture that couples a primary intrusion detector with an auxiliary autoencoder or density estimator trained to flag off-manifold adversarial samples. Suspicious inputs falling into low-density regions trigger a ``reject'' response for manual forensic triage. However, as demonstrated by Tram{\`{e}}r et al.~\cite{tramer2020adaptive}, reject-option defenses remain vulnerable to joint loss optimization, wherein an adaptive attacker crafts perturbations that simultaneously minimize classifier loss and evade the auxiliary detector. Debicha et al.~\cite{debicha2023advbot} further demonstrate that realistic adversarial botnet traffic can easily circumvent separate statistical filtering stages.

\subsection{Ensemble Defenses and Heuristic Hardening}
Soltani et al.~\cite{soltani2026multilayer} present a multi-layer ensemble architecture for software-defined cloud networks, chaining disparate weak classifiers across successive ingress layers. Roshan~\cite{roshan2026multimodel} and Roshan et al.~\cite{roshan2023untargeted} propose hybrid heuristic defenses, combining input quantization, feature squeezing, and random feature nullification. While these heuristic approaches improve resilience against naive attacks, they frequently rely on gradient masking; once an adaptive attacker formulates a differentiable surrogate or applies Backward Pass Differentiable Approximation (BPDA)~\cite{athalye2018obfuscated}, heuristic robustness drops to near zero.

\subsection{Tabular Preprocessing and Class Balancing}
Saravanan and Cherukuri~\cite{saravanan2026comparative} evaluate Variational Autoencoders (VAEs), Generative Adversarial Networks (GANs), and SMOTE~\cite{chawla2002smote} under adversarial stress. Their findings reveal that while deep generative oversamplers capture complex distributions, they introduce synthetic noise along decision boundaries. In contrast, SMOTE applied strictly to continuous numeric manifolds produces regularized interpolation vectors that stabilize minority attack classes without distorting the underlying manifold geometry.

\subsection{Attribution Fingerprinting and Behavioral Modeling}
Sharma et al.~\cite{sharma2025shap} explore SHAP attribution fingerprinting in IoT intrusion detection, utilizing feature attributions as a secondary signature to verify classification authenticity. Zhang et al.~\cite{zhang2024explainable} analyze the transferability of adversarial samples across explainable models, demonstrating that classifiers sharing similar attribution rankings exhibit high transfer susceptibility. Rajhans and Khawarey~\cite{rajhans2026explainability} quantify explainability drift, proving that adversarial perturbations distort attribution vectors long before causing misclassification. In contrast, elShehaby and Matrawy~\cite{elshehaby2026nodefense} question the necessity of complex defenses, arguing for aggressive dimensional reduction; however, their minimal feature sets suffer severe clean accuracy penalties. Finally, Ennaji et al.~\cite{ennaji2025behavior} introduce behavioral modeling on cloud telemetry, tracking temporal sequence dynamics to counter black-box evasion.

\section{Methodological Critiques, Attack Realism, and Evaluation Pitfalls}\label{sec:critique_review}

To ensure that an adversarial defense is robust, it must be evaluated against the methodological pitfalls, evaluation traps, and attack strategies documented in top-tier security literature.

\subsection{The Problem-Space vs. Feature-Space Dilemma}
A central criticism of adversarial ML research in network security is the gap between feature-space perturbations and operational network packets. Verkerken et al.~\cite{verkerken2026what} evaluate host-space perturbations, demonstrating that over $60\%$ of mathematically valid feature-space adversarial vectors cannot be reconstructed into valid TCP/IP packets due to packet format constraints and protocol header dependencies. 

Pierazzi et al.~\cite{pierazzi2020intriguing} formalize the problem-space realization framework, defining the inverse mapping problem:
\begin{equation}\label{eq:inverse_mapping}
    \Phi: \mathcal{Z} \to \mathcal{X}, \quad \Phi^{-1}: \mathcal{X} \to \mathcal{Z}
\end{equation}
where $\mathcal{Z}$ denotes the problem space (raw PCAP network packets) and $\mathcal{X}$ denotes the continuous feature space. Because the feature extraction mapping $\Phi$ is non-invertible, an adversary operating in the problem space cannot freely alter arbitrary flow features. Specifically, protocol semantics impose two fundamental restrictions:
\begin{itemize}
    \item \textbf{Monotonicity Constraints:} An attacker can inject dummy packets or padding to increase flow duration, packet count, or byte length, but cannot reduce them without dropping legitimate payload data.
    \item \textbf{Immutable Fields:} Critical flow identifiers such as TCP control flags, port combinations, and header structures must remain intact to establish a valid TCP three-way handshake.
\end{itemize}

Apruzzese et al.~\cite{apruzzese2023real} critically summarize this disparity with the maxim: \textit{``Real attackers don't compute gradients.''} In operational deployments, attackers lack direct gradient access to cloud firewalls and instead employ mutation-based query probing or traffic padding. However, as Apruzzese et al.\ acknowledge, evaluating defenses against $L_\infty$-bounded feature-space gradient attacks remains indispensable: it establishes the \textbf{worst-case mathematical upper bound} of adversarial vulnerability. A model capable of withstanding unconstrained worst-case feature perturbations is guaranteed to withstand problem-space mutations that operate within the same continuous envelope.

\subsection{Gradient Obfuscation and Masking Fallacies}
In their seminal work, Athalye, Carlini, and Wagner~\cite{athalye2018obfuscated} demonstrated that the vast majority of published adversarial defenses provide a false sense of security by unintentionally obfuscating gradients. Gradient masking occurs when a defense causes the model's loss landscape to become shattered, vanishing, or stochastic, preventing standard first-order optimization algorithms (such as FGSM or basic PGD) from finding adversarial vectors, even though vulnerable adversarial points remain densely present near clean samples.

Athalye et al.~\cite{athalye2018obfuscated} formalize five rigorous empirical diagnostic criteria to disprove gradient masking:
\begin{enumerate}
    \item \textbf{Iterative vs. Single-Step Attacks:} Iterative attacks (PGD) must consistently outperform single-step attacks (FGSM). If FGSM achieves higher ASR than multi-step PGD, gradients are obscured.
    \item \textbf{Unbounded Distortion Limit:} As perturbation budget $\epsilon \to \infty$, adversarial accuracy must drop to zero.
    \item \textbf{Monotonic Decay with Epsilon:} Adversarial accuracy must monotonically decrease as $\epsilon$ increases. Plateaus or sudden non-monotonic recoveries indicate shattered gradients.
    \item \textbf{Black-Box Query Efficacy:} Zero-gradient black-box attacks (such as Square Attack) must not achieve higher ASR than white-box gradient attacks. If black-box attacks outperform white-box attacks, the white-box model is masking its gradients.
    \item \textbf{Surrogate Transferability:} Adversarial samples crafted on an independent surrogate model must exhibit non-trivial transfer success against the target model, with white-box ASR strictly bounding transfer ASR.
\end{enumerate}

Tram{\`{e}}r et al.~\cite{tramer2020adaptive} reinforce these findings, proving that defenses claiming robustness under standard cross-entropy attacks often fail under \textbf{adaptive attacks} tailored to the defense's specific loss formulation. Croce and Hein~\cite{croce2020reliable} operationalize this principle by developing AutoAttack and Auto-PGD (APGD-CE), an ensemble of parameter-free, adaptive step-size attacks designed to circumvent local loss plateaus and provide an unbiased lower bound on empirical robustness.

\subsection{Attribution Vulnerabilities and Explanation Geometry}
Post-hoc Explainable AI (XAI) algorithms, particularly SHAP~\cite{lundberg2017unified}, are widely utilized to identify salient network features. However, Slack et al.~\cite{slack2020fooling} demonstrated that post-hoc explanation methods can be systematically fooled. An adversary can construct an adversarial scaffolding function that behaves identically to the clean model on training distributions but diverts feature attributions to arbitrary dummy features on perturbed inputs.

Dombrowski et al.~\cite{dombrowski2022explanations} investigate the geometric origins of explanation manipulation, proving that gradient-based attributions reflect local manifold curvature rather than true model sensitivity. Specifically, the explanation vector $E(x) = \nabla_x f(x)$ can be perturbed by an infinitesimally small input shift $\delta$ without altering the model's actual classification decision:
\begin{equation}\label{eq:explanation_curvature}
    \|\nabla_x f(x + \delta) - \nabla_x f(x)\| \approx \|\mathcal{H}_f(x) \delta\|
\end{equation}
where $\mathcal{H}_f(x)$ represents the Hessian matrix of second-order partial derivatives. When $\mathcal{H}_f(x)$ possesses large eigenvalues (high manifold curvature), attributions become unstable. This geometric insight is central to our work: features whose attributions fluctuate wildly under attack are precisely those residing in high-curvature, fragile manifold regions.

\subsection{Data Snooping, Dataset Leakage, and Evaluation Traps}
Arp et al.~\cite{arp2022dos} conduct an exhaustive survey of machine learning in computer security, uncovering that over $70\%$ of contemporary security papers suffer from methodological flaws, notably data snooping, preprocessing contamination, and unrealistic baseline comparisons. 

Engelen et al.~\cite{engelen2021troubleshooting} investigate the CSE-CIC-IDS2018 dataset, identifying critical artifacts:
\begin{itemize}
    \item \textbf{Socket Metadata Leakage:} Features such as `Flow ID`, `Source IP`, `Destination IP`, `Source Port`, and `Timestamp` act as artificial identifiers. Models trained on raw CSVs memorize IP addresses, achieving $>99\%$ synthetic accuracy while learning zero protocol dynamics.
    \item \textbf{Duplication and Infinity Artifacts:} Millions of duplicate flow records and non-numeric tokens (`Infinity`, `NaN`) distort variance computations if not systematically scrubbed.
\end{itemize}

Pontes et al.~\cite{pontes2023pitfalls} analyze oversampling pitfalls, proving that applying SMOTE across the entire dataset prior to train/test partitioning results in catastrophic data leakage, as synthetic test samples are interpolated from training neighbors. To maintain methodological validity, class balancing and feature scaling must be applied \textbf{strictly to the training partition}.

\subsection{Empirical Variance and Optimization Dynamics}
Raj et al.~\cite{raj2026categorical} demonstrate that single-seed evaluations in adversarial NIDS exhibit up to $\pm 15\%$ variance under multi-step PGD, rendering single-run benchmarks statistically unreliable. Valid evaluations require multi-seed protocols reporting mean and standard deviation. 

Tsipras et al.~\cite{tsipras2019robustness} theorize that adversarial robustness is fundamentally at odds with clean classification accuracy, showing that robust classifiers often suffer an inevitable clean performance degradation due to conflicting optimization goals. Rice, Wong, and Kolter~\cite{rice2020overfitting} identify the phenomenon of \textbf{robust overfitting}: during adversarial training, robust test error frequently collapses after a certain number of epochs, even while robust training loss continues to decline. Preventing robust overfitting requires early validation checkpointing and balanced clean/adversarial loss scheduling.

Finally, Moosavi-Dezfooli et al.~\cite{moosavi2016deepfool} introduce DeepFool, an untargeted iterative attack that projects inputs onto the closest decision boundary to find the minimal perturbation vector $r_{\text{adv}}$. In security evaluations, DeepFool serves as an unconstrained geometric probe: because DeepFool iterates without an $L_\infty$ ceiling until an adversarial flip occurs, its raw flip rate can approach $100\%$ on both robust and undefended models. However, the critical metric is the \textbf{required perturbation distance} $\|r_{\text{adv}}\|$; robust models force DeepFool to generate significantly larger perturbations, pushing the required distortion far outside realistic threat budgets.

\section{Comparative Summary and Identification of Research Gaps}\label{sec:gaps_and_summary}

A systematic comparison of representative peer architectures, baseline models, and our proposed Phase2Net defense is synthesized in~\Cref{tab:lit_comparison}.

\begin{table*}[!htp]
\centering
\caption{Comprehensive comparative synthesis of representative adversarial defense architectures in cloud NIDS.}\label{tab:lit_comparison}
\resizebox{\textwidth}{!}{%
\begin{tabular}{l l l l c c c}
\hline
\textbf{Work} & \textbf{Feature Selection} & \textbf{Defense Mechanism} & \textbf{Threat Model} & \textbf{Test Isolation} & \textbf{Clean Acc.} & \textbf{PGD Rob.} \\
\hline
Holla et al. (2025)~\cite{holla2025adversarial} & MI (40) + Clean SHAP (15) & Static Triad Augmentation & FGSM, PGD, DeepFool & Partial & 93.97\% & 79.70\% \\
Olukola \& Rahimi (2026)~\cite{olukola2026amds} & Full Raw Feature Space & 2-Stage Adaptive Weighting & PGD-20 & Full & 91.20\% & 89.40\% \\
G{\"{u}}ven{\c{c}} Paltun et al. (2025)~\cite{guvenc2025robust} & Attribution Alignment Loss & Regularized Loss Penalties & PGD, FGSM & Full & 92.45\% & 84.10\% \\
Nayak (2026)~\cite{nayak2026threatformer} & Attention Noise Stability & Transformer Adversarial AT & PGD, FGSM & Full & 94.10\% & 86.30\% \\
Marchiori \& Conti (2024)~\cite{marchiori2024canederli} & Telemetry Flow Selection & Clean Warm-up + PGD-AT & PGD, Transfer & Full & 93.50\% & 87.20\% \\
Zeng et al. (2025)~\cite{zeng2025csagc} & Graph Spatial Correlation & Attention Graph ConvNet & FGSM, PGD & Full & 95.12\% & 82.40\% \\
Zhou et al. (2023)~\cite{zhou2023certified} & Standard Feature Set & Certified Randomized Smooth & Gaussian $L_2$ & Full & 88.30\% & Certified \\
Debicha et al. (2021)~\cite{debicha2021adversarial} & Variance Thresholding & Dynamic Online PGD & PGD, FGSM & Full & 92.80\% & 85.60\% \\
Kara et al. (2025)~\cite{kara2025hybridguard} & MI (40) + SMOTE & Minority Adversarial Hardening & PGD, CW & Full & 94.20\% & 86.80\% \\
\hline
\textbf{Proposed Phase2Net} & \textbf{MI (40) + Stable SHAP $S(f)$ (27)} & \textbf{Pure-GPU Online PGD + Clean Warm-up} & \textbf{PGD-100, APGD, CW, Square} & \textbf{Strict (5-Point)} & \textbf{96.19\%} & \textbf{90.13\%} \\
\hline
\end{tabular}
}
\end{table*}

\subsection{Distilled Research Gaps}
From this rigorous literature review, four fundamental research gaps emerge:
\begin{enumerate}
    \item \textbf{The Static Augmentation Staleness Gap:} Existing state-of-the-art defenses (such as Holla et al.~\cite{holla2025adversarial}) rely on static offline adversarial generation, leaving models critically vulnerable to dynamic gradient attacks generated during subsequent deployment.
    \item \textbf{The Fragile Attribution Selection Gap:} Conventional XAI-guided feature selection methods select features exhibiting high clean attributions, inadvertently concentrating the classifier's attention on dimensions with high manifold curvature that are easily exploited by gradient ascent.
    \item \textbf{The Clean-Robust Accuracy Trade-off Gap:} Prior online adversarial defenses (such as AMDS~\cite{olukola2026amds} and Tsipras et al.~\cite{tsipras2019robustness}) incur a severe clean accuracy penalty (often losing $2\%$ to $5\%$ on clean traffic), which is unacceptable in enterprise cloud infrastructures processing petabytes of benign traffic daily.
    \item \textbf{The Evaluation Soundness Gap:} A significant portion of published NIDS literature fails to evaluate against adaptive attacks (APGD-CE, CW margin), neglects black-box zero-gradient verification, suffers from dataset socket leakage, and reports single-seed metrics that mask high variance.
\end{enumerate}

\subsection{Thesis Research Objectives}
To bridge these critical gaps, this thesis introduces \textbf{Phase2Net}, an end-to-end framework that:
\begin{itemize}
    \item Formulates a novel \textbf{Attribution Stability Metric $S(f)$}, mathematically quantifying feature resilience under adversarial gradient ascent and isolating a 27-dimensional stable subspace.
    \item Implements a \textbf{pure-GPU online PGD training engine} with clean warm-up pretraining and dynamic batch-level perturbation injection under a joint objective function.
    \item Enforces a \textbf{strict 5-point zero-leakage protocol} on the complete $6.32\text{M}$ CSE-CIC-IDS2018 dataset, evaluated across 3 independent random seeds against an extensive suite of 8 white-box, black-box, adaptive, and geometric attacks.
\end{itemize}

\endinput
"""

with open("SEU Research Final Template/Chapters/Chapter2.tex", "w", encoding="utf-8") as f:
    f.write(chapter2_latex.strip() + "\n")

print("Generated SEU Research Final Template/Chapters/Chapter2.tex successfully.")
