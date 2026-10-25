# scratch/check_config_keys.py
import json, re

with open("v10_multi_class.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

# Find CONFIG definition in Cell 1
c1_src = "".join(nb["cells"][0]["source"])
# Find all CONFIG[...] in all cells
all_code = "\n".join(["".join(c["source"]) for c in nb["cells"]])

config_accesses = set(re.findall(r'CONFIG(?:\[|\.get\()\s*["\']([^"\']+)["\']', all_code))

# Parse CONFIG dict
import ast
c1_tree = ast.parse(c1_src)
config_keys = set()
for node in ast.walk(c1_tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "CONFIG":
                if isinstance(node.value, ast.Dict):
                    for k in node.value.keys:
                        if isinstance(k, ast.Constant):
                            config_keys.add(k.value)

print("CONFIG keys defined in Cell 1:", len(config_keys))
print("CONFIG keys accessed in notebook:", len(config_accesses))

missing_in_config = config_accesses - config_keys
print("Keys accessed but NOT defined in CONFIG:")
for k in sorted(missing_in_config):
    print(f"  -> {k}")

unused_in_config = config_keys - config_accesses
print("\nKeys in CONFIG but not accessed directly via CONFIG['...']:")
for k in sorted(unused_in_config):
    print(f"  -> {k}")
