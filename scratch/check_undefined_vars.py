import json, ast, builtins
from pathlib import Path

nb_path = Path("F:/PythonProjects/aml_rocm_native/v10_final.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

defined_scope = set(dir(builtins))
defined_scope.update({"__name__", "__file__", "__doc__"})

errors = []

for cell_idx, cell in enumerate(nb["cells"], 1):
    if cell.get("cell_type") != "code":
        continue
    source = "".join(cell.get("source", []))
    tree = ast.parse(source)
    
    cell_local_defs = set()
    
    class ScopeVisitor(ast.NodeVisitor):
        def __init__(self):
            self.scopes = []
        
        def visit_FunctionDef(self, node):
            if not self.scopes:
                cell_local_defs.add(node.name)
            else:
                self.scopes[-1].add(node.name)
            fn_locals = {arg.arg for arg in node.args.args}
            if node.args.vararg: fn_locals.add(node.args.vararg.arg)
            if node.args.kwarg: fn_locals.add(node.args.kwarg.arg)
            for arg in node.args.kwonlyargs: fn_locals.add(arg.arg)
            self.scopes.append(fn_locals)
            self.generic_visit(node)
            self.scopes.pop()

        def visit_AsyncFunctionDef(self, node):
            self.visit_FunctionDef(node)

        def visit_ClassDef(self, node):
            if not self.scopes:
                cell_local_defs.add(node.name)
            else:
                self.scopes[-1].add(node.name)
            self.scopes.append(set())
            self.generic_visit(node)
            self.scopes.pop()

        def visit_Lambda(self, node):
            fn_locals = {arg.arg for arg in node.args.args}
            self.scopes.append(fn_locals)
            self.generic_visit(node)
            self.scopes.pop()

        def visit_Assign(self, node):
            self.visit(node.value)
            for target in node.targets:
                self._collect_target(target)

        def visit_AnnAssign(self, node):
            if node.value:
                self.visit(node.value)
            self._collect_target(node.target)

        def visit_AugAssign(self, node):
            self.visit(node.value)
            self._collect_target(node.target)

        def visit_For(self, node):
            self.visit(node.iter)
            self._collect_target(node.target)
            for stmt in node.body:
                self.visit(stmt)
            for stmt in node.orelse:
                self.visit(stmt)

        def visit_AsyncFor(self, node):
            self.visit_For(node)

        def visit_With(self, node):
            for item in node.items:
                self.visit(item.context_expr)
                if item.optional_vars:
                    self._collect_target(item.optional_vars)
            for stmt in node.body:
                self.visit(stmt)

        def visit_AsyncWith(self, node):
            self.visit_With(node)

        def visit_Try(self, node):
            for stmt in node.body:
                self.visit(stmt)
            for h in node.handlers:
                if h.name:
                    if not self.scopes:
                        cell_local_defs.add(h.name)
                    else:
                        self.scopes[-1].add(h.name)
                if h.type:
                    self.visit(h.type)
                for stmt in h.body:
                    self.visit(stmt)
            for stmt in node.orelse:
                self.visit(stmt)
            for stmt in node.finalbody:
                self.visit(stmt)

        def visit_Import(self, node):
            for alias in node.names:
                name = alias.asname or alias.name.split('.')[0]
                if not self.scopes:
                    cell_local_defs.add(name)
                else:
                    self.scopes[-1].add(name)

        def visit_ImportFrom(self, node):
            for alias in node.names:
                name = alias.asname or alias.name
                if not self.scopes:
                    cell_local_defs.add(name)
                else:
                    self.scopes[-1].add(name)

        def visit_ListComp(self, node):
            comp_locals = set()
            self.scopes.append(comp_locals)
            for gen in node.generators:
                self.visit(gen.iter)
                self._collect_names(gen.target, comp_locals)
                for if_clause in gen.ifs:
                    self.visit(if_clause)
            self.visit(node.elt)
            self.scopes.pop()

        def visit_SetComp(self, node):
            self.visit_ListComp(node)

        def visit_DictComp(self, node):
            comp_locals = set()
            self.scopes.append(comp_locals)
            for gen in node.generators:
                self.visit(gen.iter)
                self._collect_names(gen.target, comp_locals)
                for if_clause in gen.ifs:
                    self.visit(if_clause)
            self.visit(node.key)
            self.visit(node.value)
            self.scopes.pop()

        def visit_GeneratorExp(self, node):
            self.visit_ListComp(node)

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Load):
                name = node.id
                in_local = any(name in s for s in reversed(self.scopes))
                if not in_local and name not in cell_local_defs and name not in defined_scope:
                    errors.append((cell_idx, node.lineno, name, not bool(self.scopes)))

        def _collect_target(self, target):
            if not self.scopes:
                self._collect_names(target, cell_local_defs)
            else:
                self._collect_names(target, self.scopes[-1])

        def _collect_names(self, node, s):
            if isinstance(node, ast.Name):
                s.add(node.id)
            elif isinstance(node, (ast.Tuple, ast.List)):
                for elt in node.elts:
                    self._collect_names(elt, s)
            elif isinstance(node, ast.Starred):
                self._collect_names(node.value, s)

    visitor = ScopeVisitor()
    visitor.visit(tree)
    defined_scope.update(cell_local_defs)

print(f"Total potential undefined references found: {len(errors)}")
for cell_i, line_no, name, is_global in errors:
    scope_type = "GLOBAL level" if is_global else "INSIDE function/class"
    print(f"  [Cell {cell_i:02d}, Line {line_no:02d}] '{name}' ({scope_type})")
