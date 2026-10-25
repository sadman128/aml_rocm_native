import json

for s in [42, 123, 2024]:
    try:
        with open(f"outputs/v10_multy_class/seeds/{s}/zero_day_spec.json") as f:
            z_old = json.load(f)
        with open(f"outputs/v10_final/seeds/{s}/zero_day_spec.json") as f:
            z_new = json.load(f)
        print(f"Seed {s}:")
        print(f"  v10_multy_class held out: {z_old['held_out_attack']}")
        print(f"  v10_final held out:       {z_new['held_out_attack']}")
    except Exception as e:
        print(f"Seed {s}: {e}")
