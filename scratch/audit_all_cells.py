# scratch/audit_all_cells.py
import json, ast

with open("v10_multi_class.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

import builtins
builtin_names = set(dir(builtins))

def get_unresolved_names(code, outer_scope):
    tree = ast.parse(code)
    
    # We analyze global statements vs local function scopes
    class Analyzer(ast.NodeVisitor):
        def __init__(self):
            self.globals_assigned = set()
            self.globals_used = set()
            self.current_scope = [{}] # stack of local scopes

        def visit_FunctionDef(self, node):
            self.globals_assigned.add(node.name)
            # enter function scope
            args = {a.arg for a in node.args.args}
            if node.args.vararg: args.add(node.args.vararg.arg)
            if node.args.kwarg: args.add(node.args.kwarg.arg)
            self.current_scope.append(args)
            self.generic_visit(node)
            self.current_scope.pop()

        def visit_AsyncFunctionDef(self, node):
            self.visit_FunctionDef(node)

        def visit_ClassDef(self, node):
            self.globals_assigned.add(node.name)
            self.current_scope.append(set())
            self.generic_visit(node)
            self.current_scope.pop()

        def visit_Name(self, node):
            name = node.id
            if isinstance(node.ctx, ast.Store):
                if len(self.current_scope) == 1:
                    self.globals_assigned.add(name)
                else:
                    self.current_scope[-1].add(name)
            elif isinstance(node.ctx, ast.Load):
                # Check if it's in any local scope
                is_local = any(name in s for s in reversed(self.current_scope[1:]))
                if not is_local:
                    self.globals_used.add(name)

        def visit_For(self, node):
            if len(self.current_scope) == 1:
                # Target names in global for loop are assigned globals
                for n in ast.walk(node.target):
                    if isinstance(n, ast.Name):
                        self.globals_assigned.add(n.id)
            self.generic_visit(node)

        def visit_comprehension(self, node):
            # Comprehensions have their own scope in Python 3
            comp_vars = set()
            for n in ast.walk(node.target):
                if isinstance(n, ast.Name):
                    comp_vars.add(n.id)
            self.current_scope.append(comp_vars)
            self.generic_visit(node)
            self.current_scope.pop()

        def visit_ExceptHandler(self, node):
            if node.name:
                if len(self.current_scope) == 1:
                    self.globals_assigned.add(node.name)
                else:
                    self.current_scope[-1].add(node.name)
            self.generic_visit(node)

    analyzer = Analyzer()
    analyzer.visit(tree)
    
    unresolved = []
    for var in analyzer.globals_used:
        if var not in analyzer.globals_assigned and var not in outer_scope and var not in builtin_names:
            unresolved.append(var)
            
    return analyzer.globals_assigned, unresolved

cumulative_scope = set()
print("Auditing all 25 cells for unresolved names:")
for idx, c in enumerate(nb["cells"]):
    if c["cell_type"] != "code":
        continue
    src = "".join(c["source"])
    first_line = src.strip().splitlines()[0] if src.strip() else "EMPTY"
    assigned, unresolved = get_unresolved_names(src, cumulative_scope)
    if unresolved:
        print(f"\n[ALERT] Cell {idx+1:02d} ({first_line[:50]}): UNRESOLVED GLOBALS:")
        for u in sorted(unresolved):
            print(f"   -> {u}")
    else:
        print(f"Cell {idx+1:02d} [OK]: {first_line[:50]}")
    cumulative_scope.update(assigned)

print("\n--- Testing Seed 123 and Seed 2024 in isolation from Seed 42 ---")
# Check if Cell 19 or 20 depends on variables ONLY created in Cell 18
# What was created in Cell 18?
cell18_assigned, _ = get_unresolved_names("".join(nb["cells"][17]["source"]), set())
# Run scope before Cell 18:
scope_before_18 = set()
for i in range(17):
    if nb["cells"][i]["cell_type"] == "code":
        a, _ = get_unresolved_names("".join(nb["cells"][i]["source"]), scope_before_18)
        scope_before_18.update(a)

_, unresolved_19_alone = get_unresolved_names("".join(nb["cells"][18]["source"]), scope_before_18)
if unresolved_19_alone:
    print("[LEAK/DEPENDENCY ALERT] Cell 19 (Seed 123) depends on variables from Cell 18:")
    for u in sorted(unresolved_19_alone):
        print(f"   -> {u}")
else:
    print("[OK] Cell 19 has NO hidden dependencies on Cell 18!")

_, unresolved_20_alone = get_unresolved_names("".join(nb["cells"][19]["source"]), scope_before_18)
if unresolved_20_alone:
    print("[LEAK/DEPENDENCY ALERT] Cell 20 (Seed 2024) depends on variables from Cell 18/19:")
    for u in sorted(unresolved_20_alone):
        print(f"   -> {u}")
else:
    print("[OK] Cell 20 has NO hidden dependencies on Cell 18/19!")
