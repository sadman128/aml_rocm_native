# What changed this time, in short:

1. Real adversarial training, not fake augmentation — the defended model now trains on fresh adversarial examples generated from its own current weights every single training batch (Madry-style), instead of a static batch of adversarial examples generated once and reused.
2. Added a "how small an attack still works" test — sweeps attack strength from tiny to moderate and reports the smallest perturbation that fools each model.
3. Feature count is no longer a fixed number — MI and SHAP selection now keep however many features are needed to cover 90% of total importance, decided by the data instead of hardcoded.
4. Each of the 3 hidden layers is independently configurable, not locked to 128-64-32.
5. Fixed a real bug in the overhead calculation that was inflating the "% slower" number.
6. Added an automatic side-by-side comparison against the paper's published numbers, printed and saved every run.

Is it different from the paper's approach — yes, and substantially:

The paper trains its defense on a fixed, pre-generated batch of adversarial examples mixed into the dataset once, then trains normally on that mixture.
We now use on-the-fly adversarial training — a stronger, more modern method where attacks are regenerated fresh against the model's current state every batch, so the model can't just memorize a stale set of attacks.

This is a genuine methodological upgrade beyond what the paper did, not a reproduction of it — expect your defended model's robustness numbers to look meaningfully better than the paper's, and expect training to cost more time as a direct, known consequence.