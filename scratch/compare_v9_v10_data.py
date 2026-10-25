import json
import numpy as np

v9_mi = json.load(open("outputs/v9_final/artifacts/mi_features.json"))
v10_mi = json.load(open("outputs/v10/artifacts/mi_features.json"))

print("v9_mi keys:", list(v9_mi.keys()))
print("v10_mi keys:", list(v10_mi.keys()))

v9_f = v9_mi.get("features", v9_mi.get("mi_features", []))
v10_f = v10_mi.get("features", v10_mi.get("mi_features", []))

print("v9 feature count:", len(v9_f))
print("v10 feature count:", len(v10_f))
print("Same features?", v9_f == v10_f)
if v9_f != v10_f:
    print("V9[:5]:", v9_f[:5])
    print("V10[:5]:", v10_f[:5])
    print("Features in common:", len(set(v9_f) & set(v10_f)))
