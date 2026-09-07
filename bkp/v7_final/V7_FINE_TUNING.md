# V7 post-run operating-point calibration

The validated V7 result is preserved unchanged. This optional calibration targets
its main operational limitation: the defended model's elevated false-positive
rate.

## Run

Keep the completed V7 kernel alive, add one new notebook cell, and run:

```python
%run -i tools/v7_calibrate_operating_point.py
```

This normally requires only inference, not training. It uses the development
split to select separate baseline and defended thresholds by maximizing Matthews
correlation coefficient while allowing at most a one-percentage-point decrease
in attack recall from the default threshold.

The selected thresholds are then frozen and evaluated on the clean test set and
the retained Square-style, MI-FGSM, random-sanity, sparse and boundary-search
arrays. Test labels never influence threshold selection.

## New artifacts

- `calibrated_thresholds.json`
- `calibrated_clean_metrics.csv`
- `calibrated_attack_metrics.csv`
- `figures/06_calibrated_operating_point.png`

These files are saved under `output/v7/seed_42/` and do not overwrite the
validated V7 artifacts.

## Interpretation

Treat calibration as a secondary operating-point analysis. Report both the
default threshold and calibrated threshold. Do not silently replace the original
V7 metrics, and do not describe threshold calibration as additional adversarial
training.

The separate FGSM, PGD, DeepFool and C&W adversarial arrays were not retained by
the completed notebook. Their original validated results remain in `table4.csv`;
re-evaluating them under the calibrated threshold would require regenerating
those attacks.
